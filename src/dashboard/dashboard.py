import streamlit as st
import pandas as pd
import time
import altair as alt
from influxdb_client import InfluxDBClient

# --- 1. CONFIGURATION GLOBALE ---
st.set_page_config(
    layout="wide", 
    page_title="EcoStream AI | Monitor", 
    page_icon="🌤️",
    initial_sidebar_state="collapsed"
)

# --- 2. STYLE CSS AVANCÉ ---
st.markdown("""
<style>
/* FOND GLOBAL */
.stApp { background-color: #F8F9FA; }

/* KPI CARDS */
div[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E6E6EA;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

/* CONTAINERS */
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: transparent !important; }
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: #FFFFFF !important;
    border-radius: 14px;
    border: 1px solid #E6E6EA;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* GRAPHIQUES & TABLEAUX */
div[data-testid="stVegaLiteChart"], div[data-testid="stVegaLiteChart"] > div { background-color: #FFFFFF !important; }
div[data-testid="stDataFrame"], div[data-testid="stDataFrame"] > div, div[data-testid="stDataFrame"] table {
    background-color: #FFFFFF !important;
    border-radius: 10px;
}
thead, tbody, tr, td, th { background-color: #FFFFFF !important; }

/* TITRES */
h3 { font-size: 18px; font-weight: 600; color: #1E293B; margin-bottom: 16px; }

/* ESPACEMENT */
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)


# --- 3. CONNEXION BDD ---
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "adminpassword"
INFLUX_ORG = "ecostream"
INFLUX_BUCKET = "weather_data"

def load_data():
    """Charge les dernières données"""
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        query_api = client.query_api()
        
        query = f"""
        from(bucket: "{INFLUX_BUCKET}")
          |> range(start: -24h)
          |> filter(fn: (r) => r["_measurement"] == "weather_metrics")
          |> last()
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        """
        df = query_api.query_data_frame(query)
        
        if isinstance(df, list) or df.empty: return pd.DataFrame()
        if 'pred_max_tomorrow' not in df.columns: df['pred_max_tomorrow'] = 0.0
        
        cols = ['actual_temp', 'pred_max_tomorrow', 'humidity', 'wind']
        for c in cols:
            if c in df.columns: df[c] = df[c].astype(float).round(1)

        return df if 'city' in df.columns else pd.DataFrame()
    except: return pd.DataFrame()

# --- 4. INTERFACE ---
df = load_data()

# En-tête
st.markdown("###")
st.markdown("## 🌤️ EcoStream AI | Tableau de Bord")
st.markdown("---")

if df.empty:
    st.warning("📡 En attente de connexion satellite...")
    time.sleep(3)
    st.rerun()

# --- A. LIGNE DES KPIS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Stations Surveillées", f"{len(df)}")
c2.metric("Moyenne Globale", f"{df['actual_temp'].mean():.1f}°C")
c3.metric("Pic Moyen Demain", f"{df['pred_max_tomorrow'].mean():.1f}°C")
hottest = df.loc[df['actual_temp'].idxmax()]
c4.metric("Point Chaud", f"{hottest['actual_temp']}°C", delta=f"{hottest['city']}")

st.markdown("###")

# --- B. ZONE PRINCIPALE ---
c_control, c_chart = st.columns([1, 3])

with c_control:
    with st.container(border=True):
        cities = sorted(df['city'].unique())
        ix = cities.index("Tanger") if "Tanger" in cities else 0
        choix = st.selectbox("Ville :", cities, index=ix)
        
        row = df[df['city'] == choix].iloc[0]
        
        st.caption(f"🕒 Donnée reçue à : {row['_time'].strftime('%H:%M:%S')}")
        
        st.metric("Actuel", f"{row['actual_temp']}°C")
        
        # On récupère la prédiction qui correspond à l'heure actuelle
        current_h = row['_time'].strftime('%H') # ex: "19"
        pred_col = f"pred_{current_h}h"         # ex: "pred_19h"
        val_pred = float(row[pred_col]) if pred_col in row else 0.0
        
        # On affiche la valeur prédite
        delta_diff = val_pred - row['actual_temp']
        st.metric("Prédiction demain", f"{val_pred:.1f}°C", delta=f"{delta_diff:+.1f}°C")

with c_chart:
    with st.container(border=True):
        st.markdown(f"### 📈 Tendance Prédite pour Demain : {choix}")
        
        pred_data = []
        for h in range(24):
            col = f"pred_{h:02d}h"
            if col in row:
                pred_data.append({
                    "Heure": f"{h:02d}h", 
                    "Temp": float(row[col]),
                    "Type": "Prédiction"
                })
        df_pred = pd.DataFrame(pred_data)
        
        if not df_pred.empty:
            chart = alt.Chart(df_pred).mark_line(
                point=True,
                interpolate='catmull-rom',
                strokeWidth=3
            ).encode(
                x=alt.X('Heure', sort=None, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Temp', scale=alt.Scale(zero=False), title=None),
                color=alt.value("#EF4444"), # Rouge fixe
                tooltip=['Heure', alt.Tooltip('Temp', format='.1f', title='Prédiction')]
            ).properties(
                height=360 
            )
            st.altair_chart(chart, use_container_width=True)

st.markdown("###")

# --- C. TABLEAU ---
with st.container(border=True):
    st.markdown("### 📋 Vue d'Ensemble")
    
    st.dataframe(
        df[['city', 'actual_temp', 'pred_max_tomorrow', 'humidity', 'wind']],
        column_config={
            "city": "Ville",
            "actual_temp": st.column_config.NumberColumn("Actuel", format="%.1f°C"),
            "pred_max_tomorrow": st.column_config.NumberColumn("Max Demain", format="%.1f°C"),
            "humidity": st.column_config.ProgressColumn("Humidité", format="%d%%", min_value=0, max_value=100),
            "wind": st.column_config.NumberColumn("Vent", format="%.1f km/h")
        },
        use_container_width=True,
        hide_index=True,
        height=400
    )

time.sleep(3)
st.rerun()