import pandas as pd
import streamlit as st
from Functions.mongo import *
import time  # Adicionado para o feedback visual

def atualizar_banco_de_dados():
    st.title("Atualizar Banco de Dados")
    st.write("Favor Anexar as Bases de fechamentos do Mês abaixo:")
    
    # Seção para input do ano
    ano = st.text_input("Digite o Ano (Ex: 2025)")
    
    # Uploaders em colunas
    col1, col2, col3 = st.columns(3)
    with col1:
        vmb = st.file_uploader(
            "Vendas Mensal Brutas 💵 (Excel):",
            type=["xlsx"],
            accept_multiple_files=False
        )
    with col2:
        custo_fixo = st.file_uploader(
            "Custo Fixo 💼 (Excel):",
            type=["xlsx"],
            accept_multiple_files=False
        )
    with col3:
        impostos_taxas_comissao = st.file_uploader(
            "Impostos e Taxas 🧾 (Excel):",
            type=["xlsx"],
            accept_multiple_files=False
        )

    # Verifica se todos os arquivos foram carregados
    if vmb and custo_fixo and impostos_taxas_comissao and ano:
        # Lê os arquivos Excel
        vendas = pd.read_excel(vmb)
        custo_fixo_df = pd.read_excel(custo_fixo) 
        imp_tax = pd.read_excel(impostos_taxas_comissao)

        # Lista de bases com todas as informações necessárias
        bases = [
            {"nome": "Vendas Mensal Brutas 💵", "data": vendas, "collection_name": f"venda_mensal_bruta_{ano}"},
            {"nome": "Custo Fixo 💼", "data": custo_fixo_df, "collection_name": f"custos_fixos_{ano}"},
            {"nome": "Impostos e Taxas 🧾", "data": imp_tax, "collection_name": f"impostos_taxas_{ano}"}
        ]
        
        lista_bases_subir = []
        st.subheader("Confira as bases anexadas antes de continuar.")

        # Exibe os dataframes para conferência
        for base in bases:
            dict_base = base["data"].to_dict(orient='records')
            lista_bases_subir.append({
                "data": dict_base,
                "collection_name": base["collection_name"],
                "nome": base["nome"]
            })
            
            st.markdown(f"**{base['nome']}**")
            st.dataframe(base["data"])
            st.write("---")

        # Botão de atualização com status
        button = st.button("Seguir Com a Atualização")
        
        if button:
            with st.status("🚀 Atualizando banco de dados...", expanded=True) as status:
                for base in lista_bases_subir:
                    status.write(f"⏳ Processando {base['nome']}...")
                    
                    # Faz o upload para o MongoDB
                    try:
                        subir_dados_mongodb(
                            "rentabilidade_anual", 
                            base["collection_name"], 
                            base["data"]
                        )
                        status.write(f"✅ {base['nome']} atualizada com sucesso!")
                    except Exception as e:
                        status.write(f"❌ Erro ao atualizar {base['nome']}: {str(e)}")
                    
                    time.sleep(0.5)  # Pequena pausa para visualização
                
                status.update(
                    label="✅ Todas as bases foram atualizadas com sucesso!",
                    state="complete",
                    expanded=False
                )
            
            st.balloons()  # Efeito visual de confirmação
            return None
            
        return lista_bases_subir  # Retorna apenas se o botão não foi pressionado
    else:
        if not ano:
            st.warning("Por favor, informe o ano")
        else:
            st.warning("Aguardando upload de todos os arquivos...")
        return None