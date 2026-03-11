import streamlit as st
import streamlit.components.v1 as components

# --- META TAG VOOR VERIFICATIE (Plaats dit direct onder je imports) ---
st.markdown("""
    <meta name="google-adsense-account" content="ca-pub-8729817167190879">
""", unsafe_allow_html=True)

# --- ADSENSE CONFIGURATIE (De rest van je script) ---
ADS_CLIENT = "ca-pub-8729817167190879"

def inject_adsense_head():
    script = f"""
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS_CLIENT}" 
    crossorigin="anonymous"></script>
    """
    st.markdown(script, unsafe_allow_html=True)

inject_adsense_head()
