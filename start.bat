@echo off
title NetScanner - Démarrage
color 0B
echo.
echo  ███╗   ██╗███████╗████████╗███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗
echo  ████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
echo  ██╔██╗ ██║█████╗     ██║   ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
echo  ██║╚██╗██║██╔══╝     ██║   ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
echo  ██║ ╚████║███████╗   ██║   ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
echo  ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
echo.
echo  Network Discovery Tool v2.0
echo  ════════════════════════════════════════
echo.

:: Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python n'est pas installé ou non trouvé dans le PATH.
    echo  Télécharge Python sur https://www.python.org/downloads/
    echo  IMPORTANT : Coche "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

echo  [OK] Python détecté
echo.

:: Installer dépendances si besoin
echo  Vérification des dépendances...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo  Installation de Flask...
    pip install flask flask-cors --quiet
)
pip show flask-cors >nul 2>&1
if errorlevel 1 (
    pip install flask-cors --quiet
)
echo  [OK] Dépendances OK
echo.

:: Lancer le backend
echo  Démarrage du backend sur http://localhost:5000 ...
echo  ════════════════════════════════════════
echo.
start "NetScanner Backend" /B python backend.py

:: Attendre que le backend démarre
echo  Attente du démarrage du backend...
timeout /t 2 /nobreak >nul

:: Ouvrir le navigateur
echo  Ouverture de l'interface dans le navigateur...
start "" "index.html"

echo.
echo  ════════════════════════════════════════
echo  NetScanner est lancé !
echo  Interface : index.html (dans le navigateur)
echo  Backend   : http://localhost:5000
echo  ════════════════════════════════════════
echo.
echo  Appuie sur une touche pour arrêter le backend et quitter.
pause >nul

:: Arrêter le backend Python
echo  Arrêt du backend...
taskkill /F /FI "WINDOWTITLE eq NetScanner Backend" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
echo  Backend arrêté. Au revoir !
timeout /t 1 /nobreak >nul
