import streamlit as st
import random
from datetime import datetime
from openai import OpenAI
import json
import os

# --- 1. CONFIGURATIE ---
SITE_TITLE = "(TEST)Putsie EDUCATION 🎓"
MODEL_NAAM = "llama-3.1-8b-instant"
AI_PUNT_PRIJS = 1000
COOLDOWN_SECONDS = 60

# We forceren het exacte pad naar de map waar dit script staat
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. TITANIUM DATABASE MOTOR ---
def laad_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            # Als het bestand stuk is, laat de fout zien!
            st.error(f"🚨 DATABASE LEES FOUT: {e}") 
    
    # Als we hier komen, bestond het bestand niet of was het onleesbaar.
    # We maken de basis database aan:
    basis_db = {
        "users": {
            "elliot": {"pw": "Putsie", "role": "admin"},
            "annelies": {"pw": "JufAnnelies", "role": "teacher"}
        },
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
    
    # Sla deze basis DIRECT fysiek op, zodat het bestand vanaf seconde 1 bestaat
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

# Initialiseer de database
if 'db' not in st.session_state:
    st.session_state.db = laad_db()

# Tijdelijke UI variabelen
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'ai_antwoord_temp' not in st.session_state: st.session_state.ai_antwoord_temp = ""
if 'huidig_oefenwoord' not in st.session_state: st.session_state.huidig_oefenwoord = None

# --- 3. LOGIN SYSTEEM ---
# (De rest van je code blijft hier exact hetzelfde)

# --- 3. LOGIN SYSTEEM ---
if not st.session_state.ingelogd:
    st.title(f" {SITE_TITLE}")
    t1, t2 = st.tabs(["Aanmelden", ""])
    
    with t1:
        u_in = st.text_input("Naam").lower().strip()
        p_in = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen", type="primary", use_container_width=True):
            if u_in in st.session_state.db['users'] and st.session_state.db['users'][u_in]["pw"] == p_in:
                st.session_state.ingelogd = True
                st.session_state.username = u_in
                st.session_state.role = st.session_state.db['users'][u_in]["role"]
                st.rerun()
            else:
                st.error("Naam of wachtwoord onjuist.")
                
    with t2:
        nu = st.text_input("Kies Gebruikersnaam").lower().strip()
        np = st.text_input("Kies Wachtwoord ", type="password")
        kc = st.text_input("Klascode")
        if st.button("Account aanmaken", use_container_width=True):
            if kc in st.session_state.db['klascodes']:
                if nu and nu not in st.session_state.db['users']:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                    st.session_state.db['saldi'][nu] = 0
                    st.session_state.db['ai_points'][nu] = 5
                    st.session_state.db['user_vocab'][nu] = {}
                    sla_db_op()
                    st.success("Account gemaakt! Je kunt nu inloggen.")
                else: st.error("Naam is al bezet of leeg.")
            else: st.error("Klascode is niet geldig.")
    st.stop()

# --- 4. RECHTEN & LOCKDOWN ---
mijn_naam = st.session_state.username
is_admin = st.session_state.role == "admin"
is_teacher = st.session_state.role in ["teacher", "admin"]

if st.session_state.db['lockdown'] and not is_admin:
    st.markdown(f"""
        <div style="text-align:center; padding:100px; background-color:#ff4b4b; border-radius:20px; color:white;">
            <h1 style="font-size:80px;">🚫</h1>
            <h1>LOCKDOWN ACTIEF</h1>
            <p style="font-size:20px;">{st.session_state.db['lockdown_msg']}</p>
        </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("Log uit"):
        st.session_state.ingelogd = False
        st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
st.sidebar.title(f"👋 {mijn_naam.capitalize()}")
c1, c2 = st.sidebar.columns(2)
c1.metric("💰 Munten", st.session_state.db['saldi'].get(mijn_naam, 0))
c2.metric("💎 AI", st.session_state.db['ai_points'].get(mijn_naam, 0))
st.sidebar.divider()

menu = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if is_teacher: menu.append("👩‍🏫 Leraar Paneel")
if is_admin: menu.append("👑 Admin Panel")
nav = st.sidebar.radio("Navigatie", menu)

if st.sidebar.button("Uitloggen", type="secondary", use_container_width=True):
    st.session_state.ingelogd = False
    st.rerun()

# --- 6. PAGINA'S ---

if nav == "🏫 De Klas":
    st.title("🏫 Klaslokaal")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Taken")
        if not st.session_state.db['tasks']: st.info("Geen huiswerk!")
        for t in st.session_state.db['tasks']:
            with st.container(border=True):
                st.markdown(f"### {t['title']}")
                st.write(t['desc'])
    with col2:
        st.subheader("📚 Woordenlijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            with st.container(border=True):
                st.write(f"📂 **{v['title']}**")
                if st.button(f"Downloaden", key=f"dl_{i}", use_container_width=True):
                    if mijn_naam not in st.session_state.db['user_vocab']: st.session_state.db['user_vocab'][mijn_naam] = {}
                    st.session_state.db['user_vocab'][mijn_naam].update(v['words'])
                    sla_db_op()
                    st.toast("Toegevoegd aan Frans Lab!")

elif nav == "💬 SchoolChat":
    st.title("💬 Groepschat")
    chat_box = st.container(height=450, border=True)
    with chat_box:
        for m in st.session_state.db['chat_messages']:
            with st.chat_message("user"):
                st.write(f"**{m['user'].capitalize()}**: {m['text']}")
    if p := st.chat_input("Bericht aan de klas..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op()
        st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    mijn_w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    tab1, tab2 = st.tabs(["🎮 Oefenen", "➕ Toevoegen"])
    with tab1:
        if mijn_w:
            if not st.session_state.huidig_oefenwoord:
                st.session_state.huidig_oefenwoord = random.choice(list(mijn_w.keys()))
            vraag = st.session_state.huidig_oefenwoord
            st.markdown(f"### Vertaal: <span style='color:#ff4b4b'>{vraag}</span>", unsafe_allow_html=True)
            gok = st.text_input("Antwoord:")
            if st.button("Check", type="primary"):
                if gok.lower().strip() == mijn_w[vraag].lower().strip():
                    st.balloons()
                    st.session_state.db['saldi'][mijn_naam] += 50
                    st.session_state.huidig_oefenwoord = random.choice(list(mijn_w.keys()))
                    sla_db_op()
                    st.rerun()
                else: st.error("Niet goed!")
        else: st.warning("Download eerst een lijst in de klas.")
    with tab2:
        nl_in = st.text_input("NL")
        fr_in = st.text_input("FR")
        if st.button("Voeg toe"):
            if mijn_naam not in st.session_state.db['user_vocab']: st.session_state.db['user_vocab'][mijn_naam] = {}
            st.session_state.db['user_vocab'][mijn_naam][nl_in] = fr_in
            sla_db_op()
            st.success("Opgeslagen!")

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.info(f"Je hebt {st.session_state.db['ai_points'].get(mijn_naam, 0)} AI punten.")
    vraag = st.text_area("Stel je vraag:")
    if st.button("Vraag AI (-1 punt)"):
        # Hier komt je OpenAI logic. Zorg dat de API key in Secrets staat.
        st.warning("AI leraar is onderweg! (Vergeet je GROQ_API_KEY niet)")

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Leraar Paneel")
    t1, t2, t3 = st.tabs(["🔑 Klascodes", "📝 Taken", "📚 Woordenlijsten"])
    with t1:
        st.subheader("Beheer Klascodes")
        for c, k in st.session_state.db['klascodes'].items():
            st.write(f"🏷️ **{c}** -> {k}")
        nc = st.text_input("Nieuwe Code")
        nk = st.text_input("Klas Naam")
        if st.button("Code Toevoegen"):
            st.session_state.db['klascodes'][nc] = nk
            sla_db_op()
            st.rerun()
    with t2:
        tt = st.text_input("Titel")
        td = st.text_area("Uitleg")
        if st.button("Post Taak"):
            st.session_state.db['tasks'].append({"title": tt, "desc": td})
            sla_db_op()
            st.success("Gepost!")
    with t3:
        lt = st.text_input("Lijst Naam")
        ld = st.text_area("nl=fr (per regel)")
        if st.button("Deel Lijst"):
            d = {line.split("=")[0].strip(): line.split("=")[1].strip() for line in ld.split("\n") if "=" in line}
            st.session_state.db['vocab_lists'].append({"title": lt, "words": d})
            sla_db_op()
            st.success("Lijst gedeeld!")

elif nav == "👑 Admin Panel":
    st.title("👑 Admin Panel")
    
    colA, colB = st.columns(2)
    with colA:
        with st.container(border=True):
            st.subheader("🚨 Lockdown")
            l_msg = st.text_input("Bericht", value=st.session_state.db['lockdown_msg'])
            if st.button("TOGGLE LOCKDOWN", type="primary"):
                st.session_state.db['lockdown'] = not st.session_state.db['lockdown']
                st.session_state.db['lockdown_msg'] = l_msg
                sla_db_op()
                st.rerun()
            st.write("Status:", "🔴 OP SLOT" if st.session_state.db['lockdown'] else "🟢 OPEN")
            
    with colB:
        with st.container(border=True):
            st.subheader("💰 Munten Beheer")
            target = st.selectbox("Leerling", list(st.session_state.db['users'].keys()))
            bedrag = st.number_input("Aantal", value=100)
            if st.button("Geef Munten"):
                st.session_state.db['saldi'][target] = st.session_state.db['saldi'].get(target, 0) + bedrag
                sla_db_op()
                st.success(f"{bedrag} munten naar {target}!")
