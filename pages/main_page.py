import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from utils.apriori_analysis import fpgrowth_rules

def download_data(file_url):
    """
    Télécharge un fichier depuis une URL Google Drive et retourne un DataFrame.
    """
    try:
        response = requests.get(file_url)
        response.raise_for_status()
        file_data = BytesIO(response.content)
        data = pd.read_excel(file_data)
        return data
    except Exception as e:
        st.error(f"Erreur lors du téléchargement des données : {e}")
        return pd.DataFrame()

def main_page():
    st.title("Analyse de Produits Complémentaires")

    # URLs des fichiers par pays
    file_urls = {
        'FR': 'https://drive.google.com/uc?id=1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA',
        'Belgium': 'https://drive.google.com/uc?id=1fqu_YgsovkDrpqV7OsFStusEvM-9axRg',
        'UK': 'https://drive.google.com/uc?id=1ROT0ide8EQfgcWpXMY6Qnyp5nMKoLt-a',
        'US': 'https://drive.google.com/uc?id=1HsxBxGpq3lSwJKPALDsDNvJXNi6us2j-'
    }

    # Sélection du pays
    user_country = st.selectbox("Choisissez le pays à analyser :", options=list(file_urls.keys()))

    st.write(f"Téléchargement des données pour {user_country}...")
    file_url = file_urls[user_country]

    # Téléchargement et chargement des données
    data = download_data(file_url)

    # Vérification des données
    if data.empty:
        st.error("Les données n'ont pas été correctement chargées pour ce pays.")
        return

    st.write("Données chargées :", data.head())

    # Vérification des colonnes nécessaires
    if 'Product Category' not in data.columns or 'product_name' not in data.columns:
        st.error("Colonnes nécessaires manquantes dans les données.")
        return

    # Sélection de la catégorie
    categories = data['Product Category'].unique()
    chosen_category = st.selectbox("Choisissez la catégorie pour l'analyse :", options=categories)

    # Filtrage des données
    data_filtered = data[data['Product Category'] == chosen_category]

    if data_filtered.empty:
        st.error("Aucune donnée disponible pour cette catégorie.")
        return
    else:
        st.write("Transactions disponibles :", len(data_filtered))

        # Groupement des transactions par date
        transactions = data_filtered.groupby('Date')['product_name'].apply(list).tolist()

        # Lancer l'analyse lorsque l'utilisateur clique sur le bouton
        if st.button("Lancer l'analyse"):
            rules = fpgrowth_rules(transactions, min_support=0.02, min_confidence=0.5)

            # Affichage des résultats
            if rules.empty:
                st.warning("Aucune règle trouvée avec les paramètres actuels.")
            else:
                st.write("Règles trouvées :")
                st.dataframe(rules)

