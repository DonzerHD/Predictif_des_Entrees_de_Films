from django.db import models
import requests
from datetime import datetime

class Utilisateurs(models.Model):

    class Meta:
        managed = False
        db_table = 'Utilisateurs'

class UpcomingMovie(models.Model):
    titre_fr = models.CharField(max_length=200)
    realisateur = models.CharField(max_length=200)
    acteurs = models.TextField()
    genres = models.TextField()
    budget = models.PositiveIntegerField()
    date_sortie = models.DateField()
    compagnies_production = models.TextField()
    titre_non_modifie = models.CharField(max_length=200)
    affiche = models.CharField(max_length=500, blank=True, null=True)
    entree_predit = models.PositiveIntegerField(null=True, blank=True)

    @staticmethod
    def from_tmdb_data(movie, movie_details, credits):
        actors = [actor['name'] for actor in credits['cast'] if actor['order'] <= 3]
        directors = [crew_member['name'] for crew_member in credits['crew'] if crew_member['job'] == 'Director']

        release_date = datetime.strptime(movie['release_date'], '%Y-%m-%d').date()

        instance = UpcomingMovie(
            titre_fr=movie['title'],
            realisateur=", ".join(directors),
            acteurs=", ".join(actors),  
            genres=", ".join([genre['name'] for genre in movie_details['genres']]),  
            budget=movie_details['budget'],
            date_sortie=release_date,
            compagnies_production=", ".join([company['name'] for company in movie_details['production_companies']]), 
            titre_non_modifie=movie['original_title'],
            affiche=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None,
        )
        return instance

    def predict_entries(self):
        data = {
            "titre_fr": self.titre_fr,
            "realisateur": self.realisateur,
            "acteurs": self.acteurs.split(", "),
            "genres": self.genres.split(", "),
            "budget": self.budget,
            "date_sortie": self.date_sortie.strftime('%Y-%m-%d'),
            "compagnies_production": self.compagnies_production.split(", "),
            "titre_non_modifie": self.titre_non_modifie
        }

        FAST_API_URL = "http://20.19.144.195:8000/predict"
        try:
            response = requests.post(FAST_API_URL, json=data, timeout=10)

            response.raise_for_status()  
            prediction = response.json()
            self.entree_predit = prediction.get("prediction")[0] if prediction.get("prediction") else None
            self.save()

        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")
