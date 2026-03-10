import streamlit as st
import json
import os
import random
import string
from datetime import datetime
from openai import OpenAI

# --- 1. CONFIGURATIE & SETUP ---
DB_FILE = "database.json"
APP_FILE = "app.py"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
SUPER_ADMIN = "elliot"
SITE_TITLE = "(indev) Putsie EDUCATION 🎓"

# OpenAI Client Setup met jouw API-key
client = OpenAI(api_key="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")

st.set_page_config(page_title=SITE_TITLE, page_icon="🎓", layout="wide")

# --- 2. VISUAL STYLING ---
def apply_custom_styles():
    st.markdown(f"""
    <style>
        .stApp {{ background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: white; }}
        [data-testid="stVerticalBlockBorderWrapper"] {{ 
            background: rgba(255, 255, 255, 0.05) !important; 
            backdrop-filter: blur(15px) !important; border-radius: 20px !important; 
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 25px !important; box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
        }}
        .stButton > button {{ 
            border-radius: 12px !important; 
            background: linear-gradient(45deg, #00dbde 0%, #fc00ff 100%) !important;
            color: white !important; font-weight: 800 !important; transition: 0.4s !important;
            border: none !important;
        }}
        .stButton > button:hover {{ transform: scale(1.05) !important; box-shadow: 0 0 20px rgba(0, 219, 222, 0.6) !important; }}
        .stTextArea textarea {{ background-color: #1e1e2e !important; color: #00ff00 !important; font-family: 'Courier New', monospace !important; }}
        .stChatMessage {{ background: rgba(255,255,255,0.05) !important; border-radius: 15px !important; }}
        .vip-badge {{ color: #ffcc00; font-weight: bold; text-shadow: 0 0 8px rgba(255,204,0,0.6); }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 3. DATABASE FUNCTIES ---
def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            db.setdefault("klassen", {}); db.setdefault("users", {})
            return db
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

# --- 4. HULP FUNCTIES ---
def get_display_name(name):
    if name.lower() == SUPER_ADMIN:
        return f"{name.capitalize()} (VIP👑)"
    return name.capitalize()

def ai_huiswerk_hulp(vraag):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Je bent een behulpzame leraar op het Putsie EDUCATION platform. Geef niet direct het antwoord, maar leg de stappen uit zodat de leerling het zelf leert. Wees bemoedigend en kort."},
                {"role": "user", "content": vraag}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

# --- 5. AUTHENTICATIE ---
db = laad_db()
if "elliot" not in db["users"]:
    db["users"]["elliot"] = {"password": "admin", "geld": 9999, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}}
    sla_db_op(db)

if 'ingelogd' not in st.session_state:
    st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title(SITE_TITLE)
    t1, t2 = st.tabs(["🚀 Inloggen", "📝 Registreren"])
    with t1:
        u = st.text_input("Gebruikersnaam").lower().strip()
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Start Leren"):
            if u in db["users"] and db["users"][u].get("password") == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Inloggegevens onjuist!")
    with t2:
        ru = st.text_input("Kies Naam").lower().strip()
        rp = st.text_input("Kies Wachtwoord", type="password")
        if st.button("Account Aanmaken"):
            if ru and rp and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}}
                sla_db_op(db); st.success("Klaar! Log nu in."); st.balloons()
    st.stop()

# --- 6. MAIN APP LOGICA ---
user = st.session_state.username
data = db["users"].get(user, {})

with st.sidebar:
    st.title(f"👾 {get_display_name(user)}")
    st.metric("SALDO", f"€{data.get('geld', 0)}")
    st.markdown("---")
    menu = ["🏠 Home", "📚 Frans Lab", "🏫 Het Klaslokaal", "🤖 AI Studie Maatje", "🎮 Game Arcade"]
    if user == SUPER_ADMIN: menu.append("🔐 SUPER ADMIN")
    nav = st.radio("Navigatie", menu)
    if st.button("🚪 Log uit"): st.session_state.clear(); st.rerun()

# --- PAGINA: HOME ---
if nav == "🏠 Home":
    st.title(SITE_TITLE)
    st.subheader(f"Welkom terug, {get_display_name(user)}!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Top Verdieners")
        sorted_users = sorted(db["users"].items(), key=lambda x: x[1].get("geld", 0), reverse=True)[:5]
        for i, (name, d) in enumerate(sorted_users):
            st.write(f"{i+1}. {get_display_name(name)} - €{d.get('geld', 0)}")
    with col2:
        st.markdown("### 📢 Mededelingen")
        st.info("De AI Leraar is nu live! Check het menu.")

# --- PAGINA: FRANS LAB ---
elif nav == "📚 Frans Lab":
    st.title("🧪 Frans Woorden Lab")
    t1, t2 = st.tabs(["🎯 Quiz Mode", "➕ Woorden Toevoegen"])
    with t1:
        cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
        w_dict = data.get("woorden", {}).get(cat, {})
        if st.button("Nieuwe Vraag 🎲"):
            if w_dict: st.session_state.quiz_q = random.choice(list(w_dict.keys()))
        if 'quiz_q' in st.session_state:
            st.subheader(f"Vertaal naar Nederlands: {st.session_state.quiz_q}")
            ans = st.text_input("Antwoord:")
            if st.button("Controleer"):
                if ans.lower().strip() == w_dict[st.session_state.quiz_q].lower().strip():
                    data["geld"] += 15; db["users"][user] = data; sla_db_op(db); st.toast("Correct! +€15"); del st.session_state.quiz_q; st.rerun()
                else: st.error("Helaas, probeer het nog eens.")
    with t2:
        col_f, col_n = st.columns(2)
        type_w = st.radio("Type", ["woorden", "werkwoorden"])
        f_w = col_f.text_input("Frans")
        n_w = col_n.text_input("Nederlands")
        if st.button("Opslaan 💾"):
            if f_w and n_w:
                data.setdefault("woorden", {}).setdefault(type_w, {})[f_w] = n_w
                db["users"][user] = data; sla_db_op(db); st.success("Woord toegevoegd!")

# --- PAGINA: HET KLASLOKAAL ---
elif nav == "🏫 Het Klaslokaal":
    st.title("🏫 Klasomgeving")
    
    if user.lower() in LEERKRACHTEN:
        mijn_klas_code = next((c for c, i in db["klassen"].items() if i.get("docent") == user), None)
        if not mijn_klas_code:
            k_naam = st.text_input("Naam van je nieuwe klas")
            if st.button("Klas Bouwen ✨"):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                db["klassen"][code] = {"naam": k_naam, "docent": user, "taken": [], "comments": []}
                sla_db_op(db); st.rerun()
        else:
            klas_info = db["klassen"][mijn_klas_code]
            st.success(f"Klas: **{klas_info.get('naam')}** | Code: `{mijn_klas_code}`")
            tab_tk, tab_st, tab_ch = st.tabs(["📝 Taken", "👥 Leerlingen", "💬 Chat"])
            
            with tab_tk:
                st.subheader("Nieuwe Taak")
                q = st.text_input("Vraag"); a = st.text_input("Antwoord"); g = st.number_input("Geld", 10, 500, 20)
                if st.button("Plaatsen"):
                    klas_info.setdefault("taken", []).append({"vraag": q, "antwoord": a, "beloning": g})
                    sla_db_op(db); st.rerun()
                for i, t in enumerate(klas_info.get("taken", [])):
                    st.write(f"{i+1}. {t.get('vraag')} (€{t.get('beloning')})")
            
            with tab_st:
                leerlingen = [u_n for u_n, d_n in db["users"].items() if d_n.get("klas_id") == mijn_klas_code]
                for l in leerlingen:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"👤 {get_display_name(l)}")
                    if c2.button("Verwijder", key=f"rem_{l}"):
                        db["users"][l]["klas_id"] = None; sla_db_op(db); st.rerun()
            
            with tab_ch:
                for c in klas_info.get("comments", []):
                    with st.chat_message(c['user']):
                        st.write(f"**{get_display_name(c['user'])}**: {c['text']}")
                msg = st.chat_input("Typ bericht...")
                if msg:
                    klas_info.setdefault("comments", []).append({"user": user, "text": msg, "time": datetime.now().strftime("%H:%M")})
                    sla_db_op(db); st.rerun()
    else:
        if not data.get("klas_id"):
            c_in = st.text_input("Klascode invullen:").upper()
            if st.button("Deelnemen"):
                if c_in in db["klassen"]:
                    data["klas_id"] = c_in; db["users"][user] = data; sla_db_op(db); st.rerun()
        else:
            klas = db["klassen"].get(data["klas_id"], {})
            st.header(f"Klas: {klas.get('naam')}")
            st.subheader("📋 Openstaande Taken")
            for i, t in enumerate(klas.get("taken", [])):
                if i not in data.get("voltooide_taken", []):
                    if st.button(f"Taak: {t.get('vraag')}", key=f"t_{i}"):
                        st.session_state.active_t = {"idx": i, "data": t}
            
            if 'active_t' in st.session_state:
                at = st.session_state.active_t
                ans = st.text_input(f"Antwoord voor: {at['data']['vraag']}")
                if st.button("Inleveren"):
                    if ans.lower().strip() == at['data']['antwoord'].lower().strip():
                        data["geld"] += at['data']['beloning']; data.setdefault("voltooide_taken", []).append(at['idx'])
                        db["users"][user] = data; sla_db_op(db); del st.session_state.active_t; st.balloons(); st.rerun()

            st.markdown("---")
            st.subheader("💬 Klas Chat")
            for c in klas.get("comments", [])[-10:]:
                with st.chat_message(c['user']):
                    st.write(f"**{get_display_name(c['user'])}**: {c['text']}")
            n_m = st.chat_input("Zeg iets...")
            if n_m:
                db["klassen"][data["klas_id"]].setdefault("comments", []).append({"user": user, "text": n_m, "time": datetime.now().strftime("%H:%M")})
                sla_db_op(db); st.rerun()

# --- PAGINA: AI STUDIE MAATJE ---
elif nav == "🤖 AI Studie Maatje":
    st.title("🤖 AI Studie Maatje")
    st.write("Stel een vraag over je huiswerk en de AI helpt je op weg!")
    v = st.text_area("Wat wil je weten?")
    if st.button("Vraag AI 🚀"):
        if v:
            with st.spinner("AI denkt na..."):
                res = ai_huiswerk_hulp(v)
                st.markdown("---")
                st.markdown(res)

# --- PAGINA: SUPER ADMIN ---
elif nav == "🔐 SUPER ADMIN" and user == SUPER_ADMIN:
    st.title("⚡ God Mode")
    t1, t2 = st.tabs(["🗄️ Database Editor", "📜 Script Editor"])
    with t1:
        db_txt = st.text_area("Raw JSON", value=json.dumps(db, indent=4), height=400)
        if st.button("Opslaan JSON"):
            try:
                new_db = json.loads(db_txt)
                sla_db_op(new_db); st.success("DB updated!"); st.rerun()
            except: st.error("JSON Error")
    with t2:
        with open(APP_FILE, "r") as f: code = f.read()
        new_code = st.text_area("App Code", value=code, height=500)
        if st.button("Script Updaten"):
            with open(APP_FILE, "w") as f: f.write(new_code)
            st.success("Code updated!"); st.rerun()

# --- PAGINA: ARCADE ---
elif nav == "🎮 Game Arcade":
    st.title("👾 Arcade")
    if st.button("Klik voor €1 💰"):
        data["geld"] += 1; db["users"][user] = data; sla_db_op(db); st.rerun()
