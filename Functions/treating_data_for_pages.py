from .dictionaries_2 import *
import streamlit as st
import pandas as pd


def gerar_kpis_gerais_current_year(data):

    ## Pimeiras Métricas serão de rentabilidade da Rede considerando o ano atual (compilado) - metricas mais gerais
    pedidos = data['ID orçamento'].nunique()
    clientes = data['ID cliente'].nunique()
    faturamento_total = data['Valor líquido'].sum()
    custo_total = data['Custo_total_procedimento'].sum()
    resultado_periodo = faturamento_total - custo_total

    return pedidos, clientes, faturamento_total, custo_total, resultado_periodo 


## Função para gerar dados para o gráfico comparativo de períodos (valor vendido e custo total)
def gerar_dados_quadrimestrais_atual_e_retroativo(dados_retroativos, data, quadrimestre_selecionado, unidade_selecionada):

    meses_quadrimestre = dic_quadrimestre_períodos[quadrimestre_selecionado]

    dados_retroativos = dados_retroativos.loc[dados_retroativos['Mês'].isin(meses_quadrimestre)]
    dados_atuais_comparativo = data.loc[data['Mês'].isin(meses_quadrimestre)]

    dados_atuais_comparativo = dados_atuais_comparativo.sort_values(by=['Data venda'])

    if unidade_selecionada != "TODAS":
        dados_retroativos = dados_retroativos.loc[dados_retroativos['Unidade'] == unidade_selecionada]
        dados_atuais_comparativo = dados_atuais_comparativo.loc[dados_atuais_comparativo['Unidade'] == unidade_selecionada]

    index_ano_dados_retroativos = sorted(dados_retroativos['Ano'].unique())
    index_mes_dados_retroativos = meses_quadrimestre

    lista_de_kpis_retroativos = []

    for y in index_ano_dados_retroativos:
        dados_ano = dados_retroativos.loc[dados_retroativos['Ano'] == y]
        lista_de_faturamento_anual = []
        lista_de_custos_total_anual = []

        for m in index_mes_dados_retroativos:
            dados_mes = dados_ano.loc[dados_ano['Mês'] == m]
            faturamento_liquido_mes_ano = round(dados_mes['Valor líquido'].sum())
            custos_total_mes_ano = round(dados_mes['Custo_total_procedimento'].sum())

            lista_de_faturamento_anual.append(faturamento_liquido_mes_ano)
            lista_de_custos_total_anual.append(custos_total_mes_ano)

        lista_de_kpis_retroativos.append({
            "name": str(y),
            "valor_liquido": lista_de_faturamento_anual,
            "custo_total": lista_de_custos_total_anual
        })

    index_meses_dados_atuais = meses_quadrimestre
    lista_de_faturamento_anual_atual = []
    lista_de_custo_total_anual_atual = []

    for m in index_meses_dados_atuais:
        name = dados_atuais_comparativo['Ano'].iloc[0]
        dados_mensais_atuais = dados_atuais_comparativo.loc[dados_atuais_comparativo['Mês'] == m]

        faturamento_liquido_mes_ano_atual = round(dados_mensais_atuais['Valor líquido'].sum())
        custo_total_mes_ano_atual = round(dados_mensais_atuais['Custo_total_procedimento'].sum())

        lista_de_faturamento_anual_atual.append(faturamento_liquido_mes_ano_atual)
        lista_de_custo_total_anual_atual.append(custo_total_mes_ano_atual)

    lista_de_kpis_retroativos.append({
        "name": str(name),
        "valor_liquido": lista_de_faturamento_anual_atual,
        "custo_total": lista_de_custo_total_anual_atual
    })

    return lista_de_kpis_retroativos