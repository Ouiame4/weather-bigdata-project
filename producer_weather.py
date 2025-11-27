import requests
import time
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer

# Config API
API_URL = "https://api.open-meteo.com/v1/forecast"

# Votre liste complète (Monde + Maroc)
CITIES = [
    # --- VILLES MONDIALES ---
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

KAFKA_BOOTSTRAP = "localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
TOPIC = "data.weather.live"

def main():
    # Connexion au Schema Registry
    schema_registry = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})
    try:
        with open("schemas/weather_raw.avsc", "r") as f:
            schema_str = f.read()
    except:
        print("⚠️ Fichier schema introuvable.")
        return

    avro_serializer = AvroSerializer(schema_registry, schema_str)
    string_serializer = StringSerializer('utf_8')
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP})

    print(f"🌤️  Station Météo ACTIVE (Mode Scientifique Réel)...")
    print(f"📡  Surveillance de {len(CITIES)} villes.")

    while True:
        for city in CITIES:
            try:
                # Appel API sans artifice
                params = {
                    "latitude": city["lat"], 
                    "longitude": city["lon"],
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure"
                }
                resp = requests.get(API_URL, params=params, timeout=5).json().get('current')

                if resp:
                    # On prend la valeur BRUTE de l'API
                    record = {
                        "city": city["name"],
                        "temperature": float(resp['temperature_2m']),
                        "humidity": float(resp['relative_humidity_2m']),
                        "wind_speed": float(resp['wind_speed_10m']),
                        "pressure": float(resp['surface_pressure']),
                        "timestamp": int(time.time() * 1000)
                    }

                    # Envoi vers Kafka
                    producer.produce(
                        topic=TOPIC,
                        key=string_serializer(city["name"]),
                        value=avro_serializer(record, SerializationContext(TOPIC, MessageField.VALUE))
                    )
                    
                    print(f"📍 {city['name']:<10} : {record['temperature']}°C")

            except Exception as e:
                # En cas de timeout, on passe silencieusement à la ville suivante
                pass

        producer.flush()
        # On attend 20 secondes car les données réelles changent lentement
        time.sleep(20) 

if __name__ == "__main__":
    main()