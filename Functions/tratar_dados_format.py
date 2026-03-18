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

def formatar_real_resumido(valor):
    if valor is None:
        return "R$ 0,00"
    
    abs_valor = abs(valor)

    if abs_valor >= 1_000_000_000:
        return f"R$ {valor / 1_000_000_000:.2f} Bi".replace(".", ",")
    elif abs_valor >= 1_000_000:
        return f"R$ {valor / 1_000_000:.2f} Mi".replace(".", ",")
    elif abs_valor >= 1_000:
        return f"R$ {valor / 1_000:.1f} mil".replace(".", ",")
    else:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def calcular_representatividade(parte, total):
    if total in [0, None]:
        return 0.0
    return (abs(parte) / abs(total)) * 100


## Gráfico de procediemtnos específicos
def formatar_para_real(valor):
    if valor is None or pd.isna(valor):
        return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentual(valor):
    if pd.isna(valor):
        return "-"
    return f"{valor:.1f}%".replace(".", ",")


def formatar_numero_inteiro(valor):
    if valor is None or pd.isna(valor):
        return "0"
    return f"{valor:,.0f}".replace(",", ".")


def formatar_minutos(valor, resumido=True):
    if valor is None or pd.isna(valor):
        return "0 min"

    if resumido:
        horas = valor / 60
        if horas >= 1000:
            return f"{horas / 1000:.1f} mil h".replace(".", ",")
        return f"{horas:,.0f} h".replace(",", ".")

    return f"{valor:,.0f} min".replace(",", ".")


def calcular_media_movel(df, coluna_valor, janela=3):
    return df[coluna_valor].rolling(window=janela, min_periods=1).mean()


def preencher_meses_faltantes_com_zero(df, coluna_mes="Mês", colunas_valores=None):
    if colunas_valores is None:
        colunas_valores = []

    ordem_meses = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ]

    base_meses = pd.DataFrame({coluna_mes: ordem_meses})
    df_merge = base_meses.merge(df, on=coluna_mes, how="left")

    for col in colunas_valores:
        df_merge[col] = df_merge[col].fillna(0)

    if "Procedimento_padronizado" in df_merge.columns and not df.empty:
        df_merge["Procedimento_padronizado"] = df_merge["Procedimento_padronizado"].fillna(
            df["Procedimento_padronizado"].iloc[0]
        )

    return df_merge


def adicionar_variacao_percentual(df, coluna_valor, nome_coluna="% Var. vs mês anterior"):
    df = df.copy()
    df[nome_coluna] = df[coluna_valor].pct_change() * 100
    return df


def formatar_texto_barra(valor, tipo="numero"):
    if valor == 0:
        return ""

    if tipo == "moeda":
        if abs(valor) >= 1_000_000:
            return f"R$ {valor/1_000_000:.1f} Mi".replace(".", ",")
        elif abs(valor) >= 1_000:
            return f"R$ {valor/1_000:.1f} mil".replace(".", ",")
        return f"R$ {valor:,.0f}".replace(",", ".")

    if tipo == "decimal":
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    return f"{valor:,.0f}".replace(",", ".")


def formatar_hover_valor(valor, tipo="numero"):
    if tipo == "moeda":
        return formatar_para_real(valor)
    elif tipo == "decimal":
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"{valor:,.0f}".replace(",", ".")


def calcular_preco_medio_ponderado(df, coluna_preco="Preço_Praticado", coluna_qtd="Quantidade"):
    df_valid = df.copy()
    df_valid = df_valid.loc[
        (df_valid[coluna_qtd].notna()) &
        (df_valid[coluna_preco].notna()) &
        (df_valid[coluna_qtd] > 0)
    ]

    if df_valid.empty:
        return 0.0

    return (
        (df_valid[coluna_preco] * df_valid[coluna_qtd]).sum()
        / df_valid[coluna_qtd].sum()
    )


def criar_grafico_barras_com_media_movel(
    df_plot,
    df_real,
    coluna_mes,
    coluna_valor,
    titulo,
    tipo_valor="numero",
    janela_media=3,
    nome_barra=None,
    nome_linha=None,
    cor_barra="#8E44AD",
    cor_linha="#1F4E79"
):
    df_plot = df_plot.copy()
    df_real = df_real.copy()

    df_plot["Media_Movel"] = calcular_media_movel(df_plot, coluna_valor, janela=janela_media)
    df_plot["texto_barra"] = df_plot[coluna_valor].apply(
        lambda x: formatar_texto_barra(x, tipo_valor)
    )
    df_plot["valor_hover"] = df_plot[coluna_valor].apply(
        lambda x: formatar_hover_valor(x, tipo_valor)
    )
    df_plot["media_hover"] = df_plot["Media_Movel"].apply(
        lambda x: formatar_hover_valor(x, tipo_valor)
    )

    if nome_barra is None:
        nome_barra = titulo

    if nome_linha is None:
        nome_linha = f"Média móvel ({janela_media} meses)"

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_plot[coluna_mes],
            y=df_plot[coluna_valor],
            name=nome_barra,
            marker_color=cor_barra,
            text=df_plot["texto_barra"],
            textposition="outside",
            cliponaxis=False,
            customdata=df_plot[["valor_hover"]],
            hovertemplate="<b>%{x}</b><br>Valor: %{customdata[0]}<extra></extra>"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_plot[coluna_mes],
            y=df_plot["Media_Movel"],
            mode="lines+markers",
            name=nome_linha,
            line=dict(color=cor_linha, width=3),
            marker=dict(size=7, color=cor_linha),
            customdata=df_plot[["media_hover"]],
            hovertemplate="<b>%{x}</b><br>Média móvel: %{customdata[0]}<extra></extra>"
        )
    )

    # Pico e vale apenas considerando meses reais
    if not df_real.empty:
        idx_max = df_real[coluna_valor].idxmax()
        mes_max = df_real.loc[idx_max, coluna_mes]
        valor_max = df_real.loc[idx_max, coluna_valor]

        fig.add_trace(
            go.Scatter(
                x=[mes_max],
                y=[valor_max],
                mode="markers+text",
                name="Pico",
                marker=dict(size=13, color="#2E8B57", symbol="diamond"),
                text=["Pico"],
                textposition="top center",
                hovertemplate=f"<b>{mes_max}</b><br>Pico: {formatar_hover_valor(valor_max, tipo_valor)}<extra></extra>"
            )
        )

        idx_min = df_real[coluna_valor].idxmin()
        mes_min = df_real.loc[idx_min, coluna_mes]
        valor_min = df_real.loc[idx_min, coluna_valor]

        fig.add_trace(
            go.Scatter(
                x=[mes_min],
                y=[valor_min],
                mode="markers+text",
                name="Vale",
                marker=dict(size=13, color="#C0392B", symbol="diamond"),
                text=["Vale"],
                textposition="bottom center",
                hovertemplate=f"<b>{mes_min}</b><br>Vale: {formatar_hover_valor(valor_min, tipo_valor)}<extra></extra>"
            )
        )

    fig.update_layout(
        title=titulo,
        xaxis_title="Mês",
        yaxis_title="Valor",
        template="plotly_white",
        height=430,
        margin=dict(t=70, b=40, l=40, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_traces(textfont_size=11)

    return fig


def preparar_df_exibicao_specific(df_real):
    df_exibicao = df_real.copy()

    df_exibicao["Quantidade"] = df_exibicao["Quantidade"].apply(formatar_numero_inteiro)
    df_exibicao["Preço_Praticado"] = df_exibicao["Preço_Praticado"].apply(formatar_para_real)
    df_exibicao["Receita_Gerada"] = df_exibicao["Receita_Gerada"].apply(formatar_para_real)

    if "% Var. Quantidade" in df_exibicao.columns:
        df_exibicao["% Var. Quantidade"] = df_exibicao["% Var. Quantidade"].apply(formatar_percentual)

    if "% Var. Preço" in df_exibicao.columns:
        df_exibicao["% Var. Preço"] = df_exibicao["% Var. Preço"].apply(formatar_percentual)

    if "% Var. Receita" in df_exibicao.columns:
        df_exibicao["% Var. Receita"] = df_exibicao["% Var. Receita"].apply(formatar_percentual)

    return df_exibicao