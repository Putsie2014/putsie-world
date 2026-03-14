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
SITE_TITLE = "Putsie WORLD 🏝️ v15.0"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# JOUW GITHUB URL VOOR DE PLAATJES
IMG_BASE_URL = "https://raw.githubusercontent.com/JOUW_NAAM/putsie-world/main/assets/"

st.set_page_config(page_title=SITE_TITLE, layout="wide", initial_sidebar_state="expanded")

# --- 2. GAME HUD STYLING (FULLSCREEN IMMERSION) ---
def apply_premium_design():
    st.markdown("""
    <style>
        /* 1. VERBERG STREAMLIT WEBSITE ELEMENTEN */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
            max-width: 98% !important;
        }
        
        /* 2. GAME ACHTERGROND (Donker en mysterieus) */
        .stApp {
            background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
            color: white;
        }
        
        /* 3. GAME HUD (Donkere panelen met neon randjes ipv wit) */
        div[data-testid="stExpander"], .stChatMessage, div.element-container div.stMarkdown div, .stTabs {
            background: rgba(15, 20, 35, 0.8) !important;
            backdrop-filter: blur(15px);
            border-radius: 12px;
            border: 1px solid rgba(0, 210, 255, 0.3);
            padding: 15px;
            color: #e0e0e0 !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }
        p, span, label { color: #e0e0e0 !important; }
        h1, h2, h3 { color: #00d2ff !important; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 0 10px rgba(0, 210, 255, 0.3); }
        
        /* 4. GAME KNOPPEN & INPUTS */
        .stButton button { 
            background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%) !important;
            color: white !important;
            border: none !important;
            transition: all 0.2s ease 0s !important; 
            border-radius: 8px !important; 
            font-weight: bold;
        }
        .stButton button:hover { transform: translateY(-2px) scale(1.02) !important; box-shadow: 0 5px 15px rgba(0, 210, 255, 0.5) !important; }
        input, textarea { background: rgba(0,0,0,0.5) !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; }
        
        /* 5. TERMINAL */
        .hacker-term {
            background-color: #050505 !important; color: #0f0 !important;
            font-family: 'Courier New', Courier, monospace !important;
            padding: 25px; border-radius: 12px; border: 2px solid #0f0;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2); text-shadow: 0 0 5px #0f0;
        }
        
        /* Tags & Badges */
        .chat-tag { background: linear-gradient(90deg, #FFD700, #FFA500); color: black; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px; margin-right: 5px; }
        .lvl-badge { background: #4CAF50; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; margin-right: 5px; }
        
        /* 6. SEAMLESS GAME GRID VOOR EILANDEN */
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
        .game-tile.filled { background: rgba(0, 210, 255, 0.15); border: 1px solid rgba(0, 210, 255, 0.3); font-size: 35px; }
        
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

# --- 3. DATABASE ENGINE (CRASH-FREE VERSIE) ---
def laad_db():
    basis_db = {
        "users": {"elliot": {"pw": "Putsie", "role": "admin"}},
        "saldi": {}, "ai_points": {}, "user_vocab": {}, "chat_messages": [], "vocab_lists": [],
        "tasks": [], "completed_tasks": {}, "klascodes": {"ADMIN-000": "elliot"}, "teacher_classes": {},
        "chat_tags": {}, "custom_tags": ["👑 ADMIN", "⭐ VIP", "🔥 STRIJDER"], "daily_claims": {},
        "islands": {}, "island_levels": {}, "inventory": {}, 
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

# VEILIGE DATABASE INITIALISATIE
st.session_state.db.setdefault('islands', {})
st.session_state.db.setdefault('island_levels', {})
st.session_state.db.setdefault('inventory', {})

# --- 4. HACKER COMMAND PANEL ---
if st.session_state.get('in_terminal', False):
    st.markdown("<div class='hacker-term'><h1>>_ SYSTEM OVERRIDE V15.0</h1><p>Root Access Granted. Type /activateputsie for pet.</p></div>", unsafe_allow_html=True)
    cmd = st.text_input(">").strip()
    if cmd == "/deactivatelockdown":
        st.session_state.db['lockdown'] = False; sla_db_op(); st.toast("🔓 Lockdown gedeactiveerd!")
    elif cmd == "/activatelockdown":
        st.session_state.db['lockdown'] = True; sla_db_op(); st.toast("🔒 Systeem in Lockdown!")
    elif cmd == "/activateputsie":
        st.session_state.putsie_active = True; st.success("PROTOCOL: Putsie geactiveerd.")
    elif cmd.startswith("/openaccount"):
        target = cmd.split(" ")[1].lower() if len(cmd.split(" ")) > 1 else ""
        if target in st.session_state.db['users'] or target == "elliot":
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
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"
                    st.rerun()
                elif u in st.session_state.db['users'] and st.session_state.db['users'][u]["pw"] == p:
                    st.session_state.ingelogd, st.session_state.username = True, u
                    st.session_state.role = st.session_state.db['users'][u]["role"]
                    st.rerun()
                else: st.error("Inloggegevens fout!")
                
        with t_reg:
            st.info("Leraren accounts kunnen alleen door de Admin worden aangemaakt.")
            nu = st.text_input("Kies Gebruikersnaam").lower().strip()
            np = st.text_input("Kies Wachtwoord", type="password")
            kc = st.text_input("Vul Klascode in")
            
            if st.button("Account Aanmaken", use_container_width=True):
                if not nu or not np or not kc: st.error("⚠️ Vul alle velden in!")
                elif nu in st.session_state.db['users']: st.error("⚠️ Deze naam is al bezet!")
                elif kc not in st.session_state.db['klascodes']: st.error("⛔ Ongeldige klascode!")
                else:
                    st.session_state.db['users'][nu] = {"pw": np, "role": "student"}
                    st.session_state.db['saldi'][nu], st.session_state.db['ai_points'][nu] = 0, 5
                    st.session_state.db['user_vocab'][nu] = {}
                    sla_db_op(); st.success("✅ Account succesvol aangemaakt! Log nu in.")
    st.stop()

# --- 6. LOCKDOWN & LEVEL LOGICA ---
mijn_naam = st.session_state.username
is_admin = mijn_naam == "elliot" or st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"

if st.session_state.db.get('lockdown') and not is_admin and not st.session_state.get('lockdown_bypass', False):
    st.markdown(f"<div style='text-align:center; padding:100px; background: rgba(255,0,0,0.5); border-radius:20px;'><h1>🚫 CRITICAL LOCKDOWN</h1><h3>{st.session_state.db['lockdown_msg']}</h3></div>", unsafe_allow_html=True)
    if st.button("Uitloggen"): st.session_state.ingelogd = False; st.rerun()
    st.stop()

mijn_saldo = st.session_state.db['saldi'].get(mijn_naam, 0)
mijn_level = (mijn_saldo // 500) + 1 
mijn_tag = st.session_state.db.get('chat_tags', {}).get(mijn_naam, "")

# PUTSIE PET
if 'putsie_active' not in st.session_state: st.session_state.putsie_active = False
if 'putsie_mood' not in st.session_state: st.session_state.putsie_mood = "😊"
if 'putsie_text' not in st.session_state: st.session_state.putsie_text = "Hoi Elliot!"
def putsie_reageer(actie):
    r = {"eten": ["Nom nom!", "Heerlijk!"], "spel": ["Wiiiieee!", "Je bent de beste!"], "idle": ["Kijk me zweven!", "Hoi!"]}
    st.session_state.putsie_text = random.choice(r[actie])

# --- 7. HUD SIDEBAR ---
with st.sidebar:
    if st.session_state.putsie_active:
        st.markdown(f"<div style='background:rgba(0,210,255,0.1); border:1px solid #00d2ff; border-radius:15px; padding:10px; text-align:center; margin-bottom:15px;'><div style='color:#00d2ff; font-weight:bold; margin-bottom:5px;'>{st.session_state.putsie_text}</div><div style='font-size:40px;'>{st.session_state.putsie_mood}</div></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🍎 Voer"): st.session_state.putsie_mood = "😋"; putsie_reageer("eten")
        if c2.button("🎾 Speel"): st.session_state.putsie_mood = "🤩"; putsie_reageer("spel")

    tag_html = f"<span class='chat-tag'>{mijn_tag}</span>" if mijn_tag else ""
    st.markdown(f"<h3>{tag_html}{mijn_naam.capitalize()}</h3>", unsafe_allow_html=True)
    st.caption(f"⭐ Lvl: {mijn_level}")
    
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("💰 Munten", mijn_saldo)
    col_s2.metric("💎 AI Punten", st.session_state.db['ai_points'].get(mijn_naam, 0))
    
    vandaag = datetime.now().strftime("%Y-%m-%d")
    laatste_claim = st.session_state.db.get('daily_claims', {}).get(mijn_naam, "")
    if laatste_claim != vandaag:
        if st.button("🎁 Claim Daily Bonus!", use_container_width=True):
            bonus = random.randint(20, 100)
            st.session_state.db['saldi'][mijn_naam] = st.session_state.db['saldi'].get(mijn_naam, 0) + bonus
            st.session_state.db.setdefault('daily_claims', {})[mijn_naam] = vandaag
            sla_db_op(); st.balloons(); st.toast(f"Je hebt {bonus} munten gekregen!", icon="🎁"); st.rerun()
        
    st.divider()
    nav_options = ["🏝️ Eiland & Wereld", "🏫 Klas Missies", "💬 Global Chat", "🇫🇷 Trainings Lab", "🤖 AI Hulp"]
    if is_teacher: nav_options.append("👩‍🏫 Leraar Paneel")
    if is_admin: nav_options.append("👑 Admin Room")
    
    nav = st.radio("Navigatie", nav_options)
    st.divider()
    if st.button("🚪 Afsluiten", use_container_width=True):
        st.session_state.ingelogd = False; st.rerun()

# --- 8. PAGINA'S ---

if nav == "🏝️ Eiland & Wereld":
    st.title("🏝️ World Builder")
    tab1, tab2, tab3 = st.tabs(["Mijn Eiland", "Bouwmarkt", "Wereldkaart"])
    
    with tab1:
        mijn_grid_size = st.session_state.db.setdefault('island_levels', {}).get(mijn_naam, 3)
        st.subheader(f"Jouw Eiland ({mijn_grid_size}x{mijn_grid_size})")
        
        eiland_data = st.session_state.db.setdefault('islands', {}).setdefault(mijn_naam, {})
        inventaris = st.session_state.db.setdefault('inventory', {}).setdefault(mijn_naam, {})
        
        # Grid Gecentreerd
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
            st.write(f"Bouwen op coördinaat: {st.session_state.build_pos}")
            beschikbaar = [item for item, amount in inventaris.items() if amount > 0]
            if beschikbaar:
                kies = st.selectbox("Inventaris:", beschikbaar)
                if st.button("Plaats Item", type="primary"):
                    inventaris[kies] -= 1
                    eiland_data[st.session_state.build_pos] = kies
                    del st.session_state.build_pos
                    sla_db_op(); st.rerun()
                if st.button("Annuleren"): del st.session_state.build_pos; st.rerun()
            else:
                st.warning("Inventaris leeg! Ga naar de Bouwmarkt.")
                if st.button("Annuleren"): del st.session_state.build_pos; st.rerun()

    with tab2:
        st.subheader("🛒 De Bouwmarkt")
        cols = st.columns(4)
        for i, (item, data) in enumerate(SHOP_ITEMS.items()):
            with cols[i % 4]:
                st.markdown(f"<div style='background:rgba(0,0,0,0.4); padding:10px; border-radius:10px; text-align:center; border:1px solid #00d2ff;'><h1>{data['emoji']}</h1><b>{item}</b><br>{data['prijs']} 🪙</div>", unsafe_allow_html=True)
                if st.button(f"Koop {item}", key=f"buy_{item}", use_container_width=True):
                    if mijn_saldo >= data['prijs']:
                        st.session_state.db.setdefault('saldi', {})[mijn_naam] = mijn_saldo - data['prijs']
                        inventaris[item] = inventaris.get(item, 0) + 1
                        sla_db_op(); st.toast(f"{item} gekocht!", icon="🛒"); st.rerun()
                    else: st.error("Te weinig munten!")
                    
        st.divider()
        st.subheader("🏝️ Eiland Uitbreiden")
        kosten_upgrade = mijn_grid_size * 5000
        if st.button(f"Vergroot Eiland naar {mijn_grid_size + 1}x{mijn_grid_size + 1} ({kosten_upgrade} 🪙)"):
            if mijn_saldo >= kosten_upgrade:
                st.session_state.db['saldi'][mijn_naam] -= kosten_upgrade
                st.session_state.db.setdefault('island_levels', {})[mijn_naam] = mijn_grid_size + 1
                sla_db_op(); st.balloons(); st.rerun()
            else: st.error("Onvoldoende fondsen!")

    with tab3:
        st.subheader("🌍 Wereldkaart (Bezoek Klasgenoten)")
        for student in st.session_state.db['users'].keys():
            if student != mijn_naam and st.session_state.db['users'][student].get('role') != 'admin':
                col_a, col_b = st.columns([3, 1])
                col_a.write(f"**Sector van {student.capitalize()}**")
                if col_b.button("Bezoeken", key=f"visit_{student}"):
                    st.session_state.visitor_target = student
                    
        if 'visitor_target' in st.session_state:
            target = st.session_state.visitor_target
            t_size = st.session_state.db.setdefault('island_levels', {}).get(target, 3)
            t_data = st.session_state.db.setdefault('islands', {}).get(target, {})
            st.divider()
            st.subheader(f"U bezoekt: {target.capitalize()} ({t_size}x{t_size})")
            
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
                            
            if st.button("Terug naar Wereldkaart"): del st.session_state.visitor_target; st.rerun()

elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Assistent (Llama 3.1)")
    c1, c2 = st.columns([2, 1])
    with c2:
        st.write("🛒 **Winkel**")
        if st.button(f"Koop 1 💎 voor {AI_PUNT_PRIJS} 🪙", use_container_width=True):
            if mijn_saldo >= AI_PUNT_PRIJS:
                st.session_state.db['saldi'][mijn_naam] -= AI_PUNT_PRIJS
                st.session_state.db['ai_points'][mijn_naam] = st.session_state.db['ai_points'].get(mijn_naam, 0) + 1
                sla_db_op(); st.toast("💎 Opgeladen!"); st.rerun()
            else: st.error("Onvoldoende fondsen!")
    with c1:
        vraag = st.text_area("Stel je vraag aan de terminal:")
        if st.button("Vraag verzenden (-1 💎)", type="primary"):
            if st.session_state.db['ai_points'].get(mijn_naam, 0) > 0:
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(messages=[{"role": "user", "content": vraag}], model=MODEL_NAAM)
                    st.session_state.ai_res = res.choices[0].message.content
                    st.session_state.db['ai_points'][mijn_naam] -= 1; sla_db_op()
                except Exception as e: st.error(f"AI Link Offline. API Key nodig.")
            else: st.warning("Geen AI punten beschikbaar!")
        if 'ai_res' in st.session_state: st.info(st.session_state.ai_res)

elif nav == "💬 Global Chat":
    st.title("💬 Global Chat")
    with st.container(height=450, border=True):
        for m in st.session_state.db['chat_messages']:
            u = m['user']
            u_saldo = st.session_state.db['saldi'].get(u, 0)
            u_lvl = (u_saldo // 500) + 1
            u_tag = st.session_state.db.get('chat_tags', {}).get(u, "")
            tag_html = f"<span class='chat-tag'>{u_tag}</span>" if u_tag else ""
            lvl_html = f"<span class='lvl-badge'>Lvl {u_lvl}</span>"
            st.markdown(f"{lvl_html}{tag_html}**{u.capitalize()}**: {m['text']}", unsafe_allow_html=True)
            
    if p := st.chat_input("Verzend een bericht naar de server..."):
        st.session_state.db['chat_messages'].append({"user": mijn_naam, "text": p}); sla_db_op(); st.rerun()

elif nav == "🇫🇷 Trainings Lab":
    st.title("🇫🇷 Trainings Lab")
    w = st.session_state.db['user_vocab'].get(mijn_naam, {})
    if w:
        if 'q' not in st.session_state: st.session_state.q = random.choice(list(w.keys()))
        g = st.text_input(f"Vertaal: {st.session_state.q}")
        if st.button("Bevestig", type="primary"):
            if g.lower().strip() == w[st.session_state.q].lower().strip():
                st.session_state.db['saldi'][mijn_naam] = mijn_saldo + 20
                st.toast("Correct! +20 🪙", icon="🎉")
                del st.session_state.q; sla_db_op(); st.rerun()
            else: st.error("Onjuist!")
    else: st.info("Geen data gevonden. Download eerst bestanden bij Klas Missies.")

elif nav == "🏫 Klas Missies":
    st.title("🏫 Klas Missies")
    if 'active_task' not in st.session_state:
        beschikbare_taken = [t for t in st.session_state.db['tasks'] if t.get('id', t.get('title')) not in st.session_state.db.get('completed_tasks', {}).get(mijn_naam, [])]
        c1, c2 = st.columns(2)
        with c1:
            if beschikbare_taken:
                st.subheader("📋 Actieve Missies")
                for t in beschikbare_taken:
                    with st.container(border=True):
                        if 'words' in t:
                            st.write(f"**{t.get('title', 'Missie')}** ({len(t['words'])} objectieven)")
                            if st.button("Start Missie", key=f"btn_{t.get('id')}", type="primary"):
                                st.session_state.active_task = t
                                st.session_state.task_words = list(t['words'].keys())
                                st.rerun()
                        else:
                            st.write(f"**{t.get('title', 'Missie')}**\n\n{t.get('desc', '')}")
                            if st.button("Markeer als Voltooid", key=f"read_{t.get('title')}"):
                                st.session_state.db.setdefault('completed_tasks', {}).setdefault(mijn_naam, []).append(t.get('title'))
                                sla_db_op(); st.rerun()
            elif st.session_state.db['tasks']: st.success("Alle missies voltooid!")
        with c2:
            if st.session_state.db['vocab_lists']:
                st.subheader("📚 Databanken")
                for i, v in enumerate(st.session_state.db['vocab_lists']):
                    if st.button(f"📥 Download {v['title']}", key=f"dl_{i}"):
                        st.session_state.db['user_vocab'].setdefault(mijn_naam, {}).update(v['words'])
                        sla_db_op(); st.toast("Data binnengehaald!", icon="📚")
    else:
        t = st.session_state.active_task
        nog_te_doen = len(st.session_state.task_words)
        totaal = len(t['words'])
        voortgang = totaal - nog_te_doen
        st.subheader(f"Missie: {t['title']}")
        st.progress(voortgang / totaal)
        st.write(f"Objectief {voortgang + 1} van {totaal}")
        
        if nog_te_doen > 0:
            huidig_woord = st.session_state.task_words[0]
            ans = st.text_input(f"Vertaal: {huidig_woord}", key="task_ans")
            if st.button("Controleer", type="primary"):
                if ans.lower().strip() == t['words'][huidig_woord].lower().strip():
                    st.toast("Correct!", icon="✅"); st.session_state.task_words.pop(0); st.rerun()
                else: st.error("Foutcode: Onjuiste vertaling.")
        else:
            st.balloons(); st.success("🎉 Missie Voltooid! +100 munten toegekend.")
            st.session_state.db['saldi'][mijn_naam] = mijn_saldo + 100
            st.session_state.db.setdefault('completed_tasks', {}).setdefault(mijn_naam, []).append(t['id'])
            sla_db_op()
            if st.button("Sluit Missie"): del st.session_state.active_task; del st.session_state.task_words; st.rerun()

elif nav == "👩‍🏫 Leraar Paneel":
    st.title("👩‍🏫 Commander Dashboard")
    mijn_klas = st.session_state.db.get('teacher_classes', {}).get(mijn_naam, "Geen")
    st.info(f"Team Code: **{mijn_klas}**")
    t1, t2 = st.tabs(["📋 Nieuwe Missie", "📖 Nieuwe Databank"])
    with t1:
        tt = st.text_input("Titel van Missie")
        tw = st.text_area("Data (nl=fr)")
        if st.button("Lanceer Missie", type="primary"):
            if tt and tw:
                d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in tw.split("\n") if "=" in l}
                st.session_state.db['tasks'].append({"id": str(random.randint(10000, 99999)), "title": tt, "words": d})
                sla_db_op(); st.toast("Missie live!", icon="🚀"); st.rerun()
            else: st.warning("Vul data in.")
    with t2:
        lt, lw = st.text_input("Databank Naam"), st.text_area("Data (nl=fr)")
        if st.button("Upload Databank"):
            if lt and lw:
                d = {l.split("=")[0].strip(): l.split("=")[1].strip() for l in lw.split("\n") if "=" in l}
                st.session_state.db['vocab_lists'].append({"title": lt, "words": d})
                sla_db_op(); st.toast("Upload voltooid!", icon="✅"); st.rerun()

elif nav == "👑 Admin Room":
    st.title("👑 System Root Access")
    t1, t2, t3, t4 = st.tabs(["🏷️ Tags", "👩‍🏫 Commanders", "💰 Economie", "⚙️ Systeem"])
    with t1:
        st.subheader("Tag Protocol")
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            nt = st.text_input("Nieuwe Tag")
            if st.button("Genereer Tag"):
                if nt not in st.session_state.db.setdefault('custom_tags', []):
                    st.session_state.db['custom_tags'].append(nt); sla_db_op(); st.success(f"Tag {nt} actief!")
        with c_t2:
            speler = st.selectbox("Selecteer User", list(st.session_state.db['users'].keys()))
            kt = st.selectbox("Wijs Tag Toe", ["(Verwijder)"] + st.session_state.db.get('custom_tags', []))
            if st.button("Toepassen", type="primary"):
                if kt == "(Verwijder)":
                    if speler in st.session_state.db.setdefault('chat_tags', {}): del st.session_state.db['chat_tags'][speler]
                else: st.session_state.db.setdefault('chat_tags', {})[speler] = kt
                sla_db_op(); st.toast("Tag systeem geüpdatet!", icon="🏷️")
    with t2:
        st.subheader("Promoveer User")
        studenten = [u for u, data in st.session_state.db['users'].items() if data.get('role') != 'admin']
        if studenten:
            dl = st.selectbox("Selecteer User", studenten)
            if st.button("Promoveer", type="primary"):
                nc = f"KLAS-{random.randint(1000, 9999)}"
                st.session_state.db['users'][dl]['role'] = "teacher"
                st.session_state.db['klascodes'][nc] = f"Klas van {dl}"
                st.session_state.db['teacher_classes'][dl] = nc
                sla_db_op(); st.success(f"Promotie voltooid. Toegangscode: {nc}")
    with t3:
        st.subheader("Economie Override")
        doel = st.selectbox("User", list(st.session_state.db['users'].keys()), key="cs")
        aantal = st.number_input("Waarde", value=100)
        if st.button("Injecteer Munten"):
            st.session_state.db.setdefault('saldi', {})[doel] = st.session_state.db.get('saldi', {}).get(doel, 0) + aantal
            sla_db_op(); st.toast("Injectie succesvol!", icon="💸")
    with t4:
        st.session_state.db['lockdown'] = st.toggle("System Lockdown", value=st.session_state.db['lockdown'])
        if st.button("Formatteer Missies & Data"):
            st.session_state.db['tasks'], st.session_state.db['completed_tasks'], st.session_state.db['vocab_lists'] = [], {}, []
            sla_db_op(); st.toast("Geformatteerd!", icon="🧹"); st.rerun()
        raw = st.text_area("JSON Core", value=json.dumps(st.session_state.db, indent=2), height=250)
        if st.button("Force Save", type="primary"):
            try:
                st.session_state.db = json.loads(raw)
                sla_db_op()
                st.toast("Core opgeslagen!", icon="💾")
                st.rerun()
            except Exception as e:
                st.error(f"Syntax Error: {e}")
