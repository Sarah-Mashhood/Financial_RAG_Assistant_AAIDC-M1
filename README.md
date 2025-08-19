# Financial RAG Assistant

A Retrieval-Augmented Generation (RAG) project that allows users to query company annual reports and get insights using a language model.

## Features

* Load and chunk financial PDF reports
* Embed chunks into a Chroma vector database
* Ask natural language questions about any report
* Interactive Streamlit frontend for easy PDF upload and conversational querying

## Setup

```bash
git clone <repo-url>
cd financial-rag-assistant
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env_example .env  # add your GROQ_API_KEY and VECTOR_DB_DIR
```

## Usage

### 1. Ingest documents (build vector store)

```bash
python src/ingest.py
```

### 2. Query via command line

```bash
python src/query.py
```

### 3. Run Streamlit frontend app

Start the interactive app that lets you upload PDFs and chat about company financials:

```bash
streamlit run streamlit_financial_rag_assistant.py
```

Then open the local URL (usually `http://localhost:8501`) in your browser.

---

## Limitations & Future Work

The Financial RAG Assistant currently achieves 100% generation accuracy but only ~25% retrieval accuracy, mainly due to chunking and PDF text extraction limitations. Future work will focus on improving retrieval with domain-specific embeddings, table-aware parsing, metadata filtering, and query expansion for financial terminology. Planned enhancements also include multi-document conversations, finance-specific summarization, and voice-based querying to make the system more robust and scalable.

## Safety & Responsible Usage

Guardrails are limited in the current version. Future updates will add content filtering, stricter safety protocols, and validation to ensure grounded and responsible outputs.

## Licensing & Usage Rights

Released under the MIT License, allowing free use, modification, and distribution for personal or commercial purposes. Users must provide their own API keys and comply with third-party licenses (Hugging Face, ChromaDB, Streamlit, Groq). Attribution to the original author (Syeda Sarah Mashhood) is encouraged.

## Streamlit Frontend Demo

Below is a preview of the Streamlit app UI for uploading financial reports and chatting interactively. Once the PDF is uploaded, ask questions about the financial report and get instant insights.

Here is the link to a little demo: https://www.loom.com/share/6108a917f93548258a6daaf324f8379a?sid=d2aacc64-491b-40c2-bcfa-ee8abb95d098





