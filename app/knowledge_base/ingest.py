"""
Ingest a tenant's markdown docs into their own Chroma collection.

Usage:
    python -m app.knowledge_base.ingest example_institute tenants_data/example_institute

Run this once whenever a tenant's source documents change.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import glob

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import MarkdownTextSplitter

PERSIST_DIR = "chroma_store"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def ingest_tenant(tenant_id: str, data_dir: str) -> None:
    splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = []

    for filepath in glob.glob(os.path.join(data_dir, "*.md")):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        chunks.extend(splitter.split_text(text))

    if not chunks:
        print(f"No .md files found in {data_dir} — nothing to ingest.")
        return

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    persist_path = os.path.join(PERSIST_DIR, tenant_id)

    Chroma.from_texts(
        chunks,
        embedding=embeddings,
        collection_name=tenant_id,
        persist_directory=persist_path,
    )

    print(f"Ingested {len(chunks)} chunks for tenant '{tenant_id}' into {persist_path}")


if __name__ == "__main__":
    tenant_id = sys.argv[1] if len(sys.argv) > 1 else "example_institute"
    data_dir = sys.argv[2] if len(sys.argv) > 2 else f"tenants_data/{tenant_id}"
    ingest_tenant(tenant_id, data_dir)
