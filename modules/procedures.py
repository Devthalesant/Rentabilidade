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

@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_custo_fixo():
    return pegar_dados_mongodb("rentabilidade_anual", "custos_fixos_2025")

@st.cache_data(ttl=3600)
def carregar_vmb():
    return pegar_dados_mongodb("rentabilidade_anual", "venda_mensal_bruta_2025")

@st.cache_data(ttl=3600)
def carregar_taxas():
    return pegar_dados_mongodb("rentabilidade_anual", "impostos_taxas_2025")


def teste_procedures():
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

    st.dataframe(vmb_concat)

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

    Appointments_dic, Sales_dic, Month_dic, duration_dic, all_costs_2024, all_costs_2025 = obter_dicionarios()

    vmb_concat['Procedimento_padronizado'] = vmb_concat['Procedimento'].map(Sales_dic)
    vmb_concat_tratar = vmb_concat.loc[vmb_concat['Procedimento_padronizado'].isna()]

    produtos_tratar = vmb_concat_tratar['Procedimento'].unique()
    st.warning(f"Procedimentos sem custos Salvos: {produtos_tratar}")

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

    # Uso:
    df_custos = extrair_todos_custos(all_costs_2025)
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
    
    vmb_concat['Margrem_contribuição_unit_R$'] = vmb_concat['Valor_líquido_unit'] - vmb_concat['Custo_direto_unit']
    vmb_concat['Margrem_contribuição_unit_%'] = vmb_concat['Margrem_contribuição_unit_R$']/vmb_concat['Valor_líquido_unit']
    

    vmb_concat_gp = vmb_concat.groupby(['Mês venda','Unidade','Procedimento_padronizado']).agg({'Quantidade':'sum',
                                                                          'Valor_líquido_unit':'mean',
                                                                          'Margrem_contribuição_unit_R$' : 'mean',
                                                                          'Margrem_contribuição_unit_%' : 'mean'})


    st.dataframe(vmb_concat_gp)
    st.dataframe(vmb_concat)
    

    return vmb_concat_gp