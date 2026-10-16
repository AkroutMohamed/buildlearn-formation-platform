from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.ai.acquisition.deduplicator import DocumentDeduplicator, DocumentRecord
from app.ai.acquisition.external_search import SearchCandidate
from app.ai.acquisition.pipeline import AcquisitionPipeline
from app.ai.acquisition.validator import DocumentValidator, ValidationResult
from app.ai.chunking.technical_chunker import TechnicalDocumentChunker
from app.ai.schemas.chunk import ChunkCreate
from app.ai.vectorstore.qdrant_provider import QdrantVectorStore


_PDF_MAGIC = b"%PDF-1.4\n%test content here for testing purposes\n"


def _make_external_candidate(
    url: str = "https://gyproc.in/pdf/doc.pdf",
    title: str = "External Doc",
    domain: str = "gyproc.in",
    confidence: str = "high",
    discovery_provider: str = "manufacturer_targeted",
    source_type: str = "external_official",
    evidence: str = "Official domain",
    product_name: str = "BA13 Hydro",
) -> SearchCandidate:
    return SearchCandidate(
        title=title,
        url=url,
        domain=domain,
        source_type=source_type,
        confidence=confidence,
        evidence=evidence,
        product_name=product_name,
        discovery_provider=discovery_provider,
    )


def _make_valid_pdf_result(url: str = "https://gyproc.in/pdf/doc.pdf") -> ValidationResult:
    return ValidationResult(
        document_url=url,
        http_status=200,
        content_type="application/pdf",
        is_pdf=True,
        downloadable=True,
        content_hash=hashlib.sha256(_PDF_MAGIC).hexdigest(),
        file_path="/tmp/test_external.pdf",
        size_bytes=len(_PDF_MAGIC),
    )


def _make_failed_result(url: str = "https://gyproc.in/pdf/doc.pdf", error: str = "HTTP 404") -> ValidationResult:
    return ValidationResult(
        document_url=url,
        http_status=404,
        content_type="text/html",
        is_pdf=False,
        downloadable=False,
        error=error,
    )


class TestExternalDocumentRecordCreation:
    def test_accepted_candidate_creates_complete_record(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        external_searcher = MagicMock()
        candidate = _make_external_candidate()
        external_searcher.search.side_effect = [[candidate]] + [[]] * 4

        pipeline = AcquisitionPipeline(validator=validator, external_searcher=external_searcher)

        products = [{
            "name": "BA13 Hydro",
            "manufacturer": "GYPROC",
            "documents": [{"document_url": "https://x.com/broken.pdf"}],
            "source_url": "https://x.com/p1/",
        }]
        record = DocumentRecord(
            document_url="https://x.com/broken.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=False,
            downloadable=False,
            validation_error="HTTP 404",
            http_status=404,
            confidence="high",
        )
        pipeline.deduplicator.register(record)

        with patch.object(validator._session, "get", return_value=mock_response):
            missing, external_records = pipeline._handle_missing_documents(
                products, [record], "gypsobat", {"manufacturer": "Gypsobat"}
            )

        assert len(missing) == 1
        assert len(external_records) == 1
        rec = external_records[0]
        assert rec.document_url == "https://gyproc.in/pdf/doc.pdf"
        assert rec.product_name == "BA13 Hydro"
        assert rec.source == "gypsobat"
        assert rec.source_type == "external_official"
        assert rec.discovery_provider == "manufacturer_targeted"
        assert rec.domain == "gyproc.in"
        assert rec.supplier == "GYPROC"
        assert rec.http_status == 200
        assert rec.is_pdf is True
        assert rec.downloadable is True
        assert rec.content_hash is not None
        assert rec.validation_error is None
        assert rec.evidence is not None
        assert "manufacturer_targeted" in rec.evidence
        assert "gyproc.in" in rec.evidence

    def test_rejected_candidate_not_processed(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        external_searcher = MagicMock()
        candidate = _make_external_candidate(source_type="third_party", confidence="low")
        external_searcher.search.side_effect = [[candidate]] + [[]] * 4

        pipeline = AcquisitionPipeline(validator=validator, external_searcher=external_searcher)

        products = [{
            "name": "BA13 Hydro",
            "manufacturer": "GYPROC",
            "documents": [{"document_url": "https://x.com/broken.pdf"}],
            "source_url": "https://x.com/p1/",
        }]
        record = DocumentRecord(
            document_url="https://x.com/broken.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=False,
            downloadable=False,
            validation_error="HTTP 404",
            http_status=404,
            confidence="high",
        )
        pipeline.deduplicator.register(record)

        missing, external_records = pipeline._handle_missing_documents(
            products, [record], "gypsobat", {"manufacturer": "Gypsobat"}
        )

        assert len(external_records) == 0


class TestExternalDownloadFailures:
    def test_http_404_rejects_candidate(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.iter_content = lambda chunk_size: []

        external_searcher = MagicMock()
        candidate = _make_external_candidate(url="https://gyproc.in/pdf/missing.pdf")
        external_searcher.search.side_effect = [[candidate]] + [[]] * 4

        pipeline = AcquisitionPipeline(validator=validator, external_searcher=external_searcher)
        products = [{
            "name": "BA13 Hydro",
            "manufacturer": "GYPROC",
            "documents": [{"document_url": "https://x.com/broken.pdf"}],
            "source_url": "https://x.com/p1/",
        }]
        record = DocumentRecord(
            document_url="https://x.com/broken.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=False,
            downloadable=False,
            validation_error="HTTP 404",
            http_status=404,
            confidence="high",
        )
        pipeline.deduplicator.register(record)

        with patch.object(validator._session, "get", return_value=mock_response):
            missing, external_records = pipeline._handle_missing_documents(
                products, [record], "gypsobat", {"manufacturer": "Gypsobat"}
            )
        assert len(external_records) == 1
        assert external_records[0].downloadable is False

    def test_http_500_rejects_candidate(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.iter_content = lambda chunk_size: []

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/error.pdf", "gypsobat")

        assert result.http_status == 500
        assert result.error == "HTTP 500"

    def test_timeout_rejects_candidate(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        import requests
        with patch.object(validator._session, "get", side_effect=requests.Timeout("Request timed out")):
            result = validator.validate_and_download("https://gyproc.in/pdf/slow.pdf", "gypsobat")

        assert result.error is not None
        assert "Request error" in result.error or "timeout" in result.error.lower()

    def test_invalid_content_type_rejects_candidate(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.iter_content = lambda chunk_size: [b"<html>not pdf</html>"]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/page.html", "gypsobat")

        assert result.is_pdf is False
        assert "Content-Type" in result.error

    def test_invalid_pdf_magic_bytes_rejects_candidate(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [b"Not a PDF file at all!!!"]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/fake.pdf", "gypsobat")

        assert result.is_pdf is False
        assert "magic" in result.error.lower()


class TestDuplicateProtection:
    def test_same_url_discovered_twice_is_deduplicated(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        external_searcher = MagicMock()
        candidate = _make_external_candidate(url="https://gyproc.in/pdf/doc.pdf")
        external_searcher.search.return_value = [candidate]

        pipeline = AcquisitionPipeline(validator=validator, external_searcher=external_searcher)

        products = [{
            "name": "BA13 Hydro",
            "manufacturer": "GYPROC",
            "documents": [{"document_url": "https://x.com/broken.pdf"}],
            "source_url": "https://x.com/p1/",
        }]
        record = DocumentRecord(
            document_url="https://x.com/broken.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=False,
            downloadable=False,
            validation_error="HTTP 404",
            http_status=404,
            confidence="high",
        )
        pipeline.deduplicator.register(record)

        with patch.object(validator._session, "get", return_value=mock_response):
            with patch("app.ai.acquisition.pipeline.build_search_queries", return_value=["query1"]):
                missing1, ext1 = pipeline._handle_missing_documents(
                    products, [record], "gypsobat", {"manufacturer": "Gypsobat"}
                )
        assert len(ext1) == 1

        products2 = [{
            "name": "BA13 Hydro",
            "manufacturer": "GYPROC",
            "documents": [{"document_url": "https://x.com/broken2.pdf"}],
            "source_url": "https://x.com/p2/",
        }]
        record2 = DocumentRecord(
            document_url="https://x.com/broken2.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=False,
            downloadable=False,
            validation_error="HTTP 404",
            http_status=404,
            confidence="high",
        )
        pipeline.deduplicator.register(record2)

        with patch.object(validator._session, "get", return_value=mock_response):
            with patch("app.ai.acquisition.pipeline.build_search_queries", return_value=["query1"]):
                missing2, ext2 = pipeline._handle_missing_documents(
                    products2, [record2], "gypsobat", {"manufacturer": "Gypsobat"}
                )
        assert len(ext2) == 1
        assert ext2[0].duplicate_of == ext1[0].document_url

    def test_encoded_vs_unencoded_url_deduplication(self):
        dedup = DocumentDeduplicator()
        rec1 = DocumentRecord(
            document_url="https://example.com/path with spaces/file.pdf",
            content_hash="samehash",
            is_pdf=True,
            downloadable=True,
        )
        rec2 = DocumentRecord(
            document_url="https://example.com/path%20with%20spaces/file.pdf",
            content_hash="samehash",
            is_pdf=True,
            downloadable=True,
        )

        assert dedup.register(rec1) is True
        assert dedup.register(rec2) is False
        assert rec2.duplicate_of == "https://example.com/path with spaces/file.pdf"

    def test_same_document_different_providers_deduplicated(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result1 = validator.validate_and_download("https://gyproc.in/pdf/doc.pdf", "gypsobat")
            result2 = validator.validate_and_download("https://cdn.gyproc.com/doc.pdf", "gypsobat")

        assert result1.content_hash == result2.content_hash

        dedup = DocumentDeduplicator()
        rec1 = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            content_hash=result1.content_hash,
            is_pdf=True,
            downloadable=True,
            source_type="external_official",
            discovery_provider="manufacturer_targeted",
        )
        rec2 = DocumentRecord(
            document_url="https://cdn.gyproc.com/doc.pdf",
            content_hash=result2.content_hash,
            is_pdf=True,
            downloadable=True,
            source_type="external_official",
            discovery_provider="web_search",
        )

        assert dedup.register(rec1) is True
        assert dedup.register(rec2) is False
        assert rec2.duplicate_of == "https://gyproc.in/pdf/doc.pdf"


class TestPartialFailures:
    def test_partial_download_failures_continue_pipeline(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.headers = {"Content-Type": "application/pdf"}
        mock_success.iter_content = lambda chunk_size: [_PDF_MAGIC]

        mock_failure = MagicMock()
        mock_failure.status_code = 404
        mock_failure.headers = {"Content-Type": "text/html"}
        mock_failure.iter_content = lambda chunk_size: []

        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            url = args[0] if args else kwargs.get("url", "")
            if "good" in url:
                return mock_success
            return mock_failure

        candidates = [
            _make_external_candidate(url="https://gyproc.in/pdf/good.pdf", title="Good Doc"),
            _make_external_candidate(url="https://gyproc.in/pdf/bad.pdf", title="Bad Doc", confidence="high"),
            _make_external_candidate(url="https://gyproc.in/pdf/good2.pdf", title="Good Doc 2"),
        ]
        external_searcher = MagicMock()
        external_searcher.search.side_effect = [candidates, []]

        pipeline = AcquisitionPipeline(validator=validator)
        pipeline.external_searcher = external_searcher

        products = [{
            "name": "BA13 Hydro",
            "manufacturer": "GYPROC",
            "documents": [{"document_url": "https://x.com/broken.pdf"}],
            "source_url": "https://x.com/p1/",
        }]
        record = DocumentRecord(
            document_url="https://x.com/broken.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=False,
            downloadable=False,
            validation_error="HTTP 404",
            http_status=404,
            confidence="high",
        )
        pipeline.deduplicator.register(record)

        with patch.object(validator._session, "get", side_effect=side_effect):
            missing, external_records = pipeline._handle_missing_documents(
                products, [record], "gypsobat", {"manufacturer": "Gypsobat"}
            )

        assert len(external_records) == 3
        good_urls = [r.document_url for r in external_records if r.downloadable]
        bad_urls = [r.document_url for r in external_records if not r.downloadable]
        assert len(good_urls) == 2
        assert len(bad_urls) == 1


class TestProcessingFailures:
    def test_extraction_failure_does_not_crash_pipeline(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/doc.pdf", "gypsobat")

        pipeline = AcquisitionPipeline(validator=validator)
        record = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            source="gypsobat",
            source_type="external_official",
            is_pdf=result.is_pdf,
            downloadable=result.downloadable,
            content_hash=result.content_hash,
            file_path=result.file_path,
            http_status=result.http_status,
            content_type=result.content_type,
            validation_error=result.error,
            size_bytes=result.size_bytes,
        )

        with patch("app.ai.acquisition.pipeline.PdfProcessor") as MockProcessor:
            mock_processor = MagicMock()
            mock_processor.extract.side_effect = RuntimeError("PDF extraction crashed")
            MockProcessor.return_value = mock_processor

            pipeline._process_document_content([record])

        assert record.processed is False
        assert record.ocr_error is not None
        assert "PDF processing failed" in record.ocr_error

    def test_chunking_failure_reports_and_skips_document(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/doc.pdf", "gypsobat")

        pipeline = AcquisitionPipeline(validator=validator)
        record = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            source="gypsobat",
            source_type="external_official",
            is_pdf=result.is_pdf,
            downloadable=result.downloadable,
            content_hash=result.content_hash,
            file_path=result.file_path,
            http_status=result.http_status,
            content_type=result.content_type,
            validation_error=result.error,
            size_bytes=result.size_bytes,
            extracted_content="Some extracted text",
            processed=True,
            text_extractable=True,
            chunk_count=0,
        )

        mock_chunker = MagicMock(spec=TechnicalDocumentChunker)
        mock_chunker.chunk.side_effect = RuntimeError("Chunker crashed")

        mock_embedding = MagicMock()
        mock_embedding.embed.return_value = [[0.1] * 768]
        mock_vector_store = MagicMock()

        pipeline.chunker = mock_chunker
        pipeline.embedding_provider = mock_embedding
        pipeline.vector_store = mock_vector_store

        with patch.object(pipeline, "_record_to_doc_dict") as mock_to_dict:
            mock_to_dict.return_value = {"document_id": "doc-1", "content": "text"}
            pipeline._index_documents([record])

        mock_vector_store.upsert_chunks.assert_not_called()
        assert record.indexed is False

    def test_embedding_failure_does_not_crash_pipeline(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/doc.pdf", "gypsobat")

        pipeline = AcquisitionPipeline(validator=validator)
        record = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            source="gypsobat",
            source_type="external_official",
            is_pdf=result.is_pdf,
            downloadable=result.downloadable,
            content_hash=result.content_hash,
            file_path=result.file_path,
            http_status=result.http_status,
            content_type=result.content_type,
            validation_error=result.error,
            size_bytes=result.size_bytes,
            extracted_content="Some extracted text",
            processed=True,
            text_extractable=True,
            chunk_count=0,
        )

        mock_chunker = MagicMock(spec=TechnicalDocumentChunker)
        mock_chunker.chunk.return_value = [
            ChunkCreate(
                chunk_id="abc123",
                document_id="doc-1",
                chunk_index=0,
                text="chunk text",
                metadata={},
            )
        ]

        mock_embedding = MagicMock()
        mock_embedding.embed.side_effect = RuntimeError("Embedding failed")
        mock_vector_store = MagicMock()

        pipeline.chunker = mock_chunker
        pipeline.embedding_provider = mock_embedding
        pipeline.vector_store = mock_vector_store

        with patch.object(pipeline, "_record_to_doc_dict") as mock_to_dict:
            mock_to_dict.return_value = {"document_id": "doc-1", "content": "text"}
            pipeline._index_documents([record])

        mock_vector_store.upsert_chunks.assert_not_called()
        assert record.indexed is False

    def test_qdrant_insertion_failure_does_not_crash_pipeline(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/doc.pdf", "gypsobat")

        pipeline = AcquisitionPipeline(validator=validator)
        record = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            source="gypsobat",
            source_type="external_official",
            is_pdf=result.is_pdf,
            downloadable=result.downloadable,
            content_hash=result.content_hash,
            file_path=result.file_path,
            http_status=result.http_status,
            content_type=result.content_type,
            validation_error=result.error,
            size_bytes=result.size_bytes,
            extracted_content="Some extracted text",
            processed=True,
            text_extractable=True,
            chunk_count=0,
        )

        mock_chunker = MagicMock(spec=TechnicalDocumentChunker)
        mock_chunker.chunk.return_value = [
            ChunkCreate(
                chunk_id="abc123",
                document_id="doc-1",
                chunk_index=0,
                text="chunk text",
                metadata={},
            )
        ]

        mock_embedding = MagicMock()
        mock_embedding.embed.return_value = [[0.1] * 768]
        mock_vector_store = MagicMock()
        mock_vector_store.upsert_chunks.side_effect = RuntimeError("Qdrant connection failed")

        pipeline.chunker = mock_chunker
        pipeline.embedding_provider = mock_embedding
        pipeline.vector_store = mock_vector_store

        with patch.object(pipeline, "_record_to_doc_dict") as mock_to_dict:
            mock_to_dict.return_value = {"document_id": "doc-1", "content": "text"}
            pipeline._index_documents([record])

        assert record.indexed is False


class TestIdempotency:
    def test_external_candidates_idempotent_on_second_run(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/doc.pdf", "gypsobat")

        shared_dedup = DocumentDeduplicator()
        pipeline = AcquisitionPipeline(validator=validator, deduplicator=shared_dedup)

        record = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            source="gypsobat",
            source_type="external_official",
            is_pdf=result.is_pdf,
            downloadable=result.downloadable,
            content_hash=result.content_hash,
            file_path=result.file_path,
            http_status=result.http_status,
            content_type=result.content_type,
            validation_error=result.error,
            size_bytes=result.size_bytes,
            extracted_content="Some extracted text",
            processed=True,
            text_extractable=True,
            chunk_count=0,
        )
        shared_dedup.register(record)

        mock_chunker = MagicMock(spec=TechnicalDocumentChunker)
        mock_chunker.chunk.return_value = [
            ChunkCreate(
                chunk_id="abc123",
                document_id="doc-1",
                chunk_index=0,
                text="chunk text",
                metadata={},
            )
        ]

        mock_embedding = MagicMock()
        mock_embedding.embed.return_value = [[0.1] * 768]
        mock_vector_store = MagicMock()

        pipeline.chunker = mock_chunker
        pipeline.embedding_provider = mock_embedding
        pipeline.vector_store = mock_vector_store

        with patch.object(pipeline, "_record_to_doc_dict") as mock_to_dict:
            mock_to_dict.return_value = {"document_id": "doc-1", "content": "text"}
            pipeline._index_documents([record])

        assert record.indexed is True
        assert mock_vector_store.upsert_chunks.call_count == 1

        mock_vector_store.reset_mock()

        record2 = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            source="gypsobat",
            source_type="external_official",
            is_pdf=result.is_pdf,
            downloadable=result.downloadable,
            content_hash=result.content_hash,
            file_path=result.file_path,
            http_status=result.http_status,
            content_type=result.content_type,
            validation_error=result.error,
            size_bytes=result.size_bytes,
            extracted_content="Some extracted text",
            processed=True,
            text_extractable=True,
            chunk_count=0,
        )
        shared_dedup.register(record2)

        pipeline2 = AcquisitionPipeline(validator=validator, deduplicator=shared_dedup)
        pipeline2.chunker = mock_chunker
        pipeline2.embedding_provider = mock_embedding
        pipeline2.vector_store = mock_vector_store

        with patch.object(pipeline2, "_record_to_doc_dict") as mock_to_dict:
            mock_to_dict.return_value = {"document_id": "doc-1", "content": "text"}
            pipeline2._index_documents([record2])

        mock_vector_store.upsert_chunks.assert_not_called()
        assert record2.indexed is False


class TestProvenance:
    def test_external_record_to_dict_includes_provenance(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/doc.pdf", "gypsobat")

        record = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            product_name="BA13 Hydro",
            source="gypsobat",
            source_url="https://x.com/p1/",
            document_type="technical_sheet",
            title="Gyproc BA13 Hydro Datasheet",
            supplier="GYPROC",
            confidence="high",
            source_type="external_official",
            evidence="Found via manufacturer_targeted",
            discovery_provider="manufacturer_targeted",
            domain="gyproc.in",
            http_status=result.http_status,
            content_type=result.content_type,
            is_pdf=result.is_pdf,
            downloadable=result.downloadable,
            content_hash=result.content_hash,
            file_path=result.file_path,
            validation_error=result.error,
            size_bytes=result.size_bytes,
        )

        d = record.to_dict()
        assert d["document_url"] == "https://gyproc.in/pdf/doc.pdf"
        assert d["product_name"] == "BA13 Hydro"
        assert d["supplier"] == "GYPROC"
        assert d["source_type"] == "external_official"
        assert d["discovery_provider"] == "manufacturer_targeted"
        assert d["domain"] == "gyproc.in"
        assert d["confidence"] == "high"
        assert d["evidence"] == "Found via manufacturer_targeted"

    def test_record_to_doc_dict_preserves_provenance_metadata(self, tmp_path):
        validator = DocumentValidator(download_dir=tmp_path)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/pdf"}
        mock_response.iter_content = lambda chunk_size: [_PDF_MAGIC]

        with patch.object(validator._session, "get", return_value=mock_response):
            result = validator.validate_and_download("https://gyproc.in/pdf/doc.pdf", "gypsobat")

        pipeline = AcquisitionPipeline(validator=validator)
        record = DocumentRecord(
            document_url="https://gyproc.in/pdf/doc.pdf",
            product_name="BA13 Hydro",
            source="gypsobat",
            source_url="https://x.com/p1/",
            document_type="technical_sheet",
            title="Gyproc BA13 Hydro Datasheet",
            supplier="GYPROC",
            confidence="high",
            source_type="external_official",
            evidence="Found via manufacturer_targeted",
            discovery_provider="manufacturer_targeted",
            domain="gyproc.in",
            http_status=result.http_status,
            content_type=result.content_type,
            is_pdf=result.is_pdf,
            downloadable=result.downloadable,
            content_hash=result.content_hash,
            file_path=result.file_path,
            validation_error=result.error,
            size_bytes=result.size_bytes,
            extracted_content="Some extracted text",
            processed=True,
            text_extractable=True,
        )

        doc_dict = pipeline._record_to_doc_dict(record)
        assert doc_dict["document_url"] == "https://gyproc.in/pdf/doc.pdf"
        assert doc_dict["product_name"] == "BA13 Hydro"
        assert doc_dict["source_url"] == "https://x.com/p1/"
        assert doc_dict["metadata"]["source_type"] == "external_official"
        assert doc_dict["metadata"]["discovery_provider"] == "manufacturer_targeted"
        assert doc_dict["metadata"]["domain"] == "gyproc.in"
        assert doc_dict["metadata"]["product_name"] == "BA13 Hydro"
        assert doc_dict["metadata"]["supplier"] == "GYPROC"
        assert doc_dict["metadata"]["confidence"] == "high"


class TestGyprocRegression:
    def test_ba13_hydro_matches_moisture_resistant_board(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Moisture Resistant Board 2024",
            url="https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="GYPROC") is True

    def test_ba13_feu_matches_fireline(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Fireline Board 2024",
            url="https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Feu", None, manufacturer="GYPROC") is True

    def test_ba13_standard_matches_plain_board(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Plain Board 2024",
            url="https://www.gyproc.in/pdf/PB01_Gypboard_Plain.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Standard", None, manufacturer="GYPROC") is True

    def test_lika_pap2_rejected_for_ba13_hydro(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Lika PAP2",
            url="https://www.gypsobat.com/wp-content/uploads/2024/11/fiche_technique_pap2.pdf",
            domain="gypsobat.com",
            source_type="official",
            confidence="medium",
            evidence="Matched via Gypsobat documentation pages",
            discovery_provider=None,
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="Gypsobat") is False

    def test_ba13_hydro_duraline_alias_accepted(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Duraline Board",
            url="https://www.gyproc.in/pdf/PB05_Gyproc_Duraline_Board.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="GYPROC") is True

    def test_gyproc_provenance_reaches_final_qdrant_payload(self):
        record = DocumentRecord(
            document_url="https://www.gyproc.in/pdf/Gyproc_BA13_Hydro.pdf",
            product_name="BA13 Hydro",
            supplier="GYPROC",
            source="gypsobat",
            source_url="https://x.com/p1/",
            document_type="technical_sheet",
            title="Gyproc BA13 Hydro Datasheet",
            confidence="high",
            source_type="external_official",
            evidence="Found via manufacturer_targeted",
            discovery_provider="manufacturer_targeted",
            domain="www.gyproc.in",
            content_hash="abc123hash",
            extracted_content="Moisture Resistance high moisture resistance board for bathrooms.",
            processed=True,
            text_extractable=True,
        )

        pipeline = AcquisitionPipeline()
        doc_dict = pipeline._record_to_doc_dict(record)

        chunker = TechnicalDocumentChunker()
        chunks = chunker.chunk(doc_dict, product=None)
        assert len(chunks) > 0

        chunk = chunks[0]
        payload = QdrantVectorStore._build_payload(chunk)

        assert payload["product_name"] == "BA13 Hydro"
        assert payload["supplier"] == "GYPROC"
        assert payload["source_type"] == "external_official"
        assert payload["discovery_provider"] == "manufacturer_targeted"
        assert payload["domain"] == "www.gyproc.in"
        assert payload["confidence"] == "high"
        assert payload["evidence"] == "Found via manufacturer_targeted"
        assert payload["source_url"] == "https://x.com/p1/"
        assert payload["document_url"] == "https://www.gyproc.in/pdf/Gyproc_BA13_Hydro.pdf"
        assert payload["chunk_id"] is not None
        assert "Moisture Resistance" in payload["text"]
        assert "bathrooms" in payload["text"]
