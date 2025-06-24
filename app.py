import streamlit as st
from pages.analise_2024 import page_analyse_2024
from pages.analise_2025 import page_analyse_2025

st.set_page_config(
    page_title="Rentabilidade - Pró-Corpo", 
    layout="wide",
    menu_items=None               
)

def main():
    """
    Main function for the application.
    
    This function defines the menu structure of the application and uses Streamlit's 
    sidebar to let the user select a category and a page. It then calls the function 
    associated with the selected page.
    """
    # Define the menu structure
    menu_structure = {
        "Análises Rentabilidade": {
            "1 - 2024": page_analyse_2024,
            "2 - 2025": page_analyse_2025,
        },

        "Admin": {
            "1 - Atualizar Base de Dados": "",
        }
    }

    st.sidebar.title("Menu")

    category = st.sidebar.radio("Selecione a categoria", list(menu_structure.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"Páginas - {category}")
    
    pages = list(menu_structure[category].keys())
    selected_page = st.sidebar.radio("Selecione a página", pages, key="page_selector")
    
    menu_structure[category][selected_page]()
    
if __name__ == "__main__":
    main()
