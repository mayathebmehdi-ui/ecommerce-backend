# Dockerfile optimisé pour Render.com
FROM mcr.microsoft.com/playwright/python:v1.45.0-focal

WORKDIR /app

# Optimisations pour Render
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=10000

# Copier et installer les requirements d'abord (cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installer Playwright browsers
RUN playwright install --with-deps chromium

# Copier le code de l'application
COPY . .

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 10000

# Commande de démarrage pour Render
CMD ["python", "main.py"]
