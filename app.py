import streamlit as st
import random
from datetime import datetime
import json
import os

# We gebruiken de Groq client voor de snelle Llama modellen
try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' bibliotheek niet gevonden. Voeg 'groq' toe aan requirements.txt")

# --- 1. CONFIGURATIE & PADEN ---
SITE_TITLE = "Putsie EDUCATION 🎓 v9.1"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000 

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DE DATABASE MOTOR (BULLETPROOF) ---
def laad_db():
    basis_db = {
        "users": {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}},
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
                data = json.load(f)
                # Zorg dat de lockdown sleutels altijd bestaan
                if "lockdown" not in data: data["lockdown"] = False
                if "lockdown_msg" not in data: data["lockdown_msg"] = "Onderhoud"
                return data
        except: return basis_db
    return basis_db

def sla_db_op():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = laad_db()

# --- 3. LOGIN SYSTEEM ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title(SITE_TITLE)
        t_log, t_reg = st.tabs(["🔑 Inloggen", "📝 Registreren"])
        with t_log:
            u = st.text_input("Gebruikersnaam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Inloggen", type="primary", use_container_width=True):
                if u == "elliot" and p == "Putsie":
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"
                    st.rerun()
                elif u in st.session_state.db['users'] and st.session_state.db['users'][u]["pw"] == p:
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, u, st.session_state.db['users'][u]["role"]
                    st.rerun()
                else: st.error("Inloggegevens onjuist.")
        with t_reg:
            nu = st.text_input("Nieuwe Naam").lower().strip()
            np = st.text_input("Wachtwoord ", type="password")
            kc = st.text_input("Klascode")
            if st.button("Account Aanmaken", use_container_width=True):
                if kc in st.session_state.db['klascodes'] and nu and nu not in st.session_state.db['users']:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                    st.session_state.db['saldi'][nu], st.session_state.db['ai_points'][nu] = 0, 5
                    st.session_state.db['user_vocab'][nu] = {}
                    sla_db_op()
                    st.success("Account gemaakt! Je kunt nu inloggen.")
                else: st.error("Naam bezet of code fout.")
    st.stop()

# --- 4. RECHTEN & LOCKDOWN CHECK ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"

# DE LOCKDOWN BLOKKADE
if st.session_state.db.get('lockdown', False) and not is_admin:
    st.markdown(f"""
        <div style="text-align:center; padding:100px; background-color:#ff4b4b; border-radius:20px; color:white;">
            <h1 style="font-size:80px;">🚫</h1>
            <h1>SYSTEEM IN LOCKDOWN</h1>
            <p style="font-size:20px;">{st.session_state.db.get('lockdown_msg', 'Onderhoud door de admin')}</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Log uit"):
        st.session_state.ingelogd = False
        st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header(f"👤 {mijn_naam.capitalize()}")
    c1, c2 = st.columns(2)
    c1.metric("🪙", st.session_state.db['saldi'].get(mijn_naam, 0))
    c2.metric("💎", st.session_state.db['ai_points'].get(mijn_naam, 0))
    st.divider()
    menu = ["🏫 Klas", "💬 Chat", "🇫🇷 Frans Lab", "🤖 AI Hulp"]
    if is_teacher: menu.append("👩‍🏫 Leraar")
    if is_admin: menu.append("👑 Admin")
    nav = st.radio("Navigatie", menu)
    st.divider()
    if st.button("🚪 Uitloggen", use_container_width=True):
        st.session_state.ingelogd = False
        st.rerun()

# --- 6. PAGINA LOGICA ---

if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    col_a, col_b = st.columns([2, 1])
    with col_b:
        with st.container(border=True):
            st.write("🛒 **Winkel**")
            if st.button(f"Koop 1 💎 ({AI_PUNT_PRIJS} 🪙)"):
                if st.session_state.db['saldi'].get(mijn_naam, 0) >= AI_PUNT_PRIJS:
                    st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
                    st.session_state.db['ai_points'][mijn_naam] = st.session_state.db['ai_points'].get(mijn_naam, 0) + 1
                    sla_db_op(); st.rerun()
                else: st.error("Te weinig munten!")
    with col_a:
        vraag = st.text_area("Stel je vraag:")
        if st.button("Vraag AI (-1 💎)", type="primary"):
            if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    resp = client.chat.completions.create(
                        model=MODEL_NAAM,
                        messages=[{"role": "system", "content": "Je bent een leraar."}, {"role": "user", "content": vraag}]
                    )
                    st.session_state.ai_res = resp.choices[0].message.content
                    st.session_state.db['ai_points'][mijn_naam] -= 1
                    sla_db_op()
                except Exception as e: st.error(f"Fout: {e}")
            else: st.warning("Geen punten!")
        if 'ai_res' in st.session_state:
            st.info(st.session_state.ai_res)

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    with st.container(height=400, border=True):
        for m in st.session_state.db['chat_messages']:
            st.write(f"**{m['user'].capitalize()}**: {m['text']}")
    if p := st.chat_input("Bericht..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op(); st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'huidig' not in st.session_state: st.session_state.huidig = random.choice(list(w.keys()))
        st.subheader(f"Vertaal: {st.session_state.huidig}")
        gok = st.text_input("Antwoord")
        if st.button("Check"):
            if gok.lower().strip() == w[st.session_state.huidig].lower().strip():
                st.success("Top! +50 🪙"); st.session_state.db['saldi'][mijn_naam] += 50
                del st.session_state.huidig; sla_db_op(); st.rerun()
            else: st.error("Helaas!")
    else: st.info("Geen woorden.")

elif nav == "🏫 Klas":
    st.title("🏫 De Klas")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Taken")
        for t in st.session_state.db['tasks']:
            with st.container(border=True): st.write(f"**{t['title']}**\n\n{t['desc']}")
    with c2:
        st.subheader("📚 Lijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            if st.button(f"Download {v['title']}", key=i):
                st.session_state.db['user_vocab'].setdefault(mijn_naam, {}).update(v['words'])
                sla_db_op(); st.toast("Klaar!")

elif nav == "👩‍🏫 Leraar":
    st.title("👩‍🏫 Leraar Paneel")
    t1, t2 = st.tabs(["Taken", "Lijsten"])
    with t1:
        tt, td = st.text_input("Titel"), st.text_area("Uitleg")
        if st.button("Post Taak"):
            st.session_state.db['tasks'].append({"title": tt, "desc": td}); sla_db_op()
    with t2:
        lt, lw = st.text_input("Naam"), st.text_area("nl=fr")
        if st.button("Deel Lijst"):
            d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in lw.split("\n") if "=" in l}
            st.session_state.db['vocab_lists'].append({"title": lt, "words": d}); sla_db_op()

elif nav == "👑 Admin":
    st.title("👑 Admin Control Room")
    t_lock, t_eco, t_db = st.tabs(["🚨 Lockdown", "💰 Economie", "⚙️ Database"])
    
    with t_lock:
        st.subheader("Systeem Vergrendelen")
        is_locked = st.toggle("ACTIVEER LOCKDOWN", value=st.session_state.db['lockdown'])
        lock_msg = st.text_input("Lockdown Bericht", value=st.session_state.db['lockdown_msg'])
        if st.button("Update Lockdown Status"):
            st.session_state.db['lockdown'] = is_locked
            st.session_state.db['lockdown_msg'] = lock_msg
            sla_db_op()
            st.success("Status bijgewerkt!")
            st.rerun()

    with t_eco:
        doel = st.selectbox("Leerling", list(st.session_state.db['users'].keys()))
        aantal = st.number_input("Munten", value=100)
        if st.button("Geef Munten"):
            st.session_state.db['saldi'][doel] = st.session_state.db['saldi'].get(doel, 0) + aantal
            sla_db_op(); st.success("Gedaan!")

    with t_db:
        raw = st.text_area("RAW JSON", value=json.dumps(st.session_state.db, indent=4), height=400)
        if st.button("Overschrijf Database"):
            try:
                st.session_state.db = json.loads(raw); sla_db_op(); st.rerun()
            except: st.error("JSON Fout!")
