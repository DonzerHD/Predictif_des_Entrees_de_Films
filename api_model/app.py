from fastapi import FastAPI
import joblib
import pandas as pd
from utils import preprocess_data
from typing import List
from pydantic import BaseModel

class FilmData(BaseModel):
    titre_fr: str
    realisateur: str
    acteurs: List[str]
    genres: List[str]
    budget: int
    date_sortie: str
    compagnies_production: List[str]
    titre_non_modifie: str

app = FastAPI()

# Charger le modèle
model_path = "model.pkl"  # Remplacez par le chemin correct vers votre fichier .pkl
model = joblib.load(model_path)

# Charger les transformations
mlb_actor = joblib.load('mlb_actor.pkl')
mlb_company = joblib.load('mlb_company.pkl')
mlb_genre = joblib.load('mlb_genre.pkl')
@app.post("/predict")
async def predict(film: FilmData):
# Convertir les données Pydantic en DataFrame
    data = {
        'realisateur': film.realisateur,
        'budget': film.budget,
        'titre_non_modifie': film.titre_non_modifie,
        'nom_acteur': film.acteurs,
        'nom_genre': film.genres,
        'nom_compagnie': film.compagnies_production,
    }
    df = pd.DataFrame([data])

    # Prétraiter les données
    df = preprocess_data(df, mlb_actor, mlb_company, mlb_genre)

    # Utiliser le modèle pour faire une prédiction
    prediction = model.predict(df)


    # Retourner les prédictions sous forme de réponse JSON ou comme vous le souhaitez
    return {"prediction": prediction.tolist()}
