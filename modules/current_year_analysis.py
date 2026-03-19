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
from Functions.dictionaries import Month_dic_number_str
from Functions.dictionaries_2 import *
from Functions.graphic_functions import *
from Functions.tratar_dados_format import *
import plotly.graph_objects as go
import locale
from Functions.dictionaries import *

from Functions.ui import (
    aplicar_ui_pro_rentabilidade,
    render_kpi_financeiro,
    render_kpi_operacional,
    render_section_label,
    abrir_card_ui,
    fechar_card_ui,
)


def page_current_year():

    ano_atual        = datetime.now().year
    mes_atual        = datetime.now().month
    mes_passado      = mes_atual - 1
    mes_passado_str  = Month_dic[mes_passado]

    # quantos anos retroativos buscar (máx 2)
    anos_dados_len = min(ano_atual - 2024, 2)

    # ── CSS + header ─────────────────────────────────────────────────────────
    aplicar_ui_pro_rentabilidade(
        page_title="Análise de <em>Rentabilidade</em>",
        subtitle="Painel gerencial de desempenho e resultado financeiro",
        ano=ano_atual,
        mes_referencia=f"{mes_passado_str[:3]} {ano_atual}",
    )

    # ── dados do ano corrente ─────────────────────────────────────────────────
    @st.cache_data(ttl=3600)
    def dados_completos_cache(_ano):
        return consultar_dados_mongo("rentabilidade_anual", "Base_Rentabilidade_mensal", _ano)

    data = dados_completos_cache(ano_atual)

    # ── lista de períodos retroativos (montada ANTES do cache que a usa) ──────
    lista_de_periodos_busca = []
    _ano_ref  = ano_atual
    _anos_len = anos_dados_len

    while _anos_len > 0:
        _ano_ref -= 1
        for m in data['Mes_num'].unique():
            lista_de_periodos_busca.append(f"{_ano_ref}-{m}")
        _anos_len -= 1

    @st.cache_data(ttl=3600)
    def dados_retroativos_cache(_periodos):
        return consultar_dados_mongo(
            "rentabilidade_anual", "Base_Rentabilidade_mensal", periodo=list(_periodos)
        )

    dados_retroativos = dados_retroativos_cache(tuple(lista_de_periodos_busca))

    # ── KPIs gerais ───────────────────────────────────────────────────────────
    @st.cache_data(ttl=3600)
    def kpis_gerais_cache(_ano):
        _data = dados_completos_cache(_ano)
        return gerar_kpis_gerais_current_year(_data)

    pedidos, clientes, faturamento_total, custo_total, resultado_periodo = kpis_gerais_cache(ano_atual)

    faturamento_total_fmt = formatar_real_resumido(faturamento_total)
    custo_total_fmt       = formatar_real_resumido(custo_total)
    resultado_periodo_fmt = formatar_real_resumido(resultado_periodo)

    # ── SEÇÃO: KPIs financeiros ───────────────────────────────────────────────
    render_section_label("Indicadores Financeiros")
    col1, col2, col3 = st.columns(3)

    with col1:
        render_kpi_financeiro("Faturamento Total",    faturamento_total_fmt,  tipo="faturamento")
    with col2:
        render_kpi_financeiro("Custo Total",          custo_total_fmt,        tipo="custo")
    with col3:
        render_kpi_financeiro("Resultado do Período", resultado_periodo_fmt,  tipo="resultado")

    # ── SEÇÃO: KPIs operacionais ──────────────────────────────────────────────
    render_section_label("Indicadores Operacionais")
    col1, col2 = st.columns(2)

    with col1:
        render_kpi_operacional("Pedidos",  str(pedidos),  sub="no período", tipo="pedidos")
    with col2:
        render_kpi_operacional("Clientes", str(clientes), sub="únicos",     tipo="clientes")

    # ── SEÇÃO: Evolução Mensal ────────────────────────────────────────────────
    st.header("📊 Evolução Mensal de Faturamento e Custo")
    st.caption("Comparação entre anos")

    unidades      = ['TODAS'] + sorted(data['Unidade'].unique().tolist())
    quadrimestres = ['1°- QUADRIMESTRE', '2°- QUADRIMESTRE', '3°- QUADRIMESTRE']

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            quadrimestre_selecionado = st.selectbox("Período:", quadrimestres)
    with col2:
        with st.container(border=True):
            unidade_selecionada = st.selectbox("Unidade:", unidades)

    lista_de_kpis_retroativos = gerar_dados_quadrimestrais_atual_e_retroativo(
        dados_retroativos, data, quadrimestre_selecionado, unidade_selecionada
    )
    fig = grafico_faturamento_custo_comparativo(lista_de_kpis_retroativos, quadrimestre_selecionado)
    st.plotly_chart(fig, use_container_width=True)

    # ── SEÇÃO: Rankings ───────────────────────────────────────────────────────
    st.header("Rankings de Rentabilidade e Custos")

    mes_disponiveis_list   = ['PERÍODO'] + data['Mês'].unique().tolist()
    selecionar_mes_ranking = st.selectbox('Filtrar Rankings por mês:', mes_disponiveis_list)

    data_for_ranking = (
        data.copy() if selecionar_mes_ranking == 'PERÍODO'
        else data.loc[data['Mês'] == selecionar_mes_ranking]
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('🏆 Ranking de Rentabilidade')
        ranking_rent = (
            data_for_ranking
            .groupby('Unidade').agg({'Lucro_líquido_item': 'sum'}).reset_index()
            .sort_values('Lucro_líquido_item', ascending=False)
            .rename(columns={'Lucro_líquido_item': 'Resultado'})
            .reset_index(drop=True)
        )
        ranking_rent = formatar_brl_for_dataframes(ranking_rent, 'Resultado')
        st.dataframe(ranking_rent, use_container_width=True)

    with col2:
        st.subheader('💸 Ranking de Custos')
        ranking_custo = (
            data_for_ranking
            .groupby('Unidade').agg({'Custo_total_procedimento': 'sum'}).reset_index()
            .sort_values('Custo_total_procedimento', ascending=True)
            .rename(columns={'Custo_total_procedimento': 'Custo_Total'})
            .reset_index(drop=True)
        )
        ranking_custo = mapa_calor_brl(ranking_custo, 'Custo_Total')
        st.dataframe(ranking_custo, use_container_width=True)

    # ── SEÇÃO: Análise de Produtos ────────────────────────────────────────────
    st.header("💉 Análise de Produtos")
    st.caption("Análise consolidada por categoria, com participação no total de receita, tempo vendido e lucro.")

    col1, col2 = st.columns(2)
    with col1:
        selecionar_mes_produtos      = st.selectbox("Mês:", mes_disponiveis_list)
    with col2:
        unidade_selecionada_produtos = st.selectbox("Unidade (Produtos):", unidades)

    data_for_procedures = data.copy()
    if selecionar_mes_produtos != "PERÍODO":
        data_for_procedures = data_for_procedures.loc[data_for_procedures["Mês"] == selecionar_mes_produtos]
    if unidade_selecionada_produtos != "TODAS":
        data_for_procedures = data_for_procedures.loc[data_for_procedures["Unidade"] == unidade_selecionada_produtos]

    data_for_procedures_gp = gerar_groupby_para_analise_de_procedimento(data_for_procedures)
    data_for_procedures_gp = data_for_procedures_gp.loc[data_for_procedures_gp["Categoria"] != "UNMAPPED"].copy()

    tempo_total   = data_for_procedures_gp["Tempo_Vendido"].sum()
    receita_total = data_for_procedures_gp["Receita_Gerada"].sum()
    lucro_total   = data_for_procedures_gp["Lucro_Líquido"].sum()

    render_section_label("Visão Geral de Produtos")
    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi_financeiro(
            "Receita Total Gerada", formatar_real_resumido(receita_total), tipo="faturamento",
            help="Considera a coluna valor líquido item — tende a ser maior que o faturamento real.",
        )
    with col2:
        render_kpi_operacional("Tempo Total Vendido", formatar_minutos(tempo_total), tipo="tempo")
    with col3:
        render_kpi_financeiro("Resultado Total Gerado", formatar_real_resumido(lucro_total), tipo="resultado")

    # ── Tabs por categoria ────────────────────────────────────────────────────
    lista_de_categorias = sorted(data_for_procedures_gp["Categoria"].dropna().unique().tolist())
    st.markdown("### Análise por Categoria")

    for tab, categoria in zip(st.tabs(lista_de_categorias), lista_de_categorias):
        with tab:
            df_cat = data_for_procedures_gp.loc[
                data_for_procedures_gp["Categoria"] == categoria
            ].copy()

            receita_cat = df_cat["Receita_Gerada"].sum()
            tempo_cat   = df_cat["Tempo_Vendido"].sum()
            lucro_cat   = df_cat["Lucro_Líquido"].sum()

            col1, col2, col3 = st.columns(3)
            with col1:
                render_kpi_financeiro(
                    "Receita da Categoria", formatar_real_resumido(receita_cat), tipo="faturamento",
                    delta=f"{formatar_percentual(calcular_representatividade(receita_cat, receita_total))} do total",
                    delta_tipo="off",
                )
            with col2:
                render_kpi_operacional(
                    "Tempo da Categoria", formatar_minutos(tempo_cat), tipo="tempo",
                    sub=f"{formatar_percentual(calcular_representatividade(tempo_cat, tempo_total))} do total",
                )
            with col3:
                render_kpi_financeiro("Resultado da Categoria", formatar_real_resumido(lucro_cat), tipo="resultado")

            st.markdown("#### Detalhamento")
            st.dataframe(
                estilizar_dataframe(
                    df_cat.sort_values("Lucro_Líquido", ascending=False),
                    cols_percentual=["Margem_de_Contribuição", "Lucro_Líquido_%"],
                    cols_monetario=["Preço_Praticado", "Receita_Gerada", "Custo_Direto",
                                    "Custo_Fixo", "Custo_Total", "Lucro_Líquido"],
                    cols_verde_negativo=None,
                    cols_escala_cor=['Lucro_Líquido', 'Receita_Gerada'],
                    verde_menor=False,
                ),
                use_container_width=True,
            )

    # ── Produto específico ────────────────────────────────────────────────────
    st.subheader("💉 Produto Específico")

    with st.expander("Clique aqui para uma análise mais específica"):
        lista_de_procedimentos = sorted(data["Procedimento_padronizado"].dropna().unique().tolist())

        col1, col2 = st.columns(2)
        with col1:
            procedimento_selecionado = st.selectbox(
                "Procedimento:", options=lista_de_procedimentos,
                index=None, placeholder="Escolha um procedimento",
            )
        with col2:
            unidade_specific = st.selectbox("Unidade (Procedimento):", unidades)

        # FIX: st.stop() removido — bloco condicional garante que a página
        # continua renderizando normalmente quando nada está selecionado
        if not procedimento_selecionado:
            st.info("Selecione pelo menos um procedimento para visualizar a evolução mensal.")
        else:
            df_specific = data.loc[data["Procedimento_padronizado"] == procedimento_selecionado].copy()

            if unidade_specific != "TODAS":
                df_specific = df_specific.loc[df_specific["Unidade"] == unidade_specific]

            if df_specific.empty:
                st.warning("Não há dados para esse procedimento com os filtros selecionados.")
            else:
                ordem_meses = [
                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
                ]
                meses_com_dados = df_specific["Mês"].dropna().unique().tolist()
                meses_ordenados = [m for m in ordem_meses if m in meses_com_dados]

                gp_real = (
                    df_specific
                    .groupby(["Procedimento_padronizado", "Mês"], as_index=False)
                    .agg({"Quantidade": "sum", "Valor_unitário": "mean", "Valor liquido item": "sum"})
                    .rename(columns={"Valor_unitário": "Preço_Praticado", "Valor liquido item": "Receita_Gerada"})
                )
                gp_real["Mês"] = pd.Categorical(gp_real["Mês"], categories=ordem_meses, ordered=True)
                gp_real = gp_real.sort_values("Mês")

                gp_plot = preencher_meses_faltantes_com_zero(
                    gp_real, coluna_mes="Mês",
                    colunas_valores=["Quantidade", "Preço_Praticado", "Receita_Gerada"],
                )
                gp_plot["Mês"] = pd.Categorical(gp_plot["Mês"], categories=ordem_meses, ordered=True)
                gp_plot = gp_plot.sort_values("Mês")

                gp_existente          = gp_real.loc[gp_real["Mês"].isin(meses_ordenados)]
                quantidade_total      = gp_real["Quantidade"].sum()
                preco_medio_simples   = gp_existente["Preço_Praticado"].mean()
                preco_medio_ponderado = calcular_preco_medio_ponderado(
                    gp_existente, coluna_preco="Preço_Praticado", coluna_qtd="Quantidade"
                )
                receita_total_periodo = gp_real["Receita_Gerada"].sum()
                melhor_idx            = gp_real["Receita_Gerada"].idxmax()
                pior_idx              = gp_real["Receita_Gerada"].idxmin()

                render_section_label("Resumo do Procedimento")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    render_kpi_operacional("Quantidade Total",      formatar_numero_inteiro(quantidade_total),     tipo="pedidos")
                with col2:
                    render_kpi_operacional("Preço Médio Simples",   formatar_para_real(preco_medio_simples),       tipo="ticket")
                with col3:
                    render_kpi_operacional("Preço Médio Ponderado", formatar_para_real(preco_medio_ponderado),     tipo="ticket")
                with col4:
                    render_kpi_financeiro("Receita Total Gerada",   formatar_real_resumido(receita_total_periodo), tipo="faturamento")

                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Melhor mês: **{gp_real.loc[melhor_idx, 'Mês']}** · {formatar_para_real(gp_real.loc[melhor_idx, 'Receita_Gerada'])}")
                with col2:
                    st.caption(f"Pior mês: **{gp_real.loc[pior_idx, 'Mês']}** · {formatar_para_real(gp_real.loc[pior_idx, 'Receita_Gerada'])}")

                st.markdown("### Evolução Mensal")
                tab1, tab2, tab3 = st.tabs(["Quantidade", "Preço Praticado", "Receita Gerada"])

                with tab1:
                    st.plotly_chart(
                        criar_grafico_barras_com_media_movel(
                            df_plot=gp_plot, df_real=gp_real, coluna_mes="Mês", coluna_valor="Quantidade",
                            titulo="Evolução Mensal da Quantidade", tipo_valor="numero", janela_media=3,
                            nome_barra="Quantidade", nome_linha="Média móvel (3 meses)",
                            cor_barra="#8E44AD", cor_linha="#5B2C6F",
                        ), use_container_width=True,
                    )
                with tab2:
                    st.plotly_chart(
                        criar_grafico_barras_com_media_movel(
                            df_plot=gp_plot, df_real=gp_real, coluna_mes="Mês", coluna_valor="Preço_Praticado",
                            titulo="Evolução Mensal do Preço Praticado", tipo_valor="moeda", janela_media=3,
                            nome_barra="Preço Praticado", nome_linha="Média móvel (3 meses)",
                            cor_barra="#2471A3", cor_linha="#154360",
                        ), use_container_width=True,
                    )
                with tab3:
                    st.plotly_chart(
                        criar_grafico_barras_com_media_movel(
                            df_plot=gp_plot, df_real=gp_real, coluna_mes="Mês", coluna_valor="Receita_Gerada",
                            titulo="Evolução Mensal da Receita Gerada", tipo_valor="moeda", janela_media=3,
                            nome_barra="Receita Gerada", nome_linha="Média móvel (3 meses)",
                            cor_barra="#17A589", cor_linha="#0E6251",
                        ), use_container_width=True,
                    )

                st.markdown("### Detalhamento Mensal")
                df_det = gp_real.copy()
                df_det = adicionar_variacao_percentual(df_det, "Quantidade",      "% Var. Quantidade")
                df_det = adicionar_variacao_percentual(df_det, "Preço_Praticado", "% Var. Preço")
                df_det = adicionar_variacao_percentual(df_det, "Receita_Gerada",  "% Var. Receita")
                df_det = preparar_df_exibicao_specific(df_det)
                st.dataframe(
                    df_det[["Mês", "Quantidade", "% Var. Quantidade",
                             "Preço_Praticado", "% Var. Preço",
                             "Receita_Gerada",  "% Var. Receita"]],
                    use_container_width=True,
                )

    # ── SEÇÃO: Tempo, Taxas e Ociosidade ─────────────────────────────────────
    # Esta seção agora está FORA do expander, no nível correto da função
    st.header("Tempo, Taxas e Ociosidade")

    df_tempo = carregar_tempo_unidade_mes(ano=ano_atual, mes=None, periodos=None, periodo=None)
    st.dataframe(df_tempo)

    minutos_disponiveis = df_tempo['Minutos Disponivel'].sum()
    minutos_pagos       = df_tempo['Tempo Vendido'].sum()
    minutos_ociosos     = df_tempo['Tempo ocioso'].sum()
    custo_da_ociosidade = formatar_real_resumido(df_tempo['Custo da Ociosidade'].sum())

    represent_pagos   = calcular_representatividade(minutos_pagos,   minutos_disponiveis)
    represent_ociosos = calcular_representatividade(minutos_ociosos, minutos_disponiveis)

    render_section_label("Indicadores de Ociosidade")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_operacional("Tempo Disponível", formatar_minutos(minutos_disponiveis), tipo="tempo")
    with col2:
        render_kpi_operacional(
            "Tempo Pago", formatar_minutos(minutos_pagos), tipo="tempo",
            sub=f"{formatar_percentual(represent_pagos)} do disponível",
            delta=formatar_percentual(represent_pagos), delta_tipo="up",
        )
    with col3:
        render_kpi_operacional(
            "Tempo Ocioso", formatar_minutos(minutos_ociosos), tipo="ociosidade",
            sub=f"{formatar_percentual(represent_ociosos)} do disponível",
            delta=formatar_percentual(represent_ociosos), delta_tipo="down",
        )
    with col4:
        render_kpi_financeiro(
            "Custo da Ociosidade", custo_da_ociosidade, tipo="custo",
            help="Não é um custo extra. Representa a parte do custo fixo não absorvida pelos procedimentos vendidos.",
        )

    st.subheader("Evolução Mensal — Ociosidade")

    df_ociosidade = df_tempo.copy()
    df_ociosidade['Ociosidade'] = df_ociosidade['Tempo ocioso'] / df_ociosidade['Minutos Disponivel']
    df_ociosidade_gp = (
        df_ociosidade.groupby('Mes_num')
        .agg({'Ociosidade': 'mean'})
        .reset_index()
    )
    df_ociosidade_gp['Mes_str'] = df_ociosidade_gp['Mes_num'].map(Month_dic_number_str)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_ociosidade_gp["Mes_str"],
        y=df_ociosidade_gp["Ociosidade"],
        text=[f"{v:.0%}" for v in df_ociosidade_gp["Ociosidade"]],
        textposition="outside",
        name="Ociosidade",
    ))
    fig.add_hline(y=0.50, line_dash="dash", annotation_text="Meta: 50%", annotation_position="top left")
    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="Percentual",
        yaxis_tickformat=".0%",
        yaxis=dict(range=[0, 1]),
    )
    st.plotly_chart(fig, use_container_width=True)
