import streamlit as st
import random
from datetime import datetime
from openai import OpenAI

# --- 1. CONFIGURATIE ---
COOLDOWN_SECONDS = 60 
AI_PUNT_PRIJS = 1000
SITE_TITLE = "Putsie EDUCATION 🎓 v4.3 REPAIRED"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DATABASE INITIALISATIE ---
def init_all():
    defaults = {
        'users': {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}},
        'saldi': {"elliot": 10000},
        'user_vocab': {"elliot": {"hallo": "bonjour"}},
        'chat_messages': [],
        'vocab_lists': [],
        'tasks': [],
        'ai_points': 5,
        'ingelogd': False,
        'lockdown': False,
        'lockdown_msg': "Systeem onderhoud door Elliot",
        'last_ai_call': {},
        'klascodes': {"Putsie2024": "Klas 1A"},
        'ai_antwoord_temp': "",
        'huidig_oefenwoord': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_all()

# --- 3. AI MOTOR (VERBETERD) ---
def roep_ai(vraag):
    u = st.session_state.username
    nu = datetime.now()
    
    # Check cooldown
    if u in st.session_state.last_ai_call:
        if (nu - st.session_state.last_ai_call[u]).total_seconds() < COOLDOWN_SECONDS:
            return "⏳ Geduld! De AI leraar rust even uit (cooldown)."

    if st.session_state.ai_points <= 0:
        return "❌ Je hebt geen AI punten meer. Koop ze in de winkel!"

    # API Check
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "⚠️ Configuratie fout: Geen API-sleutel gevonden in st.secrets."

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    
    try:
        st.session_state.ai_points -= 1
        st.session_state.last_ai_call[u] = nu
        completion = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": "Je bent een behulpzame leraar."}, {"role": "user", "content": vraag}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- 4. LOCKDOWN & LOGIN ---
is_admin = st.session_state.get('username') == "elliot"

if st.session_state.lockdown and not is_admin:
    st.error(f"🚫 {st.session_state.lockdown_msg}")
    st.stop()

if not st.session_state.ingelogd:
    st.title("🎓 Putsie Login")
    tab1, tab2 = st.tabs(["Inloggen", "Registreren"])
    with tab1:
        u = st.text_input("Naam").lower().strip()
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Log in", key="login_main"):
            if u in st.session_state.users and st.session_state.users[u]["pw"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.session_state.role = st.session_state.users[u]["role"]
                st.rerun()
    st.stop()

# --- 5. SIDEBAR & NAVIGATIE ---
st.sidebar.title(f"👤 {st.session_state.username}")
st.sidebar.info(f"💰 {st.session_state.saldi.get(st.session_state.username, 0)} munten\n\n💎 {st.session_state.ai_points} AI punten")

menu = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if is_admin: menu.append("👑 Admin")
nav = st.sidebar.radio("Navigatie", menu)

# --- 6. CHAT (FIXED) ---
if nav == "💬 Chat":
    st.title("💬 Klas Chat")
    chat_box = st.container(height=400, border=True)
    with chat_box:
        for m in st.session_state.chat_messages:
            st.markdown(f"**{m['user']}**: {m['text']}")

    if p := st.chat_input("Typ je bericht..."):
        st.session_state.chat_messages.append({"user": st.session_state.username, "text": p})
        st.rerun()

# --- 7. FRANS LAB (FIXED) ---
elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    
    # Zorg dat de gebruiker een lijst heeft
    if st.session_state.username not in st.session_state.user_vocab:
        st.session_state.user_vocab[st.session_state.username] = {"hallo": "bonjour"}
    
    woorden = st.session_state.user_vocab[st.session_state.username]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎮 Oefenen")
        if woorden:
            if not st.session_state.huidig_oefenwoord:
                st.session_state.huidig_oefenwoord = random.choice(list(woorden.keys()))
            
            vraag = st.session_state.huidig_oefenwoord
            st.write(f"Wat is de vertaling van: **{vraag}**?")
            antwoord = st.text_input("Jouw antwoord:", key="frans_ans").lower().strip()
            
            if st.button("Controleer"):
                if antwoord == woorden[vraag].lower().strip():
                    st.success("Correct! +50 munten.")
                    st.session_state.saldi[st.session_state.username] += 50
                    st.session_state.huidig_oefenwoord = random.choice(list(woorden.keys()))
                    st.rerun()
                else:
                    st.error("Helaas, probeer het nog eens.")
        else:
            st.info("Je hebt nog geen woorden in je lijst.")

    with col2:
        st.subheader("➕ Woorden Toevoegen")
        nl = st.text_input("Nederlands:")
        fr = st.text_input("Frans:")
        if st.button("Voeg toe"):
            if nl and fr:
                st.session_state.user_vocab[st.session_state.username][nl] = fr
                st.success(f"'{nl}' toegevoegd!")
                st.rerun()

# --- 8. AI HULP (FIXED) ---
elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    vraag = st.text_area("Stel je vraag aan de AI:")
    if st.button("Verstuur (Kost 1 AI punt)"):
        with st.spinner("AI leraar schrijft..."):
            st.session_state.ai_antwoord_temp = roep_ai(vraag)
            st.rerun()
    
    if st.session_state.ai_antwoord_temp:
        st.chat_message("assistant").write(st.session_state.ai_antwoord_temp)
    
    st.divider()
    if st.button(f"Koop 1 AI punt ({AI_PUNT_PRIJS} munten)"):
        saldo = st.session_state.saldi.get(st.session_state.username, 0)
        if saldo >= AI_PUNT_PRIJS:
            st.session_state.saldi[st.session_state.username] -= AI_PUNT_PRIJS
            st.session_state.ai_points += 1
            st.success("Punt gekocht!")
            st.rerun()
        else:
            st.error("Niet genoeg munten.")

# --- 9. ADMIN ---
elif nav == "👑 Admin":
    st.title("👑 Elliot Control")
    msg = st.text_input("Lockdown bericht:", value=st.session_state.lockdown_msg)
    if st.button("Toggle Lockdown"):
        st.session_state.lockdown = not st.session_state.lockdown
        st.session_state.lockdown_msg = msg
        st.rerun()
    
    st.divider()
    st.write("Gebruikers Saldi:", st.session_state.saldi)

# --- UITLOGGEN ---
if st.sidebar.button("Uitloggen", key="logout_final"):
    st.session_state.ingelogd = False
    st.rerun()
st.sidebar.divider()
if st.sidebar.button("Uitloggen", key="sidebar_logout_btn"):
    st.session_state.ingelogd = False
    st.rerun()
