import streamlit as st
import requests

# Backend URL inside Docker network
BACKEND_URL = "http://backend:8000"

st.set_page_config(page_title="RAG Demo", layout="wide")
st.title("🧠 RAG Demo — Full Containerized Stack")

# --- Health Check ---
with st.sidebar:
    st.header("System Status")
    try:
        health = requests.get(f"{BACKEND_URL}/health").json()
        st.success("Backend Connected")
        st.json(health)
    except Exception:
        st.error("Backend Unreachable")

# --- Ingestion ---
st.subheader("📄 Re-index Documents")
if st.button("Re-index Documents"):
    try:
        resp = requests.post(f"{BACKEND_URL}/ingest")
        st.success("Ingestion Complete")
        st.json(resp.json())
    except Exception as e:
        st.error(f"Ingestion failed: {e}")

# --- Ask a Question ---
st.subheader("❓ Ask a Question")
question = st.text_input("Enter your question:")

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            payload = {"question": question}
            resp = requests.post(f"{BACKEND_URL}/ask", json=payload).json()

            st.markdown("### 🧩 Answer")
            st.write(resp.get("answer", "No answer returned."))

            st.markdown("### 📚 Sources")
            st.json(resp.get("sources", []))

            st.markdown("### 🔍 Retrieved Chunks")
            st.json(resp.get("chunks_retrieved", []))

            st.markdown("### 📈 Confidence")
            st.write(resp.get("confidence", "unknown"))

        except Exception as e:
            st.error(f"Query failed: {e}")
