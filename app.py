import streamlit as st
import json
import os
import random
import string

# --- CONFIGURATIE ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
st.set_page_config(page_title="Putsie Studios", layout="wide")

def laad_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

# --- LOGIN ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios")
    db = laad_db()
    u = st.text_input("Naam").lower().strip()
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Log in"):
        if u in db["users"] and db["users"][u].get("password") == p:
            st.session_state.ingelogd = True
            st.session_state.username = u
            st.rerun()
    st.stop()

# --- APP ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 100, "klas_id": None, "voltooide_taken": []})

with st.sidebar:
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    if st.button("🏫 Klaslokaal"): st.session_state.page = "Klas"
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- KLAS LOGICA ---
if st.session_state.get("page") == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    
    if user.lower() in LEERKRACHTEN:
        naam = st.text_input("Naam nieuwe klas:")
        if st.button("Genereer Klas"):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            db["klassen"][code] = {"naam": naam, "docent": user, "taken": []}
            sla_db_op(db); st.rerun()
        for code, info in db["klassen"].items():
            if info["docent"] == user:
                with st.expander(f"Klas: {info['naam']} (Code: {code})"):
                    q = st.text_input("Vraag:", key=f"q_{code}")
                    a = st.text_input("Antwoord:", key=f"a_{code}")
                    b = st.number_input("Bedrag:", value=20, key=f"b_{code}")
                    if st.button("Plaats Taak", key=f"p_{code}"):
                        info["taken"].append({"vraag": q, "antwoord": a, "beloning": b})
                        sla_db_op(db); st.rerun()
    else:
        if not data.get("klas_id"):
            c = st.text_input("Vul klascode in:").upper()
            if st.button("Deelnemen"):
                if c in db["klassen"]:
                    data["klas_id"] = c
                    db["users"][user] = data
                    sla_db_op(db); st.rerun()
        else:
            if "voltooide_taken" not in data: data["voltooide_taken"] = []
            klas = db["klassen"].get(data["klas_id"], {})
            st.subheader(f"Klas: {klas.get('naam')}")
            
            for i, taak in enumerate(klas.get("taken", [])):
                is_done = i in data["voltooide_taken"]
                if st.button(f"Taak: {taak['vraag']} ({'✅' if is_done else '€'+str(taak['beloning'])})", disabled=is_done):
                    st.session_state.active = {"idx": i, "data": taak}
            
            if 'active' in st.session_state:
                t = st.session_state.active
                ans = st.text_input(f"Vertaal: {t['data']['vraag']}")
                if st.button("Check"):
                    if ans.lower().strip() == t['data']['antwoord'].lower().strip():
                        data["geld"] += t['data']['beloning']
                        data["voltooide_taken"].append(t['idx'])
                        db["users"][user] = data
                        sla_db_op(db)
                        del st.session_state.active
                        st.rerun()
                    else:
                        st.error("Fout!")
