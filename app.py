import streamlit as st
import json
import os
import random

# --- 1. CONFIGURATIE ---
DB_FILE = "database.json"
st.set_page_config(page_title="Putsie Studios", layout="wide")

if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"

# --- 2. DATABASE ---
def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- 3. LOGIN ---
if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login")
    t1, t2 = st.tabs(["Inloggen", "Registreren"])
    db = laad_db()
    with t1:
        u = st.text_input("Naam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Log in"):
            if u in db["users"] and db["users"][u]["password"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Fout!")
    with t2:
        ru = st.text_input("Kies Naam", key="r_u").lower().strip()
        rp = st.text_input("Kies Wachtwoord", type="password", key="r_p")
        if st.button("Maak Account"):
            if ru and rp and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}}
                sla_db_op(db)
                st.success("Klaar! Log nu in.")
    st.stop()

# --- 4. DATA & FIXES ---
db = laad_db()
user = st.session_state.username
data = db["users"][user]
# Zorg dat de structuur altijd klopt
if "woorden" not in data: data["woorden"] = {"werkwoorden": {}, "woorden": {}}

# --- 5. ZIJKANT ---
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

# --- 6. PAGINA: FRANS ---
if st.session_state.page == "Frans":
    st.title("🎓 Putsie Education: Frans")
    
    # Bereken totaal aantal woorden voor de 10-woorden-grens
    totaal_woorden = len(data["woorden"]["woorden"]) + len(data["woorden"]["werkwoorden"])
    
    tab1, tab2 = st.tabs(["🎯 Quiz", "➕ Toevoegen"])
    
    with tab1:
        if totaal_woorden < 10:
            st.warning(f"⚠️ Je hebt nog maar {totaal_woorden} woorden. Voeg er minstens 10 toe om de quiz te kunnen spelen!")
        else:
            cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
            lijst = data["woorden"][cat]
            
            if not lijst:
                st.info(f"Je hebt geen woorden in de categorie '{cat}'.")
            else:
                if st.button("Nieuwe Vraag 🆕"):
                    st.session_state.vraag = random.choice(list(lijst.keys()))
                    st.session_state.answered = False
                
                if 'vraag' in st.session_state:
                    v = st.session_state.vraag
                    st.subheader(f"Vertaal: **{lijst[v]}**")
                    with st.form(key="q_form", clear_on_submit=True):
                        # .lower().strip() zorgt dat hoofdletters en spaties niet uitmaken!
                        ant = st.text_input("Antwoord:").lower().strip()
                        if st.form_submit_button("Check ✅"):
                            if st.session_state.get('answered', False):
                                st.warning("Al beantwoord!")
                            elif ant == v.lower().strip():
                                data["geld"] += 15
                                sla_db_op(db)
                                st.session_state.answered = True
                                st.success("Correct! +€15")
                                st.balloons()
                            else:
                                st.error(f"Fout! Het was: {v}")

    with tab2:
        st.subheader("Voeg woorden toe (Je hebt er nu: {0})".format(totaal_woorden))
        with st.form(key="add_f", clear_on_submit=True):
            c_t = st.selectbox("Type", ["woorden", "werkwoorden"])
            f_w = st.text_input("Frans:").lower().strip()
            n_w = st.text_input("Nederlands:").lower().strip()
            if st.form_submit_button("Opslaan 💾"):
                if f_w and n_w:
                    data["woorden"][c_t][f_w] = n_w
                    sla_db_op(db)
                    st.success(f"'{f_w}' toegevoegd!")
                    st.rerun() # Refresh om de teller direct bij te werken

# --- OVERIGE PAGINA'S ---
elif st.session_state.page == "Strips": st.title("📖 Putsie Strips")
elif st.session_state.page == "Games": st.title("🕹️ Putsie Games")
elif st.session_state.page == "Music": st.title("🎵 Putsie Music")
else:
    st.title("🏠 Home")
    st.write(f"Welkom bij Putsie Studios, **{user}**!")
