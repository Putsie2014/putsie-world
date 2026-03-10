import streamlit as st
import json
import os
import random
import string

# --- 1. CONFIGURATIE & HIGH-END STYLING ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
st.set_page_config(page_title="Putsie Studios", page_icon="🎮", layout="wide")

st.markdown("""
<style>
    /* High-end Dark Theme Gradient */
    .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: white; }
    
    /* Glassmorphism containers */
    [data-testid="stVerticalBlockBorderWrapper"] { 
        background: rgba(255,255,255,0.07) !important; 
        backdrop-filter: blur(15px) !important; 
        border-radius: 25px !important; 
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 25px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
    }

    /* Knoppen met animatie */
    .stButton > button { 
        border-radius: 15px !important; 
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        transition: 0.3s !important;
    }
    .stButton > button:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(37, 117, 252, 0.4); }
    
    /* Input velden styling */
    input { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE FUNCTIES ---
def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            if "klassen" not in db: db["klassen"] = {}
            if "users" not in db: db["users"] = {}
            return db
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- 3. LOGIN & REGISTRATIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios")
    db = laad_db()
    t1, t2 = st.tabs(["🔐 Inloggen", "📝 Account maken"])
    with t1:
        u = st.text_input("Naam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Start Adventure", type="primary"):
            if u in db["users"] and db["users"][u].get("password") == p:
                st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
            else: st.error("Inloggegevens kloppen niet!")
    with t2:
        ru = st.text_input("Kies een Naam", key="r_u").lower().strip()
        rp = st.text_input("Kies een Wachtwoord", type="password", key="r_p")
        if st.button("Create Account"):
            if ru and rp and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}}
                sla_db_op(db); st.success("Account klaar! Log nu in."); st.balloons()
    st.stop()

# --- 4. DATA SETUP ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 0, "woorden": {"woorden": {}, "werkwoorden": {}}})

with st.sidebar:
    st.title(f"🚀 {user.capitalize()}")
    st.metric("💰 Jouw Saldo", f"€{data.get('geld', 0)}")
    st.markdown("---")
    choice = st.radio("Menu", ["🏠 Dashboard", "📚 Woorden & Quiz", "🏫 Mijn Klas", "👾 Arcade"])
    if st.button("🚪 Uitloggen"): st.session_state.clear(); st.rerun()

# --- 5. PAGINA'S ---

# --- DASHBOARD ---
if choice == "🏠 Dashboard":
    st.title(f"Welkom terug, {user.capitalize()}!")
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.subheader("📊 Je Voortgang")
            st.write(f"Vermogen: **€{data.get('geld', 0)}**")
            w_count = len(data.get('woorden', {}).get('woorden', {})) + len(data.get('woorden', {}).get('werkwoorden', {}))
            st.write(f"Woorden geleerd: **{w_count}**")
    with col2:
        with st.container():
            st.subheader("📣 Nieuws")
            st.write("Versie 3.0 is live! Nu met betere graphics en games.")

# --- WOORDEN & QUIZ ---
elif choice == "📚 Woorden & Quiz":
    st.title("🎓 Frans Master")
    t1, t2, t3 = st.tabs(["🎯 Oefen Quiz", "➕ Woord Toevoegen", "📑 Mijn Woorden"])
    
    with t1:
        cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
        woorden_dict = data.get("woorden", {}).get(cat, {})
        if st.button("Nieuwe Vraag 🎲"):
            if woorden_dict: st.session_state.q = random.choice(list(woorden_dict.keys()))
            else: st.warning("Voeg eerst woorden toe!")
        if 'q' in st.session_state:
            st.subheader(f"Vertaal: **{st.session_state.q}**")
            ans = st.text_input("Antwoord:")
            if st.button("Check"):
                if ans.lower().strip() == woorden_dict[st.session_state.q].lower().strip():
                    data["geld"] += 10; db["users"][user] = data; sla_db_op(db); st.balloons(); del st.session_state.q; st.rerun()
                else: st.error("Foutje! Probeer het nog eens.")
    with t2:
        c = st.radio("Type", ["woorden", "werkwoorden"], horizontal=True)
        f = st.text_input("Frans"); n = st.text_input("Nederlands")
        if st.button("Opslaan 💾"):
            if f and n:
                if "woorden" not in data: data["woorden"] = {"woorden": {}, "werkwoorden": {}}
                data["woorden"][c][f] = n; db["users"][user] = data; sla_db_op(db); st.success("Opgeslagen!")
    with t3:
        st.subheader("Jouw Woordenlijst")
        st.json(data.get("woorden", {}))

# --- KLAS ---
elif choice == "🏫 Mijn Klas":
    st.title("🏫 Klaslokaal")
    if user.lower() in LEERKRACHTEN:
        mijn_klas = next((c for c, i in db["klassen"].items() if i.get("docent") == user), None)
        if not mijn_klas:
            naam = st.text_input("Naam nieuwe klas:")
            if st.button("Klas Aanmaken"):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                db["klassen"][code] = {"naam": naam, "docent": user, "taken": []}; sla_db_op(db); st.rerun()
        else:
            info = db["klassen"][mijn_klas]
            st.success(f"Klas: {info.get('naam')} | Code: **{mijn_klas}**")
            col1, col2 = st.columns(2)
            with col1:
                with st.container():
                    st.markdown("### ➕ Nieuwe Taak")
                    t_q = st.text_input("Vraag"); t_a = st.text_input("Antwoord"); t_b = st.number_input("Geld", value=20)
                    if st.button("Taak Plaatsen"):
                        info.setdefault("taken", []).append({"vraag": t_q, "antwoord": t_a, "beloning": t_b})
                        sla_db_op(db); st.rerun()
            with col2:
                st.markdown("### 📋 Actieve Taken")
                for t in info.get("taken", []):
                    # HIER IS DE FIX: .get() voorkomt de KeyError
                    v_tekst = t.get('vraag', 'Oude taak')
                    b_tekst = t.get('beloning', 0)
                    st.write(f"📝 {v_tekst} (Bonus: €{b_tekst})")
    else:
        if not data.get("klas_id"):
            code = st.text_input("Voer klascode in:").upper()
            if st.button("Deelnemen"):
                if code in db["klassen"]:
                    data["klas_id"] = code; db["users"][user] = data; sla_db_op(db); st.balloons(); st.rerun()
                else: st.error("Code niet gevonden.")
        else:
            klas = db["klassen"].get(data["klas_id"], {})
            st.subheader(f"Klas: {klas.get('naam', 'Onbekend')}")
            for i, taak in enumerate(klas.get("taken", [])):
                done = i in data.get("voltooide_taken", [])
                v = taak.get("vraag", "Vraag mist")
                b = taak.get("beloning", 0)
                if st.button(f"{'✅' if done else '▶️'} {v} (€{b})", disabled=done, key=f"t_{i}"):
                    st.session_state.active_t = {"idx": i, "data": taak}
            if 'active_t' in st.session_state:
                at = st.session_state.active_t
                ans = st.text_input(f"Beantwoord: {at['data'].get('vraag')}")
                if st.button("Inleveren"):
                    if ans.lower().strip() == at['data'].get('antwoord', '').lower().strip():
                        data["geld"] += at['data'].get('beloning', 0); data.setdefault("voltooide_taken", []).append(at['idx'])
                        db["users"][user] = data; sla_db_op(db); del st.session_state.active_t; st.balloons(); st.rerun()
                    else: st.error("Helaas, niet juist!")

# --- ARCADE ---
elif choice == "👾 Arcade":
    st.title("👾 Putsie Arcade")
    c1, c2 = st.columns(2)
    with c1:
        with st.container():
            st.subheader("Alien Shooter 🛸")
            if st.button("FIRE! 🔫"):
                if random.random() > 0.5:
                    data["geld"] += 2; db["users"][user] = data; sla_db_op(db); st.toast("RAAK! +€2", icon="👾")
                else: st.toast("MIS!", icon="💨")
    with c2:
        with st.container():
            st.subheader("Bounce Game 🏀")
            st.markdown('<div style="height:40px; width:40px; background:linear-gradient(to bottom, #ff9900, #ff6600); border-radius:50%; animation: bounce 0.6s infinite alternate; box-shadow: 0 10px 20px rgba(0,0,0,0.5);"></div><style>@keyframes bounce { from {margin-top:0px;} to {margin-top:50px;} }</style>', unsafe_allow_html=True)
            if st.button("Collect Energy"):
                data["geld"] += 1; db["users"][user] = data; sla_db_op(db); st.toast("Gevangen! +€1")
