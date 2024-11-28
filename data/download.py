import gdown
import pandas as pd
import streamlit as st
from data.preprocess import load_and_preprocess

@st.cache_data
def download_data(url, output_path):
    """
    Télécharge et charge les données depuis une URL Google Drive.
    Les données sont mises en cache pour éviter les téléchargements multiples.
    """
    try:
        # Télécharger les données
        gdown.download(url, output_path, quiet=False)
        print(f"Données téléchargées avec succès à {output_path}")
        
        # Charger les données
        data = pd.read_excel(output_path)
        if data.empty:
            print(f"Le fichier {output_path} est vide ou corrompu.")
            return pd.DataFrame()
        
        # Prétraitement
        data = load_and_preprocess(data)
        print("Données chargées et prétraitées avec succès")
        return data
    except Exception as e:
        print(f"Erreur lors du téléchargement des données : {e}")
        return pd.DataFrame()
