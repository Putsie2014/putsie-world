import streamlit as st
import random
from datetime import datetime
from openai import OpenAI
import json
import os

# --- 1. CONFIGURATIE ---
COOLDOWN_SECONDS = 120
AI_PUNT_PRIJS = 1000
SITE_TITLE = "Putsie EDUCATION"
NAAM = "llama-3.1-8b-instant"
DB_FILE = "database.json"
st.set_page_config(page_title=SITE_TITLE, layout="wide", initial_sidebar_state="expanded")

# --- 2. DE DATABASE MOTOR ---
def laad_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, indent=4)

if 'db' not in st.session_state: st.session_state.db = laad_db()
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'ai_antwoord_temp' not in st.session_state: st.session_state.ai_antwoord_temp = ""
if 'huidig_oefenwoord' not in st.session_state: st.session_state.huidig_oefenwoord = None

is_admin = st.session_state.get('username') == "elliot"

# --- 3. LOCKDOWN SCHERM (UI VERBETERD) ---
if st.session_state.db.get('lockdown') and not is_admin:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;} /* Verberg menu voor leerlingen */
        </style>
        <div style="text-align:center; padding: 50px; background-color: #ff4b4b; color: white; border-radius: 15px; margin-top: 10%;">
            <h1 style="color: white; font-size: 60px;">🚫 LOCKDOWN IS ACTIEF</h1>
            <h2>We zijn bezig met de bug te fixen.</h2>
            <p style="font-size: 20px;"><i>Bericht van admin: {msg}</i></p>
        </div>
    """.replace("{msg}", st.session_state.db.get('lockdown_msg', 'Geen bericht')), unsafe_allow_html=True)
    st.stop()

# --- 4. LOGIN SYSTEEM (UI VERBETERD) ---
if not st.session_state.ingelogd:
    # Maak login in het midden van het scherm
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown(f"<h1 style='text-align: center;'>{SITE_TITLE}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Log in om naar de klas te gaan</p>", unsafe_allow_html=True)
        
        t1, t2 = st.tabs(["Inloggen", "Registreren (Klascode)"])
        
        with t1:
            u_in = st.text_input("Naam").lower().strip()
            p_in = st.text_input("Wachtwoord", type="password")
            if st.button("Log in", type="primary", use_container_width=True):
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
            if st.button("Registreer Account", type="primary", use_container_width=True):
                if kc in st.session_state.db['klascodes']:
                    if nu and nu not in st.session_state.db['users']:
                        st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                        st.session_state.db['saldi'][nu] = 0
                        st.session_state.db['ai_points'][nu] = 5
                        st.session_state.db['user_vocab'][nu] = {}
                        sla_db_op()
                        st.success("Account gemaakt! Log in via de andere tab.")
                    else: st.error("Naam is ongeldig of bestaat al.")
                else: st.error("Klascode klopt niet!")
    st.stop()

# --- 5. AI MOTOR ---
def roep_ai(vraag):
    u = st.session_state.username
    nu = datetime.now()
    if u in st.session_state.last_ai_call and (nu - st.session_state.last_ai_call[u]).total_seconds() < COOLDOWN_SECONDS:
        return "⏳ Geduld! Je moet even wachten met nog een antwoord te vragen"
    if st.session_state.db["ai_points"].get(u, 0) <= 0: return "❌ Geen AI punten meer!"
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Fout: Geen API-sleutel gevonden."

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    try:
        st.session_state.db["ai_points"][u] -= 1
        sla_db_op()
        st.session_state.last_ai_call[u] = nu
        resp = client.chat.completions.create(model=MODEL_NAAM, messages=[{"role": "system", "content": "Je bent een leraar."}, {"role": "user", "content": vraag}])
        return resp.choices[0].message.content
    except Exception as e: return f"AI Error: {str(e)}"

# --- 6. SIDEBAR MENU ---
mijn_naam = st.session_state.username
st.sidebar.title(f"👤 {mijn_naam.capitalize()}")

# Mooie metrics
col_s1, col_s2 = st.sidebar.columns(2)
col_s1.metric("💰 Munten", st.session_state.db['saldi'].get(mijn_naam, 0))
col_s2.metric("💎 AI Punten", st.session_state.db['ai_points'].get(mijn_naam, 0))
st.sidebar.divider()

menu = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if st.session_state.role in ["teacher", "admin"]: menu.append("👩‍🏫 Leraar Paneel")
if is_admin: menu.append("👑 Owner Panel")
nav = st.sidebar.radio("Ga naar:", menu)

st.sidebar.divider()
if st.sidebar.button("Log Uit", use_container_width=True):
    st.session_state.ingelogd = False
    st.rerun()

# --- 7. PAGINA'S ---

if nav == "🏫 De Klas":
    st.title("🏫 Het Klaslokaal")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📝 Openstaande Taken")
        if not st.session_state.db['tasks']: st.info("Je bent helemaal vrij! Geen taken.")
        for t in st.session_state.db['tasks']:
            with st.container(border=True): # Mooie kaders
                st.markdown(f"### {t['title']}")
                st.write(t['desc'])

    with c2:
        st.subheader("📚 Woordenlijsten")
        if not st.session_state.db['vocab_lists']: st.info("Geen woordenlijsten gedeeld.")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            with st.container(border=True):
                st.markdown(f"**📂 {v['title']}** ({len(v['words'])} woorden)")
                if st.button("📥 Download naar mijn Lab", key=f"dl_{i}", use_container_width=True):
                    if mijn_naam not in st.session_state.db['user_vocab']:
                        st.session_state.db['user_vocab'][mijn_naam] = {}
                    st.session_state.db['user_vocab'][mijn_naam].update(v['words'])
                    sla_db_op()
                    st.toast(f"{v['title']} toegevoegd aan je Lab!", icon="✅") # Subtiele melding

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    chat_box = st.container(height=500, border=True)
    with chat_box:
        for m in st.session_state.db['chat_messages']:
            with st.chat_message("user"):
                st.write(f"**{m['user'].capitalize()}**: {m['text']}")

    if p := st.chat_input("Schrijf in de groep..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op()
        st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    mijn_woorden = st.session_state.db['user_vocab'].get(mijn_naam, {})
    
    t1, t2 = st.tabs(["🎮 Oefenen", "➕ Eigen woorden toevoegen"])
    with t1:
        if mijn_woorden:
            with st.container(border=True):
                if not st.session_state.huidig_oefenwoord:
                    st.session_state.huidig_oefenwoord = random.choice(list(mijn_woorden.keys()))
                vraag = st.session_state.huidig_oefenwoord
                
                st.markdown(f"### Wat is de vertaling van:")
                st.markdown(f"<h2 style='color: #4CAF50;'>{vraag}</h2>", unsafe_allow_html=True)
                
                antwoord = st.text_input("Typ je antwoord hier:")
                if st.button("Controleer Antwoord", type="primary"):
                    if antwoord.lower().strip() == mijn_woorden[vraag].lower().strip():
                        st.toast("Goedzo! +50 munten 🎉", icon="🪙")
                        st.session_state.db['saldi'][mijn_naam] += 50
                        st.session_state.huidig_oefenwoord = random.choice(list(mijn_woorden.keys()))
                        sla_db_op()
                        st.rerun()
                    else: st.error("Helaas, dat klopt niet helemaal. Probeer het opnieuw!")
        else: st.warning("Voeg eerst woorden toe of download een lijst uit de klas!")
        
    with t2:
        with st.container(border=True):
            st.subheader("Voeg een nieuw woord toe")
            nl = st.text_input("Nederlands woord:")
            fr = st.text_input("Franse vertaling:")
            if st.button("Sla op in mijn Lab"):
                if nl and fr:
                    if mijn_naam not in st.session_state.db['user_vocab']: st.session_state.db['user_vocab'][mijn_naam] = {}
                    st.session_state.db['user_vocab'][mijn_naam][nl.strip()] = fr.strip()
                    sla_db_op()
                    st.success(f"'{nl}' opgeslagen!")
                    st.rerun()

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.info(f"Kosten: 1 AI punt per vraag. Je hebt er nu: {st.session_state.db['ai_points'].get(mijn_naam, 0)}")
    
    vraag = st.text_area("Wat wil je weten?")
    if st.button("Vraag aan AI", type="primary"):
        with st.spinner("AI denkt na..."):
            st.session_state.ai_antwoord_temp = roep_ai(vraag)
            st.rerun()
            
    if st.session_state.ai_antwoord_temp:
        with st.chat_message("assistant"):
            st.write(st.session_state.ai_antwoord_temp)
            
    st.divider()
    if st.button(f"Koop 1 AI Punt ({AI_PUNT_PRIJS} munten)"):
        if st.session_state.db['saldi'].get(mijn_naam, 0) >= AI_PUNT_PRIJS:
            st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
            st.session_state.db['ai_points'][mijn_naam] = st.session_state.db['ai_points'].get(mijn_naam, 0) + 1
            sla_db_op()
            st.toast("AI punt gekocht!", icon="💎")
            st.rerun()
        else: st.error("Je hebt niet genoeg munten.")

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Leraar Dashboard")
    
    t1, t2 = st.tabs(["📝 Taak Posten", "📚 Woordenlijst Delen"])
    with t1:
        titel = st.text_input("Titel van de Taak")
        desc = st.text_area("Omschrijving")
        if st.button("Post Taak naar de Klas", type="primary"):
            st.session_state.db['tasks'].append({"title": titel, "desc": desc})
            sla_db_op()
            st.success("Taak staat in de klas!")
            
    with t2: # DE FIX VOOR DE WOORDENLIJSTEN
        l_titel = st.text_input("Naam van de lijst (bijv: Hoofdstuk 1)")
        l_woorden = st.text_area("Woorden (formaat: nl=fr, elke op een nieuwe regel)")
        if st.button("Deel Lijst met Klas", type="primary"):
            d = {}
            for r in l_woorden.split("\n"):
                if "=" in r:
                    k, v = r.split("=")
                    d[k.strip()] = v.strip()
            if d:
                st.session_state.db['vocab_lists'].append({"title": l_titel, "words": d})
                sla_db_op()
                st.success(f"Lijst '{l_titel}' gedeeld met {len(d)} woorden!")
            else: st.error("Geen geldige woorden gevonden. Gebruik het '=' teken.")

elif nav == "👑 Admin":
    st.title("👑 Elliot's Control Room")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("🚨 Lockdown Systeem")
            msg = st.text_input("Lockdown tekst:", value=st.session_state.db['lockdown_msg'])
            if st.button("Toggle Lockdown", type="primary" if not st.session_state.db['lockdown'] else "secondary"):
                st.session_state.db['lockdown'] = not st.session_state.db['lockdown']
                st.session_state.db['lockdown_msg'] = msg
                sla_db_op()
                st.rerun()
            if st.session_state.db['lockdown']: st.error("STATUS: ACTIEF. Leerlingen kunnen niet inloggen.")
            else: st.success("STATUS: VEILIG. De site is open.")
            
    with col2:
        with st.container(border=True):
            st.subheader("💸 Munten Uitdelen")
            users = list(st.session_state.db['users'].keys())
            target = st.selectbox("Kies leerling:", users)
            amount = st.number_input("Aantal munten (kan ook negatief zijn):", value=1000, step=100)
            if st.button("Geef Munten"):
                st.session_state.db['saldi'][target] = st.session_state.db['saldi'].get(target, 0) + amount
                sla_db_op()
                st.success(f"{amount} munten naar {target} gestuurd! Nieuw saldo: {st.session_state.db['saldi'][target]}")

    with st.container(border=True):
        st.subheader("🧹 Database Opschonen")
        if st.button("Verwijder alle Chat & Taken"):
            st.session_state.db['chat_messages'] = []
            st.session_state.db['tasks'] = []
            sla_db_op()
            st.success("Schoon!")
