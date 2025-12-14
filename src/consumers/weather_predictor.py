import joblib
import time
import pandas as pd
import os
import datetime
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import warnings

# --- INFLUXDB IMPORT ---
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

warnings.filterwarnings("ignore")

# --- CONFIG ---
KAFKA_BOOTSTRAP = "localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"
INPUT_TOPIC = "data.weather.live"
MODEL_FILE = "weather_model.pkl"

#  CONFIG INFLUXDB (A ADAPTER SELON VOTRE DOCKER)
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "adminpassword"  # Mettez ici votre token ou password admin
INFLUX_ORG = "ecostream"
INFLUX_BUCKET = "weather_data"

TARGET_HOURS = list(range(24))

def main():
    print("🔄 Prédicteur -> InfluxDB (24h) Démarré...")
    
    if not os.path.exists(MODEL_FILE): return
    model = joblib.load(MODEL_FILE)
    
    # Kafka Setup
    schema_registry = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})
    try:
        input_schema = schema_registry.get_latest_version(f"{INPUT_TOPIC}-value").schema.schema_str
        avro_deserializer = AvroDeserializer(schema_registry, input_schema)
    except: return
    
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': 'weather-influx-consumer-v2',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe([INPUT_TOPIC])

    # InfluxDB Setup
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        print("✅ Connecté à la Base de Données")
    except Exception as e:
        print(f"❌ Erreur DB: {e}")
        return

    print("📊 Traitement des flux...")

    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error(): continue

        try:
            data = avro_deserializer(msg.value(), SerializationContext(INPUT_TOPIC, MessageField.VALUE))
            
            # Données Live
            temp = float(data.get('temperature', 0))
            hum = float(data.get('humidity', 50))
            pres = float(data.get('pressure', 1013))
            wind = float(data.get('wind_speed', 10))
            is_day = int(data.get('is_day', 1))
            current_hour = datetime.datetime.now().hour
            city = str(data.get('city', 'Inconnue'))

            # Prédiction
            features = pd.DataFrame([[temp, hum, pres, wind, is_day, current_hour]], 
                                  columns=["temperature", "humidity", "pressure", "wind_speed", "is_day", "current_hour"])
            preds = model.predict(features)[0]
            pred_max = float(max(preds))

            # --- ECRITURE INFLUXDB ---
            # On stocke tout dans un "Point"
            point = Point("weather_metrics") \
                .tag("city", city) \
                .field("actual_temp", temp) \
                .field("humidity", hum) \
                .field("wind", wind) \
                .field("pred_max_tomorrow", pred_max) \
                .time(datetime.datetime.utcnow(), WritePrecision.NS)
            
            # On ajoute les 24 prévisions comme champs (fields) séparés
            for h, val in zip(TARGET_HOURS, preds):
                point.field(f"pred_{h:02d}h", float(val))

            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            
            print(f"✅ {city:<10} | Saved to DB | Max Demain: {pred_max:.1f}°C")

        except Exception as e:
            print(f"⚠️ Erreur: {e}")

if __name__ == "__main__":
    main()