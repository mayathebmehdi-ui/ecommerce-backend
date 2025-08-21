# 🌐 E-commerce Policy Analyzer

## 🎯 Description

Système d'IA innovant et professionnel qui analyse automatiquement les politiques de livraison et retours des sites e-commerce. La plateforme extrait, classifie et structure les informations selon un format CSV standardisé.

## ✨ Fonctionnalités

### 🔍 Analyse Automatique
- **Scraping intelligent** avec Playwright et BeautifulSoup
- **Navigation automatique** vers les pages pertinentes (livraison, retours, FAQ)
- **Extraction IA** avec OpenAI GPT-4 et function calling

### 📊 Interface Dynamique
- **Dashboard moderne** avec animations Framer Motion
- **Statistiques en temps réel** avec graphiques interactifs
- **Tableau intelligent** avec filtres et recherche
- **Export CSV/JSON** formaté selon les spécifications

### 🛠️ Format de Sortie

Chaque analyse produit une ligne CSV avec les colonnes :
```
domain, shipping_policy_and_cost [résumé + URL], return_policy_and_cost [résumé + URL], self_help_returns [Oui/Non + URL], insurance [Oui/Non + URL],,,,,,
```

**Exemple :**
```csv
us.jshealthvitamins.com,Standard shipping (3–7 business days) costs $4.99 for orders $59.99 and below and is free for orders over $60https://us.jshealthvitamins.com/pages/shipping-returns,"JSHealth's return guarantee applies only to incorrect or damaged products. Customers must email support@jshealthvitamins.com within 7 dayshttps://us.jshealthvitamins.com/pages/shipping-returns",No – returns are handled by emailing customer servicehttps://us.jshealthvitamins.com/pages/shipping-returns,"Yes – optional ""Shipping Protection"" costs $1.99 (≈5.4%)https://us.jshealthvitamins.com/pages/shipping-returns",,,,,,
```

## 🚀 Installation

### Prérequis
- Python 3.8+
- Node.js 16+
- OpenAI API Key

### Backend (FastAPI)
```bash
# Cloner le projet
cd ecommerce2

# Installer les dépendances Python
pip install -r requirements.txt

# Configurer l'environnement
cp env.example .env
# Éditer .env avec votre OPENAI_API_KEY

# Installer Playwright
playwright install

# Démarrer le serveur
python main.py
```

### Frontend (React)
```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Démarrer l'interface
npm start
```

## 🎨 Architecture

### Backend
- **FastAPI** : API REST moderne et rapide
- **SQLAlchemy** : ORM pour base de données SQLite
- **Playwright** : Scraping web robuste
- **OpenAI GPT-4** : Analyse et classification IA

### Frontend
- **React + TypeScript** : Interface utilisateur moderne
- **Tailwind CSS** : Design system responsive
- **Framer Motion** : Animations fluides
- **Recharts** : Graphiques interactifs
- **shadcn/ui** : Composants UI professionnels

## 📡 API Endpoints

### POST /analyze
Démarre l'analyse d'un site web
```json
{
  "url": "https://example.com"
}
```

### GET /results
Récupère tous les résultats d'analyse

### GET /stats
Statistiques de la plateforme

### GET /export/csv
Export CSV de tous les résultats

### GET /job/{job_id}
Statut d'une tâche d'analyse

## 🎯 Utilisation

1. **Accéder à l'interface** : http://localhost:3000
2. **Entrer une URL** e-commerce dans le champ de saisie
3. **Cliquer "Analyser"** pour démarrer l'extraction
4. **Suivre le statut** en temps réel
5. **Explorer les résultats** dans le tableau interactif
6. **Exporter en CSV** pour utilisation externe

## 🔧 Configuration

### Variables d'environnement
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./ecommerce_analyzer.db
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Configuration Frontend
```env
REACT_APP_API_URL=http://localhost:8000
```

## 📊 Métriques Suivies

- **Sites analysés** : Nombre total d'analyses
- **Taux de succès** : Pourcentage d'extractions réussies  
- **Self-service** : Pourcentage de sites avec portail retours
- **Assurance** : Pourcentage de sites offrant une assurance

## 🛡️ Sécurité

- **Rate limiting** sur les endpoints d'analyse
- **Validation** des URLs d'entrée
- **Sanitisation** du contenu extrait
- **Headers sécurisés** (CORS, CSP)

## 🔄 Workflow d'Analyse

1. **Réception URL** → Validation et création job
2. **Scraping** → Navigation pages politiques
3. **Extraction** → Nettoyage contenu HTML
4. **Analyse IA** → Classification GPT-4
5. **Stockage** → Sauvegarde base de données
6. **Export** → Format CSV standardisé

## 🎨 Interface Utilisateur

### Dashboard Principal
- **Hero section** avec saisie URL
- **Indicateurs clés** animés
- **Statut temps réel** des analyses

### Tableau Interactif
- **Recherche full-text**
- **Filtres avancés** (self-service, assurance)
- **Vue détaillée** par modal
- **Export ligne par ligne**

### Animations
- **Framer Motion** pour transitions fluides
- **Micro-interactions** sur hover/click
- **Loading states** informatifs
- **Feedback visuel** immédiat

## 🚀 Déploiement

### Docker (Recommandé)
```bash
# Backend
docker build -t ecommerce-analyzer-api .
docker run -p 8000:8000 ecommerce-analyzer-api

# Frontend  
docker build -t ecommerce-analyzer-ui ./frontend
docker run -p 3000:3000 ecommerce-analyzer-ui
```

### Production
- **Backend** : Uvicorn avec Gunicorn
- **Frontend** : Build optimisé + serveur statique
- **Base de données** : PostgreSQL recommandée
- **Reverse proxy** : Nginx

## 📈 Évolutions Futures

- [ ] **Webhooks** pour notifications automatiques
- [ ] **API rate limiting** avancé
- [ ] **Cache Redis** pour performances
- [ ] **Analyse batch** de plusieurs URLs
- [ ] **Intégration Zapier/n8n**
- [ ] **Historique des modifications** de politiques
- [ ] **Alertes** changements de politiques

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**Développé avec ❤️ pour automatiser l'analyse des politiques e-commerce**
