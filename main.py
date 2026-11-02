from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import requests
import json
import os
from my_rag import ingest, load_documents, rag_query
from config import settings
from chromadb.utils import embedding_functions

app = FastAPI(title="RAG API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Config ---
OLLAMA_URL = settings.OLLAMA_URL
MODEL = settings.MODEL_NAME
DB_PATH = settings.CHROMA_PATH

# --- ChromaDB setup ---
client = chromadb.PersistentClient(path=DB_PATH)

embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    "documents",
    embedding_function=embedder
)

# --- Schemas ---
class AskRequest(BaseModel):
    question: str
    n_results: int = 3
    max_distance: float = 999.0

class SourceChunk(BaseModel):
    text: str
    source: str
    distance: float

class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    confidence: str
    chunks_retrieved: list[SourceChunk]

# --- Ask Endpoint ---
@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    question = payload.question.strip()

    if question == "":
        raise HTTPException(status_code=422, detail="Question cannot be empty.")

    if collection.count() == 0:
        return AskResponse(
            answer="No documents ingested.",
            sources=[],
            confidence="low",
            chunks_retrieved=[]
        )

    # Use rag_query (your retrieval already works)
    result = rag_query(
        collection=collection,
        question=question,
        n_results=payload.n_results,
        stream=False,
        dt_threshold=payload.max_distance,
    )

    sources = [
        SourceChunk(
            text=c["text"],
            source=c["metadata"]["source"],
            distance=c["distance"],
        )
        for c in result["chunks_retrieved"]
    ]

    return AskResponse(
        answer=result["answer"],
        sources=sources,
        confidence=result["confidence"],
        chunks_retrieved=sources,
    )

# --- Ingest ---
@app.post("/ingest")
def ingest_documents():
    docs_dir = "/app/docs"

    if not os.path.exists(docs_dir):
        raise HTTPException(status_code=404, detail="docs/ directory not found")

    try:
        count = ingest(collection, docs_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    if count == 0:
        return {"message": "No documents found in docs/.", "chunks_ingested": 0}

    return {"message": "Ingestion complete.", "chunks_ingested": count}

# --- Stats ---
@app.get("/stats")
def get_stats():
    try:
        doc_count = collection.count()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read database: {str(e)}")

    return {
        "documents_indexed": doc_count,
        "model": MODEL,
        "database_path": DB_PATH
    }

# --- Debug Retrieval ---
@app.get("/debug-retrieve")
def debug_retrieve():
    try:
        results = collection.query(
            query_texts=["fastapi"],
            n_results=3
        )
        return results
    except Exception as e:
        return {"error": str(e)}

# --- Health ---
@app.get("/health")
def health_check():
    try:
        _ = collection.count()
        chroma_ok = True
    except Exception:
        chroma_ok = False

    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_ok = response.status_code == 200
    except Exception:
        ollama_ok = False

    model_available = False
    if ollama_ok:
        try:
            tags = response.json().get("models", [])
            model_available = any(m.get("name") == MODEL for m in tags)
        except Exception:
            model_available = False

    return {
        "chroma_db": "ok" if chroma_ok else "unavailable",
        "ollama": "ok" if ollama_ok else "unavailable",
        "model_loaded": "ok" if model_available else "missing",
        "model": MODEL,
        "database_path": DB_PATH
    }
