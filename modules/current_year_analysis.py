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
    st.caption("Painel gerencial de desempenho e resultado financeiro")

    data = dados_completos_cache()

    pedidos, clientes, faturamento_total, custo_total, resultado_periodo = gerar_kpis_1()

    faturamento_total_fmt = formatar_real_resumido(faturamento_total)
    custo_total_fmt = formatar_real_resumido(custo_total)
    resultado_periodo_fmt = formatar_real_resumido(resultado_periodo)

    st.markdown("### Indicadores Operacionais")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Pedidos", pedidos)

    with col2:
        st.metric("Clientes", clientes)

    st.markdown("### Indicadores Financeiros")
    col3, col4, col5 = st.columns(3)

    with col3:
        st.metric("Faturamento Total", faturamento_total_fmt)

    with col4:
        st.metric("Custo Total", custo_total_fmt)

    with col5:
        st.metric("Resultado Período", resultado_periodo_fmt)

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

    
    st.header("💉 Análise de Produtos")
    st.caption("Análise consolidada por categoria, com participação no total de receita, tempo vendido e lucro.")

    # =========================
    # FILTROS
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        selecionar_mes_produtos = st.selectbox(
            "Selecione um mês para filtrar Produtos",
            mes_disponiveis_list
        )

    with col2:
        unidade_selecionada_produtos = st.selectbox(
            "Selecione a Unidade",
            unidades
        )

# =========================
# FILTRO DA BASE
# =========================
    data_for_procedures = data.copy()

    if selecionar_mes_produtos != "PERÍODO":
        data_for_procedures = data_for_procedures.loc[
            data_for_procedures["Mês"] == selecionar_mes_produtos
        ]

    if unidade_selecionada_produtos != "TODAS":
        data_for_procedures = data_for_procedures.loc[
            data_for_procedures["Unidade"] == unidade_selecionada_produtos
        ]

    # =========================
    # AGRUPAMENTO
    # =========================
    data_for_procedures_gp = gerar_groupby_para_analise_de_procedimento(data_for_procedures)
    data_for_procedures_gp = data_for_procedures_gp.loc[data_for_procedures_gp["Categoria"] != "UNMAPPED"].copy()

    # =========================
    # KPIs MACRO
    # =========================
    tempo_total_vendido_procedimentos = data_for_procedures_gp["Tempo_Vendido"].sum()
    receita_total_procedimentos = data_for_procedures_gp["Receita_Gerada"].sum()
    lucro_total_procedimentos = data_for_procedures_gp["Lucro_Líquido"].sum()

    st.markdown("### Visão Geral")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Receita Total Gerada",
            formatar_real_resumido(receita_total_procedimentos),
            help="Esse Valor considera a coluna valor líquido item, por isso tende a ser maior que o faturamento real."
        )

    with col2:
        st.metric(
            "Tempo Total Vendido",
            formatar_minutos(tempo_total_vendido_procedimentos)
        )

    with col3:
        st.metric(
            "Resultado Total Gerado",
            formatar_real_resumido(lucro_total_procedimentos)
        )

    # =========================
    # CATEGORIAS
    # =========================
    lista_de_categorias = sorted(data_for_procedures_gp["Categoria"].dropna().unique().tolist())

    st.markdown("### Análise por Categoria")

    tabs = st.tabs(lista_de_categorias)

    for tab, categoria in zip(tabs, lista_de_categorias):
        with tab:
            df_categoria = data_for_procedures_gp.loc[
                data_for_procedures_gp["Categoria"] == categoria
            ].copy()

            receita_gerada_categoria = df_categoria["Receita_Gerada"].sum()
            tempo_vendido_categoria = df_categoria["Tempo_Vendido"].sum()
            lucro_total_categoria = df_categoria["Lucro_Líquido"].sum()

            represent_receita_categoria = calcular_representatividade(
                receita_gerada_categoria, receita_total_procedimentos
            )
            represent_tempo_categoria = calcular_representatividade(
                tempo_vendido_categoria, tempo_total_vendido_procedimentos
            )
            represent_lucro_categoria = calcular_representatividade(
                lucro_total_categoria, lucro_total_procedimentos
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Receita da Categoria",
                    formatar_real_resumido(receita_gerada_categoria),
                    delta=f"{formatar_percentual(represent_receita_categoria)} do total",
                    delta_color="off"
                )

            with col2:
                st.metric(
                    "Tempo da Categoria",
                    formatar_minutos(tempo_vendido_categoria),
                    delta=f"{formatar_percentual(represent_tempo_categoria)} do total",
                    delta_color="off"
                )

            with col3:
                st.metric(
                    "Resultado da Categoria",
                    formatar_real_resumido(lucro_total_categoria),
                    # delta=f"{formatar_percentual(represent_lucro_categoria)} do total",
                    # delta_color="off"
                )

            st.markdown("#### Detalhamento")
            df_categoria = df_categoria.sort_values(by="Lucro_Líquido", ascending=False)
            st.dataframe(
                estilizar_dataframe(
                    df_categoria,
                    cols_percentual=["Margem_de_Contribuição", "Lucro_Líquido_%"],
                    cols_monetario=["Preço_Praticado", "Receita_Gerada", "Custo_Direto",
                                    "Custo_Fixo","Custo_Total","Lucro_Líquido"],
                    cols_verde_negativo=None,
                    cols_escala_cor=['Lucro_Líquido', 'Receita_Gerada'],
                    verde_menor=False
                )
                )



    ## Adicionar a esses KPI`s valores pagos em :Impostos, comissão(proxy), MOD, Produtos, Insumos, CF e quanto representam do total do Custo
    st.subheader("💉 Produto Específico")

    with st.expander("Clique aqui para uma análise mais específica"):
        data_for_specific_procedure = data.copy()

        lista_de_procedimentos = sorted(
            data_for_specific_procedure["Procedimento_padronizado"].dropna().unique().tolist()
        )

        col1, col2 = st.columns(2)

        with col1:
            procedimento_selecionado_specific = st.selectbox(
                "Selecione um Procedimento:",
                options=lista_de_procedimentos,
                index=None,
                placeholder="Escolha um procedimento"
            )

        with col2:
            unidade_selecionada_produtos_specific = st.selectbox(
                "Selecione a Unidade:",
                unidades
            )

        if not procedimento_selecionado_specific:
            st.info("Selecione pelo menos um procedimento para visualizar a evolução mensal.")
            st.stop()

        data_for_specific_procedure = data_for_specific_procedure.loc[
            data_for_specific_procedure["Procedimento_padronizado"] == procedimento_selecionado_specific
        ]

        if unidade_selecionada_produtos_specific != "TODAS":
            data_for_specific_procedure = data_for_specific_procedure.loc[
                data_for_specific_procedure["Unidade"] == unidade_selecionada_produtos_specific
            ]

        if data_for_specific_procedure.empty:
            st.warning("Não há dados para esse procedimento com os filtros selecionados.")
            st.stop()

        ordem_meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]

        meses_com_dados = data_for_specific_procedure["Mês"].dropna().unique().tolist()
        meses_com_dados_ordenados = [mes for mes in ordem_meses if mes in meses_com_dados]

        # Base real: somente meses existentes
        gp_specific_procedure_real = (
            data_for_specific_procedure.groupby(
                ["Procedimento_padronizado", "Mês"],
                as_index=False
            )
            .agg({
                "Quantidade": "sum",
                "Valor_unitário": "mean",
                "Valor liquido item": "sum"
            })
            .rename(columns={
                "Valor_unitário": "Preço_Praticado",
                "Valor liquido item": "Receita_Gerada"
            })
        )

        gp_specific_procedure_real["Mês"] = pd.Categorical(
            gp_specific_procedure_real["Mês"],
            categories=ordem_meses,
            ordered=True
        )
        gp_specific_procedure_real = gp_specific_procedure_real.sort_values("Mês")

        # Base plot: todos os meses, com zero
        gp_specific_procedure_plot = preencher_meses_faltantes_com_zero(
            gp_specific_procedure_real,
            coluna_mes="Mês",
            colunas_valores=["Quantidade", "Preço_Praticado", "Receita_Gerada"]
        )

        gp_specific_procedure_plot["Mês"] = pd.Categorical(
            gp_specific_procedure_plot["Mês"],
            categories=ordem_meses,
            ordered=True
        )
        gp_specific_procedure_plot = gp_specific_procedure_plot.sort_values("Mês")

        # KPIs
        quantidade_total = gp_specific_procedure_real["Quantidade"].sum()

        gp_preco_existente = gp_specific_procedure_real.loc[
            gp_specific_procedure_real["Mês"].isin(meses_com_dados_ordenados)
        ].copy()

        preco_medio_simples = gp_preco_existente["Preço_Praticado"].mean()
        preco_medio_ponderado = calcular_preco_medio_ponderado(
            gp_preco_existente,
            coluna_preco="Preço_Praticado",
            coluna_qtd="Quantidade"
        )

        receita_total_periodo = gp_specific_procedure_real["Receita_Gerada"].sum()

        melhor_mes_receita = gp_specific_procedure_real.loc[
            gp_specific_procedure_real["Receita_Gerada"].idxmax(), "Mês"
        ]
        melhor_receita = gp_specific_procedure_real["Receita_Gerada"].max()

        pior_mes_receita = gp_specific_procedure_real.loc[
            gp_specific_procedure_real["Receita_Gerada"].idxmin(), "Mês"
        ]
        pior_receita = gp_specific_procedure_real["Receita_Gerada"].min()

        st.markdown("### Resumo do Procedimento")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Quantidade Total",
                formatar_numero_inteiro(quantidade_total)
            )

        with col2:
            st.metric(
                "Preço Médio Simples",
                formatar_para_real(preco_medio_simples)
            )

        with col3:
            st.metric(
                "Preço Médio Ponderado",
                formatar_para_real(preco_medio_ponderado)
            )

        with col4:
            st.metric(
                "Receita Total Gerada",
                formatar_real_resumido(receita_total_periodo)
            )

        col1, col2 = st.columns(2)

        with col1:
            st.caption(
                f"Melhor mês de receita: **{melhor_mes_receita}** • {formatar_para_real(melhor_receita)}"
            )

        with col2:
            st.caption(
                f"Pior mês de receita: **{pior_mes_receita}** • {formatar_para_real(pior_receita)}"
            )

        st.markdown("### Evolução Mensal")

        tab1, tab2, tab3 = st.tabs([
            "Quantidade",
            "Preço Praticado",
            "Receita Gerada"
        ])

        with tab1:
            fig_qtd = criar_grafico_barras_com_media_movel(
                df_plot=gp_specific_procedure_plot,
                df_real=gp_specific_procedure_real,
                coluna_mes="Mês",
                coluna_valor="Quantidade",
                titulo="Evolução Mensal da Quantidade",
                tipo_valor="numero",
                janela_media=3,
                nome_barra="Quantidade",
                nome_linha="Média móvel (3 meses)",
                cor_barra="#8E44AD",
                cor_linha="#5B2C6F"
            )
            st.plotly_chart(fig_qtd, use_container_width=True)

        with tab2:
            fig_preco = criar_grafico_barras_com_media_movel(
                df_plot=gp_specific_procedure_plot,
                df_real=gp_specific_procedure_real,
                coluna_mes="Mês",
                coluna_valor="Preço_Praticado",
                titulo="Evolução Mensal do Preço Praticado",
                tipo_valor="moeda",
                janela_media=3,
                nome_barra="Preço Praticado",
                nome_linha="Média móvel (3 meses)",
                cor_barra="#2471A3",
                cor_linha="#154360"
            )
            st.plotly_chart(fig_preco, use_container_width=True)

        with tab3:
            fig_receita = criar_grafico_barras_com_media_movel(
                df_plot=gp_specific_procedure_plot,
                df_real=gp_specific_procedure_real,
                coluna_mes="Mês",
                coluna_valor="Receita_Gerada",
                titulo="Evolução Mensal da Receita Gerada",
                tipo_valor="moeda",
                janela_media=3,
                nome_barra="Receita Gerada",
                nome_linha="Média móvel (3 meses)",
                cor_barra="#17A589",
                cor_linha="#0E6251"
            )
            st.plotly_chart(fig_receita, use_container_width=True)

        st.markdown("### Detalhamento Mensal")

        # Detalhamento apenas com meses reais
        df_detalhamento = gp_specific_procedure_real.copy()

        df_detalhamento = adicionar_variacao_percentual(
            df_detalhamento,
            "Quantidade",
            "% Var. Quantidade"
        )
        df_detalhamento = adicionar_variacao_percentual(
            df_detalhamento,
            "Preço_Praticado",
            "% Var. Preço"
        )
        df_detalhamento = adicionar_variacao_percentual(
            df_detalhamento,
            "Receita_Gerada",
            "% Var. Receita"
        )

        df_exibicao_specific = preparar_df_exibicao_specific(df_detalhamento)

        st.dataframe(
            df_exibicao_specific[
                [
                    "Mês",
                    "Quantidade",
                    "% Var. Quantidade",
                    "Preço_Praticado",
                    "% Var. Preço",
                    "Receita_Gerada",
                    "% Var. Receita"
                ]
            ],
            use_container_width=True
        )

##COmeçar análise de Ociosidade
    st.header("Tempo, Taxas e Ociosidade:")
    df_tempo = carregar_tempo_unidade_mes(ano=2026,mes=None,periodos=None,periodo=None)
    st.dataframe(df_tempo)