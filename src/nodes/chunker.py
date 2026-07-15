# src/nodes/chunker.py
import base64

from src.tools.chunking import create_chunks
from src.tools.vectorstore import index_chunks, index_image_descriptions
from src.tools.trace import create_trace
from src.library.llm import llm


def _describe_image(image_path: str) -> str:
    """
    Send an image to GPT-4o vision and return a detailed text description.
    Falls back to a placeholder if the file can't be read or vision fails.
    """
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        ext = image_path.rsplit(".", 1)[-1].lower()
        mime = f"image/{ext}" if ext in ("png", "jpg", "jpeg", "gif", "webp") else "image/png"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{image_data}"}
                    },
                    {
                        "type": "text",
                        "text": (
                            "You are analyzing an image extracted from a contract or policy document. "
                            "Describe what this image contains in detail. "
                            "If it is a table, chart, diagram, signature block, or stamp, say so explicitly "
                            "and extract any visible text or data from it."
                        )
                    }
                ]
            }
        ]

        response = llm.invoke_vision(messages)
        return response.content

    except Exception as e:
        return f"[Image description unavailable: {str(e)}]"


def chunker_node(state):
    # --------------------------------------------------
    # 1. Split text pages into overlapping chunks
    # --------------------------------------------------
    chunks = create_chunks(state["pages"])
    state["chunks"] = chunks
    state["current_chunk"] = 0

    # --------------------------------------------------
    # 2. Describe images — treat as first-class content
    # --------------------------------------------------
    image_descriptions = []
    chunk_id_offset = len(chunks) + 1

    for idx, image in enumerate(state.get("images", [])):
        description = _describe_image(image["image_path"])
        image_descriptions.append({
            "chunk_id": chunk_id_offset + idx,
            "page": image["page"],
            "image_path": image["image_path"],
            "description": description
        })

    state["image_descriptions"] = image_descriptions

    # --------------------------------------------------
    # 3. Index everything into ChromaDB for Q&A retrieval
    # --------------------------------------------------
    index_chunks(chunks, state["run_id"])

    if image_descriptions:
        index_image_descriptions(image_descriptions, state["run_id"])

    state["trace"].append(
        create_trace(
            "Chunker",
            "chunker_node",
            "SUCCESS",
            f"{len(chunks)} text chunks | {len(image_descriptions)} image descriptions indexed"
        )
    )

    return state
