import streamlit as st
from utils.apriori_analysis import fpgrowth_rules
import pandas as pd

def main_page():
    st.title("Analyse de Produits Complémentaires")

    file_urls = {
        'FR': 'https://drive.google.com/uc?id=1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA',
        'Belgium': 'https://drive.google.com/uc?id=1fqu_YgsovkDrpqV7OsFStusEvM-9axRg',
        'UK': 'https://drive.google.com/uc?id=1ROT0ide8EQfgcWpXMY6Qnyp5nMKoLt-a',
        'US': 'https://drive.google.com/uc?id=1HsxBxGpq3lSwJKPALDsDNvJXNi6us2j-'
    }

    output_paths = {
        'FR': 'dataFR.xlsx',
        'Belgium': 'dataBE.xlsx',
        'UK': 'dataUK.xlsx',
        'US': 'dataUS.xlsx'
    }

    user_country = st.selectbox("Choisissez le pays à analyser :", options=list(file_urls.keys()))

    file_url = file_urls[user_country]
    output_path = output_paths[user_country]

    st.write(f"Téléchargement des données pour {user_country}...")
    data = pd.read_excel(file_url)  # Simplifié pour cet exemple

    if data.empty:
        st.error("Les données n'ont pas été correctement chargées pour ce pays.")
        return

    st.write("Données chargées :", data.head())

    if 'Product Category' not in data.columns or 'product_name' not in data.columns:
        st.error("Colonnes nécessaires manquantes dans les données.")
        return

    categories = data['Product Category'].unique()
    chosen_category = st.selectbox("Choisissez la catégorie pour l'analyse :", options=categories)

    data_filtered = data[data['Product Category'] == chosen_category]

    if data_filtered.empty:
        st.error("Aucune donnée disponible pour cette catégorie.")
    else:
        st.write("Transactions disponibles :", len(data_filtered))

        transactions = data_filtered.groupby('Date')['product_name'].apply(list).tolist()

        if st.button("Lancer l'analyse"):
            rules = fpgrowth_rules(transactions, min_support=0.02, min_confidence=0.5)

            if rules.empty:
                st.warning("Aucune règle trouvée avec les paramètres actuels.")
            else:
                st.dataframe(rules)
