import streamlit as st
import random
from datetime import datetime
import json
import os
import time

# Probeer de AI bibliotheek te laden voor de echte AI Hulp
try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' ontbreekt in requirements.txt. Voeg deze toe voor de AI!")

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v10.8"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# --- 2. STYLING (HOGE LEESBAARHEID + 3D PUTSIE LOOK) ---
def apply_custom_design():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #1E1E1E;
        }
        /* Containers: Wit en goed leesbaar voor taken en chat */
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div, .stTabs {
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px;
            border: 2px solid #ddd;
            padding: 15px;
            color: #1E1E1E !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        p, span, label, .stMarkdown { color: #1E1E1E !important; font-weight: 500; }
        h1, h2, h3 { color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }

        /* Putsie Sidebar Pet (Zwevend effect) */
        .putsie-sidebar {
            background: white; border-radius: 20px; padding: 15px;
            text-align: center; border: 4px solid #00d2ff; margin-bottom: 20px;
            animation: floatPet 3s ease-in-out infinite;
        }
        @keyframes floatPet {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .putsie-bubble {
            background: #f0f2f6; color: #333; padding: 10px;
            border-radius: 15px; font-size: 13px; font-weight: bold; margin-bottom: 10px;
        }
        /* Hacker Terminal Style */
        .hacker-term {
            background-color: black !important; color: #00ff00 !important;
            font-family: 'Courier New', Courier, monospace !important;
            padding: 20px; border-radius: 10px; border: 2px solid #00ff00;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title=SITE_TITLE, layout="wide")
apply_custom_design()

# --- 3. DATABASE ENGINE (VOLLEDIG) ---
def laad_db():
    basis_db = {
        "users": {"elliot": {"pw": "Putsie", "role": "admin"}},
        "saldi": {"elliot": 10000},
        "ai_points": {"elliot": 10},
        "user_vocab": {"elliot": {}},
        "chat_messages": [],
        "vocab_lists": [],
        "tasks": [{"title": "Welkom bij 10.8", "desc": "Check de nieuwe terminal commands!"}],
        "klascodes": {"Putsie2024": "Klas 1A"},
        "lockdown": False,
        "lockdown_msg": "Systeem onderhoud door Elliot"
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k in basis_db: 
                    if k not in d: d[k] = basis_db[k]
                return d
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
if 'putsie_text' not in st.session_state: st.session_state.putsie_text = "Hoi Elliot! Ik ben klaar voor actie!"

def putsie_reageer(actie):
    r = {"eten": ["Heerlijk!", "Dankjewel!", "Nom nom!"], "spel": ["Wooo!", "High score!"], "idle": ["Kijk me gaan!", "Hoi!"]}
    st.session_state.putsie_text = random.choice(r[actie])

# --- 5. HACKER COMMAND PANEL (admin2014) ---
if st.session_state.get('in_terminal', False):
    st.markdown("<div class='hacker-term'><h1>>_ PUTSIE SYSTEM V10.8</h1><p>Gebruik: /activateputsie, /deactivatelockdown, /exit</p></div>", unsafe_allow_html=True)
    cmd = st.text_input("ROOT Command:", key="cmd_input").strip()
    if cmd == "/activateputsie":
        st.session_state.putsie_active = True
        st.success("PROTOCOL: Putsie Pet online.")
    elif cmd == "/deactivatelockdown":
        st.session_state.db['lockdown'] = False
        sla_db_op(); st.success("LOCKDOWN OFF")
    elif cmd == "/exit":
        st.session_state.in_terminal = False; st.rerun()
    st.stop()

# --- 6. LOGIN SYSTEEM ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title("🎓 Putsie Education")
        u = st.text_input("Gebruikersnaam").lower().strip()
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen", type="primary", use_container_width=True):
            if u == "admin2014": st.session_state.in_terminal = True; st.rerun()
            elif (u in st.session_state.db['users'] and st.session_state.db['users'][u]["pw"] == p) or (u=="elliot" and p=="Putsie"):
                st.session_state.ingelogd, st.session_state.username = True, u
                st.session_state.role = st.session_state.db['users'].get(u, {"role":"admin"})["role"]
                st.rerun()
            else: st.error("Toegang geweigerd.")
    st.stop()

# --- 7. LOCKDOWN ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"

if st.session_state.db.get('lockdown') and not is_admin:
    st.error(f"⚠️ SYSTEEM BLOKKADE: {st.session_state.db['lockdown_msg']}")
    st.stop()

# --- 8. SIDEBAR (MET PUTSIE) ---
with st.sidebar:
    if st.session_state.putsie_active:
        st.markdown(f"<div class='putsie-sidebar'><div class='putsie-bubble'>{st.session_state.putsie_text}</div><div style='font-size:50px;'>{st.session_state.putsie_mood}</div></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🍎 Voer"): st.session_state.putsie_mood = "😋"; putsie_reageer("eten")
        if c2.button("🎾 Speel"): st.session_state.putsie_mood = "🤩"; putsie_reageer("spel")

    st.header(f"👋 {mijn_naam.capitalize()}")
    st.metric("💰 Munten", st.session_state.db['saldi'].get(mijn_naam, 0))
    st.metric("💎 AI Punten", st.session_state.db['ai_points'].get(mijn_naam, 0))
    nav = st.radio("Navigatie", ["🏫 Klas & Taken", "💬 Chat", "🇫🇷 Frans Lab", "🤖 AI Hulp", "👩‍🏫 Leraar", "👑 Admin"])
    if st.button("🚪 Uitloggen"): st.session_state.ingelogd = False; st.rerun()

# --- 9. PAGINA'S (DE ECHTE 10.5 INHOUD) ---

if nav == "🏫 Klas & Taken":
    st.title("🏫 Klasoverzicht")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Takenlijst")
        for t in st.session_state.db['tasks']:
            st.info(f"**{t['title']}**\n\n{t['desc']}")
    with c2:
        st.subheader("📚 Woordenlijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            if st.button(f"Download: {v['title']}", key=f"v_{i}"):
                st.session_state.db['user_vocab'].setdefault(mijn_naam, {}).update(v['words'])
                sla_db_op(); st.success("Woorden toegevoegd aan je Lab!")

elif nav == "🤖 AI Hulp":
    st.title("🤖 Echte AI Studiehulp")
    if st.button(f"Koop 💎 voor {AI_PUNT_PRIJS} 🪙"):
        if st.session_state.db['saldi'].get(mijn_naam, 0) >= AI_PUNT_PRIJS:
            st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
            st.session_state.db['ai_points'][mijn_naam] += 1
            sla_db_op(); st.rerun()
    vraag = st.text_area("Stel je vraag aan de AI:")
    if st.button("Vraag stellen (-1 💎)"):
        if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(messages=[{"role":"user","content":vraag}], model=MODEL_NAAM)
                st.session_state.ai_res = res.choices[0].message.content
                st.session_state.db['ai_points'][mijn_naam] -= 1
                sla_db_op(); st.rerun()
            except Exception as e: st.error("Zorg voor een geldige API Key in secrets.")
    if 'ai_res' in st.session_state: st.write(st.session_state.ai_res)

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    for m in st.session_state.db['chat_messages']: st.write(f"**{m['user']}**: {m['text']}")
    if p := st.chat_input("Bericht..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p}); sla_db_op(); st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Het Frans Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'q' not in st.session_state: st.session_state.q = random.choice(list(w.keys()))
        ans = st.text_input(f"Wat is de vertaling van: '{st.session_state.q}'?")
        if st.button("Controleer"):
            if ans.lower().strip() == w[st.session_state.q].lower().strip():
                st.success("Correct! +50 🪙"); st.session_state.db['saldi'][mijn_naam] += 50
                del st.session_state.q; sla_db_op(); st.rerun()
            else: st.error("Helaas, probeer het nog eens.")
    else: st.info("Download eerst een woordenlijst in de Klas sectie!")

elif nav == "👑 Admin":
    if is_admin:
        st.title("👑 Admin Panel")
        tab1, tab2 = st.tabs(["💰 Munten Beheer", "💾 Database & Lockdown"])
        with tab1:
            doel = st.selectbox("Selecteer Leerling", list(st.session_state.db['users'].keys()))
            aantal = st.number_input("Aantal Munten", value=100)
            if st.button("Munten Toevoegen"):
                st.session_state.db['saldi'][doel] = st.session_state.db['saldi'].get(doel, 0) + aantal
                sla_db_op(); st.success(f"Munten gegeven aan {doel}")
        with tab2:
            st.session_state.db['lockdown'] = st.toggle("Activeer Lockdown", st.session_state.db['lockdown'])
            st.session_state.db['lockdown_msg'] = st.text_input("Bericht bij lockdown", st.session_state.db['lockdown_msg'])
            raw = st.text_area("RAW JSON Database", value=json.dumps(st.session_state.db, indent=2), height=250)
            if st.button("Save Database Override"):
                st.session_state.db = json.loads(raw); sla_db_op(); st.rerun()
