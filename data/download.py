import gdown
import pandas as pd
import streamlit as st
from data.preprocess import load_and_preprocess

import tempfile

@st.cache_data
def download_data(url):
    """
    Télécharge et charge les données depuis une URL Google Drive.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            gdown.download(url, tmp_file.name, quiet=False)
            print(f"Données téléchargées temporairement à {tmp_file.name}")
            
            # Charger les données
            data = pd.read_excel(tmp_file.name)
            
            if data.empty:
                print("Le fichier téléchargé est vide ou corrompu.")
                return pd.DataFrame()
            
            print("Données chargées avec succès")
            return data
    except Exception as e:
        print(f"Erreur lors du téléchargement ou du chargement des données : {e}")
        return pd.DataFrame()


import gdown
import pandas as pd
import streamlit as st

@st.cache_data
def download_segmentation_data(url, output_path):
    """
    Télécharge et charge les données de segmentation depuis une URL.
    """
    try:
        # Télécharger le fichier
        gdown.download(url, output_path, quiet=False)
        print(f"Données de segmentation téléchargées avec succès à {output_path}")
        
        # Charger les données
        data = pd.read_excel(output_path)
        return data
    except Exception as e:
        print(f"Erreur lors du téléchargement des données de segmentation : {e}")
        return pd.DataFrame()
