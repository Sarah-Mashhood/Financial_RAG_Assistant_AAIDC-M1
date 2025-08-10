from graphviz import Digraph

# High-Level Architecture Diagram
arch = Digraph(comment="Financial RAG Assistant Architecture", format='png')

# Define styles for tech components
def add_component(dot, name, label, shape="box", style="filled", color="lightblue"):
    dot.node(name, label, shape=shape, style=style, fillcolor=color)

# User and UI
add_component(arch, "user", "User", shape="oval", color="lightyellow")
add_component(arch, "ui", "Streamlit Frontend", shape="box", color="lightblue")

# Ingestion
add_component(arch, "ingest", "Ingestion Pipeline\n(ingest.py)", color="lightgreen")
add_component(arch, "embed", "HuggingFace Embeddings\n(all-MiniLM-L6-v2)", color="lightpink")
add_component(arch, "vectordb", "Vector DB\nChromaDB", color="lightgrey")

# Query
add_component(arch, "query", "Query Pipeline\n(query.py)", color="lightgreen")
add_component(arch, "llm", "Groq API\n(LLM)", color="orange")

# Output
add_component(arch, "answer", "Answer Display", color="lightyellow")

# Edges
arch.edge("user", "ui", label="Access via browser")
arch.edge("ui", "ingest", label="Upload PDF")
arch.edge("ingest", "embed", label="Chunk & Embed")
arch.edge("embed", "vectordb", label="Store embeddings")
arch.edge("ui", "query", label="Ask question")
arch.edge("query", "vectordb", label="Retrieve relevant chunks")
arch.edge("query", "llm", label="Send context + question")
arch.edge("llm", "answer", label="Generate answer")
arch.edge("answer", "user", label="Display in UI")


# Save & render
output_path = "financial_rag_architecture"
arch.render(output_path, cleanup=True)

print(f"Diagram saved as {output_path}.png")

