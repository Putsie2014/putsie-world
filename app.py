import streamlit as st
import sqlite3
import hashlib
from openai import OpenAI

# --- CONFIGURATIE ---
SITE_TITLE = "(indev) Putsie EDUCATION 🎓"
client = OpenAI(api_key="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")

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# --- DATABASE FUNCTIES (SQLite) ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, geld INTEGER)')
    conn.commit()
    conn.close()

def add_user(u, p):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_p = hashlib.sha256(p.encode()).hexdigest()
    try:
        c.execute('INSERT INTO users (username, password, geld) VALUES (?, ?, 100)', (u, hashed_p))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def check_login(u, p):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_p = hashlib.sha256(p.encode()).hexdigest()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (u, hashed_p))
    user = c.fetchone()
    conn.close()
    return user

init_db()

# --- AI FUNCTIE ---
def vraag_gpt(vraag):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "Je bent een behulpzame leraar. Geef hints, geen antwoorden."},
                      {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- AUTH LOGICA ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title(SITE_TITLE)
    tab1, tab2 = st.tabs(["🚀 Inloggen", "📝 Registreren"])
    with tab1:
        u = st.text_input("Naam").lower()
        p = st.text_input("Wachtwoord", type="password")
        if st.button("Login"):
            if check_login(u, p):
                st.session_state.ingelogd = True; st.session_state.username = u; st.rerun()
            else: st.error("Fout!")
    with tab2:
        nu = st.text_input("Nieuwe Naam").lower()
        np = st.text_input("Nieuw Wachtwoord", type="password")
        if st.button("Account Aanmaken"):
            if add_user(nu, np): st.success("Account gemaakt!")
            else: st.error("Gebruiker bestaat al.")
    st.stop()

# --- HOOFD APP ---
user = st.session_state.username
st.sidebar.title(f"Welkom {user}")
nav = st.sidebar.radio("Menu", ["🏠 Home", "🤖 AI Hulp"])

if nav == "🏠 Home":
    st.title("Putsie Education")
    st.write("Gebruik het menu om te leren.")
elif nav == "🤖 AI Hulp":
    v = st.text_area("Vraag aan de leraar:")
    if st.button("Vraag"):
        st.write(vraag_gpt(v))

if st.sidebar.button("Log uit"): st.session_state.clear(); st.rerun()
