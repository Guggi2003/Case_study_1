import streamlit as st

from users import User
from devices import Device

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
    user_ids = [u.id for u in users]

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

    # ---------- COL 2: Neues Gerät erstellen (Verwalter Pflicht) ----------
    with col2:
        st.subheader("Neues Gerät erstellen")

        if not users:
            st.error("Keine Nutzer vorhanden. Bitte zuerst einen Nutzer anlegen.")
        if users:
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

    # ---------- COL 3: Verwalter einteilen / umhaengen ----------
    with col3:
        st.subheader("Verwalter einteilen")

        if not dnames:
            st.info("Keine Geräte vorhanden.")
        elif not users:
            st.error("Keine Nutzer vorhanden. Bitte zuerst Nutzer anlegen.")
        else:
            with st.form("assign_manager_form", clear_on_submit=False):
                # Gerät zum Einteilen auswaehlen
                device_to_assign = st.selectbox("Gerät", dnames, index=0)

                # Ziel-Verwalter
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


            st.markdown("---")
            # Kleine Uebersicht verwaltete Geräte
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
                        st.write(f"- {d.device_name})")
                else:
                    st.write("Keine Geräte zugeordnet.")

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

    with col1:
        st.subheader("Reservierung anzeigen")
        st.write("Platzhalter: Reservierungen anzeigen")
        st.button("Reservierung anzeigen")

    with col2:
        st.subheader("Reservierung eintragen")
        st.write("Platzhalter: Reservierung eintragen")
        st.button("Reservierung eintragen")

    with col3:
        st.subheader("Reservierung löschen")
        st.write("Platzhalter")
        st.button("Reservierung löschen")


elif selected_area == "Wartungs-Management":
    col1, col2, col3= st.columns(3)

    with col1:
        st.subheader("Wartungen anzeigen")
        st.write("Platzhalter: Wartungsübersicht")
        st.button("Wartungen anzeigen")

    with col2:
        st.subheader("Wartungskosten anzeigen")
        st.write("Platzhalter: Kostenübersicht")
        st.button("Wartungskosten anzeigen")

    with col3:
        st.subheader("Wartung löschen")
        st.write("Platzhalter: Nutzerliste")
        st.button("Wartung löschen")