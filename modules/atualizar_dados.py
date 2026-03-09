import pandas as pd
import streamlit as st
import time
from datetime import datetime
from Functions.mongo import *
from Functions.tratar_dados_format import *
from Functions.ui import *

# =========================================================
# HELPERS
# =========================================================

def get_mes_atual_str():
    return datetime.now().strftime("%m")


def get_mes_anterior_str():
    hoje = datetime.now()
    mes_atual = hoje.month
    mes_anterior = 12 if mes_atual == 1 else mes_atual - 1
    return f"{mes_anterior:02d}"


def get_ano_atual():
    return datetime.now().year


def carregar_dict_as_df(database_name, collection_name, doc_id, colunas):
    data = carregar_doc_mongo(database_name, collection_name, doc_id)
    df = pd.DataFrame(list(data.items()), columns=colunas)
    return df, data


def carregar_custos_mes(database_name, collection_name, doc_id, mes):
    custos_doc = carregar_doc_mongo(database_name, collection_name, doc_id)

    if not custos_doc or mes not in custos_doc:
        return None, custos_doc

    custos_mes = custos_doc[mes]
    df_custos = pd.DataFrame.from_dict(custos_mes, orient="index").reset_index()
    df_custos = df_custos.rename(columns={"index": "procedimento"})
    return df_custos, custos_doc


def garantir_coluna_custo_total(df):
    if df.empty:
        return df

    df = df.copy()
    df["CUSTO PRODUTO"] = pd.to_numeric(df["CUSTO PRODUTO"], errors="coerce").fillna(0.0)
    df["MOD"] = pd.to_numeric(df["MOD"], errors="coerce").fillna(0.0)
    df["CUSTO INSUMOS"] = pd.to_numeric(df["CUSTO INSUMOS"], errors="coerce").fillna(0.0)
    df["CUSTO TOTAL"] = df["CUSTO PRODUTO"] + df["MOD"] + df["CUSTO INSUMOS"]
    return df


def salvar_df_custos_no_mes(database_name, collection_name, doc_id, mes, df_custos):
    df_custos = garantir_coluna_custo_total(df_custos)

    for _, row in df_custos.iterrows():
        adicionar_ou_atualizar_custos(
            database_name=database_name,
            collection_name=collection_name,
            doc_id=doc_id,
            mes=mes,
            procedimento=row["procedimento"],
            produto_cost=float(row["CUSTO PRODUTO"]),
            mod_cost=float(row["MOD"]),
            consumiveis_cost=float(row["CUSTO INSUMOS"])
        )


def preparar_bases_upload(vmb, custo_fixo, impostos_taxas_comissao, ano):
    vendas = pd.read_excel(vmb)
    custo_fixo_df = pd.read_excel(custo_fixo)
    imp_tax = pd.read_excel(impostos_taxas_comissao)

    bases = [
        {"nome": "Vendas Mensal Brutas 💵", "data": vendas, "collection_name": f"venda_mensal_bruta_{ano}"},
        {"nome": "Custo Fixo 💼", "data": custo_fixo_df, "collection_name": f"custos_fixos_{ano}"},
        {"nome": "Impostos e Taxas 🧾", "data": imp_tax, "collection_name": f"impostos_taxas_{ano}"}
    ]
    return bases


def obter_contexto_base():
    database_name = "rentabilidade_anual"

    # De-Para nomenclaturas
    collection_name_1 = "De-Para Nomenclaturas"
    doc_id_1 = "DE_PARA_NOMENCLATURAS"
    df_depara_name, _ = carregar_dict_as_df(
        database_name, collection_name_1, doc_id_1, ["raw_name", "categoria"]
    )

    # De-Para tempos
    collection_name_2 = "De-Para Tempo Procedimentos"
    doc_id_2 = "DE_PARA_TEMPO_PROCEDIMENTOS"
    df_depara_tempo, _ = carregar_dict_as_df(
        database_name, collection_name_2, doc_id_2, ["categoria", "tempo"]
    )

    # Custos mensais
    collection_name_3 = "Custos Procedimentos Mensal"
    doc_id_3 = f"ALL_COSTS_{get_ano_atual()}_MENSAL"

    return {
        "database_name": database_name,
        "collection_name_1": collection_name_1,
        "doc_id_1": doc_id_1,
        "collection_name_2": collection_name_2,
        "doc_id_2": doc_id_2,
        "collection_name_3": collection_name_3,
        "doc_id_3": doc_id_3,
        "df_depara_name": df_depara_name,
        "df_depara_tempo": df_depara_tempo,
    }


# =========================================================
# ABA 1 - UPLOAD DE BASES
# =========================================================

def render_tab_upload_bases(database_name):
    st.subheader("Upload de Bases Mensais")
    st.caption("Envie os três arquivos do fechamento mensal e revise antes de subir no banco.")

    ano = st.text_input("Ano de referência", placeholder="Ex: 2026")

    col1, col2, col3 = st.columns(3)
    with col1:
        vmb = st.file_uploader("Vendas Mensal Brutas 💵", type=["xlsx"], key="upload_vmb")
    with col2:
        custo_fixo = st.file_uploader("Custo Fixo 💼", type=["xlsx"], key="upload_custo_fixo")
    with col3:
        impostos_taxas_comissao = st.file_uploader("Impostos e Taxas 🧾", type=["xlsx"], key="upload_impostos")

    if not ano:
        st.info("Informe o ano para habilitar o fluxo de atualização.")
        return

    if not (vmb and custo_fixo and impostos_taxas_comissao):
        st.info("Anexe os três arquivos para revisar e continuar.")
        return

    bases = preparar_bases_upload(vmb, custo_fixo, impostos_taxas_comissao, ano)

    st.markdown("### Revisão das bases")
    preview_tabs = st.tabs([base["nome"] for base in bases])

    lista_bases_subir = []
    for i, base in enumerate(bases):
        dict_base = base["data"].to_dict(orient="records")
        lista_bases_subir.append({
            "data": dict_base,
            "collection_name": base["collection_name"],
            "nome": base["nome"]
        })

        with preview_tabs[i]:
            st.dataframe(base["data"], use_container_width=True, height=350)
            st.caption(f"Collection de destino: `{base['collection_name']}`")

    if st.button("Subir bases para o MongoDB", type="primary", key="btn_subir_bases"):
        with st.status("Atualizando banco de dados...", expanded=True) as status:
            for base in lista_bases_subir:
                status.write(f"Processando {base['nome']}...")
                try:
                    subir_dados_mongodb(
                        database_name,
                        base["collection_name"],
                        base["data"]
                    )
                    status.write(f"✅ {base['nome']} atualizada com sucesso.")
                except Exception as e:
                    status.write(f"❌ Erro em {base['nome']}: {str(e)}")
                time.sleep(0.3)

            status.update(
                label="✅ Upload concluído com sucesso.",
                state="complete",
                expanded=False
            )

        st.success("As bases foram atualizadas.")
        st.balloons()


# =========================================================
# ABA 2 - CUSTOS DO MÊS
# =========================================================

def render_tab_custos_mes(database_name, collection_name_3, doc_id_3):
    st.subheader("Custos do Mês")
    st.caption("Revise ou replique os custos do mês atual com base no mês anterior.")

    mes_atual = get_mes_atual_str()
    mes_anterior = get_mes_anterior_str()

    info1, info2 = st.columns(2)
    with info1:
        st.metric("Mês atual", mes_atual)
    with info2:
        st.metric("Mês base sugerido", mes_anterior)

    df_custos_mes_atual, _ = carregar_custos_mes(
        database_name, collection_name_3, doc_id_3, mes_atual
    )

    if df_custos_mes_atual is not None:
        df_custos_mes_atual = garantir_coluna_custo_total(df_custos_mes_atual)

        st.success(f"Já existe dicionário de custos para o mês {mes_atual}.")
        st.dataframe(df_custos_mes_atual, use_container_width=True, height=450)
        return

    st.warning(
        f"Não foram encontrados custos cadastrados para o mês {mes_atual}. "
        f"Com base no mês anterior ({mes_anterior}) atualize os custos do mês atual."
    )

    df_custos_mes_anterior, _ = carregar_custos_mes(
        database_name, collection_name_3, doc_id_3, mes_anterior
    )

    if df_custos_mes_anterior is None:
        st.error("Também não foram encontrados custos no mês anterior.")
        return

    df_custos_mes_anterior = garantir_coluna_custo_total(df_custos_mes_anterior)

    st.markdown("### Edite os custos antes de subir")
    st.caption("Você pode ajustar qualquer valor. O custo total será recalculado automaticamente no salvamento.")

    colunas_editaveis = ["procedimento", "CUSTO PRODUTO", "MOD", "CUSTO INSUMOS"]

    df_editado = st.data_editor(
        df_custos_mes_anterior[colunas_editaveis],
        use_container_width=True,
        num_rows="dynamic",
        height=500,
        key="editor_custos_mes"
    )

    df_preview = garantir_coluna_custo_total(df_editado.copy())

    with st.expander("Prévia do custo total recalculado"):
        st.dataframe(df_preview, use_container_width=True, height=350)

    if st.button(f"Salvar custos no mês {mes_atual}", type="primary", key="btn_salvar_mes_atual"):
        salvar_df_custos_no_mes(
            database_name=database_name,
            collection_name=collection_name_3,
            doc_id=doc_id_3,
            mes=mes_atual,
            df_custos=df_editado
        )
        st.success(f"Custos do mês {mes_atual} salvos com sucesso.")
        st.rerun()


# =========================================================
# ABA 3 - DE-PARA
# =========================================================

def render_tab_depara(
    database_name,
    collection_name_1,
    collection_name_2,
    collection_name_3,
    doc_id_3,
    df_depara_name,
    df_depara_tempo
):
    st.subheader("De-Para de Procedimentos")
    st.caption("Cadastre novos procedimentos do CRM e vincule à categoria, tempo e custo.")

    mes_atual = get_mes_atual_str()

    df_custos_dict, _ = carregar_custos_mes(
        database_name, collection_name_3, doc_id_3, mes_atual
    )

    if df_custos_dict is None:
        mes_base = get_mes_anterior_str()
        df_custos_dict, _ = carregar_custos_mes(
            database_name, collection_name_3, doc_id_3, mes_base
        )

    if df_custos_dict is None:
        df_custos_dict = pd.DataFrame(
            columns=["procedimento", "CUSTO TOTAL", "CUSTO PRODUTO", "MOD", "CUSTO INSUMOS"]
        )

    df_custos_dict = garantir_coluna_custo_total(df_custos_dict)

    categorias_existentes = sorted(df_depara_name["categoria"].dropna().unique().tolist())

    with st.expander("Ver tabelas de apoio"):
        subtab1, subtab2, subtab3 = st.tabs(["Nomenclaturas", "Tempos", "Custos"])
        with subtab1:
            st.dataframe(df_depara_name, use_container_width=True, height=350)
        with subtab2:
            st.dataframe(df_depara_tempo, use_container_width=True, height=350)
        with subtab3:
            st.dataframe(df_custos_dict, use_container_width=True, height=350)

    st.markdown("### Novo procedimento")

    nome_novo_crm = st.text_input(
        "Nome do procedimento no CRM",
        placeholder="Digite exatamente como está no CRM"
    )

    opcao = st.selectbox(
        "Categoria de destino",
        options=["DIGITAR NOVA"] + categorias_existentes,
        help="Escolha uma categoria existente ou crie uma nova."
    )

    categoria_digitada = ""
    tempo_final = None
    custo_produto = 0.0
    custo_mod = 0.0
    custo_insumos = 0.0

    if opcao == "DIGITAR NOVA":
        st.markdown("#### Nova categoria")
        col1, col2 = st.columns(2)

        with col1:
            categoria_digitada = st.text_input("Nome da nova categoria")
            tempo_digitado = st.number_input("Tempo do procedimento (em minutos)", min_value=0, step=5)

        with col2:
            custo_produto = st.number_input("Custo do produto (R$)", min_value=0.0, step=1.0)
            custo_mod = st.number_input("Custo da aplicação / MOD (R$)", min_value=0.0, step=1.0)
            custo_insumos = st.number_input("Custo dos consumíveis (R$)", min_value=0.0, step=1.0)

        nome_para_de_para = categoria_digitada.strip().upper()
        tempo_final = minutos_para_hhmmss(int(tempo_digitado))

    else:
        nome_para_de_para = opcao.strip().upper()
        tempo_final = pegar_tempo_do_prcedimento(df_depara_tempo, nome_para_de_para)

        try:
            custo_produto, custo_mod, custo_insumos = pegar_custos_do_prcedimento(
                df_custos_dict,
                nome_para_de_para
            )
        except Exception:
            custo_produto, custo_mod, custo_insumos = 0.0, 0.0, 0.0

    custo_total = custo_produto + custo_mod + custo_insumos

    st.markdown("### Resumo do cadastro")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Categoria", nome_para_de_para if nome_para_de_para else "-")
    r2.metric("Tempo", tempo_final if tempo_final else "-")
    r3.metric("Custo Produto", f"R$ {custo_produto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    r4.metric("Custo Total", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if st.button("Salvar novo procedimento", type="primary", key="btn_salvar_depara"):
        if not nome_novo_crm.strip():
            st.error("Digite o nome do procedimento no CRM.")
            st.stop()

        if not nome_para_de_para:
            st.error("Defina uma categoria.")
            st.stop()

        if not tempo_final:
            st.error("Defina o tempo do procedimento.")
            st.stop()

        adicionar_ou_atualizar_depara(
            database_name=database_name,
            collection_name=collection_name_1,
            raw_name=nome_novo_crm.strip(),
            categoria=nome_para_de_para
        )

        adicionar_ou_atualizar_tempo(
            database_name=database_name,
            collection_name=collection_name_2,
            categoria=nome_para_de_para,
            tempo=tempo_final
        )

        adicionar_ou_atualizar_custos(
            database_name=database_name,
            collection_name=collection_name_3,
            doc_id=doc_id_3,
            mes=mes_atual,
            procedimento=nome_para_de_para,
            produto_cost=custo_produto,
            mod_cost=custo_mod,
            consumiveis_cost=custo_insumos
        )

        st.success("Procedimento salvo com sucesso.")
        st.rerun()


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

def atualizar_banco_de_dados():
    aplicar_ui_pro_corpo(
        page_title="Atualizar Banco de Dados",
        subtitle="Gerencie uploads mensais, custos do mês e de-para de procedimentos em um único lugar."
    )

    ctx = obter_contexto_base()

    tab1, tab2, tab3 = st.tabs([
        "📤 Upload de Bases",
        "💰 Custos do Mês",
        "🧩 De-Para de Procedimentos"
    ])

    with tab1:
        abrir_card_ui()
        render_tab_upload_bases(ctx["database_name"])
        fechar_card_ui()

    with tab2:
        abrir_card_ui()
        render_tab_custos_mes(
            database_name=ctx["database_name"],
            collection_name_3=ctx["collection_name_3"],
            doc_id_3=ctx["doc_id_3"]
        )
        fechar_card_ui()

    with tab3:
        abrir_card_ui()
        render_tab_depara(
            database_name=ctx["database_name"],
            collection_name_1=ctx["collection_name_1"],
            collection_name_2=ctx["collection_name_2"],
            collection_name_3=ctx["collection_name_3"],
            doc_id_3=ctx["doc_id_3"],
            df_depara_name=ctx["df_depara_name"],
            df_depara_tempo=ctx["df_depara_tempo"]
        )
        fechar_card_ui()