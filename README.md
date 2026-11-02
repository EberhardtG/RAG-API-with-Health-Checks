# 🧠 RAG API with Health Checks (Docker Compose Edition)  
A multi‑service Retrieval‑Augmented Generation (RAG) stack using **FastAPI**, **ChromaDB**, and **Ollama**, orchestrated with **Docker Compose**. This backend supports ingestion, querying, system health checks, and persistent vector storage.

---

## 🚀 Overview

This stack runs two connected services:

### **1. FastAPI Backend (your RAG API)**
- Ingest documents  
- Query ChromaDB  
- Stream or return grounded answers  
- Provide health checks and stats  
- Communicate with Ollama via internal Docker networking  

### **2. Ollama Service**
- Hosts your LLM (e.g., `llama3.2:1b`)  
- Provides `/api/chat` and `/api/tags` endpoints  
- Stores models persistently in a named volume  

---

## 📁 Project Structure

```
rag-docker-demo/
├── docker-compose.yml        # Multi-service orchestration
├── .dockerignore             # Ignore unnecessary files during build
├── backend/
│   ├── Dockerfile            # Backend container build instructions
│   ├── main.py               # FastAPI backend
│   ├── my_rag.py             # RAG pipeline (ingest, retrieve, prompt, generate)
│   ├── requirements.txt      # Python dependencies
│   └── docs/                 # Folder containing .txt/.md documents
│       └── sample.txt
└── chroma_data/              # Persistent ChromaDB storage (created automatically)
```

---

## ⚙️ Configuration

The backend reads configuration from environment variables set in `docker-compose.yml`:

```yaml
environment:
  - OLLAMA_URL=http://ollama:11434
  - MODEL_NAME=llama3.2:1b
```

Inside `main.py`, these are accessed via:

```python
OLLAMA_URL = os.environ.get("OLLAMA_URL")
MODEL = os.environ.get("MODEL_NAME")
DB_PATH = "/app/chroma_data"   # Matches docker-compose volume
```

---

## 🐳 Docker Setup

### **docker-compose.yml**

This file defines both services and persistent volumes:

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    container_name: rag_backend
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_URL=http://ollama:11434
      - MODEL_NAME=llama3.2:1b
    depends_on:
      - ollama
    volumes:
      - chroma_data:/app/chroma_data

  ollama:
    image: ollama/ollama
    container_name: rag_ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  chroma_data:
  ollama_data:
```

### **Backend Dockerfile**

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
chroma_data/
```

---

## 🔌 Endpoints

### **POST /ask**
Ask a question and receive a grounded answer.

### **POST /ingest**
Load and embed documents from the `docs/` directory.

### **GET /stats**
Returns document count and model info.

### **GET /health**
Checks:
- ChromaDB availability  
- Ollama connectivity  
- Model availability  

---

## 🛡️ Guardrails Included

Your RAG pipeline enforces:

- Distance threshold filtering  
- Confidence scoring  
- Strict grounding rules  
- “I don’t know” fallback  
- No hallucinated citations  

---

## 🧪 Local Testing (without Docker)

Start Ollama:

```
ollama serve
```

Run FastAPI:

```
uvicorn main:app --reload
```

Open Swagger:

```
http://localhost:8000/docs
```

---

## 🐳 Running with Docker Compose

### Build and start everything:

```
docker-compose up --build
```

### Stop:

```
docker-compose down
```

### Restart (data persists):

```
docker-compose up
```

### Verify health:

```
http://localhost:8000/health
```

You should see:

```
"ollama": "connected"
```

---

## 🎯 Purpose

This multi‑service RAG stack is the foundation for your module project.  
Once this backend + Ollama setup is running, you will later add a **Streamlit frontend** to complete the full stack.

