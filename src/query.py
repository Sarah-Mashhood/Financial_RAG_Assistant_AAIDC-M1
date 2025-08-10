import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from langchain_groq import ChatGroq
from datetime import datetime

load_dotenv()

VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
collection = client.get_or_create_collection("financials")

llm = ChatGroq(model_name=os.getenv("GROQ_MODEL"))

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def query_financials(user_query):
    query_embedding = embedding_model.embed_query(user_query)
    results = collection.query(query_embeddings=[query_embedding], n_results=4, include=["documents", "metadatas"])
    
    documents = results.get("documents", [[]])[0]

    if not documents or all(doc.strip() == "" for doc in documents):
        return "Information not available."

    context = "\n\n".join(documents)

    final_prompt = f"""
You are a financial analysis assistant with access to a company's financial report. Use only the information provided in the context below to answer the user's question accurately and professionally.

Instructions:
- Respond with clear, concise, and relevant financial insights.
- Present all numerical figures in a clear and well-formatted manner (e.g., use commas for thousands, and include currency or percentage symbols where applicable).
- Do not add or assume any information outside the given context.
- If the answer is not available in the context, respond with: "Information not available."
- Do not mention the context or documents in your answer.

Context:
{context}

Question:
{user_query}

Answer:
"""

    response = llm.invoke(final_prompt)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"response_{timestamp}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Question:\n{user_query}\n\n")
        f.write("Answer:\n")
        f.write(response.content.strip())

    return response.content.strip()

if __name__ == "__main__":
    while True:
        user_input = input("Ask a question about company financials: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = query_financials(user_input)
        print("\nAnswer:\n", response)
