import streamlit as st
import random
import os

# --- 1. CONFIGURATIE & STYLING ---
st.set_page_config(page_title="Putsie World", page_icon="🌍", layout="centered")

# CSS voor de "Putsie Balk"
st.markdown("""
    <style>
    .putsie-balk {
        background-color: #ffeb3b;
        padding: 10px;
        border-radius: 10px;
        border: 2px solid #fbc02d;
        color: black;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN LOGICA (Sidebar) ---
st.sidebar.title("🌍 Putsie World Login")
username = st.sidebar.text_input("Gebruikersnaam", value="gast").strip().lower()

if not username:
    st.warning("Vul een naam in de zijbalk in om te beginnen!")
    st.stop()

# Bestandsnamen per gebruiker
user_words_file = f"woorden_{username}.txt"
user_stats_file = f"stats_{username}.txt"

# --- 3. DATA LADEN & INITIALISEREN ---
def laad_data():
    # Stats laden
    if not os.path.exists(user_stats_file):
        with open(user_stats_file, "w") as f: f.write("0;0")
    
    with open(user_stats_file, "r") as f:
        content = f.read().split(";")
        if 'geld' not in st.session_state:
            st.session_state.geld = int(content[0])
            st.session_state.land = int(content[1])

    # Woorden laden
    woorden = {}
    if os.path.exists(user_words_file):
        with open(user_words_file, "r", encoding="utf-8") as f:
            for line in f:
                d = line.strip().split(";")
                if len(d) == 2:
                    woorden[d[0]] = d[1]
    return woorden

def save_stats():
    with open(user_stats_file, "w") as f:
        f.write(f"{st.session_state.geld};{st.session_state.land}")

woorden_lijst = laad_data()

# --- 4. DE PUTSIE BALK ---
st.markdown(f'<div class="putsie-balk">Putsie: Welkom {username.capitalize()}! Hoe gaat het met je koninkrijk?</div>', unsafe_allow_html=True)

# --- 5. HET DASHBOARD ---
col1, col2 = st.columns(2)
col1.metric("💰 Saldo", f"€{st.session_state.geld}")
col2.metric("🏰 Land", f"{st.session_state.land} km²")

st.divider()

# --- 6. MENU ---
menu = st.tabs(["🎮 Quiz", "➕ Toevoegen", "🏰 Winkel", "📖 Studie"])

# TAB 1: QUIZ
with menu[0]:
    if not woorden_lijst:
        st.info("Je hebt nog geen woorden! Ga naar het tabblad 'Toevoegen'.")
    else:
        if 'huidig_woord' not in st.session_state:
            st.session_state.huidig_woord = random.choice(list(woorden_lijst.keys()))
        
        woord = st.session_state.huidig_woord
        st.write(f"### Vertaal: **{woorden_lijst[woord]}**")
        antwoord = st.text_input("Typ de Franse vertaling:", key="quiz_input")

        if st.button("Check!"):
            if antwoord.lower().strip() == woord.lower():
                st.success("Helemaal goed! +€100")
                st.session_state.geld += 100
                save_stats()
                # Kies nieuw woord voor volgende ronde
                st.session_state.huidig_woord = random.choice(list(woorden_lijst.keys()))
                st.rerun()
            else:
                st.error(f"Helaas! Het juiste woord was: {woord}")

# TAB 2: TOEVOEGEN
with menu[1]:
    st.subheader("Nieuwe woorden leren")
    f_woord = st.text_input("Frans Woord (bijv. 'La pomme')")
    n_woord = st.text_input("Nederlandse Betekenis (bijv. 'De appel')")
    
    if st.button("Opslaan in mijn lijst"):
        if f_woord and n_woord:
            with open(user_words_file, "a", encoding="utf-8") as f:
                f.write(f"{f_woord.lower().strip()};{n_woord.lower().strip()}\n")
            st.success("Opgeslagen! Je kunt dit woord nu tegenkomen in de quiz.")
            st.rerun()

# TAB 3: WINKEL
with menu[2]:
    st.subheader("Breid je koninkrijk uit")
    st.write("Elke 10 km² kost €500.")
    if st.button("Koop land (+10 km²)"):
        if st.session_state.geld >= 500:
            st.session_state.geld -= 500
            st.session_state.land += 10
            save_stats()
            st.balloons()
            st.success("Gefeliciteerd! Je land is nu groter.")
            st.rerun()
        else:
            st.error("Je hebt niet genoeg geld. Doe meer quizes!")

# TAB 4: STUDIE
with menu[3]:
    st.subheader("Je Woordenlijst")
    if woorden_lijst:
        for f, n in woorden_lijst.items():
            st.write(f"🇫🇷 {f} = 🇳🇱 {n}")
    else:
        st.write("Lijst is nog leeg.")
