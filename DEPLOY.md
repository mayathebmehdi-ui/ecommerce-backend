# 🚀 GUIDE DÉPLOIEMENT GRATUIT SUR RENDER.COM

## 🎯 ÉTAPE 1: BACKEND sur Render.com (GRATUIT)

### Prérequis
- Compte GitHub (gratuit)
- Compte Render.com (gratuit)

### 1. Pusher le code sur GitHub
```bash
# Dans le dossier test1fonctionne
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/VOTRE-USERNAME/ecommerce-analyzer.git
git push -u origin main
```

### 2. Déployer sur Render
1. Aller sur https://render.com
2. Se connecter avec GitHub
3. "New +" → "Web Service"
4. Connecter votre repo GitHub `ecommerce-analyzer`
5. Configuration automatique détectée

### 3. Configurer le service
- **Name**: `ecommerce-analyzer-backend`
- **Environment**: `Docker`
- **Region**: `Frankfurt (EU)` (plus proche de la France)
- **Branch**: `main`
- **Root Directory**: `/` (racine du projet)
- **Build Command**: (laissé vide, Docker s'en charge)
- **Start Command**: (laissé vide, défini dans Dockerfile)

### 4. Variables d'environnement
Dans Render → Environment → Environment Variables:
```
OPENAI_API_KEY=votre-clé-openai
CORS_ORIGINS=https://votre-frontend.vercel.app
PORT=10000
```

### 5. Déployer
Cliquer sur "Create Web Service"
Render déploie automatiquement et vous donne une URL comme:
`https://ecommerce-analyzer-backend.onrender.com`

---

## 🌐 ÉTAPE 2: FRONTEND sur Vercel (GRATUIT)

### 1. Modifier la config API
Dans `frontend/.env.production`, remplacer par votre vraie URL Render:
```
REACT_APP_API_URL=https://ecommerce-analyzer-backend.onrender.com
```

### 2. Déployer sur Vercel
1. Aller sur https://vercel.com
2. Se connecter avec GitHub
3. "New Project" → Importer votre repo
4. Root Directory: `frontend`
5. Deploy!

### 3. Mettre à jour CORS
Retourner dans Render → Environment → Variables:
```
CORS_ORIGINS=https://votre-frontend.vercel.app
```

---

## ✅ AVANTAGES RENDER.COM

🚀 **Déploiement automatique** - Dès que vous poussez sur GitHub  
🔒 **SSL gratuit** - HTTPS automatique  
📊 **Monitoring** - Logs et métriques inclus  
🌍 **CDN global** - Performance optimale  
💾 **Base de données** - PostgreSQL gratuit inclus  
⚡ **Auto-scaling** - Gère la charge automatiquement  

---

## 🔧 ALTERNATIVE: Netlify pour le frontend

Si Vercel ne marche pas:

### Frontend sur Netlify
1. https://netlify.com → "New site from Git"
2. Connecter GitHub repo
3. Build settings:
   - Build command: `cd frontend && npm run build`
   - Publish directory: `frontend/build`
4. Deploy!

---

## 🚨 IMPORTANT

1. **Clé OpenAI**: Gardez-la secrète dans Render
2. **CORS**: Mettez l'URL exacte du frontend
3. **Port**: Render utilise le port 10000 (défini dans Dockerfile)
4. **Playwright**: Inclus dans le Dockerfile
5. **Base de données**: SQLite se crée automatiquement

---

## 📞 TESTER

Une fois déployé sur Render:
```bash
# Tester l'API
curl https://ecommerce-analyzer-backend.onrender.com/

# Tester une analyse
curl -X POST "https://ecommerce-analyzer-backend.onrender.com/analyze" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.vincecamuto.com"}'
```

Puis ouvrir le frontend dans le navigateur!

---

## 🎉 RÉSULTAT FINAL

- **Backend API**: `https://ecommerce-analyzer-backend.onrender.com`
- **Frontend**: `https://votre-frontend.vercel.app`
- **Coût**: 100% GRATUIT!
- **Performance**: Excellente avec CDN Render
