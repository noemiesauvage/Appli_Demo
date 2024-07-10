# Utilisez une image de base officielle de Python avec des dépendances essentielles
FROM python:3.9-slim

# Définissez le répertoire de travail
WORKDIR /app

# Copiez les fichiers de votre application
COPY . /app

# Installez les dépendances du système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installez les dépendances de votre application
RUN pip install --upgrade pip
RUN pip install Flask==2.0.1 requests==2.25.1 nltk==3.6.2 pandas==1.2.4 wordcloud gunicorn

# Exposez le port sur lequel l'application s'exécute
EXPOSE 5000

# Démarrez l'application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
