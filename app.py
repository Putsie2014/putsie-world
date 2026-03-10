import streamlit as st
import json
import os
import random
import string
from datetime import datetime

# --- 1. CONFIGURATIE & ULTRA STYLING ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
SUPER_ADMIN = "elliot"  # Elliot heeft alle macht
st.set_page_config(page_title="Putsie Studios 7.0", page_icon="👑", layout="wide")

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
        .stChatMessage { background: rgba(255,255,255,0.05) !important; border-radius: 15px !important; }
        .vip-badge { color: #ffcc00; font-weight: bold; text-shadow: 0 0 10px rgba(255,204,0,0.5); }
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
    
    # Zorg dat Elliot account altijd bestaat
    if "elliot" not in db["users"]:
        db["users"]["elliot"] = {"password": "admin", "geld": 9999, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}}
        sla_db_op(db)

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

# Functie voor VIP namen in chat
def get_display_name(name):
    if name == SUPER_ADMIN:
        return f"{name.capitalize()} (VIP👑)"
    return name.capitalize()

with st.sidebar:
    st.title(f"👾 {get_display_name(user)}")
    st.metric("SALDO", f"€{data.get('geld', 0)}")
    st.markdown("---")
    menu_options = ["🏠 Home", "📚 Frans Lab", "🏫 Het Klaslokaal", "🎮 Game Arcade"]
    if user == SUPER_ADMIN:
        menu_options.append("🔐 SUPER ADMIN")
    
    nav = st.radio("NAVIGATIE", menu_options)
    if st.button("🚪 Log uit"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA LOGICA ---

if nav == "🏠 Home":
    st.title(f"Welkom in de Studio, {get_display_name(user)}!")
    st.subheader("🏆 Leaderboard")
    sorted_users = sorted(db["users"].items(), key=lambda x: x[1].get("geld", 0), reverse=True)[:5]
    for i, (name, d) in enumerate(sorted_users):
        st.write(f"{i+1}. **{get_display_name(name)}** - €{d.get('geld', 0)}")

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
            t1, t2, t3, t4 = st.tabs(["📝 Taken", "👥 Leerlingen", "⚙️ Beheer", "💬 Chat"])
            with t4:
                for c in klas_info.get("comments", []):
                    with st.chat_message(c['user']):
                        st.write(f"**{get_display_name(c['user'])}**: {c['text']}")
                msg = st.chat_input("Bericht...")
                if msg:
                    klas_info.setdefault("comments", []).append({"user": user, "text": msg, "time": datetime.now().strftime("%H:%M")})
                    sla_db_op(db); st.rerun()
    else:
        # Leerling flow (versimpeld voor ruimte)
        if data.get("klas_id"):
            klas = db["klassen"].get(data["klas_id"], {})
            st.subheader(f"💬 Chat van {klas.get('naam')}")
            for c in klas.get("comments", [])[-10:]:
                with st.chat_message(c['user']):
                    st.write(f"**{get_display_name(c['user'])}**: {c['text']}")
            n_m = st.chat_input("Zeg iets...")
            if n_m:
                db["klassen"][data["klas_id"]].setdefault("comments", []).append({"user": user, "text": n_m, "time": datetime.now().strftime("%H:%M")})
                sla_db_op(db); st.rerun()

elif nav == "🔐 SUPER ADMIN":
    if user == SUPER_ADMIN:
        st.title("🔐 Elliot's Super Control Panel")
        st.warning("Wees voorzichtig, Elliot. Hier heb je de macht over alle data.")
        
        adm_t1, adm_t2, adm_t3 = st.tabs(["📊 Database Viewer", "👤 User Manager", "💰 Money God Mode"])
        
        with adm_t1:
            st.subheader("Volledige Database JSON")
            st.json(db)
            if st.button("🚨 WIP VOLLEDIGE DATASTORE"):
                db = {"users": {SUPER_ADMIN: db["users"][SUPER_ADMIN]}, "klassen": {}}
                sla_db_op(db); st.rerun()

        with adm_t2:
            st.subheader("Verwijder Gebruikers")
            target_user = st.selectbox("Selecteer gebruiker", [u for u in db["users"].keys() if u != SUPER_ADMIN])
            if st.button(f"Verwijder {target_user} permanent"):
                del db["users"][target_user]
                sla_db_op(db); st.success(f"{target_user} is gewist!"); st.rerun()

        with adm_t3:
            st.subheader("Geld toevoegen aan wie je wilt")
            target_m = st.selectbox("Naar wie?", list(db["users"].keys()))
            bedrag = st.number_input("Bedrag", 0, 1000000, 1000)
            if st.button("Geef Geld 💸"):
                db["users"][target_m]["geld"] += bedrag
                sla_db_op(db); st.success("De bank van Putsie heeft uitgekeerd!"); st.rerun()
    else:
        st.error("Toegang geweigerd. Alleen voor VIP👑.")

elif nav == "🎮 Game Arcade":
    st.title("👾 Arcade")
    if st.button("Alien Shooter 🛸"):
        if random.random() > 0.5: data["geld"] += 2; db["users"][user] = data; sla_db_op(db); st.toast("RAAK!")
