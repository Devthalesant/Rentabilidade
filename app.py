import streamlit as st
from modules.analise_2024 import page_analyse_2024
from modules.analise_2025 import page_analyse_2025
from modules.atualizar_dados import atualizar_banco_de_dados
from modules.analise_cortesias import courtesy_period

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
        "Análise De Cortesia": {
            "1 - Período" : courtesy_period
        },

        "Admin": {
            "1 - Atualizar Base de Dados":atualizar_banco_de_dados,
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
