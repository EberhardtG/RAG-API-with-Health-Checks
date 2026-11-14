from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # --- Core RAG / Ollama Settings ---
    OLLAMA_URL: str = Field(
    "http://ollama:11434",
    env="OLLAMA_URL"
)

    MODEL_NAME: str = Field("llama3.2:1b", env="MODEL_NAME")

    # --- ChromaDB ---
    CHROMA_PATH: str = Field("/app/chroma_data", env="CHROMA_PATH")

    # --- RAG Behavior ---
    MAX_RESULTS: int = Field(3, env="MAX_RESULTS")
    CONFIDENCE_THRESHOLD: float = Field(1.0, env="CONFIDENCE_THRESHOLD")

    # --- Debug Mode ---
    DEBUG: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton settings instance
settings = Settings()
