import os
import requests
import streamlit as st

# --------------------------------------------------
# Configuration
# --------------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://backend:8000"
)

st.set_page_config(
    page_title="Containerized RAG Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Containerized RAG Assistant")

# --------------------------------------------------
# Session State
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.header("System Status")

    # Health Check
    try:
        health = requests.get(
            f"{BACKEND_URL}/health",
            timeout=5
        ).json()

        st.success("Backend Connected")

        st.write(
            f"ChromaDB: {health.get('chroma_db', 'unknown')}"
        )
        st.write(
            f"Ollama: {health.get('ollama', 'unknown')}"
        )
        st.write(
            f"Model Loaded: {health.get('model_loaded', 'unknown')}"
        )

    except Exception:
        st.error("Backend Unreachable")

    st.divider()

    # Document Count
    try:
        stats = requests.get(
            f"{BACKEND_URL}/stats",
            timeout=5
        ).json()

        st.metric(
            "Documents Indexed",
            stats.get("documents_indexed", 0)
        )

    except Exception:
        st.metric("Documents Indexed", "N/A")

    st.divider()

    # Re-index Button
    if st.button("🔄 Re-index Documents"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/ingest",
                timeout=60
            )

            result = response.json()

            st.success(
                f"Ingested {result.get('chunks_ingested', 0)} chunks"
            )

        except Exception as e:
            st.error(f"Ingestion failed: {e}")

# --------------------------------------------------
# Display Chat History
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and "sources" in message
        ):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.markdown(
                        f"""
                        **Source:** {source.get('source','unknown')}

                        Distance: {source.get('distance','N/A')}
                        """
                    )

# --------------------------------------------------
# Chat Input
# --------------------------------------------------

prompt = st.chat_input(
    "Ask a question about your documents..."
)

if prompt:

    # Show User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Query Backend
    try:
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={"question": prompt},
            timeout=120
        )

        result = response.json()

        answer = result.get(
            "answer",
            "No answer returned."
        )

        sources = result.get(
            "sources",
            []
        )

        confidence = result.get(
            "confidence",
            "unknown"
        )

        assistant_message = f"""
{answer}

**Confidence:** {confidence}
"""

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_message,
                "sources": sources,
            }
        )

        with st.chat_message("assistant"):

            st.markdown(assistant_message)

            with st.expander("📚 Sources"):

                if sources:

                    for source in sources:

                        st.markdown(
                            f"""
                            **Source:** {source.get('source','unknown')}

                            Distance: {source.get('distance','N/A')}
                            """
                        )

                else:
                    st.write("No sources returned.")

    except Exception as e:

        error_message = f"Request failed: {e}"

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message,
            }
        )

        with st.chat_message("assistant"):
            st.error(error_message)