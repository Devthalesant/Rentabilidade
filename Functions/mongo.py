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

def carregar_doc_mongo(database_name: str, collection_name: str,doc_id:str) -> dict:
    DOC_ID = doc_id
    col = get_collection(database_name, collection_name)
    doc = col.find_one({"_id": DOC_ID}, {"data": 1})
    return (doc or {}).get("data", {})


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


def adicionar_ou_atualizar_depara(database_name: str, collection_name: str, raw_name: str, categoria: str):
    client = MongoClient(uri)
    col = client[database_name][collection_name]
    DOC_ID = "DE_PARA_NOMENCLATURAS"

    col.update_one(
        {"_id": DOC_ID},
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