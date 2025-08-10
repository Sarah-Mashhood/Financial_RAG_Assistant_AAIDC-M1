import os
from langchain_community.document_loaders import PyMuPDFLoader

def load_pdf_from_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"📥 Loading PDF: {filename}")
            loader = PyMuPDFLoader(pdf_path)
            docs = loader.load()
            print(f"✅ Loaded {len(docs)} chunks from {filename}")
            for doc in docs:
                doc.metadata["source"] = filename
            return docs
    
    print("❌ No PDF file found in the folder.")
    return []
