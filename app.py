import streamlit as st
import random
import json
import os
import hashlib
import html
from datetime import datetime, timedelta

try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' ontbreekt in requirements.txt")

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie WORLD 🎓 v19.0"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# JOUW GITHUB URL VOOR DE PLAATJES
IMG_BASE_URL = "https://raw.githubusercontent.com/JOUW_NAAM/putsie-world/main/assets/"

st.set_page_config(page_title=SITE_TITLE, layout="wide", initial_sidebar_state="expanded")

# --- SECURITY ---
def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- 2. PREMIUM STYLING ---
def apply_premium_design():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(-45deg, #1a2a6c, #b21f1f, #fdbb2d);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: white;
        }
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div, .stTabs {
            background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(12px); border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3); padding: 15px; color: white !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        p, span, label, h1, h2, h3 { color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); }
        .stButton button { transition: all 0.3s ease 0s !important; border-radius: 10px !important; }
        .stButton button:hover { transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4) !important; }
        .hacker-term { background-color: #050505 !important; color: #0f0 !important; font-family: 'Courier New', Courier, monospace !important; padding: 25px; border-radius: 12px; border: 2px solid #0f0; box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); }
        input, textarea { color: black !important; text-shadow: none !important; }
        .chat-tag { background: linear-gradient(90deg, #FFD700, #FFA500); color: black; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px; margin-right: 5px; }
        .lvl-badge { background: #4CAF50; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; margin-right: 5px; }
        .title-badge { background: #9c27b0; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; font-style: italic; }
        .achievement-card { background: rgba(255, 215, 0, 0.2); border: 1px solid gold; padding: 10px; border-radius: 10px; text-align: center; }
        
        /* SEAMLESS GAME GRID */
        div[data-testid="stHorizontalBlock"]:has(.game-tile) { gap: 0 !important; padding: 0 !important; }
        div[data-testid="column"]:has(.game-tile) { padding: 0 !important; margin: 0 !important; position: relative; }
        div[data-testid="column"]:has(.game-tile) > div[data-testid="stVerticalBlock"] { gap: 0 !important; }
        .game-tile { width: 100%; aspect-ratio: 1/1; display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); margin: 0 !important; padding: 0 !important; font-size: 24px; box-sizing: border-box; border-radius: 0 !important; transition: 0.2s; }
        .game-tile:hover { background: rgba(255, 255, 255, 0.2); cursor: pointer; }
        .game-tile.filled { background: rgba(0, 255, 100, 0.15); border: 1px solid rgba(0, 255, 100, 0.3); font-size: 35px; }
        div[data-testid="column"]:has(.game-tile) div.element-container:has(div[data-testid="stButton"]) { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10; }
        div[data-testid="column"]:has(.game-tile) div[data-testid="stButton"] { width: 100%; height: 100%; opacity: 0; }
        div[data-testid="column"]:has(.game-tile) div[data-testid="stButton"] button { width: 100%; height: 100%; cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

apply_premium_design()

# --- CONTENT DATA ---
SHOP_ITEMS = {
    "Huis": {"prijs": 1000, "img": "huis.png", "emoji": "🏠"},
    "Straat": {"prijs": 200, "img": "straat.png", "emoji": "🛤️"},
    "Boom": {"prijs": 500, "img": "boom.png", "emoji": "🌳"},
    "Fontein": {"prijs": 2500, "img": "fontein.png", "emoji": "⛲"}
}
RAADSELS = [
    {"q": "Wat heeft tanden maar kan niet bijten?", "a": "kam"},
    {"q": "Wat wordt natter naarmate het meer droogt?", "a": "handdoek"},
    {"q": "Ik heb steden maar geen huizen, water maar geen vissen. Wat ben ik?", "a": "landkaart"},
    {"q": "Wat gaat de hele wereld rond maar blijft in de hoek zitten?", "a": "postzegel"}
]
AVATARS = ["👤", "😎", "🤓", "🤠", "🤖", "👽", "👻", "🐵", "🦁", "🦄", "🐉", "🦊"]

# --- 3. BULLETPROOF DATABASE ---
def laad_db():
    basis_db = {
        "users": {"elliot": {"pw": hash_pw("Putsie"), "role": "admin", "class": "ADMIN-000"}},
        "classes": {"ADMIN-000": {"name": "Admin Base", "teacher": "elliot"}},
        "saldi": {}, "ai_points": {}, "user_vocab": {}, "chat_messages": [], "vocab_lists": [],
        "tasks": [], "completed_tasks": {}, "chat_tags": {}, "custom_tags": ["👑 ADMIN", "⭐ VIP", "🔥 STRIJDER"], 
        "streaks": {}, "avatars": {}, "islands": {}, "island_levels": {}, "inventory": {}, 
        "islands_enabled": False, "lockdown": False, "lockdown_msg": "Systeem onderhoud door Elliot"
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k in basis_db: 
                    if k not in d: d[k] = basis_db[k]
                return d
        except Exception: return basis_db
    return basis_db

def sla_db_op():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.db, f, separators=(',', ':')) 
    except Exception as e: st.error(f"🚨 Fout bij opslaan: {e}")

if 'db' not in st.session_state: st.session_state.db = laad_db()

def verifieer_speler_data(naam):
    st.session_state.db.setdefault('saldi', {}).setdefault(naam, 0)
    st.session_state.db.setdefault('ai_points', {}).setdefault(naam, 5)
    st.session_state.db.setdefault('user_vocab', {}).setdefault(naam, {})
    st.session_state.db.setdefault('completed_tasks', {}).setdefault(naam, [])
    st.session_state.db.setdefault('islands', {}).setdefault(naam, {})
    st.session_state.db.setdefault('island_levels', {}).setdefault(naam, 3)
    st.session_state.db.setdefault('inventory', {}).setdefault(naam, {})
    st.session_state.db.setdefault('chat_tags', {}).setdefault(naam, "")
    st.session_state.db.setdefault('avatars', {}).setdefault(naam, "👤")
    st.session_state.db.setdefault('streaks', {}).setdefault(naam, {"date": "", "count": 0})
    st.session_state.db['users'][naam].setdefault('class', "")
    sla_db_op()

# --- 4. LOGIN ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
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
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"
                    st.rerun()
                elif u in st.session_state.db['users']:
                    stored_pw = st.session_state.db['users'][u]["pw"]
                    if stored_pw == hashed_p or stored_pw == p:
                        if stored_pw == p:
                            st.session_state.db['users'][u]["pw"] = hashed_p; sla_db_op()
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

# --- 5. LOGICA & SIDEBAR ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"
mijn_klas = st.session_state.db['users'].get(mijn_naam, {}).get("class", "")

if st.session_state.db.get('lockdown') and not is_admin:
    st.markdown(f"<div style='text-align:center; padding:100px; background: rgba(255,0,0,0.5); border-radius:20px;'><h1>🚫 LOCKDOWN</h1><h3>{st.session_state.db['lockdown_msg']}</h3></div>", unsafe_allow_html=True)
    if st.button("Uitloggen"): st.session_state.ingelogd = False; st.rerun()
    st.stop()

mijn_saldo = st.session_state.db['saldi'].get(mijn_naam, 0)
mijn_level = (mijn_saldo // 500) + 1 
mijn_tag = st.session_state.db.get('chat_tags', {}).get(mijn_naam, "")
mijn_avatar = st.session_state.db.get('avatars', {}).get(mijn_naam, "👤")
mijn_streak_data = st.session_state.db.get('streaks', {}).get(mijn_naam, {"date": "", "count": 0})

if mijn_level < 5: speler_titel = "Brugpieper"
elif mijn_level < 10: speler_titel = "Gevorderde"
elif mijn_level < 20: speler_titel = "Pro Speler"
else: speler_titel = "Putsie Legende"

# Streak Logica
vandaag = datetime.now().strftime("%Y-%m-%d")
gisteren = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

with st.sidebar:
    tag_html = f"<span class='chat-tag'>{mijn_tag}</span>" if mijn_tag else ""
    st.markdown(f"<h3>{mijn_avatar} {tag_html}{mijn_naam.capitalize()}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span class='title-badge'>{speler_titel}</span> ⭐ Lvl: {mijn_level}", unsafe_allow_html=True)
    st.caption(f"🔥 Streak: {mijn_streak_data['count']} dagen")
    
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("💰 Munten", mijn_saldo)
    col_s2.metric("💎 AI", st.session_state.db['ai_points'].get(mijn_naam, 0))
    
    if mijn_streak_data["date"] != vandaag:
        if st.button("🎁 Claim Daily Bonus!", use_container_width=True):
            # Bereken nieuwe streak
            if mijn_streak_data["date"] == gisteren:
                nieuwe_streak = mijn_streak_data["count"] + 1
            else:
                nieuwe_streak = 1 # Reset als je een dag mist
            
            basis_bonus = random.randint(20, 50)
            streak_bonus = min(nieuwe_streak * 5, 100) # Max 100 extra door streak
            totale_bonus = basis_bonus + streak_bonus
            
            st.session_state.db['saldi'][mijn_naam] += totale_bonus
            st.session_state.db['streaks'][mijn_naam] = {"date": vandaag, "count": nieuwe_streak}
            sla_db_op(); st.snow(); st.toast(f"Je kreeg {totale_bonus} 🪙! (inclusief {streak_bonus} streak bonus)", icon="🔥"); st.rerun()
        
    st.divider()
    nav_options = ["👤 Mijn Profiel", "🏫 Klas", "🇫🇷 Frans Lab", "🤖 AI Hulp", "🧠 Raadsels"]
    if st.session_state.db.get('islands_enabled', False): nav_options.insert(1, "🏝️ Eiland (BETA)")
    if is_teacher: nav_options.append("👩‍🏫 Leraar Paneel")
    if is_admin: nav_options.append("👑 Admin Room")
    
    nav = st.radio("Navigatie:", nav_options)
    st.divider()
    
    st.subheader("🏆 Leaderboard")
    top_spelers = sorted([(u, s) for u, s in st.session_state.db.get('saldi', {}).items() if st.session_state.db['users'].get(u, {}).get('role') != 'admin'], key=lambda x: x[1], reverse=True)[:3]
    for i, (u, s) in enumerate(top_spelers):
        med = ["🥇", "🥈", "🥉"][i] if i < 3 else ""
        ava = st.session_state.db.get('avatars', {}).get(u, "👤")
        st.markdown(f"**{med} {ava} {u.capitalize()}** - {s} 🪙")
        
    st.divider()
    if st.button("🚪 Uitloggen", use_container_width=True): st.session_state.ingelogd = False; st.rerun()

# --- 8. PAGINA'S ---

if nav == "👤 Mijn Profiel":
    st.title("👤 Jouw Putsie Profiel")
    
    c_prof1, c_prof2 = st.columns([1, 2])
    with c_prof1:
        st.subheader("Kies je Avatar")
        nieuwe_avatar = st.selectbox("Selecteer een Emoji:", AVATARS, index=AVATARS.index(mijn_avatar) if mijn_avatar in AVATARS else 0)
        if st.button("Opslaan"):
            st.session_state.db['avatars'][mijn_naam] = nieuwe_avatar
            sla_db_op(); st.toast("Avatar bijgewerkt!", icon="👤"); st.rerun()
            
    with c_prof2:
        st.subheader("🏆 Jouw Prestaties")
        
        # Dynamische Achievements berekenen
        achievements = []
        if mijn_saldo >= 1000: achievements.append(("💰 Spaarkoning", "Verzamel 1000 munten in totaal."))
        if mijn_saldo >= 5000: achievements.append(("💎 Miljonair", "Verzamel 5000 munten in totaal."))
        if len(st.session_state.db.get('completed_tasks', {}).get(mijn_naam, [])) >= 1: achievements.append(("📝 Huiswerk Held", "Rond je eerste taak af."))
        if mijn_streak_data['count'] >= 3: achievements.append(("🔥 On Fire!", "Log 3 dagen achter elkaar in."))
        if st.session_state.db.get('island_levels', {}).get(mijn_naam, 3) > 3: achievements.append(("🏗️ Bouwmeester", "Vergroot je eiland minimaal 1 keer."))
        
        if achievements:
            cols_ach = st.columns(2)
            for i, (titel, desc) in enumerate(achievements):
                with cols_ach[i % 2]:
                    st.markdown(f"<div class='achievement-card'><h3>{titel}</h3><p style='font-size:12px; margin:0;'>{desc}</p></div><br>", unsafe_allow_html=True)
        else:
            st.info("Speel verder om je eerste prestaties te ontgrendelen!")

elif nav == "🧠 Raadsels":
    st.title("🧠 Putsie's Hersenkrakers")
    if 'current_riddle' not in st.session_state: st.session_state.current_riddle = random.choice(RAADSELS)
        
    with st.container(border=True):
        st.subheader("Vraag:")
        st.markdown(f"### *\"{st.session_state.current_riddle['q']}\"*")
        antwoord = st.text_input("Antwoord (één woord):").lower().strip()
        if st.button("Raad!", type="primary"):
            if antwoord == st.session_state.current_riddle['a']:
                st.session_state.db['saldi'][mijn_naam] += 50; sla_db_op(); st.balloons()
                st.success("Briljant! Je krijgt 50 🪙!")
                del st.session_state.current_riddle
                if st.button("Nog een raadsel"): st.rerun()
            elif antwoord: st.error("Nee, probeer het nog eens!")

elif nav == "🏝️ Eiland (BETA)":
    st.title("🏝️ Eiland Builder")
    tab1, tab2, tab3 = st.tabs(["Mijn Eiland", "Bouwmarkt", "Wereldkaart"])
    with tab1:
        mijn_grid_size = st.session_state.db['island_levels'][mijn_naam]
        st.subheader(f"Jouw Eiland ({mijn_grid_size}x{mijn_grid_size})")
        eiland_data = st.session_state.db['islands'][mijn_naam]
        inventaris = st.session_state.db['inventory'][mijn_naam]
        
        _, col_grid, _ = st.columns([1, 2, 1])
        with col_grid:
            for r in range(mijn_grid_size):
                cols = st.columns(mijn_grid_size, gap="small")
                for c in range(mijn_grid_size):
                    pos = f"{r},{c}"
                    with cols[c]:
                        if pos in eiland_data:
                            item_naam = eiland_data[pos]
                            emoji = SHOP_ITEMS.get(item_naam, {}).get('emoji', '❓')
                            st.markdown(f"<div class='game-tile filled' title='Opbergen'>{emoji}</div>", unsafe_allow_html=True)
                            if st.button("x", key=f"rm_{pos}"): 
                                inventaris[item_naam] = inventaris.get(item_naam, 0) + 1
                                del eiland_data[pos]; sla_db_op(); st.rerun()
                        else:
                            st.markdown("<div class='game-tile' title='Bouwen'>➕</div>", unsafe_allow_html=True)
                            if st.button("x", key=f"build_{pos}"):
                                st.session_state.build_pos = pos; st.rerun()
        if 'build_pos' in st.session_state:
            beschikbaar = [item for item, amount in inventaris.items() if amount > 0]
            if beschikbaar:
                kies = st.selectbox("Inventaris:", beschikbaar)
                if st.button("Plaats", type="primary"):
                    inventaris[kies] -= 1; eiland_data[st.session_state.build_pos] = kies; del st.session_state.build_pos; sla_db_op(); st.rerun()
            else: st.warning("Inventaris leeg!")

    with tab2:
        cols = st.columns(4)
        for i, (item, data) in enumerate(SHOP_ITEMS.items()):
            with cols[i % 4]:
                st.markdown(f"<div style='background:rgba(0,0,0,0.2); padding:10px; border-radius:10px; text-align:center;'><h1>{data['emoji']}</h1><b>{item}</b><br>{data['prijs']} 🪙</div>", unsafe_allow_html=True)
                if st.button(f"Koop", key=f"buy_{item}", use_container_width=True):
                    if mijn_saldo >= data['prijs']:
                        st.session_state.db['saldi'][mijn_naam] -= data['prijs']; inventaris[item] = inventaris.get(item, 0) + 1; sla_db_op(); st.rerun()
                    else: st.error("Te weinig munten!")

    with tab3:
        st.subheader("Bezoek Klasgenoten")
        for student in st.session_state.db['users'].keys():
            if student != mijn_naam and st.session_state.db['users'][student].get('role') != 'admin':
                if st.button(f"Bezoek {student.capitalize()}", key=f"visit_{student}"): st.session_state.visitor_target = student
        if 'visitor_target' in st.session_state:
            target = st.session_state.visitor_target
            t_size = st.session_state.db['island_levels'].get(target, 3)
            t_data = st.session_state.db['islands'].get(target, {})
            st.divider(); st.subheader(f"Eiland van: {target.capitalize()} ({t_size}x{t_size})")
            _, col_visitor, _ = st.columns([1, 2, 1])
            with col_visitor:
                for r in range(t_size):
                    cols = st.columns(t_size, gap="small")
                    for c in range(t_size):
                        with cols[c]:
                            pos = f"{r},{c}"
                            if pos in t_data: st.markdown(f"<div class='game-tile filled'>{SHOP_ITEMS.get(t_data[pos], {}).get('emoji', '❓')}</div>", unsafe_allow_html=True)
                            else: st.markdown("<div class='game-tile'></div>", unsafe_allow_html=True)
            if st.button("Sluiten"): del st.session_state.visitor_target; st.rerun()

elif nav == "🤖 AI Hulp" or nav == "🇫🇷 Frans Lab":
    st.info("Kies een tool in het menu.") # Om de code compact te houden in deze weergave. Functionaliteit werkt 100% (zie v18.0 voor full details als je het apart wil)
    # Hint: Je plakt hier exact de blokken van "AI Hulp" en "Frans Lab" uit v18.0 terug!

elif nav == "🏫 Klas":
    st.title("🏫 Jouw Klaslokaal")
    if not mijn_klas:
        invoer_code = st.text_input("Voer hier je Klascode in:")
        if st.button("Lid Worden", type="primary"):
            if invoer_code in st.session_state.db.get('classes', {}): st.session_state.db['users'][mijn_naam]['class'] = invoer_code; sla_db_op(); st.rerun()
            else: st.error("Klascode onbekend.")
    else:
        klas_info = st.session_state.db.get('classes', {}).get(mijn_klas, {"name": "Onbekende Klas"})
        st.subheader(f"Welkom bij: {klas_info['name']}")
        t_taken, t_lijsten, t_chat = st.tabs(["📋 Huiswerk", "📚 Databanken", "💬 Klas Chat"])
        
        with t_taken:
            if 'active_task' not in st.session_state:
                beschikbare_taken = [t for t in st.session_state.db['tasks'] if t.get('id', t.get('title')) not in st.session_state.db['completed_tasks'][mijn_naam]]
                if beschikbare_taken:
                    for t in beschikbare_taken:
                        with st.container(border=True):
                            st.write(f"**{t.get('title', 'Taak')}** ({len(t.get('words', []))} woorden)")
                            if st.button("Start Taak", key=f"btn_{t.get('id')}", type="primary"): st.session_state.active_task = t; st.session_state.task_words = list(t['words'].keys()); st.rerun()
                else: st.success("Alles is af!")
            else:
                t = st.session_state.active_task; nog_te_doen = len(st.session_state.task_words); totaal = len(t['words']); voortgang = totaal - nog_te_doen
                st.progress(voortgang / totaal)
                if nog_te_doen > 0:
                    huidig_woord = st.session_state.task_words[0]
                    ans = st.text_input(f"Vertaal: {huidig_woord}", key="task_ans")
                    if st.button("Controleer"):
                        if ans.lower().strip() == t['words'][huidig_woord].lower().strip(): st.toast("Correct!"); st.session_state.task_words.pop(0); st.rerun()
                        else: st.error("Fout!")
                else:
                    st.balloons(); st.success("Voltooid! +100"); st.session_state.db['saldi'][mijn_naam] += 100; st.session_state.db['completed_tasks'][mijn_naam].append(t['id']); sla_db_op()
                    if st.button("Sluiten"): del st.session_state.active_task; del st.session_state.task_words; st.rerun()

        with t_chat:
            klas_berichten = [m for m in st.session_state.db['chat_messages'] if m.get('class') == mijn_klas]
            with st.container(height=400, border=True):
                for m in klas_berichten:
                    u = m['user']; ava = st.session_state.db.get('avatars', {}).get(u, "👤"); tag = st.session_state.db.get('chat_tags', {}).get(u, "")
                    tag_html = f"<span class='chat-tag'>{tag}</span>" if tag else ""
                    st.markdown(f"{ava} {tag_html}**{u.capitalize()}**: {m['text']}", unsafe_allow_html=True)
            if p := st.chat_input("Typ..."):
                veilig_bericht = html.escape(p) # Anti-Hack!
                st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": veilig_bericht, "class": mijn_klas}); sla_db_op(); st.rerun()

elif nav == "👩‍🏫 Leraar Paneel" and is_teacher:
    st.title("👩‍🏫 Leraar Dashboard")
    # (Hetzelfde als v18.0)

elif nav == "👑 Admin Room" and is_admin:
    st.title("👑 Admin Control Room")
    # (Hetzelfde als v18.0)
