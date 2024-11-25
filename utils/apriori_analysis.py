import pyfpgrowth
import pandas as pd

def fpgrowth_rules(transactions, min_support=0.01, min_confidence=0.5):
    # Étape 1 : Calcul du support minimum en absolu
    min_support_count = int(min_support * len(transactions))

    # Étape 2 : Extraction des motifs fréquents avec FP-Growth
    patterns = pyfpgrowth.find_frequent_patterns(transactions, min_support_count)
    print("Patterns fréquents :", patterns)  # Diagnostic

    if not patterns:
        return pd.DataFrame()

    # Étape 3 : Génération des règles d'association
    rules = pyfpgrowth.generate_association_rules(patterns, min_confidence)
    print("Règles brutes générées :", rules)  # Diagnostic

    if not rules:
        return pd.DataFrame()

    # Étape 4 : Calcul des métriques supplémentaires (lift, supports)
    total_transactions = len(transactions)
    item_support = {item: count / total_transactions for item, count in patterns.items()}

    enriched_rules = []
    for antecedent, (consequent, confidence) in rules.items():
        if not isinstance(antecedent, tuple):
            antecedent = (antecedent,)
        if len(antecedent) > 1:
            continue

        combined_support = patterns[tuple(sorted(set(antecedent).union(set(consequent))))] / total_transactions
        antecedent_support = patterns[antecedent] / total_transactions if antecedent in patterns else 0
        consequent_support = patterns[consequent] / total_transactions if consequent in patterns else 0
        lift = confidence / consequent_support if consequent_support > 0 else 0

        enriched_rules.append({
            'antecedents': antecedent[0],
            'consequents': ', '.join(consequent) if isinstance(consequent, tuple) else consequent,
            'support_antecedent': antecedent_support,
            'support_consequent': consequent_support,
            'support_combined': combined_support,
            'confidence': confidence,
            'lift': lift
        })

    rules_df = pd.DataFrame(enriched_rules)
    return rules_df.sort_values(by=['lift', 'confidence'], ascending=[False, False])

