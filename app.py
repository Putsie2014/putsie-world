import streamlit as st
import json
import os
import random
import string
from datetime import datetime

# --- 1. CONFIGURATIE & ULTRA STYLING ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
st.set_page_config(page_title="Putsie Studios", page_icon="🌍", layout="wide")

def apply_custom_styles():
    st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: white; }
        [data-testid="stVerticalBlockBorderWrapper"] { 
            background: rgba(255, 255, 255, 0.05) !important; 
            backdrop-filter: blur(15px) !important; 
            border-radius: 20px !important; 
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 25px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
        }
        .stButton > button { 
            border-radius: 12px !important; 
            background: linear-gradient(45deg, #00dbde 0%, #fc00ff 100%) !important;
            color: white !important; font-weight: 800 !important;
            transition: 0.4s !important;
        }
        .stButton > button:hover { transform: scale(1.05) !important; box-shadow: 0 0 20px rgba(0, 219, 222, 0.6) !important; }
        .stChatMessage { background: rgba(255,255,255,0.05) !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 2. DATABASE FUNCTIES ---
def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            db.setdefault("klassen", {}); db.setdefault("users", {})
            return db
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- 3. LOGIN SYSTEEM ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title("🌌 Putsie Studios: Login")
    db = laad_db()
    t1, t2 = st.tabs(["🚀 Inloggen", "📝 Nieuw Account"])
    with t1:
        u = st.text_input("Gebruikersnaam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Start Adventure"):
            if u in db["users"] and db["users"][u].get("password") == p:
                st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
            else: st.error("Inloggegevens onjuist!")
    with t2:
        ru = st.text_input("Kies Naam", key="r_u").lower().strip()
        rp = st.text_input("Kies Wachtwoord", type="password", key="r_p")
        if st.button("Account Aanmaken"):
            if ru and rp and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}}
                sla_db_op(db); st.success("Account klaar! Log nu in."); st.balloons()
    st.stop()

db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 0})

with st.sidebar:
    st.title(f"👾 {user.capitalize()}")
    st.metric("SALDO", f"€{data.get('geld', 0)}")
    st.markdown("---")
    nav = st.radio("NAVIGATIE", ["🏠 Home", "📚 Frans Lab", "🏫 Het Klaslokaal", "🎮 Game Arcade"])
    if st.button("🚪 Log uit"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA LOGICA ---

if nav == "🏠 Home":
    st.title(f"Welkom in de Studio, {user.capitalize()}!")
    st.write("Gebruik het menu om te leren, te chatten of games te spelen.")
    st.markdown("---")
    st.subheader("🏆 Leaderboard (Top 5)")
    # Sorteer op geld
    sorted_users = sorted(db["users"].items(), key=lambda x: x[1].get("geld", 0), reverse=True)[:5]
    for i, (name, d) in enumerate(sorted_users):
        st.write(f"{i+1}. **{name.capitalize()}** - €{d.get('geld', 0)}")

elif nav == "📚 Frans Lab":
    st.title("🧪 Frans Lab")
    t1, t2 = st.tabs(["🎯 Quiz", "➕ Toevoegen"])
    with t1:
        cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
        w_dict = data.get("woorden", {}).get(cat, {})
        if st.button("Nieuwe Vraag"):
            if w_dict: st.session_state.quiz_q = random.choice(list(w_dict.keys()))
        if 'quiz_q' in st.session_state:
            st.subheader(f"Vertaal: {st.session_state.quiz_q}")
            ans = st.text_input("Antwoord:")
            if st.button("Check"):
                if ans.lower().strip() == w_dict[st.session_state.quiz_q].lower().strip():
                    data["geld"] += 15; db["users"][user] = data; sla_db_op(db); st.toast("Lekker! +€15"); del st.session_state.quiz_q; st.rerun()
    with t2:
        tw = st.radio("Type", ["woorden", "werkwoorden"])
        fw = st.text_input("Frans"); nw = st.text_input("Nederlands")
        if st.button("Sla op"):
            data.setdefault("woorden", {}).setdefault(tw, {})[fw] = nw
            db["users"][user] = data; sla_db_op(db); st.success("Opgeslagen!")

elif nav == "🏫 Het Klaslokaal":
    st.title("🏫 Putsie Klaslokaal")
    
    if user.lower() in LEERKRACHTEN:
        mijn_klas_code = next((c for c, i in db["klassen"].items() if i.get("docent") == user), None)
        if not mijn_klas_code:
            k_naam = st.text_input("Naam van je klas")
            if st.button("Bouw Klas ✨"):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                db["klassen"][code] = {"naam": k_naam, "docent": user, "taken": [], "comments": []}
                sla_db_op(db); st.rerun()
        else:
            klas_info = db["klassen"][mijn_klas_code]
            st.success(f"Beheer: **{klas_info.get('naam')}** | Code: `{mijn_klas_code}`")
            
            t_tk, t_st, t_set, t_ch = st.tabs(["📝 Taken", "👥 Leerlingen", "⚙️ Beheer", "💬 Chat"])
            
            with t_tk:
                q = st.text_input("Vraag"); a = st.text_input("Antwoord"); g = st.number_input("Beloning", 10, 500, 20)
                if st.button("Plaats Taak"):
                    klas_info.setdefault("taken", []).append({"vraag": q, "antwoord": a, "beloning": g})
                    sla_db_op(db); st.rerun()
                for i, t in enumerate(klas_info.get("taken", [])):
                    st.write(f"{i+1}. {t.get('vraag')} (€{t.get('beloning', 0)})")
            
            with t_st:
                leerlingen = [u_n for u_n, d_n in db["users"].items() if d_n.get("klas_id") == mijn_klas_code]
                for l in leerlingen:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"👤 {l.capitalize()}")
                    if c2.button("Verwijder", key=f"rem_{l}"):
                        db["users"][l]["klas_id"] = None; sla_db_op(db); st.rerun()
            
            with t_set:
                n_nm = st.text_input("Nieuwe klasnaam", value=klas_info.get('naam'))
                if st.button("Naam Bijwerken"):
                    db["klassen"][mijn_klas_code]["naam"] = n_nm; sla_db_op(db); st.rerun()
            
            with t_ch:
                comments = klas_info.get("comments", [])
                for c in comments:
                    with st.chat_message(c['user']):
                        st.write(f"**{c['user'].capitalize()}**: {c['text']} *({c.get('time', '')})*")
                msg = st.chat_input("Bericht voor de klas...", key="admin_chat")
                if msg:
                    t_str = datetime.now().strftime("%H:%M")
                    klas_info.setdefault("comments", []).append({"user": user, "text": msg, "time": t_str})
                    sla_db_op(db); st.rerun()

    else:
        if not data.get("klas_id"):
            c_in = st.text_input("Klascode:").upper()
            if st.button("Join"):
                if c_in in db["klassen"]:
                    data["klas_id"] = c_in; db["users"][user] = data; sla_db_op(db); st.rerun()
        else:
            klas_id = data["klas_id"]
            klas = db["klassen"].get(klas_id, {})
            st.header(f"Klas: {klas.get('naam')}")
            
            st.subheader("📋 Taken")
            for i, t in enumerate(klas.get("taken", [])):
                done = i in data.get("voltooide_taken", [])
                if not done:
                    if st.button(f"▶️ {t.get('vraag')} (€{t.get('beloning')})", key=f"s_t_{i}"):
                        st.session_state.active_t = {"idx": i, "data": t}
            
            if 'active_t' in st.session_state:
                at = st.session_state.active_t
                ans = st.text_input(f"Vertaal {at['data'].get('vraag')}:")
                if st.button("Check Taak"):
                    if ans.lower().strip() == at['data'].get('antwoord', '').lower().strip():
                        data["geld"] += at['data'].get('beloning', 0); data.setdefault("voltooide_taken", []).append(at['idx'])
                        db["users"][user] = data; sla_db_op(db); del st.session_state.active_t; st.balloons(); st.rerun()

            st.markdown("---")
            st.subheader("💬 Klas Chat")
            for c in klas.get("comments", [])[-10:]:
                with st.chat_message(c['user']):
                    st.write(f"**{c['user'].capitalize()}**: {c['text']} *({c.get('time', '')})*")
            n_m = st.chat_input("Zeg iets...", key="stud_chat")
            if n_m:
                t_str = datetime.now().strftime("%H:%M")
                db["klassen"][klas_id].setdefault("comments", []).append({"user": user, "text": n_m, "time": t_str})
                sla_db_op(db); st.rerun()

elif nav == "🎮 Game Arcade":
    st.title("👾 Putsie Arcade")
    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.subheader("Alien Shooter 🛸")
            if st.button("FIRE! 💥"):
                if random.random() > 0.5:
                    data["geld"] += 2; db["users"][user] = data; sla_db_op(db); st.toast("RAAK!")
                else: st.toast("MIS!")
    with col2:
        with st.container():
            st.subheader("Neon Bouncer 🏀")
            st.markdown('<div style="height:40px; width:40px; background:linear-gradient(to bottom, #00dbde, #fc00ff); border-radius:50%; animation: bounce 0.5s infinite alternate; box-shadow: 0 0 15px #00dbde;"></div><style>@keyframes bounce { from {margin-top:0px;} to {margin-top:40px;} }</style>', unsafe_allow_html=True)
            if st.button("Collect Energy"):
                data["geld"] += 1; db["users"][user] = data; sla_db_op(db); st.toast("Power up!")
