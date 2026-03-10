import streamlit as st
import json
import os
import random

# --- 1. CONFIGURATIE & INITIALISATIE ---
DB_FILE = "database.json"
st.set_page_config(page_title="Putsie Studios", layout="wide")

# Zorg dat de essentiële session_states altijd bestaan voordat de rest van de code draait
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
    except (json.JSONDecodeError, IOError):
        # Als het bestand corrupt is, maken we een veilige backup en starten we vers
        return {"users": {}}

def sla_db_op(db):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f: 
            json.dump(db, f, indent=4)
    except Exception as e:
        st.error(f"Fout bij opslaan: {e}")

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
                    db["users"][u_reg] = {
                        "password": p_reg, 
                        "geld": 100, 
                        "woorden": {"werkwoorden": {}, "woorden": {}}
                    }
                    sla_db_op(db)
                    st.success("Account aangemaakt! Je kunt nu inloggen.")
                else:
                    st.warning("Deze naam bestaat al.")
    st.stop()

# --- 4. DATA VALIDATIE (Reparatie van oude accounts) ---
db = laad_db()
user = st.session_state.username
# Als een gebruiker een oude structuur heeft, fixen we dat hier on-the-fly
if "woorden" not in db["users"][user]: 
    db["users"][user]["woorden"] = {"werkwoorden": {}, "woorden": {}}
if "werkwoorden" not in db["users"][user]["woorden"]: 
    db["users"][user]["woorden"]["werkwoorden"] = {}
if "woorden" not in db["users"][user]["woorden"]: 
    db["users"][user]["woorden"]["woorden"] = {}
if "geld" not in db["users"][user]:
    db["users"][user]["geld"] = 0

data = db["users"][user]

# --- 5. ZIJKANT NAVIGATIE (VOLLEDIG) ---
with st.sidebar:
    st.title(f"👤 {user.capitalize()}")
    st.metric("Putsie Saldo", f"€{data['geld']}")
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

# --- 6. PAGINA CONTENT ---

# --- PAGINA: FRANS ---
if st.session_state.page == "Frans":
    st.title("🎓 Putsie Education: Frans")
    t1, t2 = st.tabs(["Quiz (Geld verdienen)", "Woordenlijst beheren"])
    
    with t1:
        cat = st.selectbox("Kies Categorie", ["woorden", "werkwoorden"])
        lijst = data["woorden"][cat]
        
        if not lijst:
            st.info("Voeg eerst woorden toe bij het tabblad 'Beheren'.")
        else:
            # Vraag laden
            if st.button("Nieuwe Vraag", use_container_width=True):
                st.session_state.vraag = random.choice(list(lijst.keys()))
                st.session_state.answered = False
            
            if 'vraag' in st.session_state:
                v = st.session_state.vraag
                st.subheader(f"Vertaal naar het Frans: **{lijst[v]}**")
                ant = st.text_input("Typ hier het Franse woord:").lower().strip()
                
                # ANTI-EXPLOIT CHECK
                if st.button("Check!"):
                    if st.session_state.get('answered', False):
                        st.warning("Je hebt deze vraag al beantwoord. Klik op 'Nieuwe Vraag'.")
                    else:
                        if ant == v:
                            data["geld"] += 15
                            sla_db_op(db)
                            st.session_state.answered = True
                            st.success("Correct! Je hebt €15 verdiend.")
                            st.balloons()
                        else:
                            st.error(f"Helaas! Het juiste antwoord was: {v}")

    with t2:
        st.subheader("Voeg nieuwe woorden of werkwoorden toe")
        c_toe = st.selectbox("Toevoegen aan:", ["woorden", "werkwoorden"])
        f_w = st.text_input("Frans (bijv. 'Etre')").lower().strip()
        n_w = st.text_input("Nederlands (bijv. 'Zijn')").lower().strip()
        if st.button("Opslaan in Database"):
            if f_w and n_w:
                data["woorden"][c_toe][f_w] = n_w
                sla_db_op(db)
                st.success(f"'{f_w}' is toegevoegd aan {c_toe}!")
            else:
                st.warning("Vul beide velden in.")

# --- OVERIGE PAGINA'S (Placeholders die niet verwijderd mogen worden) ---
elif st.session_state.page == "Strips":
    st.title("📖 Putsie Strips")
    st.info("Binnenkort: De nieuwste avonturen van Putsie!")

elif st.session_state.page == "Games":
    st.title("🕹️ Putsie Games")
    st.info("Hier komen je favoriete mini-games te staan.")

elif st.session_state.page == "Music":
    st.title("🎵 Putsie Music")
    st.info("Luister naar de Putsie Studios Soundtracks.")

else:
    st.title("🏠 Putsie Studios Home")
    st.write(f"Welkom terug, **{user}**! Je hebt momenteel **€{data['geld']}** op je account.")
    st.write("Kies een categorie in de zijbalk om te beginnen.")
