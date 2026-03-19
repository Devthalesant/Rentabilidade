import pandas as pd
import streamlit as st
import time
from datetime import datetime
from Functions.mongo import *
from Functions.tratar_dados_format import *
from Functions.ui import *
from Functions.vmb import *
from Functions.dictionaries import *
from Functions.aux_generic_functions import *

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


def preparar_bases_upload(vmb, custo_fixo, impostos_taxas_comissao):
    vendas = pd.read_excel(vmb)
    custo_fixo_df = pd.read_excel(custo_fixo)
    imp_tax = pd.read_excel(impostos_taxas_comissao)

    return [
        {"nome": "Custo Fixo 💼", "data": custo_fixo_df},
        {"nome": "Impostos e Taxas 🧾", "data": imp_tax},
        {"nome": "Vendas Mensal Brutas 💵", "data": vendas},
    ]


# =========================================================
# CONTEXTO BASE COM CACHE
# =========================================================

@st.cache_data(show_spinner="Carregando dados do banco...")
def obter_contexto_base():
    database_name = "rentabilidade_anual"

    collection_name_1 = "De-Para Nomenclaturas"
    doc_id_1 = "DE_PARA_NOMENCLATURAS"
    df_depara_name, _ = carregar_dict_as_df(
        database_name, collection_name_1, doc_id_1, ["raw_name", "categoria"]
    )

    df_depara_name["categoria"] = df_depara_name["categoria"].apply(
        lambda x: x if isinstance(x, str) else None
    )
    df_depara_name = df_depara_name.dropna(subset=["categoria"])

    collection_name_2 = "De-Para Tempo Procedimentos"
    doc_id_2 = "DE_PARA_TEMPO_PROCEDIMENTOS"
    df_depara_tempo, _ = carregar_dict_as_df(
        database_name, collection_name_2, doc_id_2, ["categoria", "tempo"]
    )

    collection_name_3 = "Custos Procedimentos Mensal"
    doc_id_3 = f"ALL_COSTS_{get_ano_atual()}_MENSAL"

    collection_name_4 = "De-Para Categorias"
    doc_id_4 = "DE_PARA_CATEGORIAS"
    df_depara_categoria, _ = carregar_dict_as_df(
        database_name, collection_name_4, doc_id_4, ["categoria", "grupo"]
    )

    return {
        "database_name": database_name,
        "collection_name_1": collection_name_1,
        "doc_id_1": doc_id_1,
        "collection_name_2": collection_name_2,
        "doc_id_2": doc_id_2,
        "collection_name_3": collection_name_3,
        "doc_id_3": doc_id_3,
        "collection_name_4": collection_name_4,
        "doc_id_4": doc_id_4,
        "df_depara_categoria": df_depara_categoria,
        "df_depara_name": df_depara_name,
        "df_depara_tempo": df_depara_tempo,
    }


def invalidar_cache_contexto():
    obter_contexto_base.clear()


# =========================================================
# ABA 1 - UPLOAD DE BASES
# =========================================================

def render_tab_upload_bases(database_name):
    st.subheader("Upload de Bases Mensais")
    st.caption("Envie os três arquivos do fechamento mensal e revise antes de subir no banco.")

    ano = st.text_input("Ano de referência", placeholder="Ex: 2026")
    mes_str = st.text_input("Mês de referência em numeral", placeholder="Ex: 2", value="1")

    if not ano:
        st.info("Informe o ano para habilitar o fluxo de atualização.")
        return

    try:
        mes = int(mes_str)
        if mes < 1 or mes > 12:
            st.warning("O mês deve estar entre 1 e 12.")
            return
    except ValueError:
        st.warning("Digite um mês válido em formato numérico.")
        return

    Appointments_dic, Sales_dic, Month_dic, duration_dic, all_costs_2024, all_costs_2025, all_costs_2025_black = obter_dicionarios()
    nome_mes = Month_dic[mes]

    st.write(f"As bases serão atualizadas no Mongo com competência de: **{nome_mes}/{ano}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        vmb = st.file_uploader("Vendas Mensal Brutas 💵", type=["xlsx"], key="upload_vmb")
    with col2:
        custo_fixo = st.file_uploader("Custo Fixo 💼", type=["xlsx"], key="upload_custo_fixo")
    with col3:
        impostos_taxas_comissao = st.file_uploader("Impostos e Taxas 🧾", type=["xlsx"], key="upload_impostos")

    if not (vmb and custo_fixo and impostos_taxas_comissao):
        st.info("Anexe os três arquivos para revisar e continuar.")
        return

    bases = preparar_bases_upload(vmb, custo_fixo, impostos_taxas_comissao)

    st.markdown("### Revisão das bases")
    preview_tabs = st.tabs([base["nome"] for base in bases])

    for i, base in enumerate(bases):
        with preview_tabs[i]:
            st.dataframe(base["data"], use_container_width=True, height=350)

    if st.button("Subir bases para o MongoDB", type="primary", key="btn_subir_bases"):
        with st.status("Atualizando banco de dados...", expanded=True) as status:
            for base in bases:
                nome_da_base = base["nome"]
                df_base = base["data"]
                status.write(f"Processando {nome_da_base}...")

                try:
                    if nome_da_base == "Impostos e Taxas 🧾":
                        subir_custos_financeiros_periodo(df_base, int(ano), mes, nome_mes)
                        status.write(f"✅ {nome_da_base} atualizada com sucesso.")

                    elif nome_da_base == "Custo Fixo 💼":
                        subir_custos_fixos_periodo(df_base, int(ano), mes, nome_mes)
                        status.write(f"✅ {nome_da_base} atualizada com sucesso.")

                    elif nome_da_base == "Vendas Mensal Brutas 💵":
                        resultado = criar_base_final(df_base)

                        if resultado is None:
                            status.write("❌ A base de vendas não foi tratada. Verifique os cadastros obrigatórios.")
                            continue

                        df_tempo_unidade_mes, base_tratada, msg1, msg2, msg3, msg4 = resultado

                        for msg in [msg1, msg2, msg3, msg4]:
                            if msg:
                                status.write(msg)

                        subir_dados_tratados(base_tratada)
                        status.write(f"✅ {nome_da_base} tratada e atualizada com sucesso.")

                except Exception as e:
                    status.write(f"❌ Erro em {nome_da_base}: {str(e)}")

                time.sleep(0.3)

            status.update(label="✅ Upload concluído com sucesso.", state="complete", expanded=False)

        st.session_state["aba_atualizar_banco_pendente"] = "📤 Upload de Bases"
        st.session_state["flash_success"] = "✅ As bases foram atualizadas com sucesso."
        st.rerun()


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

    df_editado = st.data_editor(
        df_custos_mes_anterior[["procedimento", "CUSTO PRODUTO", "MOD", "CUSTO INSUMOS"]],
        use_container_width=True,
        num_rows="dynamic",
        height=500,
        key="editor_custos_mes"
    )

    with st.expander("Prévia do custo total recalculado"):
        st.dataframe(garantir_coluna_custo_total(df_editado.copy()), use_container_width=True, height=350)

    if st.button(f"Salvar custos no mês {mes_atual}", type="primary", key="btn_salvar_mes_atual"):
        salvar_df_custos_no_mes(
            database_name=database_name,
            collection_name=collection_name_3,
            doc_id=doc_id_3,
            mes=mes_atual,
            df_custos=df_editado
        )
        st.session_state["aba_atualizar_banco_pendente"] = "💰 Custos do Mês"
        st.session_state["flash_success"] = f"✅ Custos do mês {mes_atual} salvos com sucesso."
        st.rerun()


# =========================================================
# ABA 3 - DE-PARA
# =========================================================

def _init_depara_state():
    defaults = {
        "depara_nome_crm": "",
        "depara_opcao_valor": "DIGITAR NOVA",
        "depara_nova_categoria": "",
        "depara_tempo_min": 0,
        "depara_grupo": "Estética",
        "depara_custo_produto": 0.0,
        "depara_custo_mod": 0.0,
        "depara_custo_insumos": 0.0,
        "depara_salvo": False,
        "df_upload_depara_validado": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _limpar_depara_state():
    keys_para_deletar = [
        "depara_nome_crm",
        "depara_opcao_valor",
        "depara_nova_categoria",
        "depara_tempo_min",
        "depara_grupo",
        "depara_custo_produto",
        "depara_custo_mod",
        "depara_custo_insumos",
        "depara_salvo",
    ]
    for key in keys_para_deletar:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state["df_upload_depara_validado"] = None


def render_tab_depara(
    database_name,
    collection_name_1,
    collection_name_2,
    collection_name_3,
    collection_name_4,
    doc_id_3,
    df_depara_name,
    df_depara_tempo,
    df_depara_categoria,
):
    st.subheader("De-Para de Procedimentos")
    st.caption("Cadastre novos procedimentos do CRM e vincule à categoria, tempo e custo.")

    _init_depara_state()

    mes_atual = get_mes_atual_str()

    df_custos_dict, _ = carregar_custos_mes(database_name, collection_name_3, doc_id_3, mes_atual)
    if df_custos_dict is None:
        df_custos_dict, _ = carregar_custos_mes(
            database_name, collection_name_3, doc_id_3, get_mes_anterior_str()
        )
    if df_custos_dict is None:
        df_custos_dict = pd.DataFrame(
            columns=["procedimento", "CUSTO TOTAL", "CUSTO PRODUTO", "MOD", "CUSTO INSUMOS"]
        )
    df_custos_dict = garantir_coluna_custo_total(df_custos_dict)

    grupos_validos = sorted(["Estética", "Injetáveis e Invasivos", "Produtos", "Depilação"])

    categorias_existentes = sorted(
        df_depara_name["categoria"]
        .dropna()
        .apply(lambda x: x if isinstance(x, str) else None)
        .dropna()
        .unique()
        .tolist()
    )

    lookup_categoria_grupo = dict(
        zip(df_depara_categoria["categoria"], df_depara_categoria["grupo"])
    )

    with st.expander("Ver tabelas de apoio"):
        subtab1, subtab2, subtab3, subtab4 = st.tabs(["Nomenclaturas", "Tempos", "Custos", "Categorias"])
        with subtab1:
            st.dataframe(df_depara_name, use_container_width=True, height=350)
        with subtab2:
            st.dataframe(df_depara_tempo, use_container_width=True, height=350)
        with subtab3:
            st.dataframe(df_custos_dict, use_container_width=True, height=350)
        with subtab4:
            st.dataframe(df_depara_categoria, use_container_width=True, height=350)

    st.markdown("### Novo procedimento")

    opcoes = ["DIGITAR NOVA"] + categorias_existentes

    nome_novo_crm = st.text_input(
        "Nome do procedimento no CRM",
        placeholder="Digite exatamente como está no CRM",
        key="depara_nome_crm"
    )

    opcao = st.selectbox(
        "Categoria de destino",
        options=opcoes,
        key="depara_opcao_valor",
        help="Escolha uma categoria existente ou crie uma nova."
    )

    categoria_digitada = ""
    tempo_final = None
    custo_produto = 0.0
    custo_mod = 0.0
    custo_insumos = 0.0
    grupo_final = "-"

    if opcao == "DIGITAR NOVA":
        st.markdown("#### Nova categoria")
        col1, col2 = st.columns(2)

        with col1:
            categoria_digitada = st.text_input(
                "Nome da nova categoria",
                key="depara_nova_categoria"
            )
            tempo_digitado = st.number_input(
                "Tempo do procedimento (em minutos)",
                min_value=0,
                step=5,
                key="depara_tempo_min"
            )
            grupo_selecionado = st.selectbox(
                "Grupo da categoria",
                options=grupos_validos,
                key="depara_grupo",
                help="Classifique a nova categoria entre os grupos disponíveis."
            )

        with col2:
            custo_produto = st.number_input(
                "Custo do produto (R$)", min_value=0.0, step=1.0, key="depara_custo_produto"
            )
            custo_mod = st.number_input(
                "Custo da aplicação / MOD (R$)", min_value=0.0, step=1.0, key="depara_custo_mod"
            )
            custo_insumos = st.number_input(
                "Custo dos consumíveis (R$)", min_value=0.0, step=1.0, key="depara_custo_insumos"
            )

        nome_para_de_para = categoria_digitada.strip().upper()
        tempo_final = minutos_para_hhmmss(int(tempo_digitado))
        grupo_final = grupo_selecionado

    else:
        nome_para_de_para = opcao.strip().upper()
        tempo_final = pegar_tempo_do_prcedimento(df_depara_tempo, nome_para_de_para)
        grupo_final = lookup_categoria_grupo.get(nome_para_de_para, "UNMAPPED")

        try:
            custo_produto, custo_mod, custo_insumos = pegar_custos_do_prcedimento(
                df_custos_dict, nome_para_de_para
            )
        except Exception:
            custo_produto, custo_mod, custo_insumos = 0.0, 0.0, 0.0

    custo_total = custo_produto + custo_mod + custo_insumos

    st.markdown("### Resumo do cadastro")
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Grupo", grupo_final)
    r2.metric("Categoria", nome_para_de_para if nome_para_de_para else "-")
    r3.metric("Tempo", tempo_final if tempo_final else "-")
    r4.metric("Custo Produto", f"R$ {custo_produto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    r5.metric("Custo Total", f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if st.button("Salvar novo procedimento", type="primary", key="btn_salvar_depara"):
        erros = []
        if not nome_novo_crm.strip():
            erros.append("Digite o nome do procedimento no CRM.")
        if not nome_para_de_para:
            erros.append("Defina uma categoria.")
        if not tempo_final:
            erros.append("Defina o tempo do procedimento.")

        if erros:
            for e in erros:
                st.error(e)
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

        if opcao == "DIGITAR NOVA":
            adicionar_ou_atualizar_depara(
                database_name=database_name,
                collection_name=collection_name_4,
                raw_name=nome_para_de_para,
                categoria=grupo_final,
                doc_id="DE_PARA_CATEGORIAS"
            )

        invalidar_cache_contexto()
        _limpar_depara_state()

        st.session_state["aba_atualizar_banco_pendente"] = "🧩 De-Para de Procedimentos"
        st.session_state["flash_success"] = "✅ Procedimento salvo com sucesso!"
        st.rerun()

    st.markdown("### 📄 Atualizar de-para via planilha")
    with st.container(border=True):
        st.markdown("### Atualização em lote")
        st.caption(
            "Baixe o modelo, preencha as linhas com os novos procedimentos e envie a planilha para atualizar o banco."
        )

        modelo_df = gerar_planilha_modelo_depara()
        modelo_xlsx = dataframe_para_excel_bytes(modelo_df)

        col_a, col_b = st.columns([1, 2])

        with col_a:
            st.download_button(
                label="📥 Baixar modelo",
                data=modelo_xlsx,
                file_name="Planilha_exemplo_depara.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_modelo_depara"
            )

        with col_b:
            st.info(
                "Colunas obrigatórias: Nome_procedimento_CRM, Procedimento_padronizado, "
                "Tempo_min, Custo_do_produto, custo_de_aplicacao, custo_dos_insumos e Categoria."
            )

        with st.form("form_upload_depara_lote", clear_on_submit=False):
            arquivo_postado = st.file_uploader(
                "Envie a planilha preenchida",
                type=["xlsx", "csv"],
                key="upload_planilha_depara_lote",
                help="Aceita arquivos .xlsx e .csv"
            )

            submitted_preview = st.form_submit_button("Validar planilha")

        if submitted_preview:
            st.session_state["aba_atualizar_banco_pendente"] = "🧩 De-Para de Procedimentos"

            if arquivo_postado is None:
                st.warning("Favor fazer o upload do arquivo antes de validar.")
            else:
                try:
                    arquivo_para_atualizar_de_para = ler_arquivo_upload_depara(arquivo_postado)
                    arquivo_para_atualizar_de_para = preparar_preview_upload_depara(
                        arquivo_para_atualizar_de_para
                    )

                    colunas_ausentes = validar_colunas_upload_depara(
                        arquivo_para_atualizar_de_para
                    )

                    if colunas_ausentes:
                        st.error("A planilha enviada não contém todas as colunas obrigatórias.")
                        st.write("Colunas ausentes:", colunas_ausentes)
                        st.session_state["df_upload_depara_validado"] = None
                    else:
                        st.success("Planilha validada com sucesso.")
                        st.markdown("### Prévia dos dados")
                        st.dataframe(
                            arquivo_para_atualizar_de_para,
                            use_container_width=True,
                            height=350
                        )

                        st.session_state["df_upload_depara_validado"] = arquivo_para_atualizar_de_para

                except Exception as e:
                    st.error(f"Erro ao ler a planilha: {str(e)}")
                    st.session_state["df_upload_depara_validado"] = None

        df_validado = st.session_state.get("df_upload_depara_validado")

        if df_validado is not None:
            st.markdown("### Confirmar atualização")
            st.caption(
                "Revise a prévia acima. Ao confirmar, os registros serão enviados para atualização do banco."
            )

            st.dataframe(df_validado, use_container_width=True, height=350)

            if st.button(
                "✅ Atualizar de-para em lote",
                type="primary",
                key="btn_atualizar_depara_lote"
            ):
                try:
                    with st.spinner("Atualizando de-para em lote..."):
                        resultado = atualizar_banco_de_dados_de_para_com_excel(df_validado)

                    if resultado.get("erros"):
                        for erro in resultado["erros"]:
                            st.error(erro)

                    if resultado.get("sucesso", False):
                        invalidar_cache_contexto()
                        st.session_state["df_upload_depara_validado"] = None
                        st.session_state["aba_atualizar_banco_pendente"] = "🧩 De-Para de Procedimentos"
                        st.session_state["flash_success"] = "✅ De-para atualizado com sucesso via planilha."
                        st.rerun()
                    else:
                        if resultado.get("mensagens"):
                            for msg in resultado["mensagens"]:
                                st.warning(msg)

                except Exception as e:
                    st.error(f"Erro ao atualizar o banco com a planilha: {str(e)}")


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

def atualizar_banco_de_dados():
    aplicar_ui_pro_corpo(
        page_title="Atualizar Banco de Dados",
        subtitle="Gerencie uploads mensais, custos do mês e de-para de procedimentos em um único lugar."
    )

    if "aba_atualizar_banco" not in st.session_state:
        st.session_state["aba_atualizar_banco"] = "🧩 De-Para de Procedimentos"

    if "aba_atualizar_banco_pendente" not in st.session_state:
        st.session_state["aba_atualizar_banco_pendente"] = None

    if "flash_success" not in st.session_state:
        st.session_state["flash_success"] = None

    # aplica mudança pendente antes do widget
    if st.session_state["aba_atualizar_banco_pendente"] is not None:
        st.session_state["aba_atualizar_banco"] = st.session_state["aba_atualizar_banco_pendente"]
        st.session_state["aba_atualizar_banco_pendente"] = None

    if st.session_state["flash_success"]:
        st.success(st.session_state["flash_success"])
        st.session_state["flash_success"] = None

    ctx = obter_contexto_base()

    opcoes_abas = [
        "📤 Upload de Bases",
        "💰 Custos do Mês",
        "🧩 De-Para de Procedimentos"
    ]

    if st.session_state["aba_atualizar_banco"] not in opcoes_abas:
        st.session_state["aba_atualizar_banco"] = "🧩 De-Para de Procedimentos"

    aba_escolhida = st.segmented_control(
        "Navegação",
        options=opcoes_abas,
        selection_mode="single",
        key="aba_atualizar_banco"
    )

    if aba_escolhida is None:
        aba_escolhida = st.session_state["aba_atualizar_banco"]

    if aba_escolhida == "📤 Upload de Bases":
        abrir_card_ui()
        render_tab_upload_bases(ctx["database_name"])
        fechar_card_ui()

    elif aba_escolhida == "💰 Custos do Mês":
        abrir_card_ui()
        render_tab_custos_mes(
            database_name=ctx["database_name"],
            collection_name_3=ctx["collection_name_3"],
            doc_id_3=ctx["doc_id_3"]
        )
        fechar_card_ui()

    elif aba_escolhida == "🧩 De-Para de Procedimentos":
        abrir_card_ui()
        render_tab_depara(
            database_name=ctx["database_name"],
            collection_name_1=ctx["collection_name_1"],
            collection_name_2=ctx["collection_name_2"],
            collection_name_3=ctx["collection_name_3"],
            collection_name_4=ctx["collection_name_4"],
            doc_id_3=ctx["doc_id_3"],
            df_depara_name=ctx["df_depara_name"],
            df_depara_tempo=ctx["df_depara_tempo"],
            df_depara_categoria=ctx["df_depara_categoria"]
        )
        fechar_card_ui()