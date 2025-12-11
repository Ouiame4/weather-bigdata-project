import pandas as pd
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split

print("🧠 Entraînement de l'IA Météo (Moteur XGBoost)...")

# 1. Chargement des données réelles
try:
    df = pd.read_csv("../data/history/weather_history_real.csv")
except FileNotFoundError:
    print("❌ Erreur : Lancez d'abord fetch_real_history.py !")
    exit()

# Features (Entrées) et Target (Ce qu'on veut prédire)
X = df[["temperature", "humidity", "pressure", "wind_speed", "is_day"]]
y = df["TARGET_NEXT_TEMP"]

# 2. Séparation Train/Test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Configuration de XGBoost
# C'est ici que la magie opère. XGBoost construit les arbres séquentiellement pour corriger les erreurs.
model = XGBRegressor(
    n_estimators=100,     # Nombre d'arbres
    learning_rate=0.1,    # Vitesse d'apprentissage (plus petit = plus précis mais plus lent)
    max_depth=5,          # Profondeur des arbres
    n_jobs=-1,            # Utiliser tous les coeurs du CPU
    random_state=42
)

model.fit(X_train, y_train)

# 4. Évaluation
score = model.score(X_test, y_test)
print(f"🚀 Précision du modèle XGBoost (R2): {score:.4f}")

if score > 0.95:
    print("🌟 Performance Exceptionnelle !")

# 5. Sauvegarde 
joblib.dump(model, "weather_model.pkl")
print("💾 Cerveau sauvegardé : weather_model.pkl")