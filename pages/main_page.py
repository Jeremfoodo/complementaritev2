import streamlit as st
import pandas as pd
import gdown

@st.cache_data
def load_data(url):
    """
    Télécharge les données depuis une URL Google Drive, les charge dans un DataFrame et les met en cache.
    """
    try:
        # Téléchargement du fichier
        output_path = "data.xlsx"
        gdown.download(url, output_path, quiet=False)

        # Chargement des données
        data = pd.read_excel(output_path)
        
        # Vérification si les données sont vides
        if data.empty:
            return None, "Le fichier est vide ou ne contient pas de données exploitables."
        
        return data, None  # Aucun problème
    except Exception as e:
        return None, f"Erreur lors du téléchargement ou du chargement des données : {e}"

def main_page():
    st.title("Analyse des données - Page principale")

    # URL à tester
    url = st.text_input(
        "Entrez l'URL Google Drive du fichier :",
        value="https://drive.google.com/uc?id=1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA"
    )

    if st.button("Charger les données"):
        st.write("Tentative de chargement des données...")
        st.write(f"URL utilisée pour le téléchargement : {url}")
        
        # Appel de la fonction pour charger les données
        data, error_message = load_data(url)
        
        if error_message:
            st.error(error_message)
        else:
            st.success("Les données ont été chargées avec succès !")
            st.write(data.head())  # Affiche les premières lignes du DataFrame
