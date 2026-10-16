from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from app.ai.chunking.chunker import HierarchicalChunker
from app.ai.chunking.config import ChunkConfig
from app.ai.chunking.models import ChunkResult

logger = logging.getLogger(__name__)


@dataclass
class ChunkingStats:
    documents_found: int = 0
    documents_processed: int = 0
    documents_failed: int = 0
    documents_skipped_status: int = 0
    total_children: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    @property
    def elapsed_seconds(self) -> float:
        end = self.end_time or time.time()
        return end - self.start_time

    def to_dict(self) -> dict:
        return {
            "documents_found": self.documents_found,
            "documents_processed": self.documents_processed,
            "documents_failed": self.documents_failed,
            "documents_skipped_status": self.documents_skipped_status,
            "total_children": self.total_children,
            "elapsed_seconds": round(self.elapsed_seconds, 2),
        }


class HierarchicalIndexer:
    def __init__(
        self,
        extraction_root: Path,
        chunk_config: Optional[ChunkConfig] = None,
    ) -> None:
        self._extraction_root = Path(extraction_root)
        self._chunker = HierarchicalChunker(chunk_config or ChunkConfig())
        self._stats = ChunkingStats()

    def discover_documents(self) -> list[Path]:
        files = sorted(self._extraction_root.glob("*.json"))
        docs = [f for f in files if f.name != "manifest.json"]
        self._stats.documents_found = len(docs)
        logger.info(f"Discovered {len(docs)} document files")
        return docs

    def load_document(self, file_path: Path) -> Optional[dict]:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            if data.get("extraction_status") != "success":
                logger.warning(f"Skipping {file_path.name}: extraction_status={data.get('extraction_status')!r}")
                self._stats.documents_skipped_status += 1
                return None
            return data
        except Exception as exc:
            logger.error(f"Failed to load {file_path.name}: {exc}")
            self._stats.documents_failed += 1
            return None

    def chunk_document(self, file_path: Path) -> Optional[ChunkResult]:
        self._stats.documents_processed += 1
        data = self.load_document(file_path)
        if data is None:
            return None
        try:
            result = self._chunker.chunk_from_dict(data)
            self._stats.total_children += len(result.children)
            logger.debug(f"Chunked {file_path.name}: {len(result.children)} children, {len(result.parents)} parents")
            return result
        except Exception as exc:
            self._stats.documents_failed += 1
            logger.error(f"Chunking failed for {file_path.name}: {exc}")
            return None

    def chunk_dataset(self) -> list[ChunkResult]:
        logger.info(f"Starting chunking of dataset from {self._extraction_root}")
        documents = self.discover_documents()
        results = []
        for doc_path in documents:
            result = self.chunk_document(doc_path)
            if result is not None:
                results.append(result)
        self._stats.end_time = time.time()
        logger.info(f"Chunking complete: {self._stats.to_dict()}")
        return results

    @property
    def stats(self) -> ChunkingStats:
        return self._stats


def chunk_dataset(
    extraction_root: str | Path,
) -> tuple[list[ChunkResult], ChunkingStats]:
    """Convenience function for script usage."""
    indexer = HierarchicalIndexer(Path(extraction_root))
    results = indexer.chunk_dataset()
    return results, indexer.stats