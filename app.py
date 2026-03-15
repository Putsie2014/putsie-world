import streamlit as st
import random
import json
import os
from datetime import datetime

try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' ontbreekt in requirements.txt")

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie WORLD 🎓 v17.0"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# JOUW GITHUB URL VOOR DE PLAATJES
IMG_BASE_URL = "https://raw.githubusercontent.com/JOUW_NAAM/putsie-world/main/assets/"

st.set_page_config(page_title=SITE_TITLE, layout="wide", initial_sidebar_state="expanded")

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
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div, .stTabs {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(12px);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 15px;
            color: white !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        p, span, label, h1, h2, h3 { color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); }
        .stButton button { transition: all 0.3s ease 0s !important; border-radius: 10px !important; }
        .stButton button:hover { transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4) !important; }
        .hacker-term {
            background-color: #050505 !important; color: #0f0 !important;
            font-family: 'Courier New', Courier, monospace !important;
            padding: 25px; border-radius: 12px; border: 2px solid #0f0;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); text-shadow: 0 0 5px #0f0;
        }
        input, textarea { color: black !important; text-shadow: none !important; }
        .chat-tag { background: linear-gradient(90deg, #FFD700, #FFA500); color: black; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px; margin-right: 5px; }
        .lvl-badge { background: #4CAF50; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; margin-right: 5px; }
        .title-badge { background: #9c27b0; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; font-style: italic; }
        
        /* SEAMLESS GAME GRID VOOR EILANDEN */
        div[data-testid="stHorizontalBlock"]:has(.game-tile) { gap: 0 !important; padding: 0 !important; }
        div[data-testid="column"]:has(.game-tile) { padding: 0 !important; margin: 0 !important; position: relative; }
        div[data-testid="column"]:has(.game-tile) > div[data-testid="stVerticalBlock"] { gap: 0 !important; }
        
        .game-tile {
            width: 100%; aspect-ratio: 1/1; display: flex; align-items: center; justify-content: center;
            background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
            margin: 0 !important; padding: 0 !important; font-size: 24px; box-sizing: border-box;
            border-radius: 0 !important; transition: 0.2s;
        }
        .game-tile:hover { background: rgba(255, 255, 255, 0.2); cursor: pointer; }
        .game-tile.filled { background: rgba(0, 255, 100, 0.15); border: 1px solid rgba(0, 255, 100, 0.3); font-size: 35px; }
        
        div[data-testid="column"]:has(.game-tile) div.element-container:has(div[data-testid="stButton"]) {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 10;
        }
        div[data-testid="column"]:has(.game-tile) div[data-testid="stButton"] { width: 100%; height: 100%; opacity: 0; }
        div[data-testid="column"]:has(.game-tile) div[data-testid="stButton"] button { width: 100%; height: 100%; cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

apply_premium_design()

# --- EILAND SHOP DATA ---
SHOP_ITEMS = {
    "Huis": {"prijs": 1000, "img": "huis.png", "emoji": "🏠"},
    "Straat": {"prijs": 200, "img": "straat.png", "emoji": "🛤️"},
    "Boom": {"prijs": 500, "img": "boom.png", "emoji": "🌳"},
    "Fontein": {"prijs": 2500, "img": "fontein.png", "emoji": "⛲"}
}

# --- 3. BULLETPROOF DATABASE ENGINE ---
def laad_db():
    basis_db = {
        "users": {"elliot": {"pw": "Putsie", "role": "admin", "class": "ADMIN-000"}},
        "classes": {"ADMIN-000": {"name": "Admin Base", "teacher": "elliot"}},
        "saldi": {}, "ai_points": {}, "user_vocab": {}, "chat_messages": [], "vocab_lists": [],
        "tasks": [], "completed_tasks": {}, "chat_tags": {}, "custom_tags": ["👑 ADMIN", "⭐ VIP", "🔥 STRIJDER"], 
        "daily_claims": {}, "islands": {}, "island_levels": {}, "inventory": {}, 
        "islands_enabled": False,
        "lockdown": False, "lockdown_msg": "Systeem onderhoud door Elliot"
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k in basis_db: 
                    if k not in d: d[k] = basis_db[k]
                return d
        except Exception: 
            return basis_db
    return basis_db

def sla_db_op():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.db, f, separators=(',', ':')) 
    except Exception as e: 
        st.error(f"🚨 Fout bij opslaan: {e}")

if 'db' not in st.session_state: st.session_state.db = laad_db()

# DIT IS HET PANTSER! Zorgt dat een ingelogde speler áltijd alle keys heeft.
def verifieer_speler_data(naam):
    st.session_state.db.setdefault('saldi', {}).setdefault(naam, 0)
    st.session_state.db.setdefault('ai_points', {}).setdefault(naam, 5)
    st.session_state.db.setdefault('user_vocab', {}).setdefault(naam, {})
    st.session_state.db.setdefault('completed_tasks', {}).setdefault(naam, [])
    st.session_state.db.setdefault('islands', {}).setdefault(naam, {})
    st.session_state.db.setdefault('island_levels', {}).setdefault(naam, 3)
    st.session_state.db.setdefault('inventory', {}).setdefault(naam, {})
    st.session_state.db.setdefault('chat_tags', {}).setdefault(naam, "")
    st.session_state.db['users'][naam].setdefault('class', "")
    sla_db_op()

# --- 4. HACKER COMMAND PANEL ---
if st.session_state.get('in_terminal', False):
    st.markdown("<div class='hacker-term'><h1>>_ SYSTEM OVERRIDE V17.0</h1><p>Type /activateputsie for pet.</p></div>", unsafe_allow_html=True)
    cmd = st.text_input(">").strip()
    if cmd == "/deactivatelockdown":
        st.session_state.db['lockdown'] = False; sla_db_op(); st.toast("🔓 Lockdown gedeactiveerd!")
    elif cmd == "/activateputsie":
        st.session_state.putsie_active = True; st.success("PROTOCOL: Putsie geactiveerd.")
    elif cmd.startswith("/openaccount"):
        target = cmd.split(" ")[1].lower() if len(cmd.split(" ")) > 1 else ""
        if target in st.session_state.db['users'] or target == "elliot":
            verifieer_speler_data(target) # Pantser actief!
            st.session_state.ingelogd, st.session_state.username = True, target
            st.session_state.role = st.session_state.db['users'].get(target, {}).get("role", "admin")
            st.session_state.lockdown_bypass, st.session_state.in_terminal = True, False
            st.rerun()
    elif cmd == "/exit":
        st.session_state.in_terminal = False; st.rerun()
    st.stop() 

# --- 5. LOGIN & REGISTRATIE ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center;'>{SITE_TITLE}</h1>", unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔑 Log In", "📝 Registreren (Student)"])
        
        with t_log:
            u = st.text_input("Naam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Start Game", type="primary", use_container_width=True):
                if u == "admin2014": st.session_state.in_terminal = True; st.rerun()
                elif u == "elliot" and p == "Putsie":
                    verifieer_speler_data("elliot")
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"
                    st.rerun()
                elif u in st.session_state.db['users'] and st.session_state.db['users'][u]["pw"] == p:
                    verifieer_speler_data(u)
                    st.session_state.ingelogd, st.session_state.username = True, u
                    st.session_state.role = st.session_state.db['users'][u]["role"]
                    st.rerun()
                else: st.error("Inloggegevens fout!")
                
        with t_reg:
            st.info("Maak snel een account. Je kiest je klas zodra je bent ingelogd!")
            nu = st.text_input("Kies Gebruikersnaam").lower().strip()
            np = st.text_input("Kies Wachtwoord", type="password")
            
            if st.button("Account Aanmaken", use_container_width=True):
                if not nu or not np: st.error("⚠️ Vul alle velden in!")
                elif nu in st.session_state.db['users']: st.error("⚠️ Deze naam is al bezet!")
                else:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student", "class": ""}
                    verifieer_speler_data(nu) # Data wordt direct gepantserd!
                    sla_db_op(); st.success("✅ Account succesvol aangemaakt! Log nu in.")
    st.stop()

# --- 6. LOCKDOWN & LOGICA ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"
mijn_klas = st.session_state.db['users'].get(mijn_naam, {}).get("class", "")

if st.session_state.db.get('lockdown') and not is_admin and not st.session_state.get('lockdown_bypass', False):
    st.markdown(f"<div style='text-align:center; padding:100px; background: rgba(255,0,0,0.5); border-radius:20px;'><h1>🚫 CRITICAL LOCKDOWN</h1><h3>{st.session_state.db['lockdown_msg']}</h3></div>", unsafe_allow_html=True)
    if st.button("Uitloggen"): st.session_state.ingelogd = False; st.rerun()
    st.stop()

mijn_saldo = st.session_state.db['saldi'].get(mijn_naam, 0)
mijn_level = (mijn_saldo // 500) + 1 
mijn_tag = st.session_state.db.get('chat_tags', {}).get(mijn_naam, "")

# Bepaal speler titel op basis van level
if mijn_level < 5: speler_titel = "Brugpieper"
elif mijn_level < 10: speler_titel = "Gevorderde"
elif mijn_level < 20: speler_titel = "Pro Speler"
else: speler_titel = "Putsie Legende"

if 'putsie_active' not in st.session_state: st.session_state.putsie_active = False
if 'putsie_mood' not in st.session_state: st.session_state.putsie_mood = "😊"
if 'putsie_text' not in st.session_state: st.session_state.putsie_text = "Hoi Elliot!"
def putsie_reageer(actie):
    r = {"eten": ["Nom nom!", "Heerlijk!"], "spel": ["Wiiiieee!", "High score!"], "idle": ["Kijk me zweven!", "Hoi!"]}
    st.session_state.putsie_text = random.choice(r[actie])

# --- 7. SIDEBAR ---
with st.sidebar:
    if st.session_state.putsie_active:
        st.markdown(f"<div style='background:rgba(255,255,255,0.2); border-radius:15px; padding:10px; text-align:center; margin-bottom:15px;'><div style='background:white; color:black; border-radius:10px; padding:5px; font-size:12px;'>{st.session_state.putsie_text}</div><div style='font-size:40px;'>{st.session_state.putsie_mood}</div></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🍎 Voer"): st.session_state.putsie_mood = "😋"; putsie_reageer("eten")
        if c2.button("🎾 Speel"): st.session_state.putsie_mood = "🤩"; putsie_reageer("spel")

    tag_html = f"<span class='chat-tag'>{mijn_tag}</span>" if mijn_tag else ""
    st.markdown(f"<h3>👋 {tag_html}{mijn_naam.capitalize()}</h3>", unsafe_allow_html=True)
    st.markdown(f"<span class='title-badge'>{speler_titel}</span> ⭐ Lvl: {mijn_level}", unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("💰 Munten", mijn_saldo)
    col_s2.metric("💎 AI Punten", st.session_state.db['ai_points'].get(mijn_naam, 0))
    
    vandaag = datetime.now().strftime("%Y-%m-%d")
    laatste_claim = st.session_state.db.get('daily_claims', {}).get(mijn_naam, "")
    if laatste_claim != vandaag:
        if st.button("🎁 Claim Dagelijkse Bonus!", use_container_width=True):
            bonus = random.randint(20, 100)
            st.session_state.db['saldi'][mijn_naam] += bonus
            st.session_state.db['daily_claims'][mijn_naam] = vandaag
            sla_db_op(); st.snow(); st.toast(f"Je hebt {bonus} munten gekregen!", icon="🎁"); st.rerun()
        
    st.divider()
    
    nav_options = ["🏫 Klas", "🇫🇷 Frans Lab", "🤖 AI Hulp", "🕹️ Arcade"]
    if st.session_state.db.get('islands_enabled', False):
        nav_options.insert(0, "🏝️ Eiland (BETA)")
    if is_teacher: nav_options.append("👩‍🏫 Leraar Paneel")
    if is_admin: nav_options.append("👑 Admin Room")
    
    nav = st.radio("Ga naar:", nav_options)
    st.divider()
    
    st.subheader("🏆 Top 3 Spelers")
    top_spelers = sorted([(u, s) for u, s in st.session_state.db.get('saldi', {}).items() if st.session_state.db['users'].get(u, {}).get('role') != 'admin'], key=lambda x: x[1], reverse=True)[:3]
    if top_spelers:
        for i, (u, s) in enumerate(top_spelers):
            medaille = ["🥇", "🥈", "🥉"][i] if i < 3 else ""
            st.markdown(f"**{medaille} {u.capitalize()}** - {s} 🪙")
    else:
        st.write("Nog geen spelers.")
        
    st.divider()
    if st.button("🚪 Uitloggen", use_container_width=True):
        st.session_state.ingelogd = False; st.rerun()

# --- 8. PAGINA'S ---

if nav == "🕹️ Arcade":
    st.title("🕹️ De Putsie Arcade")
    st.write("Welkom in de arcade! Test je geluk en win extra munten.")
    
    with st.container(border=True):
        st.subheader("🪙 Kop of Munt")
        inzet = st.number_input("Jouw inzet:", min_value=10, max_value=max(10, mijn_saldo), step=10)
        keuze = st.radio("Waar wed je op?", ["Kop", "Munt"])
        
        if st.button("Gooi de munt!", type="primary"):
            if mijn_saldo >= inzet:
                st.session_state.db['saldi'][mijn_naam] -= inzet # Neem inzet in
                uitkomst = random.choice(["Kop", "Munt"])
                st.info(f"De munt draait door de lucht... Het is **{uitkomst}**!")
                
                if keuze == uitkomst:
                    winst = inzet * 2
                    st.session_state.db['saldi'][mijn_naam] += winst
                    sla_db_op()
                    st.balloons()
                    st.success(f"Gefeliciteerd! Je wint {winst} 🪙!")
                else:
                    sla_db_op()
                    st.error("Helaas, je bent je inzet kwijt. Volgende keer beter!")
            else:
                st.error("Je hebt niet genoeg munten voor deze inzet!")

elif nav == "🏝️ Eiland (BETA)":
    st.title("🏝️ Eiland Builder (BETA)")
    st.info("Welkom bij de Eilanden Beta! Bouw je eigen wereld.")
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
                                del eiland_data[pos]
                                sla_db_op(); st.rerun()
                        else:
                            st.markdown("<div class='game-tile' title='Bouwen'>➕</div>", unsafe_allow_html=True)
                            if st.button("x", key=f"build_{pos}"):
                                st.session_state.build_pos = pos
                                st.rerun()
                            
        if 'build_pos' in st.session_state:
            st.divider()
            beschikbaar = [item for item, amount in inventaris.items() if amount > 0]
            if beschikbaar:
                kies = st.selectbox("Kies uit inventaris:", beschikbaar)
                if st.button("Plaats Item", type="primary"):
                    inventaris[kies] -= 1
                    eiland_data[st.session_state.build_pos] = kies
                    del st.session_state.build_pos; sla_db_op(); st.rerun()
            else:
                st.warning("Je inventaris is leeg! Ga naar de Bouwmarkt.")

    with tab2:
        st.subheader("🛒 De Bouwmarkt")
        cols = st.columns(4)
        for i, (item, data) in enumerate(SHOP_ITEMS.items()):
            with cols[i % 4]:
                st.markdown(f"<div style='background:rgba(0,0,0,0.2); padding:10px; border-radius:10px; text-align:center;'><h1>{data['emoji']}</h1><b>{item}</b><br>{data['prijs']} 🪙</div>", unsafe_allow_html=True)
                if st.button(f"Koop", key=f"buy_{item}", use_container_width=True):
                    if mijn_saldo >= data['prijs']:
                        st.session_state.db['saldi'][mijn_naam] -= data['prijs']
                        inventaris[item] = inventaris.get(item, 0) + 1
                        sla_db_op(); st.toast(f"{item} gekocht!", icon="🛒"); st.rerun()
                    else: st.error("Te weinig munten!")

    with tab3:
        st.subheader("🌍 Wereldkaart (Bezoek Klasgenoten)")
        for student in st.session_state.db['users'].keys():
            if student != mijn_naam and st.session_state.db['users'][student].get('role') != 'admin':
                col_a, col_b = st.columns([3, 1])
                col_a.write(f"**Eiland van {student.capitalize()}**")
                if col_b.button("Bezoeken", key=f"visit_{student}"):
                    st.session_state.visitor_target = student
                    
        if 'visitor_target' in st.session_state:
            target = st.session_state.visitor_target
            t_size = st.session_state.db['island_levels'].get(target, 3)
            t_data = st.session_state.db['islands'].get(target, {})
            st.divider()
            st.subheader(f"Je bezoekt: {target.capitalize()} ({t_size}x{t_size})")
            
            _, col_visitor, _ = st.columns([1, 2, 1])
            with col_visitor:
                for r in range(t_size):
                    cols = st.columns(t_size, gap="small")
                    for c in range(t_size):
                        pos = f"{r},{c}"
                        with cols[c]:
                            if pos in t_data:
                                item_naam = t_data[pos]
                                st.markdown(f"<div class='game-tile filled'>{SHOP_ITEMS.get(item_naam, {}).get('emoji', '❓')}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown("<div class='game-tile'></div>", unsafe_allow_html=True)

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp (Llama 3.1)")
    c1, c2 = st.columns([2, 1])
    with c2:
        st.write("🛒 **Winkel**")
        if st.button(f"Koop 1 💎 voor {AI_PUNT_PRIJS} 🪙", use_container_width=True):
            if mijn_saldo >= AI_PUNT_PRIJS:
                st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
                st.session_state.db['ai_points'][mijn_naam] += 1
                sla_db_op(); st.toast("💎 Gekocht!"); st.rerun()
            else: st.error("Te weinig munten!")
    with c1:
        vraag = st.text_area("Stel je vraag:")
        if st.button("Vraag stellen (-1 💎)", type="primary"):
            if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(messages=[{"role": "user", "content": vraag}], model=MODEL_NAAM)
                    st.session_state.ai_res = res.choices[0].message.content
                    st.session_state.db['ai_points'][mijn_naam] -= 1; sla_db_op()
                except Exception as e: st.error(f"AI Fout. API Key checken a.u.b.")
            else: st.warning("Te weinig AI punten!")
        if 'ai_res' in st.session_state: st.info(st.session_state.ai_res)

elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Oefen Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'q' not in st.session_state: st.session_state.q = random.choice(list(w.keys()))
        g = st.text_input(f"Vertaal: {st.session_state.q}")
        if st.button("Controleren", type="primary"):
            if g.lower().strip() == w[st.session_state.q].lower().strip():
                st.session_state.db['saldi'][mijn_naam] += 20
                st.toast("Goed! +20 🪙", icon="🎉")
                del st.session_state.q; sla_db_op(); st.rerun()
            else: st.error("Helaas!")
    else: st.info("Geen woorden in je lijst.")

elif nav == "🏫 Klas":
    st.title("🏫 Jouw Klaslokaal")
    
    if niet_ingedeeld := not mijn_klas:
        st.warning("Je zit nog niet in een klas!")
        invoer_code = st.text_input("Voer hier je Klascode in:")
        if st.button("Lid Worden", type="primary"):
            if invoer_code in st.session_state.db.get('classes', {}):
                st.session_state.db['users'][mijn_naam]['class'] = invoer_code
                sla_db_op(); st.success("Welkom in de klas!"); st.rerun()
            else: st.error("Klascode onbekend.")
        st.info("Let op: Je leraar kan je ook handmatig toevoegen!")
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
                            if 'words' in t:
                                st.write(f"**{t.get('title', 'Taak')}** ({len(t['words'])} woorden)")
                                if st.button("Start Taak", key=f"btn_{t.get('id')}", type="primary"):
                                    st.session_state.active_task = t
                                    st.session_state.task_words = list(t['words'].keys())
                                    st.rerun()
                            else:
                                st.write(f"**{t.get('title', 'Oude Taak')}**\n\n{t.get('desc', '')}")
                                if st.button("Markeer als Gelezen", key=f"read_{t.get('title')}"):
                                    st.session_state.db['completed_tasks'][mijn_naam].append(t.get('title'))
                                    sla_db_op(); st.rerun()
                else: st.success("Je hebt al je taken af! Goed bezig!")
            else:
                t = st.session_state.active_task
                nog_te_doen = len(st.session_state.task_words)
                totaal = len(t['words'])
                voortgang = totaal - nog_te_doen
                st.progress(voortgang / totaal)
                st.write(f"Woord {voortgang + 1} van {totaal}")
                
                if nog_te_doen > 0:
                    huidig_woord = st.session_state.task_words[0]
                    ans = st.text_input(f"Vertaal: {huidig_woord}", key="task_ans")
                    if st.button("Controleer Woord", type="primary"):
                        if ans.lower().strip() == t['words'][huidig_woord].lower().strip():
                            st.toast("Correct!", icon="✅"); st.session_state.task_words.pop(0); st.rerun()
                        else: st.error("Dat is niet juist. Probeer het opnieuw!")
                else:
                    st.balloons(); st.success("🎉 Taak Voltooid! +100 munten.")
                    st.session_state.db['saldi'][mijn_naam] += 100
                    st.session_state.db['completed_tasks'][mijn_naam].append(t['id'])
                    sla_db_op()
                    if st.button("Sluit Taak"): del st.session_state.active_task; del st.session_state.task_words; st.rerun()

        with t_lijsten:
            if st.session_state.db['vocab_lists']:
                for i, v in enumerate(st.session_state.db['vocab_lists']):
                    if st.button(f"📥 Download {v['title']}", key=f"dl_{i}"):
                        st.session_state.db['user_vocab'][mijn_naam].update(v['words'])
                        sla_db_op(); st.toast("Toegevoegd aan Lab!", icon="📚")
            else: st.write("Geen lijsten beschikbaar.")

        with t_chat:
            klas_berichten = [m for m in st.session_state.db['chat_messages'] if m.get('class') == mijn_klas]
            with st.container(height=400, border=True):
                for m in klas_berichten:
                    u = m['user']
                    u_saldo = st.session_state.db['saldi'].get(u, 0)
                    u_lvl = (u_saldo // 500) + 1
                    u_tag = st.session_state.db.get('chat_tags', {}).get(u, "")
                    tag_html = f"<span class='chat-tag'>{u_tag}</span>" if u_tag else ""
                    lvl_html = f"<span class='lvl-badge'>Lvl {u_lvl}</span>"
                    st.markdown(f"{lvl_html}{tag_html}**{u.capitalize()}**: {m['text']}", unsafe_allow_html=True)
            
            if p := st.chat_input("Bericht aan je klas..."):
                st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p, "class": mijn_klas})
                sla_db_op(); st.rerun()

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Leraar Dashboard")
    
    bestaande_klas = None
    for code, info in st.session_state.db.get('classes', {}).items():
        if info['teacher'] == mijn_naam: bestaande_klas = code; break
        
    if not bestaande_klas:
        st.warning("Je hebt nog geen klas aangemaakt!")
        c_naam = st.text_input("Kies een Klasnaam (bijv. Groep 8A)")
        c_code = st.text_input("Bedenk een Klascode (hiermee kunnen leerlingen joinen)")
        if st.button("Klas Aanmaken", type="primary"):
            if c_naam and c_code:
                if c_code in st.session_state.db.setdefault('classes', {}):
                    st.error("Deze code bestaat al. Kies een andere.")
                else:
                    st.session_state.db['classes'][c_code] = {"name": c_naam, "teacher": mijn_naam}
                    st.session_state.db['users'][mijn_naam]['class'] = c_code
                    sla_db_op(); st.success("Klas aangemaakt!"); st.rerun()
            else: st.error("Vul alles in.")
    else:
        k_info = st.session_state.db['classes'][bestaande_klas]
        st.info(f"Je beheert **{k_info['name']}** (Code: `{bestaande_klas}`)")
        
        t1, t2, t3 = st.tabs(["👥 Studenten Beheren", "📋 Nieuwe Taak", "📖 Vrije Lijst"])
        
        with t1:
            st.write("Voeg leerlingen toe of verwijder ze uit je klas.")
            alle_leerlingen = [u for u, d in st.session_state.db['users'].items() if d['role'] == 'student']
            in_mijn_klas = [u for u in alle_leerlingen if st.session_state.db['users'][u].get('class') == bestaande_klas]
            niet_in_klas = [u for u in alle_leerlingen if st.session_state.db['users'][u].get('class') != bestaande_klas]
            
            st.write(f"**Huidige leerlingen ({len(in_mijn_klas)}):**")
            for lln in in_mijn_klas:
                col_n, col_k = st.columns([3, 1])
                col_n.write(f"- {lln}")
                if col_k.button("Kick", key=f"kick_{lln}"):
                    st.session_state.db['users'][lln]['class'] = ""
                    sla_db_op(); st.toast(f"{lln} verwijderd uit klas."); st.rerun()
                    
            st.divider()
            if niet_in_klas:
                toevoegen = st.selectbox("Leerling toevoegen:", niet_in_klas)
                if st.button("Voeg toe aan klas"):
                    st.session_state.db['users'][toevoegen]['class'] = bestaande_klas
                    sla_db_op(); st.success(f"{toevoegen} toegevoegd!"); st.rerun()
            else: st.write("Geen losse leerlingen meer over.")
            
        with t2:
            tt = st.text_input("Titel van de Taak")
            tw = st.text_area("Woorden (nl=fr)")
            if st.button("Post Taak", type="primary"):
                if tt and tw:
                    d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in tw.split("\n") if "=" in l}
                    st.session_state.db['tasks'].append({"id": str(random.randint(10000, 99999)), "title": tt, "words": d, "class": bestaande_klas})
                    sla_db_op(); st.toast("Taak geplaatst!", icon="🚀"); st.rerun()
                else: st.warning("Vul alles in.")
        with t3:
            lt, lw = st.text_input("Lijst Naam"), st.text_area("Woordenlijst (nl=fr)")
            if st.button("Deel Lijst"):
                if lt and lw:
                    d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in lw.split("\n") if "=" in l}
                    st.session_state.db['vocab_lists'].append({"title": lt, "words": d, "class": bestaande_klas})
                    sla_db_op(); st.toast("Lijst gedeeld!", icon="✅"); st.rerun()

elif nav == "👑 Admin Room":
    st.title("👑 Admin Control Room")
    t1, t2, t3, t4, t5 = st.tabs(["⚙️ Systeem", "🏷️ Tags", "👩‍🏫 Promoties", "💰 Economie", "💾 RAW Database"])
    
    with t1:
        st.subheader("Systeem Beveiliging")
        st.session_state.db['lockdown'] = st.toggle("🔒 Activeer Global Lockdown", value=st.session_state.db.get('lockdown', False))
        if st.button("Opslaan Status"): sla_db_op(); st.toast("Opgeslagen!")
        
        st.divider()
        st.subheader("BETA Features")
        islands_on = st.session_state.db.setdefault('islands_enabled', False)
        if st.toggle("🏝️ Activeer Eilanden Systeem (BETA)", value=islands_on):
            st.session_state.db['islands_enabled'] = True
        else:
            st.session_state.db['islands_enabled'] = False
        if st.button("Opslaan Beta Features"): sla_db_op(); st.toast("Beta settings opgeslagen!"); st.rerun()
        
    with t2:
        st.subheader("Chat Tags Maken & Uitdelen")
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            nt = st.text_input("Nieuwe Tag Naam")
            if st.button("Maak Tag"):
                if nt not in st.session_state.db.setdefault('custom_tags', []):
                    st.session_state.db['custom_tags'].append(nt); sla_db_op(); st.success(f"Tag {nt} gemaakt!")
        with c_t2:
            speler = st.selectbox("Kies Speler", list(st.session_state.db['users'].keys()))
            kt = st.selectbox("Kies Tag", ["(Verwijder)"] + st.session_state.db.get('custom_tags', []))
            if st.button("Geef Tag", type="primary"):
                if kt == "(Verwijder)":
                    if speler in st.session_state.db['chat_tags']: del st.session_state.db['chat_tags'][speler]
                else: st.session_state.db['chat_tags'][speler] = kt
                sla_db_op(); st.toast("Tag bijgewerkt!", icon="🏷️")
    with t3:
        st.subheader("Promoveer Student")
        studenten = [u for u, data in st.session_state.db['users'].items() if data.get('role') != 'admin']
        if studenten:
            dl = st.selectbox("Selecteer Student", studenten)
            if st.button("Maak Leraar", type="primary"):
                st.session_state.db['users'][dl]['role'] = "teacher"
                sla_db_op(); st.success(f"{dl} is nu leraar. Zij kunnen nu in hun eigen paneel een klas maken!")
    with t4:
        st.subheader("Munten Beheer")
        doel = st.selectbox("Speler", list(st.session_state.db['users'].keys()), key="cs")
        aantal = st.number_input("Aantal", value=100)
        if st.button("Geef Munten"):
            st.session_state.db['saldi'][doel] += aantal
            sla_db_op(); st.toast("Gedaan!", icon="💸")
            
    with t5:
        st.subheader("Database Beheer (RAW)")
        if st.button("Wis Alle Taken & Lijsten"):
            st.session_state.db['tasks'] = []
            st.session_state.db['completed_tasks'] = {u: [] for u in st.session_state.db['users'].keys()}
            st.session_state.db['vocab_lists'] = []
            sla_db_op(); st.toast("Alles gewist!", icon="🧹"); st.rerun()
            
        raw = st.text_area("JSON Editor", value=json.dumps(st.session_state.db, indent=2), height=300)
        if st.button("Force Save Database", type="primary"):
            try:
                st.session_state.db = json.loads(raw)
                sla_db_op()
                st.toast("Opgeslagen!", icon="💾")
                st.rerun()
            except Exception as e:
                st.error(f"JSON Error: {e}")
