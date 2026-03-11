import streamlit as st
import random
from openai import OpenAI

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v2.0"
MODEL_NAAM = "llama-3.1-8b-instant"

# Custom CSS voor de "coole achtergrond" (Dark mode gradient style)
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
    color: white;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
</style>
"""

st.set_page_config(page_title=SITE_TITLE, layout="wide")
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- AI CLIENT INITIALISATIE ---
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# --- DATABASE IN SESSION STATE (Veilig voor Cloud) ---
if 'users' not in st.session_state:
    st.session_state.users = {"elliot": "admin"} 
if 'ingelogd' not in st.session_state:
    st.session_state.ingelogd = False
    st.session_state.username = ""

# --- FRANS LAB WOORDEN DATABASE ---
if 'frans_woorden' not in st.session_state:
    st.session_state.frans_woorden = {
        "hallo": "bonjour",
        "bedankt": "merci",
        "school": "école",
        "boek": "livre",
        "auto": "voiture",
        "altijd": "toujours",
        "vandaag": "aujourd'hui"
    }
if 'huidig_woord' not in st.session_state:
    st.session_state.huidig_woord = random.choice(list(st.session_state.frans_woorden.keys()))

# --- AI FUNCTIE ---
def vraag_groq(vraag, systeem_prompt="Je bent een behulpzame leraar. Geef hints, geen directe antwoorden."):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[
                {"role": "system", "content": systeem_prompt},
                {"role": "user", "content": vraag}
            ]
        )
        return response.choices[0].message.content
    except Exception as e: 
        return f"Oeps, AI error: {e}"

# --- INLOGGEN & REGISTREREN ---
if not st.session_state.ingelogd:
    st.title(f"Welkom bij {SITE_TITLE}")
    
    tab1, tab2 = st.tabs(["🚀 Inloggen", "📝 Registreren"])
    
    with tab1:
        u = st.text_input("Naam").lower().strip()
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.rerun()
            else: 
                st.error("Foute naam of wachtwoord!")
                
    with tab2:
        nu = st.text_input("Nieuwe Naam").lower().strip()
        np = st.text_input("Nieuw Wachtwoord", type="password")
        if st.button("Account Aanmaken"):
            if nu in st.session_state.users:
                st.error("Deze gebruiker bestaat al!")
            elif nu and np:
                st.session_state.users[nu] = np
                st.success("Account gemaakt! Je kunt nu inloggen.")
            else:
                st.warning("Vul beide velden in.")
    st.stop()

# --- HOOFD MENU ZIJBALK ---
st.sidebar.title(f"Welkom, {st.session_state.username.capitalize()}! 👑")
nav = st.sidebar.radio("Menu", ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab"])

# --- PAGINA: DE KLAS ---
if nav == "🏫 De Klas":
    st.title("🏫 De Klas")
    st.write("Welkom in de digitale klas! Hier zie je wie er allemaal meedoen.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👥 Huidige Accounts")
        for user in st.session_state.users.keys():
            if user == st.session_state.username:
                st.write(f"- 🟢 **{user.capitalize()}** (Jij)")
            else:
                st.write(f"- 👤 {user.capitalize()}")
    
    with col2:
        st.subheader("📌 Mededelingen")
        st.info("Welkom bij de nieuwe versie! Het Frans Lab is geüpdatet met AI-hulp en een ingebouwde overhoring.")

# --- PAGINA: ALGEMENE AI HULP ---
elif nav == "🤖 AI Hulp":
    st.title("🤖 Algemene AI Hulp")
    st.write("Stel hier je vragen over andere vakken.")
    v = st.text_area("Vraag aan de leraar:")
    if st.button("Verstuur Vraag"):
        with st.spinner("De AI denkt na..."):
            st.write(vraag_groq(v))

# --- PAGINA: FRANS LAB ---
elif nav == "🇫🇷 Frans Lab":
    st.title("🥐 Frans Lab: Woordjes Trainer")
    st.write("Oefen je woordjes. Kom je er niet uit? Vraag de AI om een ezelsbruggetje!")
    
    st.divider()
    
    # Woordjes overhoring
    st.subheader(f"Vertaal naar het Frans: **{st.session_state.huidig_woord}**")
    
    antwoord = st.text_input("Jouw antwoord:", key="frans_input").lower().strip()
    juiste_vertaling = st.session_state.frans_woorden[st.session_state.huidig_woord]
    
    colA, colB, colC = st.columns(3)
    
    with colA:
        if st.button("Controleer"):
            if antwoord == juiste_vertaling:
                st.success("Correct! 🎉")
            else:
                st.error(f"Fout! Het juiste antwoord was: **{juiste_vertaling}**")
                
    with colB:
        if st.button("Volgend Woord ⏭️"):
            # Kies een nieuw willekeurig woord en herlaad de pagina
            st.session_state.huidig_woord = random.choice(list(st.session_state.frans_woorden.keys()))
            st.rerun()
            
    with colC:
        if st.button("🤖 Geef me een ezelsbruggetje"):
            prompt = f"De leerling moet het Franse woord '{juiste_vertaling}' leren voor het Nederlandse woord '{st.session_state.huidig_woord}'. Geef een grappig of handig ezelsbruggetje om dit te onthouden. Houd het heel kort."
            with st.spinner("Ezelsbruggetje verzinnen..."):
                ezelsbruggetje = vraag_groq("Help me", systeem_prompt=prompt)
                st.info(ezelsbruggetje)

    st.divider()
    st.write("Wil je zelf woordjes toevoegen? (Admin only in de toekomst!)")

# --- UITLOGGEN ---
st.sidebar.markdown("---")
if st.sidebar.button("Log uit"):
    st.session_state.ingelogd = False
    st.session_state.username = ""
    st.rerun()
# --- ADMIN PANEEL (Toevoegen in de HOOFD MENU ZIJBALK sectie) ---
if st.session_state.username == "elliot": # Alleen voor admin
    nav = st.sidebar.radio("Menu", ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab", "🛠️ Admin Paneel"])
else:
    nav = st.sidebar.radio("Menu", ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab"])

# --- PAGINA: ADMIN PANEEL ---
if nav == "🛠️ Admin Paneel":
    st.title("🛠️ Admin Paneel")
    
    # 1. Gebruikers beheren
    st.subheader("👤 Spelers Beheren")
    user_to_delete = st.selectbox("Selecteer speler om te verwijderen:", list(st.session_state.users.keys()))
    if st.button("Verwijder Speler"):
        if user_to_delete != "elliot":
            del st.session_state.users[user_to_delete]
            st.rerun()
        else:
            st.error("Je kunt de admin niet verwijderen!")

    # 2. Saldo aanpassen
    st.subheader("💰 Saldo Aanpassen")
    user_to_edit = st.selectbox("Selecteer speler voor saldo:", list(st.session_state.users.keys()))
    amount = st.number_input("Bedrag wijzigen (bijv. 50 of -50):", value=0)
    if st.button("Saldo Bijwerken"):
        # We moeten saldo in session_state bijhouden
        if 'saldi' not in st.session_state: st.session_state.saldi = {u: 100 for u in st.session_state.users}
        st.session_state.saldi[user_to_edit] += amount
        st.success(f"Nieuw saldo voor {user_to_edit}: {st.session_state.saldi[user_to_edit]}")

    # 3. Database inzien (simpel overzicht)
    st.subheader("📊 Database Inzicht")
    st.write(st.session_state.users)
