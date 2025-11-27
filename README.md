# 🌍 EcoStream AI : Météo & Prédiction Temps Réel

**EcoStream AI** est un système Big Data complet qui surveille la météo mondiale en temps réel et utilise une Intelligence Artificielle pour prédire l'évolution des températures à court terme.

---

## 🏗️ Architecture

Le projet suit une architecture de streaming moderne :
1.  **Source :** API Open-Meteo (Données réelles de 50+ villes).
2.  **Transport :** Apache Kafka (Mode KRaft) pour le flux de données.
3.  **IA :** Modèle XGBoost entraîné sur 3 mois d'historique réel.
4.  **Visualisation :** Dashboard interactif Streamlit.