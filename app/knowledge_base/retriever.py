import os

from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = "chroma_store"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _get_vectorstore(tenant_id: str) -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    # embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    persist_path = os.path.join(PERSIST_DIR, tenant_id)
    return Chroma(
        collection_name=tenant_id,
        embedding_function=embeddings,
        persist_directory=persist_path,
    )


def retrieve_context(tenant_id: str, query: str, k: int = 3) -> str:
    """Returns the top-k relevant chunks joined as a single string, or '' if none found."""
    vectorstore = _get_vectorstore(tenant_id)
    docs = vectorstore.similarity_search(query, k=k)
    if not docs:
        return ""
    return "\n\n".join(d.page_content for d in docs)
