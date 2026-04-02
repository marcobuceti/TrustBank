import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Trust Radar Pro", layout="wide")

# --- CSS DARK NEON AVANZATO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    .stApp { background-color: #0b0e14; color: white; font-family: 'Inter', sans-serif; }
    
    .header-title {
        font-size: 52px; font-weight: 800;
        background: linear-gradient(90deg, #ff4bb4, #00d2ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 40px;
    }

    .bank-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 24px;
        padding: 24px; margin-bottom: 25px; position: relative; height: 280px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }
    .bank-card:hover { border-color: #00d2ff; transform: translateY(-8px); box-shadow: 0 0 20px rgba(0, 210, 255, 0.2); }

    /* Logo Banca */
    .logo-container {
        width: 50px; height: 50px; background: white; border-radius: 12px;
        padding: 5px; display: flex; align-items: center; justify-content: center;
        margin-bottom: 15px; overflow: hidden;
    }
    .logo-img { max-width: 100%; max-height: 100%; object-fit: contain; }

    /* Cerchio Punteggio */
    .score-circle {
        position: absolute; top: 24px; right: 24px;
        width: 65px; height: 65px; border: 4px solid #00d2ff; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; font-weight: 800; color: white; background: #0b0e14;
    }

    .name { font-size: 24px; font-weight: 700; color: white; margin-bottom: 2px; }
    .url { font-size: 13px; color: #8b949e; margin-bottom: 15px; }

    /* Stelline Trustpilot */
    .star { font-size: 20px; margin-right: 2px; }
    .star-filled { color: #00b67a; } /* Sarà dinamico nel codice */
    .star-empty { color: #30363d; }

    .tag-status {
        padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700;
        margin-left: 10px; text-transform: uppercase;
    }

    .rev-info { font-size: 14px; color: #8b949e; margin-top: 30px; display: block; }
    .footer-link { font-size: 12px; color: #00d2ff; text-decoration: none; margin-top: 10px; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE LOGICA STELLE ---
def get_stars_html(score):
    # Colore in base al punteggio (Stile Trustpilot)
    color = "#00b67a" if score >= 4 else ("#ff8622" if score >= 3 else "#ff3722")
    full_stars = round(score)
    stars_html = ""
    for i in range(5):
        if i < full_stars:
            stars_html += f'<span class="star" style="color:{color}">★</span>'
        else:
            stars_html += '<span class="star star-empty">★</span>'
    return stars_html

# --- TITOLO ---
st.markdown('<h1 class="header-title">TRUST RADAR</h1>', unsafe_allow_html=True)

# --- CARICAMENTO DATI ---
try:
    df = pd.read_csv('dati_banche.csv')
    df = df.sort_values(by="TrustScore", ascending=False)
except:
    st.error("Assicurati di avere il file dati_banche.csv su GitHub!")
    st.stop()

# --- GRIGLIA CARD ---
for i in range(0, len(df), 3):
    cols = st.columns(3)
    chunk = df.iloc[i:i+3]
    for j, (_, bank) in enumerate(chunk.iterrows()):
        with cols[j]:
            # Generazione Stelle
            stars = get_stars_html(bank['TrustScore'])
            
            # Colore stato
            s_color = "#00b67a" if bank['TrustScore'] >= 4 else ("#ff8622" if bank['TrustScore'] >= 3 else "#ff3722")
            s_text = "ECCELLENTE" if bank['TrustScore'] >= 4 else ("BUONO" if bank['TrustScore'] >= 3 else "SCARSO")
            
            # Logo automatico via Clearbit (usando il dominio in minuscolo)
            domain = bank['URL'].lower().replace("www.", "")
            logo_url = f"https://logo.clearbit.com/{domain}"
            
            # HTML UNICO (Per evitare bug del testo di programmazione)
            card_html = f"""
            <div class="bank-card">
                <div class="score-circle">{bank['TrustScore']}</div>
                <div class="logo-container">
                    <img src="{logo_url}" class="logo-img" onerror="this.src='https://ui-avatars.com/api/?name={bank['Banca']}&background=random'">
                </div>
                <div class="name">{bank['Banca']}</div>
                <div class="url">{bank['URL']}</div>
                
                <div style="margin: 15px 0;">
                    {stars}
                    <span style="color:{s_color}; font-size:12px; font-weight:700; margin-left:10px;">{s_text}</span>
                </div>
                
                <span class="rev-info">Recensioni: <b>{bank['Recensioni']}</b></span>
                <a href="https://it.trustpilot.com/review/{bank['URL']}" target="_blank" class="footer-link">Vedi su Trustpilot ↗</a>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")
st.caption(f"Ultimo aggiornamento manuale: {datetime.now().strftime('%d %B %Y')}")
