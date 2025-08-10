from setuptools import setup, find_packages

setup(
    name="financial_rag_assistant",
    version="0.1.0",
    author="Syeda Sarah Mashhood",
    description="A Financial RAG-based AI Assistant for answering queries using company financial reports.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "langchain",
        "openai",
        "chromadb",
        "python-dotenv",
        "PyMuPDF",
        "tqdm",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
