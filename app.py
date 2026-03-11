import streamlit as st
import random
from openai import OpenAI
import streamlit.components.v1 as components

# --- CONFIGURATIE ---
SITE_TITLE = "Putsie EDUCATION 🎓 v3.0 FULL"
MODEL_NAAM = "llama-3.1-8b-instant"

st.set_page_config(page_title=SITE_TITLE, layout="wide")

# UI Styling: Donkere achtergrond en witte tekst
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0f172a;
    background-image: radial-gradient(circle at 50% 0%, #1e293b 0%, #0f172a 70%);
    color: white;
}
.stButton>button { width: 100%; border-radius: 10px; }
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
if 'saldi' not in st.session_state: st.session_state.saldi = {"elliot": 1000}
if 'ai_points' not in st.session_state: st.session_state.ai_points = 5 
if 'class_code' not in st.session_state: st.session_state.class_code = "1234"
if 'class_name' not in st.session_state: st.session_state.class_name = "Putsie's Klas"
if 'frans_woord_nu' not in st.session_state: st.session_state.frans_woord_nu = "hallo"

frans_dict = {"hallo": "bonjour", "bedankt": "merci", "school": "école", "boek": "livre", "brood": "pain"}

# --- AI FUNCTIE ---
def vraag_groq(vraag):
    if st.session_state.active_task:
        return "⚠️ **AI GEBLOKKEERD:** Je bent momenteel bezig aan een taak. Maak je werk eerst af!"
    if st.session_state.ai_points <= 0:
        return "❌ **Geen AI Punten meer!** Bekijk een advertentie onderaan deze pagina om 3 punten te verdienen."
    
    st.session_state.ai_points -= 1
    try:
        response = client.chat.completions.create(
            model=MODEL_NAAM,
            messages=[{"role": "system", "content": "Je bent een behulpzame leraar."}, {"role": "user", "content": vraag}]
        )
        return response.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- LOGIN & REGISTRATIE ---
if not st.session_state.ingelogd:
    st.title(f"🔐 Welkom bij {SITE_TITLE}")
    t1, t2 = st.tabs(["Inloggen", "Registreren"])
    
    with t1:
        u = st.text_input("Gebruikersnaam", key="l_u").lower().strip()
        p = st.text_input("Wachtwoord", type="password", key="l_p")
        if st.button("Inloggen", key="l_btn"):
            if u in st.session_state.users:
                u_data = st.session_state.users[u]
                if (isinstance(u_data, dict) and u_data["pw"] == p) or (u_data == p):
                    st.session_state.ingelogd = True
                    st.session_state.username = u
                    st.session_state.role = u_data.get("role", "student") if isinstance(u_data, dict) else "student"
                    st.rerun()
                else: st.error("Wachtwoord onjuist.")
            else: st.error("Gebruiker niet gevonden.")

    with t2:
        nu = st.text_input("Kies Naam", key="r_u").lower().strip()
        np = st.text_input("Kies Wachtwoord", type="password", key="r_p")
        cc = st.text_input("Klascode", key="r_c")
        if st.button("Maak Account", key="r_btn"):
            if cc == st.session_state.class_code:
                if nu and np and nu not in st.session_state.users:
                    st.session_state.users[nu] = {"pw": np, "role": "student"}
                    st.session_state.saldi[nu] = 0
                    st.success("Account klaar! Log nu in.")
                else: st.error("Naam bezet of leeg.")
            else: st.error("Klascode onjuist.")
    st.stop()

# --- SIDEBAR NAVIGATIE ---
st.sidebar.title(f"👋 {st.session_state.username.capitalize()}")
st.sidebar.markdown(f"💎 **AI Punten:** {st.session_state.ai_points}")
st.sidebar.markdown(f"💰 **Saldo:** {st.session_state.saldi.get(st.session_state.username, 0)}")

menu = ["🏫 De Klas", "🤖 AI Hulp", "🇫🇷 Frans Lab", "🎮 3D Doolhof"]
if st.session_state.role in ["teacher", "admin"]: menu.append("📚 Leraar Paneel")
if st.session_state.username == "elliot": menu.append("👑 Super Admin")

nav = st.sidebar.radio("Ga naar:", menu)

# --- PAGINA: DE KLAS ---
if nav == "🏫 De Klas":
    st.title(f"🏫 {st.session_state.class_name}")
    st.info(f"Klascode voor nieuwe leerlingen: **{st.session_state.class_code}**")
    
    st.subheader("Openstaande Taken")
    if not st.session_state.tasks: st.write("Lekker! Geen taken.")
    for i, t in enumerate(st.session_state.tasks):
        if st.button(f"Start: {t['name']}", key=f"t_{i}"):
            st.session_state.active_task = t
            st.rerun()
    
    if st.session_state.active_task:
        st.error(f"📍 BEZIG: {st.session_state.active_task['name']}")
        st.write(st.session_state.active_task['content'])
        if st.button("Inleveren"):
            st.session_state.active_task = None
            st.success("Taak voltooid!")
            st.rerun()

# --- PAGINA: AI HULP ---
elif nav == "🤖 AI Hulp":
    st.title("🤖 AI Studiehulp")
    st.write(f"Punten: {st.session_state.ai_points}")
    vraag = st.text_area("Stel je vraag over je huiswerk:")
    if st.button("Vraag AI"):
        with st.spinner("AI denkt na..."):
            st.write(vraag_groq(vraag))
            st.rerun()
            
    st.divider()
    st.subheader("Punten bijvullen")
    st.write("Kijk een advertentie van 1 minuut voor 3 AI punten.")
    if st.button("▶️ Bekijk Advertentie"):
        st.session_state.ai_points += 3
        st.success("3 Punten toegevoegd!")
        st.rerun()

# --- PAGINA: FRANS LAB ---
elif nav == "🇫🇷 Frans Lab":
    st.title("🇫🇷 Frans Lab")
    if st.button("Nieuw Woord"):
        st.session_state.frans_woord_nu = random.choice(list(frans_dict.keys()))
        st.rerun()
    st.subheader(f"Vertaal naar Frans: **{st.session_state.frans_woord_nu}**")
    ans = st.text_input("Jouw antwoord:").lower().strip()
    if st.button("Controleer"):
        if ans == frans_dict[st.session_state.frans_woord_nu]:
            st.success("Correct! +10 munten.")
            st.session_state.saldi[st.session_state.username] += 10
        else: st.error(f"Fout! Het was: {frans_dict[st.session_state.frans_woord_nu]}")

# --- PAGINA: 3D DOOLHOF ---
elif nav == "🎮 3D Doolhof":
    st.title("🎮 First-Person Maze")
    st.write("Gebruik WASD of Pijltjestoetsen. Klik in het veld om de muis te locken.")
    maze_code = """
    <div id="game" style="width:100%; height:500px; background:#000;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
    <script>
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, 800/500, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(800, 500);
        document.getElementById('game').appendChild(renderer.domElement);
        camera.position.set(0, 1.6, 5);
        const controls = new THREE.PointerLockControls(camera, document.body);
        document.getElementById('game').addEventListener('click', () => controls.lock());
        const keys = {w:false,a:false,s:false,d:false,ArrowUp:false,ArrowDown:false,ArrowLeft:false,ArrowRight:false};
        document.addEventListener('keydown', (e) => { if(keys.hasOwnProperty(e.key)) keys[e.key] = true; });
        document.addEventListener('keyup', (e) => { if(keys.hasOwnProperty(e.key)) keys[e.key] = false; });
        function animate() {
            requestAnimationFrame(animate);
            if(keys.w || keys.ArrowUp) controls.moveForward(0.15);
            if(keys.s || keys.ArrowDown) controls.moveForward(-0.15);
            if(keys.a || keys.ArrowLeft) controls.moveRight(-0.15);
            if(keys.d || keys.ArrowRight) controls.moveRight(0.15);
            renderer.render(scene, camera);
        }
        animate();
    </script>
    """
    components.html(maze_code, height=520)

# --- PAGINA: LERAAR PANEEL ---
elif nav == "📚 Leraar Paneel":
    st.title("👨‍🏫 Leraar Paneel")
    t_n = st.text_input("Naam van de taak")
    t_c = st.text_area("Inhoud van de taak")
    if st.button("Taak Uitdelen"):
        st.session_state.tasks.append({"name": t_n, "content": t_c})
        st.success("Taak is verstuurd naar de klas!")

# --- PAGINA: SUPER ADMIN (ELLIOT) ---
elif nav == "👑 Super Admin":
    st.title("👑 Elliot's Control Room")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Instellingen")
        st.session_state.class_name = st.text_input("Klas Naam", st.session_state.class_name)
        st.session_state.class_code = st.text_input("Klas Code", st.session_state.class_code)
        
    with col2:
        st.subheader("Data")
        st.json(st.session_state.users)

    st.divider()
    st.subheader("Speler Beheer")
    for s in list(st.session_state.users.keys()):
        if s != "elliot":
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"👤 {s}")
            nieuw_saldo = c2.number_input(f"Saldo van {s}", value=st.session_state.saldi.get(s, 0), key=f"s_{s}")
            st.session_state.saldi[s] = nieuw_saldo
            if c3.button("BANNEN", key=f"b_{s}"):
                del st.session_state.users[s]
                st.rerun()

if st.sidebar.button("Uitloggen"):
    st.session_state.ingelogd = False
    st.rerun()
