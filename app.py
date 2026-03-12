import streamlit as st
import random
from datetime import datetime
from openai import OpenAI
import json
import os

# --- 1. CONFIGURATIE ---
COOLDOWN_SECONDS = 60 
AI_PUNT_PRIJS = 1000
SITE_TITLE = "Putsie EDUCATION 🎓 v5.0 (Echte Database)"
MODEL_NAAM = "llama-3.1-8b-instant"
DB_FILE = "database.json" # DIT IS JE NIEUWE DATABASE BESTAND

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DE DATABASE MOTOR (DE GROTE FIX) ---
def laad_db():
    # Als het bestand al bestaat, lees het in!
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Zo niet, maak een standaard database aan:
    return {
        "users": {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}},
        "saldi": {"elliot": 10000},
        "ai_points": {"elliot": 10},
        "user_vocab": {"elliot": {"hallo": "bonjour"}},
        "chat_messages": [],
        "vocab_lists": [],
        "tasks": [],
        "klascodes": {"Putsie2024": "Klas 1A"},
        "lockdown": False,
        "lockdown_msg": "Systeem onderhoud door Elliot"
    }

def sla_db_op():
    # Schrijf alle huidige gegevens fysiek weg naar het bestand
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, indent=4)

# Laad de database de allereerste keer in het geheugen
if 'db' not in st.session_state:
    st.session_state.db = laad_db()

# Tijdelijke sessie-variabelen (deze hoeven niet in de JSON)
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'ai_antwoord_temp' not in st.session_state: st.session_state.ai_antwoord_temp = ""
if 'huidig_oefenwoord' not in st.session_state: st.session_state.huidig_oefenwoord = None

# --- 3. AI MOTOR ---
def roep_ai(vraag):
    u = st.session_state.username
    nu = datetime.now()
    if u in st.session_state.last_ai_call:
        if (nu - st.session_state.last_ai_call[u]).total_seconds() < COOLDOWN_SECONDS:
            return "⏳ Geduld! De AI leraar rust even uit."

    mijn_punten = st.session_state.db["ai_points"].get(u, 0)
    if mijn_punten <= 0: return "❌ Geen AI punten meer!"

    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Fout: Geen API-sleutel gevonden."

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    try:
        st.session_state.db["ai_points"][u] -= 1
        sla_db_op() # Sla de min-punt direct op!
        st.session_state.last_ai_call[u] = nu
        completion = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": "Je bent een leraar."}, {"role": "user", "content": vraag}]
        )
        return completion.choices[0].message.content
    except Exception as e: return f"AI Error: {str(e)}"

# --- 4. LOCKDOWN CHECK ---
is_admin = st.session_state.get('username') == "elliot"
if st.session_state.db['lockdown'] and not is_admin:
    st.error(f"🚫 LOCKDOWN ACTIEF: {st.session_state.db['lockdown_msg']}")
    st.stop()

# --- 5. LOGIN SYSTEEM ---
if not st.session_state.ingelogd:
    st.title("🎓 Putsie Login")
    t1, t2 = st.tabs(["Inloggen", "Registreren (Klascode nodig)"])
    
    with t1:
        u_in = st.text_input("Naam").lower().strip()
        p_in = st.text_input("Wachtwoord", type="password")
        if st.button("Log in", key="btn_login"):
            if u_in in st.session_state.db['users'] and st.session_state.db['users'][u_in]["pw"] == p_in:
                st.session_state.ingelogd = True
                st.session_state.username = u_in
                st.session_state.role = st.session_state.db['users'][u_in]["role"]
                st.rerun()
            else: st.error("Foute inloggegevens!")
            
    with t2:
        nu = st.text_input("Kies Naam").lower().strip()
        np = st.text_input("Kies Wachtwoord", type="password")
        kc = st.text_input("Klascode")
        if st.button("Registreer Account"):
            if kc in st.session_state.db['klascodes']:
                if nu and nu not in st.session_state.db['users']:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                    st.session_state.db['saldi'][nu] = 0
                    st.session_state.db['ai_points'][nu] = 5
                    st.session_state.db['user_vocab'][nu] = {}
                    sla_db_op() # DIRECT OPSLAAN IN JSON BESTAND!
                    st.success("Account gemaakt! Je kunt nu inloggen.")
                else: st.error("Naam is ongeldig of bestaat al.")
            else: st.error("Klascode klopt niet!")
    st.stop()

# --- 6. NAVIGATIE MENU ---
mijn_naam = st.session_state.username
st.sidebar.title(f"👤 {mijn_naam.capitalize()}")
st.sidebar.info(f"💰 {st.session_state.db['saldi'].get(mijn_naam, 0)} munten\n\n💎 {st.session_state.db['ai_points'].get(mijn_naam, 0)} AI pt")

menu = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role in ["teacher", "admin"]: menu.append("👩‍🏫 Leraar Paneel")
if is_admin: menu.append("👑 Admin")
nav = st.sidebar.radio("Navigatie", menu)

# --- 7. DE PAGINA'S ---

if nav == "🏫 De Klas":
    st.title("🏫 Klaslokaal")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📝 Taken")
        if not st.session_state.db['tasks']: st.info("Geen taken vandaag!")
        for t in st.session_state.db['tasks']:
            st.warning(f"**{t['title']}**\n\n{t['desc']}")
    with c2:
        st.subheader("📚 Woordenlijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            if st.button(f"Download: {v['title']}", key=f"dl_{i}"):
                if mijn_naam not in st.session_state.db['user_vocab']:
                    st.session_state.db['user_vocab'][mijn_naam] = {}
                st.session_state.db['user_vocab'][mijn_naam].update(v['words'])
                sla_db_op() # Sla de gedownloade woorden fysiek op!
                st.success("Opgeslagen in jouw Lab!")

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    chat_box = st.container(height=400, border=True)
    with chat_box:
        for m in st.session_state.db['chat_messages']:
            st.markdown(f"**{m['user']}**: {m['text']}")

    if p := st.chat_input("Bericht..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op() # Chatbericht fysiek opslaan!
        st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    mijn_woorden = st.session_state.db['user_vocab'].get(mijn_naam, {})
    
    t1, t2 = st.tabs(["🎮 Oefenen", "➕ Toevoegen"])
    with t1:
        if mijn_woorden:
            if not st.session_state.huidig_oefenwoord:
                st.session_state.huidig_oefenwoord = random.choice(list(mijn_woorden.keys()))
            vraag = st.session_state.huidig_oefenwoord
            
            st.write(f"Vertaal: **{vraag}**")
            antwoord = st.text_input("Antwoord:")
            if st.button("Check"):
                if antwoord.lower().strip() == mijn_woorden[vraag].lower().strip():
                    st.success("Goed! +50 munten")
                    st.session_state.db['saldi'][mijn_naam] += 50
                    sla_db_op() # Geld opslaan!
                    st.session_state.huidig_oefenwoord = random.choice(list(mijn_woorden.keys()))
                    st.rerun()
                else: st.error("Fout, probeer opnieuw.")
        else: st.info("Voeg eerst woorden toe bij de andere tab!")
        
    with t2:
        nl = st.text_input("NL Woord")
        fr = st.text_input("FR Vertaling")
        if st.button("Opslaan in lijst"):
            if nl and fr:
                if mijn_naam not in st.session_state.db['user_vocab']:
                    st.session_state.db['user_vocab'][mijn_naam] = {}
                st.session_state.db['user_vocab'][mijn_naam][nl.strip()] = fr.strip()
                sla_db_op() # Nieuwe woorden opslaan!
                st.success("Opgeslagen!")
                st.rerun()

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI")
    vraag = st.text_area("Vraag aan AI:")
    if st.button("Verstuur (-1 pt)"):
        with st.spinner("Laden..."):
            st.session_state.ai_antwoord_temp = roep_ai(vraag)
            st.rerun()
    if st.session_state.ai_antwoord_temp:
        st.info(st.session_state.ai_antwoord_temp)

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Leraar")
    titel = st.text_input("Taak Titel")
    desc = st.text_area("Taak Beschrijving")
    if st.button("Post Taak"):
        st.session_state.db['tasks'].append({"title": titel, "desc": desc})
        sla_db_op()
        st.success("Taak gepost!")

elif nav == "👑 Admin":
    st.title("👑 Admin Room")
    msg = st.text_input("Lockdown tekst", value=st.session_state.db['lockdown_msg'])
    if st.button("Toggle Lockdown"):
        st.session_state.db['lockdown'] = not st.session_state.db['lockdown']
        st.session_state.db['lockdown_msg'] = msg
        sla_db_op()
        st.rerun()
    
    st.divider()
    if st.button("Maak DB schoon (VERWIJDER CHAT & TAKEN)"):
        st.session_state.db['chat_messages'] = []
        st.session_state.db['tasks'] = []
        sla_db_op()
        st.success("Schoongemaakt!")

if st.sidebar.button("Uitloggen", key="uitlog_btn"):
    st.session_state.ingelogd = False
    st.rerun()
