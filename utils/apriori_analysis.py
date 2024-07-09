from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
import streamlit as st

# Désactiver le cache temporairement
def apriori_rules(transactions, min_support=0.01, min_lift=1.2):
    encoder = TransactionEncoder()
    onehot = encoder.fit_transform(transactions)
    df_onehot = pd.DataFrame(onehot, columns=encoder.columns_)
    frequent_itemsets = apriori(df_onehot, min_support=min_support, use_colnames=True)
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift)
    return rules
