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

########################################################################################################
#FUnção de tratamento de dados: 

def tratando_base_procedimentos():

    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def carregar_custo_fixo():
        return pegar_dados_mongodb("rentabilidade_anual", "custos_fixos_2025")

    @st.cache_data(ttl=3600)
    def carregar_vmb():
        return pegar_dados_mongodb("rentabilidade_anual", "venda_mensal_bruta_2025")

    @st.cache_data(ttl=3600)
    def carregar_taxas():
        return pegar_dados_mongodb("rentabilidade_anual", "impostos_taxas_2025")
    
    custo_fixo = carregar_custo_fixo()
    vmb_concat = carregar_vmb()
    df_taxas = carregar_taxas()

    vmb_concat = vmb_concat.loc[~vmb_concat['Procedimento'].isna()]
    vmb_concat = vmb_concat.loc[vmb_concat['Procedimento'] != "Vale Presente"]
    vmb_concat['Procedimento'] = vmb_concat['Procedimento'].astype(str)
    vmb_concat['Status'] = vmb_concat['Status'].astype(str)
    vmb_concat['Valor % desconto item'] = vmb_concat['Valor % desconto item'].astype(str)
    vmb_concat = vmb_concat.loc[~vmb_concat['Procedimento'].str.contains("CORTESIA",case=False)]
    vmb_concat = vmb_concat.loc[vmb_concat['Valor % desconto item'] != '100,00%']
    vmb_concat = vmb_concat.loc[vmb_concat['Status'] == "Finalizado"]

    vmb_concat['valor_unitario'] =  vmb_concat['Valor liquido item'] /  vmb_concat['Quantidade']

    vmb_concat = vmb_concat.loc[~vmb_concat['Procedimento'].isna()]



    unidades = ['LAPA','TATUAPÉ','OSASCO','JARDINS','SÃO BERNARDO','MOOCA','SANTOS',
                'COPACABANA','LONDRINA','IPIRANGA','TUCURUVI','CAMPINAS','MOEMA','ITAIM'
                'SOROCABA','SANTO,AMARO','VILA,MASCOTE','GUARULHOS','TIJUCA','ALPHAVILLE']
    
    vmb_concat = vmb_concat.loc[vmb_concat['Unidade'].isin(unidades)]

    colunas_vmb = ['ID orçamento','Mês venda','Unidade',
                   'Grupo procedimento','Procedimento',
                   'Quantidade', 'Valor tabela item','Valor % desconto item',
                   'valor desconto item','valor_unitario']

    vmb_concat = vmb_concat[colunas_vmb]

    Appointments_dic, Sales_dic, Month_dic, duration_dic, all_costs_2024, all_costs_2025,all_costs_2025_black = obter_dicionarios()

    vmb_concat['Procedimento_padronizado'] = vmb_concat['Procedimento'].map(Sales_dic)
    vmb_concat_tratar = vmb_concat.loc[vmb_concat['Procedimento_padronizado'].isna()]

    produtos_tratar = vmb_concat_tratar['Procedimento'].unique()

    if len(produtos_tratar) != 0:
        st.error(f"Procedimentos sem custos Salvos: {produtos_tratar}, Adicionar no Dicionário!")

    return vmb_concat , df_taxas


########################################################################################################
#FUnção de Extrair Custis: 

def extrair_todos_custos(dicionario_custos):

    custos_data = []
    for procedimento, custos in dicionario_custos.items():
        custos_data.append({
            'Procedimento_padronizado': procedimento,
            'CUSTO TOTAL': custos.get("CUSTO TOTAL", 0),
            'CUSTO PRODUTO': custos.get("CUSTO PRODUTO", 0),
            'MOD': custos.get("MOD", 0),
            'CUSTO INSUMOS': custos.get("CUSTO INSUMOS", 0)
        })
    
    return pd.DataFrame(custos_data)

########################################################################################################
#FUnção de Extrair Custis: a 

def gerar_dados_agrupados_gerais(vmb_concat,df_custos,df_taxas):

    Appointments_dic, Sales_dic, Month_dic, duration_dic, all_costs_2024, all_costs_2025,all_costs_2025_black = obter_dicionarios()

    vmb_concat = vmb_concat.merge(df_custos, on='Procedimento_padronizado', how='left')

    vmb_concat = vmb_concat.merge(df_taxas[['Mês','Custo_Sobre_Venda']],how='left',
                                    left_on=['Mês venda'],
                                    right_on=['Mês'])

    vmb_concat['Tempo_unitário'] = vmb_concat['Procedimento_padronizado'].map(duration_dic)

        # Converte para timedelta e depois para minutos
    vmb_concat['Tempo_minutos_unitário'] = pd.to_timedelta(vmb_concat['Tempo_unitário']).dt.total_seconds() / 60

    # Arredonda para inteiro
    vmb_concat['Tempo_minutos_unitário'] = (pd.to_timedelta(vmb_concat['Tempo_unitário']).dt.total_seconds() / 60).round().astype(int)

    colunas_vmb = ['Mês venda','ID orçamento','Unidade','Grupo procedimento','Procedimento_padronizado',
                    'Quantidade', 'Valor tabela item','valor_unitario','CUSTO PRODUTO','MOD','CUSTO INSUMOS',
                    'Custo_Sobre_Venda','Tempo_minutos_unitário']

    vmb_concat = vmb_concat[colunas_vmb]

    vmb_concat = vmb_concat.rename(columns={'Valor tabela item':'Valor_tabela_unit',
                                            'valor_unitario' : 'Valor_líquido_unit',
                                            'CUSTO PRODUTO':'Custo_produto_unit',
                                            'MOD':'Mod_unit',
                                            'CUSTO INSUMOS':'Custo_insumo_unit'})


    vmb_concat['Custo_direto_unit'] = (vmb_concat['Custo_produto_unit'] + 
                                        vmb_concat['Mod_unit'] + 
                                        vmb_concat['Custo_insumo_unit']) + (vmb_concat['Custo_Sobre_Venda'] * vmb_concat['Valor_líquido_unit'])

    vmb_concat['Margem_contribuição_unit_R$'] = vmb_concat['Valor_líquido_unit'] - vmb_concat['Custo_direto_unit']
    vmb_concat['Margem_contribuição_unit_%'] = vmb_concat['Margem_contribuição_unit_R$']/vmb_concat['Valor_líquido_unit']

    ## Antes de opção filtrada, vamos mostrar análises compiladas
    base_gp_geral = vmb_concat.copy()

    groupby_geral = base_gp_geral.groupby(['Mês venda']).agg({'Quantidade' : 'sum',
                                                                'Valor_líquido_unit' : 'mean',
                                                                'Margem_contribuição_unit_R$' : 'mean',
                                                                'Margem_contribuição_unit_%' : 'mean'}).reset_index()

    def ordenar_por_mes(df, coluna_mes):
        ordem_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
        meses_presentes = [mes for mes in ordem_meses if mes in df[coluna_mes].values]
        
        df[coluna_mes] = pd.Categorical(df[coluna_mes], categories=meses_presentes, ordered=True)
        return df.sort_values(coluna_mes)

    groupby_geral = ordenar_por_mes(groupby_geral, 'Mês venda')

    return groupby_geral , ordenar_por_mes

########################################################################################################
#Função geradora de gráfico geral

def graficos_gerais(groupby_geral):
    fig_dashboard = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Quantidade de Vendas', 'Valor Unitário (R$)', 
                    'Margem Contribuição (R$)', 'Margem Contribuição (%)'),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    # Subplot 1: Quantidade (Barras)
    fig_dashboard.add_trace(
        go.Bar(x=groupby_geral['Mês venda'], y=groupby_geral['Quantidade'], name='Quantidade',
            marker_color='blue', hovertemplate='Quantidade: %{y:,}'),
        row=1, col=1
    )

    # Subplot 2: Valor Unitário (Linha)
    fig_dashboard.add_trace(
        go.Scatter(x=groupby_geral['Mês venda'], y=groupby_geral['Valor_líquido_unit'], 
                name='Valor Unitário', mode='lines+markers',
                line=dict(color='green', width=3),
                hovertemplate='Valor: R$ %{y:.2f}'),
        row=1, col=2
    )

    # Subplot 3: Margem R$ (Linha)
    fig_dashboard.add_trace(
        go.Scatter(x=groupby_geral['Mês venda'], y=groupby_geral['Margem_contribuição_unit_R$'], 
                name='Margem R$', mode='lines+markers',
                line=dict(color='red', width=3),
                hovertemplate='Margem: R$ %{y:.2f}'),
        row=2, col=1
    )

    # Subplot 4: Margem % (Linha)
    fig_dashboard.add_trace(
        go.Scatter(x=groupby_geral['Mês venda'], y=groupby_geral['Margem_contribuição_unit_%'], 
                name='Margem %', mode='lines+markers',
                line=dict(color='purple', width=3),
                hovertemplate='Margem: %{y:.2%}'),
        row=2, col=2
    )

    fig_dashboard.update_layout(
        height=600,
        title_text="Dashboard Completo - Evolução Mensal",
        showlegend=False,
        hovermode='x unified'
    )

    # Formatar eixos Y
    fig_dashboard.update_yaxes(title_text="Quantidade", row=1, col=1)
    fig_dashboard.update_yaxes(title_text="Valor (R$)", row=1, col=2, tickprefix="R$ ")
    fig_dashboard.update_yaxes(title_text="Margem (R$)", row=2, col=1, tickprefix="R$ ")
    fig_dashboard.update_yaxes(title_text="Margem (%)", row=2, col=2, tickformat=".1%")

    return fig_dashboard

########################################################################################################