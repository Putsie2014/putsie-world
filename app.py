import streamlit as st
import random
from datetime import datetime
from openai import OpenAI
import json
import os

# --- 1. CONFIGURATIE & PADEN ---
SITE_TITLE = "Putsie EDUCATION 🎓 v8.5"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DE "BULLETPROOF" DATABASE MOTOR ---
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
                # Zorg dat 'users' altijd bestaat
                if "users" not in data: return basis_db
                return data
        except (json.JSONDecodeError, IOError):
            # Als de file corrupt is, gebruiken we de basis en herstellen we de file later
            return basis_db
    return basis_db

def sla_db_op():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.db, f, indent=4)
    except Exception as e:
        st.error(f"Fout bij opslaan: {e}")

# Initialisatie
if 'db' not in st.session_state:
    st.session_state.db = laad_db()

# --- 3. LOGIN SYSTEEM MET HARDCODED ADMIN CHECK ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title(SITE_TITLE)
        tab_log, tab_reg = st.tabs(["🔑 Inloggen", "📝 Registreren"])
        
        with tab_log:
            u_in = st.text_input("Gebruikersnaam").lower().strip()
            p_in = st.text_input("Wachtwoord", type="password")
            if st.button("Start Sessie", type="primary", use_container_width=True):
                # DE HARDCODED REDDING: Als jij 'elliot' bent met het juiste PW, kom je er ALTIJD in
                if u_in == "elliot" and p_in == "Putsie":
                    st.session_state.ingelogd = True
                    st.session_state.username = "elliot"
                    st.session_state.role = "admin"
                    # Herstel jezelf in de DB als je er niet meer in stond
                    if "elliot" not in st.session_state.db['users']:
                        st.session_state.db['users']["elliot"] = {"pw": "Putsie", "role": "admin"}
                        sla_db_op()
                    st.rerun()
                # Normale login check
                elif u_in in st.session_state.db['users'] and st.session_state.db['users'][u_in]["pw"] == p_in:
                    st.session_state.ingelogd = True
                    st.session_state.username = u_in
                    st.session_state.role = st.session_state.db['users'][u_in]["role"]
                    st.rerun()
                else:
                    st.error("Onjuiste gegevens.")

        with tab_reg:
            nu = st.text_input("Nieuwe Naam").lower().strip()
            np = st.text_input("Nieuw Wachtwoord", type="password")
            kc = st.text_input("Klascode")
            if st.button("Maak Account", use_container_width=True):
                if kc in st.session_state.db['klascodes'] and nu and nu not in st.session_state.db['users']:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                    st.session_state.db['saldi'][nu] = 0
                    st.session_state.db['ai_points'][nu] = 5
                    st.session_state.db['user_vocab'][nu] = {}
                    sla_db_op()
                    st.success("Account klaar! Log nu in.")
                else: st.error("Code fout of naam bezet.")
    st.stop()

# --- 4. GLOBALE VARIABELEN ---
mijn_naam = st.session_state.username
# DUBBELE CHECK: Als je naam Elliot is, ben je Admin, wat er ook in de DB staat
if mijn_naam == "elliot":
    is_admin = True
    is_teacher = True
else:
    is_admin = st.session_state.role == "admin"
    is_teacher = st.session_state.role in ["teacher", "admin"]

# --- 5. LOCKDOWN CHECK ---
if st.session_state.db.get('lockdown', False) and not is_admin:
    st.error(f"⚠️ SYSTEEM OP SLOT: {st.session_state.db.get('lockdown_msg', 'Onderhoud')}")
    if st.button("Uitloggen"):
        st.session_state.ingelogd = False
        st.rerun()
    st.stop()

# --- 6. SIDEBAR & NAVIGATIE ---
with st.sidebar:
    st.header(f"👤 {mijn_naam.capitalize()}")
    st.caption(f"Rol: {st.session_state.role}")
    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("🪙", st.session_state.db['saldi'].get(mijn_naam, 0))
    c2.metric("💎", st.session_state.db['ai_points'].get(mijn_naam, 0))
    st.divider()
    
    menu = ["🏫 Klas", "💬 Chat", "🇫🇷 Frans Lab", "🤖 AI Hulp"]
    if is_teacher: menu.append("👩‍🏫 Leraar")
    if is_admin: menu.append("👑 Admin")
    nav = st.radio("Ga naar:", menu)
    
    if st.button("🚪 Uitloggen", use_container_width=True):
        st.session_state.ingelogd = False
        st.rerun()

# --- 7. PAGINA LOGICA ---

if nav == "🏫 Klas":
    st.title("🏫 De Klas")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Taken")
        for t in st.session_state.db['tasks']:
            with st.container(border=True):
                st.write(f"**{t['title']}**")
                st.caption(t['desc'])
    with col2:
        st.subheader("📚 Lijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            with st.container(border=True):
                st.write(f"📖 {v['title']}")
                if st.button(f"Download {v['title']}", key=f"v_{i}"):
                    if mijn_naam not in st.session_state.db['user_vocab']: st.session_state.db['user_vocab'][mijn_naam] = {}
                    st.session_state.db['user_vocab'][mijn_naam].update(v['words'])
                    sla_db_op()
                    st.toast("Lijst toegevoegd!")

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    with st.container(height=400, border=True):
        for m in st.session_state.db['chat_messages']:
            st.markdown(f"**{m['user'].capitalize()}**: {m['text']}")
    
    if p := st.chat_input("Bericht..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op()
        st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    w_dict = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if not w_dict:
        st.info("Download een lijst in de klas om te oefenen.")
    else:
        # Simpele oefen-omgeving
        woord = random.choice(list(w_dict.keys()))
        st.subheader(f"Vertaal: {woord}")
        antwoord = st.text_input("Antwoord")
        if st.button("Check"):
            if antwoord.lower().strip() == w_dict[woord].lower().strip():
                st.success("Correct! +50 munten")
                st.session_state.db['saldi'][mijn_naam] += 50
                sla_db_op()
            else: st.error(f"Fout! Het was: {w_dict[woord]}")

elif nav == "👩‍🏫 Leraar":
    st.title("👩‍🏫 Leraar Paneel")
    tab1, tab2, tab3 = st.tabs(["Codes", "Taken", "Lijsten"])
    with tab1:
        st.write(st.session_state.db['klascodes'])
        c_code = st.text_input("Nieuwe Code")
        c_klas = st.text_input("Klas Naam")
        if st.button("Voeg code toe"):
            st.session_state.db['klascodes'][c_code] = c_klas
            sla_db_op()
            st.rerun()
    with tab2:
        t_t = st.text_input("Titel")
        t_d = st.text_area("Uitleg")
        if st.button("Post Taak"):
            st.session_state.db['tasks'].append({"title": t_t, "desc": t_d})
            sla_db_op()
    with tab3:
        l_t = st.text_input("Lijst Naam")
        l_w = st.text_area("nl=fr (per regel)")
        if st.button("Post Lijst"):
            d = {line.split("=")[0].strip(): line.split("=")[1].strip() for line in l_w.split("\n") if "=" in line}
            st.session_state.db['vocab_lists'].append({"title": l_t, "words": d})
            sla_db_op()

elif nav == "👑 Admin":
    st.title("👑 Elliot's Dashboard")
    
    t_eco, t_lock, t_raw = st.tabs(["💰 Economie", "🚨 Lockdown", "⚙️ Database RAW"])
    
    with t_eco:
        target = st.selectbox("Wie?", list(st.session_state.db['users'].keys()))
        aantal = st.number_input("Aantal Munten", value=100)
        if st.button("Geef Munten"):
            st.session_state.db['saldi'][target] = st.session_state.db['saldi'].get(target, 0) + aantal
            sla_db_op()
            st.success("Gedaan!")

    with t_lock:
        st.toggle("LOCKDOWN ACTIEF", key="lock_toggle", value=st.session_state.db['lockdown'])
        msg = st.text_input("Bericht", value=st.session_state.db['lockdown_msg'])
        if st.button("Sla Lockdown Status Op"):
            st.session_state.db['lockdown'] = st.session_state.lock_toggle
            st.session_state.db['lockdown_msg'] = msg
            sla_db_op()
            st.rerun()

    with t_raw:
        st.warning("Let op: Foute JSON = Crash")
        raw_txt = st.text_area("Database Edit", value=json.dumps(st.session_state.db, indent=4), height=400)
        if st.button("Overschrijf Database"):
            try:
                st.session_state.db = json.loads(raw_txt)
                sla_db_op()
                st.success("Database vernieuwd!")
                st.rerun()
            except: st.error("JSON Fout!")

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.info("Koppel je API key in de secrets om dit te gebruiken.")
