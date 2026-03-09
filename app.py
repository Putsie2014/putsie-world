import streamlit as st
import random
import json
import os

# --- 1. CONFIGURATIE ---
DB_FILE = "database.json"
st.set_page_config(page_title="Putsie World Online", page_icon="🌍")

def laad_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

# --- 2. LOGIN & SESSIE ---
if 'ingelogd' not in st.session_state:
    st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.markdown("<h1 style='text-align: center;'>🌍 Putsie World</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            with st.form("login_form"):
                u = st.text_input("Gebruikersnaam").lower().strip()
                p = st.text_input("Wachtwoord", type="password")
                if st.form_submit_button("Start Avontuur", use_container_width=True):
                    db = laad_db()
                    if u in db["users"] and db["users"][u]["password"] == p:
                        st.session_state.ingelogd, st.session_state.username = True, u
                        st.rerun()
                    elif u not in db["users"] and u and p:
                        db["users"][u] = {"password": p, "geld": 0, "land": 0, "woorden": {}}
                        sla_db_op(db)
                        st.session_state.ingelogd, st.session_state.username = True, u
                        st.rerun()
                    else: st.error("Fout in gegevens")
    st.stop()

# --- 3. DATA LADEN ---
db = laad_db()
user = st.session_state.username
u_data = db["users"][user]

st.sidebar.title(f"👤 {user.capitalize()}")
st.sidebar.metric("💰 Saldo", f"€{u_data['geld']}")
st.sidebar.metric("🏰 Land", f"{u_data['land']} km²")
if st.sidebar.button("Uitloggen"):
    st.session_state.clear()
    st.rerun()

# --- 4. DE APP TABS ---
tab1, tab2, tab3 = st.tabs(["🎯 Quiz", "📝 Toevoegen", "🛒 Winkel"])

# --- QUIZ (Met automatische vernieuwing) ---
with tab1:
    if not u_data["woorden"]:
        st.info("Voeg eerst woorden toe!")
    else:
        # Kies een woord als er nog geen is
        if 'vraag' not in st.session_state:
            st.session_state.vraag = random.choice(list(u_data["woorden"].keys()))
        
        v = st.session_state.vraag
        st.write(f"### Vertaal: **{u_data['woorden'][v]}**")
        
        with st.form("quiz_form", clear_on_submit=True):
            poging = st.text_input("Antwoord in het Frans:")
            if st.form_submit_button("Check"):
                if poging.lower().strip() == v.lower():
                    u_data["geld"] += 100
                    sla_db_op(db)
                    st.success("Helemaal goed! +€100")
                    # Forceer een nieuw woord door de huidige te verwijderen uit de sessie
                    del st.session_state.vraag
                    st.rerun()
                else:
                    st.error(f"Helaas, het was: {v}")

# --- TOEVOEGEN (Met lege vakjes fix) ---
with tab2:
    st.subheader("Nieuwe woorden toevoegen")
    # clear_on_submit=True zorgt dat de vakjes direct leeg worden na het klikken
    with st.form("add_word_form", clear_on_submit=True):
        f_w = st.text_input("Frans:")
        n_w = st.text_input("Nederlands:")
        if st.form_submit_button("Opslaan"):
            if f_w and n_w:
                u_data["woorden"][f_w.strip().lower()] = n_w.strip().lower()
                sla_db_op(db)
                st.success(f"'{f_w}' opgeslagen!")
            else:
                st.warning("Vul beide velden in.")

# --- WINKEL ---
with tab3:
    st.subheader("Winkel")
    st.write(f"Huidig land: {u_data['land']} km²")
    if st.button("Koop 10km² Land (€500)"):
        if u_data["geld"] >= 500:
            u_data["geld"] -= 500
            u_data["land"] += 10
            sla_db_op(db)
            st.balloons()
            st.rerun()
        else:
            st.error("Niet genoeg geld!")
