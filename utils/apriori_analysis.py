import pyfpgrowth
import pandas as pd

def fpgrowth_rules(transactions, min_support=0.01, min_confidence=0.5):
    min_support_count = int(min_support * len(transactions))
    patterns = pyfpgrowth.find_frequent_patterns(transactions, min_support_count)

    if not patterns:
        return pd.DataFrame()

    rules = pyfpgrowth.generate_association_rules(patterns, min_confidence)
    total_transactions = len(transactions)

    enriched_rules = []
    for antecedent, (consequent, confidence) in rules.items():
        combined_support = patterns[tuple(sorted(set(antecedent).union(set(consequent))))] / total_transactions
        antecedent_support = patterns[antecedent] / total_transactions
        consequent_support = patterns[consequent] / total_transactions
        lift = confidence / consequent_support if consequent_support > 0 else 0

        enriched_rules.append({
            'antecedents': antecedent,
            'consequents': consequent,
            'support_antecedent': antecedent_support,
            'support_consequent': consequent_support,
            'support_combined': combined_support,
            'confidence': confidence,
            'lift': lift
        })

    return pd.DataFrame(enriched_rules).sort_values(by=['lift', 'confidence'], ascending=[False, False])
