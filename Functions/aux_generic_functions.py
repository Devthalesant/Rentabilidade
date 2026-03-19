from io import BytesIO
import pandas as pd
import streamlit as st


def gerar_planilha_modelo_depara():
    colunas_planilha_sample = [
        "Nome_procedimento_CRM",
        "Procedimento_padronizado",
        "Tempo_min",
        "Custo_do_produto",
        "custo_de_aplicacao",
        "custo_dos_insumos",
        "Categoria",
    ]
    return pd.DataFrame(columns=colunas_planilha_sample)


def dataframe_para_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Aba_cadastro")
    return output.getvalue()


def ler_arquivo_upload_depara(arquivo):
    if arquivo is None:
        return None

    nome = arquivo.name.lower()

    if nome.endswith(".csv"):
        return pd.read_csv(arquivo)

    if nome.endswith(".xlsx"):
        return pd.read_excel(arquivo)

    raise ValueError("Formato não suportado. Envie um arquivo .xlsx ou .csv")


def validar_colunas_upload_depara(df):
    colunas_obrigatorias = [
        "Nome_procedimento_CRM",
        "Procedimento_padronizado",
        "Tempo_min",
        "Custo_do_produto",
        "custo_de_aplicacao",
        "custo_dos_insumos",
        "Categoria",
    ]

    colunas_ausentes = [col for col in colunas_obrigatorias if col not in df.columns]
    return colunas_ausentes


def preparar_preview_upload_depara(df):
    df_preview = df.copy()

    if "Tempo_min" in df_preview.columns:
        df_preview["Tempo_min"] = pd.to_numeric(df_preview["Tempo_min"], errors="coerce")

    for col in ["Custo_do_produto", "custo_de_aplicacao", "custo_dos_insumos"]:
        if col in df_preview.columns:
            df_preview[col] = pd.to_numeric(df_preview[col], errors="coerce")

    return df_preview