import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/pdfs")
IMAGE_DIR = os.getenv("IMAGE_DIR", "uploads/images")
VECTOR_DB_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")
REPORT_DIR = os.getenv("REPORT_DIR", "src/storage/reports")
TRACE_DIR = os.getenv("TRACE_DIR", "src/storage/traces")
CHECKPOINT_DIR = os.getenv("CHECKPOINT_DIR", "src/storage/checkpoints")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))
