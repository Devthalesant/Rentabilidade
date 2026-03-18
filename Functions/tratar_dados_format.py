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

def formatar_brl_for_dataframes(df, coluna):

    def cor(val):
        if val > 0:
            return "background-color:#14532d; color:#22c55e; font-weight:bold"
        elif val < 0:
            return "background-color:#7f1d1d; color:#ef4444; font-weight:bold"
        return ""

    return (
        df.style
        .format({coluna: lambda x: f"R$ {x:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")})
        .map(cor, subset=[coluna])
    )

def mapa_calor_brl(df, colunas, verde_menor=True, q_min=0.05, q_max=0.95):
    colunas = [colunas] if isinstance(colunas, str) else colunas    
    cmap = "RdYlGn_r" if verde_menor else "RdYlGn"

    vmin = df[colunas].stack().quantile(q_min)
    vmax = df[colunas].stack().quantile(q_max)

    return (
        df.style
        .format({
            col: lambda x: f"R$ {x:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            for col in colunas
        })
        .background_gradient(cmap=cmap, subset=colunas, vmin=vmin, vmax=vmax)
    )

def formatar_metrica_brl(valor):

    valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    if valor < 0:
        return f"<span style='color:#ef4444; font-weight:600'>{valor_formatado}</span>"
    
    return valor_formatado

def estilizar_dataframe(
    df,
    cols_percentual=None,
    cols_monetario=None,
    cols_verde_negativo=None,
    cols_escala_cor=None,
    verde_menor=True,
    q_min=0.05,
    q_max=0.95
):
    cols_percentual = cols_percentual or []
    cols_monetario = cols_monetario or []
    cols_verde_negativo = cols_verde_negativo or []
    cols_escala_cor = cols_escala_cor or []

    def formatar_brl(x):
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_pct(x):
        return f"{x:.2%}".replace(".", ",")

    def pintar_verde_negativo(val):
        if val < 0:
            return "background-color:#14532d; color:#22c55e; font-weight:600"
        elif val > 0:
            return "background-color:#7f1d1d; color:#ef4444; font-weight:600"
        return ""

    formatacoes = {}
    formatacoes.update({col: formatar_pct for col in cols_percentual})
    formatacoes.update({col: formatar_brl for col in cols_monetario})

    cmap = "RdYlGn_r" if verde_menor else "RdYlGn"

    styler = df.style.format(formatacoes)

    if cols_verde_negativo:
        styler = styler.map(pintar_verde_negativo, subset=cols_verde_negativo)

    for col in cols_escala_cor:
        vmin = df[col].quantile(q_min)
        vmax = df[col].quantile(q_max)
        styler = styler.background_gradient(
            cmap=cmap,
            subset=[col],
            vmin=vmin,
            vmax=vmax
        )

    return styler

