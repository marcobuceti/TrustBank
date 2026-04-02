import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
from datetime import datetime

# Elenco banche e slug
BANCHE = {
    "BBVA Italia": "www.bbva.it",
    "Revolut": "www.revolut.com",
    "Fineco": "finecobank.com",
    "Isybank": "www.isybank.com",
    "Findomestic": "www.findomestic.it",
    "BPER Banca": "www.bper.it",
    "Mediolanum": "www.bancamediolanum.it",
    "Credem": "www.credem.it",
    "Credit Agricole": "www.credit-agricole.it",
    "ING Italia": "www.ing.it",
    "UniCredit": "www.unicredit.it",
    "Intesa Sanpaolo": "www.intesasanpaolo.com",
    "BNL Bnp Paribas": "www.bnl.it",
    "Poste Italiane": "www.poste.it",
    "Banco Posta": "www.poste.it"
}

# Funzione per prendere i dati REALI
def get_real_time_data(slug):
    url = f"https://www.trustpilot.com/review/{slug}"
    # Header molto sofisticato per non farsi bloccare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            if script:
                data = json.loads(script.string)
                bu = data['props']['pageProps']['businessUnit']
                return {
                    "score": float(bu['rating']['trustScore']),
                    "revs": bu['rating']['count']
                }
    except:
        pass
    return None

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Trust Radar Live", layout="wide")

# --- CSS DARK NEON (STILE REPLIT) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    .stApp { background-color: #0b0e14; color: white; font-family: 'Inter', sans-serif; }
    
    .header-title {
        font-size: 45px; font-weight: 800;
        background: linear-gradient(90deg, #ff4bb4, #00d2ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    /* Stile Card */
    .bank-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        position: relative;
        height: 250px;
    }

    .bank-name { font-size: 22px; font-weight: 700; color: white; margin-bottom: 2px; }
    .bank-url { font-size: 13px; color: #8b949e; margin-bottom: 15px; }

    .score-badge {
        position: absolute; top: 20px; right: 20px;
        width: 55px; height: 55px;
        border: 3px solid #00d2ff; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: 800; color: white;
    }

    .progress-bar-bg {
        background: #30363d; height: 8px; border-radius: 10px; margin: 15px 0;
    }
    .progress-bar-fill {
        height: 8px; border-radius: 10px;
        background: linear-gradient(90deg, #00d2ff, #00ff88);
    }

    .tag-excellent { background: rgba(0, 182, 122, 0.2); color: #00b67a; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
    .tag-poor { background: rgba(255, 55, 34, 0.2); color: #ff3722; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
    
    .rev-text { font-size: 14px; color: #8b949e; margin-top: 15px; display: block; }
    
    hr { border: 0.5px solid #30363d; margin: 30px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="header-title">TRUST RADAR</h1>', unsafe_allow_html=True)
st.write(f"Ultimo aggiornamento live: **{datetime.now().strftime('%H:%M:%S')}**")

# --- CARICAMENTO DATI ---
if 'data' not in st.session_state or st.button('🔄 Aggiorna Dati Live'):
    with st.spinner('Scaricamento dati reali da Trustpilot...'):
        results = []
        for name, slug in BANCHE.items():
            data = get_real_time_data(slug)
            if data:
                results.append({"name": name, "url": slug, "score": data['score'], "revs": data['revs']})
            else:
                # Se fallisce, usiamo un placeholder per non rompere la grafica
                results.append({"name": name, "url": slug, "score": 1.0, "revs": "N/D"})
        
        df = pd.DataFrame(results).sort_values(by="score", ascending=False)
        st.session_state.data = df

df = st.session_state.data

# --- GRIGLIA CARD ---
cols_per_row = 3
rows = [df.iloc[i:i + cols_per_row] for i in range(0, len(df), cols_per_row)]

for row in rows:
    columns = st.columns(cols_per_row)
    for i, (_, bank) in enumerate(row.iterrows()):
        with columns[i]:
            # Calcolo percentuale barra
            perc = (bank['score'] / 5) * 100
            tag_class = "tag-excellent" if bank['score'] >= 3.5 else "tag-poor"
            tag_text = "ECCELLENTE" if bank['score'] >= 4 else ("BUONO" if bank['score'] >= 3 else "SCARSO")
            
            # HTML Renderizzato correttamente
            st.markdown(f"""
                <div class="bank-card">
                    <div class="score-badge">{bank['score']}</div>
                    <div class="bank-name">{bank['name']}</div>
                    <div class="bank-url">{bank['url']}</div>
                    
                    <span class="{tag_class}">{tag_text}</span>
                    
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: {perc}%"></div>
                    </div>
                    
                    <span class="rev-text">Recensioni: <b>{bank['revs']}</b></span>
                    <div style="margin-top: 10px; font-size: 12px; color: #8b949e;">Trustpilot ↗</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.caption("I dati sono estratti in tempo reale analizzando il codice sorgente di Trustpilot.")
