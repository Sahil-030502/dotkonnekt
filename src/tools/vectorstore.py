# src/tools/vectorstore.py
# Native ChromaDB client — no LangChain
import chromadb
from chromadb.config import Settings

from src.library.embeddings import embed_texts, embed_query
from src.utils.config import VECTOR_DB_DIR


def _get_collection() -> chromadb.Collection:
    """Return (or create) the persistent ChromaDB collection."""
    client = chromadb.PersistentClient(
        path=VECTOR_DB_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    return client.get_or_create_collection(
        name="document_intelligence",
        metadata={"hnsw:space": "cosine"}
    )


def index_chunks(chunks: list, run_id: str) -> None:
    """
    Embed and store text chunks in ChromaDB.
    Each chunk is stored with run_id, chunk_id, page, and type metadata.
    """
    if not chunks:
        return

    collection = _get_collection()

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)

    collection.add(
        ids=[f"{run_id}_text_{c['chunk_id']}" for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "run_id": run_id,
                "chunk_id": c["chunk_id"],
                "page": c["page"],
                "type": "text"
            }
            for c in chunks
        ]
    )


def index_image_descriptions(image_descriptions: list, run_id: str) -> None:
    """
    Embed and store LLM-generated image descriptions in ChromaDB
    so images are retrievable as first-class content during Q&A.
    """
    valid = [d for d in image_descriptions if d.get("description")]
    if not valid:
        return

    collection = _get_collection()

    texts = [d["description"] for d in valid]
    embeddings = embed_texts(texts)

    collection.add(
        ids=[f"{run_id}_image_{d['chunk_id']}" for d in valid],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "run_id": run_id,
                "chunk_id": d["chunk_id"],
                "page": d["page"],
                "image_path": d.get("image_path", ""),
                "type": "image"
            }
            for d in valid
        ]
    )


def similarity_search(query: str, run_id: str = None, k: int = 5) -> list[dict]:
    """
    Return the top-k most similar documents to the query.
    Optionally filter by run_id to scope results to one document.

    Returns a list of dicts: {text, metadata, distance}
    """
    collection = _get_collection()

    query_embedding = embed_query(query)

    where = {"run_id": run_id} if run_id else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"]
    )

    docs = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        docs.append({
            "text": text,
            "metadata": meta,
            "distance": dist
        })

    return docs
