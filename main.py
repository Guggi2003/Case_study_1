import streamlit as st

# ---------- Session State ----------
if "current_device" not in st.session_state:
    st.session_state.current_device = "Der Gerät"

# ---------- Seitentitel ----------
st.title("Administrator-Portal")

# ---------- SIDEBAR (IMMER GLEICH) ----------
with st.sidebar:
    st.header("Navigation, wähle aus")

    selected_area = st.radio(
        "Bereich auswählen",
        [
            "Geräte-Verwaltung",
            "Nutzer-Verwaltung",
            "Reservierungssystem",
            "Wartungs-Management",
        ]
    )

    st.markdown("---")
    st.subheader("Geräteauswahl")

    devices = ["Gerät_A", "Gerät_B", "Gerät_C", "Gerät_D"]
    st.session_state.current_device = st.selectbox(
        "Gerät auswählen",
        devices,
        index=0
    )

    st.markdown("---")
    st.write("Aktuelles Gerät:")
    st.write(f"{st.session_state.current_device}")

# ---------- HAUPTBEREICH (WECHSELT) ----------
st.header(selected_area)

if selected_area == "Geräte-Verwaltung":
    col1, col2 , col3 = st.columns(3)

    with col1:
        st.subheader("Gerät anzeigen")
        st.write("Platzhalter: Gerätedaten anzeigen")
        st.button("Gerät anzeigen")

    with col2:
        st.subheader("Gerät ändern")
        st.write("Platzhalter: Gerätedaten ändern")
        st.button("Gerät ändern")
    
    with col3:
        st.subheader("Gerät löschen")
        st.write("Platzhalter: Nutzerliste")
        st.button("Gerät löschen")


elif selected_area == "Nutzer-Verwaltung":
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Nutzer anzeigen")
        st.write("Platzhalter: Nutzerliste / Details")
        st.button("Nutzer anzeigen")

    with col2:
        st.subheader("Nutzer verwalten")
        st.write("Platzhalter: Nutzerliste")
        st.button("Nutzer verwalten")

    with col3:
        st.subheader("Nutzer löschen")
        st.write("Platzhalter: Nutzerliste")
        st.button("Nutzer löschen")


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