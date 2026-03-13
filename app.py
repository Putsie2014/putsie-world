import streamlit as st
import random
from datetime import datetime
import json
import os
# We gebruiken de Groq client voor de snelle Llama modellen
try:
    from groq import Groq
except ImportError:
    st.error("Installeer groq: pip install groq")

# --- 1. CONFIGURATIE & PADEN ---
SITE_TITLE = "Putsie EDUCATION 🎓 v9.0"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000 # Munten per AI punt

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- 2. DE DATABASE MOTOR (BULLETPROOF) ---
def laad_db():
    basis_db = {
        "users": {"elliot": {"pw": "Putsie", "role": "admin"}, "annelies": {"pw": "JufAnnelies", "role": "teacher"}},
        "saldi": {"elliot": 10000},
        "ai_points": {"elliot": 10},
        "user_vocab": {"elliot": {}},
        "chat_messages": [],
        "vocab_lists": [],
        "tasks": [],
        "klascodes": {"Putsie2024": "Klas 1A"},
        "lockdown": False,
        "lockdown_msg": "Systeem onderhoud door Elliot"
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except: return basis_db
    return basis_db

def sla_db_op():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = laad_db()

# --- 3. LOGIN SYSTEEM ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title(SITE_TITLE)
        t_log, t_reg = st.tabs(["🔑 Inloggen", "📝 Registreren"])
        with t_log:
            u = st.text_input("Gebruikersnaam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Inloggen", type="primary", use_container_width=True):
                # Hardcoded admin bypass
                if u == "elliot" and p == "Putsie":
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"
                    st.rerun()
                elif u in st.session_state.db['users'] and st.session_state.db['users'][u]["pw"] == p:
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, u, st.session_state.db['users'][u]["role"]
                    st.rerun()
                else: st.error("Fout!")
        with t_reg:
            nu, np, kc = st.text_input("Nieuwe Naam"), st.text_input("Wachtwoord ", type="password"), st.text_input("Klascode")
            if st.button("Maak Account", use_container_width=True):
                if kc in st.session_state.db['klascodes'] and nu:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                    st.session_state.db['saldi'][nu], st.session_state.db['ai_points'][nu] = 0, 5
                    st.session_state.db['user_vocab'][nu] = {}
                    sla_db_op()
                    st.success("Klaar! Log nu in.")
    st.stop()

# --- 4. NAVIGATIE & SIDEBAR ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"

with st.sidebar:
    st.header(f"👤 {mijn_naam.capitalize()}")
    c1, c2 = st.columns(2)
    c1.metric("🪙", st.session_state.db['saldi'].get(mijn_naam, 0))
    c2.metric("💎", st.session_state.db['ai_points'].get(mijn_naam, 0))
    menu = ["🏫 Klas", "💬 Chat", "🇫🇷 Frans Lab", "🤖 AI Hulp"]
    if is_teacher: menu.append("👩‍🏫 Leraar")
    if is_admin: menu.append("👑 Admin")
    nav = st.radio("Menu", menu)
    if st.button("🚪 Uitloggen"):
        st.session_state.ingelogd = False
        st.rerun()

# --- 5. PAGINA LOGICA ---

if nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.write("Vraag hulp bij Frans, Wiskunde of andere vakken.")
    
    # AI Punten beheer
    col_a, col_b = st.columns([2, 1])
    with col_b:
        with st.container(border=True):
            st.write("🛒 **Winkel**")
            st.caption(f"1 💎 = {AI_PUNT_PRIJS} 🪙")
            if st.button("Koop 1 AI Punt"):
                if st.session_state.db['saldi'].get(mijn_naam, 0) >= AI_PUNT_PRIJS:
                    st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
                    st.session_state.db['ai_points'][mijn_naam] = st.session_state.db['ai_points'].get(mijn_naam, 0) + 1
                    sla_db_op(); st.rerun()
                else: st.error("Niet genoeg munten!")

    with col_a:
        vraag = st.text_area("Stel je vraag aan de AI leraar:", placeholder="Hoe vervoeg ik 'Être'?")
        if st.button("Stel Vraag (-1 💎)", type="primary"):
            if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
                try:
                    # AI AANROEP (Groq)
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    completion = client.chat.completions.create(
                        model=MODEL_NAAM,
                        messages=[
                            {"role": "system", "content": "Je bent een vriendelijke leraar die leerlingen helpt met korte, duidelijke uitleg."},
                            {"role": "user", "content": vraag}
                        ]
                    )
                    antwoord = completion.choices[0].message.content
                    st.session_state.db['ai_points'][mijn_naam] -= 1
                    sla_db_op()
                    st.session_state.laatste_ai_antwoord = antwoord
                except Exception as e:
                    st.error(f"AI Fout: Zorg dat de GROQ_API_KEY in Streamlit Secrets staat. Fout: {e}")
            else:
                st.warning("Je hebt geen AI punten meer! Koop er een paar in de winkel hiernaast.")

        if 'laatste_ai_antwoord' in st.session_state:
            with st.container(border=True):
                st.markdown("**Antwoord van de leraar:**")
                st.write(st.session_state.laatste_ai_antwoord)

elif nav == "💬 Chat":
    st.title("💬 Klas Chat")
    with st.container(height=400, border=True):
        for m in st.session_state.db['chat_messages']:
            st.markdown(f"**{m['user'].capitalize()}**: {m['text']}")
    if p := st.chat_input("Bericht..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p})
        sla_db_op(); st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    w_dict = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if not w_dict: st.info("Geen woorden.")
    else:
        # We kiezen een woord dat we opslaan in de sessie zodat het niet verandert bij typen
        if 'oefen_w' not in st.session_state: st.session_state.oefen_w = random.choice(list(w_dict.keys()))
        st.subheader(f"Vertaal: {st.session_state.oefen_w}")
        gok = st.text_input("Antwoord")
        if st.button("Check"):
            if gok.lower().strip() == w_dict[st.session_state.oefen_w].lower().strip():
                st.success("Goed! +50 munten"); st.session_state.db['saldi'][mijn_naam] += 50
                del st.session_state.oefen_w; sla_db_op(); st.rerun()
            else: st.error("Helaas!")

elif nav == "🏫 Klas":
    st.title("🏫 De Klas")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Taken")
        for t in st.session_state.db['tasks']:
            with st.container(border=True):
                st.write(f"**{t['title']}**\n\n{t['desc']}")
    with c2:
        st.subheader("📚 Lijsten")
        for i, v in enumerate(st.session_state.db['vocab_lists']):
            if st.button(f"Download {v['title']}", key=i):
                st.session_state.db['user_vocab'].setdefault(mijn_naam, {}).update(v['words'])
                sla_db_op(); st.toast("Gedownload!")

elif nav == "👩‍🏫 Leraar":
    st.title("👩‍🏫 Leraar Paneel")
    t1, t2, t3 = st.tabs(["Codes", "Taken", "Woorden"])
    with t1:
        st.write(st.session_state.db['klascodes'])
        nc, nk = st.text_input("Code"), st.text_input("Klas")
        if st.button("Voeg toe"):
            st.session_state.db['klascodes'][nc] = nk; sla_db_op(); st.rerun()
    with t2:
        tt, td = st.text_input("Titel"), st.text_area("Uitleg")
        if st.button("Post"):
            st.session_state.db['tasks'].append({"title": tt, "desc": td}); sla_db_op()
    with t3:
        lt, lw = st.text_input("Naam"), st.text_area("nl=fr")
        if st.button("Deel"):
            d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in lw.split("\n") if "=" in l}
            st.session_state.db['vocab_lists'].append({"title": lt, "words": d}); sla_db_op()

elif nav == "👑 Admin":
    st.title("👑 Admin Control Room")
    t_eco, t_raw = st.tabs(["💰 Economie", "⚙️ Database"])
    with t_eco:
        doel = st.selectbox("Wie?", list(st.session_state.db['users'].keys()))
        m_aantal = st.number_input("Munten", value=100)
        if st.button("Geef Munten"):
            st.session_state.db['saldi'][doel] = st.session_state.db['saldi'].get(doel, 0) + m_aantal
            sla_db_op(); st.success("Gedaan!")
    with t_raw:
        raw = st.text_area("RAW JSON", value=json.dumps(st.session_state.db, indent=4), height=400)
        if st.button("Overschrijf"):
            st.session_state.db = json.loads(raw); sla_db_op(); st.rerun()
