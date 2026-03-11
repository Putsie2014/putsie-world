import streamlit as st
import random
from datetime import datetime, timedelta
from openai import OpenAI
import streamlit.components.v1 as components

# --- 1. CONFIGURATIE ---
COOLDOWN_SECONDS = 60 
AI_PUNT_PRIJS = 1000
SITE_TITLE = "Putsie EDUCATION 🎓 v4.2 MASTER"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DATABASE INITIALISATIE ---
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
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'klascodes' not in st.session_state: st.session_state.klascodes = {"Putsie2024": "Klas 1A"}

# --- 3. LOCKDOWN SYSTEEM ---
is_admin = st.session_state.get('username') == "elliot"

if st.session_state.lockdown and not is_admin:
    st.markdown(f"""
        <div style="text-align:center; margin-top:15%;">
            <h1 style="color:red; font-size:50px;">🚫 LOCKDOWN ACTIEF</h1>
            <h2 style="color:white;">{st.session_state.lockdown_msg}</h2>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- 4. LOGIN & REGISTRATIE ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    t1, t2 = st.tabs(["Inloggen", "Nieuw Account"])
    
    with t1:
        u_in = st.text_input("Naam", key="login_u").lower().strip()
        p_in = st.text_input("Wachtwoord", type="password", key="login_p")
        if st.button("Log in", key="btn_login"):
            if u_in in st.session_state.users and st.session_state.users[u_in]["pw"] == p_in:
                st.session_state.ingelogd = True
                st.session_state.username = u_in
                st.session_state.role = st.session_state.users[u_in]["role"]
                st.rerun()
            else: st.error("Inloggegevens onjuist.")
            
    with t2:
        nu = st.text_input("Nieuwe Naam", key="reg_u").lower().strip()
        np = st.text_input("Wachtwoord ", type="password", key="reg_p")
        kc = st.text_input("Klascode", key="reg_kc")
        if st.button("Registreer", key="btn_reg"):
            if kc in st.session_state.klascodes:
                if nu and nu not in st.session_state.users:
                    st.session_state.users[nu] = {"pw": np, "role": "student"}
                    st.session_state.saldi[nu] = 0
                    st.session_state.user_vocab[nu] = {}
                    st.success("Account aangemaakt! Je kunt nu inloggen.")
                else: st.error("Naam is leeg of bestaat al.")
            else: st.error("Klascode is niet geldig.")
    st.stop()

# --- 5. SIDEBAR ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
st.sidebar.metric("💰 Munten", st.session_state.saldi.get(st.session_state.username, 0))
st.sidebar.metric("💎 AI", st.session_state.ai_points)

menu = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role in ["teacher", "admin"]: menu.append("👩‍🏫 Leraar Paneel")
if is_admin: menu.append("👑 Admin")

nav = st.sidebar.radio("Navigatie", menu)

# --- 6. PAGINA'S ---

if nav == "🏫 De Klas":
    st.title("🏫 Klaslokaal")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📝 Taken")
        if not st.session_state.tasks: st.info("Geen taken.")
        for i, t in enumerate(st.session_state.tasks):
            st.info(f"**{t['title']}**: {t['desc']}")
    with c2:
        st.subheader("📚 Woordenlijsten")
        if not st.session_state.vocab_lists: st.info("Geen lijsten beschikbaar.")
        for i, v in enumerate(st.session_state.vocab_lists):
            if st.button(f"📥 Download {v['title']}", key=f"dl_v_{i}"):
                if st.session_state.username not in st.session_state.user_vocab:
                    st.session_state.user_vocab[st.session_state.username] = {}
                st.session_state.user_vocab[st.session_state.username].update(v['words'])
                st.success("Woorden toegevoegd!")

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    chat_container = st.container(height=500)
    with chat_container:
        for m in st.session_state.chat_messages:
            with st.chat_message("user"):
                st.write(f"**{m['user']}**: {m['text']}")

    if prompt := st.chat_input("Schrijf een bericht..."):
        st.session_state.chat_messages.append({"user": st.session_state.username, "text": prompt})
        st.rerun()

elif nav == "👑 Admin":
    st.title("👑 Admin Control")
    lock_msg = st.text_input("Bericht voor lockdown", value=st.session_state.lockdown_msg)
    if st.button("🔒 Toggle Lockdown"):
        st.session_state.lockdown = not st.session_state.lockdown
        st.session_state.lockdown_msg = lock_msg
        st.rerun()
    
    st.divider()
    st.subheader("Klascodes")
    code_in = st.text_input("Nieuwe code")
    klas_in = st.text_input("Naam klas")
    if st.button("Voeg Code Toe"):
        st.session_state.klascodes[code_in] = klas_in
        st.success("Opgeslagen!")

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    st.write("Vertaal woorden om munten te verdienen.")
    if st.button("Snel oefenen (+50 munten)", key="quick_coin"):
        st.session_state.saldi[st.session_state.username] += 50
        st.rerun()

# --- 7. UITLOGGEN (UNIEKE KEY FIX) ---
st.sidebar.divider()
if st.sidebar.button("Uitloggen", key="sidebar_logout_btn"):
    st.session_state.ingelogd = False
    st.rerun()
