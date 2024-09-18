import streamlit as st
from streamlit_option_menu import option_menu
from main_page import main_page
from segmentation_page import segmentation_page

# Créer le menu de navigation
selected_page = option_menu(
    menu_title=None,
    options=["Analyse", "Segmentation"],
    icons=["bar-chart-line", "pie-chart"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# Afficher la page sélectionnée
if selected_page == "Analyse":
    main_page()
elif selected_page == "Segmentation":
    segmentation_page()
