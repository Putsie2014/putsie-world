import streamlit as st
import json
import os
import random

# --- CONFIGURATIE ---
DB_FILE = "database.json"
st.set_page_config(page_title="Putsie Studios", layout="wide")

def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f: 
        return json.load(f)

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(db, f, indent=4)

# --- LOGIN & SESSIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"

if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login")
    u = st.text_input("Gebruikersnaam").lower().strip()
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Inloggen"):
        db = laad_db()
        if u not in db["users"]:
            # Nieuwe structuur met subcategorieën
            db["users"][u] = {"password": p, "geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}}
            sla_db_op(db)
        if db["users"][u]["password"] == p:
            st.session_state.ingelogd = True
            st.session_state.username = u
            st.rerun()
    st.stop()

# --- DATA LADEN & REPAREREN ---
db = laad_db()
u = st.session_state.username
data = db["users"][u]

# REPARATIE: Zorg dat de woorden-structuur altijd klopt
if "woorden" not in data: data["woorden"] = {"werkwoorden": {}, "woorden": {}}
if "werkwoorden" not in data["woorden"]: data["woorden"]["werkwoorden"] = {}
if "woorden" not in data["woorden"]: data["woorden"]["woorden"] = {}

# --- ZIJKANT ---
with st.sidebar:
    st.title(f"👤 {u.capitalize()}")
    st.write(f"💰 {data.get('geld', 0)}")
    st.write("---")
    st.write("### 🎓 Putsie Education")
    if st.button("🇫🇷 Frans", use_container_width=True): st.session_state.page = "Frans"
    st.write("### 📖 Putsie Strips")
    if st.button("📚 Strips", use_container_width=True): st.session_state.page = "Strips"
    st.write("### 🎮 Putsie Games")
    if st.button("🕹️ Games", use_container_width=True): st.session_state.page = "Games"
    st.write("### 🎵 Putsie Music")
    if st.button("🎧 Music", use_container_width=True): st.session_state.page = "Music"
    st.write("---")
    if st.button("Uitloggen", use_container_width=True): st.session_state.clear(); st.rerun()

# --- PAGINA'S ---
if st.session_state.page == "Frans":
    st.title("🎓 Putsie Education: Frans")
    tab1, tab2 = st.tabs(["Quizzen", "Woorden Toevoegen"])
    
    with tab1:
        cat = st.selectbox("Categorie", ["werkwoorden", "woorden"])
        if not data["woorden"].get(cat): st.info("Geen woorden in deze categorie.")
        else:
            if st.button("Nieuwe vraag"): st.session_state.vraag = random.choice(list(data["woorden"][cat].keys()))
            if 'vraag' in st.session_state:
                v = st.session_state.vraag
                st.write(f"Vertaal: **{data['woorden'][cat][v]}**")
                ant = st.text_input("Jouw antwoord:")
                if st.button("Check antwoord"):
                    if ant.lower().strip() == v.lower():
                        st.success("Correct! +10 munten")
                        data["geld"] += 10
                        sla_db_op(db)
                    else: st.error(f"Fout! Het was: {v}")

    with tab2:
        cat_toe = st.selectbox("Categorie toevoegen", ["werkwoorden", "woorden"])
        f = st.text_input("Frans woord:")
        n = st.text_input("Nederlands:")
        if st.button("Toevoegen"):
            data["woorden"][cat_toe][f.lower()] = n.lower()
            sla_db_op(db)
            st.success(f"Toegevoegd aan {cat_toe}!")

else:
    st.title(f"Welkom bij Putsie Studios: {st.session_state.page}")
