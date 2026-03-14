import streamlit as st
import random
import json
import os
import time

# Probeer de AI bibliotheek te laden
try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' ontbreekt in requirements.txt")

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 💎 v11.0"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

st.set_page_config(page_title=SITE_TITLE, layout="wide", initial_sidebar_state="expanded")

# --- 2. PREMIUM STYLING & QoL ANIMATIES ---
def apply_premium_design():
    st.markdown("""
    <style>
        /* Dynamische Gradiënt Achtergrond */
        .stApp {
            background: linear-gradient(-45deg, #1a2a6c, #b21f1f, #fdbb2d);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: white;
        }
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Glassmorphism voor alle boxen (super strak) */
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div, .stTabs {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(12px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 15px;
            color: white !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        p, span, label, h1, h2, h3 { color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); }

        /* Bouncy Buttons (QoL Feature) */
        .stButton button {
            transition: all 0.3s ease 0s !important;
            border-radius: 10px !important;
        }
        .stButton button:hover {
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4) !important;
        }

        /* Hacker Terminal 2.0 */
        .hacker-term {
            background-color: #050505 !important;
            color: #0f0 !important;
            font-family: 'Courier New', Courier, monospace !important;
            padding: 25px; 
            border-radius: 12px; 
            border: 2px solid #0f0;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            text-shadow: 0 0 5px #0f0;
        }
        
        /* Zorgt dat de tekst in input velden zwart blijft voor leesbaarheid */
        input { color: black !important; text-shadow: none !important; }
        textarea { color: black !important; text-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

apply_premium_design()

# --- 3. DATABASE ENGINE (ROBUUST & BUGVRIJ) ---
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
        "teacher_classes": {}, # NIEUW: Houdt bij welke leraar welke klas heeft
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
    st.markdown("<div class='hacker-term'><h1>>_ SYSTEM OVERRIDE V11.0</h1><p>Welcome, Root User. Waiting for command...</p></div>", unsafe_allow_html=True)
    
    cmd = st.text_input(">").strip()
    
    if cmd == "/deactivatelockdown":
        st.session_state.db['lockdown'] = False
        sla_db_op(); st.toast("🔓 Lockdown gedeactiveerd!", icon="✅")
    elif cmd == "/activatelockdown":
        st.session_state.db['lockdown'] = True
        sla_db_op(); st.toast("🔒 Systeem in Lockdown!", icon="🚨")
    elif cmd.startswith("/openaccount"):
        delen = cmd.split(" ")
        if len(delen) > 1:
            target = delen[1].lower()
            if target in st.session_state.db['users'] or target == "elliot":
                st.session_state.ingelogd = True
                st.session_state.username = target
                st.session_state.role = st.session_state.db['users'].get(target, {}).get("role", "admin")
                st.session_state.lockdown_bypass = True
                st.session_state.in_terminal = False
                st.rerun()
            else: st.warning("User niet gevonden in database.")
    elif cmd == "/exit":
        st.session_state.in_terminal = False; st.rerun()
    st.stop() 

# --- 5. LOGIN LOGICA ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center;'>{SITE_TITLE}</h1>", unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔑 Log In", "📝 Nieuw Account"])
        
        with t_log:
            u = st.text_input("Naam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Start", type="primary", use_container_width=True):
                if u == "admin2014":
                    st.session_state.in_terminal = True; st.rerun()
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
            rol = st.selectbox("Ik ben een...", ["student", "teacher"])
            kc = st.text_input("Vul Klascode in (Studenten) / Kies nieuwe code (Leraar)")
            
            if st.button("Account Aanmaken", use_container_width=True):
                if not nu or not np or not kc: 
                    st.error("⚠️ Vul alle velden in!")
                elif nu in st.session_state.db['users']: 
                    st.error("⚠️ Deze naam is al bezet!")
                else:
                    if rol == "student" and kc not in st.session_state.db['klascodes']:
                        st.error("⛔ Ongeldige klascode! Vraag de leraar.")
                    elif rol == "teacher" and kc in st.session_state.db['klascodes']:
                        st.error("⛔ Deze klascode bestaat al. Kies een unieke code!")
                    else:
                        st.session_state.db['users'][nu] = {"pw": np, "role": rol}
                        st.session_state.db['saldi'][nu] = 0
                        st.session_state.db['ai_points'][nu] = 5
                        st.session_state.db['user_vocab'][nu] = {}
                        
                        if rol == "teacher":
                            st.session_state.db['klascodes'][kc] = f"Klas van {nu}"
                            st.session_state.db['teacher_classes'][nu] = kc
                            
                        sla_db_op()
                        st.success("✅ Account succesvol aangemaakt! Log nu in.")
    st.stop()

# --- 6. PERMISSIES & LOCKDOWN ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"
heeft_bypass = st.session_state.get('lockdown_bypass', False)

if st.session_state.db.get('lockdown') and not is_admin and not heeft_bypass:
    st.markdown(f"<div style='text-align:center; padding:100px; background: rgba(255,0,0,0.5); border-radius:20px; color:white;'><h1>🚫 CRITICAL LOCKDOWN</h1><h3>{st.session_state.db['lockdown_msg']}</h3></div>", unsafe_allow_html=True)
    if st.button("Uitloggen"): st.session_state.ingelogd = False; st.rerun()
    st.stop()

# --- 7. SIDEBAR ---
with st.sidebar:
    st.header(f"👋 {mijn_naam.capitalize()}")
    if heeft_bypass: st.caption("🕵️ VIP BYPASS ACTIEF")
    
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("💰 Munten", st.session_state.db['saldi'].get(mijn_naam, 0))
    col_s2.metric("💎 AI Punten", st.session_state.db['ai_points'].get(mijn_naam, 0))
    st.divider()
    
    nav_options = ["🏫 Klas", "💬 Chat", "🇫🇷 Frans Lab", "🤖 AI Hulp"]
    if is_teacher: nav_options.append("👩‍🏫 Leraar Paneel")
    if is_admin: nav_options.append("👑 Admin Room")
    
    nav = st.radio("Ga naar:", nav_options)
    st.divider()
    if st.button("🚪 Uitloggen", use_container_width=True):
        st.session_state.ingelogd = False; st.session_state.lockdown_bypass = False; st.rerun()

# --- 8. PAGINA'S ---

if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp (Llama 3.1)")
    c1, c2 = st.columns([2, 1])
    with c2:
        with st.container():
            st.write("🛒 **Winkel**")
            if st.button(f"Koop 1 💎 voor {AI_PUNT_PRIJS} 🪙", use_container_width=True):
                if st.session_state.db['saldi'].get(mijn_naam, 0) >= AI_PUNT_PRIJS:
                    st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
                    st.session_state.db['ai_points'][mijn_naam] += 1
                    sla_db_op(); st.toast("💎 AI Punt gekocht!", icon="🛒"); st.rerun()
                else: st.error("Te weinig munten!")
    with c1:
        vraag = st.text_area("Stel je vraag aan de AI leraar:")
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
        if 'ai_res' in st.session_state:
            st.info(st.session_state.ai_res)

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    with st.container(height=450, border=True):
        for m in st.session_state.db['chat_messages']:
            st.markdown(f"**{m['user'].capitalize()}**: {m['text']}")
    if p := st.chat_input("Typ iets in de groep..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op(); st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'q' not in st.session_state: st.session_state.q = random.choice(list(w.keys()))
        st.subheader(f"Vertaal: {st.session_state.q}")
        g = st.text_input("Antwoord hier:")
        if st.button("Controleren", type="primary"):
            if g.lower().strip() == w[st.session_state.q].lower().strip():
                st.session_state.db['saldi'][mijn_naam] += 50
                st.toast("Goed gedaan! +50 🪙", icon="🎉")
                del st.session_state.q; sla_db_op(); st.rerun()
            else: st.error("Helaas, dat is niet juist!")
    else: st.info("Je hebt nog geen woorden. Ga naar de 'Klas' om er een paar te downloaden.")

elif nav == "🏫 Klas":
    st.title("🏫 De Klas")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Huiswerk & Taken")
        if not st.session_state.db['tasks']: st.write("Geen taken op dit moment!")
        for t in st.session_state.db['tasks']:
            with st.container(border=True): st.markdown(f"**{t['title']}**\n\n{t['desc']}")
    with c2:
        st.subheader("📚 Woordenlijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            if st.button(f"📥 Download {v['title']}", key=f"dl_{i}", use_container_width=True):
                st.session_state.db['user_vocab'].setdefault(mijn_naam, {}).update(v['words'])
                sla_db_op(); st.toast(f"{v['title']} toegevoegd aan je Lab!", icon="📚")

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Leraar Dashboard")
    
    # De 1-Klas Beveiliging
    mijn_klas = st.session_state.db.get('teacher_classes', {}).get(mijn_naam, "Geen")
    st.info(f"Jij beheert klascode: **{mijn_klas}**")
    
    t1, t2 = st.tabs(["📋 Taak Posten", "📖 Woordenlijst Delen"])
    with t1:
        tt, td = st.text_input("Taak Titel"), st.text_area("Uitleg (Wat moeten ze doen?)")
        if st.button("Post Taak naar Klas"):
            if tt and td:
                st.session_state.db['tasks'].append({"title": tt, "desc": td})
                sla_db_op(); st.toast("Taak geplaatst!", icon="✅"); st.rerun()
            else: st.warning("Vul alles in.")
    with t2:
        lt, lw = st.text_input("Lijst Naam"), st.text_area("Format: nederlands=frans (1 woord per regel)")
        if st.button("Deel Lijst met Klas"):
            if lt and lw:
                d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in lw.split("\n") if "=" in l}
                st.session_state.db['vocab_lists'].append({"title": lt, "words": d})
                sla_db_op(); st.toast("Lijst gedeeld!", icon="✅"); st.rerun()

elif nav == "👑 Admin Room":
    st.title("👑 Admin Control Room")
    t1, t2, t3 = st.tabs(["🚨 Systeem Lockdown", "💰 Economie & Spelers", "⚙️ Database Control"])
    
    with t1:
        st.subheader("Lockdown Status")
        st.session_state.db['lockdown'] = st.toggle("Activeer Global Lockdown", value=st.session_state.db['lockdown'])
        st.session_state.db['lockdown_msg'] = st.text_input("Lockdown Bericht", value=st.session_state.db['lockdown_msg'])
        if st.button("Opslaan & Toepassen", type="primary"):
            sla_db_op(); st.toast("Status gewijzigd!", icon="🚨")
            
    with t2:
        st.subheader("Munten & Spelers Beheer")
        doel = st.selectbox("Selecteer Leerling", list(st.session_state.db['users'].keys()))
        aantal = st.number_input("Aantal Munten", value=100)
        if st.button("Verwerk Transactie"):
            st.session_state.db['saldi'][doel] = st.session_state.db['saldi'].get(doel, 0) + aantal
            sla_db_op(); st.toast(f"Transactie geslaagd voor {doel}", icon="💰")
            
    with t3:
        st.subheader("RAW Database Editor")
        st.warning("⚠️ Let op: Eén verkeerde komma kan de game breken!")
        raw = st.text_area("JSON View", value=json.dumps(st.session_state.db, indent=2), height=300)
        c_db1, c_db2 = st.columns(2)
        if c_db1.button("Database Overschrijven", type="primary", use_container_width=True):
            try: st.session_state.db = json.loads(raw); sla_db_op(); st.toast("DB Opgeslagen!", icon="💾"); st.rerun()
            except: st.error("JSON Syntax Fout!")
        if c_db2.button("Wis de Chat", use_container_width=True):
            st.session_state.db['chat_messages'] = []
            sla_db_op(); st.toast("Chat is helemaal leeg!", icon="🧹"); st.rerun()
