#!/usr/bin/env python3
"""Manual verification script for Phase 5 embeddings.

Requires:
    - Ollama running locally
    - Model pulled: ollama pull nomic-embed-text
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.ai.chunking.technical_chunker import TechnicalDocumentChunker
from app.ai.embeddings.provider import EmbeddingProvider


def main() -> None:
    content = (
        "DOMAINE D'EMPLOI\n"
        + "Contenu technique en français pour tester les embeddings. " * 10
    )
    doc = {
        "document_id": "doc-1",
        "product_id": "prod-1",
        "product_name": "Test Produit",
        "source": "test",
        "document_type": "technical_sheet",
        "language": "fr",
        "content": content,
        "content_hash": "hash123",
        "metadata": {"page_count": 1, "supplier": "Test"},
    }

    chunker = TechnicalDocumentChunker()
    chunks = chunker.chunk(doc)
    assert chunks, "Chunker produced no chunks"

    chunk = chunks[0]
    print(f"Chunk text ({len(chunk.text)} chars): {chunk.text[:120]}...")

    provider = EmbeddingProvider()
    print(f"Embedding provider: {os.environ.get('EMBEDDING_PROVIDER', 'ollama')}")
    print(f"Embedding model: {os.environ.get('EMBEDDING_MODEL', 'nomic-embed-text')}")
    print(f"Vector dimension: {provider.dimension}")

    vector = provider.embed_single(chunk.text)
    print(f"Embedding length: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")

    magnitude = sum(x * x for x in vector) ** 0.5
    print(f"Vector magnitude: {magnitude:.6f}")

    print("\nVerification PASSED")


if __name__ == "__main__":
    main()
