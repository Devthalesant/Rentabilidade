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
page_1 = st.Page(
    "pages/analise_2025.py",
    title="Análise de Rentabilidade 2025",
    icon=":material/savings:",
    default=True
)

page_2 = st.Page(
    "pages/analise_2024.py",
    title="Análise de Rentabilidade 2024",
    icon=":material/settings:",
)

# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Páginas": [page_1,page_2]
    }
)


# --- SHARED ON ALL PAGES ---
# st.logo("assets/codingisfun_logo.png")

# --- RUN NAVIGATION ---
pg.run()