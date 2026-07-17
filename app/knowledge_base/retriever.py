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


def retrieve_context(tenant_id: str, query: str, k: int = 3, score_threshold: float = 0.3) -> str:
    """Returns the top-k *relevant* chunks joined as a string, or '' if none clear the threshold.

    similarity_search alone always returns its top-k matches even when nothing
    is actually relevant — which meant genuinely unanswerable questions were
    never being logged as knowledge gaps, since retrieval "succeeded" with
    irrelevant chunks. This threshold fixes that.

    score_threshold is a starting point, not gospel — print the scores below
    during testing and adjust if real questions are being wrongly filtered
    out (threshold too high) or clearly irrelevant chunks are still getting
    through (threshold too low).
    """
    vectorstore = _get_vectorstore(tenant_id)

    try:
        results = vectorstore.similarity_search_with_relevance_scores(query, k=k)
    except Exception:
        # Fallback for any vectorstore/embedding combo that doesn't support
        # relevance scoring — behave like before rather than crash.
        docs = vectorstore.similarity_search(query, k=k)
        return "\n\n".join(d.page_content for d in docs) if docs else ""

    print(f"[retrieval scores] query={query!r} -> {[(round(s, 3)) for _, s in results]}")

    relevant = [doc.page_content for doc, score in results if score >= score_threshold]
    return "\n\n".join(relevant)
