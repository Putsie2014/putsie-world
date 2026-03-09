import streamlit as st
import random
import os

# --- 1. PAGINA INSTELLINGEN ---
st.set_page_config(page_title="Putsie World Online", page_icon="🌍")

# --- 2. INLOG SYSTEEM (Zijbalk) ---
st.sidebar.title("🔐 Inloggen")
username = st.sidebar.text_input("Vul je naam in:", key="user_login").strip().lower()

if not username:
    st.title("🌍 Welkom bij Putsie World")
    st.info("Vul je naam in de zijbalk in om je koninkrijk te laden of een nieuwe te starten!")
    st.stop() # Stop hier zodat de rest van de app niet laadt zonder naam

# Bestandsnamen koppelen aan de unieke gebruiker
user_stats_file = f"stats_{username}.txt"
user_words_file = f"woorden_{username}.txt"

# --- 3. DATA LADEN FUNCTIES ---
def laad_gebruiker_data():
    # Als de gebruiker nieuw is, maak basisbestanden aan
    if not os.path.exists(user_stats_file):
        with open(user_stats_file, "w") as f:
            f.write("0;0") # Start met 0 geld en 0 land
    
    # Laad geld en land in de sessie (tijdelijk geheugen van de browser)
    with open(user_stats_file, "r") as f:
        data = f.read().split(";")
        st.session_state.geld = int(data[0])
        st.session_state.land = int(data[1])

def sla_data_op():
    with open(user_stats_file, "w") as f:
        f.write(f"{st.session_state.geld};{st.session_state.land}")

# Initialiseer de data voor de ingelogde gebruiker
if 'huidige_gebruiker' not in st.session_state or st.session_state.huidige_gebruiker != username:
    laad_gebruiker_data()
    st.session_state.huidige_gebruiker = username

# --- 4. DE APP INTERFACE ---
st.title(f"🌍 Koninkrijk van {username.capitalize()}")

# Dashboard met statistieken
col1, col2 = st.columns(2)
col1.metric("💰 Saldo", f"€{st.session_state.geld}")
col2.metric("🏰 Landgrootte", f"{st.session_state.land} km²")

st.divider()

# Menu met Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Quiz", "📝 Woorden Toevoegen", "🛒 Winkel"])

# --- TAB 1: DE QUIZ ---
with tab1:
    woorden = {}
    if os.path.exists(user_words_file):
        with open(user_words_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) == 2:
                    woorden[parts[0]] = parts[1]

    if not woorden:
        st.warning("Je hebt nog geen woorden in je lijst! Ga naar 'Woorden Toevoegen'.")
    else:
        if 'vraag_woord' not in st.session_state:
            st.session_state.vraag_woord = random.choice(list(woorden.keys()))
        
        vraag = st.session_state.vraag_woord
        st.write(f"### Vertaal naar het Frans: **{woorden[vraag]}**")
        
        poging = st.text_input("Jouw antwoord:", key="quiz_input")
        
        if st.button("Controleren"):
            if poging.lower().strip() == vraag.lower():
                st.success("🎉 Goed gedaan! Je verdient €100.")
                st.session_state.geld += 100
                sla_data_op()
                del st.session_state.vraag_woord # Verwijder woord zodat er een nieuwe komt
                st.rerun()
            else:
                st.error(f"Helaas! Het juiste antwoord was: {vraag}")

# --- TAB 2: WOORDEN TOEVOEGEN ---
with tab2:
    st.subheader("Voeg nieuwe woorden toe aan je account")
    nieuw_frans = st.text_input("Frans woord:")
    nieuw_nl = st.text_input("Nederlandse vertaling:")
    
    if st.button("Opslaan"):
        if nieuw_frans and nieuw_nl:
            with open(user_words_file, "a", encoding="utf-8") as f:
                f.write(f"{nieuw_frans.lower().strip()};{nieuw_nl.lower().strip()}\n")
            st.success(f"'{nieuw_frans}' is toegevoegd aan jouw lijst!")
            st.rerun()

# --- TAB 3: DE WINKEL ---
with tab3:
    st.subheader("Breid je land uit")
    st.write("Kosten: €500 voor 10 km² extra.")
    if st.button("Koop 10 km² Land"):
        if st.session_state.geld >= 500:
            st.session_state.geld -= 500
            st.session_state.land += 10
            sla_data_op()
            st.balloons()
            st.success("Je land is gegroeid!")
            st.rerun()
        else:
            st.error("Je hebt niet genoeg geld! Doe meer quizzen.")

# Uitlog knop onderaan de zijbalk
if st.sidebar.button("Uitloggen"):
    st.session_state.clear()
    st.rerun()
