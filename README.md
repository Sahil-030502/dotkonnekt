# Document Intelligence API

A production-ready backend for intelligent document analysis. Upload a contract or policy PDF and get back structured clause extraction, named entity recognition, risk scoring, revision suggestions, and natural language Q&A — all powered by a **LangGraph** agent pipeline with **GPT-4o**, **ChromaDB**, and an **MCP** risk analysis server.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [LangGraph Pipeline](#langgraph-pipeline)
- [MCP Risk Analysis Server](#mcp-risk-analysis-server)
- [API Reference](#api-reference)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Testing the API](#testing-the-api)
- [How Large Documents Are Handled](#how-large-documents-are-handled)
- [Fault Tolerance](#fault-tolerance)
- [Storage Layout](#storage-layout)

---

## Overview

When a user uploads a PDF, the system:

1. **Parses** the document using PyMuPDF — extracting raw text page-by-page and saving all embedded images to disk. No third-party document intelligence service is used.
2. **Chunks** the text into overlapping segments using a custom recursive splitter. Embedded images are described by GPT-4o vision and treated as first-class content alongside text.
3. **Indexes** all chunks (text + image descriptions) into ChromaDB for vector similarity search.
4. **Analyzes** each chunk independently through the LLM to extract clauses, obligations, named entities, and risk indicators.
5. **Validates** each analyzed chunk against a rule-based MCP server that checks for known risky terms, computes a per-chunk risk score, and suggests safer wording.
6. **Accumulates** partial results across all chunks — failed chunks are isolated and do not abort the run.
7. **Aggregates** all results and generates a structured risk report saved as JSON.
8. **Answers** natural language queries over the document by retrieving the most relevant chunks from ChromaDB and passing them as context to the LLM.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Server                           │
│  POST /upload   GET /report   GET /trace   POST /query          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LangGraph Agent                             │
│                                                                 │
│  START                                                          │
│    │                                                            │
│    ▼                                                            │
│  [parser] ──────── PyMuPDF: extract text + images              │
│    │                                                            │
│    ▼                                                            │
│  [chunker] ─────── split text, describe images (GPT-4o vision) │
│    │                index all content into ChromaDB             │
│    │                                                            │
│    ▼                                                            │
│  chunk_router ──── more chunks? ──► [analyzer]                 │
│    │                                    │                       │
│    │                                    ▼                       │
│    │                               [mcp_node] ── MCP Server    │
│    │                                    │       (stdio)         │
│    │                                    ▼                       │
│    │                              [next_chunk]                  │
│    │                                    │                       │
│    └──── done ◄────────────────────────┘                       │
│    │                                                            │
│    ▼                                                            │
│  [aggregator] ──── reconcile all partial results               │
│    │                                                            │
│    ▼                                                            │
│  [report] ──────── generate narrative + save JSON              │
│    │                                                            │
│   END                                                           │
└─────────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          │                                 │
          ▼                                 ▼
   ChromaDB (vector store)       File System (JSON reports,
   text + image embeddings        traces, checkpoints)
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent orchestration | **LangGraph** | Stateful graph with conditional routing and chunk loop |
| LLM | **OpenAI GPT-4o** (raw SDK) | Clause extraction, entity recognition, risk analysis, image description, Q&A |
| Embeddings | **OpenAI text-embedding-3-small** (raw SDK) | Embedding chunks for vector search |
| Vector store | **ChromaDB** (native client) | Storing and retrieving text + image chunks |
| PDF parsing | **PyMuPDF (fitz)** | Text extraction and image extraction — no third-party doc intelligence |
| Tool server | **MCP (FastMCP)** | Rule-based risk term detection, scoring, and revision suggestions |
| API | **FastAPI** | REST endpoints with SSE streaming for upload |
| Auth | Header-based API key | `x-api-key` header on all routes |

> No LangChain. The OpenAI SDK, ChromaDB, and MCP are used directly.

---

## Project Structure

```
document-intelligence/
│
├── src/
│   ├── api/
│   │   ├── app.py              # FastAPI application factory
│   │   ├── routes.py           # Upload, report, trace, query endpoints
│   │   └── auth.py             # x-api-key header verification
│   │
│   ├── graphs/
│   │   └── agent.py            # LangGraph graph: nodes, edges, routing, compile
│   │
│   ├── nodes/                  # One file per LangGraph node
│   │   ├── parser.py           # Extract text + images from PDF
│   │   ├── chunker.py          # Chunk text, describe images, index to ChromaDB
│   │   ├── analyzer.py         # LLM analysis per chunk (clauses, entities, risk)
│   │   ├── mcp.py              # MCP tool calls for risk validation
│   │   ├── aggregator.py       # Reconcile all partial results
│   │   ├── report.py           # Generate final report + save to disk
│   │   └── qa.py               # Retrieve + answer natural language queries
│   │
│   ├── tools/                  # Stateless utility functions
│   │   ├── pdf_parser.py       # PyMuPDF text extraction
│   │   ├── image_extractor.py  # PyMuPDF image extraction
│   │   ├── chunking.py         # Custom recursive text splitter (no LangChain)
│   │   ├── vectorstore.py      # ChromaDB native: index + similarity_search
│   │   ├── retriever.py        # Query wrapper with run_id scoping
│   │   ├── risk_scorer.py      # Compute overall risk score from partial results
│   │   └── trace.py            # Create structured trace event dicts
│   │
│   ├── mcp/                    # MCP risk analysis server
│   │   ├── server.py           # Entry point: runs FastMCP server
│   │   ├── tools.py            # 3 MCP tools: lookup_clause, calculate_risk_score, suggest_revision
│   │   └── client.py           # Async stdio client that calls the MCP server
│   │
│   ├── library/                # Shared singletons
│   │   ├── llm.py              # OpenAI chat completions wrapper (LLMResponse)
│   │   ├── embeddings.py       # OpenAI embeddings (embed_texts, embed_query)
│   │   ├── prompts.py          # All prompt templates
│   │   └── checkpoint.py       # Save/load JSON checkpoints per run_id
│   │
│   ├── utils/
│   │   ├── config.py           # All env var reads (single source of truth)
│   │   ├── constants.py        # CHUNK_SIZE, CHUNK_OVERLAP, supported extensions
│   │   ├── helpers.py          # generate_run_id()
│   │   └── logger.py           # Structured stdout logger
│   │
│   ├── storage/
│   │   ├── reports/            # {run_id}.json — final risk reports
│   │   ├── traces/             # {run_id}.json — full execution traces
│   │   └── checkpoints/        # {run_id}.json — per-chunk state snapshots
│   │
│   └── state.py                # AgentState TypedDict (shared graph state)
│
├── uploads/
│   ├── pdfs/                   # Uploaded PDF files
│   └── images/                 # Extracted images from PDFs
│
├── vector_store/               # ChromaDB persistent storage
├── .env                        # Environment variables (not committed)
├── requirements.txt
├── langgraph.json              # LangGraph server config
└── run.py                      # Uvicorn entry point
```

---

## LangGraph Pipeline

The core of the system is a `StateGraph` in `src/graphs/agent.py`. All nodes share a single `AgentState` TypedDict that gets passed and mutated through the graph.

### State schema (`src/state.py`)

```python
class AgentState(TypedDict):
    run_id: str                          # Unique ID for this run
    pdf_path: str                        # Path to the uploaded PDF
    pages: List[Dict]                    # Raw text per page
    images: List[Dict]                   # Extracted image metadata
    chunks: List[Dict]                   # Text chunks (chunk_id, page, text)
    image_descriptions: List[Dict]       # LLM descriptions of images
    current_chunk: int                   # Index pointer for the chunk loop
    partial_results: List[Dict]          # Per-chunk analysis + MCP results
    failed_chunks: List[Dict]            # Chunks that errored (non-fatal)
    final_report: Dict                   # Aggregated output
    trace: List[Dict]                    # Timestamped execution events
    query: str                           # Q&A input
    answer: str                          # Q&A output
```

### Node descriptions

| Node | What it does |
|------|-------------|
| `parser` | Opens the PDF with PyMuPDF. Extracts text page-by-page into `state["pages"]` and saves embedded images to `uploads/images/` into `state["images"]`. |
| `chunker` | Splits page text into overlapping chunks using a custom recursive splitter. Sends each image to GPT-4o vision to generate a text description. Indexes all content (text + image descriptions) into ChromaDB with `run_id` metadata. |
| `analyzer` | Takes `chunks[current_chunk]`, builds a combined prompt from `CLAUSE_PROMPT + ENTITY_PROMPT + RISK_PROMPT`, invokes the LLM, and appends the result to `partial_results`. On failure, appends to `failed_chunks` instead. Saves a checkpoint after every chunk. |
| `mcp` | Calls the MCP Risk Analysis Server with the latest chunk's analysis text. Gets back: matched risky terms, a numeric risk score (0–100), and suggested revisions. Merges results into `partial_results[-1]["baseline"]`. Non-fatal on MCP errors. |
| `next_chunk` | Increments `current_chunk` by 1. |
| `chunk_router` | Conditional edge: if `current_chunk < len(chunks)`, routes to `analyzer`; otherwise routes to `aggregator`. |
| `aggregator` | Collects all `partial_results` and `failed_chunks` into `final_report`. |
| `report` | Sends all partial results to the LLM to generate a narrative report. Computes overall risk score. Saves report JSON and trace JSON to disk. |

### Graph flow

```
START → parser → chunker → [chunk_router]
                                │
                    ┌───────────┴───────────┐
                 analyzer              aggregator
                    │                      │
                   mcp                  report
                    │                      │
               next_chunk               END
                    │
              [chunk_router] (loop back)
```

---

## MCP Risk Analysis Server

The MCP server (`src/mcp/`) runs as a separate subprocess and exposes three tools over stdio:

### Tool 1 — `lookup_clause`
Checks a clause for known risky terms from a built-in list:
```
"unlimited liability", "automatic renewal", "exclusive jurisdiction",
"no termination", "sole discretion", "without notice",
"non-refundable", "perpetual license"
```
Returns: `{ "matched_terms": [...], "risk": "HIGH" | "LOW" }`

### Tool 2 — `calculate_risk_score`
Takes the list of matched terms and returns a numeric score:
```
0 terms  → 10
1–2      → 40
3–4      → 70
5+       → 95
```
Returns: `{ "risk_score": 40 }`

### Tool 3 — `suggest_revision`
For each matched risky term, returns a specific safer alternative.
Returns: `{ "recommendations": ["Replace 'unlimited liability' with...", ...] }`

The `MCPClient` in `src/mcp/client.py` connects over stdio, initializes a session, calls tools, and parses the `TextContent` response back to a plain Python dict.

---

## API Reference

All endpoints require the header:
```
x-api-key: <your API_KEY from .env>
```

### `POST /upload`

Upload a PDF for processing. Returns a Server-Sent Events (SSE) stream with progress updates.

**Request:** `multipart/form-data`
- `file` — PDF file

**SSE Response stream:**
```
data: Run ID : <uuid>
data: Upload Successful
data: Processing Started...
data: PDF Parsed
data: Chunks Processed
data: Report Generated
data: Completed
```

**Save the `run_id`** from the first event — you need it for all subsequent calls.

---

### `GET /report/{run_id}`

Retrieve the final structured risk report.

**Response:**
```json
{
  "run_id": "3f2a...",
  "risk_score": 62.5,
  "successful_chunks": 14,
  "failed_chunks": 1,
  "report": "## Executive Summary\n\nThis agreement contains..."
}
```

---

### `GET /trace/{run_id}`

Retrieve the full execution trace — every node event with timestamp, status, and message.

**Response:**
```json
[
  {
    "timestamp": "2026-07-15T10:23:01.123456",
    "event": "Parser",
    "node": "parser_node",
    "status": "SUCCESS",
    "message": "12 pages | 3 images extracted"
  },
  ...
]
```

---

### `POST /query/{run_id}?query=<question>`

Ask a natural language question about the document. Retrieves the most relevant chunks from ChromaDB (scoped to this `run_id`) and answers with the LLM.

**Query parameter:** `query` — your question string

**Response:**
```json
{
  "run_id": "3f2a...",
  "question": "What are the termination conditions?",
  "answer": "According to [Chunk 7], either party may terminate the agreement with 30 days written notice..."
}
```

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- An OpenAI API key with access to `gpt-4o` and `text-embedding-3-small`

### Steps
** Use your own API Key
**1. Clone or navigate to the project**
```cmd
cd document-intelligence
```

**2. Create a virtual environment**
```cmd
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```cmd
pip install -r requirements.txt
```

**4. Configure environment variables**
```cmd
copy .env .env.backup
```
Then edit `.env` — see [Configuration](#configuration).

---

## Configuration

All settings live in `.env`. The `src/utils/config.py` file reads them at startup.

```env
# ==========================
# OpenAI Configuration
# ==========================
OPENAI_API_KEY=sk-proj-...        # Your OpenAI API key (required)
MODEL_NAME=gpt-4o                 # Chat model (gpt-4o supports vision)
EMBEDDING_MODEL=text-embedding-3-small

# ==========================
# FastAPI Authentication
# ==========================
API_KEY=123456                    # Header key for all API requests (change in production)

# ==========================
# Storage Paths
# ==========================
UPLOAD_DIR=uploads/pdfs           # Where uploaded PDFs are saved
IMAGE_DIR=uploads/images          # Where extracted images are saved
VECTOR_STORE_DIR=vector_store     # ChromaDB persistence directory
REPORT_DIR=src/storage/reports    # Where report JSONs are saved
TRACE_DIR=src/storage/traces      # Where trace JSONs are saved
CHECKPOINT_DIR=src/storage/checkpoints

# ==========================
# Chunking Settings
# ==========================
CHUNK_SIZE=1000                   # Max characters per chunk
CHUNK_OVERLAP=200                 # Overlap between consecutive chunks
TOP_K_RESULTS=5                   # Number of chunks retrieved for Q&A
```

---

## Running the Server

```cmd
python -m uvicorn src.api.app:app --reload --port 8000
```

The server starts at `http://localhost:8000`.

**Interactive API docs (Swagger UI):** `http://localhost:8000/docs`

**OpenAPI schema:** `http://localhost:8000/openapi.json`

---

## Testing the API

### Using Swagger UI

1. Open `http://localhost:8000/docs`
2. Click any endpoint → **Try it out**
3. Enter `123456` in the `x-api-key` field
4. For `/upload`, choose a PDF file and click **Execute**
5. Copy the `Run ID` from the SSE response
6. Use that `run_id` to call `/report`, `/trace`, or `/query`

### Using curl (Windows CMD)

**Upload a PDF:**
```cmd
curl -X POST http://localhost:8000/upload ^
  -H "x-api-key: 123456" ^
  -F "file=@contract.pdf"
```

**Get the report:**
```cmd
curl http://localhost:8000/report/<run_id> ^
  -H "x-api-key: 123456"
```

**Get the trace:**
```cmd
curl http://localhost:8000/trace/<run_id> ^
  -H "x-api-key: 123456"
```

**Ask a question:**
```cmd
curl -X POST "http://localhost:8000/query/<run_id>?query=What+are+the+payment+terms?" ^
  -H "x-api-key: 123456"
```

---

## How Large Documents Are Handled

Documents that exceed the LLM's context window are handled through the chunk loop in the LangGraph graph:

- The document is split into chunks of `CHUNK_SIZE` characters (default 1000) with `CHUNK_OVERLAP` overlap (default 200).
- The graph processes **one chunk at a time** via the `analyzer → mcp → next_chunk → chunk_router` loop.
- Each chunk's results are appended to `partial_results` in the shared state.
- After all chunks are processed, the `aggregator` reconciles them and the `report` node sends only the aggregated summaries to the LLM — not the full document — keeping the final report generation well within context limits.
- A checkpoint is saved to disk after each chunk, so progress is preserved even if the process is interrupted.

---

## Fault Tolerance

The system is designed so that individual chunk failures never abort the entire run:

- In `analyzer_node`, the LLM call is wrapped in `try/except`. On failure, the chunk is added to `failed_chunks` with the error message and processing continues.
- In `mcp_node`, MCP server errors are caught and recorded in the trace. The chunk's `baseline` is set to an empty dict and the loop continues.
- The `report_node` always runs regardless of how many chunks failed, and the report includes a `failed_chunks` count.
- The Q&A route loads from checkpoint rather than re-running the pipeline, so a crashed upload doesn't prevent querying already-processed content.

---

## Storage Layout

After processing a document with `run_id = abc123`:

```
src/storage/
├── reports/
│   └── abc123.json          # Final risk report
├── traces/
│   └── abc123.json          # Full execution trace
└── checkpoints/
    └── abc123.json          # Last saved agent state

uploads/
├── pdfs/
│   └── abc123.pdf           # Original uploaded file
└── images/
    ├── page_1_0.png         # Images extracted from the PDF
    └── page_3_1.jpeg

vector_store/                # ChromaDB persistent data
```