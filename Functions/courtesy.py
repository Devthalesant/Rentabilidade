import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
from Functions.dictionaries import obter_dicionarios
from Functions.vmb import criando_df_final_Rentabilidade
import streamlit as st

def courtesy_analysis_dfs():

    appointments_concat = "C:/Users/novo1/OneDrive/Desktop/Dev/Rentabilidade Anual/Bases/Agendamento/Periodo/agdt_2025_concat.csv"
    vmb_concat = "C:/Users/novo1/OneDrive/Desktop/Dev/Rentabilidade Anual/Bases/Venda Mesal Bruta/Periodo/vmb_2025_concat.csv"
    ano = 2024

    appointments = pd.read_csv(appointments_concat,low_memory=False)
    vmb_concat = pd.read_csv(vmb_concat,low_memory=False)

    # Select relevant columns
    appointments_columns = ['ID agendamento', 'ID cliente',
                        'Unidade do agendamento',
                        'Procedimento', 'Data', 'Status']

    appointments = appointments[appointments_columns].copy()

    # Add quantity column
    appointments["Quantidade"] = 1

    # Filter out unwanted branches
    branches_to_desconsider = ['PLÁSTICA', 'HOMA', 'PRAIA GRANDE','RIBEIRÃO PRETO', 'BELO HORIZONTE']
    appointments = appointments[~appointments['Unidade do agendamento'].isin(branches_to_desconsider)]

    # Get dictionaries
    Appointments_dic, Sales_dic, Month_dic, duration_dic, all_costs_2024, all_costs_2025 = obter_dicionarios()

    # Standardize procedures
    appointments["Procedimento_padronizado"] = appointments['Procedimento'].map(Appointments_dic)
    

    # Dropping unmapped values and other procedures that we dont look: 
    appointments = appointments.loc[appointments['Procedimento_padronizado'] != "UNMAPPED"]
    appointments = appointments.loc[~appointments['Procedimento_padronizado'].isin(['TATUAGEM', 'DEPILAÇÃO', 'PRÉ TRATAMENTO'])]

    # Validation of unmapped procedures
    nan_procedures = appointments.loc[
        appointments['Procedimento_padronizado'].isna(),
        'Procedimento'
    ].unique().tolist()

    if nan_procedures:
        print("Procedimentos sem Padronização!")
        print("Pedir ao Thales para corrigir o dicionário para os seguintes Procedimentos:")
        for proc in nan_procedures:
            print(f"- {proc}")
        print(f"\nTotal de procedimentos não mapeados: {len(nan_procedures)}")
    else:
        print("Todos os Procedimentos foram Mapeados com sucesso!")

    appointments["Cortesia?"] = appointments['Procedimento'].str.contains("CORTESIA", case=False, na=False)

    appointments_columns = ['ID agendamento', 'ID cliente','Unidade do agendamento','Procedimento_padronizado', "Quantidade", 'Data', 'Status','Cortesia?']

    appointments = appointments[appointments_columns]

    appointments["Tempo"] = appointments['Procedimento_padronizado'].map(duration_dic)
    

    # Verifying if there is any procedure that we don't inform the time:

    no_time_procedures = appointments.loc[appointments['Tempo'].isna(),'Procedimento_padronizado'].unique().tolist()

    if no_time_procedures:
        print("Há Procedimentos que não tem o tempo Mapeado!")
        print("Pedir ao Thales para corrigir o dicionário de tempo para os seguintes Procedimentos:")
        for var in no_time_procedures:
            print(f"- {var}")
            print(f"\nTotal de procedimentos não mapeados: {len(no_time_procedures)}")
    else: 
        print("Todos os tempos foram mapeados com sucesso!")

    # Convert string to timedelta, then extract total minutes
    appointments['Tempo'] = (
        pd.to_timedelta(appointments['Tempo'])  # Convert to timedelta
        .dt.total_seconds()                     # Convert to total seconds
        .div(60)                                # Convert seconds to minutes
        .astype(int)                            # Convert to integer
    )

    # this df will be used for analyse the real idle rate
    df_appointments_general = appointments.copy()

    #df to analyze only the courtesy served
    appointments_cortesy = appointments.loc[appointments['Cortesia?'] == True]
    
    appointments_cortesy['Procedimento_padronizado'] = appointments_cortesy['Procedimento_padronizado'].replace({"BOTOX POWER": "LAVIEEN"})
    
    appointments_cortesy = appointments_cortesy.loc[appointments_cortesy['Status'] == "Atendido"]

    appointments_cortesy_columns = ['ID agendamento', 'ID cliente','Unidade do agendamento',
                                    'Procedimento_padronizado', "Quantidade", 'Data', 'Status',
                                    'Tempo', 'Cortesia?']

    appointments_cortesy = appointments_cortesy[appointments_cortesy_columns]

    appointments_cortesy['Data'] = pd.to_datetime(appointments_cortesy['Data'], format='%d/%m/%Y')
    appointments_cortesy['Mês'] = appointments_cortesy['Data'].dt.month
    appointments_cortesy['Ano'] = appointments_cortesy['Data'].dt.year
    appointments_cortesy['Data'] = appointments_cortesy['Data'].dt.strftime('%d/%m/%Y')

    # Bringing all costs of the procedures: 
        # Colunas de custo: 
    def get_cost(row, cost_type):
        year = row['Ano']
        if year == 2024:
            return all_costs_2024.get(row['Procedimento_padronizado'], {}).get(cost_type, 0)
        elif year == 2025:
            return all_costs_2025.get(row['Procedimento_padronizado'], {}).get(cost_type, 0)
        else:
            return 0
        
    appointments_cortesy['Custo Direto'] = appointments_cortesy.apply(lambda row: get_cost(row, 'CUSTO TOTAL'), axis=1)

    # Verifying if there is any procedure that we don't inform the Direct cost:
    no_cost_procedures = appointments_cortesy.loc[appointments_cortesy['Custo Direto'].isna(),'Procedimento_padronizado'].unique().tolist()

    if no_cost_procedures: 
        print("Procedimentos sem custo!")
        print("Pedir ao Thales para corrigir o dicionário de custos para os seguintes Procedimentos:")
        for prod in no_cost_procedures:
            print(f"- {prod}")
            print(f"\nTotal de procedimentos não mapeados: {len(no_cost_procedures)}")
    else: 
        print("Todos os custos foram mapeados com sucesso!")



    appointments_cortesy['Mês'] = appointments_cortesy['Mês'].map(Month_dic)

    appointments_cortesy_columns = ['ID agendamento', 'ID cliente','Unidade do agendamento',
                                    'Procedimento_padronizado', "Quantidade",'Data','Mês', 
                                    'Status','Custo Direto','Tempo']

    appointments_cortesy = appointments_cortesy[appointments_cortesy_columns]

    # Calling the others dataframes that we need (VMB and idle rate)
    custo_fixo = pd.read_excel('C:/Users/novo1/OneDrive/Desktop/Dev/Rentabilidade Anual/Bases/teste_para_cortesia/CF-txSala.xlsx')
    vmb_concat = pd.read_csv("C:/Users/novo1/OneDrive/Desktop/Dev/Rentabilidade Anual/Bases/teste_para_cortesia/vmb_2024_concat.csv", low_memory=False)
    df_taxas = pd.read_excel('C:/Users/novo1/OneDrive/Desktop/Dev/Rentabilidade Anual/Bases/teste_para_cortesia/CF-txSala.xlsx',sheet_name="IMP + CART")        

    df_final = criando_df_final_Rentabilidade(custo_fixo,vmb_concat,df_taxas)

    # Using only no cortesys procedure to avoid double costs
    df_final = df_final.loc[df_final['Cortesia?'] == False]

    # Only clients that is in the lst of clients that has a served cortesy
    list_of_clients_cortesy_served = appointments_cortesy['ID cliente'].unique().tolist()
    df_final = df_final.loc[df_final['ID cliente'].isin(list_of_clients_cortesy_served)]

    # Merging the base of cortesy appointments with the idle rate:
    # filter the df_final['Unidade', 'Mês venda'].unique()

    appointments_cortesy = appointments_cortesy.merge(
        df_final[['Unidade', 'Mês venda', 'Taxa Ociosidade (Min)','Taxa Sala (Min)']],  # Select only needed columns from df_final
        how='left',
        left_on=['Unidade do agendamento', 'Mês'],
        right_on=['Unidade', 'Mês venda']
    )

    appointments_cortesy = appointments_cortesy.drop_duplicates(subset=['ID agendamento'])

    appointments_cortesy = appointments_cortesy.reset_index(drop=True)

    appointments_cortesy = appointments_cortesy.drop(columns=['Unidade', 'Mês venda'], errors='ignore')

    #appointments_cortesy["Custo_Fixo"] = appointments_cortesy['Tempo'] * (appointments_cortesy['Taxa Ociosidade (Min)'] + appointments_cortesy['Taxa Sala (Min)'])

    appointments_cortesy["Custo_Fixo"] = 0

    appointments_cortesy = appointments_cortesy.drop(columns=['Taxa Ociosidade (Min)','Taxa Sala (Min)'],errors='ignore')

    appointments_cortesy["Custo_cortesia_total"] = appointments_cortesy["Custo_Fixo"] + appointments_cortesy["Custo Direto"]

    clients_totals = df_final.groupby('ID cliente').agg({"Valor liquido item" : 'sum',
                                                        "Custo Total": 'sum',}).reset_index()



    clients_totals = clients_totals.rename(columns={"Valor liquido item" : "Receita Gerada"})

    gp_aapointments_client_procedure = appointments_cortesy.groupby(["ID cliente",'Procedimento_padronizado','Unidade do agendamento']).agg({"Quantidade" : "sum","Custo_cortesia_total" : "sum"}).reset_index()

    gp_aapointments_client_procedure = gp_aapointments_client_procedure.rename(columns={"Custo_cortesia_total" : "Custo_Cortesia"})

    df_final_merged_appointments_sales = pd.merge(gp_aapointments_client_procedure,clients_totals[['ID cliente',"Receita Gerada","Custo Total"]],
                                                how='left',
                                                on='ID cliente')

    df_final_merged_appointments_sales = df_final_merged_appointments_sales.fillna(0)


    df_final_merged_appointments_sales['Custo_total_geral'] = df_final_merged_appointments_sales['Custo_Cortesia'] + df_final_merged_appointments_sales['Custo Total']

    df_final_merged_appointments_sales['Lucro/Prejuízo'] = df_final_merged_appointments_sales['Receita Gerada'] - df_final_merged_appointments_sales['Custo_total_geral']

    df_final_merged_appointments_sales['Lucro/Prejuízo'] = df_final_merged_appointments_sales['Lucro/Prejuízo'].round(2)

    df_final_merged_appointments_sales_columns = ['ID cliente', 'Procedimento_padronizado', 'Quantidade',"Unidade do agendamento",
                                                'Custo_Cortesia', 'Receita Gerada', 'Custo_total_geral',
                                                    'Lucro/Prejuízo']

    df_final_merged_appointments_sales = df_final_merged_appointments_sales[df_final_merged_appointments_sales_columns]


    # First DF to show
    gp_cortesias = df_final_merged_appointments_sales.groupby('Procedimento_padronizado').agg({'ID cliente' : 'nunique','Quantidade' : 'sum',
                                                                                            'Custo_Cortesia' : 'sum','Receita Gerada' : 'sum',
                                                                                            'Custo_total_geral' : 'sum','Lucro/Prejuízo' : 'sum'}).reset_index()

    gp_cortesias_branch = df_final_merged_appointments_sales.groupby(['Procedimento_padronizado','Unidade do agendamento']).agg({'ID cliente' : 'nunique','Quantidade' : 'sum',
                                                                                            'Custo_Cortesia' : 'sum','Receita Gerada' : 'sum',
                                                                                            'Custo_total_geral' : 'sum','Lucro/Prejuízo' : 'sum'}).reset_index()


    pd.options.display.float_format = '{:,.2f}'.format
        

    def clients_classification(valor):
        if valor <= 0:
            return "Oportunista"
        else:
            return "Comprador"

    # Aplica a função na coluna 'Receita Gerada' e cria a coluna 'Classificacao'
    df_final_merged_appointments_sales['Classificacao'] = df_final_merged_appointments_sales['Receita Gerada'].apply(clients_classification)


    #Database
    database = appointments_cortesy

    # df that show the results for each procedure
    courtesy_analysis_procedure = gp_cortesias

    # Df thatshow the classification, revenue and costs of each client
    courtesy_custumor_reviw = df_final_merged_appointments_sales

    return database,courtesy_analysis_procedure,courtesy_custumor_reviw, gp_cortesias_branch