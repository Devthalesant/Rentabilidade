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
from pages.analise_2025 import page_analyse_2025
from pages.teste_mongo import teste_mongo

# --- PAGE SETUP ---
# Sidebar Navigation
page = st.sidebar.selectbox(
    "Escolha a Página",
    ("Análise de Rentabilidade 2024", "Análise de Rentabilidade 2025")
)

# Load selected page
if page == "Análise de Rentabilidade 2024":
    page_analyse_2024()
elif page == "Análise de Rentabilidade 2025":
    page_analyse_2025()