import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.vmb import criando_df_final_Rentabilidade
from Functions.dictionaries import obter_dicionarios
from pages.analise_2024 import page_analyse_2024
from pages.auth import login

def main():
    # Sessão
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    # Tela de login
    if not st.session_state['autenticado']:
        if login():
            st.session_state['autenticado'] = True
        else:
            st.stop()

    # Depois do login, mostra só a opção de página
    escolha = st.sidebar.selectbox("Escolha uma página:", [""] + list({"1 - Análise 2024": page_analyse_2024}.keys()))
    
    # Executa a página selecionada
    if escolha == "1 - Análise 2024":
        page_analyse_2024()

if __name__ == "__main__":
    main()