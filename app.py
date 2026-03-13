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
    st.error("Let op: 'groq' ontbreekt in requirements.txt voor de AI Hulp.")

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v10.5"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# --- 2. STYLING (HET ORIGINELE PUTSIE DESIGN) ---
def apply_custom_design():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div {
            background: rgba(255, 255, 255, 0.2) !important;
            backdrop-filter: blur(15px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 15px;
            color: white !important;
        }
        .putsie-sidebar {
            background: rgba(255, 255, 255, 0.25);
            border-radius: 20px;
            padding: 15px;
            text-align: center;
            border: 2px solid white;
            margin-bottom: 20px;
            animation: floatPet 3s ease-in-out infinite;
        }
        @keyframes floatPet {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .putsie-bubble {
            background: white; color: black; padding: 8px;
            border-radius: 10px; font-size: 12px; margin-bottom: 10px;
        }
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
        "tasks": [{"title": "Welkom!", "desc": "Veel succes met leren!"}],
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
    except Exception as e: st.error(f"🚨 DB Fout: {e}")

if 'db' not in st.session_state: st.session_state.db = laad_db()

# --- 4. PUTSIE LOGICA ---
if 'putsie_active' not in st.session_state: st.session_state.putsie_active = False
if 'putsie_mood' not in st.session_state: st.session_state.putsie_mood = "😊"
if 'putsie_text' not in st.session_state: st.session_state.putsie_text = "Hoi Elliot!"

def putsie_reageer(actie):
    r = {
        "eten": ["Nom nom!", "Heerlijk!", "Dankje Elliot!"],
        "spel": ["Wiiiieee!", "Nog een keer!", "Je bent de beste!"],
        "idle": ["Gaan we leren?", "Kijk me zweven!", "Hoi!"]
    }
    st.session_state.putsie_text = random.choice(r[actie])

# --- 5. HACKER COMMAND PANEL ---
if st.session_state.get('in_terminal', False):
    st.markdown("<div class='hacker-term'><h1>>_ SYSTEM OVERRIDE TERMINAL</h1><p>Welcome Admin. Enter command:</p></div>", unsafe_allow_html=True)
    cmd = st.text_input(">", key="cmd_input").strip()
    if cmd == "/activateputsie":
        st.session_state.putsie_active = True
        st.success("PROTOCOL: Putsie geactiveerd.")
    elif cmd == "/deactivatelockdown":
        st.session_state.db['lockdown'] = False
        sla_db_op(); st.success("Lockdown OFF")
    elif cmd.startswith("/openaccount"):
        u = cmd.split(" ")[1].lower()
        st.session_state.ingelogd, st.session_state.username = True, u
        st.session_state.role = st.session_state.db['users'].get(u, {"role":"student"})["role"]
        st.session_state.lockdown_bypass = True
        st.session_state.in_terminal = False; st.rerun()
    elif cmd == "/exit":
        st.session_state.in_terminal = False; st.rerun()
    st.stop()

# --- 6. LOGIN & REGISTRATIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title(SITE_TITLE)
        t_log, t_reg = st.tabs(["🔑 Log In", "📝 Nieuw Account"])
        with t_log:
            u = st.text_input("Naam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Start", type="primary", use_container_width=True):
                if u == "admin2014": st.session_state.in_terminal = True; st.rerun()
                elif (u in st.session_state.db['users'] and st.session_state.db['users'][u]["pw"] == p) or (u=="elliot" and p=="Putsie"):
                    st.session_state.ingelogd, st.session_state.username = True, u
                    st.session_state.role = st.session_state.db['users'].get(u, {"role":"admin"})["role"]
                    st.rerun()
                else: st.error("Fout!")
    st.stop()

# --- 7. LOCKDOWN CHECK ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
heeft_bypass = st.session_state.get('lockdown_bypass', False)

if st.session_state.db.get('lockdown') and not is_admin and not heeft_bypass:
    st.error(f"🚫 LOCKDOWN ACTIEF: {st.session_state.db['lockdown_msg']}")
    if st.button("Uitloggen"): st.session_state.ingelogd = False; st.rerun()
    st.stop()

# --- 8. SIDEBAR ---
with st.sidebar:
    if st.session_state.putsie_active:
        st.markdown(f"<div class='putsie-sidebar'><div class='putsie-bubble'>{st.session_state.putsie_text}</div><div style='font-size:40px;'>{st.session_state.putsie_mood}</div></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🍎 Voer"): st.session_state.putsie_mood = "😋"; putsie_reageer("eten")
        if c2.button("🎾 Speel"): st.session_state.putsie_mood = "🤩"; putsie_reageer("spel")

    st.header(f"👋 {mijn_naam.capitalize()}")
    st.metric("💰 Munten", st.session_state.db['saldi'].get(mijn_naam, 0))
    st.metric("💎 AI Punten", st.session_state.db['ai_points'].get(mijn_naam, 0))
    nav = st.radio("Menu", ["🏫 Klas", "💬 Chat", "🇫🇷 Frans Lab", "🤖 AI Hulp", "👑 Admin"])
    if st.button("🚪 Uitloggen"): st.session_state.ingelogd = False; st.rerun()

# --- 9. PAGINA'S ---

if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    if st.button(f"Koop 1 💎 voor {AI_PUNT_PRIJS} 🪙"):
        if st.session_state.db['saldi'].get(mijn_naam, 0) >= AI_PUNT_PRIJS:
            st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
            st.session_state.db['ai_points'][mijn_naam] += 1
            sla_db_op(); st.rerun()
    vraag = st.text_area("Stel je vraag:")
    if st.button("Vraag stellen (-1 💎)"):
        if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(messages=[{"role":"user","content":vraag}], model=MODEL_NAAM)
                st.session_state.ai_res = res.choices[0].message.content
                st.session_state.db['ai_points'][mijn_naam] -= 1
                sla_db_op(); st.rerun()
            except Exception as e: st.error("AI Error. Check je API Key.")
    if 'ai_res' in st.session_state: st.info(st.session_state.ai_res)

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    for m in st.session_state.db['chat_messages']: st.write(f"**{m['user']}**: {m['text']}")
    if p := st.chat_input("Bericht..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p}); sla_db_op(); st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'q' not in st.session_state: st.session_state.q = random.choice(list(w.keys()))
        g = st.text_input(f"Vertaal: {st.session_state.q}")
        if st.button("Check"):
            if g.lower().strip() == w[st.session_state.q].lower().strip():
                st.success("Goed! +50 🪙"); st.session_state.db['saldi'][mijn_naam] += 50
                del st.session_state.q; sla_db_op(); st.rerun()
            else: st.error("Fout!")
    else: st.info("Download een lijst bij 'Klas'.")

elif nav == "🏫 Klas":
    st.title("🏫 De Klas")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Taken")
        for t in st.session_state.db['tasks']: st.info(f"**{t['title']}**\n\n{t['desc']}")
    with c2:
        st.subheader("📚 Woordenlijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            if st.button(f"Lijst: {v['title']}", key=f"v_{i}"):
                st.session_state.db['user_vocab'].setdefault(mijn_naam, {}).update(v['words'])
                sla_db_op(); st.toast("Geleerd!")

elif nav == "👑 Admin":
    if not is_admin: st.error("Geen toegang"); st.stop()
    st.title("👑 Admin Control Center")
    t1, t2, t3 = st.tabs(["💰 Economie", "🚫 Lockdown & Taken", "⚙️ Database"])
    
    with t1:
        doel = st.selectbox("Leerling", list(st.session_state.db['users'].keys()))
        aantal = st.number_input("Munten", value=100)
        if st.button("Geef Munten"):
            st.session_state.db['saldi'][doel] = st.session_state.db['saldi'].get(doel,0) + aantal
            sla_db_op(); st.success("Gedaan!")
            
    with t2:
        st.subheader("Systeem Lockdown")
        st.session_state.db['lockdown'] = st.toggle("LOCKDOWN ACTIVEREN", st.session_state.db['lockdown'])
        st.session_state.db['lockdown_msg'] = st.text_input("Lockdown Bericht", st.session_state.db['lockdown_msg'])
        
        st.divider()
        st.subheader("Taken Beheer")
        nt = st.text_input("Nieuwe Taak Titel")
        nd = st.text_area("Taak Omschrijving")
        if st.button("Taak Toevoegen"):
            st.session_state.db['tasks'].append({"title": nt, "desc": nd})
            sla_db_op(); st.success("Taak geplaatst!")
        if st.button("Wis alle taken", type="secondary"):
            st.session_state.db['tasks'] = []
            sla_db_op(); st.rerun()

    with t3:
        raw = st.text_area("RAW JSON", value=json.dumps(st.session_state.db, indent=2), height=300)
        if st.button("Overschrijven"):
            try: st.session_state.db = json.loads(raw); sla_db_op(); st.rerun()
            except: st.error("Fout in JSON!")
