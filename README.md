# 🌍 EcoStream AI — Météo & Prédiction Temps Réel

**EcoStream AI** est une solution Big Data temps réel de surveillance climatique intégrant une chaîne complète de traitement : ingestion de flux, intelligence artificielle prédictive et visualisation analytique.

Le système collecte des données météo issues de **59 stations mondiales**, les diffuse via **Apache Kafka**, prédit la température horaire des prochaines **24 heures** grâce à un modèle **XGBoost**, et stocke les données réelles ainsi que les prédictions dans une base **InfluxDB**.

Un dashboard **Streamlit** permet le suivi et l’analyse en temps réel.

---

## ✨ Fonctionnalités Clés

* **Ingestion temps réel** de données météorologiques (Streaming Kafka).
* **Architecture Event-Driven** (Kafka en mode KRaft, sans ZooKeeper).
* **Prédiction multi-horizon (24h)** par station météo.
* **Modèle IA XGBoost** – Multi-Output Regression.
* **Stockage optimisé** séries temporelles avec **InfluxDB**.
* **Comparaison** valeurs réelles vs prédictions.
* **Dashboard interactif** type SaaS / Monitoring.

---

## 🏗️ Architecture Technique

Le projet repose sur une architecture moderne orientée événements :

### 1️⃣ Source de Données
* Simulation de capteurs via l’API **Open-Meteo**.
* Couverture : 59 villes majeures (Afrique, Europe, Asie, Amériques, Océanie).

### 2️⃣ Transport & Streaming
* **Apache Kafka** (Mode KRaft).
* Sérialisation des messages avec **Avro**.
* Gestion des schémas via **Schema Registry**.
* Visualisation des topics avec **Kafdrop**.

### 3️⃣ Intelligence Artificielle
* Modèle **XGBoost (Multi-Output Regressor)**.
* Entraîné sur plusieurs mois d’historique météo.
* Génère une courbe complète de température (24 points) pour J+1.

### 4️⃣ Stockage
* **InfluxDB** (Base Time Series).
* Stockage des données météo réelles et des données prédites.

### 5️⃣ Visualisation
* Dashboard **Streamlit**.
* Lecture directe depuis InfluxDB.
* KPIs, courbes temporelles et suivi des prédictions.

---

## 🧰 Technologies Utilisées

* **Apache Kafka** (KRaft) & **Confluent Schema Registry**
* **XGBoost** (Machine Learning)
* **InfluxDB** (Time Series Database)
* **Streamlit** & **Altair** (Data Viz)
* **Docker** & **Docker Compose**
* **Python 3.9+** (Pandas, Scikit-learn)

---

## 🛠️ Pré-requis

* **Docker Desktop** (avec Docker Compose).
* **Python 3.9** ou supérieur.
* Connexion Internet (pour l'API météo).

### 📦 Installation des Dépendances Python
```bash
pip install confluent-kafka influxdb-client streamlit pandas scikit-learn xgboost requests altair  

---

### 🚀 Guide de Démarrage
1️⃣ Lancer l’Infrastructure (Docker)
Démarre Kafka, Schema Registry, Kafdrop et InfluxDB :

```bash
docker-compose up -d

2️⃣ Initialiser l’IA (À faire une seule fois)
Étape A — Télécharger l’historique météo (3 mois)

```bash
python scripts/fetch_real_history.py

Étape B — Entraîner le modèle IA Cette étape génère le fichier weather_model.pkl.

```bash
python src/models/train_weather_model.py

3️⃣ Lancer l’Application Complète
Le script d’automatisation démarre le producteur Kafka, le service de prédiction et le dashboard Streamlit simultanément.

➡️ Double-cliquez sur run.bat


Projet réalisé dans le cadre du module Big Data - ENSAO