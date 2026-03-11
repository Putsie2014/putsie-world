import streamlit as st
import random
from openai import OpenAI

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v2.5"
MODEL_NAAM = "llama-3.1-8b-instant"

# Custom CSS voor de coole achtergrond
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
    # Elliot en Annelies zijn de leerkrachten
    st.session_state.users = {
        "elliot": {"pw": "Putsie", "role": "teacher"},
        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
    }
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'class_code' not in st.session_state: st.session_state.class_code = "1234"
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'active_task' not in st.session_state: st.session_state.active_task = None
if 'saldi' not in st.session_state: st.session_state.saldi = {}

# --- AI FUNCTIE (Met Slot) ---
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
            if u in st.session_state.users and st.session_state.users[u]["pw"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.session_state.role = st.session_state.users[u]["role"]
                st.rerun()
            else: st.error("Onjuiste gegevens.")

        with st.expander("🛠️ Systeembeheer"):
            reset_code = st.text_input("Reset code:", type="password")
            if st.button("RESET DATABASE"):
                if reset_code == "Putsie":
                    st.session_state.users = {
                        "elliot": {"pw": "Putsie", "role": "teacher"},
                        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
                    }
                    st.session_state.tasks = []
                    st.success("Database hersteld naar fabrieksinstellingen!")
                    st.rerun()

    with tab2:
        nu = st.text_input("Nieuwe Leerling Naam").lower().strip()
        np = st.text_input("Nieuw Wachtwoord", type="password")
        if st.button("Account aanmaken"):
            if nu and np and nu not in st.session_state.users:
                st.session_state.users[nu] = {"pw": np, "role": "student"}
                st.session_state.saldi[nu] = 0
                st.success("Geregistreerd! Log nu in bij het eerste tabblad.")
    st.stop()

# --- ZIJBALK NAVIGATIE ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
menu_options = ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role == "teacher": menu_options.append("🛠️ Admin / Beheer")
nav = st.sidebar.radio("Ga naar:", menu_options)

# --- PAGINA: DE KLAS ---
if nav == "🏫 De Klas":
    st.title("🏫 De Klas")
    
    if st.session_state.role == "teacher":
        st.subheader("👨‍🏫 Leerkracht Paneel")
        new_task_name = st.text_input("Naam van de nieuwe taak (bijv. Woordjes Frans):")
        new_task_content = st.text_area("Woordjes (NL - FR, één per regel):", "Hond - Chien\nKat - Chat")
        
        if st.button("📢 Taak Uitdelen"):
            st.session_state.tasks.append({"name": new_task_name, "content": new_task_content})
            st.success("Taak staat klaar voor de leerlingen!")
            
        st.write(f"Huidige Klascode: **{st.session_state.class_code}**")

    else:
        st.subheader("✍️ Beschikbare Taken")
        if not st.session_state.tasks:
            st.write("Er staan momenteel geen taken voor je klaar.")
        else:
            for i, task in enumerate(st.session_state.tasks):
                st.write(f"📌 {task['name']}")
                if st.button(f"Start Taak: {task['name']}", key=f"btn_{i}"):
                    st.session_state.active_task = task
                    st.rerun()

    if st.session_state.active_task:
        st.warning("⚠️ JE MAAKT NU EEN TAAK. DE AI IS UITGESCHAKELD.")
        st.info(f"Opgave:\n{st.session_state.active_task['content']}")
        if st.button("Taak Inleveren"):
            st.session_state.active_task = None
            st.success("Taak ingeleverd! AI is weer beschikbaar.")
            st.rerun()

# --- PAGINA: AI HULP ---
elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    if st.session_state.active_task:
        st.error("Je kunt de AI niet gebruiken tijdens een taak!")
    else:
        v = st.text_area("Stel je vraag:")
        if st.button("Vraag het de AI"):
            st.write(vraag_groq(v))

# --- PAGINA: ADMIN ---
elif nav == "🛠️ Admin / Beheer" and st.session_state.role == "teacher":
    st.title("🛠️ Beheer")
    st.subheader("💰 Saldo & Spelers")
    for user, data in st.session_state.users.items():
        if data["role"] == "student":
            col1, col2 = st.columns(2)
            saldo = st.session_state.saldi.get(user, 0)
            col1.write(f"👤 {user.capitalize()} (Saldo: {saldo})")
            if col2.button(f"Geef 10 Munten aan {user}"):
                st.session_state.saldi[user] = saldo + 10
                st.rerun()

# --- UITLOGGEN ---
if st.sidebar.button("Log uit"):
    st.session_state.ingelogd = False
    st.session_state.active_task = None
    st.rerun()
