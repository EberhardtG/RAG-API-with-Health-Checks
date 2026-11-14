import chromadb
import requests
import json
import os
import time

from config import settings

# --- Configuration ---

OLLAMA_URL = settings.OLLAMA_URL
MODEL = settings.MODEL_NAME


# --- Step 1: Ingestion ---

def load_documents(directory):
    """Load all .txt and .md files from a directory."""

    if not os.path.isdir(directory):
        print(f"Directory '{directory}' does not exist.")
        return []

    docs = []

    for filename in sorted(os.listdir(directory)):
        if filename.endswith((".txt", ".md")):
            filepath = os.path.join(directory, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Chunk by paragraph
            paragraphs = [
                p.strip()
                for p in content.split("\n\n")
                if p.strip()
            ]

            for i, para in enumerate(paragraphs):
                docs.append(
                    {
                        "text": para,
                        "id": f"{filename}_{i}",
                        "metadata": {
                            "source": filename,
                            "chunk_index": str(i),
                        },
                    }
                )

    return docs


def ingest(collection, docs_directory="./docs"):
    """Load, chunk, and store documents in ChromaDB."""

    chunks = load_documents(docs_directory)

    if not chunks:
        print("No documents found!")
        return 0

    collection.upsert(
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
        ids=[c["id"] for c in chunks],
    )

    return len(chunks)


# --- Step 2: Retrieval ---

def retrieve(collection, query, n_results=3):
    """Search ChromaDB for relevant document chunks."""

    if collection.count() == 0:
        print("No documents in the collection. Did you run ingestion?")
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )

    chunks = []

    for i in range(len(results["documents"][0])):
        chunks.append(
            {
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    chunks.sort(key=lambda c: c["distance"])

    return chunks


# --- Step 3: Prompt Building ---

SYSTEM_PROMPT = """
You are a retrieval-augmented assistant.

Answer questions using the provided context.

If the answer cannot be found in the context, respond:
"I don't know."

Include sources used.
"""


def build_messages(question, retrieved_chunks):
    """Build the RAG prompt."""

    context_parts = []

    for chunk in retrieved_chunks:
        source = chunk["metadata"]["source"]
        idx = chunk["metadata"]["chunk_index"]

        context_parts.append(
            f"[Source: {source}, Chunk {idx}]\n{chunk['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    system_with_context = (
        f"{SYSTEM_PROMPT}\n\nCONTEXT:\n{context}"
    )

    return [
        {
            "role": "system",
            "content": system_with_context,
        },
        {
            "role": "user",
            "content": question,
        },
    ]


# --- Step 4: Generation ---

def generate(messages, stream=False):
    """Call Ollama."""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": messages,
                "stream": stream,
            },
            stream=stream,
            timeout=500,
        )

        if response.status_code != 200:
            return (
                f"ERROR: Ollama returned status "
                f"{response.status_code}: {response.text}"
            )

        if stream:

            full_response = ""

            for line in response.iter_lines():

                if line:
                    data = json.loads(line)

                    token = data.get(
                        "message",
                        {}
                    ).get(
                        "content",
                        ""
                    )

                    if token:
                        print(token, end="", flush=True)
                        full_response += token

            print()
            return full_response

        try:
            return response.json()["message"]["content"]

        except (KeyError, TypeError):
            return (
                "ERROR: Unexpected response format "
                "from Ollama."
            )

    except requests.exceptions.ConnectionError:
        return (
            "ERROR: Cannot connect to Ollama. "
            "Is it running? (ollama serve)"
        )


# --- Step 5: RAG Query ---

def rag_query(
    collection,
    question,
    n_results=3,
    stream=True,
    dt_threshold=1.0,
):
    print(f"\n{'=' * 60}")
    print(f"Question: {question}")
    print(f"{'=' * 60}")

    retrieved = retrieve(
        collection,
        question,
        n_results,
    )

    chunks = [
        c for c in retrieved
        if c["distance"] <= dt_threshold
    ]

    print(f"\nRetrieved {len(chunks)} chunks:")

    for i, chunk in enumerate(chunks):
        print(
            f"  [{i+1}] "
            f"(dist: {chunk['distance']:.4f}) "
            f"{chunk['metadata']['source']}"
        )

    if len(chunks) == 0:
        return {
            "answer": "I don't know.",
            "sources": [],
            "confidence": "low",
            "chunks_retrieved": [],
        }

    messages = build_messages(question, chunks)

    print("\nDEBUG CONTEXT:")
    print(messages[0]["content"])
    print("\nAnswer:\n")

    start = time.time()

    answer = generate(
        messages,
        stream=stream,
    )

    elapsed = time.time() - start

    print(f"\n[Generated in {elapsed:.1f}s]")

    best_dist = chunks[0]["distance"]

    if best_dist < 0.5:
        confidence = "high"
    elif best_dist < 1.0:
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "answer": answer,
        "sources": [
            c["metadata"]
            for c in chunks
        ],
        "confidence": confidence,
        "chunks_retrieved": chunks,
    }


# --- Step 6: Interactive Query Loop ---

def main():

    print("\nStarting RAG Pipeline...")

    client = chromadb.PersistentClient(
        path="./chroma_db"
    )

    collection = client.get_or_create_collection(
        name="documents"
    )

    chunk_count = ingest(
        collection,
        "./docs"
    )

    print(
        f"\nIngested {chunk_count} chunks."
    )

    while True:

        question = input(
            "\nAsk a question "
            "(or type 'quit'): "
        ).strip()

        if question.lower() == "quit":
            print("Goodbye!")
            break

        result = rag_query(
            collection=collection,
            question=question,
            n_results=3,
            stream=True,
        )

        print("\nConfidence:")
        print(result["confidence"])

        print("\nSources:")

        if not result["sources"]:
            print("None")
        else:
            for source in result["sources"]:
                print(
                    f"- {source['source']} "
                    f"(chunk {source['chunk_index']})"
                )


if __name__ == "__main__":
    main()