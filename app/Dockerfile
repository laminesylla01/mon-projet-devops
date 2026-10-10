# Image de départ : Linux léger avec Python déjà installé
FROM python:3.12-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY app.py .

# Port utilisé par l'application
EXPOSE 5000

# Commande lancée au démarrage du conteneur
CMD ["python", "app.py"]