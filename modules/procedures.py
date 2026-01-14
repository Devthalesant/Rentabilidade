import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.vmb import criando_df_final_Rentabilidade
from Functions.Procedures_func import *
from Functions.dictionaries import obter_dicionarios
from Functions.mongo import *
import io
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import locale

def procedimentos():

    st.title("✨Anialise de Procedimentos✨")
    st.info("""
    📈 **Análise Descendente: Do Geral ao Específico**

    Explore o comportamento dos Procedimentos através de diferentes perspectivas:

    • **Visão Temporal:** Evolução mensal dos procedimentos  
    • **Visão por Unidade:** Desempenho individual de cada unidade   
    • **Métricas Chave:** Quantidades e Margens de Contribuição  
    • **Visualização Intuitiva:** Dados complexos apresentados de forma clara

    Ideal para identificação de tendências e tomada de decisão estratégica.
    """)
    st.markdown("---")
    #Trazendo dicionário que posso precisar
    Appointments_dic, Sales_dic, Month_dic, duration_dic, all_costs_2024, all_costs_2025,all_costs_2025_black = obter_dicionarios()

    # Chamando funções
    vmb_concat,df_taxas =  tratando_base_procedimentos()
    df_custos = extrair_todos_custos(all_costs_2025)
    groupby_geral, ordenar_por_mes = gerar_dados_agrupados_gerais(vmb_concat,df_custos,df_taxas)

    # Mostrar dados
    st.subheader("📋 Dados de Vendas - Geral")
    st.dataframe(groupby_geral)
    st.markdown("---")

    meses_ocorridos = groupby_geral['Mês venda'].unique().tolist()

    # GRÁFICO: Dashboard Interativo com Subplots
    st.subheader(f"Análise Gráfica do Período - {meses_ocorridos[0]} - {meses_ocorridos[-1]}")
    st.info("""
    📈 **Evolução Consolidada dos KPI's**

    Estes gráficos trazem uma visão global do desempenho mensal:

    • **Perspectiva Ampliada:** Análise independente de cortes específicos  
    • **Métricas Principais:** Evolução das margens e quantidades totais  
    • **Visão Estratégica:** Tendências gerais dos indicadores  
    """)

    fig_dashboard = graficos_gerais(groupby_geral)

    st.plotly_chart(fig_dashboard, use_container_width=True)


    # ###  Definindo os Filtros
    st.subheader(f"Análise Gráfica Filtrada")
    base_gp_filtrada = vmb_concat.copy()

    unidades_filter = sorted(base_gp_filtrada["Unidade"].unique().tolist())

    meses_filter = ['TODAS']  + ['Janeiro','Fevereiro','Março','Abril','Maio',
                            'Junho','Julho','Agosto','Setembro','Outubro',
                            'Novembro','Dezembro']

    procedimentos_filter = sorted(base_gp_filtrada["Procedimento_padronizado"].unique().tolist())

    grupos_filter = sorted(base_gp_filtrada["Grupo procedimento"].unique().tolist())

    st.markdown("---")
        # Container para as análises
    with st.container():
        st.header("📊 Unidades X Produto Específico")

        col1,col2 = st.columns(2)
        with col1:
            unidade_selecao = st.selectbox("Selecione Uma Unidade:",unidades_filter,index=None)
        with col2:
            produto_selecao = st.selectbox("Selecione Um Procedimentos:",procedimentos_filter,index=None)
        
        if unidade_selecao and produto_selecao:
                
                ## Aqui começaremos a função, ela precisa receber somente o base_gp_filtrada
                # def Unidades_X_Procedimento(base_gp_filtrada):
                base_gp_filtrada_1 = base_gp_filtrada.loc[(base_gp_filtrada['Unidade'] == unidade_selecao) &
                                                        (base_gp_filtrada['Procedimento_padronizado'] == produto_selecao)]
                
                base_gp_filtrada_1['Faturamento_orçamento'] = base_gp_filtrada_1['Quantidade'] * base_gp_filtrada_1['Valor_líquido_unit']
                base_gp_filtrada_1['Custo_direto_orçamento'] = base_gp_filtrada_1['Quantidade'] * base_gp_filtrada_1['Custo_direto_unit']
                base_gp_filtrada_1['Margem_contribuição_orçamento'] = base_gp_filtrada_1['Quantidade'] * base_gp_filtrada_1['Margem_contribuição_unit_R$']


                valor_total_vendido = base_gp_filtrada_1['Faturamento_orçamento'].sum()
                quantidade_total_vendida = base_gp_filtrada_1['Quantidade'].sum()
                custo_direto_total = base_gp_filtrada_1['Custo_direto_orçamento'].sum()
                Margem_contribuicao_total = base_gp_filtrada_1['Margem_contribuição_orçamento'].sum()
                margem_contribuicao_2 = Margem_contribuicao_total/valor_total_vendido * 100

                col1 , col2, col3 = st.columns(3)

                with col1:
                    st.metric("Valor Total Vendido:", f"R$ {valor_total_vendido:,.2f}")
                    st.metric("Quantidade Total Vendida", f"{quantidade_total_vendida:,.0f}")

                with col2:
                    st.metric("Custo Direto Total:", f"R$ {custo_direto_total:,.2f}")
                    

                with col3:
                    st.metric("Margem de Contribuição Total", f"R$ {Margem_contribuicao_total:,.2f}")
                    st.metric("Margem de Contribuição Total (%)", f"{margem_contribuicao_2:,.2f}%")



                base_gp_final_1 = base_gp_filtrada_1.groupby(['Mês venda']).agg({'Quantidade' : 'sum',
                                                                                'Valor_líquido_unit' : 'mean',
                                                                                'Margem_contribuição_unit_R$' : 'mean',
                                                                                'Margem_contribuição_unit_%' : 'mean'}).reset_index()
                
                
                
                base_gp_final_1 = ordenar_por_mes(base_gp_final_1, 'Mês venda')
            
                ## Gráfico de Quantidade Cruzado com Preço praticado mes a mes
                fig_combinado = go.Figure()

                # Barras para Quantidade (eixo Y esquerdo)
                fig_combinado.add_trace(go.Bar(
                    x=base_gp_final_1["Mês venda"],
                    y=base_gp_final_1["Quantidade"],
                    name="Quantidade",
                    marker_color='blue',
                    opacity=0.7,
                    width=0.4,  # Largura da barra
                    offset=-0.2  # Desloca para esquerda
                ))

                # Barras para Valor Unitário (eixo Y direito)
                fig_combinado.add_trace(go.Bar(
                    x=base_gp_final_1["Mês venda"],
                    y=base_gp_final_1["Valor_líquido_unit"], 
                    name="Valor Unitário",
                    marker_color='green',
                    opacity=0.7,
                    yaxis="y2",
                    width=0.4,  # Largura da barra
                    offset=0.2   # Desloca para direita
                ))

                fig_combinado.update_layout(
                    title="Quantidade e Preço Praticado Mês a Mês",
                    xaxis_title="Mês venda",
                    yaxis=dict(
                        title="Quantidade",
                        title_font=dict(color="blue"),
                        tickfont=dict(color="blue")
                    ),
                    yaxis2=dict(
                        title="Valor Unitário (R$)",
                        title_font=dict(color="green"),
                        tickfont=dict(color="green"),
                        overlaying="y",
                        side="right",
                        tickformat=".2f",
                        tickprefix="R$ "
                    ),
                    barmode='group'
                )

                st.plotly_chart(fig_combinado, use_container_width=True)

                ## Gráfico de evolução de Preço praticado
                fig_margem = go.Figure(data=[
                    go.Bar(x=base_gp_final_1["Mês venda"], 
                        y=base_gp_final_1["Margem_contribuição_unit_R$"])
                ])

                fig_margem.update_layout(
                    title="Margem de Contribuição Mês a Mês",
                    xaxis_title="Mês venda",
                    yaxis_title="Margem de Contribuição"
                )

                # Formata o eixo Y como moeda brasileira
                fig_margem.update_yaxes(
                    tickprefix="R$ ",
                    tickformat=",.2f",
                )

                st.plotly_chart(fig_margem, use_container_width=True)

                st.header("Base De Dados")
                st.dataframe(base_gp_final_1)



        else:
            st.warning("Preencha informações nos dois Filtros Solicitados !")