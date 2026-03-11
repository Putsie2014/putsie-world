import streamlit as st
import random
from openai import OpenAI
import streamlit.components.v1 as components

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v3.1 FULL"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# UI Styling
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0f172a; color: white; }
.stMetric { background-color: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 10px; }
.stButton>button { width: 100%; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- AI CLIENT ---
client = OpenAI(api_key=st.secrets["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")

# --- INITIALISATIE DATABASE ---
if 'users' not in st.session_state:
    st.session_state.users = {
        "elliot": {"pw": "Putsie", "role": "admin"},
        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
    }
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 1000}
if 'ai_points' not in st.session_state: st.session_state.ai_points = 5
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'active_task' not in st.session_state: st.session_state.active_task = None
if 'class_code' not in st.session_state: st.session_state.class_code = "1234"
if 'class_name' not in st.session_state: st.session_state.class_name = "Putsie's Klas"
if 'frans_woord_nu' not in st.session_state: st.session_state.frans_woord_nu = "hallo"

frans_dict = {"hallo": "bonjour", "bedankt": "merci", "school": "école", "boek": "livre", "brood": "pain", "hond": "chien"}

# --- AI FUNCTIE ---
def vraag_groq(vraag):
    if st.session_state.active_task:
        return "⚠️ **AI BLOKKADE:** Je bent bezig aan een taak! Maak deze eerst af."
    if st.session_state.ai_points <= 0:
        return "❌ **Geen punten meer!** Verdien punten in het AI menu."
    
    st.session_state.ai_points -= 1
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": "Je bent een leraar."}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

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
            else: st.error("Fout!")
    with t2:
        nu = st.text_input("Nieuwe Naam", key="r_u")
        np = st.text_input("Nieuw Wachtwoord", type="password", key="r_p")
        cc = st.text_input("Klascode", key="r_c")
        if st.button("Maak Account"):
            if cc == st.session_state.class_code and nu not in st.session_state.users:
                st.session_state.users[nu] = {"pw": np, "role": "student"}
                st.session_state.saldi[nu] = 0
                st.success("Account aangemaakt!")
    st.stop()

# --- DASHBOARD STATS ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
c1, c2 = st.columns(2)
c1.metric("💰 Munten", st.session_state.saldi.get(st.session_state.username, 0))
c2.metric("💎 AI Punten", st.session_state.ai_points)

# --- NAVIGATIE ---
menu = ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab", "🎮 3D Doolhof"]
if st.session_state.role in ["teacher", "admin"]: menu.append("📚 Leraar Paneel")
if st.session_state.username == "elliot": menu.append("👑 Super Admin")
nav = st.sidebar.radio("Menu", menu)

# --- PAGINA'S ---
if nav == "🏫 De Klas":
    st.title(f"🏫 {st.session_state.class_name}")
    st.write(f"Klascode: **{st.session_state.class_code}**")
    st.subheader("Jouw Taken")
    if not st.session_state.tasks: st.info("Geen taken voor vandaag!")
    for i, t in enumerate(st.session_state.tasks):
        if st.button(f"Start: {t['name']}", key=f"btn_{i}"):
            st.session_state.active_task = t
            st.rerun()
    if st.session_state.active_task:
        st.warning(f"BEZIG: {st.session_state.active_task['name']}")
        if st.button("Klaar! Inleveren"):
            st.session_state.active_task = None
            st.success("Goed gedaan!")
            st.rerun()

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    vraag = st.text_area("Stel je vraag:")
    if st.button("Vraag het (-1 punt)"):
        st.write(vraag_groq(vraag))
        st.rerun()
    st.divider()
    if st.button("🎁 Verdien 3 AI punten (Extra oefening)"):
        st.session_state.ai_points += 3
        st.success("Punten toegevoegd!")
        st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    st.subheader(f"Vertaal: **{st.session_state.frans_woord_nu}**")
    ans = st.text_input("Franse vertaling:").lower().strip()
    if st.button("Check"):
        if ans == frans_dict.get(st.session_state.frans_woord_nu):
            st.success("Correct! +10 munten")
            st.session_state.saldi[st.session_state.username] += 10
            st.session_state.frans_woord_nu = random.choice(list(frans_dict.keys()))
            st.rerun()
        else: st.error("Helaas, probeer het nog eens.")

elif nav == "🎮 3D Doolhof":
    st.title("🎮 3D Doolhof")
    components.html("""<div style="width:100%;height:300px;background:grey;color:white;text-align:center;padding-top:100px;">3D ENGINE ACTIEF (WASD)</div>""", height=350)

elif nav == "📚 Leraar Paneel":
    st.title("📚 Taken Uitdelen")
    tn = st.text_input("Taak naam")
    tc = st.text_area("Beschrijving")
    if st.button("Stuur naar klas"):
        st.session_state.tasks.append({"name": tn, "content": tc})
        st.success("Verstuurd!")

elif nav == "👑 Super Admin":
    st.title("👑 Elliot's Control")
    st.json(st.session_state.users)
    speler = st.selectbox("Kies speler", list(st.session_state.saldi.keys()))
    nieuw_geld = st.number_input("Nieuw Saldo", value=st.session_state.saldi[speler])
    if st.button("Update Saldo"):
        st.session_state.saldi[speler] = nieuw_geld
        st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
