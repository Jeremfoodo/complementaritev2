import streamlit as st
from data.download import download_data, download_segmentation_data
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def segmentation_page():
    st.title("Segmentation des Clients")
    
    segmentation_url = 'https://docs.google.com/spreadsheets/d/1lkxXgC095L0OQdItsGYtisZqVk_nXkPa/export?format=xlsx'
    segmentation_output_path = 'segmentationFR.xlsx'
    segmentation_data = download_segmentation_data(segmentation_url, segmentation_output_path)

    zones = ['Toute France', 'Paris', 'Paris EST', 'Paris Ouest', 'Province']
    selected_zone = st.selectbox("Choisissez la zone :", options=zones)

    categories = ['Fruits et Légumes', 'Boucherie', 'Epicerie salée', 'Crémerie', 'Toutes catégories']
    selected_category = st.selectbox("Choisissez la catégorie :", options=categories)

    months = ['avril', 'mai', 'juin', '3 last month']
    selected_month = st.selectbox("Choisissez le mois :", options=months)

    if st.button("Lancer l'analyse"):
        file_urls = {
            'France': 'https://docs.google.com/spreadsheets/d/1_qfuH19aLu3JMocit2-wSL-FCmWNet1I/export?format=xlsx'
        }
        output_paths = {
            'France': 'dataFR.xlsx'
        }

        france_data = download_data(file_urls['France'], output_paths['France'])
        france_data['Date'] = pd.to_datetime(france_data['Date'], errors='coerce')

        st.write("Colonnes dans france_data:", france_data.columns)
        st.write("Colonnes dans segmentation_data:", segmentation_data.columns)

        if selected_zone != 'Toute France':
            france_data = france_data[france_data['region'] == selected_zone]

        if selected_category != 'Toutes catégories':
            france_data = france_data[france_data['Product Category'] == selected_category]

        if selected_month == 'avril':
            france_data = france_data[france_data['Date'].dt.month == 4]
        elif selected_month == 'mai':
            france_data = france_data[france_data['Date'].dt.month == 5]
        elif selected_month == 'juin':
            france_data = france_data[france_data['Date'].dt.month == 6]
        elif selected_month == '3 last month':
            france_data = france_data[france_data['Date'].dt.month.isin([4, 5, 6])]

        # Corrigez les colonnes pour la fusion
        merged_data = france_data.merge(segmentation_data, on='Restaurant_id')

        segment_counts = merged_data.groupby(['Gamme', 'Type']).size().unstack(fill_value=0)

        plt.figure(figsize=(10, 6))
        sns.heatmap(segment_counts, annot=True, fmt="d", cmap="YlGnBu")
        plt.title("Heatmap du nombre de clients pour chaque segment")
        plt.xlabel("Type")
        plt.ylabel("Gamme")
        st.pyplot(plt)
