import streamlit as st
import random
from datetime import datetime, timedelta
from openai import OpenAI
import streamlit.components.v1 as components

# --- 1. CONFIGURATIE ---
COOLDOWN_SECONDS = 60 
AI_PUNT_PRIJS = 1000
SITE_TITLE = "Putsie EDUCATION 🎓 v3.9 FINAL FIX"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DATABASE INITIALISATIE (FORCEER ALLES) ---
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
            return f"⏳ Wacht {int(COOLDOWN_SECONDS - verstreken)} sec."
    if st.session_state.ai_points <= 0: return "❌ Geen punten!"
    st.session_state.ai_points -= 1
    st.session_state.last_ai_call[u] = nu
    try:
        resp = client.chat.completions.create(model=MODEL_NAAM, messages=[{"role":"user","content":vraag}])
        return resp.choices[0].message.content
    except Exception as e: return f"Error: {e}"

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
        u = st.text_input("Naam").lower().strip()
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Log in"):
            if u in st.session_state.users and st.session_state.users[u]["pw"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.session_state.role = st.session_state.users[u]["role"]
                if u not in st.session_state.user_vocab: st.session_state.user_vocab[u] = {"hallo":"bonjour"}
                st.rerun()
    with t2:
        nu = st.text_input("Nieuwe Naam").lower().strip()
        np = st.text_input("Nieuw Wachtwoord", type="password")
        if st.button("Account maken"):
            if nu and nu not in st.session_state.users:
                st.session_state.users[nu] = {"pw":np, "role":"student"}
                st.session_state.saldi[nu] = 0
                st.session_state.user_vocab[nu] = {"hallo":"bonjour"}
                st.success("Gelukt!")
    st.stop()

# --- 6. INTERFACE ---
st.sidebar.title(f"👋 {st.session_state.username}")
st.sidebar.metric("💰 Munten", st.session_state.saldi.get(st.session_state.username, 0))
st.sidebar.metric("💎 AI Punten", st.session_state.ai_points)

menu = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role in ["teacher", "admin"]: menu.append("👩‍🏫 Leraar Paneel")
if is_admin: menu.append("👑 Admin")
nav = st.sidebar.radio("Navigatie", menu)

# --- 7. PAGINA LOGICA ---
if nav == "🏫 De Klas":
    st.title("🏫 Klaslokaal")
    c1, c2 = st.columns(2) # HIER WORDT COL2 AANGEMAAKT
    with c1:
        st.subheader("📝 Taken")
        if not st.session_state.tasks: st.info("Geen taken.")
        for i, t in enumerate(st.session_state.tasks):
            st.write(f"**{t['title']}**")
    with c2: # DIT WERKT NU OMDAT C2 HIERBOVEN IS GEDEFINIEERD
        st.subheader("📚 Lijsten")
        if not st.session_state.vocab_lists: st.info("Geen lijsten.")
        for i, v in enumerate(st.session_state.vocab_lists):
            if st.button(f"Download {v['title']}", key=f"v_{i}"):
                st.session_state.user_vocab[st.session_state.username].update(v['words'])
                st.success("Toegevoegd!")

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    for m in st.session_state.chat_messages:
        st.chat_message("user").write(f"**{m['user']}**: {m['text']}")
    if prompt := st.chat_input("Bericht..."):
        st.session_state.chat_messages.append({"user":st.session_state.username, "text":prompt})
        st.rerun()

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI")
    vraag = st.text_area("Vraag:")
    if st.button("Vraag (-1 punt)"):
        st.session_state.ai_antwoord = vraag_groq(vraag)
        st.rerun()
    if st.session_state.ai_antwoord: st.info(st.session_state.ai_antwoord)
    if st.button(f"Koop punt ({AI_PUNT_PRIJS} munten)"):
        if st.session_state.saldi[st.session_state.username] >= AI_PUNT_PRIJS:
            st.session_state.saldi[st.session_state.username] -= AI_PUNT_PRIJS
            st.session_state.ai_points += 1
            st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    mijn_w = st.session_state.user_vocab[st.session_state.username]
    tab1, tab2 = st.tabs(["Oefenen", "Toevoegen"])
    with tab1:
        if mijn_w:
            w = random.choice(list(mijn_w.keys()))
            st.write(f"Vertaal: **{w}**")
            # Simpele oefening voor nu
            if st.button("Verdien 50 munten (Demo)"):
                st.session_state.saldi[st.session_state.username] += 50
                st.rerun()
    with tab2:
        n_nl = st.text_input("NL")
        n_fr = st.text_input("FR")
        if st.button("Opslaan"):
            st.session_state.user_vocab[st.session_state.username][n_nl] = n_fr
            st.success("Opgeslagen!")

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Beheer")
    t_t = st.text_input("Taak Titel")
    t_d = st.text_area("Beschrijving")
    if st.button("Post Taak"):
        st.session_state.tasks.append({"title":t_t, "desc":t_d})
        st.success("Gepost!")

elif nav == "👑 Admin":
    st.title("👑 Admin")
    if st.button("LOCKDOWN"): st.session_state.lockdown = not st.session_state.lockdown; st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
