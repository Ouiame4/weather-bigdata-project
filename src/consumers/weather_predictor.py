import joblib
import json
import time
import pandas as pd
import os
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import warnings

warnings.filterwarnings("ignore")

# Config
KAFKA_BOOTSTRAP = "localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
INPUT_TOPIC = "data.weather.live"
MODEL_FILE = "../src/models/weather_model.pkl"

def main():
    print("🔄 Démarrage du Prédicteur (Version Robuste)...")
    
    # 1. Chargement IA
    if not os.path.exists(MODEL_FILE):
        print(f"❌ ERREUR: '{MODEL_FILE}' introuvable.")
        return
    
    model = joblib.load(MODEL_FILE)
    print("🧠 IA Météo chargée.")

    # 2. Config Kafka
    schema_registry = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})
    try:
        input_schema = schema_registry.get_latest_version(f"{INPUT_TOPIC}-value").schema.schema_str
        avro_deserializer = AvroDeserializer(schema_registry, input_schema)
    except Exception as e:
        print(f"❌ ERREUR Schéma: {e}")
        return
    
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': 'dashboard-feeder-v3', # Nouveau groupe pour éviter les conflits
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([INPUT_TOPIC])

    print("📊 Traitement des données...")

    msg_count = 0
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None: continue

        if msg.error():
            print(f"⚠️ Erreur Kafka: {msg.error()}")
            continue

        try:
            data = avro_deserializer(msg.value(), SerializationContext(INPUT_TOPIC, MessageField.VALUE))
            msg_count += 1
            
            # --- CORRECTION DU BUG ---
            # On utilise .get() avec une valeur par défaut pour éviter le crash
            # Si 'is_day' manque, on suppose qu'il fait jour (1)
            # Si 'pressure' manque, on met une pression standard (1013)
            
            temp = data.get('temperature', 0)
            hum = data.get('humidity', 50)
            pres = data.get('pressure', 1013)
            wind = data.get('wind_speed', 10)
            is_day = data.get('is_day', 1) 

            # Préparation IA
            features = pd.DataFrame([[temp, hum, pres, wind, is_day]], 
                                  columns=["temperature", "humidity", "pressure", "wind_speed", "is_day"])

            # Prédiction
            predicted_temp = model.predict(features)[0]
            
            # Sauvegarde JSON pour le Dashboard
            dashboard_data = {
                "city": data.get('city', 'Inconnue'),
                "actual_temp": temp,
                "predicted_temp": round(float(predicted_temp), 2),
                "humidity": hum,
                "wind": wind,
                "timestamp": time.time()
            }
            
            os.makedirs("dashboard_data", exist_ok=True)
            # On sauvegarde uniquement si on a un nom de ville valide
            if 'city' in data:
                with open(f"dashboard_data/{data['city']}.json", "w") as f:
                    json.dump(dashboard_data, f)
                
                print(f"✅ [{msg_count}] {data['city']} : {temp}°C -> Prévision : {predicted_temp:.2f}°C")

        except Exception as e:
            # On ignore les erreurs sur les vieux messages pour ne pas arrêter le script
            # print(f"⚠️ Message ignoré : {e}")
            pass

if __name__ == "__main__":
    main()