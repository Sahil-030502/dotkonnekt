# src/nodes/qa.py
from src.tools.retriever import retrieve
from src.library.llm import llm
from src.library.prompts import QA_PROMPT
from src.tools.trace import create_trace


def qa_node(state):
    """
    Answer a natural language query over the uploaded document.
    Retrieves relevant text chunks AND image descriptions from ChromaDB,
    builds a cited context block, and passes it to the LLM.
    """
    docs = retrieve(state["query"], run_id=state["run_id"])

    if not docs:
        state["answer"] = (
            "No relevant content found in the document for this query. "
            "Make sure the document has been processed before querying."
        )
        state["trace"].append(
            create_trace("QA", "qa_node", "FAILED", "No documents retrieved")
        )
        return state

    # Build context — each doc is a plain dict: {text, metadata, distance}
    context_parts = []
    for doc in docs:
        meta = doc["metadata"]
        chunk_id = meta.get("chunk_id", "?")
        page = meta.get("page", "?")
        content_type = meta.get("type", "text")
        prefix = f"[Chunk {chunk_id} | Page {page} | {content_type}]"
        context_parts.append(f"{prefix}\n{doc['text']}")

    context = "\n\n".join(context_parts)

    prompt = QA_PROMPT.format(
        question=state["query"],
        context=context
    )

    response = llm.invoke(prompt)
    state["answer"] = response.content

    state["trace"].append(
        create_trace(
            "QA",
            "qa_node",
            "SUCCESS",
            f"Query answered using {len(docs)} chunks: {state['query'][:60]}"
        )
    )

    return state
