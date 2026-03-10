import streamlit as st
import json
import os
import random

# --- CONFIGURATIE ---
DB_FILE = "database.json"
st.set_page_config(page_title="Putsie Studios", layout="wide")

# --- DATABASE FUNCTIES ---
def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- SESSIE INITIALISATIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"

# --- LOGIN LOGICA (Blijft voor de zijbalk) ---
if not st.session_state.ingelogd:
    st.title("🌍 Welkom bij Putsie Studios")
    with st.form("login_form"):
        u = st.text_input("Gebruikersnaam").lower().strip()
        p = st.text_input("Wachtwoord", type="password")
        if st.form_submit_button("Inloggen / Registreren"):
            db = laad_db()
            if u not in db["users"]:
                db["users"][u] = {"password": p, "geld": 0, "land": 0, "woorden": {}}
                sla_db_op(db)
            if db["users"][u]["password"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Wachtwoord fout!")
    st.stop()

# --- ZIJKANT: MENU (Nu met data toegang) ---
db = laad_db()
user = st.session_state.username
u_data = db["users"][user]

with st.sidebar:
    st.title(f"👤 {user.capitalize()}")
    st.write(f"💰 {u_data['geld']} | 🏰 {u_data['land']}km²")
    st.write("---")
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    st.write("### 🎓 Putsie Education")
    if st.button("🇫🇷 Frans", use_container_width=True): st.session_state.page = "Frans"
    st.write("### 📖 Putsie Strips")
    if st.button("📚 Strips", use_container_width=True): st.session_state.page = "Strips"
    st.write("### 🎮 Putsie Games")
    if st.button("🕹️ Games", use_container_width=True): st.session_state.page = "Games"
    st.write("### 🎵 Putsie Music")
    if st.button("🎧 Music", use_container_width=True): st.session_state.page = "Music"
    st.write("---")
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- PAGINA'S ---
if st.session_state.page == "Home":
    st.title("Welkom bij Putsie Studios!")
    st.write("Kies een onderdeel in het menu aan de linkerkant.")

elif st.session_state.page == "Frans":
    st.title("🎓 Putsie Education: Frans")
    # Hier staat je vertrouwde quiz-logica
    if not u_data["woorden"]:
        st.info("Voeg eerst woorden toe!")
    else:
        if 'vraag' not in st.session_state: st.session_state.vraag = random.choice(list(u_data["woorden"].keys()))
        v = st.session_state.vraag
        st.write(f"Vertaal: **{u_data['woorden'][v]}**")
        with st.form("quiz", clear_on_submit=True):
            p = st.text_input("Antwoord:")
            if st.form_submit_button("Check"):
                if p.lower().strip() == v.lower():
                    u_data["geld"] += 100
                    sla_db_op(db)
                    st.success("Goed! +€100")
                    del st.session_state.vraag
                    st.rerun()
                else: st.error(f"Fout! Het was: {v}")

    st.write("---")
    with st.form("add_word", clear_on_submit=True):
        f = st.text_input("Frans:")
        n = st.text_input("Nederlands:")
        if st.form_submit_button("Toevoegen"):
            u_data["woorden"][f.lower()] = n.lower()
            sla_db_op(db)
            st.success("Toegevoegd!")

# Hier kun je de rest van de pagina's (Strips, Games, Music) verder uitbouwen
