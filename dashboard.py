import streamlit as st
import json
import time
import pandas as pd
import glob
import altair as alt
import numpy as np

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="EcoStream AI | Monitoring",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. STYLE CSS (THÈME CLAIR & PRO) ---
st.markdown("""
<style>
    /* Fond de la page */
    .stApp {
        background-color: #F8F9FA;
        color: #212529;
    }

    /* CARTES MÉTRIQUES (KPIs) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E9ECEF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        /* Astuce pour forcer la même hauteur partout */
        min-height: 110px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: #4DA3FF;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }

    /* Valeurs (Chiffres) */
    div[data-testid="stMetricValue"] {
        color: #1F2937 !important;
        font-size: 26px !important;
        font-weight: 700 !important;
    }

    /* Labels (Titres des cartes) */
    div[data-testid="stMetricLabel"] {
        color: #6B7280 !important;
        font-size: 14px !important;
        font-weight: 600;
    }

    /* TITRE PRINCIPAL */
    h1 {
        color: #1A73E8;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DONNÉES GÉOGRAPHIQUES ---
CITY_COORDS = {
    "Tanger": [35.77, -5.80], "Tetouan": [35.57, -5.36], "Al Hoceima": [35.25, -3.93],
    "Nador": [35.17, -2.93], "Oujda": [34.68, -1.90], "Rabat": [34.02, -6.83],
    "Casablanca": [33.57, -7.58], "Kenitra": [34.26, -6.58], "Fes": [34.03, -5.00],
    "Meknes": [33.89, -5.55], "Ifrane": [33.53, -5.11], "Marrakech": [31.62, -7.98],
    "Essaouira": [31.50, -9.77], "Agadir": [30.42, -9.59], "Ouarzazate": [30.91, -6.89],
    "Errachidia": [31.93, -4.42], "Laayoune": [27.12, -13.19], "Dakhla": [23.68, -15.95],
    "Tunis": [36.80, 10.18], "Cairo": [30.04, 31.23], "Dakar": [14.71, -17.46],
    "Nairobi": [-1.29, 36.82], "Cape Town": [-33.92, 18.42], "Lagos": [6.52, 3.37],
    "Paris": [48.85, 2.35], "London": [51.50, -0.12], "Berlin": [52.52, 13.40],
    "Madrid": [40.41, -3.70], "Rome": [41.90, 12.49], "Moscow": [55.75, 37.61],
    "Kyiv": [50.45, 30.52], "Oslo": [59.91, 10.75], "Istanbul": [41.00, 28.97],
    "Athens": [37.98, 23.72], "Reykjavik": [64.14, -21.94], "Lisbon": [38.72, -9.13],
    "Tokyo": [35.68, 139.76], "Beijing": [39.90, 116.40], "Mumbai": [19.07, 72.87],
    "New Delhi": [28.61, 77.20], "Dubai": [25.20, 55.27], "Riyadh": [24.71, 46.67],
    "Bangkok": [13.75, 100.50], "Singapore": [1.35, 103.81], "Seoul": [37.56, 126.97],
    "Jakarta": [-6.20, 106.84], "New York": [40.71, -74.00], "Los Angeles": [34.05, -118.24],
    "Chicago": [41.87, -87.62], "Toronto": [43.65, -79.38], "Mexico City": [19.43, -99.13],
    "Rio de Janeiro": [-22.90, -43.17], "Buenos Aires": [-34.60, -58.38], "Santiago": [-33.44, -70.66],
    "Bogota": [4.71, -74.07], "Lima": [-12.04, -77.04], "Sydney": [-33.86, 151.20],
    "Melbourne": [-37.81, 144.96], "Auckland": [-36.84, 174.76]
}

def load_data():
    files = glob.glob("dashboard_data/*.json")
    data_list = []
    for file in files:
        try:
            with open(file, "r") as f:
                item = json.load(f)
                if item['city'] in CITY_COORDS:
                    item['lat'] = CITY_COORDS[item['city']][0]
                    item['lon'] = CITY_COORDS[item['city']][1]
                    data_list.append(item)
        except:
            continue
    return pd.DataFrame(data_list)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Contrôles")
    df_init = load_data()
    all_cities = sorted(df_init['city'].unique()) if not df_init.empty else []
    
    container = st.container()
    all = st.checkbox(" Tout sélectionner", value=True)
    if all:
        selected_cities = container.multiselect("Villes:", all_cities, default=all_cities)
    else:
        selected_cities = container.multiselect("Villes:", all_cities)
        
    

# --- 5. CORPS PRINCIPAL ---
placeholder = st.empty()

while True:
    with placeholder.container():
        df = load_data()

        if df.empty:
            st.warning("⏳ En attente de données du flux Kafka...")
            time.sleep(1)
            continue

        if selected_cities:
            df = df[df['city'].isin(selected_cities)]

        # --- EN-TÊTE ---
        st.markdown("# 🌤️ Tableau de Bord Météo Temps Réel")
        
        # --- KPI GLOBAUX (4 Colonnes) ---
        k1, k2, k3, k4 = st.columns(4)
        
        avg_temp = df['actual_temp'].mean()
        hottest = df.loc[df['actual_temp'].idxmax()]
        coldest = df.loc[df['actual_temp'].idxmin()]
        
        k1.metric(
            label="Moyenne Globale",
            value=f"{avg_temp:.1f} °C"
        )
        
        k2.metric(
            label=f"🔥 Max ({hottest['city']})",
            value=f"{hottest['actual_temp']}°C"
        )
        
        k3.metric(
            label=f"❄️ Min ({coldest['city']})",
            value=f"{coldest['actual_temp']}°C"
        )
        
        k4.metric(
            label="Stations Actives",
            value=f"{len(df)}"
        )

        st.markdown("<br>", unsafe_allow_html=True) 

        # --- ONGLETS ---
        tab1, tab2, tab3 = st.tabs(["📊 Graphiques", "🗺️ Carte", "📋 Détails"])

        # ONGLET 1 : GRAPHIQUE
        with tab1:
            st.subheader("Prévisions (24h) vs Réalité")
            # Tri des données pour que la courbe soit lisible (froid -> chaud)
            df_sorted = df.sort_values('actual_temp')
            df_chart = df_sorted[['city', 'actual_temp', 'predicted_temp']].melt('city', var_name='Type', value_name='Température')
            
            # Couleurs personnalisées
            domain = ['actual_temp', 'predicted_temp']
            range_ = ['#2563EB', '#F97316'] # Bleu Royal et Orange Vif
            
            chart = alt.Chart(df_chart).mark_line(point=True, strokeWidth=3).encode(
                x=alt.X('city', sort=None, title=None),
                y=alt.Y('Température', title='Température (°C)'),
                color=alt.Color('Type', scale=alt.Scale(domain=domain, range=range_), legend=alt.Legend(title="Légende")),
                tooltip=['city', 'Température', 'Type']
            ).properties(height=450).configure_axis(
                grid=True, gridColor="#E5E7EB"
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)

        # ONGLET 2 : CARTE (CORRIGÉE)
        with tab2:
            st.subheader("Vue Satellite")
            # On crée une colonne explicite pour la taille, au lieu de passer une série calculée
            df['size_col'] = df['actual_temp'].abs() * 20 + 50 
            
            # Affichage de la carte avec la colonne 'size_col'
            st.map(df, latitude='lat', longitude='lon', size='size_col', color='#DC2626')

        # ONGLET 3 : DÉTAILS
        with tab3:
            st.subheader("Données Temps Réel")
            cols = st.columns(4)
            # Tri par nom de ville pour retrouver facilement
            for index, row in df.sort_values('city').iterrows():
                delta = row['predicted_temp'] - row['actual_temp']
                
                with cols[index % 4]:
                    st.metric(
                        label=f"📍 {row['city']}",
                        value=f"{row['actual_temp']} °C",
                        delta=f"{delta:+.2f}°C (Demain)",
                        delta_color="inverse"
                    )
                    st.caption(f"Humidité: {row['humidity']}% | Vent: {row['wind']} km/h")
                    st.markdown("---")

    time.sleep(2)