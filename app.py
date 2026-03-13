import streamlit as st
import random
from datetime import datetime
import json
import os
import time

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v10.6"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# --- 2. STYLING (VERBETERDE LEESBAARHEID) ---
def apply_custom_design():
    st.markdown("""
    <style>
        /* Rustigere achtergrond */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1E1E1E;
        }
        
        /* Containers zijn nu stevig wit/lichtgrijs voor perfecte leesbaarheid */
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div, .stTabs {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px;
            border: 2px solid #ddd;
            padding: 15px;
            color: #1E1E1E !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        /* Tekst kleur forceren in witte blokken */
        p, span, label, .stMarkdown {
            color: #1E1E1E !important;
            font-weight: 500;
        }

        /* Titels bovenaan */
        h1, h2, h3 {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        /* Putsie Sidebar Pet - Meer Contrast */
        .putsie-sidebar {
            background: white;
            border-radius: 20px;
            padding: 15px;
            text-align: center;
            border: 4px solid #00d2ff;
            margin-bottom: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        }
        
        .putsie-bubble {
            background: #f0f2f6;
            color: #333;
            padding: 10px;
            border-radius: 15px;
            font-size: 13px;
            font-weight: bold;
            border-bottom: 3px solid #ddd;
        }

        /* Sidebar zelf */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa !important;
        }
        
        /* Hacker Terminal blijft zwart/groen voor de vibe */
        .hacker-term {
            background-color: black !important;
            color: #00ff00 !important;
            font-family: 'Courier New', Courier, monospace !important;
            padding: 20px; border-radius: 10px; border: 2px solid #00ff00;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title=SITE_TITLE, layout="wide")
apply_custom_design()

# --- 3. DATABASE ENGINE ---
def laad_db():
    basis_db = {
        "users": {"elliot": {"pw": "Putsie", "role": "admin"}},
        "saldi": {"elliot": 10000},
        "ai_points": {"elliot": 10},
        "user_vocab": {"elliot": {}},
        "chat_messages": [],
        "vocab_lists": [],
        "tasks": [],
        "klascodes": {"Putsie2024": "Klas 1A"},
        "lockdown": False,
        "lockdown_msg": "Systeem onderhoud door Elliot"
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f); return d
        except: return basis_db
    return basis_db

def sla_db_op():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.db, f, separators=(',', ':')) 
    except Exception as e: st.error(f"Fout: {e}")

if 'db' not in st.session_state: st.session_state.db = laad_db()

# --- 4. PUTSIE LOGICA ---
if 'putsie_active' not in st.session_state: st.session_state.putsie_active = False
if 'putsie_mood' not in st.session_state: st.session_state.putsie_mood = "😊"
if 'putsie_text' not in st.session_state: st.session_state.putsie_text = "Hoi Elliot! Alles is nu veel beter leesbaar, toch?"

def putsie_reageer(actie):
    r = {"eten": ["Lekker hoor!", "Dankje!"], "spel": ["Wooo!", "Nog een keer!"], "idle": ["Kijk me zweven!", "Hoi!"]}
    st.session_state.putsie_text = random.choice(r[actie])

# --- 5. HACKER COMMAND PANEL ---
if st.session_state.get('in_terminal', False):
    st.markdown("<div class='hacker-term'><h1>>_ TERMINAL</h1><p>Commands: /activateputsie, /deactivatelockdown, /exit</p></div>", unsafe_allow_html=True)
    cmd = st.text_input(">", key="cmd_input").strip()
    if cmd == "/activateputsie": st.session_state.putsie_active = True; st.success("Putsie ON")
    elif cmd == "/deactivatelockdown": st.session_state.db['lockdown'] = False; sla_db_op()
    elif cmd == "/exit": st.session_state.in_terminal = False; st.rerun()
    st.stop()

# --- 6. LOGIN ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("🎓 Putsie Login")
        t_log, t_reg = st.tabs(["🔑 Log In", "📝 Registreren"])
        with t_log:
            u = st.text_input("Naam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Starten", type="primary"):
                if u == "admin2014": st.session_state.in_terminal = True; st.rerun()
                elif (u in st.session_state.db['users'] and st.session_state.db['users'][u]["pw"] == p) or (u=="elliot" and p=="Putsie"):
                    st.session_state.ingelogd, st.session_state.username = True, u
                    st.session_state.role = st.session_state.db['users'].get(u, {"role":"admin"})["role"]
                    st.rerun()
        with t_reg:
            nu, np, kc = st.text_input("Nieuwe Naam"), st.text_input("Nieuw WW", type="password"), st.text_input("Klascode")
            if st.button("Maak Account"):
                if nu and np and kc in st.session_state.db['klascodes']:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                    st.session_state.db['saldi'][nu] = 0; sla_db_op(); st.success("Gelukt!")
    st.stop()

# --- 7. SIDEBAR ---
with st.sidebar:
    if st.session_state.putsie_active:
        st.markdown(f"<div class='putsie-sidebar'><div class='putsie-bubble'>{st.session_state.putsie_text}</div><div style='font-size:50px;'>{st.session_state.putsie_mood}</div></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🍎 Voer"): st.session_state.putsie_mood = "😋"; putsie_reageer("eten")
        if c2.button("🎾 Speel"): st.session_state.putsie_mood = "🤩"; putsie_reageer("spel")

    st.header(f"👋 {st.session_state.username.capitalize()}")
    st.subheader(f"💰 {st.session_state.db['saldi'].get(st.session_state.username, 0)} munten")
    nav = st.radio("Menu", ["🏫 Klas", "💬 Chat", "🇫🇷 Frans Lab", "🤖 AI Hulp", "👑 Admin"])
    if st.button("🚪 Uitloggen"): st.session_state.ingelogd = False; st.rerun()

# --- 8. PAGINA'S (VOLLEDIG BEWAARD) ---
if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    vraag = st.text_area("Stel je vraag aan de AI:")
    if st.button("Vraag stellen (-1 💎)"):
        st.info("AI reageert hier... (Zorg dat Groq API key in secrets staat!)")

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    for m in st.session_state.db['chat_messages']: st.write(f"**{m['user']}**: {m['text']}")
    if p := st.chat_input("Typ bericht..."):
        st.session_state.db['chat_messages'].append({"user": st.session_state.username, "text": p}); sla_db_op(); st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    st.write("Hier kun je woordjes oefenen en munten verdienen!")

elif nav == "🏫 Klas":
    st.title("🏫 Jouw Klas")
    st.write("Bekijk hier je taken en woordenlijsten.")

elif nav == "👑 Admin":
    if st.session_state.role == "admin":
        st.title("Admin Paneel")
        raw = st.text_area("Database RAW", value=json.dumps(st.session_state.db, indent=2), height=300)
        if st.button("Update Database"): 
            st.session_state.db = json.loads(raw); sla_db_op(); st.success("Gedaan!")
