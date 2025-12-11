import requests
import pandas as pd
import datetime

# Configuration des villes (Lat/Lon)
CITIES = [
    # --- AFRIQUE (Maroc complet + Capitales majeures) ---
    {"name": "Tanger", "lat": 35.77, "lon": -5.80}, {"name": "Tetouan", "lat": 35.57, "lon": -5.36},
    {"name": "Al Hoceima", "lat": 35.25, "lon": -3.93}, {"name": "Nador", "lat": 35.17, "lon": -2.93},
    {"name": "Oujda", "lat": 34.68, "lon": -1.90}, {"name": "Rabat", "lat": 34.02, "lon": -6.83},
    {"name": "Casablanca", "lat": 33.57, "lon": -7.58}, {"name": "Kenitra", "lat": 34.26, "lon": -6.58},
    {"name": "Fes", "lat": 34.03, "lon": -5.00}, {"name": "Meknes", "lat": 33.89, "lon": -5.55},
    {"name": "Ifrane", "lat": 33.53, "lon": -5.11}, {"name": "Marrakech", "lat": 31.62, "lon": -7.98},
    {"name": "Essaouira", "lat": 31.50, "lon": -9.77}, {"name": "Agadir", "lat": 30.42, "lon": -9.59},
    {"name": "Ouarzazate", "lat": 30.91, "lon": -6.89}, {"name": "Errachidia", "lat": 31.93, "lon": -4.42},
    {"name": "Laayoune", "lat": 27.12, "lon": -13.19}, {"name": "Dakhla", "lat": 23.68, "lon": -15.95},
    {"name": "Tunis", "lat": 36.80, "lon": 10.18}, {"name": "Cairo", "lat": 30.04, "lon": 31.23},
    {"name": "Dakar", "lat": 14.71, "lon": -17.46}, {"name": "Nairobi", "lat": -1.29, "lon": 36.82},
    {"name": "Cape Town", "lat": -33.92, "lon": 18.42}, {"name": "Lagos", "lat": 6.52, "lon": 3.37},

    # --- EUROPE (Capitales froides & tempérées) ---
    {"name": "Paris", "lat": 48.85, "lon": 2.35}, {"name": "London", "lat": 51.50, "lon": -0.12},
    {"name": "Berlin", "lat": 52.52, "lon": 13.40}, {"name": "Madrid", "lat": 40.41, "lon": -3.70},
    {"name": "Rome", "lat": 41.90, "lon": 12.49}, {"name": "Moscow", "lat": 55.75, "lon": 37.61},
    {"name": "Kyiv", "lat": 50.45, "lon": 30.52}, {"name": "Oslo", "lat": 59.91, "lon": 10.75},
    {"name": "Istanbul", "lat": 41.00, "lon": 28.97}, {"name": "Athens", "lat": 37.98, "lon": 23.72},
    {"name": "Reykjavik", "lat": 64.14, "lon": -21.94}, {"name": "Lisbon", "lat": 38.72, "lon": -9.13},

    # --- ASIE & MOYEN-ORIENT (Déserts & Tropiques) ---
    {"name": "Tokyo", "lat": 35.68, "lon": 139.76}, {"name": "Beijing", "lat": 39.90, "lon": 116.40},
    {"name": "Mumbai", "lat": 19.07, "lon": 72.87}, {"name": "New Delhi", "lat": 28.61, "lon": 77.20},
    {"name": "Dubai", "lat": 25.20, "lon": 55.27}, {"name": "Riyadh", "lat": 24.71, "lon": 46.67},
    {"name": "Bangkok", "lat": 13.75, "lon": 100.50}, {"name": "Singapore", "lat": 1.35, "lon": 103.81},
    {"name": "Seoul", "lat": 37.56, "lon": 126.97}, {"name": "Jakarta", "lat": -6.20, "lon": 106.84},

    # --- AMÉRIQUES (Nord & Sud) ---
    {"name": "New York", "lat": 40.71, "lon": -74.00}, {"name": "Los Angeles", "lat": 34.05, "lon": -118.24},
    {"name": "Chicago", "lat": 41.87, "lon": -87.62}, {"name": "Toronto", "lat": 43.65, "lon": -79.38},
    {"name": "Mexico City", "lat": 19.43, "lon": -99.13}, {"name": "Rio de Janeiro", "lat": -22.90, "lon": -43.17},
    {"name": "Buenos Aires", "lat": -34.60, "lon": -58.38}, {"name": "Santiago", "lat": -33.44, "lon": -70.66},
    {"name": "Bogota", "lat": 4.71, "lon": -74.07}, {"name": "Lima", "lat": -12.04, "lon": -77.04},

    # --- OCÉANIE ---
    {"name": "Sydney", "lat": -33.86, "lon": 151.20}, {"name": "Melbourne", "lat": -37.81, "lon": 144.96},
    {"name": "Auckland", "lat": -36.84, "lon": 174.76}
]

# On récupère les 90 derniers jours
END_DATE = datetime.date.today()
START_DATE = END_DATE - datetime.timedelta(days=90)

print(f"🌍 Téléchargement des données RÉELLES ({START_DATE} -> {END_DATE})...")

all_data = []

for city in CITIES:
    print(f"   ⬇️  Récupération pour {city['name']}...")
    
    # API Archive d'Open-Meteo (Données historiques réelles)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m"
    }
    
    try:
        resp = requests.get(url, params=params).json()
        
        hourly = resp['hourly']
        count = len(hourly['time'])
        
        for i in range(count - 24): # -1 car on ne peut pas prédire le futur du dernier point
            # Feature Engineering "Live"
            # On extrait l'heure pour savoir s'il fait jour (simplifié)
            hour = int(hourly['time'][i].split('T')[1].split(':')[0])
            is_day = 1 if 6 <= hour <= 20 else 0
            
            all_data.append({
                "temperature": hourly['temperature_2m'][i],
                "humidity": hourly['relative_humidity_2m'][i],
                "pressure": hourly['surface_pressure'][i],
                "wind_speed": hourly['wind_speed_10m'][i],
                "is_day": is_day,
                
                # C'EST ICI QUE TOUT CHANGE : [i + 24] au lieu de [i + 1]
                "TARGET_NEXT_TEMP": hourly['temperature_2m'][i + 24] 
            })
            
    except Exception as e:
        print(f"❌ Erreur {city['name']}: {e}")

# Sauvegarde
df = pd.DataFrame(all_data)
df = df.dropna()
df.to_csv("weather_history_real.csv", index=False)
print(f"✅ Succès ! {len(df)} lignes de données réelles sauvegardées.")