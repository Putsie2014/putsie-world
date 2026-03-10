import streamlit as st
import json
import os
import random

# --- 1. CONFIGURATIE & INITIALISATIE ---
DB_FILE = "database.json"
st.set_page_config(page_title="Putsie Studios", layout="wide")

if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'username' not in st.session_state: st.session_state.username = None

# --- 2. BULLETPROOF DATABASE FUNCTIES ---
def laad_db():
    if not os.path.exists(DB_FILE): 
        return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except:
        return {"users": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(db, f, indent=4)

# --- 3. LOGIN SYSTEEM ---
if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Welkom")
    tab_log, tab_reg = st.tabs(["Inloggen", "Nieuw Account"])
    db = laad_db()
    
    with tab_log:
        u_log = st.text_input("Gebruikersnaam", key="u_log").lower().strip()
        p_log = st.text_input("Wachtwoord", type="password", key="p_log")
        if st.button("Log in"):
            if u_log in db["users"] and db["users"][u_log]["password"] == p_log:
                st.session_state.ingelogd = True
                st.session_state.username = u_log
                st.rerun()
            else:
                st.error("Gebruiker niet gevonden of wachtwoord fout.")

    with tab_reg:
        u_reg = st.text_input("Kies Gebruikersnaam", key="u_reg").lower().strip()
        p_reg = st.text_input("Kies Wachtwoord", type="password", key="p_reg")
        if st.button("Registreer"):
            if u_reg and p_reg:
                if u_reg not in db["users"]:
                    db["users"][u_reg] = {"password": p_reg, "geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}}
                    sla_db_op(db)
                    st.success("Account aangemaakt! Log nu in.")
                else: st.warning("Deze naam bestaat al.")
    st.stop()

# --- 4. DATA VALIDATIE ---
db = laad_db()
user = st.session_state.username
if "woorden" not in db["users"][user]: db["users"][user]["woorden"] = {"werkwoorden": {}, "woorden": {}}
if "werkwoorden" not in db["users"][user]["woorden"]: db["users"][user]["woorden"]["werkwoorden"] = {}
if "woorden" not in db["users"][user]["woorden"]: db["users"][user]["woorden"]["woorden"] = {}
data = db["users"][user]

# --- 5. ZIJKANT NAVIGATIE ---
with st.sidebar:
    st.title(f"👤 {user.capitalize()}")
    st.metric("Saldo", f"€{data['geld']}")
    st.write("---")
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    st.write("### 🎓 Education")
    if st.button("🇫🇷 Frans & Werkwoorden", use_container_width=True): st.session_state.page = "Frans"
    st.write("### 📖 Entertainment")
    if st.button("📚 Putsie Strips", use_container_width=True): st.session_state.page = "Strips"
    if st.button("🕹️ Putsie Games", use_container_width=True): st.session_state.page = "Games"
    if st.button("🎧 Putsie Music", use_container_width=True): st.session_state.page = "Music"
    st.write("---")
    if st.button("Uitloggen", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 6. PAGINA: FRANS ---
if st.session_state.page == "Frans":
    st.title("🎓 Putsie Education: Frans")
    t1, t2 = st.tabs(["🎯 Quiz", "➕ Woorden Toevoegen"])
    
    with t1:
        cat = st.selectbox("Kies Categorie", ["woorden", "werkwoorden"])
        lijst = data["woorden"][cat]
        
        if not lijst:
            st.info("Voeg eerst woorden toe bij het tabblad 'Toevoegen'.")
        else:
            if st.button("Nieuwe Vraag 🆕"):
                st.session_state.vraag = random.choice(list(lijst.keys()))
                st.session_state.answered = False
            
            if 'vraag' in st.session_state:
                v = st.session_state.vraag
                st.subheader(f"Vertaal naar het Frans: **{lijst[v]}**")
                
                # FORMULIER ZORGT DAT VAKJE LEEG WORDT NA KLIKKEN
                with st.form(key="quiz_form", clear_on_submit=True):
                    ant = st.text_input("Antwoord:").lower().strip()
                    submit = st.form_submit_button("Check Antwoord ✅")
                    
                    if submit:
                        if st.session_state.get('answered', False):
                            st.warning("Je hebt al geld gekregen voor deze vraag!")
                        elif ant == v:
                            data["geld"] += 15
                            sla_db_op(db)
                            st.session_state.answered = True
                            st.success(f"Helemaal goed! +€15. Klik op 'Nieuwe Vraag' voor de volgende.")
                            st.balloons() # DE LEUKE BALLONNEN!
                        else:
                            st.error(f"Helaas! Het juiste antwoord was: {v}")

    with t2:
        st.subheader("Voeg nieuwe items toe")
        # FORMULIER VOOR TOEVOEGEN (MAAKT VAKJES OOK LEEG)
        with st.form(key="add_form", clear_on_submit=True):
            c_toe = st.selectbox("Type:", ["woorden", "werkwoorden"])
            f_w = st.text_input("Frans woord:")
            n_w = st.text_input("Nederlandse vertaling:")
            if st.form_submit_button("Opslaan in Database 💾"):
                if f_w and n_w:
                    data["woorden"][c_toe][f_w.lower()] = n_w.lower()
                    sla_db_op(db)
                    st.success(f"'{f_w}' is succesvol opgeslagen!")
                else:
                    st.warning("Vul beide vakjes in!")

# --- OVERIGE PAGINA'S (STRIKT BEHOUDEN) ---
elif st.session_state.page == "Strips": st.title("📖 Putsie Strips")
elif st.session_state.page == "Games": st.title("🕹️ Putsie Games")
elif st.session_state.page == "Music": st.title("🎵 Putsie Music")
else:
    st.title("🏠 Putsie Studios Home")
    st.write(f"Welkom, **{user}**! Je saldo is **€{data['geld']}**.")
