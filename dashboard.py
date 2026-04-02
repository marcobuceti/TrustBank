import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Trust Radar Live", layout="wide")

# --- CSS DARK NEON (STILE REPLIT PRO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    .stApp { background-color: #0b0e14; color: white; font-family: 'Inter', sans-serif; }
    
    .header-title {
        font-size: 48px; font-weight: 800;
        background: linear-gradient(90deg, #ff4bb4, #00d2ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    .bank-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 20px;
        padding: 24px; margin-bottom: 20px; position: relative; height: 260px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .bank-card:hover { border-color: #00d2ff; transform: translateY(-5px); transition: 0.3s; }

    .score-circle {
        position: absolute; top: 24px; right: 24px;
        width: 60px; height: 60px; border: 4px solid #00d2ff; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: 800; color: white; background: #0b0e14;
    }

    .name { font-size: 24px; font-weight: 700; color: white; margin-bottom: 2px; }
    .url { font-size: 13px; color: #8b949e; margin-bottom: 15px; }

    .badge { padding: 5px 12px; border-radius: 8px; font-size: 11px; font-weight: 700; display: inline-block; text-transform: uppercase; }
    .excellent { background: rgba(0, 182, 122, 0.15); color: #00b67a; border: 1px solid #00b67a; }
    .poor { background: rgba(255, 55, 34, 0.15); color: #ff3722; border: 1px solid #ff3722; }

    .bar-bg { background: #30363d; height: 8px; border-radius: 10px; margin: 20px 0; }
    .bar-fill { height: 8px; border-radius: 10px; background: linear-gradient(90deg, #00d2ff, #00ff88); }

    .rev-info { font-size: 14px; color: #8b949e; margin-top: 15px; }
    .trend-icon { margin-left: 10px; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- INTESTAZIONE ---
st.markdown('<h1 class="header-title">TRUST RADAR</h1>', unsafe_allow_html=True)

# --- CARICAMENTO DATI DAL FILE CSV ---
try:
    df = pd.read_csv('dati_banche.csv')
    df = df.sort_values(by="TrustScore", ascending=False)
    
    # Mostra l'ultima modifica del file
    last_mod = os.path.getmtime('dati_banche.csv')
    st.write(f"Ultimo aggiornamento dati: **{datetime.fromtimestamp(last_mod).strftime('%d %B %Y')}**")
except:
    st.error("Errore: Crea il file 'dati_banche.csv' su GitHub per visualizzare i dati.")
    st.stop()

# --- GRIGLIA CARD ---
for i in range(0, len(df), 3):
    cols = st.columns(3)
    chunk = df.iloc[i:i+3]
    for j, (_, bank) in enumerate(chunk.iterrows()):
        with cols[j]:
            perc = (bank['TrustScore'] / 5) * 100
            b_class = "excellent" if bank['TrustScore'] >= 3.5 else "poor"
            b_text = "Eccellente" if bank['TrustScore'] >= 4 else ("Buono" if bank['TrustScore'] >= 3 else "Scarso")
            t_icon = "↑" if bank['Trend'] == "su" else ("↓" if bank['Trend'] == "giu" else "→")
            
            # HTML UNITO SENZA SPAZI PER EVITARE BUG TESTO
            card_html = f"""
            <div class="bank-card">
                <div class="score-circle">{bank['TrustScore']}</div>
                <div class="name">{bank['Banca']}</div>
                <div class="url">{bank['URL']}</div>
                <div style="margin-top:10px;">
                    <span class="badge {b_class}">{b_text}</span>
                    <span class="trend-icon" style="color:{('#00ff88' if t_icon=='↑' else '#ff3722' if t_icon=='↓' else '#8b949e')}">{t_icon}</span>
                </div>
                <div class="bar-bg"><div class="bar-fill" style="width:{perc}%"></div></div>
                <div class="rev-info">Recensioni: <b>{bank['Recensioni']}</b></div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")
st.caption("Dashboard alimentata dal database privato. Aggiorna il file CSV su GitHub per riflettere i cambiamenti.")
