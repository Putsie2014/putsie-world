import streamlit as st
import random
import json
import os
import hashlib
import html
import re
from datetime import datetime, timedelta
import pandas as pd

try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' en 'pandas' ontbreken in requirements.txt")

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie WORLD 🎓 v1.02"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# --- SECURITY & MODERATIE ---
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def censor_text(text):
    """Vervangt verboden woorden door *** en geeft een rood vlaggetje af."""
    censored = text[:500] 
    flagged = False
    bad_words_list = st.session_state.db.get('bad_words', [])
    for word in bad_words_list:
        if word and re.search(r'\b' + re.escape(word) + r'\b', censored, re.IGNORECASE):
            censored = re.sub(r'\b' + re.escape(word) + r'\b', '***', censored, flags=re.IGNORECASE)
            flagged = True
    return censored, flagged

# --- 2. PREMIUM STYLING & THEMA'S ---
st.set_page_config(page_title=SITE_TITLE, layout="wide", initial_sidebar_state="expanded")

THEMES = {
    "Standaard": "linear-gradient(-45deg, #1a2a6c, #b21f1f, #fdbb2d)",
    "Matrix": "linear-gradient(180deg, #000000, #003300, #000000)",
    "Cyberpunk": "linear-gradient(-45deg, #0f0c29, #302b63, #24243e)",
    "Roze Wolken": "linear-gradient(-45deg, #ff9a9e, #fecfef, #ff9a9e)",
    "Oceaan": "linear-gradient(-45deg, #2193b0, #6dd5ed)"
}

def apply_premium_design(theme_bg):
    st.markdown(f"""
    <style>
        .stApp {{ background: {theme_bg}; background-size: 400% 400%; animation: gradientBG 15s ease infinite; color: white; }}
        @keyframes gradientBG {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div, .stTabs {{
            background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(12px); border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3); padding: 15px; color: white !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        p, span, label, h1, h2, h3 {{ color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); }}
        
        /* IPAD BUTTON FIX */
        .stButton button {{ transition: all 0.3s ease 0s !important; border-radius: 10px !important; font-weight: bold; border: 1px solid rgba(255,255,255,0.2) !important; white-space: normal !important; height: auto !important; min-height: 2.5rem; }}
        .stButton button:hover {{ transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 5px 15px rgba(0, 210, 255, 0.6) !important; border-color: #00d2ff !important; }}
        
        .hacker-term {{ background-color: #050505 !important; color: #0f0 !important; font-family: 'Courier New', Courier, monospace !important; padding: 25px; border-radius: 12px; border: 2px solid #0f0; box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); }}
        input, textarea, select {{ color: black !important; text-shadow: none !important; border-radius: 8px !important; }}
        
        /* BADGES & TITLES */
        .custom-badge {{ color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px; margin-right: 5px; display: inline-block; text-shadow: 1px 1px 2px black; border: 1px solid rgba(255,255,255,0.3); }}
        .pro-badge {{ background: linear-gradient(45deg, #FFD700, #FF8C00); color: white; padding: 2px 8px; border-radius: 10px; font-weight: 900; font-size: 12px; margin-right: 5px; display: inline-block; text-shadow: 1px 1px 2px black; box-shadow: 0 0 10px rgba(255,215,0,0.8); animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        .mood-text {{ font-style: italic; color: rgba(255,255,255,0.7) !important; font-size: 0.9em; }}
        .title-badge {{ background: rgba(0,0,0,0.5); color: #00d2ff; padding: 2px 6px; border-radius: 5px; font-size: 11px; font-style: italic; margin-right: 5px; border: 1px solid #00d2ff; box-shadow: 0 0 5px rgba(0,210,255,0.5); }}
        .lvl-badge {{ background: #4CAF50; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; margin-right: 5px; box-shadow: 0 0 5px rgba(76,175,80,0.5); }}
        
        /* IPAD EILAND FIX (Scrollbaar en geen afbreek-regels) */
        .game-map-wrapper {{ width: 100%; overflow-x: auto; text-align: center; padding-bottom: 10px; }}
        .game-map-wrapper::-webkit-scrollbar {{ height: 8px; }}
        .game-map-wrapper::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.2); border-radius: 10px; }}
        .game-map-wrapper::-webkit-scrollbar-thumb {{ background: #fdbb2d; border-radius: 10px; }}
        
        .game-map {{ text-align: center; line-height: 1.05; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 15px; border: 3px solid #fdbb2d; display: inline-block; box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 10px 30px rgba(0,0,0,0.5); white-space: nowrap; }}
        
        .island-sign {{ font-size: 24px; color: white; background: rgba(139, 69, 19, 0.8); padding: 5px 20px; border-radius: 5px; border: 2px solid #5C4033; font-weight: bold; margin-bottom: 15px; display: inline-block; text-shadow: 2px 2px 4px black; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }}
        .net-worth {{ font-size: 20px; color: gold; font-weight: bold; background: rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 10px; border: 1px solid gold;}}
        .achievement-card {{ background: rgba(255, 215, 0, 0.1); border: 1px solid gold; padding: 10px; border-radius: 10px; text-align: center; transition: 0.3s; }}
        .achievement-card:hover {{ transform: scale(1.05); background: rgba(255, 215, 0, 0.3); }}
        .pet-box {{ background: rgba(255,255,255,0.1); border: 2px dashed #00d2ff; padding: 20px; border-radius: 15px; text-align: center; transition: 0.3s; }}
        .pet-box:hover {{ background: rgba(255,255,255,0.2); border-color: #fdbb2d; }}
        .pet-emoji {{ font-size: 60px; filter: drop-shadow(0px 10px 10px rgba(0,0,0,0.5)); transition: transform 0.2s; }}
        .pet-emoji:hover {{ transform: translateY(-10px) scale(1.1); }}
        .inventory-badge {{ background: rgba(255,255,255,0.2); border-radius: 5px; padding: 5px 10px; display: inline-block; margin: 3px; border: 1px solid rgba(255,255,255,0.5); font-weight: bold; text-shadow: 1px 1px 2px black; }}
        .tour-box {{ background: rgba(0,0,0,0.8); border: 2px solid #00d2ff; border-radius: 15px; padding: 40px; text-align: center; box-shadow: 0 0 50px rgba(0,210,255,0.5); }}
    </style>
    """, unsafe_allow_html=True)

# --- CONTENT DATA ---
SHOP_ITEMS = {
    "Bloem": {"prijs": 100, "emoji": "🌺"}, "Straat": {"prijs": 200, "emoji": "🛤️"}, "Muur": {"prijs": 300, "emoji": "🧱"}, 
    "Boom": {"prijs": 500, "emoji": "🌳"}, "Tent": {"prijs": 800, "emoji": "⛺"}, "Huis": {"prijs": 1000, "emoji": "🏠"}, 
    "Kampvuur": {"prijs": 1200, "emoji": "🔥"}, "Beeld": {"prijs": 1500, "emoji": "🗿"}, "Fontein": {"prijs": 2500, "emoji": "⛲"}, 
    "Schatkist": {"prijs": 5000, "emoji": "💎"}, "Kasteel": {"prijs": 10000, "emoji": "🏰"}, "Draak": {"prijs": 25000, "emoji": "🐉"}
}
PET_TYPES = {
    "Hond": {"prijs": 2000, "emoji": "🐕"}, "Kat": {"prijs": 2000, "emoji": "🐈"}, 
    "Papegaai": {"prijs": 4000, "emoji": "🦜"}, "Alien": {"prijs": 10000, "emoji": "👽"}
}
TITEL_SHOP = {
    "Student": 0, "Brugpieper": 100, "Gezellig": 500, "Spaarvarken": 1000, 
    "De Rijke": 5000, "Tycoon": 10000, "Putsie Legende": 25000, "God van de Wereld": 100000
}
RAADSELS = [
    {"q": "Wat heeft tanden maar kan niet bijten?", "a": "kam"}, {"q": "Wat wordt natter naarmate het meer droogt?", "a": "handdoek"},
    {"q": "Ik heb steden maar geen huizen, water maar geen vissen.", "a": "landkaart"}, {"q": "Hoe meer je ervan weghaalt, hoe groter het wordt.", "a": "gat"},
    {"q": "Wat behoort tot jou, maar wordt meer door anderen gebruikt?", "a": "naam"}
]
TYPE_ZINNEN = [
    "De snelle bruine vos springt over de luie hond.",
    "Putsie is de allerbeste assistent van de hele wereld!",
    "Een goede hacker beveiligt zijn database met encryptie.",
    "In de virtuele dierenwinkel kun je een draak kopen."
]
AVATARS = ["👤", "😎", "🤓", "🤠", "🤖", "👽", "👻", "🐵", "🦁", "🦄", "🐉", "🦊", "👑", "🚀", "💎", "🔥", "⚡"]
WEER_TYPES = ["☀️ Zonnig", "🌧️ Regenachtig", "❄️ Sneeuw", "⚡ Onweer", "🌈 Regenboog"]

vandaag = datetime.now().strftime("%Y-%m-%d")
random.seed(vandaag)
huidig_weer = random.choice(WEER_TYPES)
random.seed() 

# --- 3. BULLETPROOF DATABASE ENGINE ---
def laad_db():
    basis_db = {"users": {"elliot": {"pw": hash_pw("Putsie"), "role": "admin", "class": "ADMIN-000"}}}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except Exception: return basis_db
    return basis_db

def sla_db_op():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(st.session_state.db, f, separators=(',', ':'))
    except Exception as e: st.error(f"🚨 Fout bij opslaan: {e}")

if 'db' not in st.session_state: st.session_state.db = laad_db()

safe_defaults = {
    "users": {"elliot": {"pw": hash_pw("Putsie"), "role": "admin", "class": "ADMIN-000"}},
    "classes": {"ADMIN-000": {"name": "Admin Base", "teacher": "elliot"}},
    "saldi": {}, "bank": {}, "ai_points": {}, "user_vocab": {}, "chat_messages": [], "vocab_lists": [],
    "tasks": [], "completed_tasks": {}, "chat_tags": {}, "custom_tags": ["👑 ADMIN", "⭐ VIP", "🔥 STRIJDER"],
    "custom_tags_v2": {"👑 ADMIN": "#FFD700", "⭐ VIP": "#FF4B4B", "🔥 STRIJDER": "#FFA500"},
    "player_tags": {}, "streaks": {}, "avatars": {}, "moods": {}, "islands": {}, 
    "island_levels": {}, "inventory": {}, "island_names": {}, "island_likes": {}, "is_pro": {},
    "unlocked_achievements": {}, "equipped_achievement": {}, "themes": {}, "pets": {},
    "has_done_tour": {}, "purchased_titles": {}, "active_title": {},
    "lockdown": False, "lockdown_msg": "Systeem onderhoud door Elliot",
    "announcement": "", "bad_words": ["stom", "dombo", "sukkel", "kut", "kloot", "bitch", "shit", "fuck", "lelijk", "haat"]
}
for key, default_val in safe_defaults.items():
    st.session_state.db.setdefault(key, default_val)

def verifieer_speler_data(naam):
    d = st.session_state.db
    d['saldi'].setdefault(naam, 100) 
    d['bank'].setdefault(naam, {"saldo": 0, "last_interest": vandaag})
    d['ai_points'].setdefault(naam, 5)
    d['user_vocab'].setdefault(naam, {})
    d['completed_tasks'].setdefault(naam, [])
    d['islands'].setdefault(naam, {})
    d['island_levels'].setdefault(naam, 4)
    d['inventory'].setdefault(naam, {})
    d['avatars'].setdefault(naam, "👤")
    d['moods'].setdefault(naam, "")
    d['streaks'].setdefault(naam, {"date": "", "count": 0})
    d['player_tags'].setdefault(naam, [])
    d['island_names'].setdefault(naam, f"Eiland van {naam.capitalize()}")
    d['island_likes'].setdefault(naam, 0)
    d['is_pro'].setdefault(naam, False)
    d['unlocked_achievements'].setdefault(naam, [])
    d['equipped_achievement'].setdefault(naam, "")
    d['themes'].setdefault(naam, "Standaard")
    d['pets'].setdefault(naam, {"type": None, "name": "", "hunger": 100, "happiness": 100, "level": 1})
    d['purchased_titles'].setdefault(naam, ["Student"])
    d['active_title'].setdefault(naam, "Student")
    d['users'][naam].setdefault('class', "")
    d['has_done_tour'].setdefault(naam, False)
    
    last_int = d['bank'][naam]['last_interest']
    if last_int != vandaag and d['bank'][naam]['saldo'] > 0:
        rente = int(d['bank'][naam]['saldo'] * 0.05)
        d['bank'][naam]['saldo'] += rente
        d['bank'][naam]['last_interest'] = vandaag
    sla_db_op()

# --- 4. LOGIN & AUTO-LOGIN ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if not st.session_state.ingelogd:
    apply_premium_design(THEMES["Standaard"])
    if st.session_state.db.get('announcement'): st.warning(f"📢 **SYSTEEM BERICHT:** {st.session_state.db['announcement']}")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center; font-size: 50px; text-shadow: 0px 0px 20px #fdbb2d;'>{SITE_TITLE}</h1>", unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔑 Log In", "📝 Registreren"])
        
        with t_log:
            u = st.text_input("Naam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Start Game", type="primary", use_container_width=True):
                hashed_p = hash_pw(p)
                if u == "admin2014": st.session_state.in_terminal = True; st.rerun()
                elif u == "elliot" and p == "Putsie":
                    verifieer_speler_data("elliot"); st.session_state.db['is_pro']['elliot'] = True
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"; st.rerun()
                elif u in st.session_state.db['users']:
                    stored_pw = st.session_state.db['users'][u]["pw"]
                    if stored_pw == hashed_p or stored_pw == p:
                        if stored_pw == p: st.session_state.db['users'][u]["pw"] = hashed_p; sla_db_op()
                        verifieer_speler_data(u); st.session_state.ingelogd, st.session_state.username = True, u
                        st.session_state.role = st.session_state.db['users'][u]["role"]; st.rerun()
                    else: st.error("Inloggegevens fout!")
                else: st.error("Gebruiker niet gevonden!")
                
        with t_reg:
            st.info("Maak je profiel aan.")
            nu = st.text_input("Kies Gebruikersnaam").lower().strip()
            np = st.text_input("Kies Wachtwoord", type="password")
            if st.button("Account Aanmaken", use_container_width=True):
                if not nu or not np: st.error("⚠️ Vul alles in!")
                elif nu in st.session_state.db['users']: st.error("⚠️ Deze naam is al bezet!")
                else:
                    st.session_state.db['users'][nu] = {"pw": hash_pw(np), "role": "student", "class": ""}
                    verifieer_speler_data(nu)
                    st.session_state.ingelogd = True; st.session_state.username = nu; st.session_state.role = "student"
                    sla_db_op(); st.rerun()
    st.stop()

verifieer_speler_data(st.session_state.username)
mijn_naam = st.session_state.username
mijn_thema_naam = st.session_state.db['themes'].get(mijn_naam, "Standaard")
apply_premium_design(THEMES.get(mijn_thema_naam, THEMES["Standaard"]))

# --- RONDLEIDING (TUTORIAL) SYSTEEM ---
if not st.session_state.db['has_done_tour'].get(mijn_naam, False):
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class='tour-box'>
            <h1 style='color: #00d2ff;'>🤖 Hoi {mijn_naam.capitalize()}! Ik ben Putsie!</h1>
            <h3>Welkom in versie 1.0! Jouw nieuwe, betere wereld! Hier zijn 3 snelle tips:</h3>
            <p style='font-size: 18px; text-align: left;'>
            <b>1. 💰 De Bank:</b> Zet je munten op de bank om elke dag 5% rente te krijgen!<br><br>
            <b>2. 🏫 Jouw Klas:</b> Doe opdrachten in de 'Klas' tab om supersnel rijk te worden.<br><br>
            <b>3. 🏝️ Tycoon Eiland:</b> Gebruik je munten om je eigen droom eiland te bouwen en show het aan je vrienden!
            </p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Begrepen! Geef mij mijn Start-Bonus en Let's Go!", type="primary", use_container_width=True):
            st.session_state.db['saldi'][mijn_naam] += 250 
            st.session_state.db['has_done_tour'][mijn_naam] = True
            sla_db_op(); st.balloons(); st.rerun()
    st.stop()

# --- TERMINAL ---
if st.session_state.get('in_terminal', False):
    st.markdown("<div class='hacker-term'><h1>>_ SYSTEM OVERRIDE V1.02</h1><p>Type /exit to leave.</p></div>", unsafe_allow_html=True)
    cmd = st.text_input(">").strip()
    if cmd == "/deactivatelockdown": st.session_state.db['lockdown'] = False; sla_db_op(); st.toast("🔓 Lockdown gedeactiveerd!")
    elif cmd.startswith("/openaccount"):
        target = cmd.split(" ")[1].lower() if len(cmd.split(" ")) > 1 else ""
        if target in st.session_state.db['users'] or target == "elliot":
            verifieer_speler_data(target); st.session_state.ingelogd, st.session_state.username = True, target
            st.session_state.role = st.session_state.db['users'].get(target, {}).get("role", "admin")
            st.session_state.lockdown_bypass, st.session_state.in_terminal = True, False; st.rerun()
    elif cmd == "/exit": st.session_state.in_terminal = False; st.rerun()
    st.stop() 

# --- 5. LOGICA ---
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"
is_pro = st.session_state.db['is_pro'].get(mijn_naam, False)
mijn_klas = st.session_state.db['users'][mijn_naam].get("class", "")

if st.session_state.db.get('lockdown') and not is_admin:
    st.markdown(f"<div style='text-align:center; padding:100px; background: rgba(255,0,0,0.5); border-radius:20px;'><h1>🚫 SYSTEM LOCKDOWN</h1><h3>{st.session_state.db['lockdown_msg']}</h3></div>", unsafe_allow_html=True)
    if st.button("Uitloggen"): st.session_state.ingelogd = False; st.rerun()
    st.stop()

mijn_saldo = st.session_state.db['saldi'][mijn_naam]
mijn_bank = st.session_state.db['bank'][mijn_naam]['saldo']
mijn_level = ((mijn_saldo + mijn_bank) // 500) + 1 
mijn_tags = st.session_state.db['player_tags'][mijn_naam]
mijn_avatar = st.session_state.db['avatars'][mijn_naam]
mijn_streak_data = st.session_state.db['streaks'][mijn_naam]
mijn_pet = st.session_state.db['pets'][mijn_naam]
mijn_gekozen_titel = st.session_state.db['active_title'][mijn_naam]

gisteren = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# --- 6. GESTRUCTUREERDE SIDEBAR ---
with st.sidebar:
    badge_html = "<span class='pro-badge'>🌟 PRO</span>" if is_pro else ""
    for t_name in mijn_tags:
        color = st.session_state.db['custom_tags_v2'].get(t_name, "#888888")
        badge_html += f"<span class='custom-badge' style='background:{color}'>{t_name}</span>"
    
    st.markdown(f"<h3>{mijn_avatar} {mijn_naam.capitalize()}</h3>{badge_html}", unsafe_allow_html=True)
    st.markdown(f"<span class='title-badge'>{mijn_gekozen_titel}</span> ⭐ Lvl: {mijn_level}", unsafe_allow_html=True)
    st.caption(f"🔥 Streak: {mijn_streak_data['count']} dagen | {huidig_weer}")
    
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("💰 Zakgeld", mijn_saldo)
    col_s2.metric("🏦 Bank", mijn_bank)
    
    if mijn_streak_data["date"] != vandaag:
        if st.button("🎁 Claim Daily Bonus!", use_container_width=True):
            nieuwe_streak = mijn_streak_data["count"] + 1 if mijn_streak_data["date"] == gisteren else 1 
            totale_bonus = random.randint(20, 50) + min(nieuwe_streak * 5, 100)
            if is_pro: totale_bonus *= 2; st.toast("🌟 PRO Bonus: 2x Munten geactiveerd!", icon="🌟")
            st.session_state.db['saldi'][mijn_naam] += totale_bonus
            st.session_state.db['streaks'][mijn_naam] = {"date": vandaag, "count": nieuwe_streak}
            sla_db_op(); st.snow(); st.toast(f"Je kreeg {totale_bonus} 🪙!", icon="🎁"); st.rerun()
        
    st.divider()
    hoofd_menu = st.selectbox("📍 Kies Categorie:", ["👤 Mijn Leven", "🏫 School & Leren", "🎮 Games & Eiland", "🛠️ Beheer"])
    
    if hoofd_menu == "👤 Mijn Leven": nav = st.radio("Ga naar:", ["Profiel", "Putsie Bank", "Dierenwinkel"])
    elif hoofd_menu == "🏫 School & Leren": nav = st.radio("Ga naar:", ["Klas & Taken", "Frans Lab", "🤖 Putsie AI Hulp"])
    elif hoofd_menu == "🎮 Games & Eiland":
        nav = st.radio("Ga naar:", ["Eiland Tycoon", "Game Hal", "Raadsels"])
    elif hoofd_menu == "🛠️ Beheer":
        b_opties = []
        if is_teacher: b_opties.append("Leraar Paneel")
        if is_admin: b_opties.append("Admin Room")
        if not b_opties: st.info("Geen toegang."); nav = "Profiel"
        else: nav = st.radio("Ga naar:", b_opties)
            
    st.divider()
    with st.expander("🏆 Leaderboard (Top 10)"):
        top_spelers = sorted([(u, st.session_state.db['saldi'][u] + st.session_state.db['bank'][u]['saldo']) for u in st.session_state.db['users'].keys() if st.session_state.db['users'][u].get('role') != 'admin'], key=lambda x: x[1], reverse=True)[:10]
        for i, (u, total_wealth) in enumerate(top_spelers):
            med = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
            ava = st.session_state.db['avatars'].get(u, "👤")
            pro_star = "🌟" if st.session_state.db['is_pro'].get(u, False) else ""
            st.markdown(f"**{med} {ava} {u.capitalize()} {pro_star}**<br>{total_wealth} 🪙", unsafe_allow_html=True)
            
    if st.button("🚪 Uitloggen", use_container_width=True): st.session_state.ingelogd = False; st.rerun()

if st.session_state.db.get('announcement'):
    st.warning(f"📢 **SYSTEEM BERICHT:** {st.session_state.db['announcement']}")

# --- 8. PAGINA'S ---

if nav == "Profiel":
    st.title("👤 Jouw Profiel")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Instellingen")
        nieuwe_ava = st.selectbox("Kies Avatar", AVATARS, index=AVATARS.index(mijn_avatar) if mijn_avatar in AVATARS else 0)
        nieuwe_mood = html.escape(st.text_input("Wat is je mood in de chat?", value=st.session_state.db['moods'].get(mijn_naam, ""), max_chars=30))
        huidige_eiland_naam = st.session_state.db['island_names'].get(mijn_naam, f"Eiland van {mijn_naam.capitalize()}")
        nieuwe_eiland_naam = html.escape(st.text_input("Naam van jouw Eiland (Bordje):", value=huidige_eiland_naam, max_chars=25))
        nieuw_thema = st.selectbox("Kies Website Thema", list(THEMES.keys()), index=list(THEMES.keys()).index(mijn_thema_naam))
        
        gekochte_titels = st.session_state.db['purchased_titles'][mijn_naam]
        nieuwe_titel = st.selectbox("Draag een Titel", gekochte_titels, index=gekochte_titels.index(mijn_gekozen_titel) if mijn_gekozen_titel in gekochte_titels else 0)
        
        if st.button("Profiel Opslaan", type="primary"):
            st.session_state.db['avatars'][mijn_naam] = nieuwe_ava
            st.session_state.db['moods'][mijn_naam] = nieuwe_mood
            st.session_state.db['island_names'][mijn_naam] = nieuwe_eiland_naam
            st.session_state.db['themes'][mijn_naam] = nieuw_thema
            st.session_state.db['active_title'][mijn_naam] = nieuwe_titel
            sla_db_op(); st.toast("Opgeslagen!", icon="✅"); st.rerun()
            
    with c2:
        st.subheader("🛒 Titel Winkel")
        cols_t = st.columns(2)
        for i, (t_naam, t_prijs) in enumerate(TITEL_SHOP.items()):
            with cols_t[i % 2]:
                if t_naam in gekochte_titels:
                    st.markdown(f"<div class='achievement-card' style='opacity:0.5;'><b>{t_naam}</b><br>In bezit</div><br>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='achievement-card'><b>{t_naam}</b><br>{t_prijs} 🪙</div>", unsafe_allow_html=True)
                    if st.button(f"Koop", key=f"buy_title_{t_naam}"):
                        if mijn_saldo >= t_prijs:
                            st.session_state.db['saldi'][mijn_naam] -= t_prijs
                            st.session_state.db['purchased_titles'][mijn_naam].append(t_naam)
                            sla_db_op(); st.toast(f"Titel {t_naam} gekocht!"); st.rerun()
                        else: st.error("Te weinig munten!")

elif nav == "Putsie Bank":
    st.title("🏦 De Putsie Bank")
    t_bank1, t_bank2 = st.tabs(["💰 Sparen", "💸 Tikkie sturen"])
    
    with t_bank1:
        st.write("Zet je munten op de bank en ontvang elke dag **5% rente**!")
        col_b1, col_b2, col_b3 = st.columns(3)
        col_b1.metric("Contant Geld", f"{mijn_saldo} 🪙")
        col_b2.metric("Saldo Bankrekening", f"{mijn_bank} 🪙")
        col_b3.metric("Verwachte Rente Morgen", f"+{int(mijn_bank * 0.05)} 🪙")
        st.divider()
        c_storten, c_opnemen = st.columns(2)
        with c_storten:
            stort_bedrag = st.number_input("Hoeveel wil je storten?", min_value=0, max_value=mijn_saldo, step=10)
            if st.button("Storten", type="primary"):
                if stort_bedrag > 0 and mijn_saldo >= stort_bedrag:
                    st.session_state.db['saldi'][mijn_naam] -= stort_bedrag; st.session_state.db['bank'][mijn_naam]['saldo'] += stort_bedrag
                    sla_db_op(); st.toast("Geld gestort!", icon="🏦"); st.rerun()
        with c_opnemen:
            opneem_bedrag = st.number_input("Hoeveel wil je opnemen?", min_value=0, max_value=mijn_bank, step=10)
            if st.button("Opnemen"):
                if opneem_bedrag > 0 and mijn_bank >= opneem_bedrag:
                    st.session_state.db['bank'][mijn_naam]['saldo'] -= opneem_bedrag; st.session_state.db['saldi'][mijn_naam] += opneem_bedrag
                    sla_db_op(); st.toast("Geld opgenomen!", icon="💸"); st.rerun()
                    
    with t_bank2:
        st.subheader("💸 Maak munten over naar vrienden")
        alle_spelers = [u for u in st.session_state.db['users'].keys() if u != mijn_naam]
        if alle_spelers:
            doel_speler = st.selectbox("Naar wie wil je geld sturen?", alle_spelers)
            tikkie_bedrag = st.number_input("Bedrag om te sturen (Contant):", min_value=1, max_value=max(1, mijn_saldo), step=10)
            if st.button("Verstuur Munten", type="primary"):
                if mijn_saldo >= tikkie_bedrag and tikkie_bedrag > 0:
                    st.session_state.db['saldi'][mijn_naam] -= tikkie_bedrag; st.session_state.db['saldi'][doel_speler] += tikkie_bedrag
                    sla_db_op(); st.balloons(); st.success(f"Je hebt {tikkie_bedrag} 🪙 naar {doel_speler.capitalize()} gestuurd!")
                else: st.error("Je hebt niet genoeg contant geld!")
        else: st.info("Er zijn geen andere spelers.")

elif nav == "Dierenwinkel":
    st.title("🐾 Virtuele Dierenwinkel")
    if not mijn_pet.get('type'):
        cols = st.columns(4)
        for i, (p_naam, p_data) in enumerate(PET_TYPES.items()):
            with cols[i % 4]:
                st.markdown(f"<div class='pet-box'><span class='pet-emoji'>{p_data['emoji']}</span><br><b>{p_naam}</b><br>{p_data['prijs']} 🪙</div>", unsafe_allow_html=True)
                if st.button(f"Koop {p_naam}", key=f"buy_pet_{p_naam}", use_container_width=True):
                    if mijn_saldo >= p_data['prijs']:
                        st.session_state.db['saldi'][mijn_naam] -= p_data['prijs']
                        st.session_state.db['pets'][mijn_naam] = {"type": p_naam, "emoji": p_data['emoji'], "name": f"Mijn {p_naam}", "hunger": 100, "happiness": 100, "level": 1}
                        sla_db_op(); st.balloons(); st.rerun()
                    else: st.error("Te weinig munten!")
    else:
        st.subheader(f"Jouw Huisdier: {mijn_pet.get('name', 'Huisdier')}")
        c_img, c_stats = st.columns([1, 2])
        with c_img:
            st.markdown(f"<div style='text-align:center;'><span class='pet-emoji' style='font-size:120px;'>{mijn_pet.get('emoji', '❓')}</span></div>", unsafe_allow_html=True)
            new_n = html.escape(st.text_input("Hernoem:", value=mijn_pet.get('name', ''), max_chars=20))
            if st.button("Opslaan"): st.session_state.db['pets'][mijn_naam]['name'] = new_n; sla_db_op(); st.rerun()
        with c_stats:
            st.progress(mijn_pet['hunger'] / 100, text=f"Voedsel: {mijn_pet['hunger']}%")
            st.progress(mijn_pet['happiness'] / 100, text=f"Blijheid: {mijn_pet['happiness']}%")
            st.write(f"**Level:** {mijn_pet['level']}")
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("🍎 Voeren (Kost 10 🪙)", use_container_width=True):
                if mijn_saldo >= 10:
                    st.session_state.db['saldi'][mijn_naam] -= 10; st.session_state.db['pets'][mijn_naam]['hunger'] = min(100, mijn_pet['hunger'] + 20)
                    sla_db_op(); st.toast("Nom nom!"); st.rerun()
                else: st.error("Geen geld!")
            if c_btn2.button("🎾 Spelen", use_container_width=True):
                st.session_state.db['pets'][mijn_naam]['happiness'] = min(100, mijn_pet['happiness'] + 15)
                st.session_state.db['pets'][mijn_naam]['hunger'] = max(0, mijn_pet['hunger'] - 5)
                if random.random() > 0.7: st.session_state.db['pets'][mijn_naam]['level'] += 1; st.toast(f"Level up!", icon="🆙")
                sla_db_op(); st.rerun()

elif nav == "Klas & Taken":
    st.title("🏫 Jouw Klas")
    if not mijn_klas:
        code = st.text_input("Klascode:")
        if st.button("Join"):
            if code in st.session_state.db['classes']: st.session_state.db['users'][mijn_naam]['class'] = code; sla_db_op(); st.rerun()
            else: st.error("Foutieve code.")
    else:
        k_info = st.session_state.db['classes'].get(mijn_klas, {"name": "Onbekend"})
        st.subheader(f"Klas: {k_info['name']}")
        t_tasks, t_lijsten, t_chat = st.tabs(["📋 Taken", "📚 Databanken", "💬 Klas Chat"])
        
        with t_tasks:
            if 'active_task' not in st.session_state:
                beschikbare_taken = [t for t in st.session_state.db['tasks'] if t.get('id', t.get('title')) not in st.session_state.db['completed_tasks'].get(mijn_naam, []) and t.get('class') in [mijn_klas, None, ""]]
                if beschikbare_taken:
                    for t in beschikbare_taken:
                        with st.container(border=True):
                            st.write(f"**{t.get('title', 'Taak')}** ({len(t.get('words', []))} woorden)")
                            if 'words' in t:
                                if st.button("Start Taak", key=f"btn_{t.get('id')}", type="primary"):
                                    st.session_state.active_task = t; st.session_state.task_words = list(t['words'].keys()); st.rerun()
                            else:
                                if st.button("Markeer als Gelezen", key=f"read_{t.get('title')}"):
                                    st.session_state.db['completed_tasks'][mijn_naam].append(t.get('title')); st.session_state.db['saldi'][mijn_naam] += 100; sla_db_op(); st.rerun()
                else: st.success("Alle taken zijn af!")
            else:
                t = st.session_state.active_task; nog_te_doen = len(st.session_state.task_words); totaal = len(t['words']); voortgang = totaal - nog_te_doen
                st.progress(voortgang / totaal)
                st.write(f"Woord {voortgang + 1} van {totaal}")
                if nog_te_doen > 0:
                    huidig_woord = st.session_state.task_words[0]
                    ans = st.text_input(f"Vertaal: {huidig_woord}", key="task_ans")
                    if st.button("Controleer"):
                        if ans.lower().strip() == t['words'][huidig_woord].lower().strip(): st.toast("Correct!"); st.session_state.task_words.pop(0); st.rerun()
                        else: st.error("Fout!")
                else:
                    st.balloons(); st.success("Voltooid! +100"); st.session_state.db['saldi'][mijn_naam] += 100; st.session_state.db['completed_tasks'][mijn_naam].append(t['id']); sla_db_op()
                    if st.button("Sluiten"): del st.session_state.active_task; del st.session_state.task_words; st.rerun()

        with t_lijsten:
            lijsten_voor_klas = [l for l in st.session_state.db.get('vocab_lists', []) if l.get('class') in [mijn_klas, None, ""]]
            if lijsten_voor_klas:
                for i, v in enumerate(lijsten_voor_klas):
                    if st.button(f"📥 Download {v['title']}", key=f"dl_{i}"): st.session_state.db['user_vocab'][mijn_naam].update(v['words']); sla_db_op(); st.toast("Toegevoegd aan Lab!", icon="📚")
            else: st.write("Geen lijsten beschikbaar.")
            
        with t_chat:
            with st.container(height=400, border=True):
                for m in [msg for msg in st.session_state.db['chat_messages'] if msg.get('class') == mijn_klas]:
                    u = m['user']; ava = st.session_state.db['avatars'].get(u, "👤"); mood = st.session_state.db['moods'].get(u, "")
                    tags = st.session_state.db['player_tags'].get(u, [])
                    u_titel = st.session_state.db['active_title'].get(u, "Student")
                    u_pro = "<span class='pro-badge'>🌟 PRO</span>" if st.session_state.db['is_pro'].get(u, False) else ""
                    b_html = "".join([f"<span class='custom-badge' style='background:{st.session_state.db['custom_tags_v2'].get(tn, '#888888')}'>{tn}</span>" for tn in tags])
                    st.markdown(f"{ava} <span class='title-badge'>{u_titel}</span> **{u.capitalize()}** {u_pro}{b_html} <br> <span class='mood-text'>{mood}</span> <br> {m['text']}", unsafe_allow_html=True)
            
            if p := st.chat_input("Typ een bericht..."):
                veilig_bericht, is_flagged = censor_text(html.escape(p))
                st.session_state.db['chat_messages'].append({
                    "user": mijn_naam, "text": veilig_bericht, "original": html.escape(p), "class": mijn_klas, "flagged": is_flagged
                })
                sla_db_op(); st.rerun()

elif nav == "Frans Lab":
    st.title("🇫🇷 Oefen Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'q' not in st.session_state: st.session_state.q = random.choice(list(w.keys()))
        g = st.text_input(f"Vertaal: {st.session_state.q}")
        if st.button("Controleren", type="primary"):
            if g.lower().strip() == w[st.session_state.q].lower().strip(): st.session_state.db['saldi'][mijn_naam] += 20; del st.session_state.q; sla_db_op(); st.rerun()
            else: st.error("Helaas!")
    else: st.info("Geen woorden. Download een lijst via Klas.")

elif nav == "🤖 Putsie AI Hulp":
    st.title("🤖 Putsie de AI Assistent")
    c1, c2 = st.columns([2, 1])
    with c2:
        if st.button(f"Koop 1 💎 voor {AI_PUNT_PRIJS} 🪙", use_container_width=True):
            if mijn_saldo >= AI_PUNT_PRIJS: st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS; st.session_state.db['ai_points'][mijn_naam] += 1; sla_db_op(); st.rerun()
            else: st.error("Te weinig munten!")
    with c1:
        vraag = st.text_area("Stel je vraag aan Putsie:")
        if st.button("Vraag stellen (-1 💎)", type="primary"):
            if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    messages = [
                        {"role": "system", "content": "Je bent Putsie, een vrolijke, behulpzame assistent in het educatieve spel Putsie WORLD. Geef af en toe een leuk complimentje."},
                        {"role": "user", "content": vraag}
                    ]
                    res = client.chat.completions.create(messages=messages, model=MODEL_NAAM)
                    st.session_state.ai_res = res.choices[0].message.content; st.session_state.db['ai_points'][mijn_naam] -= 1; sla_db_op()
                except Exception as e: st.error(f"AI Fout.")
            else: st.warning("Te weinig AI punten!")
        if 'ai_res' in st.session_state: st.info(st.session_state.ai_res)

elif nav == "Game Hal":
    st.title("🎮 De Game Hal")
    t1, t2, t3 = st.tabs(["🧮 Rekenwonder", "🔤 Woordhusselaar", "⌨️ Typemachine"])
    with t1:
        st.subheader("Rekenwonder")
        if 'math_q' not in st.session_state:
            a = random.randint(1, 100); b = random.randint(1, 100); op = random.choice(["+", "-", "*"])
            if op == "-": a, b = max(a,b), min(a,b)
            if op == "*": a = random.randint(1, 10); b = random.randint(1, 10)
            st.session_state.math_q = f"{a} {op} {b}"; st.session_state.math_a = eval(st.session_state.math_q)
        with st.container(border=True):
            st.markdown(f"## Wat is {st.session_state.math_q} ?")
            m_ans = st.number_input("Antwoord:", step=1, format="%d")
            if st.button("Controleer Som"):
                if m_ans == st.session_state.math_a: st.session_state.db['saldi'][mijn_naam] += 10; sla_db_op(); st.toast("+10 🪙"); del st.session_state.math_q; st.rerun()
                else: st.error("Fout!")
    with t2:
        st.subheader("Woordhusselaar")
        woorden = ["school", "computer", "eiland", "leraar", "punten", "koning", "huiswerk"]
        if 'scramble_w' not in st.session_state:
            gekozen = random.choice(woorden); st.session_state.scramble_w = gekozen
            l = list(gekozen); random.shuffle(l); st.session_state.scramble_q = "".join(l)
        with st.container(border=True):
            st.markdown(f"## {st.session_state.scramble_q.upper()}")
            s_ans = st.text_input("Originele woord?").lower().strip()
            if st.button("Controleer Woord"):
                if s_ans == st.session_state.scramble_w: st.session_state.db['saldi'][mijn_naam] += 20; sla_db_op(); st.toast("+20 🪙"); del st.session_state.scramble_w; st.rerun()
                else: st.error("Fout!")
    with t3:
        st.subheader("Typemachine")
        st.write("Typ de zin **exact** over. Inclusief hoofdletters en leestekens! (Beloning: 30 🪙)")
        if 'type_q' not in st.session_state: st.session_state.type_q = random.choice(TYPE_ZINNEN)
        with st.container(border=True):
            st.markdown(f"### *{st.session_state.type_q}*")
            t_ans = st.text_input("Typ hier:")
            if st.button("Verstuur Zin"):
                if t_ans == st.session_state.type_q: st.session_state.db['saldi'][mijn_naam] += 30; sla_db_op(); st.toast("Snel getypt! +30 🪙"); del st.session_state.type_q; st.rerun()
                else: st.error("Kijk goed naar spelfouten of hoofdletters!")

elif nav == "Raadsels":
    st.title("🧠 Putsie's Hersenkrakers")
    if 'current_riddle' not in st.session_state: st.session_state.current_riddle = random.choice(RAADSELS)
    with st.container(border=True):
        st.markdown(f"### *\"{st.session_state.current_riddle['q']}\"*")
        antwoord = st.text_input("Antwoord (één woord):").lower().strip()
        if st.button("Raad!", type="primary"):
            if antwoord == st.session_state.current_riddle['a']:
                st.session_state.db['saldi'][mijn_naam] += 50; sla_db_op(); st.balloons(); st.success("Briljant! Je krijgt 50 🪙!")
                del st.session_state.current_riddle 
            elif antwoord: st.error("Nee, probeer het nog eens!")
        if 'current_riddle' not in st.session_state:
            if st.button("Nieuw raadsel"): st.rerun()

elif nav == "Eiland Tycoon":
    st.title("🏝️ Eiland Tycoon")
    t1, t2, t3 = st.tabs(["Mijn Eiland", "Bouwmarkt", "Wereldkaart"])
    
    with t1:
        mijn_grid_size = st.session_state.db['island_levels'][mijn_naam]
        eiland_data = st.session_state.db['islands'][mijn_naam]
        mijn_eiland_naam = st.session_state.db['island_names'].get(mijn_naam, f"Eiland van {mijn_naam.capitalize()}")
        mijn_likes = st.session_state.db['island_likes'].get(mijn_naam, 0)
        
        if is_pro: st.markdown(f"<div style='text-align:center;'><div class='island-sign' style='background: linear-gradient(45deg, #FFD700, #FFA500); color: black;'>🌟 {mijn_eiland_naam} 🌟<br><span style='font-size:12px;'>❤️ {mijn_likes} Likes | Weer: {huidig_weer}</span></div></div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='text-align:center;'><div class='island-sign'>🪵 {mijn_eiland_naam}<br><span style='font-size:12px;'>❤️ {mijn_likes} Likes | Weer: {huidig_weer}</span></div></div>", unsafe_allow_html=True)

        c_map, c_controls = st.columns([1.5, 1])
        with c_map:
            fs = max(14, int(160 / mijn_grid_size))
            bg_kleur = "rgba(0,0,0,0.4)"
            if "Sneeuw" in huidig_weer: bg_kleur = "rgba(255,255,255,0.4)"
            elif "Regen" in huidig_weer: bg_kleur = "rgba(0,0,100,0.4)"
            
            # CSS wrapper voor iPad / Mobiel (scrollbaar maken)
            map_html = f"<div class='game-map-wrapper'><div class='game-map' style='font-size: {fs}px; background: {bg_kleur};'>"
            for r in range(mijn_grid_size):
                row_str = ""
                for c in range(mijn_grid_size):
                    pos = f"{r},{c}"
                    if pos in eiland_data: row_str += SHOP_ITEMS.get(eiland_data[pos], {}).get('emoji', '❓')
                    else:
                        if r == 0 or r == mijn_grid_size - 1 or c == 0 or c == mijn_grid_size - 1: row_str += "🟦"
                        else: row_str += "🟩" if "Sneeuw" not in huidig_weer else "⬜"
                map_html += row_str + "<br>"
            st.markdown(map_html + "</div></div>", unsafe_allow_html=True)

        with c_controls:
            st.subheader("🛠️ Bouw Paneel")
            st.write("**Jouw Zakken:**")
            beschikbaar = {item: amount for item, amount in st.session_state.db['inventory'][mijn_naam].items() if amount > 0}
            if beschikbaar:
                inv_html = ""
                for it, am in beschikbaar.items():
                    emo = SHOP_ITEMS.get(it, {}).get('emoji', '❓')
                    inv_html += f"<span class='inventory-badge'>{emo} {it} x{am}</span>"
                st.markdown(inv_html, unsafe_allow_html=True)
            else: st.info("Inventaris is leeg.")
            st.divider()
            
            rij = st.number_input("Rij (Y)", min_value=1, max_value=mijn_grid_size-2, step=1)
            kolom = st.number_input("Kolom (X)", min_value=1, max_value=mijn_grid_size-2, step=1)
            pos_key = f"{rij},{kolom}"
            if pos_key in eiland_data:
                st.info(f"Hier staat een **{eiland_data[pos_key]}**.")
                if st.button("Opbergen", use_container_width=True):
                    item = eiland_data[pos_key]; st.session_state.db['inventory'][mijn_naam][item] = st.session_state.db['inventory'][mijn_naam].get(item, 0) + 1
                    del eiland_data[pos_key]; sla_db_op(); st.rerun()
            else:
                if beschikbaar:
                    kies = st.selectbox("Kies uit inventaris:", list(beschikbaar.keys()))
                    if st.button("Plaats", type="primary", use_container_width=True):
                        st.session_state.db['inventory'][mijn_naam][kies] -= 1; eiland_data[pos_key] = kies; sla_db_op(); st.rerun()

    with t2:
        st.subheader("🎁 Mystery Box")
        st.write("Voor 1500 🪙 krijg je een willekeurig item. Misschien wel het Kasteel!")
        if st.button("Koop Mystery Box (1500 🪙)", type="primary"):
            if mijn_saldo >= 1500:
                st.session_state.db['saldi'][mijn_naam] -= 1500
                gewonnen = random.choice(list(SHOP_ITEMS.keys()))
                st.session_state.db['inventory'][mijn_naam][gewonnen] = st.session_state.db['inventory'][mijn_naam].get(gewonnen, 0) + 1
                sla_db_op(); st.balloons(); st.success(f"🎉 Wauw! Je hebt een {gewonnen} ({SHOP_ITEMS[gewonnen]['emoji']}) gekregen!")
            else: st.error("Te weinig munten!")
        st.divider()
        
        cols = st.columns(4)
        for i, (item, data) in enumerate(SHOP_ITEMS.items()):
            with cols[i % 4]:
                st.markdown(f"<div style='background:rgba(0,0,0,0.2); padding:10px; border-radius:10px; text-align:center;'><h1>{data['emoji']}</h1><b>{item}</b><br>{data['prijs']} 🪙</div>", unsafe_allow_html=True)
                if st.button(f"Koop", key=f"buy_{item}", use_container_width=True):
                    if mijn_saldo >= data['prijs']:
                        st.session_state.db['saldi'][mijn_naam] -= data['prijs']; st.session_state.db['inventory'][mijn_naam][item] = st.session_state.db['inventory'][mijn_naam].get(item, 0) + 1
                        sla_db_op(); st.toast(f"{item} gekocht!"); st.rerun()
                    else: st.error("Te weinig munten!")
        st.divider()
        kosten_upgrade = mijn_grid_size * 5000
        if st.button(f"Vergroot Eiland naar {mijn_grid_size + 1}x{mijn_grid_size + 1} ({kosten_upgrade} 🪙)"):
            if mijn_saldo >= kosten_upgrade:
                st.session_state.db['saldi'][mijn_naam] -= kosten_upgrade; st.session_state.db['island_levels'][mijn_naam] = mijn_grid_size + 1; sla_db_op(); st.balloons(); st.rerun()
            else: st.error("Spaar nog even door!")

    with t3:
        for student in st.session_state.db['users'].keys():
            if student != mijn_naam and st.session_state.db['users'][student].get('role') != 'admin':
                col_a, col_b = st.columns([3, 1])
                ava = st.session_state.db['avatars'].get(student, "👤")
                eiland_n = st.session_state.db['island_names'].get(student, f"Eiland van {student}")
                likes = st.session_state.db['island_likes'].get(student, 0)
                col_a.write(f"**{ava} {eiland_n}** (❤️ {likes})")
                if col_b.button("Bezoeken", key=f"visit_{student}"): st.session_state.visitor_target = student
                    
        if 'visitor_target' in st.session_state:
            target = st.session_state.visitor_target
            t_size = st.session_state.db['island_levels'].get(target, 4)
            t_data = st.session_state.db['islands'].get(target, {})
            t_naam = st.session_state.db['island_names'].get(target, f"Eiland van {target}")
            t_pro = st.session_state.db['is_pro'].get(target, False)
            t_likes = st.session_state.db['island_likes'].get(target, 0)
            st.divider()
            
            if t_pro: st.markdown(f"<div style='text-align:center;'><div class='island-sign' style='background: linear-gradient(45deg, #FFD700, #FFA500); color: black;'>🌟 {t_naam} 🌟</div></div>", unsafe_allow_html=True)
            else: st.markdown(f"<div style='text-align:center;'><div class='island-sign'>🪵 {t_naam}</div></div>", unsafe_allow_html=True)

            _, col_visitor, _ = st.columns([1, 2, 1])
            with col_visitor:
                fs_t = max(14, int(160 / t_size))
                # IPAD BEZOEKERS MAP FIX
                map_html = f"<div class='game-map-wrapper'><div class='game-map' style='font-size: {fs_t}px;'>"
                for r in range(t_size):
                    row_str = ""
                    for c in range(t_size):
                        pos = f"{r},{c}"
                        if pos in t_data: row_str += SHOP_ITEMS.get(t_data[pos], {}).get('emoji', '❓')
                        else:
                            if r == 0 or r == t_size - 1 or c == 0 or c == t_size - 1: row_str += "🟦"
                            else: row_str += "🟩"
                    map_html += row_str + "<br>"
                st.markdown(map_html + "</div></div>", unsafe_allow_html=True)
                
            col_lk, col_bk = st.columns(2)
            if col_lk.button(f"❤️ Geef een Like ({t_likes})", use_container_width=True):
                st.session_state.db['island_likes'][target] += 1; sla_db_op(); st.toast("Like gegeven!"); st.rerun()
            if col_bk.button("Sluiten", use_container_width=True): del st.session_state.visitor_target; st.rerun()

elif nav == "Leraar Paneel" and is_teacher:
    st.title("👩‍🏫 Leraar Dashboard")
    bestaande_klas = None
    for code, info in st.session_state.db.get('classes', {}).items():
        if info['teacher'] == mijn_naam: bestaande_klas = code; break
        
    if not bestaande_klas:
        c_naam = st.text_input("Klasnaam (bijv. Groep 8A)"); c_code = st.text_input("Klascode")
        if st.button("Maak Klas", type="primary"):
            if c_code in st.session_state.db['classes']: st.error("Code bestaat al.")
            else:
                st.session_state.db['classes'][c_code] = {"name": c_naam, "teacher": mijn_naam}
                st.session_state.db['users'][mijn_naam]['class'] = c_code; sla_db_op(); st.rerun()
    else:
        st.info(f"Je beheert **{st.session_state.db['classes'][bestaande_klas]['name']}** (Code: `{bestaande_klas}`)")
        t1, t2, t3, t4, t5 = st.tabs(["👥 Studenten", "📊 Analyse", "📋 Nieuwe Taak", "📖 Vrije Lijst", "🚩 Moderatie"])
        
        with t1:
            alle_leerlingen = [u for u, d in st.session_state.db['users'].items() if d.get('role') == 'student']
            in_mijn_klas = [u for u in alle_leerlingen if st.session_state.db['users'][u].get('class') == bestaande_klas]
            niet_in_klas = [u for u in alle_leerlingen if st.session_state.db['users'][u].get('class') != bestaande_klas]
            for lln in in_mijn_klas:
                col_n, col_k = st.columns([3, 1]); ava = st.session_state.db['avatars'].get(lln, "👤")
                col_n.write(f"- {ava} {lln.capitalize()}")
                if col_k.button("Kick", key=f"kick_{lln}"): st.session_state.db['users'][lln]['class'] = ""; sla_db_op(); st.rerun()
            st.divider()
            if niet_in_klas:
                toevoegen = st.selectbox("Leerling toevoegen:", niet_in_klas)
                if st.button("Voeg toe aan klas"): st.session_state.db['users'][toevoegen]['class'] = bestaande_klas; sla_db_op(); st.rerun()
                
        with t2:
            if in_mijn_klas:
                data = {"Leerling": [], "Rijkdom": [], "Taken Af": []}
                for l in in_mijn_klas:
                    data["Leerling"].append(l.capitalize())
                    data["Rijkdom"].append(st.session_state.db['saldi'][l] + st.session_state.db['bank'][l]['saldo'])
                    data["Taken Af"].append(len(st.session_state.db['completed_tasks'].get(l, [])))
                df = pd.DataFrame(data).set_index("Leerling")
                st.subheader("Rijkdom overzicht (Munten + Bank)")
                st.bar_chart(df["Rijkdom"])
                st.subheader("Gemaakte Taken")
                st.bar_chart(df["Taken Af"])
            else: st.info("Geen leerlingen in klas.")
            
        with t3:
            tt = st.text_input("Titel van de Taak"); tw = st.text_area("Woorden (nl=fr)")
            if st.button("Post Taak", type="primary"):
                d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in tw.split("\n") if "=" in l}
                st.session_state.db['tasks'].append({"id": str(random.randint(10000, 99999)), "title": tt, "words": d, "class": bestaande_klas}); sla_db_op(); st.toast("Taak geplaatst!", icon="🚀")
                
        with t4:
            lt = st.text_input("Lijst Naam"); lw = st.text_area("Woordenlijst (nl=fr)")
            if st.button("Deel Lijst"):
                d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in lw.split("\n") if "=" in l}
                st.session_state.db['vocab_lists'].append({"title": lt, "words": d, "class": bestaande_klas}); sla_db_op(); st.toast("Gedeeld!"); st.rerun()

        with t5:
            st.subheader("🚩 Gemarkeerde Chatberichten")
            flagged_msgs = [m for m in st.session_state.db['chat_messages'] if m.get('class') == bestaande_klas and m.get('flagged') == True]
            if flagged_msgs:
                for m in flagged_msgs: st.error(f"**{m['user'].capitalize()}** typte: '{m.get('original', 'Onbekend')}'")
            else: st.success("De chat is helemaal schoon en veilig!")

elif nav == "Admin Room" and is_admin:
    st.title("👑 Admin Control Room")
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(["🌟 PRO Status", "🕵️ Speler Inspectie", "📢 Aankondiging", "🏷️ Designer", "💰 Economie", "🚩 Moderatie", "💾 RAW"])
    
    with t1:
        pro_doel = st.selectbox("Kies Speler voor PRO", list(st.session_state.db['users'].keys()))
        is_nu_pro = st.session_state.db['is_pro'].get(pro_doel, False)
        if st.button("Geef / Verwijder PRO", type="primary"): st.session_state.db['is_pro'][pro_doel] = not is_nu_pro; sla_db_op(); st.rerun()
    with t2:
        spy_doel = st.selectbox("Wie wil je inspecteren?", list(st.session_state.db['users'].keys()), key="spy_select")
        if spy_doel:
            st.write(f"**Gegevens van {spy_doel.capitalize()}:**")
            st.write(f"- Rol: {st.session_state.db['users'][spy_doel]['role']}")
            st.write(f"- Zakgeld: {st.session_state.db['saldi'][spy_doel]} 🪙 | Bank: {st.session_state.db['bank'][spy_doel]['saldo']} 🪙")
            st.write(f"- Huisdier: {st.session_state.db['pets'][spy_doel].get('name', 'Geen')} (Lvl {st.session_state.db['pets'][spy_doel].get('level', 1)})")
            st.write(f"- Taken Voltooid: {len(st.session_state.db['completed_tasks'].get(spy_doel, []))}")
            if st.button("⚠️ Reset Wachtwoord naar '12345'", type="primary"):
                st.session_state.db['users'][spy_doel]['pw'] = hash_pw("12345"); sla_db_op(); st.success(f"Wachtwoord gereset!")
    with t3:
        huidige_msg = st.session_state.db.get('announcement', "")
        nieuwe_msg = st.text_input("Typ hier een bericht voor ALLE spelers:", value=huidige_msg)
        c_btn1, c_btn2 = st.columns(2)
        if c_btn1.button("Plaats Bericht", type="primary"): st.session_state.db['announcement'] = nieuwe_msg; sla_db_op(); st.rerun()
        if c_btn2.button("Verwijder Bericht"): st.session_state.db['announcement'] = ""; sla_db_op(); st.rerun()
        st.divider()
        st.session_state.db['lockdown'] = st.toggle("Activeer Global Lockdown", value=st.session_state.db.get('lockdown', False))
        l_msg = st.text_input("Lockdown Reden:", value=st.session_state.db.get('lockdown_msg', 'Onderhoud door Elliot'))
        if st.button("Opslaan Systeem Status"): st.session_state.db['lockdown_msg'] = l_msg; sla_db_op(); st.toast("Opgeslagen!")
    with t4:
        col_a, col_b = st.columns(2)
        with col_a:
            new_tag_name = st.text_input("Nieuwe Tag Naam"); new_tag_color = st.color_picker("Kies Kleur", "#FFD700")
            if st.button("Maak Badge"): st.session_state.db['custom_tags_v2'][new_tag_name] = new_tag_color; sla_db_op(); st.success("Gemaakt!")
        with col_b:
            target_user = st.selectbox("Kies Speler", list(st.session_state.db['users'].keys()), key="tag_user")
            target_tag = st.selectbox("Kies Badge", list(st.session_state.db['custom_tags_v2'].keys()))
            c_tag_list = st.session_state.db['player_tags'].setdefault(target_user, [])
            if st.button("Toevoegen"):
                if target_tag not in c_tag_list: c_tag_list.append(target_tag); sla_db_op(); st.rerun()
            if st.button("Verwijderen"):
                if target_tag in c_tag_list: c_tag_list.remove(target_tag); sla_db_op(); st.rerun()
    with t5:
        doel = st.selectbox("Speler", list(st.session_state.db['users'].keys()), key="muntdoel"); bedrag = st.number_input("Bedrag", value=100)
        if st.button("Geef Munten"): st.session_state.db['saldi'][doel] += bedrag; sla_db_op(); st.rerun()
    with t6:
        st.subheader("🚩 Gemarkeerde Chatberichten (Global)")
        flagged_msgs = [m for m in st.session_state.db['chat_messages'] if m.get('flagged') == True]
        if flagged_msgs:
            for m in flagged_msgs: st.error(f"**{m['user'].capitalize()}** (Klas {m.get('class')}) typte: '{m.get('original', 'Onbekend')}'")
            if st.button("Verwijder alle vlaggen (Schoonmaken)"):
                for m in st.session_state.db['chat_messages']: m['flagged'] = False
                sla_db_op(); st.rerun()
        else: st.success("De chat is overal schoon en veilig!")
        st.divider()
        st.subheader("🤬 Scheldwoorden Filter")
        huidige_woorden = ", ".join(st.session_state.db.get('bad_words', []))
        nieuwe_woorden = st.text_area("Verboden woorden (gescheiden door komma):", value=huidige_woorden)
        if st.button("Filter Opslaan", type="primary"):
            st.session_state.db['bad_words'] = [w.strip().lower() for w in nieuwe_woorden.split(",") if w.strip()]; sla_db_op(); st.success("Filter opgeslagen!"); st.rerun()
    with t7:
        if st.button("Wis Alle Taken & Lijsten"):
            st.session_state.db['tasks'] = []; st.session_state.db['vocab_lists'] = []; st.session_state.db['completed_tasks'] = {u: [] for u in st.session_state.db['users'].keys()}; sla_db_op(); st.rerun()
        raw = st.text_area("JSON Editor", value=json.dumps(st.session_state.db, indent=2), height=300)
        if st.button("Force Save"):
            try: st.session_state.db = json.loads(raw); sla_db_op(); st.rerun()
            except: st.error("JSON Fout!")
