import os
import tempfile
import shutil
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is importable
import sys
sys.path.append(os.path.abspath('.'))

# Import ingest and query helpers from the user's repo
try:
    from ingest import load_and_chunk_reports, embed_and_store
except Exception:
    # If ingest is in src, try that
    try:
        from src.ingest import load_and_chunk_reports, embed_and_store
    except Exception:
        load_and_chunk_reports = None
        embed_and_store = None

try:
    from query import query_financials
except Exception:
    try:
        from src.query import query_financials
    except Exception:
        query_financials = None

load_dotenv()

st.set_page_config(page_title="Financial RAG Assistant", page_icon="💼", layout="wide")

st.title("💼 Financial RAG Assistant")
st.markdown("Upload financial reports (PDF) to ingest into the vector DB, then ask questions about the company's financials.")

# Sidebar settings / environment info
with st.sidebar:
    st.header("Configuration")
    st.write("This app expects the repository's `ingest.py` and `query.py` to be available and functional.")
    VECTOR_DB_DIR = st.text_input("VECTOR_DB_DIR (env)", value=os.getenv("VECTOR_DB_DIR", "./vectordb"))
    GROQ_MODEL = st.text_input("GROQ_MODEL (env)", value=os.getenv("GROQ_MODEL", "gpt-4o-mini"))
    st.write("\\.env should contain GROQ_API_KEY and optional settings used by your ingest/query scripts.")
    st.markdown("---")
    st.write("**Status checks**")
    st.write(f"ingest functions available: {bool(load_and_chunk_reports and embed_and_store)}")
    st.write(f"query function available: {bool(query_financials)}")
    st.write(f"VECTOR_DB_DIR: `{VECTOR_DB_DIR}`")

# Tabs for Ingest and Chat
tab = st.tabs(["Ingest reports", "Chat with financials"])

with tab[0]:
    st.header("1) Ingest PDF reports")
    st.write("Upload one or more PDF files. Files will be saved to `data/reports` and then processed using your repo's ingest functions.")

    uploaded = st.file_uploader("Upload PDF(s)", type=["pdf"], accept_multiple_files=True)
    use_persistent = st.checkbox("Use persistent Chromadb client (recommended)", value=True)

    col1, col2 = st.columns(2)
    with col1:
        ingest_btn = st.button("Start ingestion")
    with col2:
        clear_btn = st.button("Clear uploaded temp files")

    if ingest_btn:
        if not uploaded:
            st.error("Please upload at least one PDF before ingesting.")
        else:
            # Save uploads into data/reports
            dest_dir = os.path.join("data", "reports")
            os.makedirs(dest_dir, exist_ok=True)

            temp_dir = tempfile.mkdtemp(prefix="streamlit_ingest_")
            try:
                st.info(f"Saving {len(uploaded)} file(s) to `{dest_dir}` and running ingest...")
                for f in uploaded:
                    out_path = os.path.join(dest_dir, f.name)
                    with open(out_path, "wb") as out:
                        out.write(f.getbuffer())

                if load_and_chunk_reports is None or embed_and_store is None:
                    st.error("Could not find ingest functions in the repo. Ensure `ingest.py` exports `load_and_chunk_reports` and `embed_and_store`.")
                else:
                    with st.spinner("Loading and chunking reports — this may take a while depending on file size..."):
                        docs = load_and_chunk_reports(dest_dir)
                        st.success(f"Loaded and chunked {len(docs)} pieces.")

                    with st.spinner("Embedding and storing chunks into the vector DB..."):
                        # allow the ingest helper to use persistent or in-memory
                        embed_and_store(docs, use_persistent=use_persistent)
                        st.success("Embedding + storage complete.")

                    st.balloons()
            except Exception as e:
                st.exception(e)
            finally:
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass

    if clear_btn:
        st.warning("Clearing `data/reports` folder (deleting files). Proceed with caution.")
        confirm = st.checkbox("Confirm delete files in data/reports")
        if confirm:
            folder = os.path.join("data", "reports")
            if os.path.exists(folder):
                for fname in os.listdir(folder):
                    try:
                        os.remove(os.path.join(folder, fname))
                    except Exception:
                        pass
                st.success("Cleared data/reports folder.")
            else:
                st.info("No data/reports folder found.")

with tab[1]:
    st.header("2) Chat with the ingested financials")
    st.write("Ask questions about the reports you ingested. The app will query the vector DB and return an LLM response using your repo's `query_financials` function.")

    if query_financials is None:
        st.error("`query_financials` not found. Ensure `query.py` exports a `query_financials(user_query)` function returning a string.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        question = st.text_input("Ask a question about the company's financials:")
        ask_btn = st.button("Ask")

        if ask_btn:
            if not question or question.strip() == "":
                st.error("Please type a question.")
            else:
                with st.spinner("Querying vector DB and LLM — this may take a few seconds..."):
                    try:
                        answer = query_financials(question)
                    except Exception as e:
                        st.exception(e)
                        answer = "Error during query. Check server logs and env variables."

                # store and render
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state.chat_history.append((timestamp, question, answer))

        # Render chat history
        if st.session_state.chat_history:
            st.markdown("---")
            for ts, q, a in reversed(st.session_state.chat_history):
                st.markdown(f"**{ts} — You:** {q}")
                st.markdown(f"**Assistant:** {a}")
                st.markdown("---")

# Footer / Run instructions
st.markdown("---")
st.caption("To run: `streamlit run streamlit_financial_rag_assistant.py`. Ensure required env vars are set in a .env file: VECTOR_DB_DIR, GROQ_API_KEY, GROQ_MODEL, etc.")
