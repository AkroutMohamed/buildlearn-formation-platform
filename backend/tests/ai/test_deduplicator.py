from __future__ import annotations

from app.ai.acquisition.deduplicator import DocumentDeduplicator, DocumentRecord


class TestDocumentDeduplicator:
    def _make_record(self, url: str, content_hash: str | None = "hash123") -> DocumentRecord:
        return DocumentRecord(
            document_url=url,
            product_name="Test Product",
            source="gypsobat",
            document_type="technical_sheet",
            supplier="Test Supplier",
            confidence="medium",
            source_type="official",
            evidence="test evidence",
            is_pdf=True,
            downloadable=True,
            content_hash=content_hash,
        )

    def test_compute_hash_deterministic(self):
        h1 = DocumentDeduplicator.compute_hash(b"hello")
        h2 = DocumentDeduplicator.compute_hash(b"hello")
        h3 = DocumentDeduplicator.compute_hash(b"world")
        assert h1 == h2
        assert h1 != h3

    def test_register_unique_document_returns_true(self):
        dedup = DocumentDeduplicator()
        record = self._make_record("https://example.com/doc1.pdf")
        is_new = dedup.register(record)
        assert is_new is True
        assert record.duplicate_of is None
        assert record.canonical_url == "https://example.com/doc1.pdf"
        assert dedup.unique_count == 1
        assert dedup.duplicate_count == 0

    def test_register_duplicate_different_url_same_hash(self):
        dedup = DocumentDeduplicator()
        canonical = self._make_record("https://example.com/original.pdf", content_hash="abc123")
        dup = self._make_record("https://example.com/duplicate.pdf", content_hash="abc123")

        assert dedup.register(canonical) is True
        assert dedup.register(dup) is False

        assert dup.duplicate_of == "https://example.com/original.pdf"
        assert dup.canonical_url == "https://example.com/original.pdf"
        assert canonical.alternative_urls == ["https://example.com/duplicate.pdf"]
        assert dedup.duplicate_count == 1

    def test_register_multiple_duplicates(self):
        dedup = DocumentDeduplicator()
        rec1 = self._make_record("https://a.com/doc.pdf", content_hash="hash_a")
        rec2 = self._make_record("https://b.com/doc.pdf", content_hash="hash_a")
        rec3 = self._make_record("https://c.com/doc.pdf", content_hash="hash_a")

        dedup.register(rec1)
        dedup.register(rec2)
        dedup.register(rec3)

        assert dedup.unique_count == 1
        assert dedup.duplicate_count == 2
        assert rec2.duplicate_of == "https://a.com/doc.pdf"
        assert rec3.duplicate_of == "https://a.com/doc.pdf"
        assert set(rec1.alternative_urls) == {"https://b.com/doc.pdf", "https://c.com/doc.pdf"}

    def test_register_different_hashes_both_unique(self):
        dedup = DocumentDeduplicator()
        rec1 = self._make_record("https://a.com/doc.pdf", content_hash="hash1")
        rec2 = self._make_record("https://b.com/doc2.pdf", content_hash="hash2")

        assert dedup.register(rec1) is True
        assert dedup.register(rec2) is True
        assert dedup.unique_count == 2
        assert dedup.duplicate_count == 0

    def test_register_no_hash_treated_as_unique(self):
        dedup = DocumentDeduplicator()
        rec1 = self._make_record("https://a.com/doc.pdf", content_hash=None)
        rec2 = self._make_record("https://b.com/doc.pdf", content_hash=None)

        assert dedup.register(rec1) is True
        assert dedup.register(rec2) is True
        # Records with no hash are not tracked in unique_count
        assert dedup.duplicate_count == 0

    def test_is_duplicate(self):
        dedup = DocumentDeduplicator()
        rec = self._make_record("https://a.com/doc.pdf", content_hash="hash1")
        dedup.register(rec)

        assert dedup.is_duplicate("hash1") is True
        assert dedup.is_duplicate("unknown_hash") is False

    def test_get_canonical_url(self):
        dedup = DocumentDeduplicator()
        rec = self._make_record("https://a.com/doc.pdf", content_hash="hash1")
        dedup.register(rec)

        assert dedup.get_canonical_url("hash1") == "https://a.com/doc.pdf"
        assert dedup.get_canonical_url("unknown") is None

    def test_all_records(self):
        dedup = DocumentDeduplicator()
        rec1 = self._make_record("https://a.com/doc.pdf", content_hash="hash1")
        rec2 = self._make_record("https://b.com/doc.pdf", content_hash="hash2")
        rec3 = self._make_record("https://c.com/doc.pdf", content_hash="hash1")

        dedup.register(rec1)
        dedup.register(rec2)
        dedup.register(rec3)

        records = dedup.all_records()
        assert len(records) == 3

    def test_summarize(self):
        dedup = DocumentDeduplicator()
        rec1 = self._make_record("https://a.com/doc.pdf", content_hash="hash1")
        rec2 = self._make_record("https://b.com/doc.pdf", content_hash="hash1")
        rec3 = self._make_record("https://c.com/doc.pdf", content_hash="hash2")

        dedup.register(rec1)
        dedup.register(rec2)
        dedup.register(rec3)

        summary = dedup.summarize()
        assert summary["unique_documents"] == 2
        assert summary["duplicate_documents"] == 1
        assert summary["total_records"] == 3

    def test_document_record_to_dict(self):
        record = DocumentRecord(
            document_url="https://example.com/doc.pdf",
            product_name="Test Product",
            source="gypsobat",
            document_type="technical_sheet",
            supplier="Gypsobat",
            confidence="high",
            source_type="official",
            evidence="Test evidence",
            content_hash="abc123",
            indexed=True,
            chunk_count=5,
        )
        d = record.to_dict()
        assert d["document_url"] == "https://example.com/doc.pdf"
        assert d["product_name"] == "Test Product"
        assert d["confidence"] == "high"
        assert d["content_hash"] == "abc123"
        assert d["indexed"] is True
        assert d["chunk_count"] == 5
        assert d["extracted_content"] is None
