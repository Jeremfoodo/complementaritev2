import streamlit as st
from streamlit_option_menu import option_menu
from pages.main_page import main_page

# Configuration de la page principale
st.set_page_config(
    page_title="Analyse de données",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Menu de navigation
selected_page = option_menu(
    menu_title=None,
    options=["Page principale"],
    icons=["bar-chart-line"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# Navigation vers la page principale
if selected_page == "Page principale":
    main_page()
