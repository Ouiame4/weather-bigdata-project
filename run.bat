@echo off
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo   StreamAI Forecaster – Démarrage complet en 1 clic
echo ╚═══════════════════════════════════════════════════════════╝
echo.

start "Producteur Meteo" cmd /c "python src\producers\weather_producer.py"
start "Predict eur IA"    cmd /c "python src\consumers\weather_predictor.py"
start "Dashboard Streamlit" cmd /c "streamlit run src\dashboard\dashboard.py --server.port=8501 --theme.base=light"

echo.
echo Tout est lance !
echo → Dashboard Streamlit : http://localhost:8501
echo → Grafana             : http://localhost:3000
echo.
echo Appuie sur une touche pour tout arreter proprement...
pause >nul
taskkill /FI "WINDOWTITLE eq Producteur Meteo*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Predict eur IA*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Dashboard Streamlit*" /F >nul 2>&1
taskkill /IM streamlit.exe /F >nul 2>&1
echo Tout arrete proprement.