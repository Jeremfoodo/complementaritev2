import pyfpgrowth
import pandas as pd

def fpgrowth_rules(transactions, min_support=0.01, min_confidence=0.5):
    """
    Extrait des règles d'association à partir des transactions en utilisant l'algorithme FP-Growth.
    Args:
    - transactions (list of lists): Liste de transactions contenant des ensembles de produits.
    - min_support (float): Support minimum pour les règles (en pourcentage, ex: 0.01 pour 1%).
    - min_confidence (float): Seuil minimum de confiance pour les règles.
    
    Returns:
    - DataFrame: Tableau des règles d'association avec les colonnes suivantes :
        - Antecedents : Ensemble des produits déclencheurs.
        - Consequents : Ensemble des produits associés.
        - Confidence : Probabilité que le conséquent soit acheté si l'antécédent l'est.
        - Support_consequent : Pourcentage d'apparition du conséquent dans toutes les transactions.
        - Lift : Force de la relation entre l'antécédent et le conséquent.
    """
    # Étape 1 : Calcul du support minimum en absolu
    min_support_count = int(min_support * len(transactions))

    # Étape 2 : Extraction des motifs fréquents avec FP-Growth
    patterns = pyfpgrowth.find_frequent_patterns(transactions, min_support_count)

    if not patterns:
        print("Aucun motif fréquent trouvé avec les paramètres donnés.")
        return pd.DataFrame()

    # Étape 3 : Génération des règles d'association
    rules = pyfpgrowth.generate_association_rules(patterns, min_confidence)

    if not rules:
        print("Aucune règle trouvée avec les paramètres donnés.")
        return pd.DataFrame()

    # Étape 4 : Calcul des métriques supplémentaires (lift, support_consequent)
    total_transactions = len(transactions)
    item_support = {item: count / total_transactions for item, count in patterns.items()}

    enriched_rules = []
    for antecedent, (consequent, confidence) in rules.items():
        consequent_support = item_support[consequent[0]] if len(consequent) == 1 else sum(
            item_support.get(item, 0) for item in consequent
        )
        lift = confidence / consequent_support if consequent_support > 0 else 0

        enriched_rules.append({
            'antecedents': antecedent,
            'consequents': consequent,
            'confidence': confidence,
            'support_consequent': consequent_support,
            'lift': lift
        })

    # Conversion en DataFrame et tri des résultats
    rules_df = pd.DataFrame(enriched_rules)
    rules_df['antecedents'] = rules_df['antecedents'].apply(lambda x: ', '.join(x) if isinstance(x, tuple) else x)
    rules_df['consequents'] = rules_df['consequents'].apply(lambda x: ', '.join(x) if isinstance(x, tuple) else x)
    return rules_df.sort_values(by=['lift', 'confidence'], ascending=[False, False])
