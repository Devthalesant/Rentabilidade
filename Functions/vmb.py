import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
from Functions.dictionaries import obter_dicionarios
import streamlit as st
from .mongo import *


def criando_df_final_Rentabilidade(custo_fixo,vmb_concat,df_taxas): 
# Essa Função Junta o VMB com a base de Custos Fixo formatada de forma exata e gera uma planilha niccolucci completa
#"Bases/Venda Mesal Bruta/2024/vmb_2024_concat.csv"
#"Bases/Custos Fixos/2024/CF-txSala.xlsx"

    Appointments_dic, Sales_dic, Month_dic, duration_dic, all_costs_2024, all_costs_2025,all_costs_2025_black = obter_dicionarios()

    vmb_concat_columns = ['ID orçamento','ID cliente', 'Status','Data venda','Mês venda',
                        'Unidade','Valor líquido','Procedimento','Quantidade',
                        'Valor tabela item', 'Valor liquido item']



    vmb_concat = vmb_concat[vmb_concat_columns]
    
    #tratando a coluna de datas: 
    vmb_concat['Data venda'] = pd.to_datetime(vmb_concat['Data venda'], errors='coerce')
    vmb_concat['Ano de venda'] = vmb_concat['Data venda'].dt.year

    columns_to_fill_nan = ['Valor liquido item','Valor tabela item','Valor líquido']

    vmb_concat[columns_to_fill_nan] = vmb_concat[columns_to_fill_nan].fillna(0)

    vmb_concat[columns_to_fill_nan] = vmb_concat[columns_to_fill_nan].fillna(0)

    # Tirando unidade que não contam e unidades que fecharam

    branchs_to_remove = ['RIBEIRÃO PRETO','BELO HORIZONTE',
                        'INSIDE SALES', 'nan', 'Matriz BKO',
                        'PRAIA GRANDE', 'LOJA ONLINE']

    vmb_concat = vmb_concat.loc[~vmb_concat['Unidade'].isin(branchs_to_remove)]

    # Valores menor que 1 como zero
    vmb_concat.loc[vmb_concat['Valor liquido item'] <= 1, 'Valor liquido item'] = 0

    # Trocando Mês nan por março (verificado)
    vmb_concat.loc[vmb_concat['Mês venda'].isna(), 'Mês venda'] = "Março"

    # Procedimentos Nan como Vale Presente: 
    vmb_concat.loc[vmb_concat['Procedimento'].isna(),'Procedimento'] = "Vale Presente"

    # Unidades Nan como "Sorocaba" (validado)
    vmb_concat.loc[vmb_concat['Unidade'].isna(),'Unidade'] = "SOROCABA"

    # Quantidade como Nan como 1 (validado): 
    vmb_concat.loc[vmb_concat['Quantidade'].isna(),'Quantidade'] = 1

    # Somente Orçamentos Finalizados
    vmb_concat = vmb_concat.loc[vmb_concat['Status'] == 'Finalizado']

    # Quantidade "Finalizado" para 1
    vmb_concat.loc[vmb_concat['Quantidade'] == "Finalizado", 'Quantidade'] = 1

    #tratando Procedimentos
    vmb_concat["Procedimento_padronizado"] = vmb_concat['Procedimento'].map(Sales_dic)

    #Quantidade de Vale Presente para 1: 
    vmb_concat.loc[vmb_concat['Procedimento_padronizado'] == "VALE PRESENTE",'Quantidade'] = 1

    # Tirando depilação: 
    vmb_concat = vmb_concat.loc[vmb_concat['Procedimento_padronizado'] != "DEPILACAO"]

    # Colunas de custo: AQUIII
    def get_cost(row, cost_type):
        if row['Ano de venda'] == 2024:
            return all_costs_2024.get(row['Procedimento_padronizado'], {}).get(cost_type, 0)
        
        elif row['Ano de venda'] == 2025:
            mes = str(row['Mês venda']).strip().lower()
            
            if mes in ['novembro', 'nov', '11', 11]:
                return all_costs_2025_black.get(row['Procedimento_padronizado'], {}).get(cost_type, 0)
            return all_costs_2025.get(row['Procedimento_padronizado'], {}).get(cost_type, 0)
        
        elif row['Ano de venda'] == 2026:
            mes = str(row['Mês venda']).strip().lower()
            
            if mes in ['novembro', 'nov', '11', 11]:
                return all_costs_2025_black.get(row['Procedimento_padronizado'], {}).get(cost_type, 0)
            return all_costs_2025.get(row['Procedimento_padronizado'], {}).get(cost_type, 0)
        
        else:
            return 0
        
    vmb_concat['Custo Produto'] = vmb_concat.apply(lambda row: get_cost(row, 'CUSTO PRODUTO'), axis=1)
    vmb_concat['Custo Insumos'] = vmb_concat.apply(lambda row: get_cost(row, 'CUSTO INSUMOS'), axis=1)
    vmb_concat['Custo Mod'] = vmb_concat.apply(lambda row: get_cost(row, 'MOD'), axis=1)

    #multiplicando cada um dos custos pelo valor da quantidade:
# Antes da multiplicação, converta as colunas para float
    vmb_concat['Custo Produto'] = pd.to_numeric(
        vmb_concat['Custo Produto'].astype(str).str.replace(',', '.').str.replace(r'[^\d\.]', '', regex=True),
        errors='coerce'
    )

    vmb_concat['Quantidade'] = pd.to_numeric(
        vmb_concat['Quantidade'].astype(str).str.replace(',', '.').str.replace(r'[^\d\.]', '', regex=True),
        errors='coerce'
    )

    vmb_concat['Custo Produto'] = vmb_concat['Custo Produto'] * vmb_concat['Quantidade']
    vmb_concat['Custo Insumos'] = vmb_concat['Custo Insumos'] * vmb_concat['Quantidade']
    vmb_concat['Custo Mod'] = vmb_concat['Custo Mod'] * vmb_concat['Quantidade']

    vmb_concat['Custo Direto Total'] = vmb_concat['Custo Produto'] + vmb_concat['Custo Insumos'] + vmb_concat['Custo Mod']

    vmb_concat["Quantidade"] = vmb_concat["Quantidade"].replace(".",",")

    vmb_concat['Quantidade'] = pd.to_numeric(vmb_concat['Quantidade'],errors='coerce')

    vmb_concat['Quantidade'] = vmb_concat['Quantidade'].astype(int)

    vmb_concat['Valor unitário'] = vmb_concat['Valor liquido item'] / vmb_concat['Quantidade']
    
    vmb_concat["Valor tabela total"] = vmb_concat['Valor tabela item'] * vmb_concat['Quantidade']

    vmb_concat["Cortesia?"] = (vmb_concat['Procedimento'].str.contains("CORTESIA", case=False) | (vmb_concat['Valor liquido item'] == 0))

    # Trazendo os Custos de Vendas para o DF:
    #cartao = 0.0818
    #imposto = 0.1425
    #comissao = 0.04

    #cmv = cartao + imposto + comissao

    vmb_concat = vmb_concat.merge(
    df_taxas[['Mês', 'Custo_Sobre_Venda']],
    left_on='Mês venda',
    right_on='Mês',
    how='left'
    )

    vmb_concat.drop(columns=['Mês'], inplace=True)

    vmb_concat['Custo Sobre Venda Final'] = vmb_concat['Valor liquido item'] * vmb_concat['Custo_Sobre_Venda']

    # Colocando Tempo dos procedimentos
    vmb_concat["Tempo Procedimento"] = vmb_concat['Procedimento_padronizado'].map(duration_dic)

    #tratando o tempo
    vmb_concat['Tempo Procedimento'] = pd.to_timedelta(vmb_concat['Tempo Procedimento']).dt.total_seconds() // 60

    vmb_concat['Tempo Total'] = vmb_concat['Tempo Procedimento'] * vmb_concat["Quantidade"]

    vmb_concat_columns = ['ID orçamento', 'ID cliente', 'Status', 'Mês venda', 'Ano de venda', 'Unidade',
                        'Valor líquido','Procedimento_padronizado', 'Quantidade',
                        'Valor tabela item', 'Valor tabela total', 'Valor liquido item','Valor unitário','Tempo Total', 'Custo Produto',
                        'Custo Insumos', 'Custo Mod', 'Custo Direto Total', 'Custo Sobre Venda Final','Cortesia?']



    vmb_concat = vmb_concat[vmb_concat_columns]

    vmb_concat = vmb_concat.rename(columns={"Tempo Total" : "Tempo Utilizado"})

    # Horas utilizadas por unidade: 
    
    df_tempo_pago = vmb_concat.groupby(['Unidade','Mês venda']).agg({"Tempo Utilizado" : 'sum'}).reset_index()

    df_tempo_pago.columns = df_tempo_pago.columns.str.strip()
    custo_fixo.columns = [col.strip() for col in custo_fixo.columns]

    #Merge da base CF com DF de tempo Utilizado
    df_merged_cf = pd.merge(df_tempo_pago,custo_fixo,how='left',
        left_on=['Unidade', 'Mês venda'],
        right_on=['Unidade', 'Mês'])

    df_merged_cf["Valor Tempo Utilizado"] = df_merged_cf['Tempo Utilizado'] * df_merged_cf['Taxa Sala (Min)']

    df_merged_cf['Tempo Ocioso'] = df_merged_cf['Minutos Disponivel'] - df_merged_cf['Tempo Utilizado']

    df_merged_cf["Valor Tempo Ocioso"] = df_merged_cf['Tempo Ocioso'] * df_merged_cf['Taxa Sala (Min)']

    df_merged_cf_columns = ['Unidade', 'Custo Fixo + Bko','Dias uteis', 'Hora/Dia','Mês',
                            'Salas','Minutos Disponivel', 'Taxa Sala (Hr)', 'Taxa Sala (Min)',
                            'Tempo Utilizado','Valor Tempo Utilizado', 'Tempo Ocioso','Valor Tempo Ocioso']

    df_merged_cf = df_merged_cf[df_merged_cf_columns]

    df_merged_cf["Taxa Ociosidade (Min)"] = df_merged_cf["Valor Tempo Ocioso"] / df_merged_cf['Tempo Utilizado']

    df_taxa_sala_ociosidade = df_merged_cf.groupby(['Unidade', 'Mês']).agg({
        'Taxa Sala (Min)': 'first',
        'Taxa Ociosidade (Min)': 'first',
        'Minutos Disponivel' : 'first',
        'Tempo Ocioso' : 'first'
        }).reset_index()
    
    
    ## Merge da base de Vendas concat com a tx sala e ociosidade - Base FInal para ANálise e Groupbys

    df_final = pd.merge(vmb_concat,df_taxa_sala_ociosidade,
                        how='left',left_on=['Unidade', 'Mês venda'],right_on=['Unidade', 'Mês'])

    df_final["Custo Fixo"] = ((df_final['Tempo Utilizado']* df_final['Taxa Sala (Min)']) + (df_final['Tempo Utilizado']* df_final['Taxa Ociosidade (Min)']))

    receita_gerada = df_final['Valor liquido item'].sum()

    df_final['Custo Total'] = df_final['Custo Fixo'] + df_final['Custo Direto Total'] + df_final['Custo Sobre Venda Final']

    df_final['Lucro'] = df_final['Valor liquido item'] - df_final['Custo Total']

    df_final['Mês venda'].unique()

    df_final.drop(columns='Mês',inplace=True)

    return df_final


####################################################################################################
### Função para tratar dados e criar a base Final V.2
####################################################################################################

def criar_base_final(vmb):
    """
    Função que cria a base final de dados para análise, processando e calculando
    informações como tempo, custo fixo, custo dos procedimentos e lucro.
    """
    # Definindo os tipos de dados para cada coluna
    tipos_colunas = {
        'ID orçamento': int,  
        'Status': str, 
        'Data venda': str,
        'Mes_num': str,
        'Ano': int,
        'Unidade': str,
        'Valor tabela': float,
        'Valor líquido': float,
        'Procedimento': str,
        'Quantidade': int,
        'Valor liquido item': float,
        'ID cliente': str,
        'Classificação cliente': str
    }
    
    # Convertendo as colunas para os tipos especificados no dicionário
    for coluna, tipo in tipos_colunas.items():
        if coluna in vmb.columns:    
            vmb[coluna] = vmb[coluna].astype(tipo, errors='ignore')

    # Tratando e extraindo dados de datas
    vmb['Data venda'] = pd.to_datetime(vmb['Data venda'])
    vmb['Mes_num'] = vmb['Data venda'].dt.strftime('%m')
    vmb['Ano'] = vmb['Data venda'].dt.year

    Mes_num = vmb['Mes_num'].iloc[0]
    periodo = f"{vmb['Ano'].iloc[0]}-{str(vmb['Mes_num'].iloc[0]).zfill(2)}"
    ano = vmb['Ano'].iloc[0]

    meses = { '01': 'Janeiro', '02': 'Fevereiro', '03': 'Março', '04': 'Abril', '05': 'Maio', '06': 'Junho',
              '07': 'Julho', '08': 'Agosto', '09': 'Setembro', '10': 'Outubro', '11': 'Novembro', '12': 'Dezembro' }

    # Filtrando as colunas úteis
    colunas_vmb = ['ID orçamento', 'Status', 'Data venda', 'Mes_num', 'Ano', 'Unidade', 'Valor tabela',
                   'Valor líquido', 'Procedimento', 'Quantidade', 'Valor liquido item', 'ID cliente', 'Classificação cliente']
    vmb = vmb[colunas_vmb]

    # Filtrando as linhas de acordo com o mês
    vmb = vmb.loc[vmb['Mes_num'] == Mes_num]

    # Mapeando mês para nome
    vmb['Mês'] = vmb['Mes_num'].map(meses)

    vmb = vmb.loc[~vmb['Procedimento'].isna()]
    vmb = vmb.loc[vmb['Procedimento'] != 'nan']

    # Filtrando status e unidades
    vmb = vmb.loc[vmb['Status'] == 'Finalizado']
    vmb['Quantidade'] = pd.to_numeric(vmb['Quantidade'], errors='coerce')

    unidades_a_desconsiderar = ['PRAIA GRANDE', 'PRÓ-CORPO ACADEMY', 'Harmonização Intíma', 'RIBEIRÃO PRETO',
                                'BELO HORIZONTE', 'INSIDE SALES', 'LOJA ONLINE']
    vmb = vmb.loc[~vmb['Unidade'].isin(unidades_a_desconsiderar)]

    # Tratando dados vazios
    vmb[['Valor líquido', 'Valor liquido item', 'Valor tabela']] = vmb[['Valor líquido', 'Valor liquido item', 'Valor tabela']].fillna(0)
    vmb['Valor_unitário'] = np.where(vmb['Quantidade'].fillna(0) != 0, vmb['Valor liquido item'] / vmb['Quantidade'], 0)

    # Criando coluna para informar a categoria da venda
    vmb['Categoria_da_venda'] = np.where(vmb['Procedimento'].str.contains('CORTESIA', case=False, na=False), 'CORTESIA', 'VENDA')

    # Trazendo dicionário de nomenclaturas
    de_para_nomes = carregar_doc_mongo("rentabilidade_anual", "De-Para Nomenclaturas", "DE_PARA_NOMENCLATURAS")
    vmb['Procedimento_padronizado'] = vmb['Procedimento'].map(de_para_nomes)

    # Verificando nomenclaturas não mapeadas
    verificar_nomenclaturas = vmb.loc[vmb['Procedimento_padronizado'].isna()]
    qtd_sem_nomenclatura = len(verificar_nomenclaturas)
    procedimentos_sem_nomenclatura_padrao = verificar_nomenclaturas['Procedimento'].unique().tolist()

    if qtd_sem_nomenclatura > 0:
        msg1 = f"Os seguintes procedimentos não têm cadastro no De-Para de Nomenclaturas:\n{procedimentos_sem_nomenclatura_padrao}\n\nPor favor, cadastre esse(s) novo(s) procedimento(s) na aba de De-Para de Procedimentos."
        print(msg1)
        return
    else:
        msg1 = print('OK nomenclaturas')

    # Trazendo dicionário de tempos dos procedimentos
    de_para_tempo = carregar_doc_mongo("rentabilidade_anual", "De-Para Tempo Procedimentos", "DE_PARA_TEMPO_PROCEDIMENTOS")
    vmb['tempo'] = vmb['Procedimento_padronizado'].map(de_para_tempo)

    # Verificando tempos não mapeados
    verificar_tempo = vmb.loc[vmb['tempo'].isna()]
    qtd_sem_tempo = len(verificar_tempo)
    procedimentos_sem_tempo_padrao = verificar_tempo['Procedimento_padronizado'].unique().tolist()

    if qtd_sem_tempo > 0:
        msg2 = f"Os seguintes procedimentos não têm cadastro no De-Para de Tempo:\n{procedimentos_sem_tempo_padrao}\n\nPor favor, cadastre esse(s) novo(s) procedimento(s) na aba de De-Para de Procedimentos."
        print(msg2)
        return
    else:
        msg2 = print('OK Tempo')

    # Criando coluna de tempo em minutos
    vmb['tempo_min_unitario'] = pd.to_timedelta(vmb['tempo']).dt.total_seconds() / 60
    vmb['tempo_min_unitario'] = vmb['tempo_min_unitario'].astype(int)
    vmb['tempo_procedimento'] = vmb['tempo_min_unitario'] * vmb['Quantidade']

    # Criando dataframe de tempo vendido por unidade no mês
    df_tempo_vendido = vmb.groupby(['Unidade']).agg({'tempo_procedimento': 'sum'}).reset_index()
    dic_de_tempo_vendido = dict(zip(df_tempo_vendido['Unidade'], df_tempo_vendido['tempo_procedimento']))

    # Trazendo df de custos fixos
    df_custos_fixos = carregar_doc_mongo("rentabilidade_anual", "Custos_Fixos", periodo, asdataframe=True)

    if df_custos_fixos.empty:
        msg3 = f"Não temos dados de Custo Fixo para o seguinte período:\n{periodo}\n\nPor favor, faça o upload da base na aba Upload de Bases"
        print(msg3)
        return
    else:
        msg3 = print('OK Custo Fixo')

    # Calculando tempo ocioso e o custo da ociosidade
    df_custos_fixos['Tempo Vendido'] = df_custos_fixos['Unidade'].map(dic_de_tempo_vendido)
    df_custos_fixos['Tempo Vendido'] = df_custos_fixos['Tempo Vendido'].fillna(0)
    df_custos_fixos['Tempo ocioso'] = df_custos_fixos['Minutos Disponivel'] - df_custos_fixos['Tempo Vendido']
    df_custos_fixos['Custo da Ociosidade'] = df_custos_fixos['Tempo ocioso'] * df_custos_fixos['Taxa Sala (Min)']
    df_custos_fixos['Taxa Ociosidade (Min)'] = df_custos_fixos['Custo da Ociosidade'] / df_custos_fixos['Tempo Vendido']

    # Substituindo valores infinitos por NaN
    df_custos_fixos.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Trazendo informações de custo fixo para a base de vmb por merge
    vmb_custo_fixo = pd.merge(vmb, df_custos_fixos[['Unidade', 'Minutos Disponivel', 'Tempo Vendido', 'Tempo ocioso', 'Custo da Ociosidade', 'Taxa Sala (Min)', 'Taxa Ociosidade (Min)']], how='left', on='Unidade')
    vmb_custo_fixo['Custo_fixo'] = ((vmb_custo_fixo['Taxa Sala (Min)'] + vmb_custo_fixo['Taxa Ociosidade (Min)']) * vmb_custo_fixo['tempo_procedimento'])

    # Trazendo custos de procedimentos
    de_para_custos = carregar_doc_mongo("rentabilidade_anual", "Custos Procedimentos Mensal", f"ALL_COSTS_{ano}_MENSAL", Mes_num)

    if not de_para_custos:
        msg4 = f"Não temos dados de Custos Procedimentos Mensal para o seguinte período:\n{periodo}\n\nPor favor, faça o cadastro dos custos na aba Custos do Mês"
        print(msg4)
        return
    else:
        msg4 = print('OK Custos Procedimentos Mensal')

    # Criando dicionário de custos para cada tipo de custo
    campos_custo = {"Custo_Produto": "CUSTO PRODUTO", "Custo_MOD": "MOD", "Custo_insumos": "CUSTO INSUMOS"}
    vmb_custo_fixo_produto = vmb_custo_fixo.copy()

    for nome_coluna, chave_custo in campos_custo.items():
        mapa = {k: v[chave_custo] for k, v in de_para_custos.items()}
        vmb_custo_fixo_produto[nome_coluna] = (vmb_custo_fixo["Procedimento_padronizado"].map(mapa) * vmb_custo_fixo["Quantidade"]).fillna(0)

    # Reordenando colunas
    col_order = ['Mes_num', 'Ano', 'ID orçamento', 'ID cliente', 'Classificação cliente', 'Data venda', 'Mês', 'Unidade',
                 'Procedimento_padronizado', 'Valor tabela', 'Valor líquido', 'Quantidade', 'Valor liquido item', 'Valor_unitário',
                 'tempo_procedimento', 'Minutos Disponivel', 'Tempo Vendido', 'Tempo ocioso', 'Custo da Ociosidade', 'Taxa Sala (Min)',
                 'Taxa Ociosidade (Min)', 'Custo_fixo', 'Custo_Produto', 'Custo_MOD', 'Custo_insumos', 'Categoria_da_venda']

    vmb_custo_fixo_produto = vmb_custo_fixo_produto[col_order]
    teste = vmb_custo_fixo_produto.copy()
    # Criando dataframe auxiliar para análise de tempo vendido e ociosidade por mês por unidade
    df_tempo_unidade_mes = vmb_custo_fixo_produto[['Ano', 'Mes_num', 'Unidade', 'Minutos Disponivel', 'Tempo Vendido', 'Tempo ocioso', 'Custo da Ociosidade']]
    df_tempo_unidade_mes['periodo'] = df_tempo_unidade_mes['Ano'].astype(str) + '-' + df_tempo_unidade_mes['Mes_num'].astype(str).str.zfill(2)
    df_tempo_unidade_mes = df_tempo_unidade_mes.drop_duplicates(subset=['periodo', 'Unidade']).reset_index(drop=True)

    # Removendo colunas desnecessárias
    vmb_custo_fixo_produto = vmb_custo_fixo_produto.drop(columns=['Minutos Disponivel', 'Tempo Vendido', 'Tempo ocioso', 'Custo da Ociosidade'])

    # Trazendo dados de taxas, impostos e comissão (Custo Financeiro)
    df_custos_financeiros = carregar_doc_mongo("rentabilidade_anual", "impostos_taxas", periodo, asdataframe=True)
    print(df_custos_financeiros)
    print(vmb_custo_fixo_produto)
    vmb_custo_fixo_produto_fin = pd.merge(vmb_custo_fixo_produto, df_custos_financeiros[['Mês', 'Custo_Sobre_Venda']], how='left', on='Mês')

    print(vmb_custo_fixo_produto_fin['Custo_Sobre_Venda'].unique())

    # Calculando o custo financeiro de cada produto vendido
    vmb_custo_fixo_produto_fin['Custo_financeiro_produto'] = vmb_custo_fixo_produto_fin['Valor liquido item'] * vmb_custo_fixo_produto_fin['Custo_Sobre_Venda']
    vmb_custo_fixo_produto_fin['Custo_financeiro_real'] = vmb_custo_fixo_produto_fin['Valor líquido'] * vmb_custo_fixo_produto_fin['Custo_Sobre_Venda']

    # Dropping coluna de Custo sobre venda % e cálculos finais
    vmb_custo_fixo_produto_fin = vmb_custo_fixo_produto_fin.drop(columns=['Custo_Sobre_Venda']).reset_index(drop=True)
    vmb_custo_fixo_produto_fin['Custo_direto_procedimento'] = (vmb_custo_fixo_produto_fin['Custo_Produto'] + vmb_custo_fixo_produto_fin['Custo_MOD'] + vmb_custo_fixo_produto_fin['Custo_insumos'])
    vmb_custo_fixo_produto_fin['Custo_total_procedimento'] = (vmb_custo_fixo_produto_fin['Custo_fixo'] + vmb_custo_fixo_produto_fin['Custo_direto_procedimento'] + vmb_custo_fixo_produto_fin['Custo_financeiro_produto'])
    vmb_custo_fixo_produto_fin['Lucro_líquido_item'] = (vmb_custo_fixo_produto_fin['Valor liquido item'] - vmb_custo_fixo_produto_fin['Custo_total_procedimento'])
    vmb_custo_fixo_produto_fin['Lucro_líquido_item_%'] = np.where(vmb_custo_fixo_produto_fin['Valor liquido item'] != 0,
                                                                  vmb_custo_fixo_produto_fin['Lucro_líquido_item'] /
                                                                  vmb_custo_fixo_produto_fin['Valor liquido item'], np.nan)

    # Reordenando colunas finais
    colum_order = ['ID orçamento', 'ID cliente', 'Classificação cliente', 'Data venda', 'Mês', 'Mes_num', 'Ano', 'Unidade',
                   'Procedimento_padronizado', 'Quantidade', 'Categoria_da_venda', 'Valor tabela', 'Valor_unitário', 'Valor líquido',
                   'Valor liquido item', 'tempo_procedimento', 'Taxa Sala (Min)', 'Taxa Ociosidade (Min)', 'Custo_Produto',
                   'Custo_MOD', 'Custo_insumos', 'Custo_financeiro_produto', 'Custo_financeiro_real', 'Custo_fixo',
                   'Custo_direto_procedimento', 'Custo_total_procedimento', 'Lucro_líquido_item', 'Lucro_líquido_item_%']

    vmb_custo_fixo_produto_fin = vmb_custo_fixo_produto_fin[colum_order]

    return df_tempo_unidade_mes, vmb_custo_fixo_produto_fin, msg1, msg2, msg3, msg4, teste
