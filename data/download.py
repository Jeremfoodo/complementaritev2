import gdown
import pandas as pd
import streamlit as st

# Désactiver le cache temporairement
def download_data(url, output_path):
    gdown.download(url, output_path, quiet=True)
    return load_and_preprocess(output_path)

def download_segmentation_data(url, output_path):
    gdown.download(url, output_path, quiet=True)
    return pd.read_excel(output_path)
