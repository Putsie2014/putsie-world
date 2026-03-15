import streamlit as st
import random
import json
import os
import hashlib
import html
from datetime import datetime, timedelta
import pandas as pd # NIEUW VOOR GRAFIEKEN!

try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' en 'pandas' ontbreken in requirements.txt")

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie WORLD 🎓 v25.0 MASTERPIECE"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# --- SECURITY ---
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
        .stApp {{
            background: {theme_bg};
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: white;
        }}
        @keyframes gradientBG {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div, .stTabs {{
            background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(12px); border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3); padding: 15px; color: white !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        p, span, label, h1, h2, h3 {{ color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); }}
        .stButton button {{ transition: all 0.3s ease 0s !important; border-radius: 10px !important; }}
        .stButton button:hover {{ transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4) !important; }}
        .hacker-term {{ background-color: #050505 !important; color: #0f0 !important; font-family: 'Courier New', Courier, monospace !important; padding: 25px; border-radius: 12px; border: 2px solid #0f0; box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); }}
        input, textarea {{ color: black !important; text-shadow: none !important; }}
        
        /* BADGES */
        .custom-badge {{ color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px; margin-right: 5px; display: inline-block; text-shadow: 1px 1px 2px black; border: 1px solid rgba(255,255,255,0.3); }}
        .pro-badge {{ background: linear-gradient(45deg, #FFD700, #FF8C00); color: white; padding: 2px 8px; border-radius: 10px; font-weight: 900; font-size: 12px; margin-right: 5px; display: inline-block; text-shadow: 1px 1px 2px black; box-shadow: 0 0 10px rgba(255,215,0,0.8); animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
        .mood-text {{ font-style: italic; color: rgba(255,255,255,0.7) !important; font-size: 0.9em; }}
        .title-badge {{ background: #9c27b0; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; font-style: italic; margin-right: 5px; }}
        .lvl-badge {{ background: #4CAF50; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; margin-right: 5px; }}
        
        /* EILAND */
        .game-map {{ text-align: center; line-height: 1.05; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 15px; border: 3px solid #fdbb2d; display: inline-block; box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 10px 30px rgba(0,0,0,0.5); }}
        .island-sign {{ font-size: 24px; color: white; background: rgba(139, 69, 19, 0.8); padding: 5px 20px; border-radius: 5px; border: 2px solid #5C4033; font-weight: bold; margin-bottom: 15px; display: inline-block; text-shadow: 2px 2px 4px black; }}
        .net-worth {{ font-size: 20px; color: gold; font-weight: bold; background: rgba(0,0,0,0.5); padding: 5px 15px; border-radius: 20px; display: inline-block; margin-bottom: 10px;}}
        .achievement-card {{ background: rgba(255, 215, 0, 0.2); border: 1px solid gold; padding: 10px; border-radius: 10px; text-align: center; }}
        
        /* PET SYSTEM */
        .pet-box {{ background: rgba(255,255,255,0.1); border: 2px dashed #00d2ff; padding: 20px; border-radius: 15px; text-align: center; }}
        .pet-emoji {{ font-size: 60px; filter: drop-shadow(0px 10px 10px rgba(0,0,0,0.5)); transition: transform 0.2s; }}
        .pet-emoji:hover {{ transform: translateY(-10px); }}
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
    "Papegaai": {"prijs": 4000, "emoji": "🦜"}, "Mini-Draak": {"prijs": 10000, "emoji": "🐉"}
}
RAADSELS = [
    {"q": "Wat heeft tanden maar kan niet bijten?", "a": "kam"}, {"q": "Wat wordt natter naarmate het meer droogt?", "a": "handdoek"},
    {"q": "Ik heb steden maar geen huizen, water maar geen vissen.", "a": "landkaart"}, {"q": "Hoe meer je ervan weghaalt, hoe groter het wordt.", "a": "gat"}
]
AVATARS = ["👤", "😎", "🤓", "🤠", "🤖", "👽", "👻", "🐵", "🦁", "🦄", "🐉", "🦊", "👑", "🚀", "💎", "🔥", "⚡"]
WEER_TYPES = ["☀️ Zonnig", "🌧️ Regenachtig", "❄️ Sneeuw", "⚡ Onweer", "🌈 Regenboog"]

# Bepaal het weer van vandaag (is voor iedereen hetzelfde per dag)
vandaag = datetime.now().strftime("%Y-%m-%d")
random.seed(vandaag)
huidig_weer = random.choice(WEER_TYPES)
random.seed() # Reset seed voor normale random dingen

# --- 3. BULLETPROOF DATABASE ENGINE ---
def laad_db():
    basis_db = {"users": {"elliot": {"pw": hash_pw("Putsie"), "role": "admin", "class": "ADMIN-000"}}}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: return basis_db
    return basis_db

def sla_db_op():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.db, f, separators=(',', ':'))
    except Exception as e: st.error(f"🚨 Fout bij opslaan: {e}")

if 'db' not in st.session_state: st.session_state.db = laad_db()

safe_defaults = {
    "users": {"elliot": {"pw": hash_pw("Putsie"), "role": "admin", "class": "ADMIN-000"}},
    "classes": {"ADMIN-000": {"name": "Admin Base", "teacher": "elliot"}},
    "saldi": {}, "bank": {}, "ai_points": {}, "user_vocab": {}, "chat_messages": [], "vocab_lists": [],
    "tasks": [], "completed_tasks": {}, "chat_tags": {}, "custom_tags": ["👑 ADMIN", "⭐ VIP", "🔥 STRIJDER"],
    "custom_tags_v2": {"👑 ADMIN": "#FFD700", "⭐ VIP": "#FF4B4B", "🔥 STRIJDER": "#FFA500"},
    "player_tags": {}, "streaks": {}, "avatars": {}, "moods": {}, "islands": {}, 
    "island_levels": {}, "inventory": {}, "island_names": {}, "is_pro": {},
    "unlocked_achievements": {}, "equipped_achievement": {}, "themes": {}, "pets": {},
    "islands_enabled": False, "lockdown": False, "lockdown_msg": "Systeem onderhoud door Elliot"
}

for key, default_val in safe_defaults.items():
    st.session_state.db.setdefault(key, default_val)

def verifieer_speler_data(naam):
    st.session_state.db['saldi'].setdefault(naam, 100) # Iedereen start met 100
    st.session_state.db['bank'].setdefault(naam, {"saldo": 0, "last_interest": vandaag})
    st.session_state.db['ai_points'].setdefault(naam, 5)
    st.session_state.db['user_vocab'].setdefault(naam, {})
    st.session_state.db['completed_tasks'].setdefault(naam, [])
    st.session_state.db['islands'].setdefault(naam, {})
    st.session_state.db['island_levels'].setdefault(naam, 4)
    st.session_state.db['inventory'].setdefault(naam, {})
    st.session_state.db['avatars'].setdefault(naam, "👤")
    st.session_state.db['moods'].setdefault(naam, "")
    st.session_state.db['streaks'].setdefault(naam, {"date": "", "count": 0})
    st.session_state.db['player_tags'].setdefault(naam, [])
    st.session_state.db['island_names'].setdefault(naam, f"Eiland van {naam.capitalize()}")
    st.session_state.db['is_pro'].setdefault(naam, False)
    st.session_state.db['unlocked_achievements'].setdefault(naam, [])
    st.session_state.db['equipped_achievement'].setdefault(naam, "")
    st.session_state.db['themes'].setdefault(naam, "Standaard")
    st.session_state.db['pets'].setdefault(naam, {"type": None, "name": "", "hunger": 100, "happiness": 100, "level": 1})
    st.session_state.db['users'][naam].setdefault('class', "")
    
    # BANK RENTE LOGICA! Bereken rente als het een nieuwe dag is
    last_int = st.session_state.db['bank'][naam]['last_interest']
    if last_int != vandaag and st.session_state.db['bank'][naam]['saldo'] > 0:
        rente = int(st.session_state.db['bank'][naam]['saldo'] * 0.05) # 5% rente
        st.session_state.db['bank'][naam]['saldo'] += rente
        st.session_state.db['bank'][naam]['last_interest'] = vandaag
        # We geven geen toast hier om spam bij login te voorkomen, ze zien het op de bank pagina.
        
    sla_db_op()

# --- 4. LOGIN & REGISTRATIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    apply_premium_design(THEMES["Standaard"])
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center;'>{SITE_TITLE}</h1>", unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔑 Log In", "📝 Registreren"])
        
        with t_log:
            u = st.text_input("Naam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Start Game", type="primary", use_container_width=True):
                hashed_p = hash_pw(p)
                if u == "admin2014": st.session_state.in_terminal = True; st.rerun()
                elif u == "elliot" and p == "Putsie":
                    verifieer_speler_data("elliot")
                    st.session_state.db['is_pro']['elliot'] = True
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"
                    st.rerun()
                elif u in st.session_state.db['users']:
                    stored_pw = st.session_state.db['users'][u]["pw"]
                    if stored_pw == hashed_p or stored_pw == p:
                        if stored_pw == p: st.session_state.db['users'][u]["pw"] = hashed_p; sla_db_op()
                        verifieer_speler_data(u)
                        st.session_state.ingelogd, st.session_state.username = True, u
                        st.session_state.role = st.session_state.db['users'][u]["role"]
                        st.rerun()
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
                    st.success("✅ Account veilig aangemaakt! Log in.")
    st.stop()

verifieer_speler_data(st.session_state.username)

# Pas thema van de speler toe
mijn_thema_naam = st.session_state.db['themes'].get(st.session_state.username, "Standaard")
apply_premium_design(THEMES.get(mijn_thema_naam, THEMES["Standaard"]))

# --- TERMINAL ---
if st.session_state.get('in_terminal', False):
    st.markdown("<div class='hacker-term'><h1>>_ SYSTEM OVERRIDE V25.0</h1><p>Type /exit to leave.</p></div>", unsafe_allow_html=True)
    cmd = st.text_input(">").strip()
    if cmd == "/deactivatelockdown": st.session_state.db['lockdown'] = False; sla_db_op(); st.toast("🔓 Lockdown gedeactiveerd!")
    elif cmd.startswith("/openaccount"):
        target = cmd.split(" ")[1].lower() if len(cmd.split(" ")) > 1 else ""
        if target in st.session_state.db['users'] or target == "elliot":
            verifieer_speler_data(target)
            st.session_state.ingelogd, st.session_state.username = True, target
            st.session_state.role = st.session_state.db['users'].get(target, {}).get("role", "admin")
            st.session_state.lockdown_bypass, st.session_state.in_terminal = True, False; st.rerun()
    elif cmd == "/exit": st.session_state.in_terminal = False; st.rerun()
    st.stop() 

# --- 5. LOGICA & SIDEBAR ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"
is_pro = st.session_state.db['is_pro'].get(mijn_naam, False)
mijn_klas = st.session_state.db['users'][mijn_naam].get("class", "")

if st.session_state.db.get('lockdown') and not is_admin:
    st.markdown(f"<div style='text-align:center; padding:100px; background: rgba(255,0,0,0.5); border-radius:20px;'><h1>🚫 LOCKDOWN</h1><h3>{st.session_state.db['lockdown_msg']}</h3></div>", unsafe_allow_html=True)
    if st.button("Uitloggen"): st.session_state.ingelogd = False; st.rerun()
    st.stop()

mijn_saldo = st.session_state.db['saldi'][mijn_naam]
mijn_bank = st.session_state.db['bank'][mijn_naam]['saldo']
mijn_level = ((mijn_saldo + mijn_bank) // 500) + 1 
mijn_tags = st.session_state.db['player_tags'][mijn_naam]
mijn_avatar = st.session_state.db['avatars'][mijn_naam]
mijn_streak_data = st.session_state.db['streaks'][mijn_naam]
mijn_pet = st.session_state.db['pets'][mijn_naam]

if mijn_level < 5: speler_titel = "Brugpieper"
elif mijn_level < 10: speler_titel = "Gevorderde"
elif mijn_level < 20: speler_titel = "Pro Speler"
elif mijn_level < 50: speler_titel = "Putsie Legende"
else: speler_titel = "God van Putsie World"

gisteren = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

with st.sidebar:
    badge_html = "<span class='pro-badge'>🌟 PRO</span>" if is_pro else ""
    for t_name in mijn_tags:
        color = st.session_state.db['custom_tags_v2'].get(t_name, "#888888")
        badge_html += f"<span class='custom-badge' style='background:{color}'>{t_name}</span>"
    
    st.markdown(f"<h3>{mijn_avatar} {mijn_naam.capitalize()}</h3>{badge_html}", unsafe_allow_html=True)
    st.markdown(f"<span class='title-badge'>{speler_titel}</span> ⭐ Lvl: {mijn_level}", unsafe_allow_html=True)
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
    nav_options = ["👤 Mijn Profiel", "🏫 Klas", "🏦 Putsie Bank", "🐾 Dierenwinkel", "🎮 Game Hal", "🇫🇷 Frans Lab", "🤖 AI Hulp"]
    if st.session_state.db.get('islands_enabled', False): nav_options.insert(1, "🏝️ Tycoon Eiland")
    if is_teacher: nav_options.append("👩‍🏫 Leraar Paneel")
    if is_admin: nav_options.append("👑 Admin Room")
    
    nav = st.radio("Menu", nav_options)
    
    st.divider()
    st.subheader("🏆 Rijkste Spelers")
    top_spelers = sorted([(u, st.session_state.db['saldi'][u] + st.session_state.db['bank'][u]['saldo']) for u in st.session_state.db['users'].keys() if st.session_state.db['users'][u].get('role') != 'admin'], key=lambda x: x[1], reverse=True)[:3]
    for i, (u, total_wealth) in enumerate(top_spelers):
        med = ["🥇", "🥈", "🥉"][i] if i < 3 else ""
        ava = st.session_state.db['avatars'].get(u, "👤")
        pro_star = "🌟" if st.session_state.db['is_pro'].get(u, False) else ""
        st.markdown(f"**{med} {ava} {u.capitalize()} {pro_star}** - {total_wealth} 🪙")
        
    st.divider()
    if st.button("🚪 Uitloggen"): st.session_state.ingelogd = False; st.rerun()

# --- 8. PAGINA'S ---

if nav == "👤 Mijn Profiel":
    st.title("👤 Jouw Profiel")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Instellingen")
        nieuwe_ava = st.selectbox("Kies Avatar", AVATARS, index=AVATARS.index(mijn_avatar) if mijn_avatar in AVATARS else 0)
        nieuwe_mood = st.text_input("Wat is je mood in de chat?", value=st.session_state.db['moods'].get(mijn_naam, ""), max_chars=30)
        huidige_eiland_naam = st.session_state.db['island_names'].get(mijn_naam, f"Eiland van {mijn_naam.capitalize()}")
        nieuwe_eiland_naam = st.text_input("Naam van jouw Eiland (Bordje):", value=huidige_eiland_naam, max_chars=25)
        
        nieuw_thema = st.selectbox("Kies Website Thema", list(THEMES.keys()), index=list(THEMES.keys()).index(mijn_thema_naam))
        
        if st.button("Profiel Opslaan", type="primary"):
            st.session_state.db['avatars'][mijn_naam] = nieuwe_ava
            st.session_state.db['moods'][mijn_naam] = nieuwe_mood
            st.session_state.db['island_names'][mijn_naam] = nieuwe_eiland_naam
            st.session_state.db['themes'][mijn_naam] = nieuw_thema
            sla_db_op(); st.toast("Opgeslagen!", icon="✅"); st.rerun()
            
    with c2:
        st.subheader("Jouw Badges")
        if is_pro:
            st.markdown("<span class='pro-badge'>🌟 PUTSIE PRO LID</span>", unsafe_allow_html=True)
            st.write("Geniet van 2x dagelijkse munten en een gouden eilandbordje!")
        if mijn_tags:
            for t in mijn_tags:
                c = st.session_state.db['custom_tags_v2'].get(t, "#888888")
                st.markdown(f"<span class='custom-badge' style='background:{c}'>{t}</span>", unsafe_allow_html=True)
        elif not is_pro:
            st.write("Je hebt nog geen badges. Vraag de Admin!")

elif nav == "🏦 Putsie Bank":
    st.title("🏦 De Putsie Bank")
    st.write("Zet je munten op de bank en ontvang elke dag **5% rente**!")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    col_b1.metric("Contant Geld", f"{mijn_saldo} 🪙")
    col_b2.metric("Saldo Bankrekening", f"{mijn_bank} 🪙")
    col_b3.metric("Verwachte Rente Morgen", f"+{int(mijn_bank * 0.05)} 🪙")
    
    st.divider()
    c_storten, c_opnemen = st.columns(2)
    with c_storten:
        st.subheader("Geld Storten")
        stort_bedrag = st.number_input("Hoeveel wil je storten?", min_value=0, max_value=mijn_saldo, step=10)
        if st.button("Storten", type="primary"):
            if stort_bedrag > 0 and mijn_saldo >= stort_bedrag:
                st.session_state.db['saldi'][mijn_naam] -= stort_bedrag
                st.session_state.db['bank'][mijn_naam]['saldo'] += stort_bedrag
                sla_db_op(); st.toast("Geld gestort!", icon="🏦"); st.rerun()
    with c_opnemen:
        st.subheader("Geld Opnemen")
        opneem_bedrag = st.number_input("Hoeveel wil je opnemen?", min_value=0, max_value=mijn_bank, step=10)
        if st.button("Opnemen"):
            if opneem_bedrag > 0 and mijn_bank >= opneem_bedrag:
                st.session_state.db['bank'][mijn_naam]['saldo'] -= opneem_bedrag
                st.session_state.db['saldi'][mijn_naam] += opneem_bedrag
                sla_db_op(); st.toast("Geld opgenomen!", icon="💸"); st.rerun()

elif nav == "🐾 Dierenwinkel":
    st.title("🐾 Virtuele Dierenwinkel")
    st.write("Koop en verzorg je eigen Putsie Pet!")
    
    if not mijn_pet.get('type'):
        st.subheader("Kies een huisdier:")
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
        c_pet_img, c_pet_stats = st.columns([1, 2])
        with c_pet_img:
            st.markdown(f"<div style='text-align:center;'><span class='pet-emoji' style='font-size:120px;'>{mijn_pet.get('emoji', '❓')}</span></div>", unsafe_allow_html=True)
            nieuwe_pet_naam = st.text_input("Naam veranderen:", value=mijn_pet.get('name', ''))
            if st.button("Hernoem"):
                st.session_state.db['pets'][mijn_naam]['name'] = nieuwe_pet_naam; sla_db_op(); st.rerun()
        with c_pet_stats:
            # Honger en Blijheid nemen af per dag/login
            st.progress(mijn_pet['hunger'] / 100, text=f"Voedsel: {mijn_pet['hunger']}%")
            st.progress(mijn_pet['happiness'] / 100, text=f"Blijheid: {mijn_pet['happiness']}%")
            st.write(f"**Level:** {mijn_pet['level']}")
            
            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("🍎 Voeren (Kost 10 🪙)", use_container_width=True):
                if mijn_saldo >= 10:
                    st.session_state.db['saldi'][mijn_naam] -= 10
                    st.session_state.db['pets'][mijn_naam]['hunger'] = min(100, mijn_pet['hunger'] + 20)
                    sla_db_op(); st.toast("Nom nom!"); st.rerun()
                else: st.error("Geen geld voor eten!")
            if c_btn2.button("🎾 Spelen", use_container_width=True):
                st.session_state.db['pets'][mijn_naam]['happiness'] = min(100, mijn_pet['happiness'] + 15)
                st.session_state.db['pets'][mijn_naam]['hunger'] = max(0, mijn_pet['hunger'] - 5) # Spelen kost energie
                
                # Level up logica
                if random.random() > 0.7:
                    st.session_state.db['pets'][mijn_naam]['level'] += 1
                    st.toast(f"Je huisdier is nu Level {st.session_state.db['pets'][mijn_naam]['level']}!", icon="🆙")
                sla_db_op(); st.rerun()

elif nav == "🎮 Game Hal":
    st.title("🎮 De Game Hal")
    t1, t2, t3 = st.tabs(["🧠 Raadsels", "🧮 Rekenwonder", "🔤 Woordhusselaar"])
    
    with t1:
        st.subheader("Hersenkrakers")
        if 'current_riddle' not in st.session_state: st.session_state.current_riddle = random.choice(RAADSELS)
        with st.container(border=True):
            st.markdown(f"### *\"{st.session_state.current_riddle['q']}\"*")
            antwoord = st.text_input("Jouw antwoord (één woord):").lower().strip()
            if st.button("Raad!", type="primary"):
                if antwoord == st.session_state.current_riddle['a']:
                    st.session_state.db['saldi'][mijn_naam] += 50; sla_db_op(); st.balloons(); st.success("Briljant! Je krijgt 50 🪙!")
                    del st.session_state.current_riddle 
                elif antwoord: st.error("Nee, probeer het nog eens!")
            if 'current_riddle' not in st.session_state:
                if st.button("Nieuw raadsel"): st.rerun()

    with t2:
        st.subheader("Rekenwonder")
        st.write("Los wiskunde sommen op voor 10 munten per stuk!")
        if 'math_q' not in st.session_state:
            a = random.randint(1, 100); b = random.randint(1, 100); op = random.choice(["+", "-", "*"])
            if op == "-": a, b = max(a,b), min(a,b) # Geen negatieve getallen
            if op == "*": a = random.randint(1, 10); b = random.randint(1, 10) # Makkelijke tafels
            st.session_state.math_q = f"{a} {op} {b}"
            st.session_state.math_a = eval(st.session_state.math_q)
            
        with st.container(border=True):
            st.markdown(f"## Wat is {st.session_state.math_q} ?")
            m_ans = st.number_input("Antwoord:", step=1, format="%d")
            if st.button("Controleer Som"):
                if m_ans == st.session_state.math_a:
                    st.session_state.db['saldi'][mijn_naam] += 10; sla_db_op(); st.toast("Goed zo! +10 🪙"); del st.session_state.math_q; st.rerun()
                else: st.error("Fout!")
                
    with t3:
        st.subheader("Woordhusselaar")
        st.write("Zet de letters in de juiste volgorde (Beloning: 20 munten)")
        woorden = ["school", "computer", "eiland", "leraar", "punten", "koning", "huiswerk"]
        if 'scramble_w' not in st.session_state:
            gekozen = random.choice(woorden)
            st.session_state.scramble_a = gekozen
            l = list(gekozen); random.shuffle(l); st.session_state.scramble_q = "".join(l)
        
        with st.container(border=True):
            st.markdown(f"## {st.session_state.scramble_q.upper()}")
            s_ans = st.text_input("Wat is het originele woord?").lower().strip()
            if st.button("Controleer Woord"):
                if s_ans == st.session_state.scramble_a:
                    st.session_state.db['saldi'][mijn_naam] += 20; sla_db_op(); st.toast("Knap! +20 🪙"); del st.session_state.scramble_w; st.rerun()
                else: st.error("Niet correct!")

elif nav == "🏫 Klas":
    st.title("🏫 Jouw Klas")
    if not mijn_klas:
        code = st.text_input("Klascode:")
        if st.button("Join"):
            if code in st.session_state.db['classes']:
                st.session_state.db['users'][mijn_naam]['class'] = code; sla_db_op(); st.rerun()
            else: st.error("Foutieve code.")
    else:
        k_info = st.session_state.db['classes'].get(mijn_klas, {"name": "Onbekend"})
        st.subheader(f"Klas: {k_info['name']}")
        t_tasks, t_chat = st.tabs(["📋 Taken & Bestanden", "💬 Klas Chat"])
        
        with t_tasks:
            beschikbare_taken = [t for t in st.session_state.db['tasks'] if t.get('id', t.get('title')) not in st.session_state.db['completed_tasks'].get(mijn_naam, []) and t.get('class') in [mijn_klas, None, ""]]
            if beschikbare_taken:
                for t in beschikbare_taken:
                    st.write(f"**{t.get('title')}**")
                    if st.button("Markeer als af", key=t.get('id')):
                        st.session_state.db['completed_tasks'][mijn_naam].append(t.get('title')); st.session_state.db['saldi'][mijn_naam] += 100; sla_db_op(); st.rerun()
            else: st.success("Alle taken zijn af!")
            
            st.divider()
            st.write("**Gedeelde Bestanden/Lijsten:**")
            lijsten_voor_klas = [l for l in st.session_state.db.get('vocab_lists', []) if l.get('class') in [mijn_klas, None, ""]]
            for i, v in enumerate(lijsten_voor_klas):
                if st.button(f"📥 Download {v['title']}", key=f"dl_{i}"):
                    st.session_state.db['user_vocab'][mijn_naam].update(v['words']); sla_db_op(); st.toast("Toegevoegd aan Lab!", icon="📚")
            
        with t_chat:
            with st.container(height=400, border=True):
                for m in [msg for msg in st.session_state.db['chat_messages'] if msg.get('class') == mijn_klas]:
                    u = m['user']
                    ava = st.session_state.db['avatars'].get(u, "👤")
                    mood = st.session_state.db['moods'].get(u, "")
                    tags = st.session_state.db['player_tags'].get(u, [])
                    u_pro = "<span class='pro-badge'>🌟 PRO</span>" if st.session_state.db['is_pro'].get(u, False) else ""
                    b_html = "".join([f"<span class='custom-badge' style='background:{st.session_state.db['custom_tags_v2'].get(tn, '#888888')}'>{tn}</span>" for tn in tags])
                    st.markdown(f"{ava} **{u.capitalize()}** {u_pro}{b_html} <br> <span class='mood-text'>{mood}</span> <br> {m['text']}", unsafe_allow_html=True)
            
            if p := st.chat_input("Typ een bericht..."):
                st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": html.escape(p), "class": mijn_klas})
                sla_db_op(); st.rerun()

elif nav == "🏝️ Tycoon Eiland":
    st.title("🏝️ Eiland Tycoon")
    t1, t2, t3 = st.tabs(["Mijn Eiland", "Bouwmarkt", "Wereldkaart"])
    
    with t1:
        mijn_grid_size = st.session_state.db['island_levels'][mijn_naam]
        eiland_data = st.session_state.db['islands'][mijn_naam]
        mijn_eiland_naam = st.session_state.db['island_names'].get(mijn_naam, f"Eiland van {mijn_naam.capitalize()}")
        
        if is_pro: st.markdown(f"<div style='text-align:center;'><div class='island-sign' style='background: linear-gradient(45deg, #FFD700, #FFA500); border-color: #B8860B; color: black;'>🌟 {mijn_eiland_naam} 🌟<br><span style='font-size:12px;'>Weer: {huidig_weer}</span></div></div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='text-align:center;'><div class='island-sign'>🪵 {mijn_eiland_naam}<br><span style='font-size:12px;'>Weer: {huidig_weer}</span></div></div>", unsafe_allow_html=True)

        c_map, c_controls = st.columns([1.5, 1])
        with c_map:
            fs = max(14, int(160 / mijn_grid_size))
            
            # Achtergrond verandert op basis van weer!
            bg_kleur = "rgba(0,0,0,0.4)"
            if "Sneeuw" in huidig_weer: bg_kleur = "rgba(255,255,255,0.4)"
            elif "Regen" in huidig_weer: bg_kleur = "rgba(0,0,100,0.4)"
            
            map_html = f"<div class='game-map' style='font-size: {fs}px; background: {bg_kleur};'>"
            for r in range(mijn_grid_size):
                row_str = ""
                for c in range(mijn_grid_size):
                    pos = f"{r},{c}"
                    if pos in eiland_data: row_str += SHOP_ITEMS.get(eiland_data[pos], {}).get('emoji', '❓')
                    else:
                        if r == 0 or r == mijn_grid_size - 1 or c == 0 or c == mijn_grid_size - 1: row_str += "🟦"
                        else: row_str += "🟩" if "Sneeuw" not in huidig_weer else "⬜" # Sneeuw eiland!
                map_html += row_str + "<br>"
            st.markdown(map_html + "</div>", unsafe_allow_html=True)

        with c_controls:
            st.subheader("🛠️ Bouw Paneel")
            rij = st.number_input("Rij (Y)", min_value=1, max_value=mijn_grid_size-2, step=1)
            kolom = st.number_input("Kolom (X)", min_value=1, max_value=mijn_grid_size-2, step=1)
            pos_key = f"{rij},{kolom}"
            if pos_key in eiland_data:
                st.info(f"Hier staat een **{eiland_data[pos_key]}**.")
                if st.button("Opbergen", use_container_width=True):
                    item = eiland_data[pos_key]; st.session_state.db['inventory'][mijn_naam][item] = st.session_state.db['inventory'][mijn_naam].get(item, 0) + 1
                    del eiland_data[pos_key]; sla_db_op(); st.rerun()
            else:
                beschikbaar = [item for item, amount in st.session_state.db['inventory'][mijn_naam].items() if amount > 0]
                if beschikbaar:
                    kies = st.selectbox("Kies uit inventaris:", beschikbaar)
                    if st.button("Plaats", type="primary", use_container_width=True):
                        st.session_state.db['inventory'][mijn_naam][kies] -= 1; eiland_data[pos_key] = kies; sla_db_op(); st.rerun()
                else: st.warning("Inventaris leeg!")

    with t2:
        st.subheader("🛒 De Bouwmarkt")
        cols = st.columns(4)
        for i, (item, data) in enumerate(SHOP_ITEMS.items()):
            with cols[i % 4]:
                st.markdown(f"<div style='background:rgba(0,0,0,0.2); padding:10px; border-radius:10px; text-align:center;'><h1>{data['emoji']}</h1><b>{item}</b><br>{data['prijs']} 🪙</div>", unsafe_allow_html=True)
                if st.button(f"Koop", key=f"buy_{item}", use_container_width=True):
                    if mijn_saldo >= data['prijs']:
                        st.session_state.db['saldi'][mijn_naam] -= data['prijs']
                        st.session_state.db['inventory'][mijn_naam][item] = st.session_state.db['inventory'][mijn_naam].get(item, 0) + 1
                        sla_db_op(); st.toast(f"{item} gekocht!"); st.rerun()
                    else: st.error("Te weinig munten!")

    with t3:
        st.subheader("Bezoek Klasgenoten")
        for student in st.session_state.db['users'].keys():
            if student != mijn_naam and st.session_state.db['users'][student].get('role') != 'admin':
                col_a, col_b = st.columns([3, 1])
                ava = st.session_state.db['avatars'].get(student, "👤")
                eiland_n = st.session_state.db['island_names'].get(student, f"Eiland van {student}")
                col_a.write(f"**{ava} {eiland_n}**")
                if col_b.button("Bezoeken", key=f"visit_{student}"): st.session_state.visitor_target = student
                    
        if 'visitor_target' in st.session_state:
            target = st.session_state.visitor_target
            t_size = st.session_state.db['island_levels'].get(target, 4)
            t_data = st.session_state.db['islands'].get(target, {})
            t_naam = st.session_state.db['island_names'].get(target, f"Eiland van {target}")
            t_pro = st.session_state.db['is_pro'].get(target, False)
            st.divider()
            
            if t_pro: st.markdown(f"<div style='text-align:center;'><div class='island-sign' style='background: linear-gradient(45deg, #FFD700, #FFA500); color: black;'>🌟 {t_naam} 🌟</div></div>", unsafe_allow_html=True)
            else: st.markdown(f"<div style='text-align:center;'><div class='island-sign'>🪵 {t_naam}</div></div>", unsafe_allow_html=True)

            _, col_visitor, _ = st.columns([1, 2, 1])
            with col_visitor:
                fs_t = max(14, int(160 / t_size))
                map_html = f"<div class='game-map' style='font-size: {fs_t}px;'>"
                for r in range(t_size):
                    row_str = ""
                    for c in range(t_size):
                        pos = f"{r},{c}"
                        if pos in t_data: row_str += SHOP_ITEMS.get(t_data[pos], {}).get('emoji', '❓')
                        else:
                            if r == 0 or r == t_size - 1 or c == 0 or c == t_size - 1: row_str += "🟦"
                            else: row_str += "🟩"
                    map_html += row_str + "<br>"
                st.markdown(map_html + "</div>", unsafe_allow_html=True)
            if st.button("Terug naar Wereldkaart"): del st.session_state.visitor_target; st.rerun()

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Oefen Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'q' not in st.session_state: st.session_state.q = random.choice(list(w.keys()))
        g = st.text_input(f"Vertaal: {st.session_state.q}")
        if st.button("Controleren", type="primary"):
            if g.lower().strip() == w[st.session_state.q].lower().strip():
                st.session_state.db['saldi'][mijn_naam] += 20; del st.session_state.q; sla_db_op(); st.rerun()
            else: st.error("Helaas!")
    else: st.info("Geen woorden in je lijst.")

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    c1, c2 = st.columns([2, 1])
    with c2:
        if st.button(f"Koop 1 💎 voor {AI_PUNT_PRIJS} 🪙", use_container_width=True):
            if mijn_saldo >= AI_PUNT_PRIJS:
                st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS; st.session_state.db['ai_points'][mijn_naam] += 1; sla_db_op(); st.rerun()
            else: st.error("Te weinig munten!")
    with c1:
        vraag = st.text_area("Stel je vraag:")
        if st.button("Vraag stellen (-1 💎)", type="primary"):
            if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(messages=[{"role": "user", "content": vraag}], model=MODEL_NAAM)
                    st.session_state.ai_res = res.choices[0].message.content; st.session_state.db['ai_points'][mijn_naam] -= 1; sla_db_op()
                except Exception as e: st.error(f"AI Fout.")
            else: st.warning("Te weinig AI punten!")
        if 'ai_res' in st.session_state: st.info(st.session_state.ai_res)

elif nav == "👩‍🏫 Leraar Paneel" and is_teacher:
    st.title("👩‍🏫 Leraar Dashboard")
    bestaande_klas = None
    for code, info in st.session_state.db.get('classes', {}).items():
        if info['teacher'] == mijn_naam: bestaande_klas = code; break
        
    if not bestaande_klas:
        c_naam = st.text_input("Kies een Klasnaam (bijv. Groep 8A)"); c_code = st.text_input("Bedenk een Klascode")
        if st.button("Klas Aanmaken", type="primary"):
            if c_naam and c_code:
                if c_code in st.session_state.db['classes']: st.error("Code bestaat al.")
                else:
                    st.session_state.db['classes'][c_code] = {"name": c_naam, "teacher": mijn_naam}
                    st.session_state.db['users'][mijn_naam]['class'] = c_code; sla_db_op(); st.rerun()
    else:
        k_info = st.session_state.db['classes'][bestaande_klas]
        st.info(f"Je beheert **{k_info['name']}** (Code: `{bestaande_klas}`)")
        t1, t2, t3, t4 = st.tabs(["👥 Studenten", "📊 Klas Analyse", "📋 Nieuwe Taak", "📖 Vrije Lijst"])
        
        with t1:
            alle_leerlingen = [u for u, d in st.session_state.db['users'].items() if d.get('role') == 'student']
            in_mijn_klas = [u for u in alle_leerlingen if st.session_state.db['users'][u].get('class') == bestaande_klas]
            for lln in in_mijn_klas:
                col_n, col_k = st.columns([3, 1]); ava = st.session_state.db['avatars'].get(lln, "👤")
                col_n.write(f"- {ava} {lln.capitalize()}")
                if col_k.button("Kick", key=f"kick_{lln}"): st.session_state.db['users'][lln]['class'] = ""; sla_db_op(); st.rerun()
        
        # NIEUWE LERAAR GRAFIEKEN!
        with t2:
            st.write("Bekijk de prestaties van je leerlingen in handige grafieken.")
            if in_mijn_klas:
                # Maak data voor grafiek
                data = {"Leerling": [], "Munten (incl Bank)": [], "Taken Af": []}
                for l in in_mijn_klas:
                    data["Leerling"].append(l.capitalize())
                    data["Munten (incl Bank)"].append(st.session_state.db['saldi'][l] + st.session_state.db['bank'][l]['saldo'])
                    data["Taken Af"].append(len(st.session_state.db['completed_tasks'].get(l, [])))
                
                df = pd.DataFrame(data).set_index("Leerling")
                st.subheader("Rijkdom overzicht")
                st.bar_chart(df["Munten (incl Bank)"])
                st.subheader("Gemaakte Taken")
                st.bar_chart(df["Taken Af"])
            else:
                st.info("Voeg eerst leerlingen toe.")

        with t3:
            tt = st.text_input("Titel van de Taak"); tw = st.text_area("Woorden (nl=fr)")
            if st.button("Post Taak", type="primary"):
                d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in tw.split("\n") if "=" in l}
                st.session_state.db['tasks'].append({"id": str(random.randint(10000, 99999)), "title": tt, "words": d, "class": bestaande_klas})
                sla_db_op(); st.toast("Taak geplaatst!", icon="🚀"); st.rerun()
        with t4:
            lt = st.text_input("Lijst Naam"); lw = st.text_area("Woordenlijst (nl=fr)")
            if st.button("Deel Lijst"):
                d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in lw.split("\n") if "=" in l}
                st.session_state.db['vocab_lists'].append({"title": lt, "words": d, "class": bestaande_klas}); sla_db_op(); st.toast("Gedeeld!"); st.rerun()

elif nav == "👑 Admin Room" and is_admin:
    st.title("👑 Admin Control Room")
    t1, t2, t3, t4, t5 = st.tabs(["🌟 PRO Status", "🏷️ Designer", "👩‍🏫 Promoties", "💰 Economie", "💾 RAW"])
    
    with t1:
        pro_doel = st.selectbox("Kies Speler voor PRO Status", list(st.session_state.db['users'].keys()))
        is_nu_pro = st.session_state.db['is_pro'].get(pro_doel, False)
        st.write(f"Status: **{'🌟 PRO LID' if is_nu_pro else 'Standaard Speler'}**")
        if st.button("Geef / Verwijder PRO", type="primary"):
            st.session_state.db['is_pro'][pro_doel] = not is_nu_pro; sla_db_op(); st.rerun()
            
        st.divider()
        st.session_state.db['lockdown'] = st.toggle("🔒 Global Lockdown", value=st.session_state.db.get('lockdown', False))
        if st.button("Opslaan Systeem Status"): sla_db_op(); st.toast("Opgeslagen!")
        
    with t2:
        col_a, col_b = st.columns(2)
        with col_a:
            new_tag_name = st.text_input("Naam van de Tag")
            new_tag_color = st.color_picker("Kies Kleur", "#FFD700")
            if st.button("Maak Badge"):
                st.session_state.db['custom_tags_v2'][new_tag_name] = new_tag_color; sla_db_op(); st.success("Gemaakt!")
        with col_b:
            target_user = st.selectbox("Kies Speler", list(st.session_state.db['users'].keys()))
            target_tag = st.selectbox("Kies Badge om uit te delen", list(st.session_state.db['custom_tags_v2'].keys()))
            c_tag_list = st.session_state.db['player_tags'].setdefault(target_user, [])
            if st.button("Badge Toevoegen"):
                if target_tag not in c_tag_list: c_tag_list.append(target_tag); sla_db_op(); st.rerun()
            if st.button("Badge Verwijderen"):
                if target_tag in c_tag_list: c_tag_list.remove(target_tag); sla_db_op(); st.rerun()
    
    with t3:
        studenten = [u for u, data in st.session_state.db['users'].items() if data.get('role') != 'admin']
        if studenten:
            dl = st.selectbox("Selecteer Student", studenten)
            if st.button("Maak Leraar", type="primary"): st.session_state.db['users'][dl]['role'] = "teacher"; sla_db_op(); st.success("Gepromoveerd!")

    with t4:
        doel = st.selectbox("Speler", list(st.session_state.db['users'].keys()), key="muntdoel")
        bedrag = st.number_input("Bedrag", value=100)
        if st.button("Geef Munten"): st.session_state.db['saldi'][doel] += bedrag; sla_db_op(); st.rerun()

    with t5:
        if st.button("Wis Alle Taken & Lijsten"):
            st.session_state.db['tasks'] = []; st.session_state.db['vocab_lists'] = []; st.session_state.db['completed_tasks'] = {u: [] for u in st.session_state.db['users'].keys()}; sla_db_op(); st.rerun()
        raw = st.text_area("JSON Editor", value=json.dumps(st.session_state.db, indent=2), height=300)
        if st.button("Force Save", type="primary"):
            try: st.session_state.db = json.loads(raw); sla_db_op(); st.rerun()
            except: st.error("JSON Fout!")
