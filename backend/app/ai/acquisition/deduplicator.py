from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class DocumentRecord:
    """Represents a discovered document with its full lifecycle metadata."""
    document_url: str
    product_name: str | None = None
    source: str | None = None
    source_url: str | None = None
    document_type: str | None = None
    title: str | None = None
    mime_type: str | None = None
    supplier: str | None = None
    confidence: str | None = None
    source_type: str | None = None
    evidence: str | None = None
    discovery_provider: str | None = None
    domain: str | None = None

    # Validation results
    http_status: int | None = None
    content_type: str | None = None
    is_pdf: bool = False
    downloadable: bool = False
    content_hash: str | None = None
    file_path: str | None = None
    validation_error: str | None = None
    size_bytes: int = 0

    # Processing results
    text_extractable: bool = False
    ocr_required: bool = False
    ocr_attempted: bool = False
    ocr_succeeded: bool = False
    ocr_error: str | None = None
    page_count: int | None = None
    processed: bool = False
    chunk_count: int = 0
    indexed: bool = False
    extracted_content: str | None = None

    # Deduplication
    canonical_url: str | None = None
    duplicate_of: str | None = None
    alternative_urls: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_url": self.document_url,
            "product_name": self.product_name,
            "source": self.source,
            "source_url": self.source_url,
            "document_type": self.document_type,
            "title": self.title,
            "mime_type": self.mime_type,
            "supplier": self.supplier,
            "confidence": self.confidence,
            "source_type": self.source_type,
            "evidence": self.evidence,
            "discovery_provider": self.discovery_provider,
            "domain": self.domain,
            "http_status": self.http_status,
            "content_type": self.content_type,
            "is_pdf": self.is_pdf,
            "downloadable": self.downloadable,
            "content_hash": self.content_hash,
            "file_path": self.file_path,
            "validation_error": self.validation_error,
            "size_bytes": self.size_bytes,
            "text_extractable": self.text_extractable,
            "ocr_required": self.ocr_required,
            "ocr_attempted": self.ocr_attempted,
            "ocr_succeeded": self.ocr_succeeded,
            "ocr_error": self.ocr_error,
            "page_count": self.page_count,
            "processed": self.processed,
            "chunk_count": self.chunk_count,
            "indexed": self.indexed,
            "extracted_content": self.extracted_content,
            "canonical_url": self.canonical_url,
            "duplicate_of": self.duplicate_of,
            "alternative_urls": self.alternative_urls,
        }


class DocumentDeduplicator:
    """Deduplicates documents by SHA-256 content hash.

    Different URLs pointing to the same PDF content are recognized as duplicates.
    The first-seen URL becomes the canonical URL.
    """

    def __init__(self) -> None:
        self._hash_to_canonical: dict[str, str] = {}
        self._hash_to_records: dict[str, list[DocumentRecord]] = {}

    @staticmethod
    def compute_hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def register(self, record: DocumentRecord) -> bool:
        """Register a document record. Returns True if it's a new unique document.

        If a document with the same content hash already exists, the record is
        marked as a duplicate and linked to the canonical URL.
        """
        if not record.content_hash:
            return True

        if record.content_hash in self._hash_to_canonical:
            canonical = self._hash_to_canonical[record.content_hash]
            record.duplicate_of = canonical
            record.canonical_url = canonical
            self._hash_to_records[record.content_hash].append(record)

            canonical_record = self._find_record_by_url(canonical, record.content_hash)
            if canonical_record and record.document_url not in canonical_record.alternative_urls:
                canonical_record.alternative_urls.append(record.document_url)
            logger.info("Duplicate document detected: %s -> %s",
                        record.document_url, canonical)
            return False

        record.canonical_url = record.document_url
        self._hash_to_canonical[record.content_hash] = record.document_url
        self._hash_to_records[record.content_hash] = [record]
        return True

    def _find_record_by_url(self, url: str, content_hash: str) -> DocumentRecord | None:
        records = self._hash_to_records.get(content_hash, [])
        for r in records:
            if r.document_url == url:
                return r
        return None

    def is_duplicate(self, content_hash: str) -> bool:
        return content_hash in self._hash_to_canonical

    def get_canonical_url(self, content_hash: str) -> str | None:
        return self._hash_to_canonical.get(content_hash)

    def all_records(self) -> list[DocumentRecord]:
        records: list[DocumentRecord] = []
        for hash_records in self._hash_to_records.values():
            records.extend(hash_records)
        return records

    @property
    def duplicate_count(self) -> int:
        total = 0
        for records in self._hash_to_records.values():
            if len(records) > 1:
                total += len(records) - 1
        return total

    @property
    def unique_count(self) -> int:
        return len(self._hash_to_canonical)

    def summarize(self) -> dict[str, Any]:
        return {
            "unique_documents": self.unique_count,
            "duplicate_documents": self.duplicate_count,
            "total_records": len(self.all_records()),
        }
