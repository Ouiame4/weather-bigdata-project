@echo off
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo   StreamAI Forecaster – Démarrage complet en 1 clic
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Démarrage du Producteur (Source de données)
start "Producteur Meteo" cmd /c "python src\producers\weather_producer.py"

:: Démarrage du Prédicteur (Intelligence Artificielle)
start "Predict eur IA"    cmd /c "python src\consumers\weather_predictor.py"

:: Démarrage du Dashboard (Visualisation)
:: CORRECTION ICI : Utilisation de "python -m streamlit" au lieu de "streamlit" direct
:: Et utilisation de /k pour garder la fenêtre ouverte si ça plante
start "Dashboard Streamlit" cmd /k "python -m streamlit run src\dashboard\dashboard.py --server.port=8501 --theme.base=light"

echo.
echo Tout est lance !
echo → Dashboard Streamlit : http://localhost:8501
echo → Grafana             : http://localhost:3000
echo.
echo Appuie sur une touche pour tout arreter proprement...
pause >nul

:: Arrêt propre des fenêtres
taskkill /FI "WINDOWTITLE eq Producteur Meteo*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Predict eur IA*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Dashboard Streamlit*" /F >nul 2>&1

:: On tue aussi python.exe si nécessaire (attention si vous avez d'autres scripts python en cours)
taskkill /IM python.exe /F >nul 2>&1

echo Tout arrete proprement.