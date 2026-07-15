from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):

    run_id: str

    pdf_path: str

    # Raw page text extracted from the PDF
    pages: List[Dict[str, Any]]

    # Raw image metadata extracted from the PDF
    images: List[Dict[str, Any]]

    # Text chunks (page-level splits)
    chunks: List[Dict[str, Any]]

    # LLM-generated descriptions for each extracted image
    # (images treated as first-class content alongside text)
    image_descriptions: List[Dict[str, Any]]

    # Pointer to the chunk currently being analyzed
    current_chunk: int

    # Per-chunk analysis results (accumulated across the loop)
    partial_results: List[Dict[str, Any]]

    # Chunks that failed analysis (isolated, don't abort the run)
    failed_chunks: List[Dict[str, Any]]

    # Final reconciled report
    final_report: Dict[str, Any]

    # Execution trace events
    trace: List[Dict[str, Any]]

    # Q&A fields
    query: str
    answer: str
