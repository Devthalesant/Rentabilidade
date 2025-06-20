import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.vmb import criando_df_final_Rentabilidade
from Functions.dictionaries import obter_dicionarios
import io

def teste_mongo():
        # Carrega o df
        df_final = criando_df_final_Rentabilidade()
        
        st.title("🌟Bases Mongo")

        st.dataframe(df_final)