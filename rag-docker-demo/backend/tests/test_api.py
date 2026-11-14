from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "chroma_db" in data
    assert "ollama" in data
    assert "model_loaded" in data


def test_stats():
    response = client.get("/stats")

    assert response.status_code == 200
    data = response.json()

    assert "documents_indexed" in data
    assert "model" in data


def test_ingest():
    response = client.post("/ingest")

    assert response.status_code in [200, 404]

    data = response.json()

    if response.status_code == 200:
        assert "message" in data
        assert "chunks_ingested" in data

    if response.status_code == 404:
        assert "detail" in data

def test_empty_question():
    response = client.post(
        "/ask",
        json={"question": ""}
    )

    assert response.status_code == 422


def test_ask_question():
    response = client.post(
        "/ask",
        json={
            "question": "What is FastAPI?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "sources" in data
    assert "confidence" in data
    assert "chunks_retrieved" in data


def test_guardrail_unknown_question():
    response = client.post(
        "/ask",
        json={
            "question": "Who won the Super Bowl in 1991?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "confidence" in data