import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.dictionaries import obter_dicionarios
from pages.analise_2024 import page_analyse_2024
from pages.auth import login
from pages.analise_2025 import page_analyse_2025

st.set_page_config(
    page_title="Rentabilidade - Pró-Corpo",  # Opcional, para o título da aba do navegador
    layout="wide"                  # Configura o modo wide
)

# O restante do seu código...
# --- PAGE SETUP ---
# Sidebar Navigation
page = st.sidebar.selectbox(
    "Escolha a Página",
    ("Rentabilidade 2024", "Rentabilidade 2025")
)

# Load selected page
if page == "Rentabilidade 2024":
    page_analyse_2024()
elif page == "Rentabilidade 2025":
    page_analyse_2025()