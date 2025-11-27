import requests
import json
from kafka.admin import KafkaAdminClient, NewTopic

def setup():
    print("🔧 SETUP MÉTÉO...")
    # 1. Créer Topic
    try:
        admin = KafkaAdminClient(bootstrap_servers="localhost:9092")
        topic = NewTopic(name="data.weather.live", num_partitions=3, replication_factor=1)
        admin.create_topics([topic])
        print("✅ Topic créé.")
    except: print("ℹ️ Topic existe déjà.")

    # 2. Enregistrer Schéma
    with open("schemas/weather_raw.avsc", "r") as f: schema = f.read()
    res = requests.post(
        "http://localhost:8081/subjects/data.weather.live-value/versions",
        headers={"Content-Type": "application/vnd.schemaregistry.v1+json"},
        data=json.dumps({"schema": schema})
    )
    print("✅ Schéma enregistré.")

if __name__ == "__main__": setup()