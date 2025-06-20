from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import streamlit as st

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