import streamlit as st
import json
import os
import random

DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
st.set_page_config(page_title="Putsie Studios", layout="wide")

def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- LOGIN ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login")
    db = laad_db()
    u = st.text_input("Naam").lower().strip()
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Log in"):
        if u in db["users"] and db["users"][u].get("password") == p:
            st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
    st.stop()

db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 100, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}})

with st.sidebar:
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    if st.button("🏠 Home"): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden"): st.session_state.page = "Frans"
    if st.button("🏫 Klaslokaal"): st.session_state.page = "Klas"
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- PAGINA'S ---
page = st.session_state.get("page", "Home")

if page == "Frans":
    st.title("🎓 Frans & Werkwoorden")
    t1, t2 = st.tabs(["🎯 Quiz", "➕ Toevoegen"])
    with t1:
        cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
        if st.button("Nieuwe Vraag"):
            st.session_state.vraag = random.choice(list(data["woorden"][cat].keys()))
        if 'vraag' in st.session_state:
            ans = st.text_input(f"Vertaal: {st.session_state.vraag}")
            if st.button("Check"):
                if ans.lower() == data["woorden"][cat][st.session_state.vraag].lower():
                    data["geld"] += 10; db["users"][user] = data; sla_db_op(db); st.success("Correct!")
    with t2:
        f = st.text_input("Frans"); n = st.text_input("Nederlands")
        if st.button("Opslaan"):
            data["woorden"]["woorden"][f] = n; db["users"][user] = data; sla_db_op(db); st.rerun()

elif page == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    if user.lower() in LEERKRACHTEN:
        for code, info in db["klassen"].items():
            if info["docent"] == user:
                with st.expander(f"Klas: {info['naam']} (Code: {code})"):
                    q = st.text_input("Vraag:", key=f"q_{code}"); a = st.text_input("Antwoord:", key=f"a_{code}"); b = st.number_input("Bedrag:", value=20, key=f"b_{code}")
                    if st.button("Plaats", key=f"p_{code}"):
                        info["taken"].append({"vraag": q, "antwoord": a, "beloning": b}); sla_db_op(db); st.rerun()
    else:
        klas = db["klassen"].get(data.get("klas_id"), {})
        for i, taak in enumerate(klas.get("taken", [])):
            is_done = i in data.get("voltooide_taken", [])
            if st.button(f"Taak: {taak.get('vraag', '??')} (+€{taak.get('beloning', 0)})", disabled=is_done):
                st.session_state.active = {"idx": i, "data": taak}
        if 'active' in st.session_state:
            t = st.session_state.active
            ans = st.text_input(f"Vertaal: {t['data']['vraag']}")
            if st.button("Check"):
                if ans.lower().strip() == t['data']['antwoord'].lower().strip():
                    data["geld"] = data.get("geld", 0) + t['data']['beloning']
                    data.setdefault("voltooide_taken", []).append(t['idx'])
                    db["users"][user] = data; sla_db_op(db); del st.session_state.active; st.rerun()
else:
    st.title("🏠 Welkom bij Putsie Studios!")
