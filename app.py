import streamlit as st
import random
from datetime import datetime
from openai import OpenAI
import json
import os

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v7.0"
MODEL_NAAM = "llama-3.1-8b-instant"
DB_FILE = "database.json"
AI_PUNT_PRIJS = 1000
COOLDOWN_SECONDS = 60

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DATABASE MOTOR (ECHTE BESTANDS-OPSLAG) ---
def laad_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # Default data als bestand niet bestaat of corrupt is
    return {
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

def sla_db_op():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, indent=4)

# Initialiseer database in sessie
if 'db' not in st.session_state:
    st.session_state.db = laad_db()

# Sessie-variabelen voor UI (worden niet opgeslagen in DB)
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'last_ai_call' not in st.session_state: st.session_state.last_ai_call = {}
if 'ai_antwoord_temp' not in st.session_state: st.session_state.ai_antwoord_temp = ""
if 'huidig_oefenwoord' not in st.session_state: st.session_state.huidig_oefenwoord = None

# --- 3. LOGIN SYSTEEM ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    t1, t2 = st.tabs(["Inloggen", "Nieuw Account"])
    
    with t1:
        u_in = st.text_input("Naam").lower().strip()
        p_in = st.text_input("Wachtwoord", type="password")
        if st.button("Inloggen", type="primary"):
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
        if st.button("Account aanmaken"):
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
        <div style="text-align:center; padding:100px;">
            <h1 style="color:red; font-size:100px;">🚫</h1>
            <h1>Systeem is op slot</h1>
            <p style="font-size:20px;">{st.session_state.db['lockdown_msg']}</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Log uit"):
        st.session_state.ingelogd = False
        st.rerun()
    st.stop()

# --- 5. SIDEBAR & METRICS ---
st.sidebar.title(f"👋 {mijn_naam.capitalize()}")
with st.sidebar:
    c1, c2 = st.columns(2)
    c1.metric("💰 Munten", st.session_state.db['saldi'].get(mijn_naam, 0))
    c2.metric("💎 AI", st.session_state.db['ai_points'].get(mijn_naam, 0))
    st.divider()

menu = ["🏫 De Klas", "💬 Chat", "🤖 AI Hulp", "🇫🇷 Frans Lab"]
if is_teacher: menu.append("👩‍🏫 Leraar Paneel")
if is_admin: menu.append("👑 Admin Panel")
nav = st.sidebar.radio("Navigatie", menu)

if st.sidebar.button("Uitloggen", use_container_width=True):
    st.session_state.ingelogd = False
    st.rerun()

# --- 6. PAGINA'S ---

if nav == "🏫 De Klas":
    st.title("🏫 Klaslokaal")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Openstaande Taken")
        if not st.session_state.db['tasks']: st.info("Geen huiswerk!")
        for t in st.session_state.db['tasks']:
            with st.container(border=True):
                st.markdown(f"### {t['title']}")
                st.write(t['desc'])
    with col2:
        st.subheader("📚 Beschikbare Lijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            with st.container(border=True):
                st.write(f"📂 **{v['title']}**")
                if st.button(f"Downloaden naar Lab", key=f"dl_{i}"):
                    if mijn_naam not in st.session_state.db['user_vocab']: st.session_state.db['user_vocab'][mijn_naam] = {}
                    st.session_state.db['user_vocab'][mijn_naam].update(v['words'])
                    sla_db_op()
                    st.toast("Toegevoegd aan Frans Lab!")

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    chat_container = st.container(height=500, border=True)
    with chat_container:
        for m in st.session_state.db['chat_messages']:
            with st.chat_message("user"):
                st.write(f"**{m['user'].capitalize()}**: {m['text']}")
    if p := st.chat_input("Typ een bericht..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op()
        st.rerun()

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    vraag = st.text_area("Stel je vraag:")
    if st.button("Vraag AI (-1 punt)"):
        # AI logic hier (OpenAI aanroep zoals voorheen)
        st.session_state.ai_antwoord_temp = "AI-functie is actief. (Zorg voor je API-key in Secrets)"
        st.rerun()
    if st.session_state.ai_antwoord_temp:
        st.info(st.session_state.ai_antwoord_temp)

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    mijn_w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    tab1, tab2 = st.tabs(["🎮 Oefenen", "➕ Toevoegen"])
    with tab1:
        if mijn_w:
            if not st.session_state.huidig_oefenwoord:
                st.session_state.huidig_oefenwoord = random.choice(list(mijn_w.keys()))
            vraag = st.session_state.huidig_oefenwoord
            st.subheader(f"Vertaal: {vraag}")
            gok = st.text_input("Antwoord:")
            if st.button("Check"):
                if gok.lower().strip() == mijn_w[vraag].lower().strip():
                    st.success("Helemaal goed! +50 munten")
                    st.session_state.db['saldi'][mijn_naam] += 50
                    st.session_state.huidig_oefenwoord = random.choice(list(mijn_w.keys()))
                    sla_db_op()
                    st.rerun()
                else: st.error("Niet juist, probeer het nog eens.")
        else: st.warning("Download eerst een lijst in 'De Klas'.")
    with tab2:
        nl_w = st.text_input("Woord (NL)")
        fr_w = st.text_input("Vertaling (FR)")
        if st.button("Sla op"):
            if mijn_naam not in st.session_state.db['user_vocab']: st.session_state.db['user_vocab'][mijn_naam] = {}
            st.session_state.db['user_vocab'][mijn_naam][nl_w] = fr_w
            sla_db_op()
            st.success("Opgeslagen!")

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Leraar Paneel")
    
    t1, t2, t3 = st.tabs(["🔑 Klascodes", "📝 Taken", "📚 Woordenlijsten"])
    
    with t1:
        st.subheader("Huidige Klascodes")
        for code, klas in st.session_state.db['klascodes'].items():
            st.write(f"🔹 **{code}** -> {klas}")
        st.divider()
        n_code = st.text_input("Nieuwe Code")
        n_klas = st.text_input("Klas Naam (bv. 1B)")
        if st.button("Voeg Code Toe"):
            st.session_state.db['klascodes'][n_code] = n_klas
            sla_db_op()
            st.success("Code toegevoegd!")
            st.rerun()
            
    with t2:
        t_title = st.text_input("Taak Titel")
        t_desc = st.text_area("Taak Uitleg")
        if st.button("Post Taak"):
            st.session_state.db['tasks'].append({"title": t_title, "desc": t_desc})
            sla_db_op()
            st.success("Taak staat in de klas!")

    with t3:
        l_title = st.text_input("Lijst Titel")
        l_data = st.text_area("Woorden (nl=fr per regel)")
        if st.button("Deel Lijst"):
            d = {}
            for line in l_data.split("\n"):
                if "=" in line:
                    k, v = line.split("=")
                    d[k.strip()] = v.strip()
            st.session_state.db['vocab_lists'].append({"title": l_title, "words": d})
            sla_db_op()
            st.success("Gedeeld!")

elif nav == "👑 Admin Panel":
    st.title("👑 Admin Control")
    with st.container(border=True):
        st.subheader("🚨 Lockdown")
        l_msg = st.text_input("Bericht", value=st.session_state.db['lockdown_msg'])
        if st.button("Switch Lockdown Status"):
            st.session_state.db['lockdown'] = not st.session_state.db['lockdown']
            st.session_state.db['lockdown_msg'] = l_msg
            sla_db_op()
            st.rerun()
        st.write("Status:", "🔴 ACTIEF" if st.session_state.db['lockdown'] else "🟢 UIT")

    with st.container(border=True):
        st.subheader("💰 Economie")
        target = st.selectbox("Gebruiker", list(st.session_state.db['users'].keys()))
        bedrag = st.number_input("Munten geven/afnemen", value=100)
        if st.button("Bevestig Transactie"):
            st.session_state.db['saldi'][target] = st.session_state.db['saldi'].get(target, 0) + bedrag
            sla_db_op()
            st.success(f"Saldo van {target} nu: {st.session_state.db['saldi'][target]}")
                st.success(f"{amount} munten naar {target} gestuurd! Nieuw saldo: {st.session_state.db['saldi'][target]}")

    with st.container(border=True):
        st.subheader("🧹 Database Opschonen")
        if st.button("Verwijder alle Chat & Taken"):
            st.session_state.db['chat_messages'] = []
            st.session_state.db['tasks'] = []
            sla_db_op()
            st.success("Schoon!")
