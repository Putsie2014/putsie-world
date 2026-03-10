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
    # Zorg dat de database altijd de juiste structuur heeft
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": {}, "klassen": {}}, f)
    else:
        # Check op ontbrekende sleutels in bestaande database
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
        if "klassen" not in db:
            db["klassen"] = {}
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4)

def laad_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}, "klassen": {}}

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
                db["users"][ru] = {"password": rp, "geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}, "klas_id": None}
                sla_db_op(db)
                st.success("Account aangemaakt!")
    st.stop()

# --- 3. SIDEBAR & DATA ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}, "klas_id": None})

with st.sidebar:
    st.title(f"👤 {user.capitalize()}")
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    st.write("---")
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden", use_container_width=True): st.session_state.page = "Frans"
    if st.button("🏫 Klaslokaal", use_container_width=True): st.session_state.page = "Klas"
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA'S ---
if st.session_state.page == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    
    # LEERKRACHT PANEEL
    if user.lower() in LEERKRACHTEN:
        st.subheader("Leerkracht: Beheer je klassen")
        naam = st.text_input("Naam nieuwe klas:")
        if st.button("Genereer Klas"):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            db["klassen"][code] = {"naam": naam, "docent": user, "leerlingen": [], "taken": []}
            sla_db_op(db); st.success(f"Klas aangemaakt! Code: **{code}**"); st.rerun()
        
        st.write("---")
        for code, info in db["klassen"].items():
            if info["docent"] == user:
                with st.expander(f"Klas: {info['naam']} (Code: {code})"):
                    st.write(f"Leerlingen: {', '.join(info['leerlingen'])}")
                    nieuwe_taak = st.text_input(f"Nieuwe taak voor {info['naam']}:", key=f"t_{code}")
                    beloning = st.number_input("Bedrag:", value=20, key=f"b_{code}")
                    if st.button("Plaats Taak", key=f"btn_{code}"):
                        info["taken"].append({"taak": nieuwe_taak, "beloning": beloning})
                        sla_db_op(db); st.rerun()
    
    # LEERLING PANEEL
    else:
        if not data.get("klas_id"):
            st.warning("Je zit nog niet in een klaslokaal.")
            code_input = st.text_input("Vul hier je klascode in:").upper()
            if st.button("Deelnemen"):
                if code_input in db["klassen"]:
                    db["klassen"][code_input]["leerlingen"].append(user)
                    data["klas_id"] = code_input
                    db["users"][user] = data
                    sla_db_op(db); st.rerun()
                else: st.error("Code niet gevonden!")
        else:
            klas = db["klassen"].get(data["klas_id"], {})
            st.success(f"Je zit in klas: {klas.get('naam', 'Onbekend')}")
            st.subheader("Jouw Taken")
            for i, taak in enumerate(klas.get("taken", [])):
                st.write(f"✅ **{taak['taak']}** - Beloning: €{taak['beloning']}")
                if st.button(f"Taak Voltooid! {i}"):
                    data["geld"] += taak['beloning']
                    db["users"][user] = data
                    sla_db_op(db); st.rerun()

elif st.session_state.page == "Frans":
    st.title("🎓 Frans & Werkwoorden")
    # (Je quiz code kan hier blijven staan)
else:
    st.title("🏠 Welkom bij Putsie Studios!")
elif st.session_state.page == "Home":
    st.title("🏠 Welkom bij Putsie Studios!")
else:
    st.title(f"Pagina: {st.session_state.page}")
