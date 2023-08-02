from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd

def preprocess_data(df, mlb_actor, mlb_company, mlb_genre):
    # Utiliser les transformateurs chargés au lieu de les ajuster de nouveau
    df = df.join(pd.DataFrame(mlb_actor.transform(df.pop('nom_acteur')),
                              columns=[f'actor_{cls}' for cls in mlb_actor.classes_],
                              index=df.index))

    df = df.join(pd.DataFrame(mlb_company.transform(df.pop('nom_compagnie')),
                              columns=[f'company_{cls}' for cls in mlb_company.classes_],
                              index=df.index))

    df = df.join(pd.DataFrame(mlb_genre.transform(df.pop('nom_genre')),
                              columns=[f'genre_{cls}' for cls in mlb_genre.classes_],
                              index=df.index))

    # Remplir les valeurs manquantes par 0
    df = df.fillna(0)
    
    return df


