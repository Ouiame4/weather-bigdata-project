import requests
import pandas as pd
import datetime

# Configuration des villes (Lat/Lon)
CITIES = [
    # --- VILLES MONDIALES (Pour la diversité climatique) ---
    {"name": "Paris", "lat": 48.85, "lon": 2.35},
    {"name": "London", "lat": 51.50, "lon": -0.12},
    {"name": "New York", "lat": 40.71, "lon": -74.00},
    {"name": "Tokyo", "lat": 35.68, "lon": 139.76},
    {"name": "Sydney", "lat": -33.86, "lon": 151.20},
    {"name": "Berlin", "lat": 52.52, "lon": 13.40},
    {"name": "Madrid", "lat": 40.41, "lon": -3.70},
    {"name": "Rome", "lat": 41.90, "lon": 12.49},
    {"name": "Moscow", "lat": 55.75, "lon": 37.61},     # Grand froid
    {"name": "Dubai", "lat": 25.20, "lon": 55.27},      # Désert chaud
    {"name": "Mumbai", "lat": 19.07, "lon": 72.87},     # Tropical humide
    {"name": "Beijing", "lat": 39.90, "lon": 116.40},
    {"name": "Los Angeles", "lat": 34.05, "lon": -118.24},
    {"name": "Rio de Janeiro", "lat": -22.90, "lon": -43.17},
    {"name": "Cairo", "lat": 30.04, "lon": 31.23},

    # --- MAROC : NORD & RIF ---
    {"name": "Tanger", "lat": 35.77, "lon": -5.80},
    {"name": "Tetouan", "lat": 35.57, "lon": -5.36},
    {"name": "Al Hoceima", "lat": 35.25, "lon": -3.93},
    {"name": "Nador", "lat": 35.17, "lon": -2.93},
    {"name": "Chefchaouen", "lat": 35.17, "lon": -5.26},
    {"name": "Larache", "lat": 35.19, "lon": -6.15},

    # --- MAROC : CENTRE & CÔTE ATLANTIQUE ---
    {"name": "Oujda", "lat": 34.68, "lon": -1.90},
    {"name": "Kenitra", "lat": 34.26, "lon": -6.58},
    {"name": "Rabat", "lat": 34.02, "lon": -6.83},
    {"name": "Casablanca", "lat": 33.57, "lon": -7.58},
    {"name": "Mohammedia", "lat": 33.68, "lon": -7.38},
    {"name": "El Jadida", "lat": 33.23, "lon": -8.50},
    {"name": "Settat", "lat": 33.00, "lon": -7.62},
    {"name": "Safi", "lat": 32.31, "lon": -9.23},
    {"name": "Essaouira", "lat": 31.50, "lon": -9.77},
    {"name": "Agadir", "lat": 30.42, "lon": -9.59},

    # --- MAROC : INTÉRIEUR & ATLAS (Montagnes) ---
    {"name": "Fes", "lat": 34.03, "lon": -5.00},
    {"name": "Meknes", "lat": 33.89, "lon": -5.55},
    {"name": "Ifrane", "lat": 33.53, "lon": -5.11},    
    {"name": "Beni Mellal", "lat": 32.34, "lon": -6.35},
    {"name": "Khenifra", "lat": 32.93, "lon": -5.66},
    {"name": "Midelt", "lat": 32.68, "lon": -4.73},
    {"name": "Marrakech", "lat": 31.62, "lon": -7.98},

    # --- MAROC : SUD & DÉSERT ---
    {"name": "Ouarzazate", "lat": 30.91, "lon": -6.89},
    {"name": "Errachidia", "lat": 31.93, "lon": -4.42},
    {"name": "Zagora", "lat": 30.33, "lon": -5.84},
    {"name": "Tinghir", "lat": 31.51, "lon": -5.53},
    {"name": "Taroudant", "lat": 30.47, "lon": -8.87},
    {"name": "Tiznit", "lat": 29.69, "lon": -9.73},
    {"name": "Guelmim", "lat": 28.99, "lon": -10.06},
    {"name": "Tan-Tan", "lat": 28.43, "lon": -11.10},
    {"name": "Laayoune", "lat": 27.12, "lon": -13.19},
    {"name": "Smara", "lat": 26.74, "lon": -11.67},
    {"name": "Dakhla", "lat": 23.68, "lon": -15.95}
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
        
        for i in range(count - 1): # -1 car on ne peut pas prédire le futur du dernier point
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
                # CIBLE : La température réelle de l'heure suivante
                "TARGET_NEXT_TEMP": hourly['temperature_2m'][i+1]
            })
            
    except Exception as e:
        print(f"❌ Erreur {city['name']}: {e}")

# Sauvegarde
df = pd.DataFrame(all_data)
df = df.dropna()
df.to_csv("weather_history_real.csv", index=False)
print(f"✅ Succès ! {len(df)} lignes de données réelles sauvegardées.")