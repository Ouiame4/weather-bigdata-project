# 🌍 EcoStream AI : Météo & Prédiction Temps Réel

**EcoStream AI** est une solution Big Data de surveillance climatique intégrant une chaîne de traitement complète : streaming de données en temps réel, intelligence artificielle prédictive et visualisation analytique.

Le système collecte les données de **59 stations météorologiques** mondiales, les traite via **Apache Kafka**, prédit la courbe de température pour les prochaines 24 heures grâce à un modèle **XGBoost**, et stocke le tout dans une base de données **InfluxDB**.

---

## Architecture Technique

Le projet repose sur une architecture moderne orientée événements (Event-Driven Architecture) :

* **Source de Données :**
    -  Simulation de capteurs via l'API **Open-Meteo**.
    -  Couverture : 59 villes majeures (Afrique, Europe, Asie, Amériques, Océanie).
* **Transport (Streaming) :**
    - **Apache Kafka** (Mode KRaft, sans ZooKeeper).
    - Sérialisation Avro via **Schema Registry**.
* **Intelligence Artificielle :**
    - Modèle **XGBoost (Multi-Output Regressor)**.
    - Capacité : Prédit une courbe complète de 24 points (heure par heure) pour J+1.
* **Stockage (Time Series) :**
    - **InfluxDB** : Base de données optimisée pour les séries temporelles.
    - Persistance des données réelles et des prédictions.
* **Visualisation :**
    - Dashboard **Streamlit** style "SaaS/Monitoring".
    - Connexion directe à la base de données.

---

##  Technologies Utilisées

* **Apache Kafka** (KRaft) & **Confluent Schema Registry**
* **XGBoost** (Machine Learning)
* **InfluxDB** (Time Series Database)
* **Streamlit** & **Altair** (Data Viz)
* **Docker** & **Docker Compose**
* **Python 3.9+** (Pandas, Scikit-learn)

---

##  Pré-requis

* **Docker Desktop** (avec Docker Compose).
* **Python 3.9** ou supérieur.
* Connexion Internet (pour l'API météo).

###  Installation des Dépendances Python
```bash
pip install confluent-kafka influxdb-client streamlit pandas scikit-learn xgboost requests altair  
```
---

###  Guide de Démarrage
Lancer l’Infrastructure (Docker)
Démarre Kafka, Schema Registry, Kafdrop et InfluxDB :

```bash
docker-compose up -d
```

Initialiser l’IA (À faire une seule fois)
Étape A — Télécharger l’historique météo (3 mois)

```bash
python scripts/fetch_real_history.py
```

Étape B — Entraîner le modèle IA Cette étape génère le fichier weather_model.pkl.

```bash
python src/models/train_weather_model.py
```

Lancer l’Application Complète
Le script d’automatisation démarre le producteur Kafka, le service de prédiction et le dashboard Streamlit simultanément.

Double-cliquez sur 
```bash 
run.bat 
```


Projet réalisé dans le cadre du module Big Data - ENSAO
