import streamlit as st
from utils.apriori_analysis import fpgrowth_rules
from data.download import download_data

# URLs des fichiers par pays
FILE_URLS = {
    'FR': 'https://drive.google.com/uc?id=1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA',
    'Belgium': 'https://drive.google.com/uc?id=1fqu_YgsovkDrpqV7OsFStusEvM-9axRg',
    'UK': 'https://drive.google.com/uc?id=1ROT0ide8EQfgcWpXMY6Qnyp5nMKoLt-a',
    'US': 'https://drive.google.com/uc?id=1HsxBxGpq3lSwJKPALDsDNvJXNi6us2j-'
}

def main_page():
    st.title("Analyse de Produits Complémentaires")

    # Sélection du pays
    user_country = st.selectbox("Choisissez un pays :", options=list(FILE_URLS.keys()))

    # Téléchargement et chargement des données (mise en cache activée)
    with st.spinner("Téléchargement des données..."):
        data = download_data(FILE_URLS[user_country], f"{user_country}_data.xlsx")

    # Vérification des données
    if data.empty:
        st.error("Les données n'ont pas été correctement chargées pour ce pays.")
        return

    st.write("Données chargées :", data.head())

    # Sélection de la catégorie
    categories = data['Product Category'].dropna().unique()
    chosen_category = st.selectbox("Choisissez une catégorie de produit :", options=categories)

    # Filtrer les données par catégorie
    data_filtered = data[data['Product Category'] == chosen_category]

    # Récupérer les 30 produits les plus fréquents
    top_products = (
        data_filtered['product_name']
        .value_counts()
        .nlargest(30)
        .sort_index()
        .index.tolist()
    )
    chosen_product = st.selectbox("Choisissez un produit :", options=top_products)

    # Transactions par commande
    transactions = data_filtered.groupby('order_id')['product_name'].apply(list).tolist()

    # Analyse avec FP-Growth
    if st.button("Lancer l'analyse"):
        rules = fpgrowth_rules(transactions, min_support=0.01, min_confidence=0.5)

        if rules.empty:
            st.warning(f"Aucune règle trouvée pour le produit {chosen_product}.")
        else:
            rules_filtered = rules[rules['antecedents'] == chosen_product]
            st.write(f"Règles trouvées pour le produit {chosen_product} :")
            st.dataframe(rules_filtered)
