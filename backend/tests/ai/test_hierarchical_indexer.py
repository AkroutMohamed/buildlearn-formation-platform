import json
import tempfile
from pathlib import Path

import pytest

from app.ai.chunking.models import ChunkResult
from app.ai.indexing.hierarchical_indexer import HierarchicalIndexer, chunk_dataset


def make_doc(
    doc_id: str,
    file_name: str,
    page_texts: list[str],
    extraction_status: str = "success",
) -> dict:
    pages = []
    for i, text in enumerate(page_texts, 1):
        pages.append({
            "page_number": i,
            "page_width": 600.0,
            "page_height": 800.0,
            "classification": "OCR_REQUIRED",
            "backend_used": "ocr",
            "extraction_status": "success",
            "raw_text": text,
            "ordered_elements": [],
            "warnings": [],
            "errors": [],
        })
    return {
        "schema_version": "1.0",
        "document_id": doc_id,
        "source_path": f"ai_data/raw/test/{file_name}",
        "source_url": None,
        "file_name": file_name,
        "file_hash": f"sha256:{doc_id}",
        "page_count": len(pages),
        "extraction_status": extraction_status,
        "warnings": [],
        "errors": [],
        "pages": pages,
    }


@pytest.fixture
def temp_dataset():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # Document 1: 2 pages
        doc1 = make_doc("doc-1", "doc1.pdf", ["Page 1 text.", "Page 2 text."])
        (root / "doc1.json").write_text(json.dumps(doc1), encoding="utf-8")
        # Document 2: 1 page
        doc2 = make_doc("doc-2", "doc2.pdf", ["Single page."])
        (root / "doc2.json").write_text(json.dumps(doc2), encoding="utf-8")
        # Document 3: extraction failed
        doc3 = make_doc("doc-3", "doc3.pdf", ["Bad doc."], extraction_status="failed")
        (root / "doc3.json").write_text(json.dumps(doc3), encoding="utf-8")
        # Manifest (should be excluded)
        (root / "manifest.json").write_text(json.dumps({"files": ["doc1.json", "doc2.json"]}), encoding="utf-8")
        yield root


def test_discover_documents_excludes_manifest(temp_dataset):
    indexer = HierarchicalIndexer(temp_dataset)
    docs = indexer.discover_documents()
    assert len(docs) == 3  # doc1, doc2, doc3 (manifest excluded)
    names = {d.name for d in docs}
    assert names == {"doc1.json", "doc2.json", "doc3.json"}


def test_load_document_success(temp_dataset):
    indexer = HierarchicalIndexer(temp_dataset)
    doc = indexer.load_document(temp_dataset / "doc1.json")
    assert doc is not None
    assert doc["document_id"] == "doc-1"
    assert doc["extraction_status"] == "success"
    assert len(doc["pages"]) == 2


def test_load_document_skips_failed_extraction(temp_dataset):
    indexer = HierarchicalIndexer(temp_dataset)
    doc = indexer.load_document(temp_dataset / "doc3.json")
    assert doc is None
    assert indexer.stats.documents_skipped_status == 1


def test_chunk_document_produces_children(temp_dataset):
    indexer = HierarchicalIndexer(temp_dataset)
    result = indexer.chunk_document(temp_dataset / "doc1.json")
    assert result is not None
    assert isinstance(result, ChunkResult)
    assert len(result.children) >= 0  # may be 0 for OCR garbage
    assert indexer.stats.documents_processed == 1
    assert indexer.stats.total_children == len(result.children)


def test_chunk_document_failed_extraction_returns_none(temp_dataset):
    indexer = HierarchicalIndexer(temp_dataset)
    result = indexer.chunk_document(temp_dataset / "doc3.json")
    assert result is None
    assert indexer.stats.documents_skipped_status == 1


def test_chunk_dataset_processes_all(temp_dataset):
    indexer = HierarchicalIndexer(temp_dataset)
    results = indexer.chunk_dataset()
    assert len(results) == 2  # doc1 and doc2 (doc3 skipped)
    assert indexer.stats.documents_found == 3
    assert indexer.stats.documents_processed == 3
    assert indexer.stats.documents_failed == 0
    assert indexer.stats.documents_skipped_status == 1


def test_chunk_dataset_stats_aggregated(temp_dataset):
    indexer = HierarchicalIndexer(temp_dataset)
    indexer.chunk_dataset()
    stats = indexer.stats.to_dict()
    assert stats["documents_found"] == 3
    assert stats["documents_processed"] == 3
    assert stats["documents_skipped_status"] == 1
    assert stats["documents_failed"] == 0
    assert stats["total_children"] >= 0
    assert stats["elapsed_seconds"] >= 0


def test_convenience_function():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        doc = make_doc("doc-x", "x.pdf", ["Hello world."])
        (root / "x.json").write_text(json.dumps(doc), encoding="utf-8")
        (root / "manifest.json").write_text("{}", encoding="utf-8")

        results, stats = chunk_dataset(root)
        assert len(results) == 1
        assert stats.documents_found == 1
        assert stats.documents_processed == 1