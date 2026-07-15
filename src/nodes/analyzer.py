import os
import json

from src.library.llm import llm
from src.library.prompts import CLAUSE_PROMPT, ENTITY_PROMPT, RISK_PROMPT
from src.library.checkpoint import save_checkpoint
from src.tools.trace import create_trace


def analyzer_node(state):

    chunk = state["chunks"][state["current_chunk"]]

    prompt = f"""
{CLAUSE_PROMPT}

{ENTITY_PROMPT}

{RISK_PROMPT}

Chunk:
{chunk["text"]}
"""

    try:

        response = llm.invoke(prompt)

        state["partial_results"].append({
            "chunk_id": chunk["chunk_id"],
            "page": chunk["page"],
            "analysis": response.content
        })

        state["trace"].append(
            create_trace(
                "Analyzer",
                "analyzer_node",
                "SUCCESS",
                f"Chunk {chunk['chunk_id']} processed"
            )
        )

    except Exception as e:

        state["failed_chunks"].append({
            "chunk_id": chunk["chunk_id"],
            "page": chunk["page"],
            "error": str(e)
        })

        state["trace"].append(
            create_trace(
                "Analyzer",
                "analyzer_node",
                "FAILED",
                str(e)
            )
        )

    # Save checkpoint after each chunk
    save_checkpoint(state["run_id"], state)

    return state
