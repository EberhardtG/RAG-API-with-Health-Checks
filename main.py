from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import requests
import json
import os
from my_rag import ingest, load_documents, rag_query
from config import settings



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
collection = client.get_or_create_collection("documents")

# --- Schemas ---
class AskRequest(BaseModel):
    question: str
    n_results: int = 3
    max_distance: float = 1.2

class SourceChunk(BaseModel):
    text: str
    source: str
    distance: float

class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    confidence: str
    chunks_retrieved: list[SourceChunk]


#---endpoints---
@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    question = payload.question.strip()

    # --- Validation ---
    if question == "":
        raise HTTPException(status_code=422, detail="Question cannot be empty.")

    # --- Check if documents exist ---
    if collection.count() == 0:
        return AskResponse(
            answer="No documents ingested.",
            sources=[],
            confidence="low",
            chunks_retrieved=[]
        )

    # --- Retrieval ---
    results = collection.query(
        query_texts=[question],
        n_results=min(payload.n_results, collection.count())
    )

    # Build chunk list
    retrieved_chunks = []
    for i in range(len(results["documents"][0])):
        retrieved_chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i],
            "metadata": results["metadatas"][0][i]
        })

    # Sort by distance
    retrieved_chunks.sort(key=lambda c: c["distance"])

    # --- Distance threshold filtering ---
    filtered = [
        c for c in retrieved_chunks
        if c["distance"] <= payload.max_distance
    ]

    # --- No relevant chunks ---
    if len(filtered) == 0:
        return AskResponse(
            answer="I don’t know.",
            sources=[],
            confidence="low",
            chunks_retrieved=[]
        )

    # --- Build system prompt ---
    context_blocks = []
    for c in filtered:
        context_blocks.append(
            f"[Source: {c['source']}, Chunk {c['metadata']['chunk_index']}]\n{c['text']}"
        )

    context_text = "\n\n---\n\n".join(context_blocks)

    system_prompt = f"""
You are a guardrailed retrieval‑augmented assistant. Follow these rules exactly:

1. Use ONLY the retrieved context provided to you. Never rely on outside knowledge.
2. If the answer is not fully supported by the context, say “I don’t know.”
3. Never make up information, details, explanations, or assumptions.
4. Cite your sources by listing the filename and chunk index for every fact you use.
5. Do NOT invent citations. Only cite chunks that were actually retrieved.
6. Keep your answer concise, factual, and grounded.
7. Your answer will be placed into a structured response dictionary. Do NOT include extra commentary.
8. After your answer, include a “Sources:” section listing the chunks you used.
9. If no chunks are relevant, respond only with: “I don’t know.” and an empty Sources list.

CONTEXT:
{context_text}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    # --- Call Ollama ---
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={"model": MODEL, "messages": messages},
            timeout=30
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama is not running.")

    if response.status_code != 200:
        raise HTTPException(status_code=503, detail="Ollama returned an error.")

    try:
        answer = response.json()["message"]["content"]
    except:
        answer = "I don’t know."

    # --- Confidence scoring ---
    best_dist = filtered[0]["distance"]
    if best_dist < 0.5:
        confidence = "high"
    elif best_dist < 1.0:
        confidence = "medium"
    else:
        confidence = "low"

    # --- Build response ---
    sources = [
        SourceChunk(
            text=c["text"],
            source=c["source"],
            distance=c["distance"]
        )
        for c in filtered
    ]

    chunks_retrieved = sources  # same structure

    return AskResponse(
        answer=answer,
        sources=sources,
        confidence=confidence,
        chunks_retrieved=chunks_retrieved
    )

@app.post("/ingest")
def ingest_documents():
    docs_dir = "docs"

    # Check directory exists
    if not os.path.exists(docs_dir):
        raise HTTPException(status_code=404, detail="docs/ directory not found")

    # Load and ingest documents
    try:
        count = ingest(collection, docs_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

    if count == 0:
        return {"message": "No documents found in docs/.", "chunks_ingested": 0}

    return {"message": "Ingestion complete.", "chunks_ingested": count}

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

@app.get("/health")
def health_check():
    # --- Check ChromaDB ---
    try:
        _ = collection.count()   # simple read test
        chroma_ok = True
    except Exception as e:
        chroma_ok = False

    # --- Check Ollama ---
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_ok = response.status_code == 200
    except Exception:
        ollama_ok = False

    # --- Check model availability ---
    model_available = False
    if ollama_ok:
        try:
            tags = response.json().get("models", [])
            model_available = any(m.get("name") == MODEL for m in tags)
        except Exception:
            model_available = False

    # --- Build health report ---
    return {
        "chroma_db": "ok" if chroma_ok else "unavailable",
        "ollama": "ok" if ollama_ok else "unavailable",
        "model_loaded": "ok" if model_available else "missing",
        "model": MODEL,
        "database_path": DB_PATH
    }
