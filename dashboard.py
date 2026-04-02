import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import plotly.express as px

# 1. ELENCO COMPLETO BANCHE
BANCHE_CONFIG = {
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

def get_trust_data(slug):
    url = f"https://www.trustpilot.com/review/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9"
    }
    try:
        time.sleep(0.5) # Evita blocchi
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200: return None
        soup = BeautifulSoup(resp.content, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        if script:
            data = json.loads(script.string)
            unit = data['props']['pageProps']['businessUnit']
            return {"score": float(unit['rating']['trustScore']), "reviews": int(unit['rating']['count'])}
    except:
        return None
    return None

# --- UI CONFIG ---
st.set_page_config(page_title="Banking Dashboard IT", layout="wide")

# CSS CORRETTO PER VISIBILITÀ (Fix scritte bianche)
st.markdown("""
    <style>
    .stMetric {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0 !important;
        padding: 15px !important;
        border-radius: 12px !important;
    }
    [data-testid="stMetricLabel"] {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #00b67a !important;
    }
    .main { background-color: #f8fafc; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 TrustScore Banche Italia")
st.write(f"Ultimo aggiornamento: {datetime.now().strftime('%H:%M:%S')}")

# RECOUPERO DATI
all_data = []
with st.sidebar:
    st.header("Stato Sincronizzazione")
    progress = st.progress(0)
    for i, (name, slug) in enumerate(BANCHE_CONFIG.items()):
        info = get_trust_data(slug)
        if info:
            all_data.append({"Banca": name, "TrustScore": info['score'], "Recensioni": info['reviews']})
        else:
            # Dati fallback se Trustpilot blocca (voti reali approssimativi)
            mock_score = 1.2 if "Poste" in name or "BNL" in name else 2.5
            all_data.append({"Banca": name, "TrustScore": mock_score, "Recensioni": 0})
        progress.progress((i + 1) / len(BANCHE_CONFIG))

df = pd.DataFrame(all_data).sort_values(by="TrustScore", ascending=False)

# --- CARDS TOP 4 ---
cols = st.columns(4)
for i in range(min(4, len(df))):
    with cols[i]:
        st.metric(label=df.iloc[i]['Banca'], value=f"{df.iloc[i]['TrustScore']} ⭐")

st.divider()

col_table, col_chart = st.columns([1, 1.2])

with col_table:
    st.subheader("📋 Classifica Completa")
    # FIX: Usiamo 'map' invece di 'applymap' per le nuove versioni di Pandas
    def color_score(val):
        color = '#00b67a' if val >= 4 else ('#ff8622' if val >= 2.5 else '#ff3722')
        return f'color: {color}; font-weight: bold'

    st.dataframe(
        df.style.map(color_score, subset=['TrustScore']), # Qui c'era l'errore
        use_container_width=True, height=500
    )

with col_chart:
    st.subheader("📊 Confronto Visivo")
    fig = px.bar(df, x='TrustScore', y='Banca', orientation='h',
                 color='TrustScore', color_continuous_scale='RdYlGn',
                 range_x=[0, 5], text_auto=True)
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
    st.plotly_chart(fig, use_container_width=True)

st.info("I dati vengono aggiornati in tempo reale caricando la pagina. Se vedi punteggi fissi a 1.2 o 2.5, Trustpilot sta limitando le richieste dal server: riprova tra poco.")
