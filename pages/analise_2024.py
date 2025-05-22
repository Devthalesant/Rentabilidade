import pandas as pd
import streamlit as st
from Functions.vmb import criando_df_final_Rentabilidade

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
        "SÃO BERNARDO", "SANTO AMARO", "SANTOS", "TIJUCA", "TATUAPÉ", "TUCURUVI",
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
        "Lucro": "sum"
    })

    # Soma total de Lucro
    lucro_total = df_gp['Lucro'].sum()

    # Separar procedimentos com lucro e prejuízo
    lucros = df_gp[df_gp['Lucro'] > 0].sort_values(by='Lucro', ascending=False)
    prejuizos = df_gp[df_gp['Lucro'] < 0].sort_values(by='Lucro')

    # Exibir o Lucro total com destaque
    if lucro_total >= 0:
        color = 'green'
    else:
        color = 'red'
    st.markdown(f"<h3 style='color:{color}; text-align:center;'>Lucro Total: R$ {lucro_total:,.2f}</h3>", unsafe_allow_html=True)

    # Procedimentos com maior lucro
    st.subheader("Procedimentos com Lucro (ordenados por maior lucro)")
    st.dataframe(
        lucros.style
            .background_gradient(cmap='Greens', subset=['Lucro'])
            .format({'Lucro': 'R$ {:,.2f}'.format, 'Valor unitário': 'R$ {:,.2f}'.format})
    )

    # Procedimentos com maior prejuízo
    st.subheader("Procedimentos com Prejuízo (ordenados por maior prejuízo)")
    st.dataframe(
        prejuizos.style
            .background_gradient(cmap='Reds', subset=['Lucro'])
            .format({'Lucro': 'R$ {:,.2f}'.format, 'Valor unitário': 'R$ {:,.2f}'.format})
    )
