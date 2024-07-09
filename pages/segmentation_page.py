import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import gdown

def segmentation_page():
    st.title("Segmentation des Clients")

    # URLs des fichiers Google Drive
    segmentation_url = 'https://docs.google.com/spreadsheets/d/1lkxXgC095L0OQdItsGYtisZqVk_nXkPa/export?format=xlsx'
    achats_url = 'https://docs.google.com/spreadsheets/d/1_qfuH19aLu3JMocit2-wSL-FCmWNet1I/export?format=xlsx'

    # Chemins des fichiers téléchargés
    segmentation_output_path = 'segmentationFR.xlsx'
    achats_output_path = 'dataFR.xlsx'

    # Télécharger les données de segmentation
    gdown.download(segmentation_url, segmentation_output_path, quiet=False)

    # Télécharger les données d'achats
    gdown.download(achats_url, achats_output_path, quiet=False)

    # Charger les données de segmentation
    segmentation_data = pd.read_excel(segmentation_output_path)

    # Charger les données d'achats
    achats_data = pd.read_excel(achats_output_path, sheet_name='Export')
    achats_data['Date'] = pd.to_datetime(achats_data['Date'], errors='coerce')

    # Sélections interactives
    zones = ['Toute France', 'Paris', 'Paris EST', 'Paris Ouest', 'Province']
    selected_zone = st.selectbox("Choisissez la zone :", options=zones)

    categories = ['Fruits et Légumes', 'Boucherie', 'Epicerie salée', 'Crémerie', 'Toutes catégories']
    selected_category = st.selectbox("Choisissez la catégorie :", options=categories)

    months = ['janvier', 'février', 'mars', 'avril', '3 last month']
    selected_month = st.selectbox("Choisissez le mois :", options=months)

    if st.button("Lancer l'analyse"):
        # Filtrer les données d'achats
        if selected_zone != 'Toute France':
            achats_data = achats_data[achats_data['region'] == selected_zone]

        if selected_category != 'Toutes catégories':
            achats_data = achats_data[achats_data['Product Category'] == selected_category]

        if selected_month == 'janvier':
            achats_data = achats_data[achats_data['Date'].dt.month == 1]
        elif selected_month == 'février':
            achats_data = achats_data[achats_data['Date'].dt.month == 2]
        elif selected_month == 'mars':
            achats_data = achats_data[achats_data['Date'].dt.month == 3]
        elif selected_month == 'avril':
            achats_data = achats_data[achats_data['Date'].dt.month == 4]
        elif selected_month == '3 last month':
            achats_data = achats_data[achats_data['Date'].dt.month.isin([1, 2, 3, 4])]

        # Fusionner les données d'achats avec les données de segmentation
        data_merged = pd.merge(achats_data, segmentation_data, on='Restaurant_id', how='left')

        # Renommer les valeurs de gamme pour une meilleure lisibilité
        gamme_mapping = {1: 'à emporter', 2: 'regular', 3: 'chic'}
        data_merged['Gamme'] = data_merged['Gamme'].replace(gamme_mapping)

        # Préparer les données pour les heatmaps
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))  # Inclure 3 heatmaps

        # Nombre de clients par segment
        clients_par_segment = data_merged.groupby(['Gamme', 'Type'])['Restaurant_id'].nunique()
        sns.heatmap(clients_par_segment.unstack(fill_value=0), annot=True, fmt="d", cmap='Blues', cbar_kws={'label': 'Nombre de Clients'},
                    linecolor='black', linewidths=.5, ax=axes[0])
        axes[0].set_title('Nombre de Clients par Segment')
        axes[0].set_xlabel('Type de Cuisine')
        axes[0].set_ylabel('Gamme')

        # Pourcentage de clients par segment
        total_clients = data_merged['Restaurant_id'].nunique()
        pourcentage_clients_par_segment = (clients_par_segment / total_clients * 100).fillna(0)
        sns.heatmap(pourcentage_clients_par_segment.unstack(fill_value=0), annot=True, fmt=".0f", cmap='Greens', cbar_kws={'label': '% du Total de Clients'},
                    linecolor='black', linewidths=.5, ax=axes[1])
        axes[1].set_title('% de Clients par Segment')
        axes[1].set_xlabel('Type de Cuisine')
        axes[1].set_ylabel('Gamme')

        # GMV totale par segment
        gmv_par_segment = data_merged.groupby(['Gamme', 'Type'])['GMV WITH TAX'].sum().fillna(0).round(0).astype(int)
        sns.heatmap(gmv_par_segment.unstack(fill_value=0), annot=True, fmt="d", cmap='Reds', cbar_kws={'label': 'GMV Totale par Segment'},
                    linecolor='black', linewidths=.5, ax=axes[2])
        axes[2].set_title('GMV Totale par Segment')
        axes[2].set_xlabel('Type de Cuisine')
        axes[2].set_ylabel('Gamme')

        # Afficher le texte
        st.markdown('<h1 style="font-size: 16px;"><br> Heatmap montrant au global le nombre de clients que nous avons et leur GMV en France . </h1>', unsafe_allow_html=True)
        st.markdown('<h1 style="font-size: 12px;"> <br>A noter, ces données sont pour le moment uniquement basées sur les clients actifs en Janvier à Paris, Province et Paris Ouest. Les données de Paris Est seront bientot ajoutées. Cela n\'empeche que les pourcentages sont assez représentatifs . </h1>', unsafe_allow_html=True)

        plt.tight_layout()
        st.pyplot(fig)
