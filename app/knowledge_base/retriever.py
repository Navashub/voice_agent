import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = "chroma_store"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Cache both the embedding model and per-tenant vectorstores at module level.
# Without this, the embedding model reloads from disk on every single
# question — which is exactly the "Loading weights" spam on every turn.
_embeddings = None
_vectorstores = {}


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


def _get_vectorstore(tenant_id: str) -> Chroma:
    if tenant_id not in _vectorstores:
        persist_path = os.path.join(PERSIST_DIR, tenant_id)
        _vectorstores[tenant_id] = Chroma(
            collection_name=tenant_id,
            embedding_function=_get_embeddings(),
            persist_directory=persist_path,
        )
    return _vectorstores[tenant_id]


def retrieve_context(tenant_id: str, query: str, k: int = 3) -> str:
    """Returns the top-k relevant chunks joined as a single string, or '' if none found."""
    vectorstore = _get_vectorstore(tenant_id)
    docs = vectorstore.similarity_search(query, k=k)
    if not docs:
        return ""
    return "\n\n".join(d.page_content for d in docs)
