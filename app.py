import streamlit as st
import random
from datetime import datetime, timedelta
from openai import OpenAI
import streamlit.components.v1 as components

# --- 1. CONFIGURATIE (ALTIJD BOVENAAN) ---
COOLDOWN_SECONDS = 60 
AI_PUNT_PRIJS = 1000
SITE_TITLE = "Putsie EDUCATION 🎓 v4.0"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DATABASE INITIALISATIE (DE "ALT-TAB" BEVEILIGING) ---
# We checken elk object individueel zodat er nooit een AttributeError komt
if 'users' not in st.session_state:
    st.session_state.users = {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}}
if 'saldi' not in st.session_state:
    st.session_state.saldi = {"elliot": 10000, "annelies": 1000}
if 'user_vocab' not in st.session_state:
    st.session_state.user_vocab = {"elliot": {"hallo": "bonjour"}, "annelies": {"hallo": "bonjour"}}
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'vocab_lists' not in st.session_state:
    st.session_state.vocab_lists = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'ai_points' not in st.session_state:
    st.session_state.ai_points = 5
if 'ingelogd' not in st.session_state:
    st.session_state.ingelogd = False
if 'ai_antwoord' not in st.session_state:
    st.session_state.ai_antwoord = ""
if 'lockdown' not in st.session_state:
    st.session_state.lockdown = False
if 'security_alert' not in st.session_state:
    st.session_state.security_alert = False
if 'last_ai_call' not in st.session_state:
    st.session_state.last_ai_call = {}

# --- 3. AI FUNCTIE ---
client = OpenAI(api_key=st.secrets.get("GROQ_API_KEY", "dummy"), base_url="https://api.groq.com/openai/v1")

def vraag_groq(vraag):
    u = st.session_state.username
    nu = datetime.now()
    if u in st.session_state.last_ai_call:
        verstreken = (nu - st.session_state.last_ai_call[u]).total_seconds()
        if verstreken < COOLDOWN_SECONDS:
            return f"⏳ Wacht nog {int(COOLDOWN_SECONDS - verstreken)} seconden."
    
    if st.session_state.ai_points <= 0:
        return "❌ Je hebt geen AI punten meer."
        
    st.session_state.ai_points -= 1
    st.session_state.last_ai_call[u] = nu
    try:
        resp = client.chat.completions.create(model=MODEL_NAAM, messages=[{"role":"user","content":vraag}])
        return resp.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

# --- 4. LOCKDOWN CHECK ---
is_admin = st.session_state.get('username') == "elliot"
if st.session_state.lockdown and not is_admin:
    st.markdown("<h1 style='text-align:center;margin-top:20%;color:red;'>we zijn zo terug: Putsie Studios</h1>", unsafe_allow_html=True)
    st.stop()

# --- 5. LOGIN ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    t1, t2 = st.tabs(["Inloggen", "Registreren"])
    with t1:
        u_in = st.text_input("Naam", key="login_naam").lower().strip()
        p_in = st.text_input("Wachtwoord", type="password", key="login_pw")
        if st.button("Log in"):
            if u_in in st.session_state.users and st.session_state.users[u_in]["pw"] == p_in:
                st.session_state.ingelogd = True
                st.session_state.username = u_in
                st.session_state.role = st.session_state.users[u_in]["role"]
                if u_in not in st.session_state.user_vocab: st.session_state.user_vocab[u_in] = {"hallo":"bonjour"}
                st.rerun()
            else: st.error("Inloggegevens onjuist.")
    with t2:
        nu_in = st.text_input("Nieuwe Naam", key="reg_naam").lower().strip()
        np_in = st.text_input("Nieuw Wachtwoord", type="password", key="reg_pw")
        if st.button("Account maken"):
            if nu_in and nu_in not in st.session_state.users:
                st.session_state.users[nu_in] = {"pw":np_in, "role":"student"}
                st.session_state.saldi[nu_in] = 0
                st.session_state.user_vocab[nu_in] = {"hallo":"bonjour"}
                st.success("Account aangemaakt! Je kunt nu inloggen.")
    st.stop()

# --- 6. NAVIGATIE ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
st.sidebar.metric("💰 Munten", st.session_state.saldi.get(st.session_state.username, 0))
st.sidebar.metric("💎 AI Punten", st.session_state.ai_points)

menu_options = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role in ["teacher", "admin"]: menu_options.append("👩‍🏫 Leraar Paneel")
if is_admin: menu_options.append("👑 Admin")
nav = st.sidebar.radio("Ga naar:", menu_options)

# --- 7. PAGINA'S ---

if nav == "🏫 De Klas":
    st.title("🏫 Klaslokaal")
    # FIX: Hier maken we de kolommen aan binnen het Klas-blok
    col_links, col_rechts = st.columns(2) 
    
    with col_links:
        st.subheader("📝 Openstaande Taken")
        if not st.session_state.tasks:
            st.info("Lekker bezig! Geen huiswerk.")
        for i, task in enumerate(st.session_state.tasks):
            with st.expander(task['title']):
                st.write(task['desc'])
                if st.button("Klaar!", key=f"task_{i}"): st.balloons()

    with col_rechts:
        st.subheader("📚 Woordenlijsten")
        if not st.session_state.vocab_lists:
            st.info("De leraar heeft nog geen lijsten gepost.")
        for i, v_list in enumerate(st.session_state.vocab_lists):
            st.write(f"📂 **{v_list['title']}**")
            if st.button(f"Download {v_list['title']}", key=f"dl_{i}"):
                st.session_state.user_vocab[st.session_state.username].update(v_list['words'])
                st.success("Woorden toegevoegd aan je Lab!")

elif nav == "💬 Chat":
    st.title("💬 Groepschat")
    for msg in st.session_state.chat_messages:
        with st.chat_message("user"):
            st.write(f"**{msg['user']}**: {msg['text']}")
    
    if prompt := st.chat_input("Typ je bericht..."):
        st.session_state.chat_messages.append({"user": st.session_state.username, "text": prompt})
        st.rerun()

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.warning(f"Kosten: 1 punt per vraag | Cooldown: {COOLDOWN_SECONDS}s")
    vraag_input = st.text_area("Stel je vraag aan de AI:")
    if st.button("Verstuur Vraag"):
        with st.spinner("AI denkt na..."):
            st.session_state.ai_antwoord = vraag_groq(vraag_input)
            st.rerun()
    if st.session_state.ai_antwoord:
        st.chat_message("assistant").write(st.session_state.ai_antwoord)
    
    st.divider()
    if st.button(f"Koop 1 AI Punt ({AI_PUNT_PRIJS} munten)"):
        if st.session_state.saldi[st.session_state.username] >= AI_PUNT_PRIJS:
            st.session_state.saldi[st.session_state.username] -= AI_PUNT_PRIJS
            st.session_state.ai_points += 1
            st.rerun()
        else: st.error("Te weinig munten!")

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    mijn_w = st.session_state.user_vocab.get(st.session_state.username, {})
    tab_oefen, tab_maak = st.tabs(["Oefenen", "Eigen Woorden"])
    
    with tab_oefen:
        if mijn_w:
            # We kiezen een random woord en slaan het op in session_state
            if 'current_word' not in st.session_state:
                st.session_state.current_word = random.choice(list(mijn_w.keys()))
            
            st.subheader(f"Vertaal: {st.session_state.current_word}")
            gok = st.text_input("Antwoord:")
            if st.button("Check"):
                if gok.lower().strip() == mijn_w[st.session_state.current_word].lower().strip():
                    st.success("Goedzo! +50 Munten!")
                    st.session_state.saldi[st.session_state.username] += 50
                    st.session_state.current_word = random.choice(list(mijn_w.keys()))
                    st.rerun()
                else: st.error("Niet goed, probeer opnieuw!")
        else: st.warning("Voeg eerst woorden toe!")

    with tab_maak:
        n_nl = st.text_input("Nederlands")
        n_fr = st.text_input("Frans")
        if st.button("Opslaan in mijn lijst"):
            if n_nl and n_fr:
                st.session_state.user_vocab[st.session_state.username][n_nl] = n_fr
                st.success("Opgeslagen!")
                st.rerun()

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Docenten Dashboard")
    st.subheader("Post een Woordenlijst")
    titel = st.text_input("Naam van de lijst")
    inhoud = st.text_area("Formaat: nl=fr (bijv: hond=chien), elke op nieuwe regel")
    if st.button("Deel met Klas"):
        d = {}
        for r in inhoud.split("\n"):
            if "=" in r:
                k, v = r.split("=")
                d[k.strip()] = v.strip()
        st.session_state.vocab_lists.append({"title": titel, "words": d})
        st.success("Lijst gepost!")

elif nav == "👑 Admin":
    st.title("👑 Elliot's Control Room")
    if st.button("🚨 TOGGLE LOCKDOWN"):
        st.session_state.lockdown = not st.session_state.lockdown
        st.rerun()
    if st.button("SIMULEER SECURITY ALERT"):
        st.session_state.security_alert = True
        st.rerun()
    if st.session_state.security_alert:
        st.error("SECURITY DETECTED!")
        if st.button("NEGEER"): st.session_state.security_alert = False; st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
