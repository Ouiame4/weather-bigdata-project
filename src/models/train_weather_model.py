import pandas as pd
import joblib
import os
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split

print("🧠 Entraînement IA (24 Sorties)...")

if not os.path.exists("weather_history_real.csv"):
    print("❌ Erreur : CSV introuvable.")
    exit()

df = pd.read_csv("weather_history_real.csv")

# Features
X = df[["temperature", "humidity", "pressure", "wind_speed", "is_day", "current_hour"]]

# Cibles (T_00H ... T_23H)
TARGET_HOURS = list(range(24))
target_cols = [f"T_{h:02d}H" for h in TARGET_HOURS]
y = df[target_cols]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Modèle
xgb = XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=7, n_jobs=-1, random_state=42)
model = MultiOutputRegressor(xgb)

model.fit(X_train, y_train)
print(f"🚀 Précision (R2): {model.score(X_test, y_test):.4f}")

joblib.dump(model, "weather_model.pkl")
print("💾 Modèle sauvegardé.")