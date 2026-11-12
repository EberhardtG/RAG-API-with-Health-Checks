# 🧠 Full-Stack RAG System (FastAPI + ChromaDB + Ollama + Streamlit + Docker Compose + CI)

A complete Retrieval-Augmented Generation (RAG) system built with:

- **FastAPI** (backend API)
- **ChromaDB** (vector database)
- **Ollama** (local LLM inference)
- **Sentence Transformers** (embeddings)
- **Streamlit** (frontend interface)
- **Docker Compose** (multi-container orchestration)
- **GitHub Actions** (CI/CD)

The system ingests local documents, stores embeddings in ChromaDB, retrieves relevant context, and generates grounded responses using Ollama.

---

# 🚀 Features

## Backend (FastAPI)

- GET `/`
- POST `/ask`
- POST `/ingest`
- GET `/stats`
- GET `/debug-retrieve`
- GET `/health`

### RAG Features

- Document ingestion from a local document collection
- Paragraph-based chunking
- ChromaDB vector storage
- Retrieval of top 3 most relevant chunks
- Ollama-powered answer generation
- Source citation instructions
- Confidence scoring
- Interactive CLI mode
- Graceful Ollama connection handling

## Frontend (Streamlit)

- Chat-style question interface
- Health status checks
- Document ingestion controls
- Statistics view
- Retrieved chunk display
- Confidence display

## Infrastructure

- Dockerized backend
- Dockerized frontend
- Ollama container
- Persistent ChromaDB storage
- Environment-based configuration
- Automated CI workflow

---

# 📁 Project Structure

```text
rag-docker-demo/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .dockerignore
│
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── my_rag.py
│   ├── config.py
│   ├── requirements.txt
│   ├── docs/
│   │   ├── api_basics.txt
│   │   ├── fastapi_intro.txt
│   │   ├── embeddings_overview.txt
│   │   ├── llm_behavior.txt
│   │   ├── python_functions.txt
│   │   └── sql_databases.txt
│   └── tests/
│       └── test_api.py
│
├── frontend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

# 📚 Document Collection

The RAG pipeline uses a document collection located in:

```text
backend/docs/
```

The collection contains six text documents covering:

- FastAPI
- API Concepts
- ChromaDB
- Ollama
- RAG Architecture
- Prompt Engineering

These documents are loaded, chunked, embedded, and stored in ChromaDB during ingestion.

---

# ⚙️ Configuration

Configuration is managed with Pydantic Settings.

Example `.env.example`:

```env
OLLAMA_URL=http://ollama:11434
MODEL_NAME=llama3.2:1b
CHROMA_PATH=/app/chroma_data
MAX_RESULTS=3
CONFIDENCE_THRESHOLD=1.0
DEBUG=false
```

## Environment Security

The project includes:

```text
.gitignore
```

which excludes:

```text
.env
.venv/
__pycache__/
chroma_data/
```

to prevent accidental commits of local configuration and generated data.

---

# 🔍 RAG Pipeline

## Step 1: Ingestion

Documents are read from:

```text
backend/docs/
```

and split into paragraph chunks.

Each chunk receives:

- unique ID
- source filename
- chunk index metadata

The chunks are stored in ChromaDB.

---

## Step 2: Retrieval

When a user asks a question:

1. ChromaDB performs vector similarity search.
2. The top three chunks are retrieved.
3. Retrieved chunks are displayed before generation.

Example:

```text
Retrieved 1 chunks:
[1] fastapi_intro.txt
```

---

## Step 3: Generation

Retrieved context is inserted into a guardrailed system prompt and sent to Ollama.

The model is instructed to:

- use retrieved context only
- avoid hallucinations
- cite document sources
- respond with "I don't know" when context is insufficient

---

## Step 4: Confidence Scoring

Confidence is based on retrieval distance:

| Distance | Confidence |
|-----------|------------|
| < 0.5 | High |
| < 1.0 | Medium |
| >= 1.0 | Low |

---

# 🧪 Interactive CLI

The assignment required an interactive query loop.

Example:

```text
Ask a question (or type 'quit'):
```

The application continues running until:

```text
quit
```

is entered.

---

# 🧪 Required Test Queries

The system was tested with the three required query types.

## Query 1: Answerable Question

Question:

```text
What is FastAPI?
```

Retrieved:

```text
fastapi_intro.txt
```

Result:

```text
I don't know.
```

The system successfully retrieved the relevant source document and supplied it to the model.

---

## Query 2: Related Question

Question:

```text
Why is FastAPI useful for building AI applications?
```

Retrieved:

```text
fastapi_intro.txt
```

Result:

```text
I don't know.
```

This demonstrates retrieval of related context from the document collection.

---

## Query 3: Outside Scope

Question:

```text
Who won the Super Bowl?
```

Retrieved:

```text
0 chunks
```

Result:

```text
I don't know.
```

This verifies proper handling of out-of-scope questions.

---

# 🔌 API Endpoints

| Endpoint | Method | Description |
|-----------|----------|-------------|
| `/` | GET | Root endpoint |
| `/ask` | POST | Submit a question |
| `/ingest` | POST | Load and embed documents |
| `/stats` | GET | Database statistics |
| `/debug-retrieve` | GET | Retrieval debugging |
| `/health` | GET | Service health checks |

---

# 🐳 Docker Architecture

The application consists of three services:

## Backend

FastAPI + ChromaDB

Port:

```text
8000
```

## Frontend

Streamlit

Port:

```text
8501
```

## Ollama

LLM Inference

Port:

```text
11434
```

---

# 🐳 Docker Verification

Backend Dockerfile:

- Uses Python 3.11 Slim
- Installs backend dependencies
- Copies source code
- Copies document collection
- Runs FastAPI with Uvicorn

Frontend Dockerfile:

- Uses Python 3.11 Slim
- Installs Streamlit dependencies
- Runs Streamlit application

---

# ⚡ Docker Layer Caching Verification

Docker layer caching was verified during image rebuilds.

Build output showed cached dependency layers:

```text
CACHED [4/10] COPY requirements.txt .
CACHED [5/10] RUN pip install --no-cache-dir -r requirements.txt
CACHED [6/10] RUN pip install numpy==1.26.4
```

This confirms Docker reused previously built layers rather than reinstalling dependencies.

---

# 🔁 Persistence

Docker named volumes are used for persistence:

```yaml
volumes:
  chroma_data:
  ollama_data:
```

These volumes preserve:

- ChromaDB embeddings
- Ollama model downloads

across container restarts.

---

# ✅ Continuous Integration

GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

CI tasks include:

- Dependency installation
- Backend testing
- Docker image builds
- Build verification

---

# 🎯 Lessons Learned

This project demonstrates:

- Retrieval-Augmented Generation architecture
- FastAPI service design
- Streamlit frontend integration
- Vector database retrieval
- Prompt engineering
- Docker multi-service deployments
- Environment-based configuration
- CI/CD automation

