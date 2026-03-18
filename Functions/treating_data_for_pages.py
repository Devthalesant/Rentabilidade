from .dictionaries_2 import *
import streamlit as st
import pandas as pd
from .mongo import *


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