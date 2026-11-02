# 🧠 Full‑Stack RAG System (FastAPI + ChromaDB + Ollama + Streamlit + Docker Compose + CI)

A complete Retrieval‑Augmented Generation (RAG) system built with:

- **FastAPI** (backend API)  
- **ChromaDB** (vector store)  
- **Ollama** (local LLM inference)  
- **Sentence‑Transformers** (embeddings)  
- **Streamlit** (frontend UI)  
- **Docker Compose** (multi‑service orchestration)  
- **GitHub Actions CI** (automated testing + Docker build verification)

The system is fully configurable via `.env`, uses persistent storage, and provides guardrailed, grounded answers with confidence scoring.

---

## 🚀 Features

### 🔧 Backend (FastAPI)
- **GET /** — Root endpoint (added for CI tests)  
- **POST /ask** — Ask a question, get grounded RAG answers  
- **POST /ingest** — Embed documents from `docs/`  
- **GET /stats** — Document count + model info  
- **GET /debug-retrieve** — Raw ChromaDB retrieval (for debugging)  
- **GET /health** — ChromaDB + Ollama + model status  

### 🎨 Frontend (Streamlit)
- Chat‑style interface for asking questions  
- Buttons for ingestion, stats, and health checks  
- Displays retrieved chunks, sources, and confidence  
- Clean UI for interacting with the backend  

### 🧱 Infrastructure
- Centralized configuration via `config.py`  
- `.env` file for environment variables  
- Docker Compose with persistent volumes  
- Single ChromaDB client + embedding function  
- Clean `/ask` endpoint using `rag_query()`  

### 🔁 Continuous Integration (GitHub Actions)
- Runs backend tests (`pytest`)  
- Builds backend + frontend Docker images  
- Verifies images were created  
- Ensures your RAG backend stays stable  

---

## 📁 Project Structure

```
rag-docker-demo/
├── docker-compose.yml
├── .env
├── .env.example
├── .dockerignore
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── my_rag.py
│   ├── config.py
│   ├── requirements.txt
│   ├── tests/
│   │   └── test_api.py
│   └── docs/
│       └── sample.txt
├── frontend/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── assets/
└── chroma_data/
```

---

## ⚙️ Configuration (Pydantic Settings)

All configuration lives in `backend/config.py`:

```python
class Settings(BaseSettings):
    OLLAMA_URL: str = Field("http://localhost:11434", env="OLLAMA_URL")
    MODEL_NAME: str = Field("llama3.2:1b", env="MODEL_NAME")
    CHROMA_PATH: str = Field("/app/chroma_data", env="CHROMA_PATH")
    MAX_RESULTS: int = Field(3, env="MAX_RESULTS")
    CONFIDENCE_THRESHOLD: float = Field(1.0, env="CONFIDENCE_THRESHOLD")
    DEBUG: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"
```

### `.env`

```
OLLAMA_URL=http://ollama:11434
MODEL_NAME=llama3.2:1b
CHROMA_PATH=/app/chroma_data
MAX_RESULTS=3
CONFIDENCE_THRESHOLD=1.0
DEBUG=false
```

---

## 🐳 Docker Compose (Backend + Frontend + Ollama)

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

  frontend:
    build: ./frontend
    container_name: rag_frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend

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

---

## 🧩 Streamlit Frontend

### Example `streamlit_app.py`

```python
import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.title("RAG Demo")

question = st.text_input("Ask a question:")

if st.button("Ask"):
    response = requests.post(
        f"{BACKEND_URL}/ask",
        json={"question": question}
    ).json()

    st.write("### Answer")
    st.write(response["answer"])

    st.write("### Confidence")
    st.write(response["confidence"])

    st.write("### Retrieved Chunks")
    for chunk in response["chunks_retrieved"]:
        st.write(f"**{chunk['source']}** (distance: {chunk['distance']:.2f})")
        st.write(chunk["text"])
        st.write("---")

if st.button("Re-index Documents"):
    st.write(requests.post(f"{BACKEND_URL}/ingest").json())

if st.button("Stats"):
    st.write(requests.get(f"{BACKEND_URL}/stats").json())

if st.button("Health Check"):
    st.write(requests.get(f"{BACKEND_URL}/health").json())
```

---

## 🔌 Backend Endpoints

### **GET /**  
Root endpoint added for CI:

```python
@app.get("/")
def root():
    return {"message": "RAG API running"}
```

### **POST /ask**  
Uses `rag_query()` internally.

### **POST /ingest**  
Embeds documents from `docs/`.

### **GET /stats**  
Shows document count + model name.

### **GET /debug-retrieve**  
Raw ChromaDB query results.

### **GET /health**  
Verifies:

- ChromaDB connection  
- Ollama availability  
- Model load status  

---

## 🧪 Backend Tests (Pytest)

Located at:

```
backend/tests/test_api.py
```

### Tests included:

#### ✔ Root endpoint

```python
def test_root():
    response = client.get("/")
    assert response.status_code == 200
```

#### ✔ Health endpoint

```python
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "chroma_db" in data
    assert "ollama" in data
    assert "model_loaded" in data
```

#### ✔ Stats endpoint

```python
def test_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "documents_indexed" in data
```

---

## 🔁 Continuous Integration (GitHub Actions)

Your CI workflow lives at:

```
.github/workflows/ci.yml
```

### CI Jobs

#### **1. test**
- Installs backend dependencies  
- Runs pytest  
- Validates API endpoints  

#### **2. docker**
- Builds backend Docker image  
- Builds frontend Docker image  
- Verifies images exist  

---

## 🧪 Local Testing (without Docker)

```
ollama serve
uvicorn main:app --reload
http://localhost:8000/docs
```

---

## 🐳 Running the Full Stack

### Start everything:

```
docker compose up --build
```

### Backend:

```
http://localhost:8000/docs
```

### Frontend:

```
http://localhost:8501
```

---

## 🎯 Purpose

This system is now:

- Fully configurable  
- Docker‑ready  
- Retrieval‑verified  
- Frontend‑integrated  
- CI‑validated  
- Guardrailed  
- Production‑aligned  
- Ready for deployment or grading  

