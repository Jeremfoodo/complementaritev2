import streamlit as st
from data.download import download_data, download_segmentation_data
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def segmentation_page():
    st.title("Segmentation des Clients")
    
    segmentation_url = 'https://docs.google.com/spreadsheets/d/1lkxXgC095L0OQdItsGYtisZqVk_nXkPa/export?format=xlsx'
    segmentation_output_path = 'segmentationFR.xlsx'
    
    try:
        segmentation_data = download_segmentation_data(segmentation_url, segmentation_output_path)
    except Exception as e:
        st.error(f"Erreur lors du téléchargement des données de segmentation : {e}")
        return

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

        try:
            france_data = download_data(file_urls['France'], output_paths['France'])
        except Exception as e:
            st.error(f"Erreur lors du téléchargement des données de France : {e}")
            return

        france_data['Date'] = pd.to_datetime(france_data['Date'], errors='coerce')

        st.write("Colonnes dans france_data avant filtrage:", france_data.columns)
        st.write("Colonnes dans segmentation_data:", segmentation_data.columns)

        if selected_zone != 'Toute France':
            if 'region' in france_data.columns:
                france_data = france_data[france_data['region'] == selected_zone]
            else:
                st.error(f"La colonne 'region' n'existe pas dans france_data")
                return

        if selected_category != 'Toutes catégories':
            st.write("Filtrage par catégorie:", selected_category)
            if 'Product Category' in france_data.columns:
                france_data = france_data[france_data['Product Category'] == selected_category]
            else:
                st.error(f"La colonne 'Product Category' n'existe pas dans france_data")
                return

        st.write("Colonnes dans france_data après filtrage:", france_data.columns)

        if selected_month == 'avril':
            france_data = france_data[france_data['Date'].dt.month == 4]
        elif selected_month == 'mai':
            france_data = france_data[france_data['Date'].dt.month == 5]
        elif selected_month == 'juin':
            france_data = france_data[france_data['Date'].dt.month == 6]
        elif selected_month == '3 last month':
            france_data = france_data[france_data['Date'].dt.month.isin([4, 5, 6])]

        st.write("Colonnes dans france_data avant fusion:", france_data.columns)
        st.write("Échantillon de france_data:", france_data.head())
        st.write("Échantillon de segmentation_data:", segmentation_data.head())

        # Renommer les colonnes pour éviter les conflits
        france_data = france_data.rename(columns={'Restaurant_id': 'france_Restaurant_id'})
        segmentation_data = segmentation_data.rename(columns={'Restaurant_id': 'segment_Restaurant_id'})

        st.write("Colonnes dans france_data après renommage:", france_data.columns)
        st.write("Colonnes dans segmentation_data après renommage:", segmentation_data.columns)

        if 'france_Restaurant_id' in france_data.columns and 'segment_Restaurant_id' in segmentation_data.columns:
            try:
                merged_data = france_data.merge(segmentation_data, left_on='france_Restaurant_id', right_on='segment_Restaurant_id')
                st.write("Colonnes dans merged_data après fusion:", merged_data.columns)
                st.write("Échantillon de merged_data:", merged_data.head())
            except Exception as e:
                st.error(f"Erreur lors de la fusion des données : {e}")
                return
        else:
            st.error("Les colonnes 'france_Restaurant_id' ou 'segment_Restaurant_id' n'existent pas dans l'un des DataFrames pour la fusion")
            return

        if not merged_data.empty:
            segment_counts = merged_data.groupby(['Gamme', 'Type']).size().unstack(fill_value=0)

            plt.figure(figsize=(10, 6))
            sns.heatmap(segment_counts, annot=True, fmt="d", cmap="YlGnBu")
            plt.title("Heatmap du nombre de clients pour chaque segment")
            plt.xlabel("Type")
            plt.ylabel("Gamme")
            st.pyplot(plt)
        else:
            st.error("Les données fusionnées sont vides. Vérifiez les filtres appliqués.")
