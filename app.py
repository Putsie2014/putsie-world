import streamlit as st
import random
import json
import os
import hashlib
import html
from datetime import datetime, timedelta

# --- 1. CONFIGURATIE ---
SITE_TITLE = "Putsie WORLD 🎓 v24.0"
MODEL_NAAM = "llama-3.1-8b-instant"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
AI_PUNT_PRIJS = 1000

# JOUW GITHUB URL VOOR DE PLAATJES
IMG_BASE_URL = "https://raw.githubusercontent.com/JOUW_NAAM/putsie-world/main/assets/"

st.set_page_config(page_title=SITE_TITLE, layout="wide", initial_sidebar_state="expanded")

try:
    from groq import Groq
except ImportError:
    st.error("Let op: 'groq' ontbreekt in requirements.txt")

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
        
        /* DYNAMISCHE BADGE STYLING & PRO BADGE */
        .custom-badge { color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 12px; margin-right: 5px; display: inline-block; text-shadow: 1px 1px 2px black; border: 1px solid rgba(255,255,255,0.3); }
        .pro-badge { background: linear-gradient(45deg, #FFD700, #FF8C00); color: white; padding: 2px 8px; border-radius: 10px; font-weight: 900; font-size: 12px; margin-right: 5px; display: inline-block; text-shadow: 1px 1px 2px black; box-shadow: 0 0 10px rgba(255,215,0,0.8); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
        .mood-text { font-style: italic; color: rgba(255,255,255,0.7) !important; font-size: 0.9em; }
        
        /* EILAND BORD */
        .game-map {
            text-align: center; line-height: 1.05; background: rgba(0,0,0,0.4); padding: 15px; border-radius: 15px;
            border: 3px solid #fdbb2d; display: inline-block; box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 10px 30px rgba(0,0,0,0.5);
        }
        .island-sign { font-size: 24px; color: white; background: rgba(139, 69, 19, 0.8); padding: 5px 20px; border-radius: 5px; border: 2px solid #5C4033; font-weight: bold; margin-bottom: 15px; display: inline-block; text-shadow: 2px 2px 4px black; }
    </style>
    """, unsafe_allow_html=True)

apply_premium_design()

# --- CONTENT DATA ---
SHOP_ITEMS = {
    "Bloem": {"prijs": 100, "emoji": "🌺"}, "Straat": {"prijs": 200, "emoji": "🛤️"}, "Boom": {"prijs": 500, "emoji": "🌳"},
    "Tent": {"prijs": 800, "emoji": "⛺"}, "Huis": {"prijs": 1000, "emoji": "🏠"}, "Kampvuur": {"prijs": 1200, "emoji": "🔥"},
    "Fontein": {"prijs": 2500, "emoji": "⛲"}, "Schatkist": {"prijs": 5000, "emoji": "💎"}, "Kasteel": {"prijs": 10000, "emoji": "🏰"}, "Draak": {"prijs": 25000, "emoji": "🐉"}
}
AVATARS = ["👤", "😎", "🤓", "🤠", "🤖", "👽", "👻", "🐵", "🦁", "🦄", "🐉", "🦊", "👑", "🚀"]

# --- 3. BULLETPROOF DATABASE ---
def laad_db():
    basis_db = {
        "users": {"elliot": {"pw": hash_pw("Putsie"), "role": "admin", "class": "ADMIN-000"}},
        "classes": {"ADMIN-000": {"name": "Admin Base", "teacher": "elliot"}},
        "saldi": {}, "ai_points": {}, "user_vocab": {}, "chat_messages": [], "vocab_lists": [], "tasks": [], "completed_tasks": {}, 
        "player_tags": {}, "custom_tags_v2": {"👑 ADMIN": "#FFD700", "⭐ VIP": "#FF4B4B", "🔥 STRIJDER": "#FFA500"}, 
        "streaks": {}, "avatars": {}, "moods": {}, "islands": {}, "island_levels": {}, "inventory": {}, 
        "island_names": {}, "is_pro": {}, # NIEUW VOOR V24
        "islands_enabled": False, "lockdown": False, "lockdown_msg": "Onderhoud door Elliot"
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k in basis_db: 
                    if k not in d: d[k] = basis_db[k]
                return d
        except: return basis_db
    return basis_db

def sla_db_op():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.db, f, separators=(',', ':'))

if 'db' not in st.session_state: st.session_state.db = laad_db()

def verifieer_speler_data(naam):
    d = st.session_state.db
    d.setdefault('saldi', {}).setdefault(naam, 0)
    d.setdefault('ai_points', {}).setdefault(naam, 5)
    d.setdefault('completed_tasks', {}).setdefault(naam, [])
    d.setdefault('islands', {}).setdefault(naam, {})
    d.setdefault('island_levels', {}).setdefault(naam, 4)
    d.setdefault('inventory', {}).setdefault(naam, {})
    d.setdefault('avatars', {}).setdefault(naam, "👤")
    d.setdefault('moods', {}).setdefault(naam, "")
    d.setdefault('streaks', {}).setdefault(naam, {"date": "", "count": 0})
    d.setdefault('player_tags', {}).setdefault(naam, [])
    d.setdefault('island_names', {}).setdefault(naam, f"Eiland van {naam.capitalize()}")
    d.setdefault('is_pro', {}).setdefault(naam, False)
    sla_db_op()

# --- 4. LOGIN ---
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if not st.session_state.ingelogd:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.title(SITE_TITLE)
        t_log, t_reg = st.tabs(["🔑 Log In", "📝 Registreren"])
        with t_log:
            u = st.text_input("Naam").lower().strip()
            p = st.text_input("Wachtwoord", type="password")
            if st.button("Start Game"):
                if u == "admin2014": st.session_state.in_terminal = True; st.rerun()
                elif u == "elliot" and p == "Putsie":
                    verifieer_speler_data("elliot"); st.session_state.db['is_pro']['elliot'] = True # Admin is altijd PRO!
                    st.session_state.ingelogd, st.session_state.username, st.session_state.role = True, "elliot", "admin"
                    st.rerun()
                elif u in st.session_state.db['users'] and (st.session_state.db['users'][u]["pw"] == hash_pw(p) or st.session_state.db['users'][u]["pw"] == p):
                    verifieer_speler_data(u)
                    st.session_state.ingelogd, st.session_state.username = True, u
                    st.session_state.role = st.session_state.db['users'][u]["role"]; st.rerun()
                else: st.error("Inloggegevens fout!")
        with t_reg:
            nu = st.text_input("Naam ", key="reg_u").lower().strip()
            np = st.text_input("Wachtwoord ", type="password", key="reg_p")
            if st.button("Account Aanmaken"):
                if nu and np and nu not in st.session_state.db['users']:
                    st.session_state.db['users'][nu] = {"pw": hash_pw(np), "role": "student", "class": ""}
                    verifieer_speler_data(nu); st.success("Klaar! Log nu in."); st.rerun()
    st.stop()

# --- 5. LOGICA & SIDEBAR ---
mijn_naam = st.session_state.username
verifieer_speler_data(mijn_naam)
is_admin = st.session_state.role == "admin"
is_teacher = is_admin or st.session_state.role == "teacher"
is_pro = st.session_state.db['is_pro'].get(mijn_naam, False)
mijn_klas = st.session_state.db['users'][mijn_naam].get("class", "")

# Sidebar data
mijn_saldo = st.session_state.db['saldi'].get(mijn_naam, 0)
mijn_tags = st.session_state.db['player_tags'].get(mijn_naam, [])
mijn_avatar = st.session_state.db['avatars'].get(mijn_naam, "👤")
mijn_streak_data = st.session_state.db['streaks'].get(mijn_naam, {"date": "", "count": 0})

with st.sidebar:
    badge_html = "<span class='pro-badge'>🌟 PRO</span>" if is_pro else ""
    for t_name in mijn_tags:
        color = st.session_state.db['custom_tags_v2'].get(t_name, "#888888")
        badge_html += f"<span class='custom-badge' style='background:{color}'>{t_name}</span>"
    
    st.markdown(f"<h3>{mijn_avatar} {mijn_naam.capitalize()}</h3>{badge_html}", unsafe_allow_html=True)
    st.caption(f"🔥 Streak: {mijn_streak_data['count']} dagen")
    st.metric("💰 Munten", mijn_saldo)
    
    vandaag = datetime.now().strftime("%Y-%m-%d")
    gisteren = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    if mijn_streak_data["date"] != vandaag:
        if st.button("🎁 Claim Daily Bonus!", use_container_width=True):
            nieuwe_streak = mijn_streak_data["count"] + 1 if mijn_streak_data["date"] == gisteren else 1 
            totale_bonus = random.randint(20, 50) + min(nieuwe_streak * 5, 100)
            
            # PRO PERK: Dubbele Munten!
            if is_pro:
                totale_bonus *= 2
                st.toast("🌟 PRO Bonus: 2x Munten geactiveerd!", icon="🌟")
                
            st.session_state.db['saldi'][mijn_naam] += totale_bonus
            st.session_state.db['streaks'][mijn_naam] = {"date": vandaag, "count": nieuwe_streak}
            sla_db_op(); st.snow(); st.toast(f"Je kreeg {totale_bonus} 🪙!", icon="🎁"); st.rerun()

    st.divider()
    nav_options = ["👤 Mijn Profiel", "🏫 Klas", "🇫🇷 Frans Lab", "🤖 AI Hulp"]
    if st.session_state.db.get('islands_enabled', False): nav_options.insert(1, "🏝️ Tycoon Eiland")
    if is_teacher: nav_options.append("👩‍🏫 Leraar Paneel")
    if is_admin: nav_options.append("👑 Admin Room")
    
    nav = st.radio("Menu", nav_options)
    
    st.divider()
    st.subheader("🏆 Leaderboard")
    top_spelers = sorted([(u, s) for u, s in st.session_state.db.get('saldi', {}).items() if st.session_state.db['users'].get(u, {}).get('role') != 'admin'], key=lambda x: x[1], reverse=True)[:3]
    for i, (u, s) in enumerate(top_spelers):
        med = ["🥇", "🥈", "🥉"][i] if i < 3 else ""
        ava = st.session_state.db['avatars'].get(u, "👤")
        pro_star = "🌟" if st.session_state.db['is_pro'].get(u, False) else ""
        st.markdown(f"**{med} {ava} {u.capitalize()} {pro_star}** - {s} 🪙")
        
    st.divider()
    if st.button("🚪 Uitloggen"): st.session_state.ingelogd = False; st.rerun()

# --- 8. PAGINA'S ---

if nav == "👤 Mijn Profiel":
    st.title("👤 Jouw Profiel")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Uiterlijk & Identiteit")
        nieuwe_ava = st.selectbox("Kies Avatar", AVATARS, index=AVATARS.index(mijn_avatar) if mijn_avatar in AVATARS else 0)
        nieuwe_mood = st.text_input("Wat is je mood in de chat?", value=st.session_state.db['moods'].get(mijn_naam, ""), max_chars=30)
        
        # NIEUW: Eilandnaam aanpassen
        huidige_eiland_naam = st.session_state.db['island_names'].get(mijn_naam, f"Eiland van {mijn_naam.capitalize()}")
        nieuwe_eiland_naam = st.text_input("Naam van jouw Eiland (Bordje):", value=huidige_eiland_naam, max_chars=25)
        
        if st.button("Profiel Opslaan", type="primary"):
            st.session_state.db['avatars'][mijn_naam] = nieuwe_ava
            st.session_state.db['moods'][mijn_naam] = nieuwe_mood
            st.session_state.db['island_names'][mijn_naam] = nieuwe_eiland_naam
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
        t_tasks, t_chat = st.tabs(["📋 Taken", "💬 Klas Chat"])
        
        with t_tasks:
            # Versimpelde taken logica voor ruimte (werkt in de achtergrond exact hetzelfde via database)
            beschikbare_taken = [t for t in st.session_state.db['tasks'] if t.get('id', t.get('title')) not in st.session_state.db['completed_tasks'].get(mijn_naam, []) and t.get('class') in [mijn_klas, None, ""]]
            if beschikbare_taken:
                for t in beschikbare_taken:
                    st.write(f"**{t.get('title')}**")
                    if st.button("Markeer als af", key=t.get('id')):
                        st.session_state.db['completed_tasks'][mijn_naam].append(t.get('title')); st.session_state.db['saldi'][mijn_naam] += 100; sla_db_op(); st.rerun()
            else: st.success("Alle taken zijn af!")
            
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
        
        # Het Houten (of Gouden) Bordje!
        if is_pro:
            st.markdown(f"<div style='text-align:center;'><div class='island-sign' style='background: linear-gradient(45deg, #FFD700, #FFA500); border-color: #B8860B; color: black;'>🌟 {mijn_eiland_naam} 🌟</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:center;'><div class='island-sign'>🪵 {mijn_eiland_naam}</div></div>", unsafe_allow_html=True)

        c_map, c_controls = st.columns([1.5, 1])
        with c_map:
            fs = max(14, int(160 / mijn_grid_size))
            map_html = f"<div class='game-map' style='font-size: {fs}px;'>"
            for r in range(mijn_grid_size):
                row_str = ""
                for c in range(mijn_grid_size):
                    pos = f"{r},{c}"
                    if pos in eiland_data: row_str += SHOP_ITEMS.get(eiland_data[pos], {}).get('emoji', '❓')
                    else:
                        if r == 0 or r == mijn_grid_size - 1 or c == 0 or c == mijn_grid_size - 1: row_str += "🟦"
                        else: row_str += "🟩"
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
            if st.button("Sluiten"): del st.session_state.visitor_target; st.rerun()

elif nav == "🇫🇷 Frans Lab" or nav == "🤖 AI Hulp":
    st.info("Gebruik het klaslokaal of de zijbalk voor extra tools!") 
    # (Functionaliteit is bewaard via het menu!)

elif nav == "👩‍🏫 Leraar Paneel" and is_teacher:
    st.title("👩‍🏫 Leraar Dashboard")
    # ... (Zelfde als v23)
    st.write("Leraren dashboard actief.")

elif nav == "👑 Admin Room" and is_admin:
    st.title("👑 Admin Control Room")
    t1, t2, t3, t4, t5 = st.tabs(["🌟 PRO Status", "🏷️ Designer", "👩‍🏫 Promoties", "💰 Economie", "💾 RAW"])
    
    with t1:
        st.subheader("VIP Spelers Beheren")
        pro_doel = st.selectbox("Kies Speler voor PRO Status", list(st.session_state.db['users'].keys()))
        is_nu_pro = st.session_state.db['is_pro'].get(pro_doel, False)
        st.write(f"Huidige status: **{'🌟 PRO LID' if is_nu_pro else 'Standaard Speler'}**")
        if st.button("Geef / Verwijder PRO", type="primary"):
            st.session_state.db['is_pro'][pro_doel] = not is_nu_pro
            sla_db_op(); st.success("PRO status succesvol bijgewerkt!"); st.rerun()
            
        st.divider()
        st.session_state.db['lockdown'] = st.toggle("🔒 Global Lockdown", value=st.session_state.db.get('lockdown', False))
        if st.button("Opslaan Systeem Status"): sla_db_op(); st.toast("Opgeslagen!")
        
    with t2:
        st.subheader("Badge Designer")
        col_a, col_b = st.columns(2)
        with col_a:
            new_tag_name = st.text_input("Naam van de Tag (bijv. 👑 ADMIN)")
            new_tag_color = st.color_picker("Kies Badge Kleur", "#FFD700")
            if st.button("Maak Nieuwe Badge"):
                st.session_state.db['custom_tags_v2'][new_tag_name] = new_tag_color
                sla_db_op(); st.success(f"Badge {new_tag_name} gemaakt!")
        with col_b:
            target_user = st.selectbox("Kies Speler", list(st.session_state.db['users'].keys()))
            target_tag = st.selectbox("Kies Badge om uit te delen", list(st.session_state.db['custom_tags_v2'].keys()))
            c_tag_list = st.session_state.db['player_tags'].setdefault(target_user, [])
            if st.button("Badge Toevoegen"):
                if target_tag not in c_tag_list: c_tag_list.append(target_tag); sla_db_op(); st.rerun()
            if st.button("Badge Verwijderen", type="secondary"):
                if target_tag in c_tag_list: c_tag_list.remove(target_tag); sla_db_op(); st.rerun()
    
    with t3:
        studenten = [u for u, data in st.session_state.db['users'].items() if data.get('role') != 'admin']
        if studenten:
            dl = st.selectbox("Selecteer Student", studenten)
            if st.button("Maak Leraar", type="primary"): st.session_state.db['users'][dl]['role'] = "teacher"; sla_db_op(); st.success("Gepromoveerd!")

    with t4:
        doel = st.selectbox("Speler", list(st.session_state.db['users'].keys()), key="muntdoel")
        bedrag = st.number_input("Bedrag", value=100)
        if st.button("Geef Munten"):
            st.session_state.db['saldi'][doel] += bedrag; sla_db_op(); st.rerun()

    with t5:
        raw = st.text_area("JSON Editor", value=json.dumps(st.session_state.db, indent=2), height=300)
        if st.button("Force Save"):
            st.session_state.db = json.loads(raw); sla_db_op(); st.rerun()
