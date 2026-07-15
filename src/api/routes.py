import os
import json

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)
from fastapi.responses import StreamingResponse

from src.api.auth import verify_api_key
from src.graphs.agent import agent
from src.nodes.qa import qa_node
from src.library.checkpoint import load_checkpoint
from src.utils.helpers import generate_run_id
from src.utils.config import UPLOAD_DIR, REPORT_DIR, TRACE_DIR

router = APIRouter()


# ==========================================================
# Upload PDF
# ==========================================================
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    _: bool = Depends(verify_api_key)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    run_id = generate_run_id()

    pdf_path = os.path.join(UPLOAD_DIR, f"{run_id}.pdf")

    with open(pdf_path, "wb") as pdf:
        pdf.write(await file.read())

    # Initial LangGraph state
    state = {
        "run_id": run_id,
        "pdf_path": pdf_path,
        "pages": [],
        "images": [],
        "chunks": [],
        "image_descriptions": [],
        "current_chunk": 0,
        "partial_results": [],
        "failed_chunks": [],
        "final_report": {},
        "trace": [],
        "query": "",
        "answer": ""
    }

    def event_stream():

        yield f"data: Run ID : {run_id}\n\n"
        yield "data: Upload Successful\n\n"
        yield "data: Processing Started...\n\n"

        try:
            agent.invoke(state)

            yield "data: PDF Parsed\n\n"
            yield "data: Chunks Processed\n\n"
            yield "data: Report Generated\n\n"
            yield "data: Completed\n\n"

        except Exception as e:
            yield f"data: Error : {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ==========================================================
# Get Report
# ==========================================================
@router.get("/report/{run_id}")
def get_report(
    run_id: str,
    _: bool = Depends(verify_api_key)
):

    report_file = os.path.join(REPORT_DIR, f"{run_id}.json")

    if not os.path.exists(report_file):
        raise HTTPException(status_code=404, detail="Report not found.")

    with open(report_file, "r") as file:
        return json.load(file)


# ==========================================================
# Get Trace
# ==========================================================
@router.get("/trace/{run_id}")
def get_trace(
    run_id: str,
    _: bool = Depends(verify_api_key)
):

    trace_file = os.path.join(TRACE_DIR, f"{run_id}.json")

    if not os.path.exists(trace_file):
        raise HTTPException(status_code=404, detail="Trace not found.")

    with open(trace_file, "r") as file:
        return json.load(file)


# ==========================================================
# Query Document
# ==========================================================
@router.post("/query/{run_id}")
def query_document(
    run_id: str,
    query: str,
    _: bool = Depends(verify_api_key)
):
    # Load the existing checkpoint so the QA node has context
    state = load_checkpoint(run_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="No processed document found for this run_id. Upload and process a PDF first."
        )

    state["query"] = query
    state["answer"] = ""

    result = qa_node(state)

    return {
        "run_id": run_id,
        "question": query,
        "answer": result.get("answer", "")
    }
