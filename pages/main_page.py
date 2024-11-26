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
        # Gestion des URL Google Drive
        if "drive.google.com" in file_url and "id=" in file_url:
            file_id = file_url.split("id=")[-1]
            file_url = f"https://drive.google.com/uc?id={file_id}"

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
    required_columns = ['Product Category', 'product_name', 'Date']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        st.error(f"Les colonnes suivantes sont manquantes dans les données : {', '.join(missing_columns)}")
        return

    # Sélection de la catégorie
    categories = data['Product Category'].unique()
    chosen_category = st.selectbox("Choisissez la catégorie pour l'analyse :", options=categories)

    # Filtrage des données par catégorie
    data_filtered = data[data['Product Category'] == chosen_category]

    if data_filtered.empty:
        st.error("Aucune donnée disponible pour cette catégorie.")
        return
    else:
        st.write("Transactions disponibles pour la catégorie :", len(data_filtered))

        # Récupérer les 30 produits les plus fréquents
        top_products = (
            data_filtered['product_name']
            .value_counts()
            .nlargest(30)
            .sort_index()
            .index.tolist()
        )
        chosen_product = st.selectbox("Choisissez un produit à analyser :", options=top_products)

        # Groupement des transactions par date
        transactions = data_filtered.groupby('Date')['product_name'].apply(lambda x: list(map(str, x))).tolist()
        st.write("Exemple de transactions :", transactions[:5])  # Diagnostic

        # Lancer l'analyse lorsque l'utilisateur clique sur le bouton
        if st.button("Lancer l'analyse"):
            rules = fpgrowth_rules(transactions, min_support=0.01, min_confidence=0.5)
            st.write("Règles générées :", rules)  # Diagnostic

            # Filtrer les règles contenant uniquement un antécédent unique
            rules_filtered = rules[
                (rules['antecedents'] == chosen_product)
            ]

            if rules_filtered.empty:
                st.warning(f"Aucune règle trouvée pour le produit {chosen_product}.")
            else:
                st.write(f"Règles trouvées pour le produit {chosen_product} :")
                st.dataframe(rules_filtered)
