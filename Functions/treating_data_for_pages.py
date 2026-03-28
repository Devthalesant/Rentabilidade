from .dictionaries_2 import *
import streamlit as st
import pandas as pd
from .mongo import *
from .tratar_dados_format import *


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

## Gerar groupby para análise de procedimentos

def gerar_groupby_para_analise_de_procedimento(data_for_procedures):
    data_for_procedures_gp = data_for_procedures.groupby(['Procedimento_padronizado']).agg({'Valor_unitário' : 'mean',
                                                                                            'Quantidade' : 'sum',
                                                                                            'Valor liquido item' : 'sum',
                                                                                            'Custo_direto_procedimento' : 'sum',
                                                                                            'tempo_procedimento' : 'sum',
                                                                                            'Custo_fixo' : 'sum',
                                                                                            'Custo_total_procedimento' : 'sum',
                                                                                            'Lucro_líquido_item' : 'sum',
                                                                                            'Lucro_líquido_item_%' : 'mean'}).reset_index()
    
    data_for_procedures_gp = data_for_procedures_gp.rename(columns={'Valor_unitário' : 'Preço_Praticado',
                                                                    'Valor liquido item' : 'Receita_Gerada',
                                                                    'Custo_direto_procedimento' : 'Custo_Direto',
                                                                    'Custo_fixo' : 'Custo_Fixo',
                                                                    'tempo_procedimento' : 'Tempo_Vendido',
                                                                    'Custo_total_procedimento' : 'Custo_Total',
                                                                    'Lucro_líquido_item' : 'Lucro_Líquido',
                                                                    'Lucro_líquido_item_%' : 'Lucro_Líquido_%'}).reset_index(drop=True)
    
    
    data_for_procedures_gp['Margem_de_Contribuição'] = data_for_procedures_gp['Custo_Direto'] / data_for_procedures_gp['Receita_Gerada']

    data_for_procedures_gp_columns = ['Procedimento_padronizado','Preço_Praticado','Quantidade','Receita_Gerada',
                                    'Custo_Direto','Margem_de_Contribuição','Custo_Fixo','Custo_Total',
                                    'Lucro_Líquido','Lucro_Líquido_%','Tempo_Vendido']

    data_for_procedures_gp = data_for_procedures_gp[data_for_procedures_gp_columns]

    data_for_procedures_gp = data_for_procedures_gp.sort_values(by=['Receita_Gerada'],ascending=False).reset_index(drop=True)

    ## Puxando dados De-Para de Categorias: 
    De_para_catgorias = carregar_doc_mongo('rentabilidade_anual','De-Para Categorias',"DE_PARA_CATEGORIAS",asdataframe=True)
    De_para_catgorias.columns = ['Procedimento_padronizado','Categoria']

    data_for_procedures_gp = pd.merge(data_for_procedures_gp,De_para_catgorias,
                                    how='left',
                                    on='Procedimento_padronizado')
    
    return data_for_procedures_gp

## Função para pegar dados atuais de taxa sala e ocisoidade
def pegar_taxa_sala_ocs_periodo_unidade_atual(data):
    df_gp_sala_ocs = data.groupby(['Unidade','periodo']).agg({'Taxa Sala (Min)' : 'first',
                                                            'Taxa Ociosidade (Min)' : 'first'}).reset_index()
    return df_gp_sala_ocs

def gerar_kpis_tempo_rede(df_tempo):

    minutos_disponiveis = df_tempo['Minutos Disponivel'].sum()
    minutos_pagos       = df_tempo['Tempo Vendido'].sum()
    minutos_ociosos     = df_tempo['Tempo ocioso'].sum()
    custo_da_ociosidade = formatar_real_resumido(df_tempo['Custo da Ociosidade'].sum())

    return minutos_disponiveis, minutos_pagos, minutos_ociosos, custo_da_ociosidade

# ── Funções: Tratar Dados — Tempo, Taxas e Ociosidade ────────────────────────
# Origem: current_year_analysis.py → SEÇÃO: Tempo, Taxas e Ociosidade
# Colar em: Functions/tratar_dados_format.py (ou arquivo de tratar_dados equivalente)


def tratar_ociosidade_mensal(df_tempo: pd.DataFrame, Month_dic_number_str: dict) -> pd.DataFrame:
    """
    Calcula percentuais de ociosidade e produtividade por mês (nível rede).

    Parâmetros:
        df_tempo             : DataFrame retornado por carregar_tempo_unidade_mes()
        Month_dic_number_str : Dicionário {numero_mes: nome_mes_str}

    Retorna:
        DataFrame com colunas: Mes_num | Ociosidade | Produtivo | Mes_str
    """
    df = df_tempo.copy()
    df['Ociosidade'] = df['Tempo ocioso'] / df['Minutos Disponivel']
    df['Produtivo']  = 1 - df['Ociosidade']

    df_gp = (
        df.groupby('Mes_num')
        .agg({'Ociosidade': 'mean', 'Produtivo': 'mean'})
        .reset_index()
    )
    df_gp['Mes_str'] = df_gp['Mes_num'].map(Month_dic_number_str)
    return df_gp


def tratar_ociosidade_por_unidade(df_taxa_sala_ocs: pd.DataFrame, unidade: str) -> dict:
    """
    Filtra e calcula KPIs de ociosidade para uma unidade específica.

    Parâmetros:
        df_taxa_sala_ocs : DataFrame retornado por pegar_taxa_sala_ocs_periodo_unidade_atual()
        unidade          : Nome da unidade selecionada

    Retorna:
        Dicionário com chaves:
            df_u            : DataFrame filtrado da unidade
            df_sorted       : DataFrame ordenado por período
            df_graf         : DataFrame com pct_ocs, pct_prod, mes_label e custo_total_min
            tx_sala_mean    : float — média da Taxa Sala (Min)
            tx_ocs_mean     : float — média da Taxa Ociosidade (Min)
            custo_fixo_min  : float — soma das médias
            pct_ociosidade  : float — % ociosidade média
            pct_produtivo   : float — % tempo produtivo médio
            delta_pct_str   : str | None — variação vs mês anterior formatada
            delta_tipo_ocs  : str — "down" | "up" | "off"
    """
    df_u = df_taxa_sala_ocs[df_taxa_sala_ocs['Unidade'] == unidade].copy()

    tx_sala_mean   = df_u['Taxa Sala (Min)'].mean()
    tx_ocs_mean    = df_u['Taxa Ociosidade (Min)'].mean()
    custo_fixo_min = tx_sala_mean + tx_ocs_mean
    pct_ociosidade = tx_ocs_mean / custo_fixo_min if custo_fixo_min > 0 else 0
    pct_produtivo  = 1 - pct_ociosidade

    df_sorted = df_u.sort_values('periodo')

    # Delta: variação percentual da ociosidade no último mês vs penúltimo
    if len(df_sorted) >= 2:
        ocs_ult   = df_sorted.iloc[-1]['Taxa Ociosidade (Min)']
        ocs_pen   = df_sorted.iloc[-2]['Taxa Ociosidade (Min)']
        custo_ult = df_sorted.iloc[-1]['Taxa Sala (Min)'] + ocs_ult
        custo_pen = df_sorted.iloc[-2]['Taxa Sala (Min)'] + ocs_pen
        pct_ocs_ult    = ocs_ult / custo_ult if custo_ult > 0 else 0
        pct_ocs_pen    = ocs_pen / custo_pen if custo_pen > 0 else 0
        delta_pct_str  = f"{pct_ocs_ult - pct_ocs_pen:+.1%} vs mês anterior"
        delta_tipo_ocs = "down" if pct_ocs_ult > pct_ocs_pen else "up"  # subiu = piora
    else:
        delta_pct_str  = None
        delta_tipo_ocs = "off"

    # DataFrame para gráficos
    df_graf = df_sorted.copy()
    df_graf['pct_ocs']        = df_graf['Taxa Ociosidade (Min)'] / (df_graf['Taxa Sala (Min)'] + df_graf['Taxa Ociosidade (Min)'])
    df_graf['pct_prod']       = 1 - df_graf['pct_ocs']
    df_graf['mes_label']      = df_graf['periodo'].astype(str)
    df_graf['custo_total_min'] = df_graf['Taxa Sala (Min)'] + df_graf['Taxa Ociosidade (Min)']

    return {
        "df_u"           : df_u,
        "df_sorted"      : df_sorted,
        "df_graf"        : df_graf,
        "tx_sala_mean"   : tx_sala_mean,
        "tx_ocs_mean"    : tx_ocs_mean,
        "custo_fixo_min" : custo_fixo_min,
        "pct_ociosidade" : pct_ociosidade,
        "pct_produtivo"  : pct_produtivo,
        "delta_pct_str"  : delta_pct_str,
        "delta_tipo_ocs" : delta_tipo_ocs,
    }
