import streamlit as st
import json
import os
import random
import string

# --- 1. CONFIGURATIE ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
st.set_page_config(page_title="Putsie Studios", layout="wide")

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": {}, "klassen": {}}, f)

def laad_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            if "klassen" not in db: db["klassen"] = {}
            return db
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

init_db()

# --- 2. LOGIN & REGISTRATIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login/Registratie")
    db = laad_db()
    tab1, tab2 = st.tabs(["Inloggen", "Account aanmaken"])
    with tab1:
        u = st.text_input("Naam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Log in"):
            if u in db["users"] and db["users"][u].get("password") == p:
                st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
            else: st.error("Fout!")
    with tab2:
        ru = st.text_input("Kies Naam", key="r_u").lower().strip()
        rp = st.text_input("Kies Wachtwoord", type="password", key="r_p")
        if st.button("Maak Account"):
            if ru and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}, "klas_id": None}
                sla_db_op(db); st.success("Account gemaakt!"); st.rerun()
    st.stop()

# --- 3. GEDEELDE DATA ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}, "klas_id": None})

# --- 4. ZIJKANT ---
with st.sidebar:
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    if st.button("🏠 Home"): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden"): st.session_state.page = "Frans"
    if st.button("🏫 Klaslokaal"): st.session_state.page = "Klas"
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- PAGINA LOGICA: KLAS (Quiz-integratie toegevoegd) ---
elif page == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    
    # LEERKRACHT GEDEELTE
    if user.lower() in LEERKRACHTEN:
        # ... (je bestaande leerkracht code) ...
        pass 
        
    # LEERLING GEDEELTE
    else:
        if not data.get("klas_id"):
            # ... (je bestaande join code) ...
            c = st.text_input("Vul klascode in:").upper()
            if st.button("Deelnemen"):
                if c in db["klassen"]:
                    data["klas_id"] = c; db["users"][user] = data; sla_db_op(db); st.rerun()
        else:
            klas_id = data.get("klas_id")
            klas = db["klassen"].get(klas_id, {})
            st.subheader(f"Jouw Klas: {klas.get('naam', 'Niet gevonden')}")
            
            # Taken lijst
            for i, taak in enumerate(klas.get("taken", [])):
                if st.button(f"Start Taak: {taak['taak']}", key=f"start_{i}"):
                    st.session_state.actieve_taak = i
                    st.rerun()
            
            # QUIZ LOGICA VOOR TAAK
            if 'actieve_taak' in st.session_state:
                taak_idx = st.session_state.actieve_taak
                taak = klas["taken"][taak_idx]
                
                st.write(f"---")
                st.subheader(f"Quiz voor: {taak['taak']}")
                
                # Pak een random woord uit de eigen woordenlijst van de gebruiker
                woorden_lijst = list(data["woorden"]["woorden"].keys())
                if woorden_lijst:
                    vraag = random.choice(woorden_lijst)
                    antwoord = st.text_input(f"Vertaal: {vraag}")
                    
                    if st.button("Controleer antwoord"):
                        if antwoord.lower() == data["woorden"]["woorden"][vraag].lower():
                            # Taak gelukt! Geld toevoegen
                            data["geld"] += taak['beloning']
                            db["users"][user] = data
                            sla_db_op(db)
                            st.success(f"Goed gedaan! +€{taak['beloning']}")
                            del st.session_state.actieve_taak
                            st.rerun()
                        else:
                            st.error("Niet goed, probeer het nog eens!")
                else:
                    st.warning("Voeg eerst woorden toe aan je woordenlijst!")
