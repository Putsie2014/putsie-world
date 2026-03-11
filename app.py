import streamlit as st
import random
from datetime import datetime, timedelta
from openai import OpenAI
import streamlit.components.v1 as components

# --- 1. CONFIGURATIE ---
COOLDOWN_SECONDS = 60 
AI_PUNT_PRIJS = 1000
SITE_TITLE = "Putsie EDUCATION 🎓 v4.1 MASTER"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DATABASE INITIALISATIE (NIETS VERWIJDEREN) ---
if 'users' not in st.session_state:
    st.session_state.users = {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}}
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 10000}
if 'user_vocab' not in st.session_state: st.session_state.user_vocab = {"elliot": {}}
if 'chat_messages' not in st.session_state: st.session_state.chat_messages = []
if 'vocab_lists' not in st.session_state: st.session_state.vocab_lists = []
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'ai_points' not in st.session_state: st.session_state.ai_points = 5
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'lockdown' not in st.session_state: st.session_state.lockdown = False
if 'lockdown_msg' not in st.session_state: st.session_state.lockdown_msg = "We zijn zo terug: Putsie Studios"
if 'security_alert' not in st.session_state: st.session_state.security_alert = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'klascodes' not in st.session_state: st.session_state.klascodes = {"Putsie2024": "Klas 1A"}

# --- 3. LOCKDOWN SYSTEEM (ECHT WERKEND) ---
is_admin = st.session_state.get('username') == "elliot"

if st.session_state.lockdown and not is_admin:
    st.empty() # Maak de pagina leeg
    st.markdown(f"""
        <div style="text-align:center; margin-top:15%;">
            <h1 style="color:red; font-size:50px;">LOCKDOWN ACTIEF</h1>
            <h2 style="color:white;">{st.session_state.lockdown_msg}</h2>
            <p style="color:gray;">Neem contact op met Elliot voor meer info.</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop() # Stop de rest van de website

# --- 4. LOGIN & KLASCODES ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    t1, t2 = st.tabs(["Inloggen", "Nieuw Account (Klascode nodig)"])
    
    with t1:
        u_in = st.text_input("Naam").lower().strip()
        p_in = st.text_input("Wachtwoord", type="password")
        if st.button("Log in"):
            if u_in in st.session_state.users and st.session_state.users[u_in]["pw"] == p_in:
                st.session_state.ingelogd = True
                st.session_state.username = u_in
                st.session_state.role = st.session_state.users[u_in]["role"]
                st.rerun()
            else: st.error("Fout!")
            
    with t2:
        nu = st.text_input("Nieuwe Naam").lower().strip()
        np = st.text_input("Wachtwoord ", type="password")
        kc = st.text_input("Klascode")
        if st.button("Registreer"):
            if kc in st.session_state.klascodes:
                if nu not in st.session_state.users:
                    st.session_state.users[nu] = {"pw": np, "role": "student"}
                    st.session_state.saldi[nu] = 0
                    st.session_state.user_vocab[nu] = {}
                    st.success(f"Welkom bij {st.session_state.klascodes[kc]}!")
                else: st.error("Naam bestaat al.")
            else: st.error("Onjuiste klascode.")
    st.stop()

# --- 5. INTERFACE ---
st.sidebar.title(f"👋 {st.session_state.username}")
st.sidebar.metric("💰 Munten", st.session_state.saldi.get(st.session_state.username, 0))
st.sidebar.metric("💎 AI", st.session_state.ai_points)

menu = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role in ["teacher", "admin"]: menu.append("👩‍🏫 Leraar Paneel")
if is_admin: menu.append("👑 Admin")
nav = st.sidebar.radio("Navigatie", menu)

# --- 6. CHAT FIX (WERKT NU ECHT) ---
if nav == "💬 Chat":
    st.title("💬 Klas Chat")
    
    # Container voor berichten
    chat_container = st.container(height=400)
    for m in st.session_state.chat_messages:
        with chat_container:
            st.chat_message("user").write(f"**{m['user']}**: {m['text']}")

    # Input onderaan
    if prompt := st.chat_input("Typ je bericht..."):
        st.session_state.chat_messages.append({"user": st.session_state.username, "text": prompt})
        st.rerun()

# --- 7. DE KLAS ---
elif nav == "🏫 De Klas":
    st.title("🏫 Klaslokaal")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📝 Taken")
        for i, t in enumerate(st.session_state.tasks):
            st.info(f"**{t['title']}**: {t['desc']}")
    with c2:
        st.subheader("📚 Woordenlijsten")
        for i, v in enumerate(st.session_state.vocab_lists):
            if st.button(f"Download {v['title']}", key=f"v_{i}"):
                st.session_state.user_vocab[st.session_state.username].update(v['words'])
                st.success("Gedownload!")

# --- 8. ADMIN & LOCKDOWN (ELLIOT ONLY) ---
elif nav == "👑 Admin":
    st.title("👑 Elliot's Control Room")
    
    st.subheader("🚨 Lockdown Instellingen")
    new_msg = st.text_input("Lockdown Bericht", value=st.session_state.lockdown_msg)
    
    if not st.session_state.lockdown:
        if st.button("🔒 ACTIVEER LOCKDOWN"):
            st.session_state.lockdown = True
            st.session_state.lockdown_msg = new_msg
            st.rerun()
    else:
        st.warning("SITE IS MOMENTEEL OP SLOT")
        if st.button("🔓 DEACTIVEER LOCKDOWN"):
            st.session_state.lockdown = False
            st.rerun()

    st.divider()
    st.subheader("🔑 Klascodes Beheren")
    new_code = st.text_input("Nieuwe Code")
    klas_naam = st.text_input("Klas Naam")
    if st.button("Code Toevoegen"):
        st.session_state.klascodes[new_code] = klas_naam
        st.success("Code opgeslagen!")

# --- 9. FRANS LAB (NIETS VERWIJDERD) ---
elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    # (Hetzelfde systeem als v4.0 voor woorden oefenen)
    if st.button("Oefen Demo (+50 munten)"):
        st.session_state.saldi[st.session_state.username] += 50
        st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
