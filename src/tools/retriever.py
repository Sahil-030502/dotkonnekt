# src/tools/retriever.py
# Uses native ChromaDB — no LangChain
from src.tools.vectorstore import similarity_search
from src.utils.config import TOP_K_RESULTS


def retrieve(query: str, run_id: str = None, k: int = None) -> list[dict]:
    """
    Retrieve the most relevant chunks (text + image descriptions)
    for a natural language query.

    Scoped to run_id when provided so results come only from the
    specific uploaded document, not the entire vector store.

    Returns a list of dicts: {text, metadata, distance}
    """
    k = k or TOP_K_RESULTS
    return similarity_search(query, run_id=run_id, k=k)
