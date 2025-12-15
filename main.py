import streamlit as st

from users import User
from devices import Device
from maintenance import Maintenance, MaintenanceManager
from reservations import Reservation, ReservationManager

reservation_manager = ReservationManager()

maintenance_manager = MaintenanceManager()

st.set_page_config(page_title="Administrator-Portal", layout="wide")

# ---------- Helpers ----------
def load_users() -> list[User]:
    return User.find_all()

def load_devices() -> list[Device]:
    return Device.find_all()

def users_by_id(users: list[User]) -> dict[str, User]:
    return {u.id: u for u in users}

def device_names(devices: list[Device]) -> list[str]:
    return [d.device_name for d in devices]


# ---------- Session State ----------
if "current_device_name" not in st.session_state:
    st.session_state["current_device_name"] = None

# ---------- Daten laden ----------
users = load_users()
devices = load_devices()
user_map = users_by_id(users)

# ---------- Seitentitel ----------
st.title("Administrator-Portal")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Navigation")

    selected_area = st.radio(
        "Bereich auswählen",
        [
            "Geräte-Verwaltung",
            "Nutzer-Verwaltung",
            "Reservierungssystem",
            "Wartungs-Management",
        ],
    )

    st.markdown("---")
    st.subheader("Geräteauswahl")

    dnames = device_names(devices)
    current = st.session_state.get("current_device_name", None)

    if dnames:
        default_idx = 0
        if current in dnames:
            default_idx = dnames.index(current)

        selected = st.selectbox("Gerät auswählen", dnames, index=default_idx)
        st.session_state["current_device_name"] = selected

        st.write("Aktuelles Gerät:")
        st.write(st.session_state["current_device_name"])
    else:
        st.info("Keine Geräte in der Datenbank.")
        st.session_state["current_device_name"] = None


# ---------- HAUPTBEREICH (WECHSELT) ----------
st.header(selected_area)

if selected_area == "Geräte-Verwaltung":
    col1, col2, col3 = st.columns(3)

    # ---------- Daten fuer UI ----------
    dnames = [d.device_name for d in devices]
    user_labels = [f"{u.name} ({u.id})" for u in users]

    # Helper: label -> id
    def label_to_id(label: str) -> str:
        return label.split("(")[-1].rstrip(")")

    # ---------- COL 1: Gerätedetails anzeigen ----------
    with col1:
        st.subheader("Gerätedetails")

        current_name = st.session_state.get("current_device_name", None)
        if current_name:
            dev = Device.find_by_attribute("device_name", current_name)
            if dev:
                st.write(f"Name: {dev.device_name}")
                st.write(f"Managed by: {dev.managed_by_user_id}")
                st.write(f"Aktiv: {dev.is_active}")
            else:
                st.warning("Gerät nicht gefunden.")

        st.markdown("---")
        if current_name:
            if st.button("Gerät löschen", type="primary"):
                dev = Device.find_by_attribute("device_name", current_name)
                if dev:
                    dev.delete()
                    st.session_state["current_device_name"] = None
                    st.success("Gerät gelöscht.")
                    st.rerun()
                else:
                    st.error("Gerät nicht gefunden.")

    # ---------- COL 2: Neues Gerät erstellen (Verwalter Pflicht) ----------
    with col2:
        st.subheader("Neues Gerät erstellen")

        if not users:
            st.error("Keine Nutzer vorhanden. Bitte zuerst einen Nutzer anlegen.")
        else:
            with st.form("create_device_form", clear_on_submit=True):
                new_device_name = st.text_input("Gerätename", value="")
                new_is_active = st.checkbox("Aktiv", value=True)

                selected_user_label = st.selectbox(
                    "Verwalter zuweisen (verpflichtend)",
                    user_labels,
                    index=0
                )
                selected_user_id = label_to_id(selected_user_label)

                submitted = st.form_submit_button("Gerät erstellen")

                if submitted:
                    if not new_device_name.strip():
                        st.error("Gerätename darf nicht leer sein.")
                    else:
                        dev = Device(new_device_name.strip(), selected_user_id)
                        dev.is_active = new_is_active
                        dev.store_data()
                        st.success("Gerät erstellt.")
                        st.rerun()

    # ---------- COL 3: Verwalter einteilen / umhaengen ----------
    with col3:
        st.subheader("Verwalter einteilen")

        if not dnames:
            st.info("Keine Geräte vorhanden.")
        elif not users:
            st.error("Keine Nutzer vorhanden. Bitte zuerst Nutzer anlegen.")
        else:
            with st.form("assign_manager_form", clear_on_submit=False):
                device_to_assign = st.selectbox("Gerät", dnames, index=0)

                manager_label = st.selectbox("Neuer Verwalter", user_labels, index=0)
                manager_id = label_to_id(manager_label)

                submitted = st.form_submit_button("Zuweisen")

                if submitted:
                    dev = Device.find_by_attribute("device_name", device_to_assign)
                    if not dev:
                        st.error("Gerät nicht gefunden.")
                    else:
                        dev.set_managed_by_user_id(manager_id)
                        dev.store_data()
                        st.success(f"Verwalter zugewiesen: {device_to_assign} -> {manager_id}")
                        st.rerun()

            st.markdown("---")
            st.write("Übersicht Verwalter -> Geräte")
            for u in users:
                assigned = Device.find_by_attribute("managed_by_user_id", u.id, num_to_return=100)
                count = len(assigned) if assigned else 0
                st.write(f"- {u.name} ({u.id}): {count}")


#################################################################################################################################################

elif selected_area == "Nutzer-Verwaltung":
    col1, col2, col3 = st.columns(3)

    # --- Nutzer anzeigen ---
    with col1:
        st.subheader("Nutzer anzeigen")

        if users:
            selected_user_id = st.selectbox("User auswählen (ID)", [u.id for u in users], index=0)
            u = User.find_by_attribute("id", selected_user_id)

            if u:
                st.write(f"ID: {u.id}")
                st.write(f"Name: {u.name}")

                assigned = Device.find_by_attribute("managed_by_user_id", u.id, num_to_return=100)
                st.markdown("---")
                st.write("Zugeordnete Geräte:")
                if assigned:
                    for d in assigned:
                        st.write(f"- {d.device_name}")
                else:
                    st.write("Keine Geräte zugeordnet.")
        else:
            st.info("Keine Nutzer vorhanden.")

    # --- Nutzer erstellen/ändern ---
    with col2:
        st.subheader("Nutzer erstellen/ändern")

        with st.form("user_upsert", clear_on_submit=False):
            uid = st.text_input("User-ID (Format: NUMBER@mci.edu)", value="")
            uname = st.text_input("Name", value="")
            submitted = st.form_submit_button("Speichern")

            if submitted:
                if not uid.strip():
                    st.error("User-ID darf nicht leer sein.")
                elif not uname.strip():
                    st.error("Name darf nicht leer sein.")
                else:
                    u = User(uid.strip(), uname.strip())
                    u.store_data()
                    st.success("User gespeichert.")
                    st.rerun()

    # --- Nutzer löschen ---
    with col3:
        st.subheader("Nutzer löschen")

        if users:
            del_user_id = st.selectbox("User löschen (ID)", [u.id for u in users], index=0)

            if st.button("User endgültig löschen", type="primary"):
                u = User.find_by_attribute("id", del_user_id)
                if u:
                    assigned = Device.find_by_attribute("managed_by_user_id", u.id, num_to_return=100)
                    if assigned:
                        st.error("User hat noch Geräte zugeordnet - erst umhaengen oder Geräte loeschen.")
                    else:
                        u.delete()
                        st.success("User gelöscht.")
                        st.rerun()
                else:
                    st.error("User nicht gefunden.")
        else:
            st.write("Keine Nutzer vorhanden.")


elif selected_area == "Reservierungssystem":
    col1, col2, col3 = st.columns(3)

    reservations = reservation_manager.find_all()

    with col1:
        st.subheader("Reservierungen anzeigen")
        if not reservations:
            st.info("Keine Reservierungen vorhanden.")
        else:
            for r in reservations:
                st.write(f"- {r.reservation_id} | {r.device_name} | {r.user_id} | {r.start_iso} -> {r.end_iso} | {r.note}")

    with col2:
        st.subheader("Reservierung eintragen")
        if not devices:
            st.error("Keine Geräte vorhanden.")
        elif not users:
            st.error("Keine Nutzer vorhanden.")
        else:
            dnames = [d.device_name for d in devices]
            uids = [u.id for u in users]

            with st.form("create_reservation", clear_on_submit=True):
                rid = st.text_input("Reservierungs-ID (eindeutig)")
                dev = st.selectbox("Gerät", dnames)
                uid = st.selectbox("User", uids)
                start = st.text_input("Start (ISO, z.B. 2025-12-15T10:00:00)")
                end = st.text_input("Ende (ISO, z.B. 2025-12-15T12:00:00)")
                note = st.text_input("Notiz (optional)")
                submitted = st.form_submit_button("Reservieren")

                if submitted:
                    if not rid.strip() or not start.strip() or not end.strip():
                        st.error("ID, Start und Ende sind Pflicht.")
                    else:
                        ok = reservation_manager.create(Reservation(rid.strip(), dev, uid, start.strip(), end.strip(), note.strip()))
                        if ok:
                            st.success("Reservierung gespeichert.")
                            st.rerun()
                        else:
                            st.error("Nicht möglich (ID existiert oder Zeit überschneidet sich / Format falsch).")

    with col3:
        st.subheader("Reservierung löschen")
        if not reservations:
            st.info("Keine Reservierungen vorhanden.")
        else:
            ids = [r.reservation_id for r in reservations]
            del_id = st.selectbox("Reservierung-ID", ids)
            if st.button("Löschen", type="primary"):
                if reservation_manager.delete_by_id(del_id):
                    st.success("Gelöscht.")
                    st.rerun()
                else:
                    st.error("Nicht gefunden.")


###############################################################################
elif selected_area == "Wartungs-Management":
    col1, col2, col3 = st.columns(3)

    maints = maintenance_manager.find_all()

    with col1:
        st.subheader("Wartungen anzeigen")

        if not maints:
            st.info("Keine Wartungen vorhanden.")
        else:
            st.write("Alle Wartungen:")
            for m in maints:
                st.write(f"- {m.maintenance_id} | Gerät: {m.device_name} | Kosten: {m.cost:.2f} | {m.description}")

            st.markdown("---")
            if devices:
                dnames = [d.device_name for d in devices]
                sel_dev = st.selectbox("Nach Gerät filtern", ["(alle)"] + dnames, index=0)
                if sel_dev != "(alle)":
                    filtered = maintenance_manager.find_by_attribute("device_name", sel_dev, num_to_return=500)
                    st.write(f"Wartungen für {sel_dev}:")
                    for m in filtered:
                        st.write(f"- {m.maintenance_id} | Kosten: {m.cost:.2f} | {m.description}")

    with col2:
        st.subheader("Wartung anlegen/ändern")

        if not devices:
            st.error("Keine Geräte vorhanden. Bitte zuerst Geräte anlegen.")
        else:
            dnames = [d.device_name for d in devices]

            with st.form("maintenance_upsert_form", clear_on_submit=True):
                mid = st.text_input("Wartungs-ID (eindeutig)", value="")
                dev_name = st.selectbox("Gerät", dnames, index=0)
                desc = st.text_area("Beschreibung", value="")
                cost = st.number_input("Kosten", min_value=0.0, value=0.0, step=1.0)

                submitted = st.form_submit_button("Speichern")

                if submitted:
                    if not mid.strip():
                        st.error("Wartungs-ID darf nicht leer sein.")
                    elif not desc.strip():
                        st.error("Beschreibung darf nicht leer sein.")
                    else:
                        m = Maintenance(
                            maintenance_id=mid.strip(),
                            device_name=dev_name,
                            description=desc.strip(),
                            cost=float(cost),
                        )
                        maintenance_manager.upsert(m)
                        st.success("Wartung gespeichert.")
                        st.rerun()

    with col3:
        st.subheader("Wartungskosten anzeigen / Wartung löschen")

        if not maints:
            st.info("Keine Wartungen vorhanden.")
        else:
            total = sum(m.cost for m in maints)
            st.write(f"Gesamtkosten: {total:.2f}")

            st.markdown("---")
            st.write("Kosten pro Gerät:")
            per_device = {}
            for m in maints:
                per_device[m.device_name] = per_device.get(m.device_name, 0.0) + m.cost
            for dev, c in per_device.items():
                st.write(f"- {dev}: {c:.2f}")

            st.markdown("---")
            ids = [m.maintenance_id for m in maints]
            del_id = st.selectbox("Wartung löschen (ID)", ids, index=0)

            if st.button("Wartung endgültig löschen", type="primary"):
                ok = maintenance_manager.delete_by_id(del_id)
                if ok:
                    st.success("Wartung gelöscht.")
                    st.rerun()
                else:
                    st.error("Wartung nicht gefunden.")
