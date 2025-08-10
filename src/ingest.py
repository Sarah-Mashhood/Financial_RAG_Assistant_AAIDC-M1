import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from chromadb.config import Settings

import sys
sys.path.append(os.path.abspath("."))

from src.utils.file_loader import load_pdf_from_folder
from src.utils.text_helpers import split_documents

load_dotenv()

VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR")

def load_and_chunk_reports(folder_path):
    docs = load_pdf_from_folder(folder_path)
    return split_documents(docs)

def embed_and_store(docs, use_persistent=True):
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if use_persistent:
        client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    else:
        client = chromadb.Client()

    collection = client.get_or_create_collection(name="financials")

    for i, doc in enumerate(docs):
        text = doc.page_content
        metadata = doc.metadata
        id_ = f"doc_{i}"

        try:
            vector = embedding_model.embed_documents([text])
            collection.add(
                documents=[text],
                embeddings=vector,
                metadatas=[metadata],
                ids=[id_]
            )
        except Exception as e:
            print(f"Error embedding or storing document {i}: {e}")
            break

if __name__ == "__main__":
    print("Starting ingestion...")
    docs = load_and_chunk_reports("data/reports")
    print(f"Loaded and chunked {len(docs)} pieces.")
    embed_and_store(docs, use_persistent=True)
    print("Ingestion complete.")
