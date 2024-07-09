import pandas as pd
import streamlit as st

# Désactiver le cache temporairement
def load_and_preprocess(file_path):
    data = pd.read_excel(file_path, sheet_name='Export')
    data = data[data[data.columns[0]] != "Total"]
    data = data.dropna(subset=[data.columns[0]])
    data = data[~data[data.columns[0]].astype(str).str.startswith("Filtres")]
    data = data.rename(columns={'GMV': 'GMV WITH TAX'})
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    return data

def process_data(data):
    return data.groupby('order_id')['product_name'].apply(list).tolist()
