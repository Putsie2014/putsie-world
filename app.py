import streamlit as st
import random
from datetime import datetime, timedelta
from openai import OpenAI
import streamlit.components.v1 as components

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v3.3"
MODEL_NAAM = "llama-3.1-8b-instant"
AI_PUNT_PRIJS = 1000
COOLDOWN_SECONDS = 60 

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- INITIALISATIE ---
if 'users' not in st.session_state:
    st.session_state.users = {"elliot": {"pw": "Putsie", "role": "admin"}}
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 10000}
if 'ai_points' not in st.session_state: st.session_state.ai_points = 5
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'lockdown' not in st.session_state: st.session_state.lockdown = False
if 'lockdown_until' not in st.session_state: st.session_state.lockdown_until = None
if 'security_alert' not in st.session_state: st.session_state.security_alert = False
if 'ai_antwoord' not in st.session_state: st.session_state.ai_antwoord = "" # HET GEHEUGEN

# --- LOCKDOWN CHECK ---
if st.session_state.lockdown:
    st.markdown(f"<h1 style='text-align: center; margin-top: 20%; color: red;'>we zijn zo terug: Putsie Studios</h1>", unsafe_allow_html=True)
    if st.session_state.get('username') == "elliot":
        if st.button("🔓 Elliot: Unlock Site"): 
            st.session_state.lockdown = False
            st.rerun()
    st.stop()

# --- SECURITY SYSTEEM ---
if st.session_state.get('username') == "elliot" and st.session_state.security_alert:
    st.error("🚨 SECURITY DETECTED: Onbevoegde wijziging gemerkt!")
    c1, c2 = st.columns(2)
    if c1.button("NEGEER"): st.session_state.security_alert = False; st.rerun()
    if c2.button("LOCKDOWN"): st.session_state.lockdown = True; st.session_state.security_alert = False; st.rerun()

# --- AI CLIENT ---
client = OpenAI(api_key=st.secrets["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")

def vraag_groq(vraag):
    u = st.session_state.username
    nu = datetime.now()
    
    # Cooldown check
    if u in st.session_state.last_ai_call:
        verstreken = (nu - st.session_state.last_ai_call[u]).total_seconds()
        if verstreken < COOLDOWN_SECONDS:
            return f"⏳ Wacht {int(COOLDOWN_SECONDS - verstreken)} seconden."

    if st.session_state.ai_points <= 0: return "❌ Geen AI Punten meer!"
    
    st.session_state.ai_points -= 1
    st.session_state.last_ai_call[u] = nu
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": "Je bent een leraar."}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"Fout: {e}"

# --- LOGIN ---
if not st.session_state.ingelogd:
    st.title("🔐 Inloggen bij Putsie")
    u = st.text_input("Naam").lower().strip()
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Log in"):
        if u in st.session_state.users and st.session_state.users[u]["pw"] == p:
            st.session_state.ingelogd = True
            st.session_state.username = u
            st.rerun()
    st.stop()

# --- SIDEBAR & NAVIGATIE ---
st.sidebar.title(f"👋 {st.session_state.username}")
st.sidebar.metric("💰 Munten", st.session_state.saldi.get(st.session_state.username, 0))
st.sidebar.metric("💎 AI Punten", st.session_state.ai_points)

menu = ["🤖 AI Hulp", "🇫🇷 Frans Lab", "🎮 3D Doolhof"]
if st.session_state.username == "elliot": menu.append("👑 Admin")
nav = st.sidebar.radio("Ga naar", menu)

# --- PAGINA: AI HULP ---
if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.info(f"Cooldown: {COOLDOWN_SECONDS} sec | Kosten: 1 punt")
    
    vraag = st.text_area("Wat wil je weten?")
    if st.button("Stel vraag"):
        with st.spinner("AI denkt na..."):
            antwoord = vraag_groq(vraag)
            st.session_state.ai_antwoord = antwoord # Sla het antwoord op!
            st.rerun() # Ververs om punten/cooldown bij te werken

    # Laat het opgeslagen antwoord ALTIJD zien
    if st.session_state.ai_antwoord:
        st.chat_message("assistant").write(st.session_state.ai_antwoord)

    st.divider()
    if st.button(f"Koop 1 AI Punt ({AI_PUNT_PRIJS} munten)"):
        if st.session_state.saldi[st.session_state.username] >= AI_PUNT_PRIJS:
            st.session_state.saldi[st.session_state.username] -= AI_PUNT_PRIJS
            st.session_state.ai_points += 1
            st.session_state.ai_antwoord = "Punt gekocht! Stel je vraag."
            st.rerun()
        else: st.error("Te weinig munten!")

# --- PAGINA: ADMIN ---
elif nav == "👑 Admin":
    st.title("Control Room")
    if st.button("🚨 TEST SECURITY BREACH"):
        st.session_state.security_alert = True
        st.rerun()
    
    minuten = st.slider("Lockdown duur (min)", 1, 60, 10)
    if st.button("🔒 START LOCKDOWN"):
        st.session_state.lockdown = True
        st.session_state.lockdown_until = datetime.now() + timedelta(minutes=minuten)
        st.rerun()

# --- FRANS LAB ---
elif nav == "🇫🇷 Frans Lab":
    st.title("Frans Lab")
    if st.button("Oefen woord (+50 munten)"):
        st.session_state.saldi[st.session_state.username] += 50
        st.success("Verdiend!")
        st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
