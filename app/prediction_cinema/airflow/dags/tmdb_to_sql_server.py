from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import requests
import time
import pyodbc

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 1),
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG('tmdb_data_extraction', default_args=default_args, schedule_interval='@weekly')

def extraction_films_tmdb(**context):
    API_KEY = "a6275c028adf4e9bc5ae5f67edfb4c5f"
    URL_UPCOMING_MOVIES = f'https://api.themoviedb.org/3/movie/upcoming?api_key={API_KEY}&language=fr-FR&region=FR'
    MIN_BUDGET = 1000000

    response = requests.get(URL_UPCOMING_MOVIES)
    if response.status_code != 200:
        print("Erreur lors de la récupération des films à venir")
        return []

    upcoming_movies = response.json()['results']
    extracted_movies = []

    for movie in upcoming_movies:
        movie_id = movie['id']
        movie_details_url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=fr-FR'
        movie_details = requests.get(movie_details_url).json()

        if movie_details['budget'] < MIN_BUDGET:
            continue

        credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}'
        credits_details = requests.get(credits_url).json()

        actors = [actor['name'] for actor in credits_details['cast'] if actor['order'] <= 3]
        directors = [crew['name'] for crew in credits_details['crew'] if crew['job'] == 'Director']

        extracted_movie = {
            'affiche': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None,
            'titre': movie['title'],
            'date_sortie': movie['release_date'],
            'genres': [genre['name'] for genre in movie_details['genres']],
            'budget': movie_details['budget'],
            'acteurs': actors,
            'realisateur': directors,
            'production_companies': [company['name'] for company in movie_details['production_companies']]
        }

        extracted_movies.append(extracted_movie)
        
        time.sleep(0.10)

    # on pousse les données extraites pour les rendre disponibles aux tâches suivantes
    context['ti'].xcom_push(key='extracted_movies', value=extracted_movies)

def charger_donnes_bdd(**context):
    # on récupère les données extraites de la tâche précédente
    extracted_movies = context['ti'].xcom_pull(key='extracted_movies', task_ids='extraction_films_tmdb')

    conn_str = (
        r'DRIVER={ODBC Driver 18 for SQL Server};'
        r'SERVER=tcp:films-serveur.database.windows.net,1433;'  
        r'DATABASE=films_bdd;' 
        r'UID=adminfilms;' 
        r'PWD=Denain59220,'  
    )
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()

    cursor.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'films_sorties')
        CREATE TABLE films_sorties (
            id INT IDENTITY(1,1),
            affiche NVARCHAR(500),
            titre NVARCHAR(500),
            date_sortie DATE,
            genres NVARCHAR(500),
            budget INT,
            acteurs NVARCHAR(500),
            realisateur NVARCHAR(500),
            production_companies NVARCHAR(500)
        );
    ''')

    for movie in extracted_movies:
        cursor.execute('''
            INSERT INTO films_sorties (affiche, titre, date_sortie, genres, budget, acteurs, realisateur, production_companies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            movie['affiche'], 
            movie['titre'], 
            movie['date_sortie'], 
            ','.join(movie['genres']), 
            movie['budget'], 
            ','.join(movie['acteurs']), 
            ','.join(movie['realisateur']), 
            ','.join(movie['production_companies'])
        ))

    cnxn.commit()
    cursor.close()
    cnxn.close()    

# on ajoute 'provide_context=True' pour que les tâches reçoivent un dictionnaire de contexte en argument
extract_task = PythonOperator(
    task_id='extraction_films_tmdb',
    python_callable=extraction_films_tmdb,
    provide_context=True,
    dag=dag)

load_task = PythonOperator(
    task_id='charger_donnes_bdd',
    python_callable=charger_donnes_bdd,
    provide_context=True,
    dag=dag)

extract_task >> load_task
