import streamlit as st
import json
import os
import random
import string

# --- CONFIGURATIE ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]

# --- DATABASE FUNCTIES (Deze repareren de database automatisch) ---
def laad_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            if "users" not in db: db["users"] = {}
            if "klassen" not in db: db["klassen"] = {}
            return db
    except:
        return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

# --- APP START ---
st.set_page_config(page_title="Putsie Studios", layout="wide")

if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"

# Hier zou je login-logica moeten staan...
# Als je hier hulp bij nodig hebt, plak ik die er weer bij.

# --- ZIJKANT ---
with st.sidebar:
    if st.button("🏫 Klaslokaal"): st.session_state.page = "Klas"

# --- PAGINA LOGICA ---
if st.session_state.page == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    db = laad_db()
    user = st.session_state.get("username", "gast")
    
    # LEERKRACHT LOGICA
    if user.lower() in LEERKRACHTEN:
        st.subheader("Beheer")
        naam = st.text_input("Naam klas:")
        if st.button("Maak klas"):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            db["klassen"][code] = {"naam": naam, "docent": user, "leerlingen": [], "taken": []}
            sla_db_op(db); st.rerun()
            
    # LEERLING LOGICA
    else:
        st.write("Klaslokaal voor leerlingen...")
