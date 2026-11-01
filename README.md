# 🧠 RAG API with Health Checks  
A FastAPI backend providing a guardrailed Retrieval‑Augmented Generation (RAG) service powered by ChromaDB and Ollama. This API supports ingestion, querying, system health checks, and statistics — forming the backend foundation for your module project.

---

## 🚀 Overview

This API exposes your guardrailed RAG pipeline through four endpoints:

- **POST /ask** — Ask a question and receive a grounded answer with sources and confidence  
- **POST /ingest** — Load documents from the `docs/` directory into ChromaDB  
- **GET /stats** — View document count and model information  
- **GET /health** — Check ChromaDB and Ollama availability  

It includes:

- Pydantic request/response schemas  
- CORS middleware for frontend connectivity  
- Error handling for missing documents, invalid questions, and Ollama downtime  
- Structured responses compatible with your guardrailed RAG pipeline  

---

## 📁 Project Structure

```
my_rag.py          # RAG pipeline (ingest, retrieve, prompt, generate)
main.py            # FastAPI backend
docs/              # Folder containing .txt/.md documents
rag_db/            # Persistent ChromaDB storage
Dockerfile         # Container build instructions
.dockerignore      # Files excluded from Docker build context
requirements.txt   # Python dependencies
```

---

## ⚙️ Configuration

The API uses:

- **Ollama** for LLM inference  
- **ChromaDB** for vector storage  
- **llama3.2:1b** as the default model  
- **rag_db/** as the persistent database directory  

You can adjust these in the config section of `main.py`:

```python
OLLAMA_URL = "http://host.docker.internal:11434"
MODEL = "llama3.2:1b"
DB_PATH = "./rag_db"
```

---

## 🐳 Docker Setup

### **Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir numpy==1.26.4

COPY main.py .
COPY my_rag.py .
COPY docs/ docs/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **.dockerignore**

```
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv
rag_db/
```

---

## 🔌 Endpoints

### **POST /ask**  
Ask a question and receive a grounded answer.

**Request Body:**
```json
{
  "question": "What does it mean for an API to be stateless?",
  "n_results": 3,
  "max_distance": 1.2
}
```

**Response:**
```json
{
  "answer": "...",
  "sources": [...],
  "confidence": "high",
  "chunks_retrieved": [...]
}
```

Includes:

- Distance threshold filtering  
- Guardrailed system prompt  
- Confidence scoring  
- Structured response  

---

### **POST /ingest**  
Load and embed documents from the `docs/` directory.

**Response:**
```json
{
  "message": "Ingestion complete.",
  "chunks_ingested": 42
}
```

Handles:

- Missing directory  
- Empty folder  
- Ingestion errors  

---

### **GET /stats**  
Returns basic system statistics.

**Response:**
```json
{
  "documents_indexed": 42,
  "model": "llama3.2:1b",
  "database_path": "./rag_db"
}
```

---

### **GET /health**  
Checks ChromaDB, Ollama, and model availability.

**Response:**
```json
{
  "chroma_db": "ok",
  "ollama": "ok",
  "model_loaded": "ok",
  "model": "llama3.2:1b",
  "database_path": "./rag_db"
}
```

---

## 🛡️ Guardrails Included

Your API uses the same guardrails as your RAG pipeline:

- **Distance threshold filtering**  
- **Confidence scoring**  
- **Strengthened system prompt**  
- **Structured response dictionary**  
- **“I don’t know” fallback**  
- **No hallucinated citations**  

These ensure safe, grounded, predictable outputs.

---

## 🧪 Testing

Start Ollama:

```
ollama serve
```

Run the API locally:

```
uvicorn main:app --reload
```

Open Swagger UI:

```
http://localhost:8000/docs
```

Test:

- `/ingest` first  
- `/ask` next  
- `/stats` and `/health` anytime  

---

## 🐳 Running with Docker

Build the container:

```
docker build --no-cache -t rag-api .
```

Run it:

```
docker run -p 8000:8000 rag-api
```

Swagger UI:

```
http://localhost:8000/docs
```

---

## 🎯 Purpose

This API is the backend foundation for your module project. Completing it now ensures Week 2 focuses on Dockerization and deployment rather than debugging.

