import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def ingest_global_health_data(directory_path: str = "./health_vault") -> List[Document]:
    """
    Loads PDF files and converts them into LangChain Documents.
    """

    if not os.path.exists(directory_path):
        print(f"[*] Creating directory: {directory_path}")
        os.makedirs(directory_path)
        print("[!] Add your PDF files to this folder.")
        return []

    documents = []

    for file in os.listdir(directory_path):
        if file.lower().endswith(".pdf"):
            path = os.path.join(directory_path, file)
            print(f"[*] Loading {file}")

            try:
                loader = PyPDFLoader(path)
                pages = loader.load()
                documents.extend(pages)
                print(f"[+] Loaded {len(pages)} pages")
            except Exception as e:
                print(f"[!] Error loading {file}: {e}")

    print(f"[+] Total pages loaded: {len(documents)}")
    return documents


if __name__ == "__main__":
    ingest_global_health_data()