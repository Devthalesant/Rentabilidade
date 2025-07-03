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
from Functions.courtesy import courtesy_analysis_dfs
import matplotlib.pyplot as plt
import plotly.express as px


def courtesy_period():

    #bringing the dataframes: 
    database,courtesy_analysis_procedure,courtesy_custumor_reviw = courtesy_analysis_dfs()

    st.title("Análise de Cortesias Período 🎁:")

    analysis_options = ['Custo Fixo Zerado', 'Custo Fixo Real']


    format_dict = {
        'Custo_Cortesia': 'R$ {:,.2f}',
        'Receita Gerada': 'R$ {:,.2f}',
        'Custo_total_geral': 'R$ {:,.2f}',
        'Lucro/Prejuízo': 'R$ {:,.2f}',
    }

    # Sort by Profit/Loss (highest to lowest)
    df_sorted = courtesy_analysis_procedure.sort_values('Lucro/Prejuízo', ascending=False)

    # Apply formatting
    # Df of courtesy procedures results
    st.subheader("Retorno Agregado dos Procedimentos Oferecidos: ")
    st.dataframe(
        df_sorted.style
            .apply(lambda x: ['color: green' if v >= 0 else 'color: red' 
                for v in x], subset=['Lucro/Prejuízo'])
            .format(format_dict)
    )

    # Df od custumers Classification:
    st.divider()
    df_custumer = courtesy_custumor_reviw.groupby(["Procedimento_padronizado",'Classificacao']).agg({"ID cliente" : "nunique",
                                                                                                                  "Quantidade" : 'sum',
                                                                                                                  'Lucro/Prejuízo' : 'sum'}).reset_index()
    
    # 1. Calculate total quantity per procedure (sum of both classifications)
    df_custumer['Total_Quantidade'] = df_custumer.groupby('Procedimento_padronizado')['Quantidade'].transform('sum')

    df_custumer = df_custumer.sort_values(by=['Total_Quantidade', 'Procedimento_padronizado', 'Classificacao'],
                                           ascending=[False, True, True]).reset_index(drop=True)

    st.subheader("Classificação de Clientes por Procedimento: ")
    st.dataframe(
        df_custumer.style
            .apply(lambda x: ['background: lightyellow' if v == 'Oportunista' else '' 
                for v in x], subset=['Classificacao'])
            .apply(lambda x: ['color: green' if v >= 0 else 'color: red' 
                for v in x], subset=['Lucro/Prejuízo'])
            .format(format_dict)
    )
    st.divider()

    st.subheader("Gráficos Análiticos: ")

    graphic_one = courtesy_custumor_reviw.groupby('Procedimento_padronizado')['Quantidade'].sum().reset_index()
    graphic_one = graphic_one.sort_values('Quantidade', ascending=False)
    graphic_one_top_5 = graphic_one.iloc[:5]
    # Plot
    fig = px.bar(
        graphic_one_top_5, 
        x='Procedimento_padronizado', 
        y='Quantidade',
        title="Top Procedures by Quantity (Interactive)",
        labels={'Quantidade': 'Total Quantity', 'Procedimento_padronizado': 'Procedure'},
        color='Quantidade',
        color_continuous_scale='Purples',
        height=400  # Compact height
    )

    # Adjust layout
    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20),  # Reduce margins
    )
    st.plotly_chart(fig, use_container_width=True)  # Fits Streamlit container

    # 1. Aggregate and sort properly
    graphic_two = courtesy_custumor_reviw.groupby(
        ['Procedimento_padronizado', 'Classificacao']
    )['Quantidade'].sum().unstack().reset_index()

    # Verify data before sorting
    print("Before sorting:\n", graphic_two[['Procedimento_padronizado', 'Comprador', 'Oportunista']])

    # Sort by Comprador specifically (since you want to highlight buyer dominance)
    graphic_two_top_5 = graphic_two.sort_values(by='Comprador', ascending=False).head(5)

    # 2. Melt with correct value assignments
    plotly_df = graphic_two_top_5.melt(
        id_vars='Procedimento_padronizado',
        value_vars=['Comprador', 'Oportunista'],
        var_name='Classificacao',
        value_name='Quantidade'
    )

    # 3. Create bar chart with emphasized comparison
    fig = px.bar(
        plotly_df,
        x='Procedimento_padronizado',
        y='Quantidade',
        color='Classificacao',
        title='Top 5 Procedures by Buyer Quantity (Comprador)',
        labels={'Quantidade': 'Quantity', 'Procedimento_padronizado': 'Procedure'},
        color_discrete_map={  # Explicit color mapping
            'Comprador': '#7851a9',  # Purple for buyers
            'Oportunista': '#ff7f0e'  # Orange for opportunists
        },
        barmode='group',  # Use GROUPED bars instead of stacked
        height=500
    )

    # 4. Add annotations to highlight the difference
    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        legend_title_text='Client Type',
        annotations=[
            dict(
                x=xi, y=yi,
                text=f"{yi/1000:.1f}k",
                showarrow=False,
                font=dict(color='white' if color == 'Comprador' else 'black'),
                xanchor='center',
                yanchor='bottom'
            ) for xi, yi, color in zip(
                plotly_df['Procedimento_padronizado'],
                plotly_df['Quantidade'],
                plotly_df['Classificacao']
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    # 1. Calculate unique clients per classification
    client_distribution = courtesy_custumor_reviw.groupby('Classificacao')['ID cliente'].nunique().reset_index()
    client_distribution.columns = ['Classificacao', 'Unique Clients']

    # 2. Create pie chart with percentages
    fig = px.pie(
        client_distribution,
        names='Classificacao',
        values='Unique Clients',
        title='Client Distribution by Classification (%)',
        color='Classificacao',
        color_discrete_map={
            'Comprador': '#7851a9',  # Purple
            'Oportunista': '#ff7f0e'  # Orange
        },
        hole=0.3,  # Optional: Creates a donut chart
        height=500
    )

    # 3. Format labels to show percentages
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hoverinfo='label+percent+value',
        marker=dict(line=dict(color='white', width=2))  # White borders
    )

    # 4. Improve layout
    fig.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)
