from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

def apriori_rules(transactions, min_support=0.01, min_lift=1.2):
    """
    Extrait des règles d'association à partir des transactions.
    
    Args:
    - transactions (list of lists): Liste de transactions contenant des ensembles de produits.
    - min_support (float): Support minimum pour les itemsets fréquents.
    - min_lift (float): Seuil minimum pour le lift des règles.
    
    Returns:
    - DataFrame: Tableau des règles d'association avec les colonnes pertinentes.
    """
    # Étape 1 : Encodage des transactions
    encoder = TransactionEncoder()
    onehot = encoder.fit_transform(transactions)
    df_onehot = pd.DataFrame(onehot, columns=encoder.columns_)

    # Étape 2 : Extraction des itemsets fréquents
    frequent_itemsets = apriori(df_onehot, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        print("Aucun itemset fréquent trouvé avec les paramètres donnés.")
        return pd.DataFrame()

    # Étape 3 : Calcul de num_itemsets
    num_itemsets = {
        length: len(frequent_itemsets[frequent_itemsets['itemsets'].apply(len) == length])
        for length in frequent_itemsets['itemsets'].apply(len).unique()
    }

    # Étape 4 : Génération des règles d'association
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift, num_itemsets=num_itemsets)
    if rules.empty:
        print("Aucune règle trouvée avec les paramètres donnés.")
        return pd.DataFrame()

    # Étape 5 : Sélection des colonnes importantes et tri des résultats
    rules = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
    rules = rules.sort_values(by=['lift', 'confidence'], ascending=[False, False])
    
    # Conversion des ensembles en listes pour affichage lisible
    rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x)[0] if len(x) == 1 else ', '.join(x))
    rules['consequents'] = rules['consequents'].apply(lambda x: list(x)[0] if len(x) == 1 else ', '.join(x))

    return rules
