# Utiliser une image de base compatible avec Render, par exemple python:3.8-slim
FROM python:3.8-slim

# Copier les fichiers nécessaires
COPY . /app

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && \
    apt-get install -y $(cat apt.txt) && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port
EXPOSE 5000

# Démarrer l'application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
