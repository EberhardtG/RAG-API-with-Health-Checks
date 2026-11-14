
# 🧠 Full-Stack RAG System
## FastAPI + ChromaDB + Ollama + Streamlit + Docker Compose + CI

A complete Retrieval-Augmented Generation (RAG) application built with:

- FastAPI
- ChromaDB
- Ollama
- Sentence Transformers
- Streamlit
- Docker Compose
- GitHub Actions

The system ingests local documents, generates embeddings, stores them in ChromaDB, retrieves relevant context using semantic search, and generates grounded responses using a local LLM running through Ollama.

---

# 🚀 Features

## Backend (FastAPI)

Endpoints:

- GET `/`
- POST `/ask`
- POST `/ingest`
- GET `/stats`
- GET `/debug-retrieve`
- GET `/health`

### RAG Features

- Document ingestion
- Paragraph-based chunking
- Sentence Transformer embeddings
- ChromaDB vector storage
- Retrieval of relevant document chunks
- Source citations
- Confidence scoring
- Retrieval guardrails
- Health monitoring
- Statistics endpoint

---

## Frontend (Streamlit)

- Chat-based interface using `st.chat_input()`
- Persistent chat history using Session State
- Chat rendering with `st.chat_message()`
- Health monitoring sidebar
- Indexed document count display
- Re-index documents button
- Confidence score display
- Expandable source citation panel
- Environment variable configuration

---

## Infrastructure

- Dockerized backend
- Dockerized frontend
- Ollama container
- ChromaDB persistent volume
- Ollama persistent volume
- Environment-based configuration
- CI/CD pipeline

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
│   │
│   ├── docs/
│   │   ├── api_basics.txt
│   │   ├── fastapi_intro.txt
│   │   ├── embeddings_overview.txt
│   │   ├── llm_behavior.txt
│   │   ├── python_functions.txt
│   │   └── sql_databases.txt
│   │
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

The RAG pipeline uses a document corpus located in:

```text
backend/docs/
```

The corpus contains six expanded technical documents:

- API Fundamentals
- FastAPI Introduction
- Embeddings Overview
- Large Language Model Behavior
- Python Functions
- SQL Databases

The combined corpus exceeds the minimum assignment requirement and provides enough content to support meaningful retrieval and semantic search.

Documents are:

- Loaded from disk
- Split into chunks
- Converted into embeddings
- Stored in ChromaDB
- Retrieved during semantic search

---

# ⚙️ Configuration

Configuration is managed with environment variables.

Example `.env.example`:

```env
OLLAMA_URL=http://ollama:11434
MODEL_NAME=llama3.2:1b

CHROMA_PATH=/app/chroma_data

MAX_RESULTS=3
CONFIDENCE_THRESHOLD=1.0

BACKEND_URL=http://backend:8000
```

---

## Environment Security

The repository includes:

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

preventing sensitive or generated files from being committed.

---

# 🔍 RAG Pipeline

## Step 1: Ingestion

Documents are loaded from:

```text
backend/docs/
```

and split into paragraph chunks.

Each chunk receives metadata including:

- Source filename
- Chunk index
- Unique chunk identifier

Chunks are then embedded and stored in ChromaDB.

---

## Step 2: Retrieval

When a question is asked:

1. The question is converted into an embedding.
2. ChromaDB performs semantic similarity search.
3. Relevant document chunks are returned.
4. Retrieved context is supplied to the language model.

Example:

```text
Retrieved 1 chunks:

[1] embeddings_overview.txt
```

---

## Step 3: Generation

Retrieved context is injected into a guardrailed system prompt and sent to Ollama.

The model is instructed to:

- Use provided context
- Avoid unsupported claims
- Cite sources
- Respond with "I don't know" when context is insufficient

---

## Step 4: Confidence Scoring

Confidence is based on retrieval distance.

| Distance | Confidence |
|-----------|------------|
| < 0.5 | High |
| < 1.0 | Medium |
| >= 1.0 | Low |

---

# 🛡️ Reliability Guardrails

The application includes retrieval-based guardrails designed to reduce hallucinations.

Workflow:

1. Retrieve relevant document chunks
2. Evaluate similarity distance
3. Assign confidence score
4. Reject unsupported answers when confidence is low

Fallback behavior:

```text
I don't know.
```

Example out-of-scope question:

```text
Who won the Super Bowl in 1991?
```

Expected response:

```text
Confidence: low

I don't know.
```

This ensures responses remain grounded in the document collection.

---

# 💬 Streamlit Features

The Streamlit interface includes:

- Chat history persistence
- Real-time question answering
- Expandable source citations
- Confidence indicators
- Backend health monitoring
- Indexed document statistics
- Re-index functionality

The frontend communicates with the FastAPI backend through Docker networking.

---

# 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|----------|-------------|
| `/` | GET | Root endpoint |
| `/ask` | POST | Submit a question |
| `/ingest` | POST | Load and embed documents |
| `/stats` | GET | Collection statistics |
| `/debug-retrieve` | GET | Retrieval debugging |
| `/health` | GET | Service health checks |

---

# 🧪 Testing

The project includes automated API tests located in:

```text
backend/tests/test_api.py
```

Current test coverage includes:

- Root endpoint
- Health endpoint
- Statistics endpoint
- Ask endpoint
- Question validation
- Retrieval behavior
- Guardrail behavior

Run tests with:

```bash
python -m pytest -v
```

Example output:

```text
7 tests collected
6+ tests passing
```

---

# 🐳 Docker Architecture

The project uses three containers.

## Backend

Technology:

```text
FastAPI
ChromaDB
Sentence Transformers
```

Port:

```text
8000
```

---

## Frontend

Technology:

```text
Streamlit
```

Port:

```text
8501
```

---

## Ollama

Technology:

```text
Llama 3.2 1B
```

Port:

```text
11434
```

---

## Environment Configuration

Application settings are loaded through:

```text
.env
```

A template configuration file is included:

```text
.env.example
```

The frontend uses:

```python
BACKEND_URL = os.getenv(...)
```

instead of hardcoded URLs.

This improves portability across environments.

---

# 🔁 Persistence

Docker named volumes preserve data across restarts.

```yaml
volumes:
  chroma_data:
  ollama_data:
```

Stored data includes:

- ChromaDB embeddings
- Downloaded Ollama models

---

# ✅ Continuous Integration

GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

Automated tasks:

- Dependency installation
- API testing
- Docker image builds
- Build verification

---

# 🎯 Required Query Demonstration

### Question 1

```text
What is FastAPI?
```

Retrieved:

```text
fastapi_intro.txt
```

Expected behavior:

- Answer generated
- Confidence displayed
- Source citation shown

---

### Question 2

```text
What are embeddings?
```

Retrieved:

```text
embeddings_overview.txt
```

Expected behavior:

- Semantic retrieval
- Context-grounded response
- Source citation shown

---

### Question 3

```text
Who won the Super Bowl in 1991?
```

Expected behavior:

```text
Confidence: low

I don't know.
```

Demonstrates retrieval guardrails and hallucination prevention.

---

# 🔮 Future Improvements

Potential enhancements include:

- Multi-turn conversation memory
- File upload support
- Streaming LLM responses
- Enhanced confidence calculations
- Additional document formats (PDF, DOCX)
- Expanded automated testing
- Faster inference performance
- Advanced citation formatting

---

# 🎓 Lessons Learned

This project demonstrates:

- Retrieval-Augmented Generation architecture
- Semantic search with embeddings
- FastAPI API development
- Streamlit application development
- ChromaDB vector databases
- Ollama local LLM deployment
- Docker Compose orchestration
- Environment-based configuration
- Automated testing
- CI/CD workflows
- Reliability guardrails
- Source-grounded AI responses


