from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import streamlit as st
from datetime import datetime

uri = st.secrets.mongo_credentials.uri


def subir_dados_mongodb(database_name,collection_name,dados):

    client = MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]

    if len(dados) > 0:

        insert_result = collection.insert_many(dados)

    else:
        insert_result = None

    return insert_result

def pegar_dados_mongodb(database_name,collection_name, query=None):
    client = MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]

    # Use empty query if none is provided
    if query is None:
        query = {}

    # Apply the query to filter documents
    filtered_documents = collection.find(query)

    data = list(filtered_documents)
    df = pd.DataFrame(data).drop(columns=['_id'], errors='ignore')

    return df

def deletar_todos_documentos(database_name, collection_name, query=None):
    client = MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]

    # Delete all documents if no query is specified
    if query is None:
        result = collection.delete_many({})
    else:
        result = collection.delete_many(query)

    client.close()

#########################################################
# MONGODB 2.0
#########################################################

from pymongo import MongoClient, ReturnDocument
from datetime import datetime
import streamlit as st

def get_collection(database_name: str, collection_name: str):
    client = MongoClient(uri)
    db = client[database_name]
    return db[collection_name]

def ensure_depara_doc(database_name: str, collection_name: str):
    col = get_collection(database_name, collection_name)
    DOC_ID = "DE_PARA_NOMENCLATURAS"
    col.update_one(
        {"_id": DOC_ID},
        {"$setOnInsert": {
            "_id": DOC_ID,
            "type": "de_para_nomenclaturas",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "data": {},
        }},
        upsert=True
    )


## Função que pega de forma generalista todas as clusters que temos no MONGODB
def carregar_doc_mongo(
    database_name: str,
    collection_name: str,
    doc_id: str,
    sub_key: str = None,
    return_full_doc: bool = False,
    default=None,
    asdataframe: bool = False,
):
    col = get_collection(database_name, collection_name)
    doc = col.find_one({"_id": doc_id})

    if not doc:
        return default if default is not None else {}

    if return_full_doc:
        return doc

    data = doc.get("data", default if default is not None else {})

    # aplica sub_key primeiro
    if sub_key is not None:
        if isinstance(data, dict):
            data = data.get(sub_key, default if default is not None else {})
        else:
            data = default if default is not None else {}

    # depois transforma em dataframe, se pedido
    if asdataframe:
        data = carregar_como_dataframe(data)

    return data

## Tranforma os dados recebido da função carregar_doc_mongo em dataframe
def carregar_como_dataframe(data):
    if isinstance(data,list):
        df = pd.DataFrame(data)
    if isinstance(data,dict):
        df = pd.DataFrame.from_dict(data, orient="index").reset_index()
    
    return df


def criar_doc_depara_se_nao_existir(database_name: str, collection_name: str, de_para: dict,doc_id:str):

    client = MongoClient(uri)
    DOC_ID = doc_id
    col = client[database_name][collection_name]

    col.update_one(
        {"_id": DOC_ID},
        {"$setOnInsert": {
            "_id": DOC_ID,
            "type": "de_para_nomenclaturas",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "data": de_para
        }},
        upsert=True
    )

################################################################################################################
### FUNÇÕES PARA SUBIR ATUALIZAÇÕES NOS DICTIONARIES DE CUSTOS E DE-PARAS
### DE-PARA, TEMPO E CUSTOS (MOD,PRODUTO, INSUMO)
################################################################################################################

def adicionar_ou_atualizar_depara(
    database_name: str,
    collection_name: str,
    raw_name: str,
    categoria: str,
    doc_id: str = "DE_PARA_NOMENCLATURAS"   # <-- novo parâmetro com default
):
    client = MongoClient(uri)
    col = client[database_name][collection_name]

    col.update_one(
        {"_id": doc_id},
        {"$set": {
            f"data.{raw_name}": categoria,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )

def adicionar_ou_atualizar_tempo(database_name: str, collection_name: str, categoria: str, tempo: str):
    client = MongoClient(uri)
    col = client[database_name][collection_name]
    col.update_one(
        {"_id": "DE_PARA_TEMPO_PROCEDIMENTOS"},
        {"$set": {f"data.{categoria}": tempo, "updated_at": datetime.utcnow()}},
        upsert=True
    )

def adicionar_ou_atualizar_custos(
    database_name: str,
    collection_name: str,
    doc_id: str,
    mes: str,
    procedimento: str,
    produto_cost: float,
    mod_cost: float,
    consumiveis_cost: float
):
    client = MongoClient(uri)
    col = client[database_name][collection_name]

    custo_total = float(produto_cost) + float(mod_cost) + float(consumiveis_cost)

    col.update_one(
        {"_id": doc_id},
        {
            "$set": {
                f"data.{mes}.{procedimento}": {
                    "CUSTO TOTAL": custo_total,
                    "CUSTO PRODUTO": float(produto_cost),
                    "MOD": float(mod_cost),
                    "CUSTO INSUMOS": float(consumiveis_cost),
                },
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )

################################################################################################################
### FUNÇÕES PARA SUBIR AS BASES DE ATUALIZAÇÕES MENSAIS 
### VENDA MENSAL BRUTA, CUSTOS FIXOS, IMPOSTOS, TAXAS E COMISSÃO
################################################################################################################

def subir_dados_tratados(treated_vmb):

    uri = st.secrets.mongo_credentials.uri

    # Conectando ao MongoDB
    client = MongoClient(uri, retryWrites=True, serverSelectionTimeoutMS=30000)  # Altere o URI conforme necessário
    db = client['rentabilidade_anual']
    collection = db['Base_Rentabilidade_mensal']

    treated_vmb['periodo'] = treated_vmb['Ano'].astype(str) + '-' + treated_vmb['Mes_num'].astype(str).str.zfill(2)
        

    # Passo 3: Subir para o MongoDB
    # Convertendo o dataframe para um formato que o MongoDB compreende (lista de dicionários)
    records = treated_vmb.to_dict('records')
    collection.insert_many(records)
    
    sucess_message = f"Base tratada do período {treated_vmb['periodo']} adicionada com Sucesso !"

    return sucess_message


def subir_custos_fixos_periodo(
    df: pd.DataFrame,
    ano: int,
    mes: int,
    nome_mes: str = None
):
    client = MongoClient(uri)
    database_name = 'rentabilidade_anual'
    collection_name = 'Custos_Fixos'

    col = client[database_name][collection_name]

    mes = int(mes)
    ano = int(ano)
    periodo = f"{ano}-{str(mes).zfill(2)}"

    df = df.copy()
    colunas_remover = [c for c in ["Ano", "Mês_num", "Mês"] if c in df.columns]
    df_data = df.drop(columns=colunas_remover, errors="ignore")

    payload = {
        "_id": periodo,
        "Ano": ano,
        "Mês_num": mes,
        "Mês": nome_mes if nome_mes else None,
        "periodo": periodo,
        "row_count": len(df_data),
        "updated_at": datetime.utcnow(),
        "data": df_data.to_dict(orient="records")
    }

    col.update_one(
        {"_id": periodo},
        {
            "$set": payload,
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    print("Dados de Custo Fixo Adicionados ao banco de Dados!")

####################
# Ess é para puxar os dados trataods
####################

def consultar_dados_mongo(database_name, collection_name, ano=None, mes=None, periodo=None):
    """
    Função para consultar dados de uma base MongoDB com filtros dinâmicos.

    Parâmetros:
    - ano (int, opcional): O ano para filtrar os dados.
    - mes (int ou list, opcional): O mês ou lista de meses para filtrar os dados (1 a 12).
    - periodo (str ou list, opcional): O(s) período(s) no formato 'yyyy-mm'.

    Retorna:
    - pandas.DataFrame: Dados filtrados em um DataFrame.
    """
    # Conectando ao MongoDB
    client = MongoClient(uri)  # Coloque sua URI do MongoDB aqui
    db = client[database_name]
    collection = db[collection_name]

    # Inicializando o filtro
    filtro = {}

    # Filtro por ano
    if ano:
        filtro['Ano'] = ano

    # Filtro por mês
    if mes:
        if isinstance(mes, list):  # Se for uma lista de meses
            filtro['Mes_num'] = {'$in': [str(m).zfill(2) for m in mes]}  # Converte todos os meses em 2 dígitos
        else:
            filtro['Mes_num'] = str(mes).zfill(2)  # Se for um único mês, converte em 2 dígitos

    # Filtro por período (ano-mês)
    if periodo:
        if isinstance(periodo, list):  # Se for uma lista de períodos
            filtro['periodo'] = {'$in': periodo}
        else:
            filtro['periodo'] = periodo  # Se for um único período

    # Realizando a consulta no MongoDB
    dados = collection.find(filtro)

    # Convertendo os dados para um DataFrame
    df = pd.DataFrame(list(dados))

    # Fechar a conexão do Mongo
    client.close()

    return df


def subir_custos_financeiros_periodo(
    df: pd.DataFrame,
    ano: int,
    mes: int,
    nome_mes: str = None
):
    
    database_name = 'rentabilidade_anual'
    collection_name = 'impostos_taxas'
    client = MongoClient(uri)
    col = client[database_name][collection_name]

    mes = int(mes)
    ano = int(ano)
    periodo = f"{ano}-{str(mes).zfill(2)}"

    df = df.copy()

    if "Ano" in df.columns:
        df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")

    # aceita tanto Mês_num quanto Mes_num
    if "Mes_num" in df.columns and "Mês_num" not in df.columns:
        df = df.rename(columns={"Mes_num": "Mês_num"})

    if "Mês_num" in df.columns:
        df["Mês_num"] = pd.to_numeric(df["Mês_num"], errors="coerce").astype("Int64")
        df["Mês_num"] = df["Mês_num"].apply(
            lambda x: f"{int(x):02d}" if pd.notna(x) else None
        )

    if "Mês" in df.columns:
        df["Mês"] = df["Mês"].apply(lambda x: x.strip() if isinstance(x, str) else x)

    colunas_remover = [c for c in ["Ano", "Mês_num"] if c in df.columns]
    df_data = df.drop(columns=colunas_remover, errors="ignore")

    payload = {
        "_id": periodo,
        "Ano": ano,
        "Mês_num": mes,
        "Mês": nome_mes if nome_mes else None,
        "periodo": periodo,
        "row_count": len(df_data),
        "updated_at": datetime.utcnow(),
        "data": df_data.to_dict(orient="records")
    }

    col.update_one(
        {"_id": periodo},
        {
            "$set": payload,
            "$setOnInsert": {
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )