
import streamlit as st
import time

# Getränke Definition
GETRAENKE = {
    "Wasser": 1.50,
    "Cola": 2.00,
    "Fanta Orange": 2.00,
    "Sprite": 2.00,
    "Kaffee": 1.50,
    "Tee": 1.00,
    "Saft": 2.50,
    "Flying Muh": 1.80,
}

# Initialize state
if "state" not in st.session_state:
    st.session_state["state"] = "Auswahl anfordern"
if "selected_drink" not in st.session_state:
    st.session_state["selected_drink"] = None

# Callback function to change state
# Callback function are triggered when the button is clicked
def go_to_state_start():
    st.session_state["state"] = "Auswahl anfordern"
    st.session_state["selected_drink"] = None

def go_to_state_bez(drink):
    st.session_state["selected_drink"] = drink
    st.session_state["state"] = "Bezahlung anfordern"

def go_to_state_rueck():
    st.session_state["state"] = "Rueckgabe anfordern"

def go_to_state_ausgeben():
    st.session_state["state"] = "Ware ausgeben"

if st.session_state["state"] == "Auswahl anfordern":
    st.title("Getraenkeautomat")
    st.header("Auswahl treffen")
    
    # Display drinks as buttons
    cols = st.columns(2)
    for idx, (drink, price) in enumerate(GETRAENKE.items()):
        with cols[idx % 2]:
            st.button(
                f"{drink}\n€{price:.2f}",
                on_click=go_to_state_bez,
                args=(drink,),
                use_container_width=True
            )
    
    st.divider()
    st.button("Rückgabe anfordern!", type="secondary", on_click=go_to_state_rueck)    

elif st.session_state["state"] == "Bezahlung anfordern":
    drink = st.session_state["selected_drink"]
    price = GETRAENKE[drink]
    st.title(f"Bezahlung fuer: {drink}")
    st.info(f"Preis: €{price:.2f}")
    st.button("Bezahlung akzeptiert!", type="primary", on_click=go_to_state_ausgeben)
    st.button("Abbrechen", on_click=go_to_state_start)

elif st.session_state["state"] == "Rueckgabe anfordern":
    st.title("Rueckgabe anfordern")
    st.info("Bitte geben Sie die geleerte Flasche zurueck.")
    st.button("Rückgabe abgeschlossen!", type="primary", on_click=go_to_state_start)

elif st.session_state["state"] == "Ware ausgeben":
    drink = st.session_state["selected_drink"]
    st.title(f"Ware wird ausgegeben: {drink}")
    st.success(f"Geniessen Sie Ihr {drink}!")
    time.sleep(2)
    st.button("Restart!", type="primary", on_click=go_to_state_start)
