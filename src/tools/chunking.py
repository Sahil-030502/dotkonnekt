# src/tools/chunking.py
# Custom recursive text splitter — no LangChain
from src.utils.config import CHUNK_SIZE, CHUNK_OVERLAP


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """
    Recursively split text on paragraph breaks, then sentences, then words,
    then characters — same strategy as LangChain's RecursiveCharacterTextSplitter.
    """
    separators = ["\n\n", "\n", ". ", " ", ""]

    def _split(text: str, separators: list[str]) -> list[str]:
        if not text:
            return []

        separator = separators[0]
        remaining = separators[1:]

        if separator == "":
            # Character-level split as last resort
            splits = list(text)
        else:
            splits = text.split(separator)

        chunks = []
        current = ""

        for split in splits:
            piece = (current + separator + split).lstrip(separator) if current else split

            if len(piece) <= chunk_size:
                current = piece
            else:
                if current:
                    chunks.append(current)
                # If the split itself is too large, recurse with finer separators
                if len(split) > chunk_size and remaining:
                    chunks.extend(_split(split, remaining))
                else:
                    current = split

        if current:
            chunks.append(current)

        return chunks

    raw_chunks = _split(text, separators)

    # Apply overlap: each chunk starts chunk_overlap chars before the previous ended
    if chunk_overlap == 0 or len(raw_chunks) <= 1:
        return [c for c in raw_chunks if c.strip()]

    merged: list[str] = []
    for i, chunk in enumerate(raw_chunks):
        if i == 0:
            merged.append(chunk)
        else:
            # Prepend tail of previous chunk for context overlap
            prev = merged[-1]
            overlap_text = prev[-chunk_overlap:] if len(prev) > chunk_overlap else prev
            merged.append(overlap_text + " " + chunk)

    return [c.strip() for c in merged if c.strip()]


def create_chunks(pages: list) -> list:
    """
    Split page text into overlapping chunks while preserving page metadata.
    Returns a flat list of chunk dicts with chunk_id, page, and text.
    """
    chunks = []
    chunk_id = 1

    for page in pages:
        texts = _split_text(page["text"], CHUNK_SIZE, CHUNK_OVERLAP)
        for text in texts:
            chunks.append({
                "chunk_id": chunk_id,
                "page": page["page"],
                "text": text
            })
            chunk_id += 1

    return chunks
