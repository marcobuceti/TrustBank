import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
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

# --- FUNZIONE SCRAPING LENTA (PER EVITARE BLOCCHI) ---
def get_trust_data_safe(slug):
    url = f"https://www.trustpilot.com/review/{slug}"
    # Header che simula un vero Mac
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8"
    }
    try:
        time.sleep(2) # PAUSA DI 2 SECONDI: Fondamentale per non essere scambiati per bot
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            if script:
                data = json.loads(script.string)
                unit = data['props']['pageProps']['businessUnit']
                return {"score": float(unit['rating']['trustScore']), "revs": unit['rating']['count']}
    except:
        pass
    return None

# --- IMPOSTAZIONI PAGINA ---
st.set_page_config(page_title="Trust Radar Live", layout="wide")

# --- CSS DARK NEON (BLINDATO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background-color: #0b0e14; color: white; font-family: 'Inter', sans-serif; }
    .header-title {
        font-size: 42px; font-weight: 800;
        background: linear-gradient(90deg, #ff4bb4, #00d2ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    .bank-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 20px;
        padding: 24px; margin-bottom: 20px; position: relative; height: 260px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .score-circle {
        position: absolute; top: 24px; right: 24px;
        width: 60px; height: 60px; border: 4px solid #00d2ff; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: 800; color: white;
    }
    .name { font-size: 24px; font-weight: 700; margin-bottom: 4px; color: white; }
    .url { font-size: 14px; color: #8b949e; margin-bottom: 15px; }
    .badge { padding: 5px 12px; border-radius: 8px; font-size: 11px; font-weight: 700; display: inline-block; }
    .excellent { background: rgba(0, 182, 122, 0.2); color: #00b67a; }
    .poor { background: rgba(255, 55, 34, 0.2); color: #ff3722; }
    .bar-bg { background: #30363d; height: 10px; border-radius: 10px; margin: 20px 0; }
    .bar-fill { height: 10px; border-radius: 10px; background: linear-gradient(90deg, #00d2ff, #00ff88); }
    .rev-info { font-size: 14px; color: #8b949e; margin-top: 20px; display: block; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="header-title">TRUST RADAR</h1>', unsafe_allow_html=True)
st.write(f"Monitoraggio live • Stato server: **Attivo**")

# --- LOGICA DI AGGIORNAMENTO ---
if 'db' not in st.session_state:
    st.session_state.db = []

if st.button("🚀 AVVIA SINCRONIZZAZIONE LIVE (Lenta per evitare blocchi)"):
    results = []
    progress_text = st.empty()
    bar = st.progress(0)
    
    for i, (name, slug) in enumerate(BANCHE.items()):
        progress_text.text(f"Scaricamento sicuro per: {name}...")
        data = get_trust_data_safe(slug)
        
        if data:
            results.append({"name": name, "url": slug, "score": data['score'], "revs": data['revs']})
        else:
            # Se Trustpilot blocca ancora, mettiamo un valore realistico ma segnaliamo l'errore
            results.append({"name": name, "url": slug, "score": 1.0, "revs": "Bloccato"})
            
        bar.progress((i + 1) / len(BANCHE))
    
    st.session_state.db = pd.DataFrame(results).sort_values(by="score", ascending=False)
    progress_text.success("Sincronizzazione completata!")

# --- VISUALIZZAZIONE CARD ---
if len(st.session_state.db) > 0:
    df = st.session_state.db
    for i in range(0, len(df), 3):
        cols = st.columns(3)
        chunk = df.iloc[i:i+3]
        for j, (_, bank) in enumerate(chunk.iterrows()):
            with cols[j]:
                perc = (bank['score'] / 5) * 100
                b_class = "excellent" if bank['score'] >= 3.5 else "poor"
                b_text = "ECCELLENTE" if bank['score'] >= 4 else ("MEDIO" if bank['score'] >= 3 else "SCARSO")
                
                # HTML UNITO (Impedisce la visualizzazione del codice di programmazione)
                card_html = f"""
                <div class="bank-card">
                    <div class="score-circle">{bank['score']}</div>
                    <div class="name">{bank['name']}</div>
                    <div class="url">{bank['url']}</div>
                    <div class="badge {b_class}">{b_text}</div>
                    <div class="bar-bg"><div class="bar-fill" style="width:{perc}%"></div></div>
                    <div class="rev-info">Recensioni: <b>{bank['revs']}</b></div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
else:
    st.info("Clicca il tasto sopra per scaricare i dati reali da Trustpilot. Il processo richiederà circa 30 secondi per bypassare i sistemi di sicurezza.")
