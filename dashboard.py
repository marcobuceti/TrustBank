import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE BANCHE ---
BANCHE = {
    "BBVA Italia": "www.bbva.it", "Revolut": "www.revolut.com", "Fineco": "finecobank.com",
    "Isybank": "www.isybank.com", "Findomestic": "www.findomestic.it", "BPER Banca": "www.bper.it",
    "Mediolanum": "www.bancamediolanum.it", "Credem": "www.credem.it", "Credit Agricole": "www.credit-agricole.it",
    "ING Italia": "www.ing.it", "UniCredit": "www.unicredit.it", "Intesa Sanpaolo": "www.intesasanpaolo.com",
    "BNL Bnp Paribas": "www.bnl.it", "Poste Italiane": "www.poste.it", "Banco Posta": "www.poste.it"
}

# --- FUNZIONE SCRAPING REALE ---
def get_trust_data(slug):
    url = f"https://www.trustpilot.com/review/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.content, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        if script:
            data = json.loads(script.string)
            unit = data['props']['pageProps']['businessUnit']
            return {"score": float(unit['rating']['trustScore']), "revs": unit['rating']['count']}
    except:
        return {"score": 1.0, "revs": "N/D"} # Fallback in caso di blocco IP
    return {"score": 1.0, "revs": "N/D"}

# --- IMPOSTAZIONI PAGINA ---
st.set_page_config(page_title="Trust Radar", layout="wide")

# --- CSS DARK NEON ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    .stApp { background-color: #0b0e14; color: white; font-family: 'Inter', sans-serif; }
    
    .header-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .header-title {
        font-size: 42px; font-weight: 800;
        background: linear-gradient(90deg, #ff4bb4, #00d2ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }

    .card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        height: 260px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .card:hover { border-color: #00d2ff; transform: translateY(-3px); transition: 0.3s; }

    .score-circle {
        position: absolute; top: 24px; right: 24px;
        width: 60px; height: 60px;
        border: 4px solid #00d2ff; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: 800; color: white;
    }

    .name { font-size: 24px; font-weight: 700; margin-bottom: 4px; color: white; }
    .url { font-size: 14px; color: #8b949e; margin-bottom: 15px; }

    .badge {
        padding: 5px 12px; border-radius: 8px; font-size: 12px; font-weight: 700; margin-top: 10px;
    }
    .excellent { background: rgba(0, 182, 122, 0.2); color: #00b67a; }
    .poor { background: rgba(255, 55, 34, 0.2); color: #ff3722; }

    .bar-bg { background: #30363d; height: 10px; border-radius: 10px; margin: 20px 0; }
    .bar-fill { height: 10px; border-radius: 10px; background: linear-gradient(90deg, #00d2ff, #00ff88); }

    .rev-info { font-size: 14px; color: #8b949e; margin-top: 20px; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER E TASTO AGGIORNA ---
st.markdown('<h1 class="header-title">TRUST RADAR</h1>', unsafe_allow_html=True)
col_header, col_btn = st.columns([4, 1])

with col_header:
    st.write(f"Ultimo aggiornamento live: **{datetime.now().strftime('%H:%M:%S')}**")

with col_btn:
    # Tasto Aggiorna sempre visibile
    aggiorna = st.button("🔄 Aggiorna Dashboard")

# --- LOGICA DATI ---
if 'data_cache' not in st.session_state or aggiorna:
    with st.spinner('Scaricamento dati reali da Trustpilot...'):
        results = []
        for name, slug in BANCHE.items():
            d = get_trust_data(slug)
            results.append({"name": name, "url": slug, "score": d['score'], "revs": d['revs']})
        
        df = pd.DataFrame(results).sort_values(by="score", ascending=False)
        st.session_state.data_cache = df

df = st.session_state.data_cache

# --- GRIGLIA CARD (Render HTML) ---
# Dividiamo in 3 colonne
for i in range(0, len(df), 3):
    cols = st.columns(3)
    chunk = df.iloc[i:i+3]
    
    for j, (_, bank) in enumerate(chunk.iterrows()):
        with cols[j]:
            # Calcoli per la grafica
            perc = (bank['score'] / 5) * 100
            status_class = "excellent" if bank['score'] >= 3.5 else "poor"
            status_text = "ECCELLENTE" if bank['score'] >= 4 else ("MEDIO" if bank['score'] >= 2.5 else "SCARSO")
            
            # UNICO BLOCCO HTML PER EVITARE BUG TESTO
            card_html = f"""
            <div class="card">
                <div class="score-circle">{bank['score']}</div>
                <div class="name">{bank['name']}</div>
                <div class="url">{bank['url']}</div>
                <span class="badge {status_class}">{status_text}</span>
                <div class="bar-bg">
                    <div class="bar-fill" style="width: {perc}%;"></div>
                </div>
                <span class="rev-info">Recensioni: <b>{bank['revs']}</b></span>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

st.markdown("---")
st.caption("I dati vengono letti direttamente da Trustpilot ogni volta che clicchi 'Aggiorna'.")
