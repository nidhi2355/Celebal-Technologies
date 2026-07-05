import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from ingestion import ingest_global_health_data
from chunking import split_health_indicators


DB_DIR = "./storage_db"
DATA_DIR = "./health_vault"


def build_or_load_vector_store():

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Load existing DB
    if os.path.exists(DB_DIR) and os.listdir(DB_DIR):
        print("[+] Loading existing vector database...")
        return Chroma(
            persist_directory=DB_DIR,
            embedding_function=embedding
        )

    print("[*] Creating new vector database...")

    docs = ingest_global_health_data(DATA_DIR)

    if not docs:
        raise ValueError("No documents found in health_vault")

    chunks = split_health_indicators(docs)

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=DB_DIR
    )

    print("[+] Vector DB created successfully")
    return db


if __name__ == "__main__":
    build_or_load_vector_store()