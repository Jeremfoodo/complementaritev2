import streamlit as st
from data.download import download_data
from data.preprocess import load_and_preprocess, process_data
from utils.apriori_analysis import apriori_rules
import pandas as pd

def main_page():
    st.title("Analyse de Produits Complémentaires")

    file_urls = {
        'France': 'https://drive.google.com/uc?id=1_qfuH19aLu3JMocit2-wSL-FCmWNet1I',
        'Belgium': 'https://drive.google.com/uc?id=1IpVNWpAyjDBjprZ3Kl0BYaLaxJHH7wg2',
        'UK': 'https://drive.google.com/uc?id=1ROT0ide8EQfgcWpXMY6Qnyp5nMKoLt-a',
        'US': 'https://drive.google.com/uc?id=1l7KRNgouPsx3CiT13j5K2pMYevpuRHqt'
    }

    output_paths = {
        'France': 'dataFR.xlsx',
        'Belgium': 'dataBE.xlsx',
        'UK': 'dataUK.xlsx',
        'US': 'dataUS.xlsx'
    }

    user_country = st.selectbox("Choisissez le pays à analyser :", options=list(file_urls.keys()))

    file_url = file_urls[user_country]
    output_path = output_paths[user_country]

    st.write(f"Téléchargement des données pour {user_country}...")
    data = download_data(file_url, output_path)

    st.write("Données chargées :", data.head())

    if data.empty:
        st.error("Les données n'ont pas été correctement chargées pour ce pays.")
    else:
        if user_country in ['France', 'US']:
            zone_mappings = {
                'France': ['Toute France', 'Paris', 'Paris EST', 'Paris Ouest', 'Province'],
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
                    rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x))
                    rules['consequents'] = rules['consequents'].apply(lambda x: list(x))
                    rules_single = rules[(rules['antecedents'].apply(len) == 1) & (rules['consequents'].apply(len) == 1)]
                    rules_single['antecedents'] = rules_single['antecedents'].apply(lambda x: ', '.join(x))
                    rules_single['consequents'] = rules_single['consequents'].apply(lambda x: ', '.join(x))
                    rules_single[['antecedent support', 'consequent support', 'support', 'confidence', 'lift', 'leverage', 'conviction']] = \
                        rules_single[['antecedent support', 'consequent support', 'support', 'confidence', 'lift', 'leverage', 'conviction']].round(2)
                    rules_high_support = rules_single[rules_single['antecedent support'] > 0.1]
                    rules_chosen_product = rules_single[rules_single['antecedents'] == chosen_product]
                    columns_to_display = ['antecedents', 'consequents', 'antecedent support', 'consequent support',
                                          'support', 'confidence', 'lift', 'leverage', 'conviction']
                    rules_display = rules_chosen_product[columns_to_display]
                    rules_display.columns = ['Antécédents', 'Conséquents', 'Support Antécédent', 'Support Conséquent',
                                             'Support', 'Confiance', 'Lift', 'Leverage', 'Conviction']
                    rules_display.sort_values(by=['Leverage', 'Support Antécédent', 'Confiance', 'Lift'], ascending=[False, False, False, False], inplace=True)
                    st.subheader("Résultats de l'Analyse")
                    st.markdown(
                        """
                        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; font-size: 0.5em;">
                            <p><strong>Pour rappel, important pour vous :</strong></p>
                            <p><strong>Support Antécédent</strong> : le % de commande qui contiennent le produit "Antécédent"</p>
                            <p><strong>Support Conséquent</strong> : le % de commande qui contiennent le produit "Conséquent"</p>
                            <p><strong>Support</strong> : le % de commande qui contiennent au moins ces 2 articles ensemble</p>
                            <p><strong>Lift </strong> : Nombre de chance supérieure qu'à le produit Conséquent a être acheté avec le produit Antécédent plutôt que tout seul. C'est l'indicateur principal de corrélation.</p>
                            <p>Vous pouvez trier le tableau en cliquant sur les colonnes, et aussi télécharger la liste (passer la souris sur le tableau et download as csv)</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.dataframe(rules_display.head(50))
