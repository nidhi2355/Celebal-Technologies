from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

import os

DB_DIR = "./storage_db"


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def initialize_rag():

    print("[*] Loading embeddings...")
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("[*] Loading vector DB...")
    db = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embedding
    )

    retriever = db.as_retriever(search_kwargs={"k": 3})

    print("[*] Connecting to Ollama (phi3)...")
    # Added max_tokens (or num_predict) to forcefully prevent 7-minute infinite loops
    llm = ChatOllama(model="phi3", temperature=0)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a strict data-extractor. Read the Context below.\n"
         "If the Context DOES NOT explicitly contain the answer, output exactly one word: UNKNOWN.\n"
         "If the Context DOES contain the answer, provide a brief answer using ONLY that context.\n\n"
         "CRITICAL: You are strictly forbidden from using your pre-trained medical knowledge. Even if you know the answer to a general health or medical question, if the exact facts are not written in the Context below, you MUST output UNKNOWN.\n\n"
         "Context:\n{context}"),
        ("human", "{question}")
    ])

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("[+] RAG system ready!")
    return rag_chain


if __name__ == "__main__":

    rag = initialize_rag()

    while True:
        q = input("\nAsk AI (or exit): ")
        if q.lower() == "exit":
            break

        result = rag.invoke(q)

        print("\n🤖 Answer:\n", result)