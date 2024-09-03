import pandas as pd

def load_and_preprocess(file_path):
    try:
        data = pd.read_excel(file_path, sheet_name='Export', engine='openpyxl')
        print("Données chargées avec succès")
        data = data[data[data.columns[0]] != "Total"]
        data = data.dropna(subset=[data.columns[0]])
        data = data[~data[data.columns[0]].astype(str).str.startswith("Filtres")]
        data = data.rename(columns={'GMV': 'GMV WITH TAX'})
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        print("Données prétraitées avec succès")
        return data
    except Exception as e:
        print(f"Erreur lors du chargement et du prétraitement des données : {e}")
        return pd.DataFrame()

def process_data(data):
    try:
        transactions = data.groupby('order_id')['product_name'].apply(list).tolist()
        print("Données traitées avec succès")
        return transactions
    except Exception as e:
        print(f"Erreur lors du traitement des données : {e}")
        return []
