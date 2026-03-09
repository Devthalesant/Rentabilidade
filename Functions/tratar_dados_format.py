from datetime import timedelta
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
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import locale

def minutos_para_hhmmss(minutos: int) -> str:
    tempo = timedelta(minutes=minutos)
    return str(tempo)

def pegar_tempo_do_prcedimento(df_depara_tempo,opcao):

    df_tempo_one = df_depara_tempo.loc[df_depara_tempo['categoria'] == opcao]

    tempo_one = df_tempo_one['tempo'].iloc[0]
    
    return tempo_one

def pegar_custos_do_prcedimento(df_custos_dict,opcao):

    df_custos = df_custos_dict.loc[df_custos_dict['procedimento'] == opcao]
    custo_produto = df_custos['CUSTO PRODUTO'].iloc[0]
    custo_mod = df_custos['MOD'].iloc[0]
    custo_insumos = df_custos['CUSTO INSUMOS'].iloc[0]

    return custo_produto, custo_mod, custo_insumos