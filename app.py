import streamlit as st
import random
import time
from datetime import datetime, timedelta
from openai import OpenAI
import streamlit.components.v1 as components

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v3.2 PRO"
MODEL_NAAM = "llama-3.1-8b-instant"
AI_PUNT_PRIJS = 1000
COOLDOWN_SECONDS = 60 # 1 minuut wachten tussen vragen

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- INITIALISATIE DATABASE ---
if 'users' not in st.session_state:
    st.session_state.users = {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}}
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 10000}
if 'ai_points' not in st.session_state: st.session_state.ai_points = 5
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'lockdown' not in st.session_state: st.session_state.lockdown = False
if 'lockdown_until' not in st.session_state: st.session_state.lockdown_until = None
if 'security_alert' not in st.session_state: st.session_state.security_alert = False

# --- LOCKDOWN CHECK ---
if st.session_state.lockdown:
    if st.session_state.lockdown_until and datetime.now() > st.session_state.lockdown_until:
        st.session_state.lockdown = False
    else:
        st.markdown(f"<h1 style='text-align: center; margin-top: 20%;'>we zijn zo terug: Putsie Studios</h1>", unsafe_allow_html=True)
        if st.session_state.username == "elliot": # Elliot kan altijd deblokkeren
            if st.button("Unlock Site"): 
                st.session_state.lockdown = False
                st.rerun()
        st.stop()

# --- SECURITY ALERT SYSTEM ---
if st.session_state.username == "elliot" and st.session_state.security_alert:
    st.warning("⚠️ SECURITY DETECTED: Er is een onbekende wijziging in de app-structuur opgemerkt!")
    col_s1, col_s2 = st.columns(2)
    if col_s1.button("NEGEER"): st.session_state.security_alert = False; st.rerun()
    if col_s2.button("LOCKDOWN NU"): 
        st.session_state.lockdown = True
        st.session_state.security_alert = False
        st.rerun()

# --- AI CLIENT ---
client = OpenAI(api_key=st.secrets["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")

# --- AI FUNCTIE MET COOLDOWN & KOSTEN ---
def vraag_groq(vraag):
    u = st.session_state.username
    nu = datetime.now()
    
    # Cooldown Check
    if u in st.session_state.last_ai_call:
        verstreken = (nu - st.session_state.last_ai_call[u]).total_seconds()
        if verstreken < COOLDOWN_SECONDS:
            return f"⏳ **Wacht even!** Je kunt pas over {int(COOLDOWN_SECONDS - verstreken)} seconden weer een vraag stellen."

    if st.session_state.ai_points <= 0:
        return "❌ **Geen AI Punten.** Koop punten met munten in het menu."
    
    st.session_state.ai_points -= 1
    st.session_state.last_ai_call[u] = nu
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": "Je bent een leraar."}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

# --- LOGIN --- (Gekopieerd uit v3.1 voor stabiliteit)
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    u = st.text_input("Naam").lower().strip()
    p = st.text_input("Wachtwoord", type="password")
    if st.button("Log in"):
        if u in st.session_state.users and st.session_state.users[u]["pw"] == p:
            st.session_state.ingelogd = True
            st.session_state.username = u
            st.session_state.role = st.session_state.users[u].get("role", "student")
            st.rerun()
    st.stop()

# --- INTERFACE ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
st.sidebar.metric("💰 Munten", st.session_state.saldi.get(st.session_state.username, 0))
st.sidebar.metric("💎 AI Punten", st.session_state.ai_points)

menu = ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab", "🎮 3D Doolhof"]
if st.session_state.role in ["teacher", "admin"]: menu.append("📚 Leraar Paneel")
if st.session_state.username == "elliot": menu.append("👑 Super Admin")
nav = st.sidebar.radio("Menu", menu)

# --- PAGINA: AI HULP ---
if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.write("Vragen kosten 1 AI punt. Je kunt punten kopen voor 1000 munten.")
    
    vraag = st.text_area("Stel je vraag:")
    if st.button("Stel vraag (-1 punt)"):
        st.write(vraag_groq(vraag))
        st.rerun()
    
    st.divider()
    st.subheader("Winkel")
    if st.button(f"Koop 1 AI Punt (Cost: {AI_PUNT_PRIJS} munten)"):
        if st.session_state.saldi[st.session_state.username] >= AI_PUNT_PRIJS:
            st.session_state.saldi[st.session_state.username] -= AI_PUNT_PRIJS
            st.session_state.ai_points += 1
            st.success("Punt gekocht!")
            st.rerun()
        else: st.error("Niet genoeg munten!")

# --- PAGINA: SUPER ADMIN ---
elif nav == "👑 Super Admin":
    st.title("👑 Elliot's Control Room")
    
    st.subheader("🚀 Lockdown Systeem")
    duur = st.number_input("Lockdown duur (minuten)", min_value=1, value=10)
    if st.button("ACTIVEER LOCKDOWN"):
        st.session_state.lockdown = True
        st.session_state.lockdown_until = datetime.now() + timedelta(minutes=duur)
        st.rerun()

    st.divider()
    st.subheader("🛡️ Beveiliging Test")
    if st.button("Simuleer Security Breach"):
        st.session_state.security_alert = True
        st.rerun()
    
    st.divider()
    st.write("Spelerslijst:")
    st.json(st.session_state.saldi)

# --- REST VAN DE PAGINA'S (FRANS LAB ETC) ---
elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    st.write("Verdien hier munten voor AI punten!")
    if st.button("Oefen (+10 munten)"):
        st.session_state.saldi[st.session_state.username] += 10
        st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
