import streamlit as st
from data.download import download_data, download_segmentation_data
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Fonction avec cache pour éviter de télécharger plusieurs fois
@st.cache_data
def get_segmentation_data(segmentation_url, segmentation_output_path):
    return download_segmentation_data(segmentation_url, segmentation_output_path)

@st.cache_data
def get_country_data(file_url, output_path):
    return download_data(file_url, output_path)

def segmentation_page():
    st.title("Segmentation des Clients")
    
    # Nouveau lien de téléchargement des données de segmentation
    segmentation_url = 'https://docs.google.com/spreadsheets/d/1Vv7n3pj3J7xDbsizmdWyw2ZF3oVQNBfu/export?format=xlsx'
    segmentation_output_path = 'segmentation_all.xlsx'
    
    # Téléchargement des données de segmentation (utilisation du cache)
    segmentation_data = get_segmentation_data(segmentation_url, segmentation_output_path)

    # Liste des pays disponibles
    countries = ['France', 'Belgique', 'US', 'UK']
    selected_country = st.selectbox("Choisissez le pays :", options=countries)

    # Zones disponibles
    zones = ['Toute France', 'Paris', 'Paris EST', 'Paris Ouest', 'Province']
    selected_zone = st.selectbox("Choisissez la zone :", options=zones)
    
    # Catégories de produits disponibles
    categories = ['Fruits et Légumes', 'Boucherie', 'Epicerie salée', 'Crémerie', 'Toutes catégories']
    selected_category = st.selectbox("Choisissez la catégorie :", options=categories)
    
    # Générer la liste des mois disponibles dynamiquement
    months = pd.date_range(start="2024-01", end=pd.Timestamp.now(), freq='M').strftime('%B %Y').tolist()
    months.extend(['3 derniers mois', 'Toute la base'])
    selected_month = st.selectbox("Choisissez le mois :", options=months)

    if st.button("Lancer l'analyse"):
        # Lien de téléchargement des données pour chaque pays
        file_urls = {
            'France': 'https://docs.google.com/spreadsheets/d/1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA/export?format=xlsx',
            'Belgique': 'https://docs.google.com/spreadsheets/d/1fqu_YgsovkDrpqV7OsFStusEvM-9axRg/export?format=xlsx',
            'US': 'https://docs.google.com/spreadsheets/d/1HsxBxGpq3lSwJKPALDsDNvJXNi6us2j-/export?format=xlsx',
            'UK': 'https://docs.google.com/spreadsheets/d/1ROT0ide8EQfgcWpXMY6Qnyp5nMKoLt-a/export?format=xlsx'
        }
        output_paths = {
            'France': 'dataFR.xlsx',
            'Belgique': 'dataBE.xlsx',
            'US': 'dataUS.xlsx',
            'UK': 'dataUK.xlsx'
        }
        
        # Téléchargement des données pour le pays sélectionné (utilisation du cache)
        country_data = get_country_data(file_urls[selected_country], output_paths[selected_country])
        country_data['Date'] = pd.to_datetime(country_data['Date'], errors='coerce')

        # Filtrage par zone et catégorie si nécessaire
        if selected_zone != 'Toute France':
            country_data = country_data[country_data['region'] == selected_zone]
        if selected_category != 'Toutes catégories':
            country_data = country_data[country_data['Product Category'] == selected_category]
        
        # Filtrage par mois
        if selected_month not in ['3 derniers mois', 'Toute la base']:
            selected_month_num = pd.to_datetime(selected_month, format='%B %Y').month
            country_data = country_data[country_data['Date'].dt.month == selected_month_num]
        elif selected_month == '3 derniers mois':
            available_months = country_data['Date'].dt.month.unique()
            country_data = country_data[country_data['Date'].dt.month.isin(sorted(available_months)[-3:])]

        # Fusion des données avec la segmentation
        merged_data = country_data.merge(segmentation_data, left_on='Restaurant_id', right_on='Restaurant_id')

        # Ne garder que les clients uniques
        unique_clients_data = merged_data.drop_duplicates(subset=['Restaurant_id'])

        # Comptage des segments basés sur les clients uniques
        segment_counts = unique_clients_data.groupby(['Gamme', 'Type']).size().unstack(fill_value=0)

        # Génération d'un heatmap pour afficher les segments
        plt.figure(figsize=(10, 6))
        sns.heatmap(segment_counts, annot=True, fmt="d", cmap="YlGnBu")
        plt.title("Heatmap du nombre de clients uniques pour chaque segment")
        plt.xlabel("Type")
        plt.ylabel("Gamme")
        st.pyplot(plt)


# Assurez-vous d'exécuter la fonction pour afficher la page de segmentation
if __name__ == '__main__':
    segmentation_page()
