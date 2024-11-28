import streamlit as st
import pandas as pd
import gdown

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

def main_page():
    st.title("Analyse des données - Top produits par catégorie")

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
        
        if error_message:
            st.error(error_message)
            return
        else:
            st.success("Les données ont été chargées avec succès !")
            st.write("Les premières lignes des données :")
            st.write(data.head())
            
            # Étape 1 : Sélection de la catégorie
            st.subheader("Étape 1 : Choisissez une catégorie de produit")
            product_categories = data['Product Category'].dropna().unique()
            selected_category = st.selectbox("Sélectionnez une catégorie :", options=product_categories)

            if st.button("Valider la catégorie"):
                # Étape 2 : Calculer le top 30 des produits
                st.write(f"Calcul du top 30 des produits pour la catégorie : {selected_category}")
                top_products = calculate_top_products(data, selected_category)

                if not top_products.empty:
                    st.write("Voici le top 30 des produits (par fréquence) :")
                    st.dataframe(top_products)
                else:
                    st.warning(f"Aucun produit trouvé pour la catégorie {selected_category}.")
