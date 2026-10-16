from app.ai.chunking.technical_chunker import TechnicalDocumentChunker


def _make_document(content: str, page_count: int = 1, **kwargs):
    return {
        "document_id": "doc-1",
        "product_id": "prod-1",
        "product_name": "Lika PAP2",
        "source": "gypsobat",
        "source_url": "https://www.gypsobat.com/fiche-technique-systemes-humides/",
        "document_url": "https://www.gypsobat.com/wp-content/uploads/2024/11/fiche_technique_pap2.pdf",
        "document_type": "technical_sheet",
        "language": "fr",
        "content": content,
        "content_hash": "hash123",
        "metadata": {"page_count": page_count, "supplier": "SIPS", **kwargs},
    }


def test_chunker_returns_list():
    chunker = TechnicalDocumentChunker()
    doc = _make_document("Hello world")
    chunks = chunker.chunk(doc)
    assert isinstance(chunks, list)


def test_chunker_preserves_metadata():
    chunker = TechnicalDocumentChunker()
    content = "DOMAINE D'EMPLOI\n" + "Test content with enough characters to pass the minimum threshold for chunking. " * 5
    doc = _make_document(content)
    chunks = chunker.chunk(doc)
    assert len(chunks) > 0
    chunk = chunks[0]
    assert chunk.document_id == "doc-1"
    assert chunk.product_id == "prod-1"
    assert chunk.product_name == "Lika PAP2"
    assert chunk.source == "gypsobat"
    assert chunk.document_type == "technical_sheet"
    assert chunk.language == "fr"
    assert chunk.content_hash == "hash123"
    assert chunk.supplier == "SIPS"


def test_chunker_detects_section_title():
    chunker = TechnicalDocumentChunker()
    content = "DOMAINE D'EMPLOI\n" + "Test content here that is long enough for chunking to work properly. " * 5
    doc = _make_document(content)
    chunks = chunker.chunk(doc)
    assert len(chunks) > 0
    section_titles = [c.section_title for c in chunks if c.section_title]
    assert "DOMAINE D'EMPLOI" in section_titles


def test_chunker_splits_by_max_size():
    chunker = TechnicalDocumentChunker(max_chunk_size=100, min_chunk_size=10)
    text = "A" * 300
    doc = _make_document(text)
    chunks = chunker.chunk(doc)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c.text) <= 100


def test_chunker_handles_empty_content():
    chunker = TechnicalDocumentChunker()
    doc = _make_document("")
    chunks = chunker.chunk(doc)
    assert chunks == []


def test_chunker_handles_none_content():
    chunker = TechnicalDocumentChunker()
    doc = _make_document(None)
    chunks = chunker.chunk(doc)
    assert chunks == []


def test_chunker_assigns_chunk_index():
    chunker = TechnicalDocumentChunker(max_chunk_size=100, min_chunk_size=10)
    text = "Section A\n" + "Word " * 50 + "\n\nSection B\n" + "Word " * 50
    doc = _make_document(text)
    chunks = chunker.chunk(doc)
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))


def test_chunker_preserves_page_number():
    chunker = TechnicalDocumentChunker()
    content = "DOMAINE D'EMPLOI\n" + "Content here that is long enough for chunking to work properly. " * 5
    doc = _make_document(content, page_count=2)
    chunks = chunker.chunk(doc)
    assert len(chunks) > 0
    assert all(c.page_number == 1 for c in chunks)


def test_chunker_handles_multi_page_content():
    chunker = TechnicalDocumentChunker()
    text = "Page 1 content\nDOMAINE D'EMPLOI\nDetail here that is long enough for chunking to work properly.\n\nPage 2 content\nCARACTERISTIQUES\nValues here that are long enough for chunking to work properly."
    doc = _make_document(text, page_count=2)
    chunks = chunker.chunk(doc)
    assert len(chunks) > 0
    page_numbers = sorted(set(c.page_number for c in chunks))
    assert 1 in page_numbers


def test_chunker_generates_unique_chunk_ids():
    chunker = TechnicalDocumentChunker(max_chunk_size=100, min_chunk_size=10)
    text = "A" * 200
    doc = _make_document(text)
    chunks = chunker.chunk(doc)
    chunk_ids = [c.chunk_id for c in chunks]
    assert len(chunk_ids) == len(set(chunk_ids))


def test_chunker_includes_metadata():
    chunker = TechnicalDocumentChunker()
    content = "DOMAINE D'EMPLOI\n" + "Content here that is long enough for chunking to work properly. " * 5
    doc = _make_document(content)
    chunks = chunker.chunk(doc)
    assert len(chunks) > 0
    chunk = chunks[0]
    assert chunk.metadata is not None
    assert "char_count" in chunk.metadata
    assert "word_count" in chunk.metadata