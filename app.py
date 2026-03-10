import streamlit as st
import json
import os
from openai import OpenAI

# --- 1. CONFIGURATIE & SETUP ---
DB_FILE = "database.json"
APP_FILE = "app.py"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
SUPER_ADMIN = "elliot"
SITE_TITLE = "(indev) Putsie EDUCATION 🎓"

# OpenAI Client Setup (Jouw sk-... key)
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
        .vip-badge {{ color: #ffcc00; font-weight: bold; text-shadow: 0 0 10px rgba(255,204,0,0.6); }}
    </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 3. CORE LOGICA FUNCTIES ---
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

def get_display_name(name):
    if name.lower() == SUPER_ADMIN:
        return f"{name.capitalize()} (VIP👑)"
    return name.capitalize()

def vraag_gpt(vraag):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Je bent een motiverende leraar op {SITE_TITLE}. Help de leerling met hun vraag, maar geef niet direct het antwoord. Leg de logica uit."},
                {"role": "user", "content": vraag}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"GPT Error: {e}"

# --- 4. AUTH & INITIALISATIE ---
db = laad_db()
if "elliot" not in db["users"]:
    db["users"]["elliot"] = {"password": "admin", "geld": 10000, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}}
    sla_db_op(db)

if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title(SITE_TITLE)
    u = st.text_input("Naam").lower().strip()
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Start Adventure"):
        if u in db["users"] and db["users"][u]["password"] == p:
            st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
    st.stop()

user = st.session_state.username
data = db["users"].get(user, {})

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title(get_display_name(user))
    st.metric("SALDO", f"€{data.get('geld', 0)}")
    st.markdown("---")
    menu = ["🏠 Home", "📚 Frans Lab", "🏫 Het Klaslokaal", "🤖 AI Huiswerk Hulp", "🎮 Arcade"]
    if user == SUPER_ADMIN: menu.append("🔐 SUPER ADMIN")
    nav = st.radio("Menu", menu)
    if st.button("Log uit"): st.session_state.clear(); st.rerun()

# --- 6. PAGINA'S ---

if nav == "🏠 Home":
    st.title(SITE_TITLE)
    st.subheader(f"Welkom bij de toekomst van onderwijs, {get_display_name(user)}!")
    st.info("Gebruik het menu aan de linkerkant om te beginnen met leren of games te spelen.")

elif nav == "📚 Frans Lab":
    st.title("🧪 Frans Lab")
    t1, t2 = st.tabs(["🎯 Oefenen", "➕ Woorden"])
    # (Logica voor woorden toevoegen/oefenen zoals in eerdere scripts)

elif nav == "🏫 Het Klaslokaal":
    st.title("🏫 Klasomgeving")
    # (Logica voor klas-beheer, taken en chat met VIP labels)
    if user.lower() in LEERKRACHTEN:
        # Teacher Logic...
        pass
    else:
        # Student Logic...
        pass

elif nav == "🤖 AI Huiswerk Hulp":
    st.title("🤖 Jouw Persoonlijke AI Leraar")
    st.write("Stel een vraag over een vak waar je moeite mee hebt.")
    v = st.text_area("Typ hier je vraag...")
    if st.button("Vraag GPT 🚀"):
        if v:
            with st.spinner("De AI leraar kijkt naar je vraag..."):
                antwoord = vraag_gpt(v)
                st.markdown("---")
                st.write(antwoord)
        else: st.warning("Vul eerst een vraag in!")

elif nav == "🔐 SUPER ADMIN" and user == SUPER_ADMIN:
    st.title("🔐 Elliot's Control Panel")
    t_db, t_code = st.tabs(["📊 Database", "📜 Script"])
    with t_db:
        db_txt = st.text_area("Database JSON", value=json.dumps(db, indent=4), height=400)
        if st.button("Save DB"):
            sla_db_op(json.loads(db_txt)); st.rerun()
    with t_code:
        with open(APP_FILE, "r") as f: code = f.read()
        nc = st.text_area("App Code", value=code, height=400)
        if st.button("Save Script"):
            with open(APP_FILE, "w") as f: f.write(nc)
            st.rerun()

elif nav == "🎮 Arcade":
    st.title("👾 Arcade")
    if st.button("Verdien €1 💰"):
        data["geld"] += 1; db["users"][user] = data; sla_db_op(db); st.rerun()
