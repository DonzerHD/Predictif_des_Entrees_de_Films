from django.db import models
import requests
from datetime import datetime

class Utilisateurs(models.Model):

    class Meta:
        managed = False
        db_table = 'Utilisateurs'

class UpcomingMovie(models.Model):
    """
    Modèle représentant un film à venir.

    Attributs:
        titre_fr (CharField): Titre du film en français.
        realisateur (CharField): Nom du réalisateur du film.
        acteurs (TextField): Liste des principaux acteurs du film.
        genres (TextField): Genres du film.
        budget (PositiveIntegerField): Budget du film.
        date_sortie (DateField): Date de sortie du film.
        compagnies_production (TextField): Compagnies qui ont produit le film.
        titre_non_modifie (CharField): Titre original du film (non traduit).
        affiche (CharField): URL de l'affiche du film.
        entree_predit (PositiveIntegerField): Prédictions d'entrées pour le film.

    Note:
        Ce modèle est utilisé pour stocker des informations sur les films à venir
        et leurs prédictions d'entrées potentielles.
    """
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
        """
        Crée une instance d'UpcomingMovie à partir des données fournies par l'API TMDB.
        
        Cette méthode statique prend en compte les informations principales d'un film 
        telles que le titre, les acteurs, le réalisateur, les genres, le budget, la date de sortie, 
        les compagnies de production et l'affiche pour créer une instance d'UpcomingMovie.
        
        Args:
            movie (dict): Un dictionnaire contenant les informations principales du film provenant de TMDB.
            movie_details (dict): Un dictionnaire contenant des détails supplémentaires sur le film.
            credits (dict): Un dictionnaire contenant les informations sur les acteurs et l'équipe du film.
            
        Returns:
            UpcomingMovie: Une instance d'UpcomingMovie avec toutes les informations pertinentes du film.
        """
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
        """
        Prédit le nombre d'entrées pour un film à l'aide d'une API externe.
        
        Cette méthode prend les informations principales de l'instance d'UpcomingMovie, 
        puis elle envoie ces informations à une API FAST_API pour obtenir une prédiction 
        sur le nombre d'entrées. Une fois la prédiction obtenue, elle met à jour 
        l'attribut 'entree_predit' de l'instance avec la valeur prédite et sauvegarde l'instance.
        
        Utilise une requête POST vers FAST_API_URL pour obtenir la prédiction.
        
        Si une erreur HTTP se produit lors de la demande à l'API, elle sera affichée.
        De même, pour les autres types d'erreurs.
        
        Note:
            L'API doit renvoyer un JSON avec une clé "prediction" contenant la valeur prédite.
        
        Attributes:
            entree_predit (int): Le nombre d'entrées prédit pour le film.
        """
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

    def get_predicted_local_entries(self):
        """
        Calcule et retourne les entrées locales prévues pour le film.

        Cette méthode convertit les entrées nationales prédites en entrées locales 
        en utilisant un facteur de conversion fixe (1/2000). Cela représente le 
        ratio des entrées locales par rapport aux entrées nationales.

        Returns:
            int: Le nombre arrondi d'entrées locales prévues pour le film.
        """
        national_entries_predicted = self.entree_predit
        local_entries = national_entries_predicted * 1/2000
        return round(local_entries)
    
    