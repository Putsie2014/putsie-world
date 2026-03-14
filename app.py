import streamlit as st
import random
from datetime import datetime
import json
import os

# Probeer de AI bibliotheek te laden
try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' ontbreekt in requirements.txt")

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v10.2"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# --- 2. STYLING ---
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
        [data-testid="stVerticalBlock"] > div {
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 10px;
        }
        section[data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.3) !important;
        }
        /* Hacker Terminal Styling */
        .hacker-term {
            background-color: black !important;
            color: #00ff00 !important;
            font-family: 'Courier New', Courier, monospace !important;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #00ff00;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title=SITE_TITLE, layout="wide")
apply_custom_design()

# --- 3. DATABASE ENGINE (COMPACT) ---
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
                d = json.load(f)
                for k in basis_db: 
                    if k not in d: d[k] = basis_db[k]
                return d
        except: return basis_db
    return basis_db

def sla_db_op():
    try:
        schone_db = st.session_state.db.copy()
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(schone_db, f, separators=(',', ':')) 
    except Exception as e:
        st.error(f"🚨 Fout bij opslaan: {e}")

if 'db' not in st.session_state: st.session_state.db = laad_db()

# --- 4. HACKER COMMAND PANEL ---
if st.session_state.get('in_terminal', False):
    st.markdown("<div class='hacker-term'><h1>>_ SYSTEM OVERRIDE TERMINAL</h1><p>Welcome, Admin. Enter command:</p></div>", unsafe_allow_html=True)
    
    cmd = st.text_input(">", key="cmd_input").strip()
    
    if cmd == "/deactivatelockdown":
        st.session_state.db['lockdown'] = False
        sla_db_op()
        st.success("ACCESS GRANTED: Lockdown is nu UIT.")
    elif cmd == "/activatelockdown":
        st.session_state.db['lockdown'] = True
        sla_db_op()
        st.error("SYSTEM ALERT: Lockdown is nu AAN.")
    elif cmd.startswith("/openaccount"):
        delen = cmd.split(" ")
        if len(delen) > 1:
            target = delen[1].lower()
            if target in st.session_state.db['users'] or target == "elliot":
                st.session_state.ingelogd = True
                st.session_state.username = target
                st.session_state.role = st.session_state.db['users'].get(target, {}).get("role", "admin")
                st.session_state.lockdown_bypass = True # De magische sleutel
                st.session_state.in_terminal = False
                st.rerun()
            else: st.warning("User niet gevonden in database.")
        else: st.warning("Gebruik: /openaccount [naam]")
    elif cmd == "/exit":
        st.session_state.in_terminal = False
        st.rerun()
    
    st.stop() # Zorgt dat de rest van de website niet laadt zolang je in de terminal zit

# --- 5. LOGIN LOGICA ---
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
                
                # DE GEHEIME TRIGGER VOOR DE TERMINAL
                if u == "admin2014":
                    st.session_state.in_terminal = True
                    st.rerun()
                    
                elif u == "elliot" and p == "Putsie":
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"
                    st.rerun()
                elif u in st.session_state.db['users'] and st.session_state.db['users'][u]["pw"] == p:
                    st.session_state.ingelogd, st.session_state.username = True, u
                    st.session_state.role = st.session_state.db['users'][u]["role"]
                    st.rerun()
                else: st.error("Inloggegevens fout!")
                
        with t_reg:
            nu = st.text_input("Kies Gebruikersnaam").lower().strip()
            np = st.text_input("Kies Wachtwoord", type="password")
            kc = st.text_input("Vul Klascode in")
            if st.button("Account Aanmaken", use_container_width=True):
                if not nu or not np or not kc: st.error("⚠️ Vul alle velden in!")
                elif kc not in st.session_state.db['klascodes']: st.error("⛔ Ongeldige klascode!")
                elif nu in st.session_state.db['users']: st.error("⚠️ Deze naam is al bezet!")
                else:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                    st.session_state.db['saldi'][nu] = 0
                    st.session_state.db['ai_points'][nu] = 5
                    st.session_state.db['user_vocab'][nu] = {}
                    sla_db_op()
                    st.success("✅ Account succesvol aangemaakt! Log nu in.")
    st.stop()

# --- 6. PERMISSIES & LOCKDOWN (MET BYPASS) ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"
heeft_bypass = st.session_state.get('lockdown_bypass', False)

# Als de lockdown AAN is EN je bent geen admin EN je hebt geen bypass pas...
if st.session_state.db.get('lockdown') and not is_admin and not heeft_bypass:
    st.markdown(f"<div style='text-align:center; padding:100px; background: rgba(255,0,0,0.2); border-radius:20px;'><h1>🚫 CRITICAL LOCKDOWN</h1><h3>{st.session_state.db['lockdown_msg']}</h3></div>", unsafe_allow_html=True)
    if st.button("Uitloggen"): st.session_state.ingelogd = False; st.rerun()
    st.stop()

# --- 7. SIDEBAR ---
with st.sidebar:
    st.header(f"👋 {mijn_naam.capitalize()}")
    if heeft_bypass: st.caption("🕵️ VIP BYPASS ACTIEF")
    st.metric("💰 Munten", st.session_state.db['saldi'].get(mijn_naam, 0))
    st.metric("💎 AI Punten", st.session_state.db['ai_points'].get(mijn_naam, 0))
    st.divider()
    nav = st.radio("Ga naar:", ["🏫 Klas", "💬 Chat", "🇫🇷 Frans Lab", "🤖 AI Hulp", "👩‍🏫 Leraar", "👑 Admin"])
    if st.button("🚪 Uitloggen", use_container_width=True):
        st.session_state.ingelogd = False; st.session_state.lockdown_bypass = False; st.rerun()

# --- 8. PAGINA'S (NIETS VERWIJDERD!) ---

if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp (Llama 3.1)")
    c1, c2 = st.columns([2, 1])
    with c2:
        with st.container(border=True):
            st.write("🛒 **Winkel**")
            if st.button(f"Koop 1 💎 voor {AI_PUNT_PRIJS} 🪙"):
                if st.session_state.db['saldi'].get(mijn_naam, 0) >= AI_PUNT_PRIJS:
                    st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
                    st.session_state.db['ai_points'][mijn_naam] += 1
                    sla_db_op(); st.rerun()
                else: st.error("Te weinig munten!")
    with c1:
        vraag = st.text_area("Stel je vraag aan de AI:")
        if st.button("Vraag stellen (-1 💎)", type="primary"):
            if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
                try:
                    if "GROQ_API_KEY" not in st.secrets:
                        st.error("GROQ_API_KEY ontbreekt in Secrets!")
                    else:
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": vraag}],
                            model=MODEL_NAAM,
                        )
                        st.session_state.ai_res = chat_completion.choices[0].message.content
                        st.session_state.db['ai_points'][mijn_naam] -= 1
                        sla_db_op()
                except Exception as e: st.error(f"AI Fout: {e}")
            else: st.warning("Te weinig AI punten!")
        if 'ai_res' in st.session_state: st.info(st.session_state.ai_res)

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    with st.container(height=450, border=True):
        for m in st.session_state.db['chat_messages']:
            st.write(f"**{m['user'].capitalize()}**: {m['text']}")
    if p := st.chat_input("Typ iets..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op(); st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'q' not in st.session_state: st.session_state.q = random.choice(list(w.keys()))
        st.subheader(f"Vertaal: {st.session_state.q}")
        g = st.text_input("Antwoord")
        if st.button("Check"):
            if g.lower().strip() == w[st.session_state.q].lower().strip():
                st.success("Goed! +50 🪙"); st.session_state.db['saldi'][mijn_naam] += 50
                del st.session_state.q; sla_db_op(); st.rerun()
            else: st.error("Fout!")
    else: st.info("Geen woorden in je lijst.")

elif nav == "🏫 Klas":
    st.title("🏫 De Klas")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Huiswerk")
        for t in st.session_state.db['tasks']:
            with st.container(border=True): st.write(f"**{t['title']}**\n\n{t['desc']}")
    with c2:
        st.subheader("📚 Woordenlijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            if st.button(f"Download {v['title']}", key=f"dl_{i}"):
                st.session_state.db['user_vocab'].setdefault(mijn_naam, {}).update(v['words'])
                sla_db_op(); st.toast("Lijst toegevoegd!")

elif nav == "👩‍🏫 Leraar":
    if not is_teacher: st.error("Geen toegang"); st.stop()
    st.title("👩‍🏫 Leraar Paneel")
    t1, t2 = st.tabs(["Taken Posten", "Woorden Delen"])
    with t1:
        tt, td = st.text_input("Taak Titel"), st.text_area("Uitleg")
        if st.button("Post Taak"):
            st.session_state.db['tasks'].append({"title": tt, "desc": td}); sla_db_op(); st.rerun()
    with t2:
        lt, lw = st.text_input("Lijst Naam"), st.text_area("nl=fr (per regel)")
        if st.button("Deel Lijst"):
            d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in lw.split("\n") if "=" in l}
            st.session_state.db['vocab_lists'].append({"title": lt, "words": d}); sla_db_op(); st.rerun()

elif nav == "👑 Admin":
    if not is_admin: st.error("Geen toegang"); st.stop()
    st.title("👑 Admin Control Room")
    t1, t2, t3 = st.tabs(["🚨 Lockdown", "💰 Economie", "⚙️ Database"])
    with t1:
        st.session_state.db['lockdown'] = st.toggle("Lockdown Actief", value=st.session_state.db['lockdown'])
        st.session_state.db['lockdown_msg'] = st.text_input("Bericht", value=st.session_state.db['lockdown_msg'])
        if st.button("Sla Status Op"): sla_db_op(); st.success("Opgeslagen")
    with t2:
        doel = st.selectbox("Leerling", list(st.session_state.db['users'].keys()))
        aantal = st.number_input("Munten", value=100)
        if st.button("Verwerk"):
            st.session_state.db['saldi'][doel] = st.session_state.db['saldi'].get(doel, 0) + aantal
            sla_db_op(); st.success("Gedaan!")
    with t3:
        st.warning("⚠️ RAW Editor: Compact Mode (hier getoond met overzichtelijke opmaak)")
        raw = st.text_area("RAW JSON", value=json.dumps(st.session_state.db, indent=2), height=300)
        if st.button("Database Overschrijven"):
            try: st.session_state.db = json.loads(raw); sla_db_op(); st.rerun()
            except: st.error("JSON Fout!")
