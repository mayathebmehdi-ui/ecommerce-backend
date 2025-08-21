#!/bin/bash

# E-commerce Policy Analyzer - Script de démarrage
echo "🌐 Démarrage de l'E-commerce Policy Analyzer..."

# Vérifier que les dépendances sont installées
echo "📦 Vérification des dépendances..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

# Vérifier le fichier .env
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env manquant. Copie du template..."
    cp env.example .env
    echo "✅ Veuillez configurer votre OPENAI_API_KEY dans le fichier .env"
    echo "📝 Éditez le fichier .env avec votre clé API OpenAI"
    exit 1
fi

# Installer les dépendances Python si nécessaire
if [ ! -d "venv" ]; then
    echo "🐍 Création de l'environnement virtuel Python..."
    python3 -m venv venv
fi

echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

echo "📥 Installation des dépendances Python..."
pip install -r requirements.txt

echo "🎭 Installation de Playwright..."
playwright install

# Installer les dépendances Frontend si nécessaire
if [ ! -d "frontend/node_modules" ]; then
    echo "⚛️  Installation des dépendances React..."
    cd frontend
    npm install --legacy-peer-deps
    cd ..
fi

# Corriger les permissions des scripts React
echo "🔧 Correction des permissions React..."
if [ -f "frontend/node_modules/.bin/react-scripts" ]; then
    chmod +x frontend/node_modules/.bin/react-scripts
    echo "✅ Permissions react-scripts corrigées"
fi

# Corriger les permissions de tous les binaires dans node_modules/.bin
if [ -d "frontend/node_modules/.bin" ]; then
    chmod +x frontend/node_modules/.bin/* 2>/dev/null
    echo "✅ Permissions des binaires Node.js corrigées"
fi

echo "🧹 Nettoyage des anciens processus..."

# Arrêter les anciens processus utilisant les ports 8000 et 3000
echo "🔍 Recherche des processus utilisant les ports 8000 et 3000..."

# Tuer les processus sur le port 8000 (Backend)
PORT_8000_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$PORT_8000_PID" ]; then
    echo "⚡ Arrêt du processus utilisant le port 8000 (PID: $PORT_8000_PID)"
    kill -9 $PORT_8000_PID 2>/dev/null
    sleep 2
fi

# Tuer les processus sur le port 3000 (Frontend)
PORT_3000_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$PORT_3000_PID" ]; then
    echo "⚡ Arrêt du processus utilisant le port 3000 (PID: $PORT_3000_PID)"
    kill -9 $PORT_3000_PID 2>/dev/null
    sleep 2
fi

# Tuer les anciens processus Python et Node spécifiques
echo "🧽 Nettoyage des anciens processus spécifiques..."
pkill -f "python main.py" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null
pkill -f "npm start" 2>/dev/null

echo "✅ Nettoyage terminé"

echo "🚀 Démarrage des services..."

# Démarrer le backend en arrière-plan
echo "🔧 Démarrage du backend FastAPI..."
python main.py &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "⏳ Attente du démarrage du backend..."
sleep 5

# Démarrer le frontend
echo "🎨 Démarrage du frontend React..."
cd frontend

# Vérifier que react-scripts existe et a les bonnes permissions
if [ ! -f "node_modules/.bin/react-scripts" ]; then
    echo "❌ react-scripts non trouvé, réinstallation des dépendances..."
    npm install --legacy-peer-deps
fi

# S'assurer que react-scripts a les permissions d'exécution
chmod +x node_modules/.bin/react-scripts 2>/dev/null

echo "🔧 Démarrage du serveur React (sans navigateur)..."
BROWSER=none npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Services démarrés avec succès!"
echo ""
echo "🌐 Interface web: http://localhost:3000"
echo "🔧 API Backend: http://localhost:8000"
echo "📚 Documentation API: http://localhost:8000/docs"
echo ""
echo "⚡ Pour arrêter les services, appuyez sur Ctrl+C"
echo ""

# Fonction pour nettoyer les processus à l'arrêt
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services arrêtés"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Attendre indéfiniment
wait
