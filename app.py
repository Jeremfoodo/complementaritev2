import streamlit as st
from streamlit_option_menu import option_menu
from pages.main_page import main_page
from pages.segmentation_page import segmentation_page

# Configuration de la page principale
st.set_page_config(
    page_title="Analyse de Produits et Segmentation",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Menu de navigation
selected_page = option_menu(
    menu_title=None,
    options=["Analyse de complémentarité", "Segmentation"],
    icons=["bar-chart-line", "pie-chart"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# Afficher la page sélectionnée
if selected_page == "Analyse de complémentarité":
    main_page()
elif selected_page == "Segmentation":
    segmentation_page()
