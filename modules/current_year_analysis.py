import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.vmb import *
from Functions.mongo import *
from Functions.treating_data_for_pages import *
import io
from Functions.dictionaries import Month_dic
from Functions.dictionaries_2 import *
from Functions.graphic_functions import *
from Functions.tratar_dados_format import *
import plotly.graph_objects as go
import locale

def page_current_year():

    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    mes_str_atual = Month_dic[mes_atual]
    mes_passado = mes_atual - 1 
    mes_passado_str = Month_dic[mes_passado]

    anos_dados_len = ano_atual - 2024

    def formatar_para_real(valor):
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    ## garantindo que o período de busca retroativa comtemple apenas os dois anoa anteriores: 
    if anos_dados_len > 2: 
        while anos_dados_len > 2:
            anos_dados_len -= 1

    @st.cache_data(ttl=3600)
    def dados_completos_cache():
        return consultar_dados_mongo("rentabilidade_anual", "Base_Rentabilidade_mensal", ano_atual)
    
    @st.cache_data(ttl=3600)
    def gerar_kpis_1():
        return gerar_kpis_gerais_current_year(data)
    
    @st.cache_data(ttl=3600)
    def dados_retorativos_cache():
        return consultar_dados_mongo("rentabilidade_anual","Base_Rentabilidade_mensal",periodo=lista_de_periodos_busca)

    st.title(f"Análises de Rentabilidade - {ano_atual}")
    data = dados_completos_cache()
    
    pedidos, clientes, faturamento_total, custo_total, resultado_periodo  = gerar_kpis_1()

    faturamento_total = formatar_para_real(faturamento_total)
    custo_total = formatar_para_real(custo_total)
    resultado_periodo = formatar_para_real(resultado_periodo)

    col1,col2,col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            with st.container(border=True):
                st.metric("Pedidos", pedidos)
            with st.container(border=True):
                st.metric("Clientes", clientes)
    with col2:
        with st.container(border=True):
            with st.container(border=True):
                st.metric("Faturamento Total", faturamento_total)
            with st.container(border=True):
                st.metric("Custo Total",custo_total)
    with col3:
        with st.container(border=True):
            with st.container():
                with st.container(border=True):
                    st.metric("Resultado Período",resultado_periodo)

    st.header("📊Evolução Mensal de Faturamento e Custo (Comparação entre Anos)")
    ## Trazendo dados dos anos anteriores para comparar performance:
    lista_de_periodos_busca = []

    while anos_dados_len > 0:
        ano_atual -= 1
        for m in data['Mes_num'].unique():
            periodo_busca_retroativa = f"{ano_atual}-{m}"
            lista_de_periodos_busca.append(periodo_busca_retroativa)
        anos_dados_len -= 1
        
    ## puxando os dados retroativos dos períodos passados:
    dados_retroativos = dados_retorativos_cache()

    ## opção de seleção de quadrimetre para uma melehor visualização (UX)
    quadrimestres = ['1°- QUADRIMESTRE','2°- QUADRIMESTRE','3°- QUADRIMESTRE']
    unidades = ['TODAS']
    unidades.extend(sorted(data['Unidade'].unique().tolist()))

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            quadrimestre_selecionado = st.selectbox("Selecione o Período que deseja Visualizar:",quadrimestres)
    with col2:
        with st.container(border=True):
            unidade_selecionada = st.selectbox("Selecione Uma Unidade:",unidades)

    ## pegando so dados em dic para gerar gráfico
    lista_de_kpis_retroativos = gerar_dados_quadrimestrais_atual_e_retroativo(dados_retroativos,data,quadrimestre_selecionado,unidade_selecionada)

    ## Gerando o gráfico comparativo de faturamento e custo total atual X retroativo (Y-2 Max)
    fig = grafico_faturamento_custo_comparativo(lista_de_kpis_retroativos,quadrimestre_selecionado)
    st.plotly_chart(fig, use_container_width=True)

    ## Fazendo Rankings de Rentabilidade e Custo com filtro mensal ou período.
    st.header("Rankings de Rentabilidade e Custos")
    mes_disponiveis_list = ['PERÍODO']
    mes_disponiveis_list.extend(data['Mês'].unique().tolist())
    selecionar_mes_ranking = st.selectbox('Selecione um mês para filtrar os Rankings', mes_disponiveis_list)

    if selecionar_mes_ranking == 'PERÍODO':
        data_for_ranking = data.copy()
    else:
        data_for_ranking = data.loc[data['Mês'] == selecionar_mes_ranking]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('🏆Ranking de Rentabilidade')
        ranking_rentabilidade_gp = data_for_ranking.groupby(['Unidade']).agg({'Lucro_líquido_item' : 'sum'}).reset_index()
        ranking_rentabilidade_gp = ranking_rentabilidade_gp.sort_values(by=['Lucro_líquido_item'],ascending=False)
        ranking_rentabilidade_gp = ranking_rentabilidade_gp.rename(columns={'Lucro_líquido_item' : 'Resultado'}).reset_index(drop=True)
        ranking_rentabilidade_gp = formatar_brl_for_dataframes(ranking_rentabilidade_gp,'Resultado')
        st.dataframe(ranking_rentabilidade_gp,use_container_width=True)

    with col2:
        st.subheader('💸Ranking de Custos')
        ranking_custos_dp = data_for_ranking.groupby(['Unidade']).agg({'Custo_total_procedimento' : 'sum'}).reset_index()
        ranking_custos_dp = ranking_custos_dp.sort_values(by=['Custo_total_procedimento'],ascending=True)
        ranking_custos_dp = ranking_custos_dp.rename(columns={'Custo_total_procedimento' : 'Custo_Total'}).reset_index(drop=True)
        ranking_custos_dp = mapa_calor_brl(ranking_custos_dp,'Custo_Total')
        st.dataframe(ranking_custos_dp,use_container_width=True)

    
    st.header("💉Análise de Produtos")
    ## Validar Base de fevereiro, está faltando coisa...

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            selecionar_mes_produtos = st.selectbox(
                'Selecione um mês para filtrar Produtos',
                mes_disponiveis_list
            )

    with col2:
        with st.container(border=True):
            unidade_selecionada_produtos = st.selectbox(
                "Selecione a Unidade:",
                unidades
            )

    data_for_procedures = data.copy()

    if selecionar_mes_produtos != 'PERÍODO':
        data_for_procedures = data_for_procedures.loc[
            data_for_procedures['Mês'] == selecionar_mes_produtos
        ]

    if unidade_selecionada_produtos != 'TODAS':
        data_for_procedures = data_for_procedures.loc[
            data_for_procedures['Unidade'] == unidade_selecionada_produtos
        ]

    data_for_procedures_gp = data_for_procedures.groupby(['Procedimento_padronizado']).agg({'Valor_unitário' : 'mean',
                                                                                            'Quantidade' : 'sum',
                                                                                            'Valor liquido item' : 'sum',
                                                                                            'Custo_direto_procedimento' : 'sum',
                                                                                            'Custo_fixo' : 'sum',
                                                                                            'Custo_total_procedimento' : 'sum',
                                                                                            'Lucro_líquido_item' : 'sum',
                                                                                            'Lucro_líquido_item_%' : 'mean'}).reset_index()
    
    data_for_procedures_gp = data_for_procedures_gp.rename(columns={'Valor_unitário' : 'Preço_Praticado',
                                                                    'Valor liquido item' : 'Receita_Gerada',
                                                                    'Custo_direto_procedimento' : 'Custo_Direto',
                                                                    'Custo_fixo' : 'Custo_Fixo',
                                                                    'Custo_total_procedimento' : 'Custo_Total',
                                                                    'Lucro_líquido_item' : 'Lucro_Líquido',
                                                                    'Lucro_líquido_item_%' : 'Lucro_Líquido_%'}).reset_index(drop=True)
    
    
    data_for_procedures_gp['Margem_de_Contribuição'] = data_for_procedures_gp['Custo_Direto'] / data_for_procedures_gp['Receita_Gerada']

    data_for_procedures_gp_columns = ['Procedimento_padronizado','Preço_Praticado','Quantidade','Receita_Gerada',
                                      'Custo_Direto','Margem_de_Contribuição','Custo_Fixo','Custo_Total',
                                      'Lucro_Líquido','Lucro_Líquido_%']

    data_for_procedures_gp = data_for_procedures_gp[data_for_procedures_gp_columns]

    data_for_procedures_gp = data_for_procedures_gp.sort_values(by=['Receita_Gerada'],ascending=False).reset_index(drop=True)

    st.dataframe(
        estilizar_dataframe(
            data_for_procedures_gp,
            cols_percentual=["Margem_de_Contribuição", "Lucro_Líquido_%"],
            cols_monetario=["Preço_Praticado", "Receita_Gerada", "Custo_Direto",
                            "Custo_Fixo","Custo_Total","Lucro_Líquido"],
            cols_verde_negativo=None,
            cols_escala_cor=['Lucro_Líquido_%', 'Receita_Gerada'],
            verde_menor=False
        )
        )










    


