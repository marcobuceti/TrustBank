import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Trust Radar Pro", layout="wide")

# --- CSS DARK NEON (BLINDATO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    .stApp { background-color: #0b0e14; color: white; font-family: 'Inter', sans-serif; }
    .header-title {
        font-size: 50px; font-weight: 800; text-align: center; margin-bottom: 30px;
        background: linear-gradient(90deg, #ff4bb4, #00d2ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    /* Rimuove padding inutile dalle colonne di Streamlit */
    [data-testid="column"] { padding: 0 10px !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONE GENERAZIONE CARD (SENZA BUG DI TESTO) ---
def draw_card(name, url, score, revs, trend):
    # Colore in base al punteggio
    color = "#00b67a" if score >= 4 else ("#ff8622" if score >= 3 else "#ff3722")
    status = "ECCELLENTE" if score >= 4 else ("BUONO" if score >= 3 else "SCARSO")
    
    # Stelline Trustpilot
    stars = ""
    for i in range(5):
        stars += f"<span style='color:{color if i < round(score) else '#30363d'}; font-size:20px;'>★</span>"
    
    # Trend Icon
    t_icon = "↑" if trend == "su" else ("↓" if trend == "giu" else "→")
    t_color = "#00ff88" if t_icon == "↑" else ("#ff3722" if t_icon == "↓" else "#8b949e")

    # Logo via Google Favicon (Più stabile)
    domain = url.lower().replace("www.", "")
    logo_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"

    # HTML COMPATTATO (Evita la visualizzazione del codice di programmazione)
    html = f"""<div style="background:#161b22; border:1px solid #30363d; border-radius:20px; padding:24px; position:relative; height:270px; margin-bottom:20px; box-shadow:0 10px 20px rgba(0,0,0,0.4);">
<div style="position:absolute; top:24px; right:24px; width:60px; height:60px; border:4px solid #00d2ff; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:800; background:#0b0e14;">{score}</div>
<div style="width:50px; height:50px; background:white; border-radius:10px; padding:5px; margin-bottom:15px; display:flex; align-items:center; justify-content:center; overflow:hidden;">
<img src="{logo_url}" style="max-width:100%; max-height:100%;" onerror="this.src='https://ui-avatars.com/api/?name={name}&background=random'"></div>
<div style="font-size:22px; font-weight:700; color:white; margin-bottom:2px;">{name}</div>
<div style="font-size:13px; color:#8b949e; margin-bottom:15px;">{url}</div>
<div style="margin:10px 0;">{stars} <span style="color:{color}; font-size:11px; font-weight:800; margin-left:8px; border:1px solid {color}; padding:2px 6px; border-radius:4px;">{status}</span></div>
<div style="margin-top:25px; display:flex; justify-content:space-between; align-items:center;">
<span style="font-size:14px; color:#8b949e;">Recensioni: <b>{revs}</b> <span style="color:{t_color}; margin-left:5px;">{t_icon}</span></span>
<a href="https://it.trustpilot.com/review/{url}" target="_blank" style="color:#00d2ff; text-decoration:none; font-size:12px;">Trustpilot ↗</a>
</div></div>"""
    return st.markdown(html, unsafe_allow_html=True)

# --- TITOLO ---
st.markdown('<h1 class="header-title">TRUST RADAR</h1>', unsafe_allow_html=True)

# --- CARICAMENTO DATI ---
try:
    # Carichiamo il CSV dal tuo repository
    df = pd.read_csv('dati_banche.csv')
    df = df.sort_values(by="TrustScore", ascending=False)
    st.write(f"📊 Dati aggiornati al: **{datetime.now().strftime('%d %B %Y')}**")
except:
    st.error("Errore: Il file 'dati_banche.csv' non è stato trovato o è formattato male.")
    st.stop()

# --- GRIGLIA CARD ---
for i in range(0, len(df), 3):
    cols = st.columns(3)
    chunk = df.iloc[i:i+3]
    for j, (_, row) in enumerate(chunk.iterrows()):
        with cols[j]:
            draw_card(row['Banca'], row['URL'], row['TrustScore'], row['Recensioni'], row['Trend'])

st.markdown("<br><hr><center style='color:#8b949e; font-size:12px;'>Dashboard Privata • Dati estratti da Trustpilot</center>", unsafe_allow_html=True)
