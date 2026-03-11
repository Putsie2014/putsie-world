import streamlit as st
import random
from openai import OpenAI
import streamlit.components.v1 as components

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v3.0"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# UI Styling
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0f172a; color: white; }
.stButton>button { width: 100%; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- AI CLIENT ---
client = OpenAI(api_key=st.secrets["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")

# --- INITIALISATIE ---
if 'users' not in st.session_state:
    st.session_state.users = {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}}
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'active_task' not in st.session_state: st.session_state.active_task = None
if 'ai_points' not in st.session_state: st.session_state.ai_points = 5
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 1000}
if 'class_code' not in st.session_state: st.session_state.class_code = "1234"
if 'class_name' not in st.session_state: st.session_state.class_name = "Putsie's Klas"

# --- AI FUNCTIE ---
def vraag_groq(vraag):
    if st.session_state.active_task:
        return "⚠️ **AI BLOKKADE:** Je bent bezig aan een taak! Maak deze eerst af."
    if st.session_state.ai_points <= 0:
        return "❌ **Geen punten meer!**"
    
    st.session_state.ai_points -= 1
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": "Je bent een leraar."}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

# --- LOGIN SCHERM ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    u = st.text_input("Gebruikersnaam", key="u").lower().strip()
    p = st.text_input("Wachtwoord", type="password", key="p")
    if st.button("Log in"):
        if u in st.session_state.users and st.session_state.users[u]["pw"] == p:
            st.session_state.ingelogd = True
            st.session_state.username = u
            st.session_state.role = st.session_state.users[u].get("role", "student")
            st.rerun()
        else: st.error("Foutieve gegevens.")
    st.stop()

# --- INTERFACE ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
st.sidebar.info(f"AI Punten: **{st.session_state.ai_points}** 💎")
nav = st.sidebar.radio("Navigatie", ["🏫 De Klas", "🤖 AI Hulp", "🎮 3D Doolhof"] + 
                       (["📚 Leraar Paneel"] if st.session_state.role in ["teacher", "admin"] else []) +
                       (["👑 Super Admin"] if st.session_state.username == "elliot" else []))

# --- PAGINA'S ---
if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.write(f"Je hebt nog **{st.session_state.ai_points}** punten over.")
    vraag = st.text_area("Stel je vraag:")
    if st.button("Verstuur vraag"):
        st.write(vraag_groq(vraag))
        st.rerun()

elif nav == "🎮 3D Doolhof":
    st.title("🎮 3D Doolhof")
    st.write("Gebruik WASD om te bewegen.")
    # (Je 3D Doolhof code hier)

elif nav == "👑 Super Admin":
    st.title("👑 Super Admin")
    if st.button("Punten resetten"):
        st.session_state.ai_points = 100
        st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
