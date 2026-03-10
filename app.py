import streamlit as st
import json
import os
import random
import string

# --- CONFIGURATIE ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]

# Maak de pagina breder en geef een leuk icoontje mee
st.set_page_config(page_title="Putsie Studios", page_icon="🌍", layout="wide")

# --- CUSTOM CSS VOOR EEN HIGH-END LOOK ---
def voeg_custom_css_toe():
    st.markdown("""
    <style>
    /* Zachte gradient achtergrond */
    .stApp {
        background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
    }
    
    /* Mooie witte kaders met schaduw en ronde hoeken */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s;
    }
    
    /* Zweef-effect voor de kaders */
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15) !important;
    }
    
    /* Knoppen ronder en interactiever maken */
    .stButton > button {
        border-radius: 25px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    
    /* Knop animatie bij hover */
    .stButton > button:hover {
        transform: scale(1.05) translateY(-2px) !important;
        box-shadow: 0 7px 14px rgba(0,0,0,0.2) !important;
    }
    
    /* Titels wat dikker maken */
    h1, h2, h3 {
        font-family: 'Trebuchet MS', sans-serif !important;
        color: #2c3e50 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Activeer de styling direct
voeg_custom_css_toe()

# --- DATABASE FUNCTIES ---
def laad_db():
    if not os.path.exists(DB_FILE): 
        return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: 
            return json.load(f)
    except: 
        return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: 
        json.dump(db, f, indent=4)

# --- LOGIN & REGISTRATIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    with st.container():
        st.title("🌍 Welkom bij Putsie Studios")
        st.write("Log in of maak een account aan om je avontuur te beginnen!")
    
    db = laad_db()
    
    tab1, tab2 = st.tabs(["🔐 Inloggen", "📝 Account aanmaken"])
    
    with tab1:
        u = st.text_input("Naam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Log in 🚀", type="primary"):
            if u in db["users"] and db["users"][u].get("password") == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.toast(f"Welkom terug, {u.capitalize()}!", icon="👋")
                st.rerun()
            else: 
                st.error("Foutieve naam of wachtwoord!")
                
    with tab2:
        ru = st.text_input("Kies een Naam", key="r_u").lower().strip()
        rp = st.text_input("Kies een Wachtwoord", type="password", key="r_p")
        if st.button("Maak Account ✨", type="primary"):
            if not ru or not rp:
                st.warning("Vul beide velden in!")
            elif ru in db["users"]:
                st.error("Deze naam bestaat al!")
            else:
                db["users"][ru] = {
                    "password": rp, 
                    "geld": 100, 
                    "klas_id": None, 
                    "voltooide_taken": [],
                    "woorden": {"woorden": {}, "werkwoorden": {}}
                }
                sla_db_op(db)
                st.balloons()
                st.success("Account succesvol aangemaakt! Je kunt nu inloggen via het andere tabblad.")
    st.stop()

# --- APP DATA LADEN ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 100, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}})

with st.sidebar:
    st.header(f"👤 {user.capitalize()}")
    st.metric("💰 Jouw Saldo", f"€{data.get('geld', 0)}")
    st.markdown("---")
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden", use_container_width=True): st.session_state.page = "Frans"
    if st.button("🏫 Klaslokaal", use_container_width=True): st.session_state.page = "Klas"
    st.markdown("---")
    if st.button("🚪 Uitloggen", use_container_width=True): st.session_state.clear(); st.rerun()

# --- PAGINA LOGICA ---
page = st.session_state.get("page", "Home")

if page == "Frans":
    st.title("🎓 Frans & Werkwoorden")
    st.write("Oefen hier je eigen woordenlijsten of voeg nieuwe toe.")
    
    t1, t2 = st.tabs(["🎯 Oefen Quiz", "➕ Woorden Toevoegen"])
    with t1:
        cat = st.selectbox("Wat wil je oefenen?", ["woorden", "werkwoorden"])
        if st.button("Genereer Nieuwe Vraag 🎲", type="primary"):
            if data["woorden"][cat]:
                st.session_state.vraag = random.choice(list(data["woorden"][cat].keys()))
            else:
                st.warning(f"Je hebt nog geen {cat} toegevoegd! Ga naar het andere tabblad.")
                
        if 'vraag' in st.session_state:
            with st.container(border=True):
                st.subheader(f"Vertaal: **{st.session_state.vraag}**")
                ans = st.text_input("Jouw antwoord:")
                if st.button("Controleer ✔️"):
                    correct_antwoord = data["woorden"][cat].get(st.session_state.vraag, "")
                    if ans.lower().strip() == correct_antwoord.lower().strip():
                        data["geld"] += 10
                        db["users"][user] = data
                        sla_db_op(db)
                        del st.session_state.vraag
                        st.toast("Correct! +€10", icon="🎉")
                        st.rerun()
                    else:
                        st.error("Helaas, probeer het nog eens! ❌")
    with t2:
        with st.container(border=True):
            st.markdown("### ✨ Voeg nieuwe vertalingen toe")
            soort = st.radio("Kies soort:", ["woorden", "werkwoorden"])
            f = st.text_input("Frans (of de vreemde taal):")
            n = st.text_input("Nederlands (jouw taal):")
            if st.button("💾 Opslaan", type="primary"):
                if f and n:
                    data["woorden"][soort][f] = n
                    db["users"][user] = data
                    sla_db_op(db)
                    st.toast(f"Opgeslagen: {f} = {n}", icon="✅")
                    st.rerun()

elif page == "Klas":
    st.title("🏫 Putsie Klaslokaal")
    st.markdown("---")
    
    # ------------------ LEERKRACHT GEDEELTE ------------------
    if user.lower() in LEERKRACHTEN:
        mijn_klas_code = None
        mijn_klas_info = None
        for code, info in db["klassen"].items():
            if info.get("docent") == user:
                mijn_klas_code = code
                mijn_klas_info = info
                break
                
        if not mijn_klas_code:
            st.info("💡 Je hebt nog geen klas. Maak er hieronder eentje aan!")
            with st.container(border=True):
                naam = st.text_input("Hoe wil je jouw klas noemen?")
                if st.button("✨ Genereer Mijn Klas", type="primary", use_container_width=True):
                    if naam:
                        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                        db["klassen"][code] = {"naam": naam, "docent": user, "taken": []}
                        sla_db_op(db); st.rerun()
                    else:
                        st.warning("Vul een naam in!")
        else:
            st.subheader(f"🎒 Klas: **{mijn_klas_info.get('naam', 'Onbekend')}**")
            st.success(f"🔑 Jouw klascode is: **{mijn_klas_code}** (Deel deze met je leerlingen!)")
            
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.markdown("### ➕ Nieuwe taak maken")
                    q = st.text_input("Vraag (Wat moeten ze vertalen?):", key="new_q")
                    a = st.text_input("Antwoord (Exacte vertaling):", key="new_a")
                    b = st.number_input("Beloning (€):", value=20, min_value=1, key="new_b")
                    if st.button("Plaats Taak 🚀", type="primary", use_container_width=True):
                        if q and a:
                            if "taken" not in mijn_klas_info: mijn_klas_info["taken"] = []
                            mijn_klas_info["taken"].append({"vraag": q, "antwoord": a, "beloning": b})
                            sla_db_op(db); st.rerun()
                        else:
                            st.error("Vul zowel vraag als antwoord in!")
                            
            with col2:
                with st.container(border=True):
                    st.markdown("### 📋 Actieve Taken")
                    takenlijst = mijn_klas_info.get("taken", [])
                    if not takenlijst:
                        st.write("Je hebt nog geen taken geplaatst.")
                    for i, taak in enumerate(takenlijst):
                        v = taak.get("vraag", "Oude/kapotte taak")
                        ant = taak.get("antwoord", "?")
                        bel = taak.get("beloning", 0)
                        st.markdown(f"**{i+1}. {v}** ➔ *{ant}* (💰 €{bel})")

    # ------------------ LEERLING GEDEELTE ------------------
    else:
        if not data.get("klas_id"):
            st.info("👋 Je zit nog niet in een klas. Vraag je leerkracht om de code!")
            with st.container(border=True):
                c = st.text_input("Vul hier je 5-cijferige klascode in:").upper()
                if st.button("🚀 Deelnemen", type="primary", use_container_width=True):
                    if c in db["klassen"]:
                        data["klas_id"] = c
                        db["users"][user] = data
                        sla_db_op(db)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Oeps! Die code bestaat niet.")
        else:
            klas = db["klassen"].get(data["klas_id"], {})
            st.subheader(f"🎓 Welkom in: **{klas.get('naam', 'Onbekende Klas')}**")
            
            col1, col2 = st.columns([2, 1])
            taken = klas.get("taken", [])
            voltooide_taken = data.get("voltooide_taken", [])
            
            with col2:
                with st.container(border=True):
                    st.markdown("### 🏆 Jouw Stats")
                    st.metric("Verdiend met taken", f"€{data.get('geld', 0)}")
                    st.metric("Taken afgerond", f"{len(voltooide_taken)} / {len(taken)}")
            
            with col1:
                st.markdown("### 📋 Jouw Taken")
                if not taken:
                    st.info("Je leerkracht heeft nog geen taken toegevoegd. Lekker chillen! 🛋️")
                    
                for i, taak in enumerate(taken):
                    is_done = i in voltooide_taken
                    vraag_tekst = taak.get("vraag", "Onbekende vraag")
                    beloning_bedrag = taak.get("beloning", 0)
                    
                    with st.container(border=True):
                        colA, colB = st.columns([3, 1])
                        with colA:
                            st.markdown(f"**{'✅' if is_done else '📝'} {vraag_tekst}**")
                            if is_done:
                                st.caption("Voltooid! 🎉")
                            else:
                                st.caption(f"Verdien 💰 €{beloning_bedrag}")
                        with colB:
                            if not is_done:
                                if st.button("Start ▶️", key=f"start_{i}", type="primary", use_container_width=True):
                                    st.session_state.active = {"idx": i, "data": taak}
            
            if 'active' in st.session_state:
                st.markdown("---")
                t = st.session_state.active
                
                vraag_tekst = t['data'].get('vraag', 'Onbekende Vraag')
                antwoord_tekst = t['data'].get('antwoord', '')
                beloning_bedrag = t['data'].get('beloning', 0)
                
                st.subheader(f"✍️ Taak: Vertaal '{vraag_tekst}'")
                with st.container(border=True):
                    ans = st.text_input("Wat is de juiste vertaling?", key="ans_input")
                    if st.button("Check Antwoord ✔️", type="primary"):
                        if antwoord_tekst and ans.lower().strip() == antwoord_tekst.lower().strip():
                            data["geld"] = data.get("geld", 0) + beloning_bedrag
                            if "voltooide_taken" not in data: data["voltooide_taken"] = []
                            data["voltooide_taken"].append(t['idx'])
                            db["users"][user] = data
                            sla_db_op(db)
                            del st.session_state.active
                            st.balloons()
                            st.success(f"Super! Je hebt €{beloning_bedrag} verdiend! 🎊")
                        else:
                            st.error("Helaas, dat klopt niet. Probeer het nog eens! ❌")

else:
    with st.container(border=True):
        st.title("🏠 Welkom bij Putsie Studios!")
        st.write("Gebruik het menu aan de zijkant om te navigeren. Veel succes en plezier met leren! 🚀")
