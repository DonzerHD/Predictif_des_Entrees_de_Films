from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import csv
import os
import requests
from datetime import date

def fetch_movies():
    # Chemin vers le fichier CSV
    csv_path = 'films.csv'

    # Vérifier si le fichier CSV existe, sinon le créer et ajouter l'en-tête
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['titre_fr', 'realisateur', 'acteurs', 'genres', 'budget', 'date_sortie', 'compagnies_production', 'prediction']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

    # Clé API
    api_key = "a6275c028adf4e9bc5ae5f67edfb4c5f"

    # Date du mercredi prochain
    next_wednesday = date.today() + timedelta((2-date.today().weekday() + 7) % 7 + 7)

    response = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={api_key}&primary_release_date.gte={next_wednesday}&primary_release_date.lte={next_wednesday}&region=FR&language=fr-FR")
    data = response.json()

    with open(csv_path, 'a', newline='') as csvfile:
        fieldnames = ['titre_fr', 'realisateur', 'acteurs', 'genres', 'budget', 'date_sortie', 'compagnies_production', 'prediction']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for film in data['results']:
            response = requests.get(f"https://api.themoviedb.org/3/movie/{film['id']}?api_key={api_key}&language=fr-FR")
            details = response.json()

            response = requests.get(f"https://api.themoviedb.org/3/movie/{film['id']}/credits?api_key={api_key}&language=fr-FR")
            credits = response.json()

            companies = details['production_companies']
            compagnies_production = [company['name'] for company in companies]

            realisateur = next((membre for membre in credits['crew'] if membre['job'] == 'Director'), None)
            if realisateur is not None:
                realisateur = realisateur['name']

            acteurs = [acteur['name'] for acteur in credits['cast'] if acteur['order'] <= 3]
            genres = [genre['name'] for genre in details['genres']]

            # Préparer les données pour la prédiction
            prediction_data = {
                "titre_fr": details['title'],
                "realisateur": realisateur,
                "acteurs": acteurs,
                "genres": genres,
                "budget": details['budget'],
                "date_sortie": film['release_date'],
                "compagnies_production": compagnies_production,
                "titre_non_modifie": details['original_title']
            }

            # Appeler votre API pour faire la prédiction
            FAST_API_URL = "http://20.19.144.195:8000/predict"
            response = requests.post(FAST_API_URL, json=prediction_data, timeout=10)
            prediction = response.json().get("prediction")[0] if response.json().get("prediction") else None

            # Écrire les données et la prédiction dans le CSV
            writer.writerow({
                'titre_fr': details['title'],
                'realisateur': realisateur,
                'acteurs': acteurs,
                'genres': genres,
                'budget': details['budget'],
                'date_sortie': film['release_date'],
                'compagnies_production': compagnies_production,
                'prediction': prediction
            })

dag = DAG(
    'fetch_movies_dag',
    description='Récupérer les informations sur les films qui sortiront le mercredi prochain en France',
    schedule_interval=timedelta(hours=14, minutes=41),  # Exécution tous les mercredis à 11h35
    start_date=datetime(2023, 8, 9),
    catchup=False
)

# Définition de la tâche
fetch_movies_task = PythonOperator(
    task_id='fetch_movies',
    python_callable=fetch_movies,
    dag=dag
)