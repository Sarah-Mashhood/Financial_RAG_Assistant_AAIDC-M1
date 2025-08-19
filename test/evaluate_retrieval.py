"""
Evaluate both retrieval and generation quality.
- Retrieval: Checks if expected keywords are present in retrieved chunks.
- Generation: Runs query_financials() and checks if LLM response contains expected keywords.
- Logs both results into a CSV file.
"""

import os
import warnings
import csv
from datetime import datetime

warnings.filterwarnings("ignore", category=FutureWarning)

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

# Import your query pipeline
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from query import query_financials

# Load environment
load_dotenv()
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR")

# === Setup embeddings & Chroma client ===
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
collection = client.get_or_create_collection("financials")


# === Define evaluation queries with expected keywords ===
test_queries = [
    {
        "query": "What was the company's revenue in 2024?",
        "expected_keywords": ["revenue", "2024"]
    },
    {
        "query": "List key financial ratios like ROE, ROA, and profit margin.",
        "expected_keywords": ["ROE", "ROA", "profit margin"]
    },
    {
        "query": "What was the efficiency ratio in the last quarter?",
        "expected_keywords": ["efficiency ratio", "quarter"]
    },
    {
        "query": "Compare revenue and net profit year-over-year.",
        "expected_keywords": ["revenue", "net profit"]
    },
]


# === Evaluation Function ===
def evaluate_retrieval_and_generation(k: int = 3, log_to_csv: bool = True):
    total_queries = len(test_queries)
    retrieval_hits, generation_hits = 0, 0
    results_log = []

    for tq in test_queries:
        query = tq["query"]
        expected_keywords = tq["expected_keywords"]

        # ---- Retrieval Evaluation ----
        query_embedding = embedding_model.embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents"]
        )
        retrieved_chunks = results.get("documents", [[]])[0]
        retrieved_text = " ".join(retrieved_chunks).lower()

        retrieval_found = all(kw.lower() in retrieved_text for kw in expected_keywords)
        retrieval_status = "PASS" if retrieval_found else "FAIL"
        if retrieval_found:
            retrieval_hits += 1

        # ---- Generation Evaluation ----
        llm_response = query_financials(query).lower()
        generation_found = all(kw.lower() in llm_response for kw in expected_keywords)
        generation_status = "PASS" if generation_found else "FAIL"
        if generation_found:
            generation_hits += 1

        # ---- Logging ----
        results_log.append({
            "query": query,
            "expected_keywords": ", ".join(expected_keywords),
            "retrieved_preview": retrieved_chunks[0][:120] if retrieved_chunks else "None",
            "retrieval_status": retrieval_status,
            "llm_response_preview": llm_response[:120] + ("..." if len(llm_response) > 120 else ""),
            "generation_status": generation_status
        })

        print(f"\n🔎 Query: {query}")
        print(f" Retrieval -> {retrieval_status}")
        print(f" Generation -> {generation_status}")

    # ---- Final Summary ----
    print("\n📊 Evaluation Summary")
    print("=" * 40)
    print(f"Retrieval Hit Rate@{k}: {retrieval_hits / total_queries:.2f}")
    print(f"Generation Hit Rate: {generation_hits / total_queries:.2f}")
    print("=" * 40)

    # ---- Save Results to CSV ----
    if log_to_csv:
        os.makedirs("evaluation_logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join("evaluation_logs", f"rag_eval_{timestamp}.csv")

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["query", "expected_keywords", "retrieved_preview", "retrieval_status", "llm_response_preview", "generation_status"]
            )
            writer.writeheader()
            writer.writerows(results_log)

        print(f"\n📂 Results logged to: {csv_path}")


if __name__ == "__main__":
    evaluate_retrieval_and_generation(k=3, log_to_csv=True)
