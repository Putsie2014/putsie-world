import streamlit as st
import streamlit.components.v1 as components

# --- ADSENSE CONFIGURATIE ---
ADS_CLIENT = "ca-pub-8729817167190879"

def inject_adsense_head():
    """Injecteert het AdSense script in de header."""
    script = f"""
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS_CLIENT}" 
    crossorigin="anonymous"></script>
    """
    st.markdown(script, unsafe_allow_html=True)

def show_ad_block(slot_id):
    """Toont een advertentieblok op een specifieke plek."""
    ad_html = f"""
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="{ADS_CLIENT}"
         data-ad-slot="{slot_id}"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({{}});
    </script>
    """
    components.html(ad_html, height=280)

# --- APP START ---
st.set_page_config(page_title="Putsie EDUCATION", layout="wide")
inject_adsense_head()

# --- JOUW BESTAANDE LOGICA HIERONDER ---
# Gebruik show_ad_block("JOUW_AD_SLOT_ID") op de plek waar je advertenties wilt.
# Let op: je hebt in je AdSense dashboard een 'Ad Slot ID' nodig voor het blok.

st.title("Welkom bij Putsie Education")
st.write("Je app is nu technisch voorbereid voor AdSense.")
