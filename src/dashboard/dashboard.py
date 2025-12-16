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
/* ========================= */
/* FOND GLOBAL (GRIS)        */
/* ========================= */
.stApp {
    background-color: #F8F9FA;
}

/* ========================= */
/* KPI CARDS                 */
/* ========================= */
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

/* ========================= */
/* CONTAINERS (BORDURES)     */
/* ========================= */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: transparent !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: #FFFFFF !important;
    border-radius: 14px;
    border: 1px solid #E6E6EA;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* ========================= */
/* GRAPHIQUES ALTAIR         */
/* ========================= */
div[data-testid="stVegaLiteChart"],
div[data-testid="stVegaLiteChart"] > div {
    background-color: #FFFFFF !important;
}

/* ========================= */
/* DATAFRAME / TABLEAU       */
/* ========================= */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrame"] > div,
div[data-testid="stDataFrame"] table {
    background-color: #FFFFFF !important;
    border-radius: 10px;
}

/* cellules tableau */
thead, tbody, tr, td, th {
    background-color: #FFFFFF !important;
}

/* ========================= */
/* TITRES                    */
/* ========================= */
h3 {
    font-size: 18px;
    font-weight: 600;
    color: #1E293B;
    margin-bottom: 16px;
}

/* ========================= */
/* ESPACEMENT GLOBAL         */
/* ========================= */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)


# --- 3. CONNEXION BDD ---
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "adminpassword"
INFLUX_ORG = "ecostream"
INFLUX_BUCKET = "weather_data"

def load_data():
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

# En-tête simplifié
st.markdown("###")
st.markdown("## 🌤️ EcoStream AI | Tableau de Bord")
st.markdown("---")

if df.empty:
    st.warning("📡 En attente de connexion satellite...")
    time.sleep(3)
    st.rerun()

# --- A. LIGNE DES KPIS (Alignés grâce au CSS 'height: 140px') ---
c1, c2, c3, c4 = st.columns(4)

c1.metric("Stations Surveillées", f"{len(df)}")
c2.metric("Moyenne Globale", f"{df['actual_temp'].mean():.1f}°C")
c3.metric("Pic Moyen Demain", f"{df['pred_max_tomorrow'].mean():.1f}°C")

hottest = df.loc[df['actual_temp'].idxmax()]
# Le delta s'affiche, mais la carte aura la même taille que les autres grâce au CSS
c4.metric("Point Chaud", f"{hottest['actual_temp']}°C", delta=f"{hottest['city']}")

st.markdown("###")

# --- B. ZONE PRINCIPALE (Alignement Hauteur) ---
# On utilise st.columns pour séparer Contrôle (1/4) et Graphique (3/4)
c_control, c_chart = st.columns([1, 3])

with c_control:
    # Conteneur Contrôle
    with st.container(border=True):
        
        cities = sorted(df['city'].unique())
        ix = cities.index("Tanger") if "Tanger" in cities else 0
        choix = st.selectbox("Ville :", cities, index=ix)
        
        row = df[df['city'] == choix].iloc[0]
        
        st.caption(f"🕒 Donnée reçue à : {row['_time'].strftime('%H:%M:%S')}")
        
        # Métriques internes compactes
        st.metric("Actuel", f"{row['actual_temp']}°C")
        delta_val = row['pred_max_tomorrow'] - row['actual_temp']
        st.metric("Max Demain", f"{row['pred_max_tomorrow']}°C", delta=f"{delta_val:+.1f}°C")

with c_chart:
    # Conteneur Graphique
    with st.container(border=True):
        st.markdown(f"### 📈 Courbe d'évolution prévue pour {choix}")
        
        # Données
        hourly_data = []
        for h in range(24):
            col = f"pred_{h:02d}h"
            if col in row:
                valeur_arrondie = round(float(row[col]), 1)
                hourly_data.append({"Heure": f"{h:02d}h", "Temp": row[col]})
        chart_df = pd.DataFrame(hourly_data)
        
        if not chart_df.empty:
            chart = alt.Chart(chart_df).mark_line(
                point=True,
                interpolate='catmull-rom',
                strokeWidth=3
            ).encode(
                x=alt.X('Heure', sort=None, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y('Temp', scale=alt.Scale(zero=False), title=None),
                color=alt.value("#3B82F6"),
                tooltip=['Heure', alt.Tooltip('Temp', format='.1f', title='Température')]
            ).properties(
                height=360 # Hauteur ajustée pour correspondre visuellement au bloc de gauche
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