import streamlit as st
import random
from openai import OpenAI

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v2.5"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- AI CLIENT ---
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# --- INITIALISATIE DATABASE ---
if 'users' not in st.session_state:
    st.session_state.users = {
        "elliot": {"pw": "Putsie", "role": "teacher"},
        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
    }
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'class_code' not in st.session_state: st.session_state.class_code = "1234"
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'active_task' not in st.session_state: st.session_state.active_task = None
if 'saldi' not in st.session_state: st.session_state.saldi = {}
if 'frans_woorden' not in st.session_state:
    st.session_state.frans_woorden = {"hallo": "bonjour", "bedankt": "merci", "school": "école"}

# --- AI FUNCTIE ---
def vraag_groq(vraag, systeem_prompt="Je bent een behulpzame leraar."):
    if st.session_state.active_task:
        return "⚠️ **AI GEBLOKKEERD:** Je bent momenteel bezig aan een taak. Maak je werk eerst af!"
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": systeem_prompt}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- LOGIN SCHERM ---
if not st.session_state.ingelogd:
    st.title(f"🔐 Login - {SITE_TITLE}")
    tab1, tab2 = st.tabs(["🚀 Inloggen", "📝 Registreren"])
    with tab1:
        u = st.text_input("Naam").lower().strip()
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Login"):
            if u in st.session_state.users:
                user_data = st.session_state.users[u]
                wachtwoord = user_data["pw"] if isinstance(user_data, dict) else user_data
                if wachtwoord == p:
                    st.session_state.ingelogd = True
                    st.session_state.username = u
                    st.session_state.role = user_data.get("role", "student") if isinstance(user_data, dict) else "student"
                    st.rerun()
                else: st.error("Fout wachtwoord.")
            else: st.error("Gebruiker niet gevonden.")
        
        with st.expander("🛠️ Systeembeheer"):
            reset_code = st.text_input("Reset code:", type="password")
            if st.button("RESET DATABASE"):
                if reset_code == "Putsie":
                    st.session_state.users = {"elliot": {"pw": "Putsie", "role": "teacher"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}}
                    st.session_state.tasks = []
                    st.rerun()
    with tab2:
        nu = st.text_input("Nieuwe Naam").lower().strip()
        np = st.text_input("Wachtwoord", type="password")
        if st.button("Registreren"):
            if nu and np and nu not in st.session_state.users:
                st.session_state.users[nu] = {"pw": np, "role": "student"}
                st.session_state.saldi[nu] = 0
                st.success("Account gemaakt!")
    st.stop()

# --- HOOFD MENU ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
menu = ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role == "teacher": menu.append("🛠️ Admin Paneel")
nav = st.sidebar.radio("Menu:", menu)

# --- PAGINA'S ---
if nav == "🏫 De Klas":
    st.title("🏫 De Klas")
    if st.session_state.role == "teacher":
        st.subheader("👨‍🏫 Taak Beheer")
        t_naam = st.text_input("Taak naam")
        t_inhoud = st.text_area("Opgave")
        if st.button("📢 Taak Uitdelen"):
            st.session_state.tasks.append({"name": t_naam, "content": t_inhoud})
    else:
        for i, task in enumerate(st.session_state.tasks):
            if st.button(f"Start Taak: {task['name']}"):
                st.session_state.active_task = task
                st.rerun()
        if st.session_state.active_task:
            st.warning(f"⚠️ TAAK: {st.session_state.active_task['content']}")
            if st.button("Taak Inleveren"):
                st.session_state.active_task = None
                st.rerun()

elif nav == "🤖 AI Hulp":
    v = st.text_area("Vraag aan de AI:")
    if st.button("Verstuur"):
        st.write(vraag_groq(v))

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    w = random.choice(list(st.session_state.frans_woorden.keys()))
    st.write(f"Vertaal: {w}")
    ans = st.text_input("Antwoord:")
    if st.button("Controleer"):
        st.write("Correct!" if ans == st.session_state.frans_woorden[w] else "Fout.")

elif nav == "🛠️ Admin Paneel":
    st.title("🛠️ Admin")
    for u in st.session_state.users:
        if u != "elliot" and u != "annelies":
            if st.button(f"Verwijder {u}"):
                del st.session_state.users[u]
                st.rerun()

if st.sidebar.button("Log uit"):
    st.session_state.ingelogd = False
    st.rerun()
