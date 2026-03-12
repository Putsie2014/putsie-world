import streamlit as st
import random
from datetime import datetime
from openai import OpenAI
import json
import os

# --- 1. CONFIGURATIE & PADEN ---
SITE_TITLE = "🌎 Putsie EDUCATION 🎓"
MODEL_NAAM = "llama-3.1-8b-instant"
AI_PUNT_PRIJS = 5000
COOLDOWN_SECONDS = 180

# Geforceerd pad zodat Streamlit het bestand NOOIT kwijtraakt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")

st.set_page_config(page_title=SITE_TITLE, layout="wide", initial_sidebar_state="expanded")

# --- 2. TITANIUM DATABASE MOTOR ---
def laad_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"🚨 DATABASE LEES FOUT: {e}") 
    
    basis_db = {
        "users": {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}},
        "saldi": {"elliot": 10000, "annelies": 1000},
        "ai_points": {"elliot": 10, "annelies": 5},
        "user_vocab": {"elliot": {"hallo": "bonjour"}},
        "chat_messages": [],
        "vocab_lists": [],
        "tasks": [],
        "klascodes": {"Putsie2024": "Klas 1A"},
        "lockdown": False,
        "lockdown_msg": "Systeem onderhoud door Elliot"
    }
    
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(basis_db, f, indent=4)
    except Exception as e:
        st.error(f"🚨 KAN DATABASE NIET AANMAKEN: {e}")
    return basis_db

def sla_db_op():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.db, f, indent=4)
    except Exception as e:
        st.error(f"🚨 DATABASE OPSLAG FOUT: {e}")

# Zorg dat de DB altijd geladen is
if 'db' not in st.session_state:
    st.session_state.db = laad_db()

# Sessie variabelen (resetten bij refresh, is normaal voor UI)
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'ai_antwoord_temp' not in st.session_state: st.session_state.ai_antwoord_temp = ""
if 'huidig_oefenwoord' not in st.session_state: st.session_state.huidig_oefenwoord = None

# --- 3. LOGIN & REGISTRATIE (NU MET INSTANT SAVE) ---
if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center;'>{SITE_TITLE}</h1>", unsafe_allow_html=True)
        st.write("---")
        
        t1, t2 = st.tabs(["🔑 Inloggen", "📝 Registreren"])
        
        with t1:
            u_in = st.text_input("Naam").lower().strip()
            p_in = st.text_input("Wachtwoord", type="password")
            if st.button("Log In", type="primary", use_container_width=True):
                if u_in in st.session_state.db['users'] and st.session_state.db['users'][u_in]["pw"] == p_in:
                    st.session_state.ingelogd = True
                    st.session_state.username = u_in
                    st.session_state.role = st.session_state.db['users'][u_in]["role"]
                    st.rerun()
                else:
                    st.error("❌ Naam of wachtwoord fout.")
                    
        with t2:
            nu = st.text_input("Kies Gebruikersnaam").lower().strip()
            np = st.text_input("Kies Wachtwoord ", type="password")
            kc = st.text_input("Klascode (Vraag aan de juf)")
            if st.button("Account Aanmaken", use_container_width=True):
                if kc in st.session_state.db['klascodes']:
                    if nu and nu not in st.session_state.db['users']:
                        # Maak alles aan in het geheugen
                        st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                        st.session_state.db['saldi'][nu] = 0
                        st.session_state.db['ai_points'][nu] = 5
                        st.session_state.db['user_vocab'][nu] = {}
                        # SLA DIRECT OP NAAR DE HARDE SCHIJF!
                        sla_db_op() 
                        st.success("✅ Account opgeslagen, Je kunt nu inloggen via inloggen.")
                    else: st.error("⚠️ Naam is al bezet of leeg.")
                else: st.error("⛔ Klascode is ongeldig")
    st.stop()

# --- 4. RECHTEN & LOCKDOWN ---
mijn_naam = st.session_state.username
is_admin = st.session_state.role == "admin"
is_teacher = st.session_state.role in ["teacher", "admin"]

if st.session_state.db['lockdown'] and not is_admin:
    st.markdown(f"""
        <style>[data-testid="stSidebar"] {{display: none;}}</style>
        <div style="text-align:center; padding:80px; background-color:#ff4b4b; border-radius:15px; color:white; margin-top:50px;">
            <h1 style="font-size:80px; margin:0;">Fout!</h1>
            <h1 style="margin:Systeem is in lockown</h1>
            <p style="font-size:22px;">{st.session_state.db['lockdown_msg']}</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Uitloggen", type="secondary"):
        st.session_state.ingelogd = False
        st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
st.sidebar.markdown(f"## 👋Welkom, **{mijn_naam.capitalize()}** bij Putsie Education ")
st.sidebar.write("---")
c1, c2 = st.sidebar.columns(2)
c1.metric("💰 Geld", st.session_state.db['saldi'].get(mijn_naam, 0))
c2.metric("💎 AI Punten", st.session_state.db['ai_points'].get(mijn_naam, 0))
st.sidebar.write("---")

menu = ["🏫 De Klas", "💬 Klas Chat", "AI Hulp", "🇫🇷 Frans Lab"]
if is_teacher: menu.append("👩‍🏫 Leraar Paneel")
if is_admin: menu.append("👑 Admin Panel")

nav = st.sidebar.radio("📍 Navigatie", menu)
st.sidebar.write("---")
if st.sidebar.button("🚪 Uitloggen", use_container_width=True):
    st.session_state.ingelogd = False
    st.rerun()

# --- 6. PAGINA'S ---

if nav == "🏫 De Klas":
    st.title("🏫 Het Klaslokaal")
    st.markdown("Hier vind je al je taken en gedeelde woordenlijsten.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Jouw Taken")
        if not st.session_state.db['tasks']: 
            st.info("🎉 Je bent helemaal vrij! Geen huiswerk vandaag, ga buiten spelen ⚽️")
        for t in st.session_state.db['tasks']:
            with st.container(border=True):
                st.markdown(f"#### 📌 {t['title']}")
                st.write(t['desc'])
                
    with col2:
        st.subheader("📚 WoordenPakketen")
        if not st.session_state.db['vocab_lists']:
            st.info("Geen lijsten gedeeld door de leerkracht.")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            with st.container(border=True):
                st.write(f"**📂 {v['title']}** ({len(v['words'])} woorden)")
                if st.button(f"📥 Download naar mijn Labo", key=f"dl_{i}", use_container_width=True):
                    if mijn_naam not in st.session_state.db['user_vocab']: st.session_state.db['user_vocab'][mijn_naam] = {}
                    st.session_state.db['user_vocab'][mijn_naam].update(v['words'])
                    sla_db_op()
                    st.toast(f"Lijst '{v['title']}' opgeslagen!", icon="✅")

elif nav == "💬 Klas Chat":
    st.title("💬 Klas Chat")
    st.markdown("Praat met je klas")
    
    chat_box = st.container(height=500, border=True)
    with chat_box:
        if not st.session_state.db['chat_messages']:
            st.write("Nog geen berichten... Wees de eerste!")
        for m in st.session_state.db['chat_messages']:
            with st.chat_message("user" if m['user'] != mijn_naam else "assistant"):
                st.write(f"**{m['user'].capitalize()}**: {m['text']}")
                
    if p := st.chat_input("Typ je bericht hier..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op()
        st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    mijn_w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    
    tab1, tab2 = st.tabs([" Oefenen", "➕ Woorden Toevoegen"])
    with tab1:
        if mijn_w:
            with st.container(border=True):
                if not st.session_state.huidig_oefenwoord:
                    st.session_state.huidig_oefenwoord = random.choice(list(mijn_w.keys()))
                vraag = st.session_state.huidig_oefenwoord
                
                st.markdown(f"### Vertaal: **<span style='color:#0080ff'>{vraag}</span>**", unsafe_allow_html=True)
                gok = st.text_input("Typ je Franse antwoord:")
                
                if st.button("Controleer Antwoord", type="primary"):
                    if gok.lower().strip() == mijn_w[vraag].lower().strip():
                        st.balloons()
                        st.toast("Fantastisch! +50 munten 🎉", icon="💰")
                        st.session_state.db['saldi'][mijn_naam] += 50
                        st.session_state.huidig_oefenwoord = random.choice(list(mijn_w.keys()))
                        sla_db_op()
                        st.rerun()
                    else: 
                        st.error("Dat klopt helaas niet. Probeer het opnieuw!")
        else: 
            st.warning("Je lijst is leeg! Ga naar 'De Klas' om een lijst te downloaden of voeg zelf woorden toe.")
            
    with tab2:
        with st.container(border=True):
            st.subheader("Voeg je eigen woorden toe")
            nl_in = st.text_input("Nederlands woord:")
            fr_in = st.text_input("Franse vertaling:")
            if st.button("Sla op in mijn lijst", type="secondary"):
                if nl_in and fr_in:
                    if mijn_naam not in st.session_state.db['user_vocab']: st.session_state.db['user_vocab'][mijn_naam] = {}
                    st.session_state.db['user_vocab'][mijn_naam][nl_in.strip()] = fr_in.strip()
                    sla_db_op()
                    st.success(f"'{nl_in}' succesvol toegevoegd!")
                else:
                    st.error("Vul beide velden in!")

elif nav == "AI Hulp":
    st.title("AI hulp")
    st.info(f"Je hebt {st.session_state.db['ai_points'].get(mijn_naam, 0)} AI punten. Elke vraag kost 1 punt.")
    
    vraag = st.text_area("Wat wil je aan de virtuele leraar vragen?")
    if st.button("Verstuur Vraag", type="primary"):
        # Plaats hier de Groq/OpenAI code
        st.warning("⚠️ Let op: AI functie is actief. Zorg dat je GROQ_API_KEY in je secrets staat!")
    
    st.write("---")
    st.subheader("🛒 Winkel")
    if st.button(f"Koop 1 AI Punt ({AI_PUNT_PRIJS} munten)"):
        if st.session_state.db['saldi'].get(mijn_naam, 0) >= AI_PUNT_PRIJS:
            st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
            st.session_state.db['ai_points'][mijn_naam] = st.session_state.db['ai_points'].get(mijn_naam, 0) + 1
            sla_db_op()
            st.success("Aankoop geslaagd!")
            st.rerun()
        else:
            st.error("Je hebt niet genoeg munten!")

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Leraar Paneel")
    
    t1, t2, t3 = st.tabs(["🔑 Klascodes", "📝 Taken Posten", "📚 Lijsten Delen"])
    with t1:
        st.subheader("Actieve Klascodes")
        for c, k in st.session_state.db['klascodes'].items():
            st.write(f"🏷️ **{c}** verleent toegang tot: {k}")
        st.write("---")
        nc = st.text_input("Maak Nieuwe Code")
        nk = st.text_input("Voor welke klas? (bijv. 2B)")
        if st.button("Code Toevoegen", type="primary"):
            if nc and nk:
                st.session_state.db['klascodes'][nc] = nk
                sla_db_op()
                st.success("Klascode toegevoegd!")
                st.rerun()
    with t2:
        tt = st.text_input("Titel van de taak")
        td = st.text_area("Omschrijving / Huiswerk details")
        if st.button("Post Taak naar Klas"):
            st.session_state.db['tasks'].append({"title": tt, "desc": td})
            sla_db_op()
            st.success("Taak gepost!")
    with t3:
        lt = st.text_input("Naam van de woordenlijst")
        ld = st.text_area("Typ de woorden zo: nederlands=frans (elke op een nieuwe regel)")
        if st.button("Deel met Klas"):
            d = {line.split("=")[0].strip(): line.split("=")[1].strip() for line in ld.split("\n") if "=" in line}
            if d:
                st.session_state.db['vocab_lists'].append({"title": lt, "words": d})
                sla_db_op()
                st.success("Lijst gedeeld!")
            else:
                st.error("Geen geldige woorden gevonden.")

elif nav == "👑 Admin Panel":
    st.title("👑 Admin Control Room")
    
    tab_eco, tab_lock, tab_db = st.tabs(["💰 Economie", "🚨 Lockdown", "⚙️ RAW Database Editor"])
    
    with tab_eco:
        st.subheader("Munten & Punten Beheren")
        users = list(st.session_state.db['users'].keys())
        doelwit = st.selectbox("Selecteer Leerling", users)
        
        c1, c2 = st.columns(2)
        with c1:
            bedrag = st.number_input("Munten (kan ook negatief zijn)", value=100)
            if st.button("Verwerk Munten"):
                st.session_state.db['saldi'][doelwit] = st.session_state.db['saldi'].get(doelwit, 0) + bedrag
                sla_db_op()
                st.success(f"{bedrag} munten naar {doelwit}!")
        with c2:
            ai_pt = st.number_input("AI Punten toevoegen", value=1)
            if st.button("Geef AI Punten"):
                st.session_state.db['ai_points'][doelwit] = st.session_state.db['ai_points'].get(doelwit, 0) + ai_pt
                sla_db_op()
                st.success(f"Punten gegeven!")

    with tab_lock:
        st.subheader("Systeem Vergrendelen")
        l_msg = st.text_input("Lockdown Bericht", value=st.session_state.db['lockdown_msg'])
        if st.button("TOGGLE LOCKDOWN STATUS", type="primary" if not st.session_state.db['lockdown'] else "secondary"):
            st.session_state.db['lockdown'] = not st.session_state.db['lockdown']
            st.session_state.db['lockdown_msg'] = l_msg
            sla_db_op()
            st.rerun()
        if st.session_state.db['lockdown']:
            st.error("STATUS: ACTIEF. Leerlingen kunnen de site niet in.")
        else:
            st.success("STATUS: VEILIG. Site is open.")
            
    with tab_db:
        st.subheader("⚠️ Rauwe Database Bewerken (Gevaarlijk!)")
        st.markdown("Hier kun je direct in de code van de database werken. **Zorg dat je geen comma's of haakjes verwijdert, anders crasht de app!**")
        
        # Converteer de huidige database naar een mooi geformatteerde JSON string
        huidige_db_string = json.dumps(st.session_state.db, indent=4)
        
        # Laat een tekstveld zien waar Elliot de code kan aanpassen
        nieuwe_db_string = st.text_area("JSON Database", value=huidige_db_string, height=500)
        
        if st.button("Sla Gewijzigde Code Op", type="primary"):
            try:
                # Probeer de tekst terug te zetten naar data
                nieuwe_db = json.loads(nieuwe_db_string)
                # Als het lukt, overschrijf de sessie en sla op!
                st.session_state.db = nieuwe_db
                sla_db_op()
                st.success("✅ Database succesvol overschreven en opgeslagen!")
                st.rerun()
            except json.JSONDecodeError as e:
                # Als Elliot een tikfoutje maakt (bijv. een vergeten aanhalingsteken)
                st.error(f"❌ Fout in JSON code! Je hebt ergens een haakje of komma verkeerd staan. Foutmelding: {e}")
