from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_health_indicators(
    documents: List[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> List[Document]:

    if not documents:
        print("[!] No documents to split.")
        return []

    print("[*] Chunking documents...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    print(f"[+] Created {len(chunks)} chunks")
    return chunks


if __name__ == "__main__":
    print("Chunking module ready.")