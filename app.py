import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.vmb import criando_df_final_Rentabilidade
from Functions.dictionaries import obter_dicionarios
from pages.analise_2024 import page_analyse_2024

# Função principal
def main():
    st.title("Dashboard de Rentabilidade")
    
    # Menu de navegação
    menu = {
        "1 - Análise 2024": page_analyse_2024
    }
    
    # Cria um menu lateral
    escolha = st.sidebar.selectbox("Escolha uma página", list(menu.keys()))

    # Executa a função da página escolhida
    menu[escolha]()

if __name__ == "__main__":
    main()