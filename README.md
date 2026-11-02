# 🧠 RAG API with Health Checks (Configurable + Docker Compose Edition)

A multi‑service Retrieval‑Augmented Generation (RAG) backend using **FastAPI**, **ChromaDB**, and **Ollama**, now fully refactored to use **environment‑driven configuration** via a centralized `Settings` class and `.env` management. The stack runs under **Docker Compose** with persistent volumes and service‑to‑service networking.

---

## 🚀 Overview

This backend exposes a guardrailed RAG pipeline with:

- **POST /ask** — Ask a question and receive grounded answers  
- **POST /ingest** — Embed documents from `docs/` into ChromaDB  
- **GET /stats** — View document count and model info  
- **GET /health** — Check ChromaDB + Ollama connectivity  

New improvements:

- Centralized configuration via `config.py`  
- `.env` file for environment variables  
- Docker Compose `env_file: .env` integration  
- Pydantic v2 + pydantic‑settings  
- Persistent ChromaDB volume (`/app/chroma_data`)  
- No hardcoded paths or model names  

---

## 📁 Project Structure

```
rag-docker-demo/
├── docker-compose.yml        # Multi-service orchestration
├── .env                      # Environment variables (used by Docker Compose)
├── .env.example              # Safe example for documentation
├── .dockerignore             # Ignore unnecessary files during build
├── backend/
│   ├── Dockerfile            # Backend container build instructions
│   ├── main.py               # FastAPI backend
│   ├── my_rag.py             # RAG pipeline (ingest, retrieve, generate)
│   ├── config.py             # Centralized Settings class (Pydantic v2)
│   ├── requirements.txt      # Python dependencies
│   └── docs/                 # Folder containing .txt/.md documents
│       └── sample.txt
└── chroma_data/              # Persistent ChromaDB storage (created automatically)
```

---

## ⚙️ Configuration (NEW)

All configuration is now centralized in `backend/config.py` using **pydantic‑settings**:

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    OLLAMA_URL: str = Field("http://localhost:11434", env="OLLAMA_URL")
    MODEL_NAME: str = Field("llama3.2:1b", env="MODEL_NAME")
    CHROMA_PATH: str = Field("/app/chroma_data", env="CHROMA_PATH")
    MAX_RESULTS: int = Field(3, env="MAX_RESULTS")
    CONFIDENCE_THRESHOLD: float = Field(1.0, env="CONFIDENCE_THRESHOLD")
    DEBUG: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### `.env` (used by Docker Compose)

```
OLLAMA_URL=http://ollama:11434
MODEL_NAME=llama3.2:1b
CHROMA_PATH=/app/chroma_data
MAX_RESULTS=3
CONFIDENCE_THRESHOLD=1.0
DEBUG=false
```

### `.env.example` (safe for documentation)

```
OLLAMA_URL=http://ollama:11434
MODEL_NAME=llama3.2:1b
CHROMA_PATH=/app/chroma_data
MAX_RESULTS=3
CONFIDENCE_THRESHOLD=1.0
DEBUG=false
```

### Updated `main.py`

All hardcoded values were removed:

```python
from config import settings

OLLAMA_URL = settings.OLLAMA_URL
MODEL = settings.MODEL_NAME
DB_PATH = settings.CHROMA_PATH
```

### Updated `my_rag.py`

Your RAG pipeline now uses:

```python
settings.MAX_RESULTS
settings.CONFIDENCE_THRESHOLD
```

---

## 🐳 Docker Setup (UPDATED)

### docker-compose.yml

Now uses `env_file: .env`:

```yaml
services:
  backend:
    build: ./backend
    container_name: rag_backend
    ports:
      - "8000:8000"
    env_file: .env
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

### Backend Dockerfile (UPDATED)

Includes `config.py` and updated requirements:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY my_rag.py .
COPY config.py .
COPY docs/ docs/
```

### requirements.txt (UPDATED)

```
fastapi==0.109.0
uvicorn==0.27.0
chromadb==0.4.24
sentence-transformers==2.3.1
requests==2.31.0
pydantic>=2.7.0
pydantic-settings==2.6.1
numpy==1.26.4
```

---

## 🔌 Endpoints

### **POST /ask**
Grounded answer with confidence scoring.

### **POST /ingest**
Embeds documents from `docs/`.

### **GET /stats**
Shows document count + model name.

### **GET /health**
Verifies:

- ChromaDB connection  
- Ollama availability  
- Model load status  

---

## 🛡️ Guardrails Included

- Distance threshold filtering  
- Confidence scoring  
- Strict grounding rules  
- “I don’t know” fallback  
- No hallucinated citations  

---

## 🧪 Local Testing (without Docker)

```
ollama serve
uvicorn main:app --reload
http://localhost:8000/docs
```

---

## 🐳 Running with Docker Compose

### Build + start:

```
docker compose up --build
```

### Stop:

```
docker compose down
```

### Restart (persistent data):

```
docker compose up
```

### Verify:

```
http://localhost:8000/health
```

You should see:

```
"ollama": "connected"
```

---

## 🎯 Purpose

This backend is now:

- Fully configurable  
- Docker‑ready  
- Production‑aligned  
- Persistent  
- Guardrailed  
- Ready for the **Streamlit frontend**   

