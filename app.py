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
    if not os.path.exists(DB_FILE): init_db()
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            if "klassen" not in db: db["klassen"] = {}
            return db
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- 2. LOGIN ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login")
    db = laad_db()
    u = st.text_input("Naam").lower().strip()
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Log in"):
        if u in db["users"] and db["users"][u]["password"] == p:
            st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
        else: st.error("Fout!")
    st.stop()

# --- 3. DATA & ZIJKANT ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}, "klas_id": None})

with st.sidebar:
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    if st.button("🏠 Home"): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden"): st.session_state.page = "Frans"
    if st.button("🏫 Klaslokaal"): st.session_state.page = "Klas"
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA'S ---
page = st.session_state.get("page", "Home")

if page == "Frans":
    st.title("🎓 Frans & Werkwoorden")
    t1, t2 = st.tabs(["🎯 Quiz", "➕ Toevoegen"])
    with t1:
        cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
        if st.button("Nieuwe Vraag"):
            st.session_state.vraag = random.choice(list(data["woorden"][cat].keys()))
            st.rerun()
        if 'vraag' in st.session_state:
            v = st.session_state.vraag
            st.write(f"Vertaal: **{v}**")
            ans = st.text_input("Antwoord:")
            if st.button("Check"):
                data["geld"] += 10; db["users"][user] = data; sla_db_op(db); st.success("Correct! +€10")
    with t2:
        f = st.text_input("Frans"); n = st.text_input("Nederlands")
        if st.button("Opslaan"):
            data["woorden"]["woorden"][f] = n; db["users"][user] = data; sla_db_op(db); st.rerun()

elif page == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    if user.lower() in LEERKRACHTEN:
        naam = st.text_input("Naam nieuwe klas:"); 
        if st.button("Genereer Klas"):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            db["klassen"][code] = {"naam": naam, "docent": user, "taken": []}; sla_db_op(db); st.rerun()
        for code, info in db["klassen"].items():
            if info["docent"] == user:
                with st.expander(f"Klas: {info['naam']} (Code: {code})"):
                    t = st.text_input("Taak:", key=f"t_{code}")
                    b = st.number_input("Bedrag:", value=20, key=f"b_{code}")
                    if st.button("Plaats", key=f"p_{code}"):
                        info["taken"].append({"taak": t, "beloning": b}); sla_db_op(db); st.rerun()
    else:
        if not data.get("klas_id"):
            c = st.text_input("Vul klascode in:").upper()
            if st.button("Deelnemen"):
                data["klas_id"] = c; db["users"][user] = data; sla_db_op(db); st.rerun()
        else:
            klas = db["klassen"].get(data["klas_id"], {})
            for i, taak in enumerate(klas.get("taken", [])):
                st.write(f"✅ {taak['taak']} (Beloning: €{taak['beloning']})")
                if st.button(f"Voltooid {i}"):
                    data["geld"] += taak['beloning']; db["users"][user] = data; sla_db_op(db); st.rerun()

else:
    st.title("🏠 Welkom bij Putsie Studios!")
