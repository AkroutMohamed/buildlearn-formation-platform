"""Run from backend: python run_hierarchical_indexing.py --help."""
import os

# Task-specific defaults; explicit process environment takes precedence.
os.environ.setdefault("EMBEDDING_PROVIDER", "ollama")
os.environ.setdefault("EMBEDDING_MODEL", "nomic-embed-text")
os.environ.setdefault("QDRANT_URL", "http://127.0.0.1:6333")
os.environ.setdefault("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

from app.ai.indexing.hierarchical_pipeline import main

if __name__ == "__main__":
    main()
