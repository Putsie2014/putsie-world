import streamlit as st
import json
import os
import random

# --- 1. CONFIGURATIE & INITIALISATIE ---
DB_FILE = "database.json"
st.set_page_config(page_title="Putsie Studios", layout="wide")

if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"

def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- 2. LOGIN ---
if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login")
    tab1, tab2 = st.tabs(["Inloggen", "Registreren"])
    db = laad_db()
    with tab1:
        u = st.text_input("Naam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Log in"):
            if u in db["users"] and db["users"][u]["password"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Fout!")
    with tab2:
        ru = st.text_input("Kies Naam", key="r_u").lower().strip()
        rp = st.text_input("Kies Wachtwoord", type="password", key="r_p")
        if st.button("Maak Account"):
            if ru and rp and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}}
                sla_db_op(db)
                st.success("Account aangemaakt!")
    st.stop()

# --- 3. DATA & ZIJKANT ---
db = laad_db()
user = st.session_state.username
data = db["users"][user]
if "woorden" not in data: data["woorden"] = {"werkwoorden": {}, "woorden": {}}

with st.sidebar:
    st.title(f"👤 {user.capitalize()}")
    st.metric("Saldo", f"€{data['geld']}")
    st.write("---")
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    st.write("### 🎓 Education")
    if st.button("🇫🇷 Frans", use_container_width=True): st.session_state.page = "Frans"
    st.write("### 📖 Entertainment")
    if st.button("📚 Strips", use_container_width=True): st.session_state.page = "Strips"
    if st.button("🕹️ Games", use_container_width=True): st.session_state.page = "Games"
    if st.button("🎧 Music", use_container_width=True): st.session_state.page = "Music"
    st.write("---")
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA'S ---
if st.session_state.page == "Frans":
    st.title("🎓 Putsie Education: Frans")
    t1, t2 = st.tabs(["🎯 Quiz", "➕ Toevoegen"])
    
    with t1:
        if len(data["woorden"]["woorden"]) + len(data["woorden"]["werkwoorden"]) < 10:
            st.warning("Voeg minstens 10 woorden toe om de quiz te ontgrendelen!")
        else:
            cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
            if st.button("Nieuwe Vraag 🆕"):
                st.session_state.vraag = random.choice(list(data["woorden"][cat].keys()))
                st.session_state.answered = False
            if 'vraag' in st.session_state:
                v = st.session_state.vraag
                with st.form(key="q_form", clear_on_submit=True):
                    st.write(f"Vertaal: **{data['woorden'][cat][v]}**")
                    ant = st.text_input("Antwoord:").lower().strip()
                    if st.form_submit_button("Check ✅"):
                        if not st.session_state.get('answered', False) and ant == v:
                            data["geld"] += 15
                            sla_db_op(db)
                            st.session_state.answered = True
                            st.success("Correct! +€15"); st.balloons()
                        else: st.error("Fout of al beantwoord.")

    with t2:
        st.write("Voeg toe aan de database:")
        c_t = st.selectbox("Type", ["woorden", "werkwoorden"])
        with st.form("add", clear_on_submit=True):
            f_w = st.text_input("Frans:").lower().strip()
            n_w = st.text_input("Nederlands:").lower().strip()
            if st.form_submit_button("Opslaan 💾"):
                data["woorden"][c_t][f_w] = n_w
                sla_db_op(db)
                st.success("Toegevoegd!")

elif st.session_state.page == "Strips": st.title("📖 Putsie Strips")
elif st.session_state.page == "Games": st.title("🕹️ Putsie Games")
elif st.session_state.page == "Music": st.title("🎵 Putsie Music")
else: st.title("🏠 Welkom bij Putsie Studios!")
