# Utiliser une image de base Python
FROM python:3.10

# Définir le répertoire de travail
WORKDIR /api_model

# Copier les exigences et les installer
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copier le reste des fichiers
COPY ./ .

# Commande pour exécuter l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
