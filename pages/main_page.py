import streamlit as st
from data.download import download_data
from data.preprocess import load_and_preprocess, process_data
from utils.apriori_analysis import apriori_rules
import pandas as pd
import openpyxl

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
    data = download_data(file_url, output_path)

    # Vérification si les données ont bien été chargées
    if data.empty:
        st.error("Les données n'ont pas été correctement chargées pour ce pays.")
        return
    
    st.write("Données chargées :", data.head())

    # Vérification des colonnes obligatoires
    required_columns = ['region', 'Product Category', 'product_name']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        st.error(f"Les colonnes suivantes sont manquantes : {', '.join(missing_columns)}")
        return

    if user_country in ['FR', 'US']:
        zone_mappings = {
            'FR': ['Toute France', 'Paris', 'Paris EST', 'Paris Ouest', 'Province'],
            'US': ['All US', 'CA', 'NY']
        }
        user_region = st.selectbox("Choisissez la région à analyser :", options=zone_mappings[user_country])
        if user_region in ['Toute France', 'All US']:
            data_region_selected = data
        else:
            data_region_selected = data[data['region'] == user_region]
    else:
        user_region = user_country
        data_region_selected = data

    st.write("Données pour la région sélectionnée :", data_region_selected.head())

    if data_region_selected.empty:
        st.error("Aucune donnée disponible pour cette région.")
    else:
        categories = data_region_selected['Product Category'].unique()
        chosen_category = st.selectbox("Choisissez la catégorie pour l'analyse :", options=categories)

        top_products = data_region_selected[data_region_selected['Product Category'] == chosen_category]['product_name'].value_counts().index.tolist()
        if not top_products:
            st.error("Aucun produit disponible pour cette catégorie.")
        else:
            chosen_product = st.selectbox("Choisissez le produit pour l'analyse :", options=top_products)

            if st.button("Lancer l'analyse"):
                category_data = data_region_selected[data_region_selected['Product Category'] == chosen_category].copy()
                assert 'Date' in category_data.columns, "La colonne 'Date' n'est pas dans category_data"
                transactions = process_data(category_data)
                rules = apriori_rules(transactions)
                
                # Prétraitement des règles pour affichage
                rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x))
                rules['consequents'] = rules['consequents'].apply(lambda x: list(x))
                rules_single = rules[(rules['antecedents'].apply(len) == 1) & (rules['consequents'].apply(len) == 1)]
                rules_single['antecedents'] = rules_single['antecedents'].apply(lambda x: ', '.join(x))
                rules_single['consequents'] = rules_single['consequents'].apply(lambda x: ', '.join(x))
                rules_single[['antecedent support', 'consequent support', 'support', 'confidence', 'lift', 'leverage', 'conviction']] = \
                    rules_single[['antecedent support', 'consequent support', 'support', 'confidence', 'lift', 'leverage', 'conviction']].round(2)
                rules_high_support = rules_single[rules_single['antecedent support'] > 0.1]
                rules_chosen_product = rules_single[rules_single['antecedents'] == chosen_product]
                
                # Affichage des règles
                columns_to_display = ['antecedents', 'consequents', 'antecedent support', 'consequent support',
                                      'support', 'confidence', 'lift', 'leverage', 'conviction']
                rules_display = rules_chosen_product[columns_to_display]
                rules_display.columns = ['Antécédents', 'Conséquents', 'Support Antécédent', 'Support Conséquent',
                                         'Support', 'Confiance', 'Lift', 'Leverage', 'Conviction']
                rules_display.sort_values(by=['Leverage', 'Support Antécédent', 'Confiance', 'Lift'], ascending=[False, False, False, False], inplace=True)
                
                st.subheader("Résultats de l'Analyse")
                st.dataframe(rules_display.head(50))
