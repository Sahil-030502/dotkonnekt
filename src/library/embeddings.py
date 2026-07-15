# src/library/embeddings.py
# Raw OpenAI SDK — no LangChain
from openai import OpenAI
from src.utils.config import OPENAI_API_KEY, EMBEDDING_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of strings using the OpenAI embeddings endpoint.
    Returns a list of float vectors in the same order as the input.
    """
    if not texts:
        return []

    response = _client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )

    # Sort by index to guarantee order matches input
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]


def embed_query(text: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([text])[0]
