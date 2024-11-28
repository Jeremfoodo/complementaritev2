import streamlit as st
from data.download import download_data, download_segmentation_data
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

@st.cache_data
def get_segmentation_data(url, output_path):
    return download_segmentation_data(url, output_path)

@st.cache_data
def get_country_data(file_url, output_path):
    return download_data(file_url, output_path)

def segmentation_page():
    st.title("Segmentation des Clients")

    segmentation_url = 'https://drive.google.com/uc?id=1Vv7n3pj3J7xDbsizmdWyw2ZF3oVQNBfu'
    segmentation_output_path = 'segmentation_all.xlsx'

    segmentation_data = get_segmentation_data(segmentation_url, segmentation_output_path)

    countries = ['France', 'Belgique', 'US', 'UK']
    selected_country = st.selectbox("Choisissez le pays :", options=countries)

    zones = ['Toute France', 'Paris', 'Paris EST', 'Paris Ouest', 'Province']
    selected_zone = st.selectbox("Choisissez la zone :", options=zones)

    categories = ['Fruits et Légumes', 'Boucherie', 'Epicerie salée', 'Crémerie', 'Toutes catégories']
    selected_category = st.selectbox("Choisissez une catégorie :", options=categories)

    # Lancer l'analyse
    if st.button("Lancer l'analyse"):
        file_urls = {
            'France': 'https://drive.google.com/uc?id=1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA',
            'Belgique': 'https://drive.google.com/uc?id=1fqu_YgsovkDrpqV7OsFStusEvM-9axRg',
            'US': 'https://drive.google.com/uc?id=1HsxBxGpq3lSwJKPALDsDNvJXNi6us2j-',
            'UK': 'https://drive.google.com/uc?id=1ROT0ide8EQfgcWpXMY6Qnyp5nMKoLt-a'
        }
        country_data = get_country_data(file_urls[selected_country], f"{selected_country}_data.xlsx")
        country_data['Date'] = pd.to_datetime(country_data['Date'], errors='coerce')

        if selected_zone != 'Toute France':
            country_data = country_data[country_data['region'] == selected_zone]
        if selected_category != 'Toutes catégories':
            country_data = country_data[country_data['Product Category'] == selected_category]

        merged_data = country_data.merge(segmentation_data, on='Restaurant_id')
        unique_clients_data = merged_data.drop_duplicates(subset=['Restaurant_id'])

        segment_counts = unique_clients_data.groupby(['Gamme', 'Type']).size().unstack(fill_value=0)

        # Heatmap
        plt.figure(figsize=(10, 6))
        sns.heatmap(segment_counts, annot=True, fmt="d", cmap="YlGnBu")
        plt.title("Heatmap des segments de clients")
        plt.xlabel("Type")
        plt.ylabel("Gamme")
        st.pyplot(plt)
