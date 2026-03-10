import streamlit as st
import json
import os
import random

# --- 1. CONFIGURATIE ---
DB_FILE = "database.json"
st.set_page_config(page_title="Putsie Studios", layout="wide")

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": {}}, f)

def laad_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

init_db()

if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"

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
data = db["users"].get(user, {"geld": 0, "woorden": {"werkwoorden": {}, "woorden": {}}})

with st.sidebar:
    st.title(f"👤 {user.capitalize()}")
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    st.write("---")
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden", use_container_width=True): st.session_state.page = "Frans"
    if st.button("📖 Strips", use_container_width=True): st.session_state.page = "Strips"
    if st.button("🕹️ Games", use_container_width=True): st.session_state.page = "Games"
    if st.button("🎧 Music", use_container_width=True): st.session_state.page = "Music"
    st.write("---")
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA'S ---
if st.session_state.page == "Frans":
    st.title("🎓 Putsie Education: Frans")
    t1, t2, t3 = st.tabs(["🎯 Quiz", "➕ Toevoegen", "📋 Overzicht"])
    
    with t1:
        if len(data["woorden"]["woorden"]) + len(data["woorden"]["werkwoorden"]) < 10:
            st.warning("Voeg minstens 10 woorden toe!")
        else:
            cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
            if st.button("Nieuwe Vraag 🆕"):
                if cat == "woorden": 
                    st.session_state.vraag = random.choice(list(data["woorden"]["woorden"].keys()))
                else: 
                    st.session_state.vraag = random.choice(list(data["woorden"]["werkwoorden"].keys()))
                    st.session_state.vorm = random.choice(["je", "tu", "il", "nous", "vous", "ils"])
                st.session_state.answered = False
                st.rerun()
            
            if 'vraag' in st.session_state:
                v = st.session_state.vraag
                lijst = data["woorden"][cat]
                if v in lijst:
                    with st.form(key="q_form", clear_on_submit=True):
                        if cat == "woorden": 
                            st.write(f"Vertaal: **{lijst[v]}**")
                            juist = v
                        else: 
                            st.write(f"Vervoeg **{v}** ({lijst[v]['ned']}) - **{st.session_state.vorm}**:")
                            juist = lijst[v][st.session_state.vorm]
                        ant = st.text_input("Antwoord:").lower().strip()
                        if st.form_submit_button("Check ✅"):
                            if ant == juist:
                                data["geld"] += 15
                                db["users"][user] = data
                                sla_db_op(db)
                                st.success("Correct! +€15"); st.balloons()
                            else: st.error(f"Fout! Het was: {juist}")

    with t2:
        keuze = st.radio("Wat voeg je toe?", ["Woord", "Werkwoord"])
        if keuze == "Woord":
            with st.form("add_w", clear_on_submit=True):
                f = st.text_input("Frans:").lower().strip()
                n = st.text_input("Nederlands:").lower().strip()
                if st.form_submit_button("Opslaan"):
                    data["woorden"]["woorden"][f] = n
                    db["users"][user] = data; sla_db_op(db); st.rerun()
        else:
            with st.form("add_ww", clear_on_submit=True):
                inf = st.text_input("Heel werkwoord:").lower().strip()
                ned = st.text_input("Betekenis:").lower().strip()
                c1, c2 = st.columns(2)
                with c1:
                    je = st.text_input("Je:"); tu = st.text_input("Tu:"); il = st.text_input("Il/Elle:")
                with c2:
                    nous = st.text_input("Nous:"); vous = st.text_input("Vous:"); ils = st.text_input("Ils/Elles:")
                if st.form_submit_button("Werkwoord Opslaan 💾"):
                    data["woorden"]["werkwoorden"][inf] = {"ned": ned, "je": je, "tu": tu, "il": il, "nous": nous, "vous": vous, "ils": ils}
                    db["users"][user] = data; sla_db_op(db); st.rerun()

    with t3:
        st.subheader("Jouw Woordenlijst")
        st.write("### Woorden", data["woorden"]["woorden"])
        st.write("### Werkwoorden", data["woorden"]["werkwoorden"])

elif st.session_state.page == "Strips": st.title("📖 Putsie Strips")
elif st.session_state.page == "Games": st.title("🕹️ Putsie Games")
elif st.session_state.page == "Music": st.title("🎵 Putsie Music")
else: st.title("🏠 Welkom bij Putsie Studios!")

# --- 5. BEHEERDERS PANEEL ---
ADMIN_LIJST = ["elliot", "admin"] 
if st.session_state.ingelogd and st.session_state.username.lower() in ADMIN_LIJST:
    with st.sidebar:
        st.write("---")
        st.subheader("⚙️ Beheerpaneel")
        if st.button("Beheer Spelers"): st.session_state.page = "Admin"

if st.session_state.page == "Admin":
    if st.session_state.username.lower() in ADMIN_LIJST:
        st.title("🛡️ Beheer: Putsie Studios")
        db = laad_db()
        alle_spelers = list(db["users"].keys())
        te_beheren = st.selectbox("Selecteer speler:", alle_spelers)
        if te_beheren:
            gebruiker_data = db["users"][te_beheren]
            st.write(f"### Instellingen voor: **{te_beheren.capitalize()}**")
            huidig_geld = gebruiker_data.get("geld", 0)
            nieuw_geld = st.number_input("Pas saldo aan:", value=huidig_geld, step=1)
            if st.button("Sla saldo op"):
                db["users"][te_beheren]["geld"] = int(nieuw_geld)
                sla_db_op(db); st.rerun()
            
            st.write("### Overzicht Woordenlijsten")
            col1, col2 = st.columns(2)
            with col1: st.json(gebruiker_data["woorden"]["woorden"])
            with col2: st.json(gebruiker_data["woorden"]["werkwoorden"])
