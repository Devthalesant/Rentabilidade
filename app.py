import streamlit as st
from modules.analise_2024 import page_analyse_2024
from modules.analise_2025 import page_analyse_2025
from modules.atualizar_dados import atualizar_banco_de_dados
from modules.procedures import procedimentos

st.set_page_config(
    page_title="Rentabilidade - Pró-Corpo", 
    layout="wide",
    menu_items=None               
)

def main():
    # Autenticação simples usando secrets.toml
    password = st.sidebar.text_input("Digite a senha:", type="password")

    # Verifica se uma senha foi inserida
    if not password:
        st.error("Por favor, insira a senha.")
        st.stop()  # Para a execução aqui se a senha não for fornecida

    # Verifica se a senha está correta
    if password != st.secrets["credentials"]["password"]:
        st.error("Senha incorreta!")
        st.stop()  # Para a execução se a senha estiver errada
    # Define o menu se a senha estiver correta
    
    menu_structure = {
        "Análises Rentabilidade": {
            "1 - 2024": page_analyse_2024,
            "2 - 2025": page_analyse_2025,
            "3 - 2025 procedures" : procedimentos,
        },
        "Admin": {
            "1 - Atualizar Base de Dados": atualizar_banco_de_dados,
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