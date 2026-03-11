import streamlit as st
import random
from openai import OpenAI

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v2.7"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# De "Coole" achtergrond
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
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'active_task' not in st.session_state: st.session_state.active_task = None
if 'saldi' not in st.session_state: st.session_state.saldi = {}
if 'class_code' not in st.session_state: st.session_state.class_code = "1234"
if 'frans_woord_nu' not in st.session_state: st.session_state.frans_woord_nu = "hallo"

frans_dict = {"hallo": "bonjour", "bedankt": "merci", "school": "école", "boek": "livre", "brood": "pain"}

# --- AI FUNCTIE ---
def vraag_groq(vraag, systeem_prompt="Je bent een leraar."):
    if st.session_state.active_task:
        return "⚠️ **AI BLOKKADE:** Je bent bezig aan een taak! Maak deze eerst af."
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": systeem_prompt}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

# --- LOGIN SCHERM ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    tab1, tab2 = st.tabs(["🚀 Inloggen", "📝 Registreren"])
    
    with tab1:
        u = st.text_input("Gebruikersnaam", key="login_user").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="login_pw")
        if st.button("Log in", key="login_btn"):
            if u in st.session_state.users:
                u_data = st.session_state.users[u]
                correct_pw = u_data["pw"] if isinstance(u_data, dict) else u_data
                if correct_pw == p:
                    st.session_state.ingelogd = True
                    st.session_state.username = u
                    st.session_state.role = u_data.get("role", "teacher") if u in ["elliot", "annelies"] else "student"
                    st.rerun()
                else: st.error("Wachtwoord onjuist.")
            else: st.error("Gebruiker niet gevonden.")
        
        with st.expander("🛠️ Systeemherstel"):
            rc = st.text_input("Reset code", type="password", key="reset_code")
            if st.button("Hard Reset", key="reset_btn"):
                if rc == "Putsie":
                    st.session_state.users = {
                        "elliot": {"pw": "Putsie", "role": "teacher"},
                        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
                    }
                    st.session_state.tasks = []
                    st.session_state.class_code = "1234"
                    st.rerun()

    with tab2:
        nu = st.text_input("Kies een Naam", key="reg_user").lower().strip()
        np = st.text_input("Kies een Wachtwoord", type="password", key="reg_pw")
        code_input = st.text_input("Klascode (Vraag aan de juf/meester)", key="reg_code")
        if st.button("Account Aanmaken", key="reg_btn"):
            if code_input == st.session_state.class_code:
                if nu and np and nu not in st.session_state.users:
                    st.session_state.users[nu] = {"pw": np, "role": "student"}
                    st.session_state.saldi[nu] = 0
                    st.success("Gelukt! Je kunt nu inloggen.")
                else: st.error("Naam bezet of leeg.")
            else: st.error("Klascode onjuist! Kijk in 'De Klas' bij een ingelogde leerling.")
    st.stop()

# --- INTERFACE ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
st.sidebar.info(f"Klascode: **{st.session_state.class_code}**") # Zichtbaar in de zijbalk
opts = ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role == "teacher": opts.append("🛠️ Admin Paneel")
nav = st.sidebar.radio("Navigatie", opts)

# --- DE KLAS ---
if nav == "🏫 De Klas":
    st.title("🏫 De Klas")
    
    # Klascode display
    st.success(f"### 🔑 De huidige klascode is: `{st.session_state.class_code}`")
    st.write("Deel deze code met klasgenoten zodat ze zich kunnen registreren.")

    if st.session_state.role == "teacher":
        st.divider()
        st.subheader("👨‍🏫 Instellingen voor Leerkrachten")
        new_code = st.text_input("Verander de klascode:", value=st.session_state.class_code)
        if st.button("Update Code"):
            st.session_state.class_code = new_code
            st.success(f"Code veranderd naar: {new_code}")
            st.rerun()

        st.subheader("Taak Toevoegen")
        t_n = st.text_input("Naam van taak")
        t_i = st.text_area("Wat moeten ze doen?")
        if st.button("Verstuur naar Klas"):
            st.session_state.tasks.append({"name": t_n, "content": t_i})
            st.success("Taak geplaatst!")
    
    st.divider()
    st.subheader("Beschikbare Taken")
    if not st.session_state.tasks: st.write("Geen taken momenteel.")
    for i, t in enumerate(st.session_state.tasks):
        if st.button(f"Start: {t['name']}", key=f"task_{i}"):
            st.session_state.active_task = t
            st.rerun()

    if st.session_state.active_task:
        st.error(f"📍 BEZIG MET TAAK: {st.session_state.active_task['name']}")
        st.info(st.session_state.active_task['content'])
        if st.button("Klaar! (Lever in)", key="finish_task"):
            st.session_state.active_task = None
            st.success("Taak ingediend!")
            st.rerun()

# --- AI HULP ---
elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    vraag = st.text_area("Stel je vraag over school:")
    if st.button("Vraag het"):
        with st.spinner("AI denkt na..."):
            st.write(vraag_groq(vraag))

# --- FRANS LAB ---
elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    if st.button("Nieuw Woord", key="new_fr"):
        st.session_state.frans_woord_nu = random.choice(list(frans_dict.keys()))
        st.rerun()
    
    st.subheader(f"Vertaal: **{st.session_state.frans_woord_nu}**")
    p_ans = st.text_input("Jouw vertaling:", key="ans_fr").lower().strip()
    if st.button("Check", key="check_fr"):
        if p_ans == frans_dict[st.session_state.frans_woord_nu]:
            st.success("Helemaal goed! +5 munten.")
            st.session_state.saldi[st.session_state.username] = st.session_state.saldi.get(st.session_state.username, 0) + 5
        else:
            st.error(f"Helaas! Het was: {frans_dict[st.session_state.frans_woord_nu]}")

# --- ADMIN ---
elif nav == "🛠️ Admin Paneel":
    st.title("🛠️ Beheer")
    for speler in list(st.session_state.users.keys()):
        if st.session_state.users[speler].get("role") != "teacher":
            col1, col2, col3 = st.columns(3)
            col1.write(f"👤 {speler}")
            col2.write(f"💰 {st.session_state.saldi.get(speler, 0)}")
            if col3.button(f"Verwijder {speler}", key=f"del_{speler}"):
                del st.session_state.users[speler]
                st.rerun()

if st.sidebar.button("Uitloggen", key="logout"):
    st.session_state.ingelogd = False
    st.rerun()
