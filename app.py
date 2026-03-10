import streamlit as st
import json
import os
import random
import string

# --- 1. CONFIGURATIE & ULTRA STYLING ---
DB_FILE = "database.json"
LEERKRACHTEN = ["elliot", "annelies", "admin"]
st.set_page_config(page_title="Putsie Studios", page_icon="🌍", layout="wide")

def apply_custom_styles():
    st.markdown("""
    <style>
        /* Deep Galaxy Background */
        .stApp { 
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); 
            color: white; 
        }
        
        /* Glassmorphism Containers */
        [data-testid="stVerticalBlockBorderWrapper"] { 
            background: rgba(255, 255, 255, 0.05) !important; 
            backdrop-filter: blur(15px) !important; 
            border-radius: 20px !important; 
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 25px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
            transition: 0.3s ease-in-out;
        }
        
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }

        /* Neon Buttons */
        .stButton > button { 
            border-radius: 12px !important; 
            background: linear-gradient(45deg, #00dbde 0%, #fc00ff 100%) !important;
            color: white !important;
            border: none !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: 0.4s !important;
            padding: 10px 24px !important;
        }
        
        .stButton > button:hover { 
            box-shadow: 0 0 20px rgba(0, 219, 222, 0.6) !important;
            transform: scale(1.05) !important;
        }

        /* Input fields */
        input { 
            background-color: rgba(0,0,0,0.2) !important; 
            color: white !important; 
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 2. DATABASE ARCHITECTUUR ---
def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            if "klassen" not in db: db["klassen"] = {}
            if "users" not in db: db["users"] = {}
            return db
    except: return {"users": {}, "klassen": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

# --- 3. TOEGANGSCONTROLE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title("🌌 Putsie Studios: Login")
    db = laad_db()
    t1, t2 = st.tabs(["🚀 Inloggen", "📝 Nieuw Account"])
    with t1:
        u = st.text_input("Gebruikersnaam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Start Adventure"):
            if u in db["users"] and db["users"][u].get("password") == p:
                st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
            else: st.error("Inloggegevens onjuist!")
    with t2:
        ru = st.text_input("Kies Naam", key="r_u").lower().strip()
        rp = st.text_input("Kies Wachtwoord", type="password", key="r_p")
        if st.button("Account Aanmaken"):
            if ru and rp and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "klas_id": None, "voltooide_taken": [], "woorden": {"woorden": {}, "werkwoorden": {}}}
                sla_db_op(db); st.success("Welkom! Log nu in."); st.balloons()
    st.stop()

# --- 4. DATA SYNCHRONISATIE ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 0, "woorden": {"woorden": {}, "werkwoorden": {}}})

with st.sidebar:
    st.title(f"👾 {user.capitalize()}")
    st.metric("SALDO", f"€{data.get('geld', 0)}")
    st.markdown("---")
    nav = st.radio("NAVIGATIE", ["🏠 Home", "📚 Frans Lab", "🏫 Het Klaslokaal", "🎮 Game Arcade"])
    if st.button("🚪 Log uit"): st.session_state.clear(); st.rerun()

# --- 5. PAGINA'S ---

if nav == "🏠 Home":
    st.title(f"Welkom in de Studio, {user.capitalize()}!")
    with st.container():
        st.markdown("### 📈 Jouw Status")
        c1, c2, c3 = st.columns(3)
        c1.metric("Geld", f"€{data.get('geld', 0)}")
        c2.metric("Taken afgerond", len(data.get("voltooide_taken", [])))
        c3.metric("Rangen", "Goud" if data.get("geld", 0) > 500 else "Zilver")

elif nav == "📚 Frans Lab":
    st.title("🧪 Frans Woorden Lab")
    t1, t2 = st.tabs(["🎯 Quiz Mode", "🧪 Voeg woorden toe"])
    with t1:
        cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
        w_dict = data.get("woorden", {}).get(cat, {})
        if st.button("Nieuwe Vraag 🎲"):
            if w_dict: st.session_state.quiz_q = random.choice(list(w_dict.keys()))
            else: st.warning("Voeg eerst woorden toe in het andere tabblad!")
        if 'quiz_q' in st.session_state:
            st.subheader(f"Vertaal: {st.session_state.quiz_q}")
            ans = st.text_input("Antwoord:")
            if st.button("Check ✔️"):
                if ans.lower().strip() == w_dict[st.session_state.quiz_q].lower().strip():
                    data["geld"] += 15; db["users"][user] = data; sla_db_op(db)
                    st.toast("Lekker hoor! +€15"); del st.session_state.quiz_q; st.rerun()
                else: st.error("Helaas! Probeer het opnieuw.")
    with t2:
        colA, colB = st.columns(2)
        type_w = colA.radio("Type", ["woorden", "werkwoorden"])
        f_w = colA.text_input("Frans"); n_w = colB.text_input("Nederlands")
        if st.button("Opslaan in Lab 💾"):
            if f_w and n_w:
                data.setdefault("woorden", {}).setdefault(type_w, {})[f_w] = n_w
                db["users"][user] = data; sla_db_op(db); st.success("Woord opgeslagen!")

elif nav == "🏫 Het Klaslokaal":
    st.title("🏫 Putsie Klaslokaal")
    
    # ADMIN GEDEELTE
    if user.lower() in LEERKRACHTEN:
        st.markdown("### 🛠️ Leerkracht Dashboard (ADMIN)")
        mijn_klas = next((c for c, i in db["klassen"].items() if i.get("docent") == user), None)
        
        if not mijn_klas:
            with st.container():
                st.write("Je hebt nog geen klas. Laten we er een bouwen!")
                k_naam = st.text_input("Naam van je klas")
                if st.button("Bouw Klas ✨"):
                    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                    db["klassen"][code] = {"naam": k_naam, "docent": user, "taken": []}
                    sla_db_op(db); st.rerun()
        else:
            klas_info = db["klassen"][mijn_klas]
            st.success(f"Actieve Klas: **{klas_info.get('naam')}** | Code: `{mijn_klas}`")
            
            c1, c2 = st.columns(2)
            with c1:
                with st.container():
                    st.markdown("#### ➕ Nieuwe Taak")
                    q = st.text_input("Vraag"); a = st.text_input("Antwoord"); g = st.number_input("Beloning", 10, 500, 20)
                    if st.button("Taak de wereld in sturen 🚀"):
                        klas_info.setdefault("taken", []).append({"vraag": q, "antwoord": a, "beloning": g})
                        sla_db_op(db); st.success("Taak geplaatst!"); st.rerun()
            with c2:
                with st.container():
                    st.markdown("#### 📋 Overzicht Taken")
                    for i, t in enumerate(klas_info.get("taken", [])):
                        st.write(f"**{i+1}.** {t.get('vraag')} ➔ *{t.get('antwoord')}* (€{t.get('beloning')})")
                    if st.button("Verwijder alle taken 🗑️"):
                        klas_info["taken"] = []; sla_db_op(db); st.rerun()

    # LEERLING GEDEELTE
    else:
        if not data.get("klas_id"):
            with st.container():
                st.write("Je bent nog geen lid van een klas.")
                c_in = st.text_input("Voer de geheime klascode in:").upper()
                if st.button("Betreed Klas 🚪"):
                    if c_in in db["klassen"]:
                        data["klas_id"] = c_in; db["users"][user] = data; sla_db_op(db)
                        st.balloons(); st.rerun()
                    else: st.error("Code niet gevonden!")
        else:
            klas = db["klassen"].get(data["klas_id"], {})
            st.subheader(f"🎒 Klas: {klas.get('naam', 'Onbekend')}")
            
            taken = klas.get("taken", [])
            if not taken:
                st.info("De leerkracht heeft nog geen taken geplaatst. Relax-tijd! 😎")
            else:
                for i, t in enumerate(taken):
                    is_done = i in data.get("voltooide_taken", [])
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        col1.markdown(f"**{'✅' if is_done else '📝'} {t.get('vraag', 'Geen vraag')}**")
                        if not is_done:
                            if col2.button("Start", key=f"t_{i}"):
                                st.session_state.active_task = {"idx": i, "data": t}
                        else: col2.write("Voltooid!")
                
                if 'active_task' in st.session_state:
                    st.markdown("---")
                    at = st.session_state.active_task
                    st.subheader(f"Beantwoord: {at['data'].get('vraag')}")
                    leerling_ans = st.text_input("Jouw antwoord op de taak:")
                    if st.button("Taak Inleveren ✔️"):
                        if leerling_ans.lower().strip() == at['data'].get('antwoord', '').lower().strip():
                            data["geld"] += at['data'].get('beloning', 0)
                            data.setdefault("voltooide_taken", []).append(at['idx'])
                            db["users"][user] = data; sla_db_op(db)
                            del st.session_state.active_task
                            st.balloons(); st.success("Geld verdiend!"); st.rerun()
                        else: st.error("Dat is niet het juiste antwoord!")

elif nav == "🎮 Game Arcade":
    st.title("👾 Putsie Game Arcade")
    st.write("Zet je verstand op nul en verdien een beetje extra.")
    c1, c2 = st.columns(2)
    with c1:
        with st.container():
            st.subheader("Alien Clicker 🛸")
            if st.button("SCHIET! 💥"):
                if random.random() > 0.4:
                    data["geld"] += 2; db["users"][user] = data; sla_db_op(db); st.toast("RAAK! +€2")
                else: st.toast("MIS! 💨")
    with c2:
        with st.container():
            st.subheader("Neon Bouncer 🏀")
            st.markdown('<div style="height:40px; width:40px; background:linear-gradient(to bottom, #00dbde, #fc00ff); border-radius:50%; animation: bounce 0.4s infinite alternate; box-shadow: 0 0 15px #00dbde;"></div><style>@keyframes bounce { from {margin-top:0px;} to {margin-top:40px;} }</style>', unsafe_allow_html=True)
            if st.button("Power-up Pakken"):
                data["geld"] += 1; db["users"][user] = data; sla_db_op(db); st.toast("Energy +1")
