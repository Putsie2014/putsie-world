import streamlit as st
import random
from datetime import datetime, timedelta
from openai import OpenAI
import streamlit.components.v1 as components

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v3.6 FIX"
MODEL_NAAM = "llama-3.1-8b-instant"
AI_PUNT_PRIJS = 1000
COOLDOWN_SECONDS = 60 

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 1. INITIALISATIE VAN DE DATABASE ---
if 'users' not in st.session_state:
    st.session_state.users = {
        "elliot": {"pw": "Putsie", "role": "admin"},
        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
    }
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 10000, "annelies": 1000}
if 'ai_points' not in st.session_state: st.session_state.ai_points = 5
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'lockdown' not in st.session_state: st.session_state.lockdown = False
if 'lockdown_until' not in st.session_state: st.session_state.lockdown_until = None
if 'security_alert' not in st.session_state: st.session_state.security_alert = False
if 'ai_antwoord' not in st.session_state: st.session_state.ai_antwoord = ""
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'chat_messages' not in st.session_state: st.session_state.chat_messages = []
if 'vocab_lists' not in st.session_state: st.session_state.vocab_lists = []
if 'user_vocab' not in st.session_state: 
    # Forceer een startlijst voor de standaard accounts
    st.session_state.user_vocab = {
        "elliot": {"hallo": "bonjour"}, 
        "annelies": {"hallo": "bonjour"}
    }

# --- 2. LOCKDOWN & SECURITY CHECK ---
is_admin = st.session_state.get('username') == "elliot"

if st.session_state.lockdown and not is_admin:
    st.markdown(f"<h1 style='text-align: center; margin-top: 20%; color: red;'>we zijn zo terug: Putsie Studios</h1>", unsafe_allow_html=True)
    st.stop()

if is_admin and st.session_state.security_alert:
    st.error("🚨 SECURITY DETECTED: Onbekende wijziging in de app-structuur opgemerkt!")
    c1, c2 = st.columns(2)
    if c1.button("NEGEER"): st.session_state.security_alert = False; st.rerun()
    if c2.button("LOCKDOWN NU"): 
        st.session_state.lockdown = True
        st.session_state.security_alert = False
        st.rerun()

# --- 3. AI CLIENT ---
client = OpenAI(api_key=st.secrets.get("GROQ_API_KEY", "dummy_key"), base_url="https://api.groq.com/openai/v1")

def vraag_groq(vraag):
    u = st.session_state.username
    nu = datetime.now()
    
    if u in st.session_state.last_ai_call:
        verstreken = (nu - st.session_state.last_ai_call[u]).total_seconds()
        if verstreken < COOLDOWN_SECONDS:
            return f"⏳ Wacht {int(COOLDOWN_SECONDS - verstreken)} seconden."

    if st.session_state.ai_points <= 0: return "❌ Geen AI Punten meer! Koop er in de winkel."
    
    st.session_state.ai_points -= 1
    st.session_state.last_ai_call[u] = nu
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": "Je bent een leraar."}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"AI Error: API key checken aub. ({e})"

# --- 4. LOGIN & REGISTRATIE ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    t1, t2 = st.tabs(["Inloggen", "Nieuw Account"])
    with t1:
        u = st.text_input("Naam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Log in"):
            if u in st.session_state.users and st.session_state.users[u]["pw"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.session_state.role = st.session_state.users[u].get("role", "student")
                # BUGFIX: Zorg dat elke inloggende speler een vocab-lijst krijgt als ze die missen
                if u not in st.session_state.user_vocab:
                    st.session_state.user_vocab[u] = {"hallo": "bonjour"}
                st.rerun()
            else: st.error("Foutieve gegevens!")
    with t2:
        nu = st.text_input("Kies een Naam", key="r_u").lower().strip()
        np = st.text_input("Kies een Wachtwoord", type="password", key="r_p")
        if st.button("Maak account"):
            if nu and nu not in st.session_state.users:
                st.session_state.users[nu] = {"pw": np, "role": "student"}
                st.session_state.saldi[nu] = 0
                st.session_state.user_vocab[nu] = {"hallo": "bonjour"}
                st.success("Account gemaakt! Log nu in.")
            else: st.error("Naam is leeg of bestaat al.")
    st.stop()

# --- 5. SIDEBAR & NAVIGATIE ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
st.sidebar.metric("💰 Munten", st.session_state.saldi.get(st.session_state.username, 0))
st.sidebar.metric("💎 AI Punten", st.session_state.ai_points)

menu = ["🏫 De Klas", "💬 Groepschat", "🤖 AI Hulp", "🇫🇷 Frans Lab", "🎮 3D Doolhof"]
if st.session_state.role in ["teacher", "admin"]: menu.append("👩‍🏫 Leraar Paneel")
if st.session_state.username == "elliot": menu.append("👑 Admin Security")
nav = st.sidebar.radio("Navigatie", menu)

# --- 6. PAGINA: DE KLAS ---
if nav == "🏫 De Klas":
    st.title("🏫 Het Klaslokaal")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Jouw Taken")
        if not st.session_state.tasks: st.info("Geen huiswerk vandaag!")
        for i, t in enumerate(st.session_state.tasks):
            with st.expander(t["title"]):
                st.write(t["desc"])
                if st.button("Markeer als Klaar", key=f"tk_{i}"): st.success("Ingeleverd!")
                
    with col2:
        st.subheader("📚 Woordenlijsten van de Leraar")
        if not st.session_state.vocab_lists: st.info("Geen nieuwe woordenlijsten.")
        for i, vlist in enumerate(st.session_state.vocab_lists):
            st.write(f"**{vlist['title']}** ({len(vlist['words'])} woorden)")
            if st.button("📥 Download naar mijn Frans Lab", key=f"dl_{i}"):
                # BUGFIX: Update de lijst veilig
                huidige_woorden = st.session_state.user_vocab[st.session_state.username]
                huidige_woorden.update(vlist['words'])
                st.session_state.user_vocab[st.session_state.username] = huidige_woorden
                st.success("Woorden toegevoegd aan jouw account!")

# --- 7. PAGINA: GROEPSCHAT ---
elif nav == "💬 Groepschat":
    st.title("💬 Putsie Chat")
    st.write("Praat met de klas! (Leerkrachten kijken mee 👀)")
    
    # BUGFIX: native Streamlit chat elementen gebruiken voor stabiliteit
    chat_container = st.container(height=400)
    with chat_container:
        if not st.session_state.chat_messages:
            st.info("Nog geen berichten. Wees de eerste!")
        for msg in st.session_state.chat_messages:
            st.chat_message("user" if msg['user'] == st.session_state.username else "assistant").write(f"**{msg['user']}**: {msg['text']}")
            
    if txt := st.chat_input("Typ je bericht hier..."):
        st.session_state.chat_messages.append({"user": st.session_state.username, "text": txt})
        st.rerun()

# --- 8. PAGINA: AI HULP ---
elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.warning(f"Cooldown: {COOLDOWN_SECONDS} sec | Kost: 1 AI Punt per vraag")
    
    vraag = st.text_area("Wat is je vraag?")
    if st.button("Vraag het aan AI"):
        with st.spinner("AI is aan het denken..."):
            antwoord = vraag_groq(vraag)
            st.session_state.ai_antwoord = antwoord
            st.rerun()

    if st.session_state.ai_antwoord:
        st.info("💡 Laatste AI Antwoord:")
        st.write(st.session_state.ai_antwoord)

    st.divider()
    st.subheader("🛒 AI Punten Winkel")
    if st.button(f"Koop 1 AI Punt ({AI_PUNT_PRIJS} munten)"):
        if st.session_state.saldi[st.session_state.username] >= AI_PUNT_PRIJS:
            st.session_state.saldi[st.session_state.username] -= AI_PUNT_PRIJS
            st.session_state.ai_points += 1
            st.success("Punt gekocht!")
            st.rerun()
        else: st.error("Je hebt niet genoeg munten! Ga werken in het Frans Lab.")

# --- 9. PAGINA: FRANS LAB ---
elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    
    # Zeker weten dat de lijst bestaat voor deze gebruiker (extra beveiliging)
    if st.session_state.username not in st.session_state.user_vocab:
        st.session_state.user_vocab[st.session_state.username] = {"hallo": "bonjour"}
        
    mijn_woorden = st.session_state.user_vocab[st.session_state.username]
    
    t1, t2 = st.tabs(["🎮 Oefenen (+50 Munten)", "➕ Eigen woorden maken"])
    
    with t1:
        st.write("Vertaal de woorden uit jouw persoonlijke woordenlijst om geld te verdienen!")
        if len(mijn_woorden) > 0:
            if 'oefen_woord' not in st.session_state or st.session_state.oefen_woord not in mijn_woorden: 
                st.session_state.oefen_woord = random.choice(list(mijn_woorden.keys()))
            
            st.subheader(f"Vertaal: **{st.session_state.oefen_woord}**")
            ans = st.text_input("Jouw antwoord (Frans):").lower().strip()
            if st.button("Controleer"):
                if ans == mijn_woorden[st.session_state.oefen_woord]:
                    st.success("Perfect! +50 Munten 💰")
                    st.session_state.saldi[st.session_state.username] += 50
                    st.session_state.oefen_woord = random.choice(list(mijn_woorden.keys()))
                    st.rerun()
                else: st.error("Fout! Probeer het nog eens.")
        else:
            st.warning("Je hebt nog geen woorden! Voeg er toe in de andere tab.")

    with t2:
        st.write("Maak je eigen woorden aan om te oefenen.")
        nieuw_nl = st.text_input("Nederlands woord:")
        nieuw_fr = st.text_input("Franse vertaling:").lower().strip()
        if st.button("Woord Opslaan"):
            if nieuw_nl and nieuw_fr:
                # BUGFIX: Duidelijk opslaan en rerunnen
                st.session_state.user_vocab[st.session_state.username][nieuw_nl.strip()] = nieuw_fr.strip()
                st.success(f"Opgeslagen: {nieuw_nl} = {nieuw_fr}")
                st.rerun()
            else: st.error("Vul beide velden in.")

# --- 10. PAGINA: LERAAR PANEEL ---
elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Docenten Dashboard")
    
    st.subheader("1. Woordenlijst Posten naar Klas")
    lijst_naam = st.text_input("Titel (bijv. Hoofdstuk 3)")
    woorden_ruw = st.text_area("Woorden (Formaat: nederlands=frans, elke op nieuwe regel)")
    if st.button("Post naar Klaslokaal"):
        woorden_dict = {}
        # BUGFIX: Veilig splitsen zodat lege regels de boel niet laten crashen
        for regel in woorden_ruw.split("\n"):
            if "=" in regel:
                nl, fr = regel.split("=", 1) # Max 1 keer splitsen
                if nl.strip() and fr.strip():
                    woorden_dict[nl.strip()] = fr.strip().lower()
                    
        if woorden_dict:
            st.session_state.vocab_lists.append({"title": lijst_naam, "words": woorden_dict})
            st.success(f"Lijst '{lijst_naam}' gedeeld met de klas!")
        else:
            st.error("Je hebt geen geldige woorden ingevuld.")
        
    st.divider()
    st.subheader("2. Leerlingen Beheren")
    for s_naam, s_data in st.session_state.users.items():
        if s_data['role'] == 'student':
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"**{s_naam}**")
            c2.write(f"Munten: {st.session_state.saldi.get(s_naam, 0)}")
            if c3.button("Reset Wachtwoord", key=f"pw_{s_naam}"):
                st.session_state.users[s_naam]['pw'] = "1234"
                st.success(f"Wachtwoord van {s_naam} is nu '1234'")

# --- 11. PAGINA: ADMIN SECURITY ---
elif nav == "👑 Admin Security":
    st.title("👑 Elliot's Control Room")
    
    st.subheader("🚨 Beveiliging & Lockdown")
    if st.button("TEST SECURITY BREACH"): st.session_state.security_alert = True; st.rerun()
    if st.button("LOCKDOWN AAN"): st.session_state.lockdown = True; st.rerun()
    if st.button("LOCKDOWN UIT"): st.session_state.lockdown = False; st.rerun()
    
    st.divider()
    st.subheader("💰 Bank Beheren")
    speler = st.selectbox("Kies Speler", list(st.session_state.saldi.keys()))
    bedrag = st.number_input("Zet saldo op", value=st.session_state.saldi[speler])
    if st.button("Update Saldo"):
        st.session_state.saldi[speler] = bedrag
        st.success("Aangepast!")
        st.rerun()

# --- 12. PAGINA: 3D DOOLHOF ---
elif nav == "🎮 3D Doolhof":
    st.title("🎮 3D Doolhof")
    components.html("""<div style="width:100%;height:400px;background:#222;color:#0f0;display:flex;align-items:center;justify-content:center;font-family:monospace;">[ THREE.JS ENGINE ACTIVE ]<br>Use WASD to move</div>""", height=450)

# --- UITLOGGEN ---
if st.sidebar.button("Uitloggen", type="primary"):
    st.session_state.ingelogd = False
    st.session_state.username = None
    st.rerun()
