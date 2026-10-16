from __future__ import annotations

import logging
from typing import Any

from app.ai.chunking.chunker import BaseChunker
from app.ai.embeddings.base import BaseEmbeddingProvider
from app.ai.vectorstore.base import BaseVectorStore

logger = logging.getLogger(__name__)


class IndexingService:
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_provider: BaseEmbeddingProvider,
        chunker: BaseChunker,
    ) -> None:
        self._vector_store = vector_store
        self._embedding_provider = embedding_provider
        self._chunker = chunker

    def index_document(self, document: Any, product: Any = None) -> None:
        chunks = self._chunker.chunk(document, product)
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks if chunk.text]
        if not texts:
            return

        embeddings = self._embedding_provider.embed(texts)
        self._vector_store.upsert_chunks(chunks, embeddings)

        document_id = getattr(document, "document_id", None) or (
            document.get("document_id") if isinstance(document, dict) else None
        )
        logger.info("Indexed %d chunks for document %s", len(chunks), document_id)
