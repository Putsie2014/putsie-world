import streamlit as st
import json
import os
import random
import string

# --- 1. CONFIGURATIE (Alles bovenaan) ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": {}, "klassen": {}}, f)

def laad_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# App Initialisatie
st.set_page_config(page_title="Putsie Studios", layout="wide")
init_db()

if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"

# --- 2. LOGIN (Zoals je gewend bent) ---
if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login")
    # (Je login logica hier)
    # ...
    st.stop()

# --- 3. DATA & ZIJKANT ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 0, "woorden": {"werkwoorden": {}, "woorden": {}}, "klas_id": None})

with st.sidebar:
    st.title(f"👤 {user.capitalize()}")
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    st.write("---")
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden", use_container_width=True): st.session_state.page = "Frans"
    if st.button("🏫 Klaslokaal", use_container_width=True): st.session_state.page = "Klas"
    # ... rest van de knoppen ...
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA LOGICA ---
if st.session_state.page == "Frans":
    st.title("🎓 Putsie Education: Frans")
    # ... (jouw Franse quiz code) ...

elif st.session_state.page == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    db = laad_db()
    
    # LEERKRACHT (Elliot / Annelies)
    if user.lower() in LEERKRACHTEN:
        st.subheader("Beheer je klassen")
        naam = st.text_input("Naam voor de nieuwe klas:")
        if st.button("Genereer Klas"):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            db["klassen"][code] = {"naam": naam, "docent": user, "leerlingen": [], "taken": []}
            sla_db_op(db); st.success(f"Klas aangemaakt! Code: **{code}**"); st.rerun()
        
        st.write("---")
        for code, info in db["klassen"].items():
            if info["docent"] == user:
                with st.expander(f"Klas: {info['naam']} (Code: {code})"):
                    taak = st.text_input(f"Taak voor {info['naam']}:", key=f"t_{code}")
                    if st.button("Plaats Taak", key=f"btn_{code}"):
                        info["taken"].append({"taak": taak, "beloning": 20})
                        sla_db_op(db); st.rerun()
    
    # LEERLING
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
            st.subheader("Taken van je leraar")
            for i, taak in enumerate(klas.get("taken", [])):
                st.write(f"- {taak['taak']} (Beloning: €{taak['beloning']})")
                if st.button(f"Taak Voltooid! {i}"):
                    data["geld"] += taak["beloning"]
                    db["users"][user] = data
                    sla_db_op(db); st.rerun()

else:
    st.title("🏠 Welkom bij Putsie Studios!")
            col1, col2 = st.columns(2)
            with col1: st.json(gebruiker_data["woorden"]["woorden"])
            with col2: st.json(gebruiker_data["woorden"]["werkwoorden"])
