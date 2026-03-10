import streamlit as st
import json
import os
import random
import string

# --- 1. CONFIGURATIE & STYLING ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
st.set_page_config(page_title="Putsie Studios", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1e1e2f 0%, #4e085e 100%); color: white; }
    [data-testid="stVerticalBlockBorderWrapper"] { 
        background: rgba(255,255,255,0.05); backdrop-filter: blur(15px); 
        border-radius: 20px; border: 1px solid rgba(255,255,255,0.15);
        padding: 20px; transition: 0.3s;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
    .stButton > button { border-radius: 20px !important; font-weight: bold !important; transition: 0.2s !important; }
    .stButton > button:hover { transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE HELPERS ---
def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            if "klassen" not in db: db["klassen"] = {}
            return db
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- 3. LOGIN & REGISTRATIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login")
    db = laad_db()
    t1, t2 = st.tabs(["🔐 Inloggen", "📝 Account maken"])
    with t1:
        u = st.text_input("Gebruikersnaam", key="login_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="login_p")
        if st.button("Start Sessie", type="primary"):
            if u in db["users"] and db["users"][u].get("password") == p:
                st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
            else: st.error("Inloggegevens kloppen niet!")
    with t2:
        ru = st.text_input("Nieuwe Naam", key="reg_u").lower().strip()
        rp = st.text_input("Wachtwoord", type="password", key="reg_p")
        if st.button("Account Aanmaken"):
            if ru and rp and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}}
                sla_db_op(db); st.success("Gelukt! Log nu in."); st.balloons()
    st.stop()

# --- 4. DATA LADEN & SIDEBAR ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 100, "woorden": {"woorden": {}, "werkwoorden": {}}})

with st.sidebar:
    st.header(f"👋 {user.capitalize()}")
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    st.markdown("---")
    choice = st.radio("Ga naar:", ["🏠 Dashboard", "📚 Woorden & Quiz", "🏫 Mijn Klas", "👾 Arcade (Games)"])
    if st.button("🚪 Uitloggen"): st.session_state.clear(); st.rerun()

# --- 5. PAGINA LOGICA ---

if choice == "🏠 Dashboard":
    st.title(f"Welkom bij Putsie Studios, {user.capitalize()}!")
    st.write("Gebruik het menu links om te leren, te oefenen of games te spelen.")
    with st.container(border=True):
        st.markdown(f"### 📊 Jouw Statistieken")
        st.write(f"💰 Vermogen: **€{data.get('geld', 0)}**")
        st.write(f"📖 Woorden in lijst: **{len(data['woorden']['woorden']) + len(data['woorden']['werkwoorden'])}**")

elif choice == "📚 Woorden & Quiz":
    st.title("🎓 Frans & Woorden")
    tab_quiz, tab_add, tab_view = st.tabs(["🎯 Quiz", "➕ Toevoegen", "📑 Lijst Bekijken"])
    
    with tab_quiz:
        cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
        if st.button("Nieuwe Vraag 🎲"):
            if data["woorden"][cat]:
                st.session_state.q = random.choice(list(data["woorden"][cat].keys()))
            else: st.warning("Voeg eerst woorden toe!")
        if 'q' in st.session_state:
            st.subheader(f"Vertaal: {st.session_state.q}")
            ans = st.text_input("Jouw antwoord:")
            if st.button("Check ✔️"):
                if ans.lower().strip() == data["woorden"][cat][st.session_state.q].lower().strip():
                    data["geld"] += 10; db["users"][user] = data; sla_db_op(db); st.toast("Goed! +€10"); del st.session_state.q; st.rerun()
                else: st.error("Fout, probeer het nog eens!")

    with tab_add:
        c = st.radio("Soort", ["woorden", "werkwoorden"], horizontal=True)
        f = st.text_input("Frans")
        n = st.text_input("Nederlands")
        if st.button("Opslaan 💾"):
            data["woorden"][c][f] = n; db["users"][user] = data; sla_db_op(db); st.success("Toegevoegd!")

    with tab_view:
        st.subheader("Jouw Woordenlijst")
        st.json(data["woorden"])

elif choice == "🏫 Mijn Klas":
    st.title("🏫 Putsie Klaslokaal")
    if user.lower() in LEERKRACHTEN:
        mijn_klas = next((c for c, i in db["klassen"].items() if i.get("docent") == user), None)
        if not mijn_klas:
            naam = st.text_input("Naam van je nieuwe klas:")
            if st.button("Klas Aanmaken ✨"):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                db["klassen"][code] = {"naam": naam, "docent": user, "taken": []}; sla_db_op(db); st.rerun()
        else:
            info = db["klassen"][mijn_klas]
            st.success(f"Klas: {info['naam']} | Code: **{mijn_klas}**")
            with st.container(border=True):
                st.markdown("### ➕ Taak Toevoegen")
                t_q = st.text_input("Vraag"); t_a = st.text_input("Antwoord"); t_b = st.number_input("Geld", value=20)
                if st.button("Plaatsen"):
                    info["taken"].append({"vraag": t_q, "antwoord": t_a, "beloning": t_b}); sla_db_op(db); st.rerun()
            st.markdown("### Actieve Taken")
            for t in info["taken"]: st.write(f"📝 {t['vraag']} (Bonus: €{t['beloning']})")
    else:
        if not data.get("klas_id"):
            code = st.text_input("Klascode:").upper()
            if st.button("Deelnemen"):
                if code in db["klassen"]:
                    data["klas_id"] = code; db["users"][user] = data; sla_db_op(db); st.balloons(); st.rerun()
        else:
            klas = db["klassen"].get(data["klas_id"], {})
            st.subheader(f"Klas: {klas.get('naam')}")
            for i, taak in enumerate(klas.get("taken", [])):
                done = i in data.get("voltooide_taken", [])
                if st.button(f"{'✅' if done else '▶️'} {taak.get('vraag')} (+€{taak.get('beloning')})", disabled=done, key=f"tk_{i}"):
                    st.session_state.active_tk = {"idx": i, "data": taak}
            if 'active_tk' in st.session_state:
                tk = st.session_state.active_tk
                ans = st.text_input(f"Antwoord op: {tk['data']['vraag']}")
                if st.button("Indienen"):
                    if ans.lower().strip() == tk['data']['antwoord'].lower().strip():
                        data["geld"] += tk['data']['beloning']; data.setdefault("voltooide_taken", []).append(tk['idx'])
                        db["users"][user] = data; sla_db_op(db); del st.session_state.active_tk; st.balloons(); st.rerun()

elif choice == "👾 Arcade (Games)":
    st.title("👾 Putsie Arcade")
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        with st.container(border=True):
            st.subheader("Alien Shooter 🛸")
            if st.button("Schiet!"):
                if random.random() > 0.4:
                    data["geld"] += 2; db["users"][user] = data; sla_db_op(db); st.success("RAAK! +€2")
                else: st.error("MIS!")
    with g_col2:
        with st.container(border=True):
            st.subheader("Bounce Ball 🏀")
            st.markdown('<div style="height:50px; width:50px; background:orange; border-radius:50%; animation: bounce 0.5s infinite alternate;"></div><style>@keyframes bounce { from {margin-top:0px;} to {margin-top:40px;} }</style>', unsafe_allow_html=True)
            if st.button("Vang de bal"):
                data["geld"] += 1; db["users"][user] = data; sla_db_op(db); st.toast("Gevangen!")
else:
    with st.container(border=True):
        st.title("🏠 Welkom bij Putsie Studios!")
        st.write("Gebruik het menu aan de zijkant om te navigeren. Veel succes en plezier met leren! 🚀")
