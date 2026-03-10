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
        .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: white; }
        [data-testid="stVerticalBlockBorderWrapper"] { 
            background: rgba(255, 255, 255, 0.05) !important; 
            backdrop-filter: blur(15px) !important; 
            border-radius: 20px !important; 
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 25px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4) !important;
        }
        .stButton > button { 
            border-radius: 12px !important; 
            background: linear-gradient(45deg, #00dbde 0%, #fc00ff 100%) !important;
            color: white !important; font-weight: 800 !important;
            transition: 0.4s !important;
        }
        .stButton > button:hover { transform: scale(1.05) !important; box-shadow: 0 0 20px rgba(0, 219, 222, 0.6) !important; }
        .delete-btn > button { background: linear-gradient(45deg, #ff4b1f 0%, #ff9068 100%) !important; }
    </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 2. DATABASE ARCHITECTUUR ---
def laad_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "klassen": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
            db.setdefault("klassen", {}); db.setdefault("users", {})
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
    c1, c2, c3 = st.columns(3)
    c1.metric("Geld", f"€{data.get('geld', 0)}")
    c2.metric("Taken voltooid", len(data.get("voltooide_taken", [])))
    c3.metric("Status", "Pro Gamer" if data.get("geld", 0) > 1000 else "Starter")

elif nav == "📚 Frans Lab":
    st.title("🧪 Frans Woorden Lab")
    t1, t2 = st.tabs(["🎯 Quiz Mode", "🧪 Woorden toevoegen"])
    with t1:
        cat = st.selectbox("Categorie", ["woorden", "werkwoorden"])
        w_dict = data.get("woorden", {}).get(cat, {})
        if st.button("Nieuwe Vraag 🎲"):
            if w_dict: st.session_state.quiz_q = random.choice(list(w_dict.keys()))
            else: st.warning("Voeg eerst woorden toe!")
        if 'quiz_q' in st.session_state:
            st.subheader(f"Vertaal: {st.session_state.quiz_q}")
            ans = st.text_input("Antwoord:")
            if st.button("Check ✔️"):
                if ans.lower().strip() == w_dict[st.session_state.quiz_q].lower().strip():
                    data["geld"] += 15; db["users"][user] = data; sla_db_op(db)
                    st.toast("Correct! +€15"); del st.session_state.quiz_q; st.rerun()
                else: st.error("Niet juist!")
    with t2:
        colA, colB = st.columns(2)
        type_w = colA.radio("Type", ["woorden", "werkwoorden"])
        f_w = colA.text_input("Frans"); n_w = colB.text_input("Nederlands")
        if st.button("Opslaan 💾"):
            if f_w and n_w:
                data.setdefault("woorden", {}).setdefault(type_w, {})[f_w] = n_w
                db["users"][user] = data; sla_db_op(db); st.success("Opgeslagen!")

elif nav == "🏫 Het Klaslokaal":
    st.title("🏫 Putsie Klaslokaal")
    
    if user.lower() in LEERKRACHTEN:
        mijn_klas_code = next((c for c, i in db["klassen"].items() if i.get("docent") == user), None)
        
        if not mijn_klas_code:
            k_naam = st.text_input("Naam van je nieuwe klas")
            if st.button("Bouw Klas ✨"):
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                db["klassen"][code] = {"naam": k_naam, "docent": user, "taken": []}
                sla_db_op(db); st.rerun()
        else:
            klas_info = db["klassen"][mijn_klas_code]
            st.success(f"Beheer: **{klas_info.get('naam')}** | Code: `{mijn_klas_code}`")
            
            admin_tab1, admin_tab2, admin_tab3 = st.tabs(["📝 Taken Beheren", "👥 Leerlingen", "⚙️ Klasinstellingen"])
            
            with admin_tab1:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("#### ➕ Nieuwe Taak")
                    q = st.text_input("Vraag"); a = st.text_input("Antwoord"); g = st.number_input("Beloning", 10, 500, 20)
                    if st.button("Plaats Taak 🚀"):
                        klas_info.setdefault("taken", []).append({"vraag": q, "antwoord": a, "beloning": g})
                        sla_db_op(db); st.rerun()
                with c2:
                    st.markdown("#### 📋 Actieve Taken")
                    for i, t in enumerate(klas_info.get("taken", [])):
                        st.write(f"{i+1}. {t.get('vraag')} (€{t.get('beloning')})")
                    if st.button("🗑️ Wis alle taken"):
                        klas_info["taken"] = []; sla_db_op(db); st.rerun()

            with admin_tab2:
                st.markdown("#### 👥 Leerlingen in deze klas")
                leerlingen = [u for u, d in db["users"].items() if d.get("klas_id") == mijn_klas_code]
                if not leerlingen:
                    st.info("Er zijn nog geen leerlingen aangemeld.")
                else:
                    for l_naam in leerlingen:
                        col_l1, col_l2 = st.columns([3, 1])
                        col_l1.write(f"👤 **{l_naam.capitalize()}**")
                        if col_l2.button(f"Verwijder {l_naam}", key=f"del_{l_naam}"):
                            db["users"][l_naam]["klas_id"] = None
                            db["users"][l_naam]["voltooide_taken"] = []
                            sla_db_op(db); st.toast(f"{l_naam} verwijderd!"); st.rerun()

            with admin_tab3:
                st.markdown("#### ⚙️ Klas aanpassen")
                nieuwe_naam = st.text_input("Nieuwe klasnaam", value=klas_info.get('naam'))
                if st.button("Naam Bijwerken 💾"):
                    db["klassen"][mijn_klas_code]["naam"] = nieuwe_naam
                    sla_db_op(db); st.success("Naam gewijzigd!"); st.rerun()
                
                st.markdown("---")
                if st.button("❗ VERWIJDER VOLLEDIGE KLAS", type="secondary"):
                    for l_naam in leerlingen:
                        db["users"][l_naam]["klas_id"] = None
                    del db["klassen"][mijn_klas_code]
                    sla_db_op(db); st.rerun()

    else: # LEERLING FLOW
        if not data.get("klas_id"):
            c_in = st.text_input("Klascode:").upper()
            if st.button("Deelnemen 🚪"):
                if c_in in db["klassen"]:
                    data["klas_id"] = c_in; db["users"][user] = data; sla_db_op(db); st.rerun()
                else: st.error("Code onjuist!")
        else:
            klas = db["klassen"].get(data["klas_id"], {})
            st.subheader(f"🎒 Klas: {klas.get('naam', 'Onbekend')}")
            for i, t in enumerate(klas.get("taken", [])):
                is_done = i in data.get("voltooide_taken", [])
                c1, c2 = st.columns([3, 1])
                c1.write(f"{'✅' if is_done else '📝'} {t.get('vraag')}")
                if not is_done and c2.button("Start", key=f"st_{i}"):
                    st.session_state.active_task = {"idx": i, "data": t}
            
            if 'active_task' in st.session_state:
                at = st.session_state.active_task
                ans = st.text_input(f"Antwoord op: {at['data'].get('vraag')}")
                if st.button("Indienen ✔️"):
                    if ans.lower().strip() == at['data'].get('antwoord', '').lower().strip():
                        data["geld"] += at['data'].get('beloning', 0)
                        data.setdefault("voltooide_taken", []).append(at['idx'])
                        db["users"][user] = data; sla_db_op(db); del st.session_state.active_task; st.balloons(); st.rerun()
                    else: st.error("Fout!")

elif nav == "🎮 Game Arcade":
    st.title("👾 Arcade")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Alien Shooter 🛸"):
            if random.random() > 0.5: data["geld"] += 2; sla_db_op(db); st.toast("RAAK!")
            else: st.toast("MIS!")
    with c2:
        st.markdown('<div style="height:40px; width:40px; background:orange; border-radius:50%; animation: bounce 0.4s infinite alternate;"></div><style>@keyframes bounce { from {margin-top:0px;} to {margin-top:40px;} }</style>', unsafe_allow_html=True)
        if st.button("Collect Energy 🏀"): data["geld"] += 1; sla_db_op(db); st.toast("Power up!")
