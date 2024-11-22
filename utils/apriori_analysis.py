from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
import streamlit as st

@st.cache_data
def apriori_rules(transactions, min_support=0.01, min_lift=1.2):
    """
    Fonction pour extraire des règles d'association à partir des transactions.
    Args:
    - transactions (list of lists): Transactions list contenant des ensembles d'articles.
    - min_support (float): Support minimum pour les itemsets fréquents.
    - min_lift (float): Seuil minimum pour le lift des règles.
    
    Returns:
    - DataFrame: Contenant les règles générées.
    """
    # Encodage des transactions
    encoder = TransactionEncoder()
    onehot = encoder.fit_transform(transactions)
    df_onehot = pd.DataFrame(onehot, columns=encoder.columns_)

    # Extraction des itemsets fréquents
    frequent_itemsets = apriori(df_onehot, min_support=min_support, use_colnames=True)

    # Vérification si des itemsets fréquents sont trouvés
    if frequent_itemsets.empty:
        st.warning("Aucun itemset fréquent trouvé avec les paramètres actuels.")
        return pd.DataFrame()

    # Calcul de num_itemsets
    num_itemsets = {
        length: len(frequent_itemsets[frequent_itemsets['itemsets'].apply(len) == length])
        for length in frequent_itemsets['itemsets'].apply(len).unique()
    }

    # Extraction des règles d'association
    try:
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift, num_itemsets=num_itemsets)
    except TypeError as e:
        st.error(f"Erreur lors de l'extraction des règles : {e}")
        return pd.DataFrame()

    # Vérification si des règles ont été générées
    if rules.empty:
        st.warning("Aucune règle trouvée avec les paramètres actuels.")
        return pd.DataFrame()

    return rules
