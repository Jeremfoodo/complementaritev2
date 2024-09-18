import gdown
import pandas as pd
from data.preprocess import load_and_preprocess
import openpyxl

def download_data(url, output_path):
    try:
        gdown.download(url, output_path, quiet=False)
        print(f"Données téléchargées avec succès à {output_path}")
        
        # Vérifier si le fichier existe et n'est pas vide
        if pd.read_excel(output_path).empty:
            print(f"Le fichier {output_path} est vide ou corrompu.")
            return pd.DataFrame()
        
        data = load_and_preprocess(output_path)
        print("Données chargées et prétraitées avec succès")
        return data
    except Exception as e:
        print(f"Erreur lors du téléchargement des données : {e}")
        return pd.DataFrame()

def download_segmentation_data(url, output_path):
    try:
        gdown.download(url, output_path, quiet=False)
        return pd.read_excel(output_path)
    except Exception as e:
        print(f"Erreur lors du téléchargement des données de segmentation : {e}")
        return pd.DataFrame()
