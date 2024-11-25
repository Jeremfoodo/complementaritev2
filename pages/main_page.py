import pyfpgrowth
import pandas as pd

def fpgrowth_rules(transactions, min_support=0.01, min_confidence=0.5):
    """
    Extrait des règles d'association à partir des transactions en utilisant FP-Growth.
    Args:
    - transactions (list of lists): Liste de transactions contenant des ensembles de produits.
    - min_support (float): Support minimum pour les règles (en pourcentage, ex: 0.01 pour 1%).
    - min_confidence (float): Seuil minimum de confiance pour les règles.
    
    Returns:
    - DataFrame: Tableau des règles d'association avec les colonnes suivantes :
        - Antecedents : Ensemble des produits déclencheurs (uniques uniquement).
        - Consequents : Ensemble des produits associés.
        - Support_antecedent : Fréquence d'apparition de l'antécédent.
        - Support_consequent : Fréquence d'apparition du conséquent.
        - Support_combined : Fréquence des transactions contenant l'antécédent et le conséquent.
        - Lift : Indicateur de la force de la relation entre antécédent et conséquent.
    """
    # Étape 1 : Calcul du support minimum en absolu
    min_support_count = int(min_support * len(transactions))

    # Étape 2 : Extraction des motifs fréquents avec FP-Growth
    patterns = pyfpgrowth.find_frequent_patterns(transactions, min_support_count)

    if not patterns:
        return pd.DataFrame()

    # Étape 3 : Génération des règles d'association
    rules = pyfpgrowth.generate_association_rules(patterns, min_confidence)

    if not rules:
        return pd.DataFrame()

    # Étape 4 : Calcul des métriques supplémentaires (lift, supports)
    total_transactions = len(transactions)
    item_support = {item: count / total_transactions for item, count in patterns.items()}

    enriched_rules = []
    for antecedent, (consequent, confidence) in rules.items():
        # Ne garder que les antécédents uniques
        if not isinstance(antecedent, tuple):
            antecedent = (antecedent,)
        if len(antecedent) > 1:
            continue

        # Support combiné = Support des deux ensemble
        combined_support = patterns[tuple(sorted(set(antecedent).union(set(consequent))))] / total_transactions

        # Support de l'antécédent
        antecedent_support = patterns[antecedent] / total_transactions if antecedent in patterns else 0

        # Support du conséquent
        consequent_support = patterns[consequent] / total_transactions if consequent in patterns else 0

        # Calcul du lift
        lift = confidence / consequent_support if consequent_support > 0 else 0

        enriched_rules.append({
            'antecedents': antecedent[0],  # Produit unique
            'consequents': ', '.join(consequent) if isinstance(consequent, tuple) else consequent,
            'support_antecedent': antecedent_support,
            'support_consequent': consequent_support,
            'support_combined': combined_support,
            'confidence': confidence,
            'lift': lift
        })

    # Conversion en DataFrame
    rules_df = pd.DataFrame(enriched_rules)
    return rules_df.sort_values(by=['lift', 'confidence'], ascending=[False, False])
