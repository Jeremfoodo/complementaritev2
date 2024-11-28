import streamlit as st
import pandas as pd
import gdown
from mlxtend.frequent_patterns import apriori, association_rules

@st.cache_data
def load_data(url):
    """
    Télécharge les données depuis une URL Google Drive, les charge dans un DataFrame et les met en cache.
    """
    try:
        # Téléchargement du fichier
        output_path = "data.xlsx"
        gdown.download(url, output_path, quiet=False)

        # Chargement des données
        data = pd.read_excel(output_path)
        
        # Vérification si les données sont vides
        if data.empty:
            return None, "Le fichier est vide ou ne contient pas de données exploitables."
        
        return data, None  # Aucun problème
    except Exception as e:
        return None, f"Erreur lors du téléchargement ou du chargement des données : {e}"

def calculate_top_products(data, category):
    """
    Calcule le top 30 des produits uniques en fonction de leur fréquence dans les commandes.
    """
    # Filtrer les données par catégorie
    filtered_data = data[data['Product Category'] == category]

    # Calculer la fréquence par produit unique
    product_frequency = (
        filtered_data.groupby('product_name')['order_id']
        .nunique()
        .sort_values(ascending=False)
    )

    # Calculer le pourcentage de fréquence
    total_orders = data['order_id'].nunique()
    product_frequency_percentage = (product_frequency / total_orders * 100).reset_index()
    product_frequency_percentage.columns = ['product_name', 'frequency_percentage']

    # Renvoyer les 30 meilleurs produits
    return product_frequency_percentage.head(30)

def get_association_rules(data, selected_product, min_support=0.01, min_confidence=0.5):
    """
    Génère des règles d'association pour identifier les produits complémentaires.
    """
    # Regrouper les transactions
    transactions = data.groupby('order_id')['product_name'].apply(list)

    # Convertir en un DataFrame One-Hot Encoded
    one_hot = pd.get_dummies(transactions.apply(pd.Series).stack()).groupby(level=0).sum()

    # Calcul des motifs fréquents
    frequent_itemsets = apriori(one_hot, min_support=min_support, use_colnames=True)

    # Génération des règles d'association
    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

    # Ajouter une métrique pour le pourcentage de commandes contenant les deux produits
    rules['support_combined'] = rules['support'] * len(transactions)

    # Filtrer les règles pour lesquelles l'antécédent est le produit sélectionné
    filtered_rules = rules[rules['antecedents'].apply(lambda x: selected_product in x)]

    # Reformater les résultats pour un affichage clair
    results = filtered_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'support_combined']].copy()
    results['antecedents'] = results['antecedents'].apply(lambda x: ', '.join(list(x)))
    results['consequents'] = results['consequents'].apply(lambda x: ', '.join(list(x)))
    return results.sort_values(by='lift', ascending=False).head(50)

def main_page():
    st.title("Analyse des données - Produits complémentaires")

    # Utilisation de st.session_state pour conserver l'état des données et des sélections
    if 'data' not in st.session_state:
        st.session_state['data'] = None
    if 'error_message' not in st.session_state:
        st.session_state['error_message'] = None
    if 'selected_category' not in st.session_state:
        st.session_state['selected_category'] = None
    if 'top_products' not in st.session_state:
        st.session_state['top_products'] = None
    if 'selected_product' not in st.session_state:
        st.session_state['selected_product'] = None
    if 'association_rules' not in st.session_state:
        st.session_state['association_rules'] = None

    # URL à tester
    url = st.text_input(
        "Entrez l'URL Google Drive du fichier :",
        value="https://drive.google.com/uc?id=1sv6E1UsMV3fe-T_3p94uAUt1kz4xlXZA"
    )

    if st.button("Charger les données"):
        st.write("Tentative de chargement des données...")
        st.write(f"URL utilisée pour le téléchargement : {url}")
        
        # Appel de la fonction pour charger les données
        data, error_message = load_data(url)
        st.session_state['data'] = data
        st.session_state['error_message'] = error_message
        st.session_state['selected_category'] = None  # Réinitialiser la sélection
        st.session_state['selected_product'] = None
        st.session_state['association_rules'] = None

    # Vérification des données chargées
    if st.session_state['error_message']:
        st.error(st.session_state['error_message'])
        return

    if st.session_state['data'] is not None:
        st.success("Les données ont été chargées avec succès !")
        st.write("Les premières lignes des données :")
        st.write(st.session_state['data'].head())
        
        # Étape 1 : Sélection de la catégorie
        st.subheader("Étape 1 : Choisissez une catégorie de produit")
        product_categories = st.session_state['data']['Product Category'].dropna().unique()
        selected_category = st.selectbox(
            "Sélectionnez une catégorie :",
            options=product_categories,
            index=0 if st.session_state['selected_category'] is None else list(product_categories).index(st.session_state['selected_category'])
        )

        if st.button("Valider la catégorie"):
            st.session_state['selected_category'] = selected_category
            # Calculer le top 30 des produits
            st.session_state['top_products'] = calculate_top_products(st.session_state['data'], selected_category)

        # Afficher le top 30 des produits s'il est calculé
        if st.session_state['top_products'] is not None:
            st.write("Voici le top 30 des produits (par fréquence) :")
            st.dataframe(st.session_state['top_products'])

            # Étape 2 : Sélection d'un produit pour l'analyse
            st.subheader("Étape 2 : Sélectionnez un produit pour analyser ses compléments")
            top_products_list = st.session_state['top_products']['product_name'].tolist()
            selected_product = st.selectbox(
                "Choisissez un produit :",
                options=top_products_list,
                index=0 if st.session_state['selected_product'] is None else top_products_list.index(st.session_state['selected_product'])
            )

            if st.button("Analyser les produits complémentaires"):
                st.session_state['selected_product'] = selected_product
                st.session_state['association_rules'] = get_association_rules(
                    st.session_state['data'],
                    selected_product
                )

            # Afficher les résultats des produits complémentaires
            if st.session_state['association_rules'] is not None:
                st.write(f"Produits complémentaires pour : {st.session_state['selected_product']}")
                st.dataframe(st.session_state['association_rules'])
