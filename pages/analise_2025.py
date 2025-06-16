import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path
import streamlit as st
from Functions.vmb import criando_df_final_Rentabilidade
from Functions.dictionaries import obter_dicionarios
import io

def page_analyse_2025():
        # Carrega o df
        df_final = criando_df_final_Rentabilidade(
            "Bases/Venda Mesal Bruta/2025/vmb_2025_concat.csv",
            "Bases/Custos Fixos/2025/CF-txSala_Mensal.xlsx"
        )
        
        st.title("🌟 Análise de Rentabilidade 2025")
        
        unidades_options = [
            "TODAS COMPILADAS", "ALPHAVILLE", "CAMPINAS", "COPACABANA", "GUARULHOS",
            "JARDINS", "LAPA", "LONDRINA", "MOOCA", "MOEMA", "OSASCO", "IPIRANGA","ITAIM",
            "SÃO BERNARDO", "SANTO AMARO","SOROCABA", "SANTOS", "TIJUCA", "TATUAPÉ", "TUCURUVI",
            "VILA MASCOTE"
        ]
        
        time_options = [
            'Anual','Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
            'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]

        price_options = ["Preço Praticado", "Preço Tabela"]
        
        # Inputs do usuário
        branch = st.selectbox("✅ Selecione a Unidade que deseja Analisar:", unidades_options)
        time = st.selectbox("🗓️ Selecione o Período:", time_options)
        price = st.selectbox("🗓️ Selecione o estudo:", price_options)
        
        # Cópia do df
        df_database = df_final.copy()
        df = df_final.copy()
        
        # Filtro por unidade
        if branch != "TODAS COMPILADAS":
            df = df[df['Unidade'] == branch]
        
        # Filtro por mês
        if time != 'Anual':
            df = df[df['Mês venda'] == time]
        
        # Filtro por preço
        if price != "Preço Praticado":
            df = df.drop(columns=['Valor liquido item','Valor unitário','Custo Sobre Venda Final','Custo Total','Lucro'])
            df = df.rename(columns={'Valor tabela total': 'Valor liquido item'})
            df = df.rename(columns={'Valor tabela item': 'Valor unitário'})
            df['Custo Sobre Venda Final'] = df['Valor liquido item'] * 0.2643
            df['Custo Total'] = df['Custo Direto Total'] + df['Custo Sobre Venda Final'] + df['Custo Fixo']
            df['Lucro'] = df['Valor liquido item'] - df['Custo Total'] 
        
        # Agrupamento
        df_gp = df.groupby(["Procedimento_padronizado"]).agg({
            "Quantidade": "sum",
            "Valor unitário": "mean",
            "Valor liquido item" : "sum",
            "Custo Direto Total" : "sum",
            "Custo Sobre Venda Final" : "sum",
            "Custo Fixo" : "sum",
            "Custo Total" : "sum",
            "Lucro": "sum",
            "Tempo Utilizado": "sum"
        })
        df_gp = df_gp.rename(columns={'Valor liquido item' : 'Receita Gerada','Valor unitário' : 'Preço Praticado'})
        
        # Calculating Contribuition Margin
        df_gp["Margem de Contribuição %"] = np.where(df_gp['Receita Gerada'] != 0,
        (df_gp['Receita Gerada'] - df_gp['Custo Direto Total'] - df_gp['Custo Sobre Venda Final']) / df_gp['Receita Gerada'] * 100, 0)

        # Soma total de Lucro
        lucro_total = df_gp['Lucro'].sum()
        custo_fixo_total = df_gp['Custo Fixo'].sum()

        receita_total = df_gp['Receita Gerada'].sum()
        custo_total = df_gp['Custo Total'].sum()
        

        # Separar procedimentos com lucro e prejuízo
        lucros = df_gp[df_gp['Lucro'] > 0].sort_values(by='Lucro', ascending=False)
        prejuizos = df_gp[df_gp['Lucro'] < 0].sort_values(by='Lucro')
        quantidade_total = df_gp['Quantidade'].sum()
        tempo_total = df_gp['Tempo Utilizado'].sum() 


        # Exibir Receita Gerada Total
        if receita_total > custo_total:
            color = 'green'
            st.markdown(f"<h3 style='color:{'green'};text-align:center;'>Receita Gerada Total: R$ {receita_total:,.2f}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:{color};text-align:center;'>Custo Total Geral: R$ {custo_total:,.2f}</h3>", unsafe_allow_html=True)
        else:
            color = 'red'
            st.markdown(f"<h3 style='color:{'green'}; text-align:center;'>Receita Gerada Total: R$ {receita_total:,.2f}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:{color}; text-align:center;'>Custo Total Geral: R$ {custo_total:,.2f}</h3>", unsafe_allow_html=True)

        # Exibir o Lucro total com destaque
        if lucro_total >= 0:
            color = 'green'
            st.markdown(f"<h3 style='color:{color}; text-align:center;'>Lucro Total: R$ {lucro_total:,.2f}</h3>", unsafe_allow_html=True)

        else:
            color = 'red'
            st.markdown(f"<h3 style='color:{color}; text-align:center;'>Prejuízo Total: R$ {lucro_total:,.2f}</h3>", unsafe_allow_html=True)
        
        # Exibir outros KPI´s
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<h3 style='color:black; text-align:center;'>Quantidade Total: {quantidade_total:,.0f}".replace(",", ".") + "</h3>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<h3 style='color:black; text-align:center;'>Tempo Total(Min): {tempo_total:,.0f}".replace(",",".") + "</h3>", unsafe_allow_html=True)
            


        format_dict = {
            'Lucro': 'R$ {:,.2f}'.format,
            'Preço Praticado': 'R$ {:,.2f}'.format,
            'Receita Gerada': 'R$ {:,.2f}'.format,
            'Custo Direto Total': 'R$ {:,.2f}'.format,
            'Custo Sobre Venda Final': 'R$ {:,.2f}'.format,
            'Custo Fixo': 'R$ {:,.2f}'.format,
            'Custo Total': 'R$ {:,.2f}'.format,
            'Margem de Contribuição %': '{:.2f}%'.format,
            'Receita_total_clientes' : 'R$ {:,.2f}'.format,
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

        # Exibir o Dataframe de Base: 
        st.subheader("Base de Dados Utilizada")
        # Ajusta o limite de células do Styler para evitar erro de excesso de células
        pd.set_option("styler.render.max_elements", df_database.size)
        st.dataframe(df_database)

        st.subheader("Procedmentos Agregados - Prejuízo")
        # Identifica procedimentos com prejuízo consolidado (usando df_database)
        procedimentos_prejuizo = prejuizos.index.tolist()  # Pega os nomes dos procedimentos com Lucro < 0

        # Filtra a base original para pegar apenas clientes que compraram esses procedimentos
        df_clientes_preju = df[df["Procedimento_padronizado"].isin(procedimentos_prejuizo)]

        # Agora, para cada procedimento problemático, buscamos TODOS os orçamentos desses clientes
        resultados = []
        for procedimento in procedimentos_prejuizo:
            # Pega os clientes que compraram esse procedimento
            clientes = df_clientes_preju[df_clientes_preju["Procedimento_padronizado"] == procedimento]["ID cliente"].unique()
            
            # Filtra TODOS os orçamentos desses clientes (incluindo outros procedimentos)
            df_clientes = df[df["ID cliente"].isin(clientes)]
            
            # Calcula métricas
            qtd_orcamentos = df_clientes["ID orçamento"].nunique()
            receita_total = df_clientes["Valor liquido item"].sum()
            
            # Pega outros procedimentos comprados por esses clientes (excluindo o atual)
            outros_procedimentos = (
                df_clientes[df_clientes["Procedimento_padronizado"] != procedimento]
                ["Procedimento_padronizado"]
                .value_counts()
                .to_dict()
            )
            
            resultados.append({
                "Procedimento_padronizado": procedimento,
                "Qtd_orcamentos_clientes": qtd_orcamentos,
                "Receita_total_clientes": receita_total,
                "Outros_procedimentos_comprados": outros_procedimentos
            })

        # Cria o DataFrame final
        df_analise_preju_final = pd.DataFrame(resultados)
        st.dataframe(df_analise_preju_final.style.format(format_dict))

## Dataframe por unidade:
        df_groupby_unidade = df.groupby(["Unidade"]).agg({"Valor liquido item" : "sum","Custo Direto Total" : "sum",
                                                        "Custo Total" : "sum"}).reset_index()
        
        df_groupby_unidade["Margem Bruta"] = df_groupby_unidade["Valor liquido item"] - df_groupby_unidade["Custo Direto Total"]
        df_groupby_unidade["Margem Bruta %"] = df_groupby_unidade["Margem Bruta"] / df_groupby_unidade["Valor liquido item"] * 100
        df_groupby_unidade["EBITDA"] = df_groupby_unidade["Valor liquido item"] - df_groupby_unidade["Custo Total"]
        df_groupby_unidade["EBITDA %"] = df_groupby_unidade["EBITDA"] / df_groupby_unidade["Valor liquido item"] * 100

        df_groupby_unidade.rename(columns={"Valor liquido item" : "Receita Total"},inplace=True)

        # reorganizing columns: 
        df_groupby_unidade_columns = ["Unidade","Receita Total","Margem Bruta","Margem Bruta %","EBITDA","EBITDA %"]
        df_groupby_unidade = df_groupby_unidade[df_groupby_unidade_columns]

        # Formating the columns
        format_gp_unidade_dict = {'Margem Bruta %': '{:.2f}%'.format,
                                  'Margem Bruta': 'R$ {:,.2f}'.format,
                                  'EBITDA %': '{:.2f}%'.format,
                                  'EBITDA': 'R$ {:,.2f}'.format,
                                  'Receita Total': 'R$ {:,.2f}'.format}
        
        st.subheader("Análise por Unidade :")

        st.dataframe(df_groupby_unidade.style.format(format_gp_unidade_dict))

        def to_excel_bytes(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=True)
            return output.getvalue()

        lucros_excel = to_excel_bytes(lucros)
        prejuizos_excel = to_excel_bytes(prejuizos)
        base_excel = to_excel_bytes(df_database)
        preju_agregados_excel = to_excel_bytes(df_analise_preju_final)

        st.download_button(
            label="Baixar Dataframe de Procedimentos com Lucro",
            data=lucros_excel,
            file_name="lucros_procedimentos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            label="Baixar Dataframe de Procedimentos com Prejuízo",
            data=prejuizos_excel,
            file_name="prejuizos_procedimentos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            label="Baixar Base de Dados Completa",
            data=base_excel,
            file_name="base_dados_completa.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            label="Baixar Dataframe de Procedmentos Agregados - Prejuízo",
            data=preju_agregados_excel,
            file_name="Procedimentos_agregados_prejuízo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
