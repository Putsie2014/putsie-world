import streamlit as st
import json
import os
import random
from huggingface_hub import InferenceClient

# --- 1. CONFIGURATIE ---
DB_FILE = "database.json"
API_TOKEN = "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" # Jouw token
client = InferenceClient(api_key=API_TOKEN)

st.set_page_config(page_title="Putsie Studios", layout="wide")

# --- AI FUNCTIE ---
def vraag_ai(vraag):
    try:
        completion = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=[
                {"role": "system", "content": "Je bent een behulpzame Franse taaltutor voor Putsie Studios."},
                {"role": "user", "content": vraag}
            ],
            max_tokens=400
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI is even niet bereikbaar: {e}"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": {}}, f)

def laad_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {"users": {}}

def sla_db_op(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, indent=4)

init_db()

if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'page' not in st.session_state: st.session_state.page = "Home"

# --- 2. LOGIN (Hetzelfde als jouw code) ---
if not st.session_state.ingelogd:
    st.title("🌍 Putsie Studios - Login")
    tab1, tab2 = st.tabs(["Inloggen", "Registreren"])
    db = laad_db()
    with tab1:
        u = st.text_input("Naam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Log in"):
            if u in db["users"] and db["users"][u]["password"] == p:
                st.session_state.ingelogd = True
                st.session_state.username = u
                st.rerun()
            else: st.error("Fout!")
    with tab2:
        ru = st.text_input("Kies Naam", key="r_u").lower().strip()
        rp = st.text_input("Kies Wachtwoord", type="password", key="r_p")
        if st.button("Maak Account"):
            if ru and rp and ru not in db["users"]:
                db["users"][ru] = {"password": rp, "geld": 100, "woorden": {"werkwoorden": {}, "woorden": {}}}
                sla_db_op(db)
                st.success("Account aangemaakt!")
    st.stop()

# --- 3. DATA & ZIJKANT ---
db = laad_db()
user = st.session_state.username
data = db["users"].get(user, {"geld": 0, "woorden": {"werkwoorden": {}, "woorden": {}}})

with st.sidebar:
    st.title(f"👤 {user.capitalize()}")
    st.metric("Saldo", f"€{data.get('geld', 0)}")
    st.write("---")
    # Menu knoppen
    if st.button("🏠 Home", use_container_width=True): st.session_state.page = "Home"
    if st.button("🇫🇷 Frans & Werkwoorden", use_container_width=True): st.session_state.page = "Frans"
    if st.button("🤖 AI Tutor", use_container_width=True): st.session_state.page = "AI"
    if st.button("📖 Strips", use_container_width=True): st.session_state.page = "Strips"
    if st.button("🕹️ Games", use_container_width=True): st.session_state.page = "Games"
    if st.button("🎧 Music", use_container_width=True): st.session_state.page = "Music"
    st.write("---")
    if st.button("Uitloggen"): st.session_state.clear(); st.rerun()

# --- 4. PAGINA'S ---
# AI Tutor Pagina
if st.session_state.page == "AI":
    st.title("🤖 Putsie AI Tutor")
    vraag = st.text_area("Wat wil je weten over Frans?")
    if st.button("Vraag verzenden"):
        with st.spinner("AI denkt na..."):
            st.info(vraag_ai(vraag))

# [Hieronder volgen jouw bestaande pagina's: Frans, Strips, Games, Music, Admin]
# (Knip en plak hier je bestaande logica voor die pagina's uit je eigen script)
elif st.session_state.page == "Frans":
    # Jouw code voor Frans pagina...
    pass
elif st.session_state.page == "Admin":
    # Jouw code voor Admin pagina...
    pass
