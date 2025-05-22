import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
from .dictionaries import obter_dicionarios

def criando_df_final_Rentabilidade(vmb_concat_path,custo_fixo): 
# Essa Função Junta o VMB com a base de Custos Fixo formatada de forma exata e gera uma planilha niccolucci completa
#"Bases/Venda Mesal Bruta/2024/vmb_2024_concat.csv"
#"Bases/Custos Fixos/2024/CF-txSala.xlsx"

    Appointments_dic, Sales_dic, Month_dic, duration_dic, all_costs_2024 = obter_dicionarios()

    vmb_concat = pd.read_csv(vmb_concat_path,low_memory=False)
    custo_fixo = pd.read_excel(custo_fixo)

    vmb_concat_columns = ['ID orçamento','ID cliente', 'Status','Mês venda',
                        'Unidade','Valor líquido','Procedimento','Quantidade',
                        'Valor tabela item', 'Valor liquido item']



    vmb_concat = vmb_concat[vmb_concat_columns]

    columns_to_fill_nan = ['Valor liquido item','Valor tabela item','Valor líquido']

    vmb_concat[columns_to_fill_nan] = vmb_concat[columns_to_fill_nan].fillna(0)

    vmb_concat = vmb_concat.loc[vmb_concat["Status"] == "Finalizado"]

    vmb_concat['Unidade'].unique()

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

    # Quantidade "Finalizado" para 1
    vmb_concat.loc[vmb_concat['Quantidade'] == "Finalizado", 'Quantidade'] = 1

    #tratando Procedimentos
    vmb_concat["Procedimento_padronizado"] = vmb_concat['Procedimento'].map(Sales_dic)

    #Quantidade de Vale Presente para 1: 
    vmb_concat.loc[vmb_concat['Procedimento_padronizado'] == "VALE PRESENTE",'Quantidade'] = 1

    # Tirando depilação: 
    vmb_concat = vmb_concat.loc[vmb_concat['Procedimento_padronizado'] != "DEPILACAO"]

    # Colunas de custo: 
    vmb_concat['Custo Produto'] = vmb_concat['Procedimento_padronizado'].map(lambda x: all_costs_2024.get(x, {}).get('CUSTO PRODUTO', 0))
    vmb_concat['Custo Insumos'] = vmb_concat['Procedimento_padronizado'].map(lambda x: all_costs_2024.get(x, {}).get('CUSTO INSUMOS', 0))
    vmb_concat['Custo Mod'] = vmb_concat['Procedimento_padronizado'].map(lambda x: all_costs_2024.get(x, {}).get('MOD', 0))

    vmb_concat['Custo Direto'] = vmb_concat['Custo Produto'] + vmb_concat['Custo Insumos'] + vmb_concat['Custo Mod']

    vmb_concat["Quantidade"] = vmb_concat["Quantidade"].replace(".",",")

    vmb_concat['Quantidade'] = pd.to_numeric(vmb_concat['Quantidade'],errors='coerce')

    vmb_concat['Quantidade'] = vmb_concat['Quantidade'].astype(int)

    vmb_concat['Custo Direto Total'] = vmb_concat['Custo Direto'] * vmb_concat['Quantidade']

    vmb_concat['Valor unitário'] = vmb_concat['Valor liquido item'] / vmb_concat['Quantidade']

    #dropndo colunad não utilizadas mais
    vmb_concat = vmb_concat.drop(columns=['Custo Direto'])

    vmb_concat["Cortesia?"] = (vmb_concat['Procedimento'].str.contains("CORTESIA", case=False) | (vmb_concat['Valor liquido item'] == 0))

    # Trazendo os Custos de Vendas para o DF:
    cartao = 0.0818
    imposto = 0.1425
    comissao = 0.04

    cmv = cartao + imposto + comissao

    vmb_concat['Custo Sobre Venda'] = vmb_concat['Valor liquido item'] * cmv

    # Colocando Tempo dos procedimentos
    vmb_concat["Tempo Procedimento"] = vmb_concat['Procedimento_padronizado'].map(duration_dic)

    #tratando o tempo
    vmb_concat['Tempo Procedimento'] = pd.to_timedelta(vmb_concat['Tempo Procedimento']).dt.total_seconds() // 60

    vmb_concat['Tempo Total'] = vmb_concat['Tempo Procedimento'] * vmb_concat["Quantidade"]

    vmb_concat_columns = ['ID orçamento', 'ID cliente', 'Status', 'Mês venda', 'Unidade',
                        'Valor líquido','Procedimento_padronizado', 'Quantidade',
                        'Valor tabela item','Valor liquido item','Valor unitário','Tempo Total', 'Custo Produto',
                        'Custo Insumos', 'Custo Mod', 'Custo Direto Total', 'Custo Sobre Venda','Cortesia?']



    vmb_concat = vmb_concat[vmb_concat_columns]

    vmb_concat = vmb_concat.rename(columns={"Tempo Total" : "Tempo Utilizado"})

    # Horas utilizadas por unidade: 

    df_tempo_pago = vmb_concat.groupby(['Unidade']).agg({"Tempo Utilizado" : 'sum'}).reset_index()

    df_tempo_pago

    print(df_tempo_pago)

    #Merge da base CF com DF de tempo Utilizado

    df_merged_cf = pd.merge(df_tempo_pago,custo_fixo,how='left')

    df_merged_cf["Valor Tempo Utilizado"] = df_merged_cf['Tempo Utilizado'] * df_merged_cf['Taxa Sala (Min)']

    df_merged_cf['Tempo Ocioso'] = df_merged_cf['Minutos Disponivel'] - df_merged_cf['Tempo Utilizado']

    df_merged_cf["Valor Tempo Ocioso"] = df_merged_cf['Tempo Ocioso'] * df_merged_cf['Taxa Sala (Min)']

    #Colocar os valores em escala
    #clumns_to_dividir = ["Custo Fixo",'Custo Fixo + Bko','Valor Tempo Utilizado','Tempo Ocioso',"Valor Tempo Ocioso"]

    #df_merged_cf[clumns_to_dividir] = df_merged_cf[clumns_to_dividir] / 1000

    df_merged_cf_columns = ['Unidade', 'Custo Fixo', 'Custo Fixo + Bko','Meses Funcionando',
                            'Dias uteis', 'Hora/Dia', 'Salas','Minutos Disponivel', 
                            'Taxa Sala (Hr)', 'Taxa Sala (Min)','Tempo Utilizado',
                            'Valor Tempo Utilizado', 'Tempo Ocioso','Valor Tempo Ocioso']

    df_merged_cf = df_merged_cf[df_merged_cf_columns]

    df_merged_cf["Taxa Ociosidade (Min)"] = df_merged_cf["Valor Tempo Ocioso"] / df_merged_cf['Tempo Utilizado']

    df_merged_cf

    df_taxa_sala_ociosidade = df_merged_cf.groupby(['Unidade']).agg({'Taxa Sala (Min)' : "sum","Taxa Ociosidade (Min)" : 'sum' }).reset_index()

    df_taxa_sala_ociosidade

    print(df_taxa_sala_ociosidade)

    ## Merge da base de Vendas concat com a tx sala e ociosidade - Base FInal para ANálise e Groupbys

    df_final = pd.merge(vmb_concat,df_taxa_sala_ociosidade,how='left')

    df_final["Custo Fixo"] = ((df_final['Tempo Utilizado']* df_final['Taxa Sala (Min)']) + (df_final['Tempo Utilizado']* df_final['Taxa Ociosidade (Min)']))

    receita_gerada = df_final['Valor liquido item'].sum()

    df_final['Custo Total'] = df_final['Custo Fixo'] + df_final['Custo Direto Total'] + df_final['Custo Sobre Venda']

    df_final['Lucro'] = df_final['Valor liquido item'] - df_final['Custo Total']

    print(df_final)

    return df_final
