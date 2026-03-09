import streamlit as st
import random
import json
import os

# --- 1. CONFIGURATIE ---
DB_FILE = "database.json"

st.set_page_config(page_title="Putsie World Online", page_icon="🌍")

# --- 2. DATABASE FUNCTIES ---
def laad_db():
    if not os.path.exists(DB_FILE):
        # Als er nog geen database is, maken we een lege
        return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

# --- 3. SESSIE INITIALISATIE ---
if 'ingelogd' not in st.session_state:
    st.session_state.ingelogd = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# --- 4. HOOFDMENU (LOGIN) ---
if not st.session_state.ingelogd:
    st.markdown("<h1 style='text-align: center;'>🌍 Putsie World</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Klaar om te leren?</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 4, 1]) # Iets breder voor mobiel
    with col2:
        # Gebruik een formulier zodat mobiel niet tussentijds ververst
        with st.form("login_form"):
            st.write("### Log in of Registreer")
            u = st.text_input("Gebruikersnaam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            submit_button = st.form_submit_button("Start Avontuur", use_container_width=True)
            
            if submit_button:
                db = laad_db()
                if u in db["users"]:
                    if db["users"][u]["password"] == p:
                        st.session_state.ingelogd = True
                        st.session_state.username = u
                        st.rerun()
                    else:
                        st.error("Wachtwoord onjuist!")
                else:
                    if u and p:
                        db["users"][u] = {
                            "password": p,
                            "geld": 0,
                            "land": 0,
                            "woorden": {}
                        }
                        sla_db_op(db)
                        st.session_state.ingelogd = True
                        st.session_state.username = u
                        st.rerun()
                    else:
                        st.warning("Vul een naam en wachtwoord in.")
    st.stop()

# --- 5. DE APP (NA INLOGGEN) ---
db = laad_db()
user = st.session_state.username
u_data = db["users"][user]

# Sidebar voor stats en uitloggen
st.sidebar.title(f"👤 {user.capitalize()}")
st.sidebar.metric("💰 Saldo", f"€{u_data['geld']}")
st.sidebar.metric("🏰 Land", f"{u_data['land']} km²")

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()

st.title(f"Koninkrijk van {user.capitalize()}")

# Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Quiz", "📝 Toevoegen", "🛒 Winkel"])

# --- TAB 1: QUIZ ---
with tab1:
    if not u_data["woorden"]:
        st.info("Voeg eerst woorden toe in het volgende tabblad!")
    else:
        if 'vraag' not in st.session_state:
            st.session_state.vraag = random.choice(list(u_data["woorden"].keys()))
        
        v = st.session_state.vraag
        st.write(f"### Vertaal naar het Frans: **{u_data['woorden'][v]}**")
        poging = st.text_input("Antwoord:", key="quiz_in")
        
        if st.button("Check"):
            if poging.lower().strip() == v.lower():
                st.balloons()
                u_data["geld"] += 100
                sla_db_op(db)
                st.success("Goed! +€100")
                del st.session_state.vraag
                st.rerun()
            else:
                st.error(f"Fout! Het was: {v}")

# --- TAB 2: TOEVOEGEN ---
with tab2:
    st.subheader("Nieuwe woorden")
    f_w = st.text_input("Frans:")
    n_w = st.text_input("Nederlands:")
    if st.button("Opslaan"):
        if f_w and n_w:
            u_data["woorden"][f_w.strip().lower()] = n_w.strip().lower()
            sla_db_op(db)
            st.success("Toegevoegd aan je persoonlijke database!")
            st.rerun()

# --- TAB 3: WINKEL ---
with tab3:
    st.subheader("Winkel")
    if st.button("Koop 10km² Land (€500)"):
        if u_data["geld"] >= 500:
            u_data["geld"] -= 500
            u_data["land"] += 10
            sla_db_op(db)
            st.rerun()
        else:
            st.error("Niet genoeg geld!")
