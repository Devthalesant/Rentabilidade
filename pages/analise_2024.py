import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.vmb import criando_df_final_Rentabilidade
from Functions.dictionaries import obter_dicionarios

def page_analyse_2024():
        # Carrega o df
        df_final = criando_df_final_Rentabilidade(
            "Bases/Venda Mesal Bruta/2024/vmb_2024_concat.csv",
            "Bases/Custos Fixos/2024/CF-txSala.xlsx"
        )
        
        st.title("🌟 Análise de Rentabilidade 2024")
        
        unidades_options = [
            "TODAS COMPILADAS", "ALPHAVILLE", "CAMPINAS", "COPACABANA", "GUARULHOS",
            "JARDINS", "LAPA", "LONDRINA", "MOOCA", "MOEMA", "OSASCO", "IPIRANGA",
            "SÃO BERNARDO", "SANTO AMARO","SOROCABA", "SANTOS", "TIJUCA", "TATUAPÉ", "TUCURUVI",
            "VILA MASCOTE"
        ]
        
        time_options = [
            'Anual','Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
            'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        
        # Inputs do usuário
        branch = st.selectbox("✅ Selecione a Unidade que deseja Analisar:", unidades_options)
        time = st.selectbox("🗓️ Selecione o Período:", time_options)
        
        # Cópia do df
        df = df_final.copy()
        
        # Filtro por unidade
        if branch != "TODAS COMPILADAS":
            df = df[df['Unidade'] == branch]
        
        # Filtro por mês
        if time != 'Anual':
            df = df[df['Mês venda'] == time]
        
        # Agrupamento
        df_gp = df.groupby(["Procedimento_padronizado"]).agg({
            "Quantidade": "sum",
            "Valor unitário": "mean",
            "Valor liquido item" : "sum",
            "Custo Direto Total" : "sum",
            "Custo Sobre Venda" : "sum",
            "Custo Fixo" : "sum",
            "Custo Total" : "sum",
            "Lucro": "sum"
        })
        df_gp = df_gp.rename(columns={'Valor liquido item' : 'Receita Gerada','Valor unitário' : 'Preço Praticado'})
        # Soma total de Lucro
        lucro_total = df_gp['Lucro'].sum()
        custo_fixo_total = df_gp['Custo Fixo'].sum()
        

        # Separar procedimentos com lucro e prejuízo
        lucros = df_gp[df_gp['Lucro'] > 0].sort_values(by='Lucro', ascending=False)
        prejuizos = df_gp[df_gp['Lucro'] < 0].sort_values(by='Lucro')

        # Exibir o Lucro total com destaque
        if lucro_total >= 0:
            color = 'green'
            st.markdown(f"<h3 style='color:{color}; text-align:center;'>Lucro Total: R$ {lucro_total:,.2f}</h3>", unsafe_allow_html=True)
        else:
            color = 'red'
            st.markdown(f"<h3 style='color:{color}; text-align:center;'>Prejuízo Total: R$ {lucro_total:,.2f}</h3>", unsafe_allow_html=True)
        
            st.markdown(f"<h3 style='color:{color}; text-align:center;'>Prejuízo Total: R$ {custo_fixo_total:,.2f}</h3>", unsafe_allow_html=True)


        format_dict = {
        'Lucro': 'R$ {:,.2f}'.format,
        'Preço Praticado': 'R$ {:,.2f}'.format,
        'Receita Gerada': 'R$ {:,.2f}'.format,
        'Custo Direto Total': 'R$ {:,.2f}'.format,
        'Custo Sobre Venda': 'R$ {:,.2f}'.format,
        'Custo Fixo': 'R$ {:,.2f}'.format,
        'Custo Total': 'R$ {:,.2f}'.format,
        }

        # Procedimentos com maior lucro
        st.subheader("Procedimentos com Lucro (ordenados por maior lucro)")
        st.dataframe(
        lucros.style
            .background_gradient(cmap='Greens', subset=['Lucro'])
            .format(format_dict)
        )

        # Procedimentos com maior prejuízo
        st.subheader("Procedimentos com Prejuízo (ordenados por maior prejuízo)")
        st.dataframe(
            prejuizos.style
                .background_gradient(cmap='Reds', subset=['Lucro'])
                .format(format_dict)
        )

        # --- Cálculo das métricas de taxa de sala e ociosidade ---
        if branch == "TODAS COMPILADAS":
            taxa_sala_media = df['Taxa Sala (Min)'].mean()
            taxa_ociosidade_media = df['Taxa Ociosidade (Min)'].mean()
        else:
            # Pega os valores da unidade específica
            df_unidade = df[df['Unidade'] == branch]
            taxa_sala_media = df_unidade['Taxa Sala (Min)'].iloc[0]
            taxa_ociosidade_media = df_unidade['Taxa Ociosidade (Min)'].iloc[0]
        

        custo_fixo_min = taxa_sala_media + taxa_ociosidade_media

        taxa_sala_fmt = f"{taxa_sala_media:.2f}".replace('.',',')
        taxa_ociosidade_fmt = f"{taxa_ociosidade_media:.2f}".replace('.',',')
        custo_fixo_fmt = f"{custo_fixo_min:,.2f}".replace('.',',')

        cols = st.columns(3)

        with cols[0]:
            st.markdown(
                f"<div style='background-color:#BDBDBD; padding:10px; border-radius:8px; text-align:center;'>"
                f"<h4 style='margin-bottom:5px;'>Taxa Sala (Min)</h4>"
                f"<p style='font-size:20px; font-weight:bold;'>R$ {taxa_sala_fmt}</p>"
                "</div>", unsafe_allow_html=True
            )

        with cols[1]:
            st.markdown(
                f"<div style='background-color:#BDBDBD; padding:10px; border-radius:8px; text-align:center;'>"
                f"<h4 style='margin-bottom:5px;'>Taxa Ociosidade (Min)</h4>"
                f"<p style='font-size:20px; font-weight:bold;'>R$ {taxa_ociosidade_fmt}</p>"
                "</div>", unsafe_allow_html=True
            )

        with cols[2]:
            st.markdown(
                f"<div style='background-color:#BDBDBD; padding:10px; border-radius:8px; text-align:center;'>"
                f"<h4 style='margin-bottom:5px;'>Custo Fixo (Min)</h4>"
                f"<p style='font-size:20px; font-weight:bold;'>R$ {custo_fixo_fmt}</p>"
                "</div>", unsafe_allow_html=True
            )
