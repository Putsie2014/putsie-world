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
                db["users"][ru] = {"password": rp, "geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}, "klas_id": None, "voltooide_taken": []}
                sla_db_op(db); st.success("Account gemaakt!"); st.rerun()
    st.stop()

# --- 3. DATA & ZIJKANT ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}, "klas_id": None, "voltooide_taken": []})

with st.sidebar:
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    if st.button("🏠 Home"): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden"): st.session_state.page = "Frans"
    if st.button("🏫 Klaslokaal"): st.session_state.page = "Klas"
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA LOGICA ---
page = st.session_state.get("page", "Home")

if page == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    if user.lower() in LEERKRACHTEN:
        naam = st.text_input("Naam nieuwe klas:")
        if st.button("Genereer Klas"):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            db["klassen"][code] = {"naam": naam, "docent": user, "taken": []}; sla_db_op(db); st.rerun()
        for code, info in db["klassen"].items():
            if info["docent"] == user:
                with st.expander(f"Klas: {info['naam']} (Code: {code})"):
                    t_vraag = st.text_input("Vraag:", key=f"q_{code}")
                    t_ant = st.text_input("Antwoord:", key=f"a_{code}")
                    b = st.number_input("Bedrag:", value=20, key=f"b_{code}")
                    if st.button("Plaats", key=f"p_{code}"):
                        info["taken"].append({"vraag": t_vraag, "antwoord": t_ant, "beloning": b}); sla_db_op(db); st.rerun()
    else:
        if not data.get("klas_id"):
            c = st.text_input("Vul klascode in:").upper()
            if st.button("Deelnemen"):
                if c in db["klassen"]:
                    data["klas_id"] = c; db["users"][user] = data; sla_db_op(db); st.rerun()
        else:
            if "voltooide_taken" not in data: data["voltooide_taken"] = []
            klas = db["klassen"].get(data["klas_id"], {})
            st.subheader(f"Klas: {klas.get('naam')}")
            for i, taak in enumerate(klas.get("taken", [])):
                is_gedaan = i in data["voltooide_taken"]
                if st.button(f"{'✅' if is_gedaan else 'Start'} {taak['vraag']} (+€{taak['beloning']})", key=f"btn_{i}", disabled=is_gedaan):
                    st.session_state.actieve_taak = {"idx": i, "data": taak}
            if 'actieve_taak' in st.session_state:
                t = st.session_state.actieve_taak
                ant = st.text_input(f"Vertaal: {t['data']['vraag']}")
                if st.button("Check"):
                    if ant.lower().strip() == t['data']['antwoord'].lower().strip():
                        data["geld"] += t['data']['beloning']; data["voltooide_taken"].append(t['idx']); db["users"][user] = data; sla_db_op(db); del st.session_state.actieve_taak; st.rerun()
                    else: st.error("Niet goed!")
elif page == "Frans":
    st.title("🎓 Frans & Werkwoorden")
    st.write("Frans sectie actief")
else:
    st.title("🏠 Welkom bij Putsie Studios!")
                        del st.session_state.actieve_taak
                        st.rerun()
                    else:
                        st.error("Niet goed, probeer het nog eens!")
