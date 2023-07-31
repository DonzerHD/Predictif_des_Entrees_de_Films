import pandas as pd
import pyodbc
from dotenv import load_dotenv
import os

def get_grouped_df():
    # Charger les variables d'environnement à partir du fichier .env
    load_dotenv()

    # Créer une connexion à la base de données
    connection = pyodbc.connect(f'DRIVER=ODBC Driver 18 for SQL Server;SERVER={os.getenv("DB_SERVER")};DATABASE={os.getenv("DB_DATABASE")};UID={os.getenv("DB_UID")};PWD={os.getenv("DB_PWD")}')

    # Exécuter une requête SQL avec JOIN pour récupérer les données souhaitées
    query = """
    SELECT f.title, f.entries, f.date, f.realisateur, f.budget, f.titre_non_modifie, f.film_id, 
           a.nom AS nom_acteur, c.nom AS nom_compagnie, g.nom AS nom_genre
    FROM films AS f
    LEFT JOIN films_acteurs AS fa ON f.film_id = fa.film_id
    LEFT JOIN acteurs AS a ON fa.acteur_id = a.acteur_id
    LEFT JOIN films_compagnies AS fc ON f.film_id = fc.film_id
    LEFT JOIN compagnies AS c ON fc.compagnie_id = c.compagnie_id
    LEFT JOIN films_genres AS fg ON f.film_id = fg.film_id
    LEFT JOIN genres AS g ON fg.genre_id = g.genre_id
    """
    df = pd.read_sql(query, connection)

    # Fermer la connexion
    connection.close()

    # Grouper les données par les colonnes que vous voulez garder uniques, ici je suppose que ce sont
    # 'title', 'entries', 'date', 'realisateur', 'budget', 'titre_non_modifie', 'film_id'
    grouped_df = df.groupby(['title', 'entries', 'date', 'realisateur', 'budget', 'titre_non_modifie', 'film_id']).agg({
        'nom_acteur': lambda x: ', '.join(x.dropna().unique()),
        'nom_compagnie': lambda x: ', '.join(x.dropna().unique()),
        'nom_genre': lambda x: ', '.join(x.dropna().unique()),
    }).reset_index()

    return grouped_df
