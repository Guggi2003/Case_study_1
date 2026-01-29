import streamlit as st
import datetime as dt

# Backend-Klassen importieren
from users import User
from devices import Device, DeviceState
from maintenance import Maintenance, MaintenanceManager
from reservations import Reservation, ReservationManager

# --------------------------------------------------------------------------------
# CONFIG & MANAGERS
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Administrator-Portal", layout="wide")

# Instanzen einmalig anlegen
reservation_manager = ReservationManager()
maintenance_manager = MaintenanceManager()

# --------------------------------------------------------------------------------
# CACHE / HELPER
# --------------------------------------------------------------------------------
def load_users_cached() -> list[User]:
    if "users_cache" not in st.session_state:
        st.session_state["users_cache"] = User.find_all()
    return st.session_state["users_cache"]

def load_devices_cached() -> list[Device]:
    if "devices_cache" not in st.session_state:
        st.session_state["devices_cache"] = Device.find_all()
    return st.session_state["devices_cache"]

def invalidate_users_cache():
    if "users_cache" in st.session_state:
        del st.session_state["users_cache"]

def invalidate_devices_cache():
    if "devices_cache" in st.session_state:
        del st.session_state["devices_cache"]

def label_to_id(label: str) -> str:
    # Format "Name (ID)" -> nur ID zurückgeben
    return label.split(" (")[1].rstrip(")")

# Initialer Load
users = load_users_cached()
devices = load_devices_cached()

# --------------------------------------------------------------------------------
# NAVIGATION CALLBACKS
# Setzen den State für den Rerun
# --------------------------------------------------------------------------------
def go_to_state_device_management():
    st.session_state["state"] = "state_device_management"

def go_to_state_user_management():
    st.session_state["state"] = "state_user_management"

def go_to_state_reservation_system():
    st.session_state["state"] = "state_reservation_system"

def go_to_state_maintenance_system():
    st.session_state["state"] = "state_maintenance_system"

# --------------------------------------------------------------------------------
# SIDEBAR
# --------------------------------------------------------------------------------
with st.sidebar:
    st.title("Navigation")
    st.button("Geräte-Verwaltung", on_click=go_to_state_device_management, use_container_width=True)
    st.button("Nutzer-Verwaltung", on_click=go_to_state_user_management, use_container_width=True)
    st.button("Reservierungssystem", on_click=go_to_state_reservation_system, use_container_width=True)
    st.button("Wartungssystem", on_click=go_to_state_maintenance_system, use_container_width=True)
    
    st.markdown("---")


# --------------------------------------------------------------------------------
# MAIN ROUTING
# --------------------------------------------------------------------------------

# Default-Route
if "state" not in st.session_state:
    go_to_state_device_management()
    st.rerun()

# ==============================================================================
# VIEW: GERÄTE
# ==============================================================================
elif st.session_state["state"] == "state_device_management":
    st.header("Geräte-Verwaltung")
    col1, col2, col3 = st.columns(3)

    # Hilfslisten für Dropdowns
    dnames = [d.device_name for d in devices]
    user_labels = [f"{u.name} ({u.id})" for u in users]

    # --- Spalte 1: Detailansicht & Status-Check ---
    with col1:
        st.subheader("Geräte anzeigen")
        current_name = st.selectbox("Gerät auswählen", dnames if dnames else ["Keine Geräte"])
        
        if current_name and current_name != "Keine Geräte":
            dev = Device.find_by_attribute("device_name", current_name)
            if dev:
                is_live_reserved = False
                active_res_info = ""
                
                
                all_res = reservation_manager.find_all()
                now = dt.datetime.now()
                
                for r in all_res:
                    if r.device_name == dev.device_name:
                        if r.start <= now <= r.end:
                            is_live_reserved = True
                            active_res_info = f"User: {r.user_id} (bis {r.end.strftime('%H:%M')})"
                            break
                
                # Status-Anzeige
                if is_live_reserved:
                    st.warning(f"Status: Reserved")
                    st.caption(f"Aktuell belegt durch {active_res_info}")
                else:
                    real_state = dev.state.value 
                    
                    if real_state == "available":
                        st.success(f"Status: {real_state}")
                    elif real_state == "maintenance":
                        st.error(f"Status: {real_state}")
                    else:
                        st.info(f"Status: {real_state}")

                st.write(f"Verwalter-ID: {dev.managed_by_user_id}")
                
                st.markdown("---")
                if st.button("Gerät löschen", type="primary"):
                    dev.delete()
                    invalidate_devices_cache()
                    st.success("Gerät gelöscht!")
                    st.rerun()

    # --- Spalte 2: Neues Gerät ---
    with col2:
        st.subheader("Neues Gerät")
        if not users:
            st.error("Zuerst Nutzer anlegen!")
        else:
            with st.form("create_device_form", clear_on_submit=True):
                new_device_name = st.text_input("Gerätename")
                
                selected_user_label = st.selectbox("Verwalter", user_labels)
                
                if st.form_submit_button("Erstellen"):
                    if new_device_name:
                        selected_user_id = label_to_id(selected_user_label)
                        dev = Device(new_device_name.strip(), selected_user_id)
                        dev.store_data()
                        invalidate_devices_cache()
                        st.success("Erstellt!")
                        st.rerun()
                    else:
                        st.error("Name fehlt.")

    # --- Spalte 3: Verwalter Update ---
    with col3:
        st.subheader("Verwalter ändern")
        if dnames and users:
            with st.form("assign_manager"):
                dev_assign = st.selectbox("Gerät", dnames)
                mgr_assign = st.selectbox("Neuer Verwalter", user_labels)
                
                if st.form_submit_button("Zuweisen"):
                    dev = Device.find_by_attribute("device_name", dev_assign)
                    if dev:
                        dev.set_managed_by_user_id(label_to_id(mgr_assign))
                        dev.store_data()
                        invalidate_devices_cache()
                        st.success("Zugewiesen!")
                        st.rerun()

# ==============================================================================
# VIEW: NUTZER
# ==============================================================================
elif st.session_state["state"] == "state_user_management":
    st.header("Nutzer-Verwaltung")
    col1, col2, col3 = st.columns(3)

    # --- Spalte 1: Info ---
    with col1:
        st.subheader("Details")
        if users:
            sel_uid = st.selectbox("User ID", [u.id for u in users])
            u = User.find_by_attribute("id", sel_uid)
            if u:
                st.write(f"Name: **{u.name}**")
                assigned_devs = Device.find_by_attribute("managed_by_user_id", u.id, num_to_return=100)
                st.caption(f"Verwaltet {len(assigned_devs) if assigned_devs else 0} Geräte")
        else:
            st.info("Keine Nutzer.")

    # --- Spalte 2: Create / Update ---
    with col2:
        st.subheader("Erstellen / Update")
        with st.form("user_upsert"):
            uid = st.text_input("ID (eindeutig)")
            uname = st.text_input("Anzeigename")
            if st.form_submit_button("Speichern"):
                if uid and uname:
                    u = User(uid.strip(), uname.strip())
                    u.store_data()
                    invalidate_users_cache()
                    st.success("Gespeichert!")
                    st.rerun()
                else:
                    st.error("Daten fehlen.")

    # --- Spalte 3: Delete ---
    with col3:
        st.subheader("Löschen")
        if users:
            del_uid = st.selectbox("User löschen", [u.id for u in users])
            if st.button("Endgültig löschen", type="primary"):
                u = User.find_by_attribute("id", del_uid)
                # Schutz: User darf keine Geräte verwalten
                assigned = Device.find_by_attribute("managed_by_user_id", u.id, num_to_return=1)
                if assigned:
                    st.error("User verwaltet noch Geräte! Erst ändern.")
                else:
                    u.delete()
                    invalidate_users_cache()
                    st.success("Gelöscht.")
                    st.rerun()

# ==============================================================================
# VIEW: RESERVIERUNGEN
# ==============================================================================
elif st.session_state["state"] == "state_reservation_system":
    st.header("Reservierungssystem")
    col1, col2, col3 = st.columns(3)
    
    reservations = reservation_manager.find_all()
    
    if reservations:
        try:
            next_id = max(int(r.reservation_id) for r in reservations) + 1
        except ValueError:
            next_id = len(reservations) + 1
    else:
        next_id = 1

    # --- Spalte 1: Übersicht ---
    with col1:
        st.subheader("Liste")
        if not reservations:
            st.info("Leer.")
        for r in reservations:
            with st.expander(f"{r.device_name} ({r.start.strftime('%d.%m')})"):
                st.write(f"User: {r.user_id}")
                st.write(f"Von: {r.start}")
                st.write(f"Bis: {r.end}")
                st.caption(r.note)

    # --- Spalte 2: Buchung ---
    with col2:
        st.subheader("Neue Reservierung")
        if devices and users:
            with st.form("new_res"):
                st.text_input("ID", value=str(next_id), disabled=True)
                r_dev = st.selectbox("Gerät", [d.device_name for d in devices])
                r_user_label = st.selectbox("User", [f"{u.name} ({u.id})" for u in users])
                
                c1, c2 = st.columns(2)
                d_start = c1.date_input("Start")
                t_start = c2.time_input("Start Zeit", value=dt.time(9,0))
                d_end = c1.date_input("Ende")
                t_end = c2.time_input("End Zeit", value=dt.time(17,0))
                note = st.text_input("Notiz")

                if st.form_submit_button("Buchen"):
                    start_dt = dt.datetime.combine(d_start, t_start)
                    end_dt = dt.datetime.combine(d_end, t_end)
                    
                    if end_dt <= start_dt:
                        st.error("Ende vor Start!")
                    else:
                        r = Reservation(str(next_id), r_dev, label_to_id(r_user_label), start_dt, end_dt, note)
                        if reservation_manager.create(r):
                            st.success("Gebucht!")
                            st.rerun()
                        else:
                            st.error("Konflikt oder ID belegt.")
        else:
            st.warning("Keine Geräte/Nutzer.")

    # --- Spalte 3: Storno ---
    with col3:
        st.subheader("Stornieren")
        if reservations:
            del_rid = st.selectbox("Wähle ID", [r.reservation_id for r in reservations])
            if st.button("Löschen", key="del_res"):
                reservation_manager.delete_by_id(del_rid)
                st.success("Gelöscht.")
                st.rerun()

# ==============================================================================
# VIEW: WARTUNG
# ==============================================================================
elif st.session_state["state"] == "state_maintenance_system":
    st.header("Wartungssystem")
    col1, col2, col3 = st.columns(3)
    
    maints = maintenance_manager.find_all()
    
    if maints:
        try:
            next_mid = max(int(m.maintenance_id) for m in maints) + 1
        except ValueError:
            next_mid = len(maints) + 1
    else:
        next_mid = 1

    # --- Spalte 1: Logs ---
    with col1:
        st.subheader("Historie")
        if maints:
            for m in maints:
                st.markdown(f"**{m.device_name}** ({m.cost}€)")
                st.caption(f"ID: {m.maintenance_id} | {m.description}")
                st.markdown("---")
        else:
            st.info("Keine Wartungen.")

    # --- Spalte 2: Eintrag ---
    with col2:
        st.subheader("Eintragen")
        if devices:
            with st.form("new_maint"):
                st.text_input("ID", value=str(next_mid), disabled=True)
                m_dev = st.selectbox("Gerät", [d.device_name for d in devices])
                desc = st.text_area("Beschreibung")
                cost = st.number_input("Kosten (€)", min_value=0.0, step=10.0)
                
                if st.form_submit_button("Speichern"):
                    if desc:
                        m = Maintenance(str(next_mid), m_dev, desc, cost)
                        maintenance_manager.upsert(m)
                        st.success("Gespeichert!")
                        st.rerun()
                    else:
                        st.error("Beschreibung fehlt.")
        else:
            st.warning("Keine Geräte.")

    # --- Spalte 3: Stats & Delete ---
    with col3:
        st.subheader("Verwaltung")
        if maints:
            total = sum(m.cost for m in maints)
            st.metric("Gesamtkosten", f"{total:.2f} €")
            
            st.markdown("---")
            del_mid = st.selectbox("Löschen ID", [m.maintenance_id for m in maints])
            if st.button("Löschen", key="del_maint"):
                maintenance_manager.delete_by_id(del_mid)
                st.success("Gelöscht.")
                st.rerun()