import streamlit as st
import random
from openai import OpenAI
import streamlit.components.v1 as components

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v3.0"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# De "Coole" achtergrond
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- AI CLIENT ---
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# --- INITIALISATIE DATABASE ---
if 'users' not in st.session_state:
    st.session_state.users = {
        "elliot": {"pw": "Putsie", "role": "admin"},
        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
    }
if 'tasks' not in st.session_state: st.session_state.tasks = []
if 'ingelogd' not in st.session_state: st.session_state.ingelogd = False
if 'active_task' not in st.session_state: st.session_state.active_task = None
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 1000, "annelies": 500}
if 'class_code' not in st.session_state: st.session_state.class_code = "1234"
if 'class_name' not in st.session_state: st.session_state.class_name = "Putsie's Klas"
if 'frans_woord_nu' not in st.session_state: st.session_state.frans_woord_nu = "hallo"

frans_dict = {"hallo": "bonjour", "bedankt": "merci", "school": "école", "boek": "livre", "brood": "pain"}

# --- AI FUNCTIE ---
def vraag_groq(vraag, systeem_prompt="Je bent een leraar."):
    if st.session_state.active_task:
        return "⚠️ **AI BLOKKADE:** Je bent bezig aan een taak! Maak deze eerst af."
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": systeem_prompt}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"AI Error: {e}"

# --- LOGIN SCHERM ---
if not st.session_state.ingelogd:
    st.title(f"🔐 {SITE_TITLE}")
    tab1, tab2 = st.tabs(["🚀 Inloggen", "📝 Registreren"])
    
    with tab1:
        u = st.text_input("Gebruikersnaam", key="login_user").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="login_pw")
        if st.button("Log in", key="login_btn"):
            if u in st.session_state.users:
                u_data = st.session_state.users[u]
                correct_pw = u_data["pw"]
                if correct_pw == p:
                    st.session_state.ingelogd = True
                    st.session_state.username = u
                    st.session_state.role = u_data.get("role", "student")
                    st.rerun()
                else: st.error("Wachtwoord onjuist.")
            else: st.error("Gebruiker niet gevonden.")
        
        with st.expander("🛠️ Systeemherstel"):
            rc = st.text_input("Reset code", type="password", key="reset_code")
            if st.button("Hard Reset", key="reset_btn"):
                if rc == "Putsie":
                    st.session_state.users = {
                        "elliot": {"pw": "Putsie", "role": "admin"},
                        "annelies": {"pw": "JufAnnelies", "role": "teacher"}
                    }
                    st.session_state.tasks = []
                    st.session_state.class_code = "1234"
                    st.rerun()

    with tab2:
        nu = st.text_input("Kies een Naam", key="reg_user").lower().strip()
        np = st.text_input("Kies een Wachtwoord", type="password", key="reg_pw")
        code_input = st.text_input("Klascode", key="reg_code")
        if st.button("Account Aanmaken", key="reg_btn"):
            if code_input == st.session_state.class_code:
                if nu and np and nu not in st.session_state.users:
                    st.session_state.users[nu] = {"pw": np, "role": "student"}
                    st.session_state.saldi[nu] = 0
                    st.success("Gelukt! Je kunt nu inloggen.")
                else: st.error("Naam bezet of leeg.")
            else: st.error("Klascode onjuist!")
    st.stop()

# --- INTERFACE ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
st.sidebar.info(f"Klas: **{st.session_state.class_name}**\nCode: **{st.session_state.class_code}**")

# Zoek deze regel en voeg '🎮 3D Doolhof' toe:
opts = ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab", "🎮 3D Doolhof"]
if st.session_state.role in ["teacher", "admin"]:
    opts.append("📚 Leraar Paneel")
if st.session_state.username == "elliot":
    opts.append("👑 Super Admin")

nav = st.sidebar.radio("Navigatie", opts)

# --- DE KLAS ---
if nav == "🏫 De Klas":
    st.title(f"🏫 Welkom bij {st.session_state.class_name}")
    st.success(f"De huidige klascode is: `{st.session_state.class_code}`")
    
    st.subheader("Beschikbare Taken")
    if not st.session_state.tasks: st.write("Geen taken momenteel.")
    for i, t in enumerate(st.session_state.tasks):
        if st.button(f"Start: {t['name']}", key=f"task_{i}"):
            st.session_state.active_task = t
            st.rerun()

    if st.session_state.active_task:
        st.error(f"📍 BEZIG MET TAAK: {st.session_state.active_task['name']}")
        st.info(st.session_state.active_task['content'])
        if st.button("Taak Inleveren", key="finish_task"):
            st.session_state.active_task = None
            st.success("Taak ingediend!")
            st.rerun()

# --- LERAAR PANEEL ---
elif nav == "📚 Leraar Paneel":
    st.title("👨‍🏫 Leraar Paneel")
    st.subheader("Taak Toevoegen")
    t_n = st.text_input("Naam van taak")
    t_i = st.text_area("Wat moeten de leerlingen doen?")
    if st.button("Taak versturen naar klas"):
        st.session_state.tasks.append({"name": t_n, "content": t_i})
        st.success("Taak geplaatst!")

# --- SUPER ADMIN (ALLEEN ELLIOT) ---
elif nav == "👑 Super Admin":
    st.title("👑 Elliot's Super Admin Paneel")
    
    # 1. Klas Naam aanpassen
    st.subheader("📁 Klas Instellingen")
    nieuwe_klasnaam = st.text_input("Nieuwe naam voor je klas:", value=st.session_state.class_name)
    if st.button("Klasnaam Opslaan"):
        st.session_state.class_name = nieuwe_klasnaam
        st.success("Klasnaam aangepast!")
        st.rerun()

    # 2. Database overzicht
    st.subheader("📊 Volledige Database")
    st.json(st.session_state.users)
    
    # 3. Spelers beheren (Ban/Geld)
    st.subheader("👥 Speler Beheer")
    for speler in list(st.session_state.users.keys()):
        if speler != "elliot": # Elliot kan zichzelf niet bannen
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                col1.write(f"**{speler}** ({st.session_state.users[speler]['role']})")
                
                # Geld aanpassen
                huidig_geld = st.session_state.saldi.get(speler, 0)
                nieuw_geld = col2.number_input(f"Saldo {speler}", value=huidig_geld, key=f"money_{speler}")
                if col3.button("Update $", key=f"upd_{speler}"):
                    st.session_state.saldi[speler] = nieuw_geld
                    st.success("Geld aangepast!")
                
                # Speler bannen
                if col4.button("🚫 PERM BAN", key=f"ban_{speler}"):
                    del st.session_state.users[speler]
                    if speler in st.session_state.saldi: del st.session_state.saldi[speler]
                    st.warning(f"{speler} is verbannen!")
                    st.rerun()
            st.divider()

# --- AI HULP ---
elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    vraag = st.text_area("Stel je vraag:")
    if st.button("Vraag het"):
        with st.spinner("AI denkt na..."):
            st.write(vraag_groq(vraag))

# --- FRANS LAB ---
elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    if st.button("Nieuw Woord", key="new_fr"):
        st.session_state.frans_woord_nu = random.choice(list(frans_dict.keys()))
        st.rerun()
    st.subheader(f"Vertaal: **{st.session_state.frans_woord_nu}**")
    p_ans = st.text_input("Antwoord:", key="ans_fr").lower().strip()
    if st.button("Check", key="check_fr"):
        if p_ans == frans_dict[st.session_state.frans_woord_nu]:
            st.success("Goedzo! +5 munten.")
            st.session_state.saldi[st.session_state.username] = st.session_state.saldi.get(st.session_state.username, 0) + 5
        else: st.error(f"Fout! Het was: {frans_dict[st.session_state.frans_woord_nu]}")

if st.sidebar.button("Uitloggen", key="logout"):
    st.session_state.ingelogd = False
    st.rerun()
# --------------------------------------------------Doolhof-------------------------------------------------------------------------------- #

elif nav == "🎮 3D Doolhof":
    st.title("🎮 First-Person Doolhof")
    st.write("Klik in het scherm om te beginnen met lopen (WASD + Pijltjes).")
    
    maze_html = """
    <div id="game-container" style="width: 100%; height: 500px; cursor: pointer; border: 2px solid #fff;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x202020);
        const camera = new THREE.PerspectiveCamera(75, 800/500, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(800, 500);
        document.getElementById('game-container').appendChild(renderer.domElement);

        camera.position.set(0, 1.6, 5);
        
        const controls = new THREE.PointerLockControls(camera, document.body);
        document.getElementById('game-container').addEventListener('click', () => controls.lock());

        const keys = {w: false, a: false, s: false, d: false, ArrowUp: false, ArrowDown: false, ArrowLeft: false, ArrowRight: false};
        
        document.addEventListener('keydown', (e) => { if(keys.hasOwnProperty(e.key)) keys[e.key] = true; });
        document.addEventListener('keyup', (e) => { if(keys.hasOwnProperty(e.key)) keys[e.key] = false; });

        function animate() {
            requestAnimationFrame(animate);
            const speed = 0.15;
            if (keys.w || keys.ArrowUp) controls.moveForward(speed);
            if (keys.s || keys.ArrowDown) controls.moveForward(-speed);
            if (keys.a || keys.ArrowLeft) controls.moveRight(-speed);
            if (keys.d || keys.ArrowRight) controls.moveRight(speed);
            renderer.render(scene, camera);
        }
        animate();
    </script>
    """
    components.html(maze_html, height=520)
