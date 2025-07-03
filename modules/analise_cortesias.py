import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.vmb import criando_df_final_Rentabilidade
from Functions.dictionaries import obter_dicionarios
from Functions.mongo import *
import io
from Functions.courtesy import courtesy_analysis_dfs

def courtesy_period():

    #bringing the dataframes: 
    database,courtesy_analysis_procedure,courtesy_custumor_reviw = courtesy_analysis_dfs()

    st.title("Análise de Cortesias Período 🎁:")

    analysis_options = ['Custo Fixo Zerado', 'Custo Fixo Real']


    format_dict = {
        'Custo_Cortesia': 'R$ {:,.2f}',
        'Receita Gerada': 'R$ {:,.2f}',
        'Custo_total_geral': 'R$ {:,.2f}',
        'Lucro/Prejuízo': 'R$ {:,.2f}',
    }

    # Sort by Profit/Loss (highest to lowest)
    df_sorted = courtesy_analysis_procedure.sort_values('Lucro/Prejuízo', ascending=False)

    # Apply formatting
    # Df of courtesy procedures results
    st.subheader("Retorno Agregado dos Procedimentos Oferecidos: ")
    st.dataframe(
        df_sorted.style
            .apply(lambda x: ['color: green' if v >= 0 else 'color: red' 
                for v in x], subset=['Lucro/Prejuízo'])
            .format(format_dict)
    )

    # Df od custumers Classification:
    
    df_custumer = courtesy_custumor_reviw.groupby(["Procedimento_padronizado",'Classificacao']).agg({"ID cliente" : "nunique",
                                                                                                                  "Quantidade" : 'sum',
                                                                                                                  'Lucro/Prejuízo' : 'sum'}).reset_index()
    
    st.dataframe(
        df_custumer.style
            .apply(lambda x: ['background: lightyellow' if v == 'Oportunista' else '' 
                for v in x], subset=['Classificacao'])
            .apply(lambda x: ['color: green' if v >= 0 else 'color: red' 
                for v in x], subset=['Lucro/Prejuízo'])
            .format(format_dict)
    )