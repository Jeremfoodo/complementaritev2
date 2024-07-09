import gdown
import pandas as pd

def download_data(url, output_path):
    try:
        gdown.download(url, output_path, quiet=False)
        return load_and_preprocess(output_path)
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
