import streamlit as st
import random
from openai import OpenAI
import streamlit.components.v1 as components

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v3.1"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# UI Styling
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    color: white;
}
.stMetric {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 10px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# --- AI CLIENT ---
client = OpenAI(api_key=st.secrets["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")

# --- INITIALISATIE DATABASE (FORCEER PUNTEN & GELD) ---
if 'users' not in st.session_state:
    st.session_state.users = {
        "elliot": {"pw": "Putsie", "role": "admin"},
        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
    }
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 1000, "annelies": 500}
if 'ai_points' not in st.session_state: st.session_state.ai_points = 5
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'class_code' not in st.session_state: st.session_state.class_code = "1234"
if 'class_name' not in st.session_state: st.session_state.class_name = "Putsie's Klas"

# --- LOGIN & REGISTRATIE ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    t1, t2 = st.tabs(["Inloggen", "Registreren"])
    with t1:
        u = st.text_input("Gebruikersnaam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Log in"):
            if u in st.session_state.users and st.session_state.users[u]["pw"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.session_state.role = st.session_state.users[u].get("role", "student")
                st.rerun()
            else: st.error("Inloggegevens kloppen niet.")
    with t2:
        nu = st.text_input("Naam", key="r_u").lower().strip()
        np = st.text_input("Wachtwoord", type="password", key="r_p")
        cc = st.text_input("Klascode", key="r_c")
        if st.button("Account maken"):
            if cc == st.session_state.class_code:
                if nu and np and nu not in st.session_state.users:
                    st.session_state.users[nu] = {"pw": np, "role": "student"}
                    st.session_state.saldi[nu] = 0 # Startgeld
                    st.success("Klaar! Log nu in bij het eerste tabblad.")
                else: st.error("Naam bezet of leeg.")
            else: st.error("Code fout.")
    st.stop()

# --- HET DASHBOARD (Altijd bovenaan zichtbaar) ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
current_money = st.session_state.saldi.get(st.session_state.username, 0)

# Visuele balk bovenaan
col_a, col_b, col_c = st.columns(3)
col_a.metric("💰 Munten", f"{current_money}")
col_b.metric("💎 AI Punten", f"{st.session_state.ai_points}")
col_c.metric("🏫 Klas", st.session_state.class_name)
st.divider()

# --- NAVIGATIE ---
menu = ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab", "🎮 3D Doolhof"]
if st.session_state.role in ["teacher", "admin"]: menu.append("📚 Leraar Paneel")
if st.session_state.username == "elliot": menu.append("👑 Super Admin")
nav = st.sidebar.radio("Navigatie", menu)

# --- PAGINA LOGICA ---
if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    if st.session_state.ai_points > 0:
        vraag = st.text_area("Stel je vraag:")
        if st.button("Stel vraag (-1 punt)"):
            st.session_state.ai_points -= 1
            with st.spinner("AI denkt..."):
                # Simpele placeholder voor API call
                st.write("De AI zegt: Succes met je huiswerk!") 
                st.rerun()
    else:
        st.error("Je punten zijn op!")
    
    st.divider()
    if st.button("▶️ Bekijk advertentie (+3 punten)"):
        st.session_state.ai_points += 3
        st.success("Punten toegevoegd!")
        st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    st.write("Verdien hier munten door woorden te vertalen!")
    if st.button("Oefen woord (+10 munten test)"):
        st.session_state.saldi[st.session_state.username] += 10
        st.rerun()

elif nav == "🎮 3D Doolhof":
    st.title("🎮 3D Maze")
    maze_code = """<div style="width:100%;height:400px;background:black;color:green;display:flex;align-items:center;justify-content:center;">3D ENGINE LOADING... (WASD READY)</div>"""
    components.html(maze_code, height=450)

elif nav == "👑 Super Admin":
    st.title("👑 Admin")
    for speler in list(st.session_state.users.keys()):
        if speler != "elliot":
            val = st.number_input(f"Saldo {speler}", value=st.session_state.saldi.get(speler, 0), key=f"edit_{speler}")
            st.session_state.saldi[speler] = val
    if st.button("Update alles"): st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
    <meta name="google-adsense-account" content="ca-pub-8729817167190879">
