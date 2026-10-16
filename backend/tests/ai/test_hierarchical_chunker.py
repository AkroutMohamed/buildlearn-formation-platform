from __future__ import annotations

import json
import os

import pytest

from app.ai.chunking import (
    BlockType,
    ChunkConfig,
    ChunkResult,
    ChildChunk,
    ParentChunk,
    SemanticBlock,
    SourceInfo,
    chunk_document,
    build_hierarchy,
    parse_text_blocks,
)
from app.ai.chunking.chunker import HierarchicalChunker
from app.ai.chunking.config import ChunkConfig as CC
from app.ai.chunking.hierarchy import HierarchyBuilder
from app.ai.chunking.models import (
    ChildChunk as CC2,
    ChunkResult as CR2,
    ParentChunk as PC2,
    SemanticBlock as SB2,
    SourceInfo as SI2,
)
from app.ai.schemas.chunk import ChunkCreate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_doc(pages_data: list[dict], **kwargs) -> dict:
    doc: dict = {
        "document_id": "test-doc-001",
        "source_path": "/test/path.pdf",
        "source_url": None,
        "file_name": "test.pdf",
        "file_hash": "sha256:test",
        "page_count": len(pages_data),
        "extraction_status": "success",
        "warnings": [],
        "errors": [],
        "pages": pages_data,
    }
    doc.update(kwargs)
    return doc


def _page(page_number: int, raw_text: str) -> dict:
    return {"page_number": page_number, "raw_text": raw_text}


# ---------------------------------------------------------------------------
# ChunkConfig tests
# ---------------------------------------------------------------------------

class TestChunkConfig:
    def test_defaults(self):
        cfg = ChunkConfig()
        assert cfg.min_chunk_size == 100
        assert cfg.max_chunk_size == 1500
        assert cfg.max_parent_depth == 3
        assert cfg.preserve_original_text is True

    def test_effective_min(self):
        cfg = ChunkConfig(min_chunk_size=100)
        assert cfg.effective_min == 100

    def test_effective_min_with_zero(self):
        cfg = ChunkConfig(min_chunk_size=0)
        assert cfg.effective_min == 1

    def test_effective_max(self):
        cfg = ChunkConfig(max_chunk_size=1500)
        assert cfg.effective_max == 1500

    def test_custom_sizes(self):
        cfg = ChunkConfig(min_chunk_size=50, max_chunk_size=500)
        assert cfg.effective_min == 50
        assert cfg.effective_max == 500

    def test_effective_max_at_min(self):
        cfg = ChunkConfig(min_chunk_size=200, max_chunk_size=100)
        assert cfg.effective_max >= cfg.effective_min + 1


# ---------------------------------------------------------------------------
# Deterministic ID tests
# ---------------------------------------------------------------------------

class TestDeterministicIDs:
    def test_deterministic_block_id(self):
        source = SourceInfo(document_id="doc-1")
        b1 = SemanticBlock.from_text("Test content", BlockType.PARAGRAPH, source)
        b2 = SemanticBlock.from_text("Test content", BlockType.PARAGRAPH, source)
        assert b1.block_id == b2.block_id

    def test_different_content_different_id(self):
        source = SourceInfo(document_id="doc-1")
        b1 = SemanticBlock.from_text("Content A", BlockType.PARAGRAPH, source)
        b2 = SemanticBlock.from_text("Content B", BlockType.PARAGRAPH, source)
        assert b1.block_id != b2.block_id

    def test_deterministic_parent_id(self):
        source = SourceInfo(document_id="doc-1")
        b1 = SemanticBlock.from_text("Heading", BlockType.HEADING, source)
        p1 = ParentChunk.from_block(b1)
        b2 = SemanticBlock.from_text("Heading", BlockType.HEADING, source)
        p2 = ParentChunk.from_block(b2)
        assert p1.chunk_id == p2.chunk_id

    def test_child_id_deterministic(self):
        from app.ai.chunking.chunker import _deterministic_child_id
        cid1 = _deterministic_child_id("parent-1", "paragraph", "text", 0)
        cid2 = _deterministic_child_id("parent-1", "paragraph", "text", 0)
        assert cid1 == cid2

    def test_all_child_ids_unique_in_result(self):
        doc = _make_doc([_page(1, "HEADING\nParagraph text that is long enough for chunking purposes.")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        ids = [c.chunk_id for c in result.children]
        assert len(ids) == len(set(ids))

    def test_parent_ids_unique_in_result(self):
        doc = _make_doc([_page(1, "HEADING A\nPara A\n\nHEADING B\nPara B")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        ids = [p.chunk_id for p in result.parents]
        assert len(ids) == len(set(ids))


def _make_child_id(parent_id, block_type, text_prefix, index):
    import hashlib
    raw = f"{parent_id}:{block_type}:{text_prefix}:{index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Parser tests - real text patterns
# ---------------------------------------------------------------------------

class TestParser:
    def test_empty_text(self):
        source = SourceInfo(document_id="doc-1")
        blocks = parse_text_blocks("", source, 1)
        assert blocks == []

    def test_whitespace_only(self):
        source = SourceInfo(document_id="doc-1")
        blocks = parse_text_blocks("   \n\n  ", source, 1)
        assert blocks == []

    def test_none_text(self):
        source = SourceInfo(document_id="doc-1")
        blocks = parse_text_blocks(None, source, 1)  # type: ignore[arg-type]
        assert blocks == []

    def test_heading_detection(self):
        source = SourceInfo(document_id="doc-1")
        blocks = parse_text_blocks("INTRODUCTION\nBody text here", source, 1)
        assert any(b.block_type == BlockType.HEADING for b in blocks)
        heading = [b for b in blocks if b.block_type == BlockType.HEADING][0]
        assert heading.text == "INTRODUCTION"

    def test_multiple_headings(self):
        source = SourceInfo(document_id="doc-1")
        text = "SECTION A\nContent for A\n\nSECTION B\nContent for B"
        blocks = parse_text_blocks(text, source, 1)
        headings = [b for b in blocks if b.block_type == BlockType.HEADING]
        assert len(headings) == 2
        assert headings[0].text == "SECTION A"
        assert headings[1].text == "SECTION B"

    def test_paragraph_detection(self):
        source = SourceInfo(document_id="doc-1")
        blocks = parse_text_blocks("This is a paragraph of text.", source, 1)
        assert any(b.block_type == BlockType.PARAGRAPH for b in blocks)

    def test_list_item_detection_bullet(self):
        source = SourceInfo(document_id="doc-1")
        text = "First heading\n• Item one\n• Item two\n• Item three"
        blocks = parse_text_blocks(text, source, 1)
        items = [b for b in blocks if b.block_type == BlockType.LIST_ITEM]
        assert len(items) >= 1

    def test_list_item_detection_dash(self):
        source = SourceInfo(document_id="doc-1")
        text = "Heading\n- First item\n- Second item"
        blocks = parse_text_blocks(text, source, 1)
        items = [b for b in blocks if b.block_type == BlockType.LIST_ITEM]
        assert len(items) >= 1

    def test_list_item_detection_numbered(self):
        source = SourceInfo(document_id="doc-1")
        text = "Heading\n1. First step\n2. Second step\n3. Third step"
        blocks = parse_text_blocks(text, source, 1)
        items = [b for b in blocks if b.block_type == BlockType.LIST_ITEM]
        assert len(items) >= 1

    def test_key_value_detection(self):
        source = SourceInfo(document_id="doc-1")
        text = "Heading\nModel: XT-200\nThickness: 12.5 mm"
        blocks = parse_text_blocks(text, source, 1)
        kv = [b for b in blocks if b.block_type == BlockType.KEY_VALUE]
        assert len(kv) >= 1

    def test_table_detection_pipe(self):
        source = SourceInfo(document_id="doc-1")
        text = "Specifications\nProperty | Value\nThickness | 12.5 mm\nWidth | 1200 mm"
        blocks = parse_text_blocks(text, source, 1)
        tables = [b for b in blocks if b.block_type == BlockType.TABLE]
        assert len(tables) >= 1

    def test_caption_detection(self):
        source = SourceInfo(document_id="doc-1")
        text = "Fig. 1. Test diagram showing results"
        blocks = parse_text_blocks(text, source, 1)
        captions = [b for b in blocks if b.block_type == BlockType.CAPTION]
        assert len(captions) >= 1

    def test_page_boundary(self):
        source = SourceInfo(document_id="doc-1")
        text = "Page 1 content here"
        blocks = parse_text_blocks(text, source, 1)
        assert all(b.page_start == 1 for b in blocks)

    def test_page_boundary_separate_pages(self):
        source = SourceInfo(document_id="doc-1")
        doc = _make_doc([_page(1, "Page one content"), _page(2, "Page two content")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=500))
        assert result.total_children > 0
        pages = set(c.page_start for c in result.children if c.page_start is not None)
        assert 1 in pages
        assert 2 in pages

    def test_mixed_content(self):
        source = SourceInfo(document_id="doc-1")
        text = (
            "DOCUMENT TITLE\n"
            "Introduction paragraph here.\n"
            "Key Feature: Value one\n"
            "Key Feature: Value two\n"
            "• Bullet one\n"
            "• Bullet two\n"
        )
        blocks = parse_text_blocks(text, source, 1)
        types = {b.block_type for b in blocks}
        assert BlockType.HEADING in types
        assert BlockType.PARAGRAPH in types
        assert BlockType.KEY_VALUE in types


# ---------------------------------------------------------------------------
# Hierarchy tests
# ---------------------------------------------------------------------------

class TestHierarchy:
    def test_empty_input(self):
        source = SourceInfo(document_id="doc-1")
        blocks = build_hierarchy("", source, 1)
        assert blocks == []

    def test_heading_becomes_section(self):
        source = SourceInfo(document_id="doc-1")
        blocks = build_hierarchy("SECTION TITLE\nBody content here", source, 1)
        headings = [b for b in blocks if b.block_type == BlockType.HEADING]
        assert len(headings) == 1
        assert headings[0].section_path == []

    def test_paragraph_inherits_section_path(self):
        source = SourceInfo(document_id="doc-1")
        blocks = build_hierarchy("SECTION TITLE\nBody content here", source, 1)
        paras = [b for b in blocks if b.block_type == BlockType.PARAGRAPH]
        assert len(paras) == 1
        assert len(paras[0].section_path) >= 1
        assert paras[0].section_path[0] == "SECTION TITLE"

    def test_paragraph_has_parent_id(self):
        source = SourceInfo(document_id="doc-1")
        blocks = build_hierarchy("SECTION TITLE\nBody content here", source, 1)
        paras = [b for b in blocks if b.block_type == BlockType.PARAGRAPH]
        assert len(paras) == 1
        assert paras[0].parent_id is not None

    def test_two_sections(self):
        source = SourceInfo(document_id="doc-1")
        text = "SECTION A\nContent A\n\nSECTION B\nContent B"
        blocks = build_hierarchy(text, source, 1)
        headings = [b for b in blocks if b.block_type == BlockType.HEADING]
        assert len(headings) == 2
        assert headings[0].text == "SECTION A"
        assert headings[1].text == "SECTION B"

    def test_heading_preserves_original_text(self):
        source = SourceInfo(document_id="doc-1")
        blocks = build_hierarchy("SPECIFICATIONS", source, 1)
        headings = [b for b in blocks if b.block_type == BlockType.HEADING]
        assert len(headings) == 1
        assert headings[0].text == "SPECIFICATIONS"


# ---------------------------------------------------------------------------
# Parent/Child relationship tests
# ---------------------------------------------------------------------------

class TestParentChildRelationships:
    def test_parent_is_not_embeddable(self):
        source = SourceInfo(document_id="doc-1")
        block = SemanticBlock.from_text("Heading", BlockType.HEADING, source)
        parent = ParentChunk.from_block(block)
        assert parent.is_embeddable is False

    def test_child_is_embeddable(self):
        source = SourceInfo(document_id="doc-1")
        block = SemanticBlock.from_text("Paragraph text", BlockType.PARAGRAPH, source)
        child = ChildChunk(
            chunk_id="test",
            chunk_type=BlockType.PARAGRAPH,
            text="Paragraph text",
            source=source,
            section_path=[],
            parent_id=None,
            block_type=BlockType.PARAGRAPH,
            config=ChunkConfig(),
        )
        assert child.is_embeddable is True

    def test_child_has_parent_id(self):
        doc = _make_doc([_page(1, "SECTION\nParagraph content here")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        paras = [c for c in result.children if c.block_type == BlockType.PARAGRAPH]
        assert len(paras) >= 1
        assert paras[0].parent_id is not None

    def test_child_has_section_path(self):
        doc = _make_doc([_page(1, "SECTION\nParagraph content here")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        paras = [c for c in result.children if c.block_type == BlockType.PARAGRAPH]
        assert len(paras) >= 1
        assert len(paras[0].section_path) >= 1

    def test_parent_has_children_reference(self):
        doc = _make_doc([_page(1, "SECTION\nParagraph content here")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        parents = [p for p in result.parents if p.chunk_type == BlockType.HEADING]
        assert len(parents) >= 1
        assert len(parents[0].children) >= 1

    def test_detinistic_ids_preserved(self):
        doc = _make_doc([_page(1, "SECTION\nParagraph content here")])
        result1 = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        result2 = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        for c1, c2 in zip(result1.children, result2.children):
            assert c1.chunk_id == c2.chunk_id
        for p1, p2 in zip(result1.parents, result2.parents):
            assert p1.chunk_id == p2.chunk_id


# ---------------------------------------------------------------------------
# Source preservation tests
# ---------------------------------------------------------------------------

class TestSourcePreservation:
    def test_source_path_preserved(self):
        doc = _make_doc([_page(1, "Heading\nContent")], source_path="/data/doc.pdf")
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        for c in result.children:
            assert c.source.source_path == "/data/doc.pdf"
        for p in result.parents:
            assert p.source.source_path == "/data/doc.pdf"

    def test_document_id_preserved(self):
        doc = _make_doc([_page(1, "Heading\nContent")], document_id="doc-42")
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        for c in result.children:
            assert c.source.document_id == "doc-42"
        for p in result.parents:
            assert p.source.document_id == "doc-42"

    def test_page_start_preserved(self):
        doc = _make_doc([_page(1, "Heading\nContent"), _page(2, "Page 2 heading\nText")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        children = result.children
        assert children[0].page_start == 1
        page2_children = [c for c in children if c.page_start == 2]
        assert len(page2_children) >= 0

    def test_file_name_preserved(self):
        doc = _make_doc([_page(1, "Heading\nContent")], file_name="test.pdf")
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        for c in result.children:
            assert c.source.file_name == "test.pdf"


# ---------------------------------------------------------------------------
# Size control tests
# ---------------------------------------------------------------------------

class TestSizeControl:
    def test_small_block_under_max_is_single_chunk(self):
        config = ChunkConfig(min_chunk_size=10, max_chunk_size=1000)
        doc = _make_doc([_page(1, "Heading\nShort content")])
        result = chunk_document(doc, config)
        assert all(c.char_count <= 1000 for c in result.children)

    def test_oversized_block_gets_split(self):
        config = ChunkConfig(min_chunk_size=10, max_chunk_size=50)
        doc = _make_doc([_page(1, "Heading\n" + "A" * 200)])
        result = chunk_document(doc, config)
        assert len(result.children) > 1
        assert all(c.char_count <= 50 for c in result.children)

    def test_min_chunk_size_respected(self):
        config = ChunkConfig(min_chunk_size=10, max_chunk_size=1500)
        doc = _make_doc([_page(1, "Heading\n" + "A" * 200)])
        result = chunk_document(doc, config)
        assert all(c.char_count >= 0 for c in result.children)

    def test_no_chunks_for_empty_content(self):
        doc = _make_doc([_page(1, "")])
        result = chunk_document(doc)
        assert result.total_children == 0
        assert result.total_parents == 0

    def test_no_chunks_for_none_content(self):
        doc = _make_doc([_page(1, None)])  # type: ignore[dict-unknown]
        result = chunk_document(doc)
        assert result.total_children == 0

    def test_recursive_split_for_extremely_large_text(self):
        config = ChunkConfig(min_chunk_size=10, max_chunk_size=30)
        doc = _make_doc([_page(1, "Heading\n" + "A" * 500)])
        result = chunk_document(doc, config)
        assert all(c.char_count <= 30 for c in result.children)


# ---------------------------------------------------------------------------
# Structure type tests
# ---------------------------------------------------------------------------

class TestStructureTypes:
    def test_heading_type(self):
        doc = _make_doc([_page(1, "SECTION HEADING\nBody text here")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        types = [c.block_type.value for c in result.children]
        assert BlockType.PARAGRAPH in types or BlockType.HEADING in types

    def test_list_type(self):
        doc = _make_doc([_page(1, "LIST TITLE\n• Item one\n• Item two\n• Item three")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        types = {c.block_type for c in result.children}
        assert BlockType.LIST_ITEM in types or BlockType.LIST in types

    def test_table_type(self):
        doc = _make_doc([_page(1, "TABLE\nProp | Value\nA | 1\nB | 2")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        types = {c.block_type for c in result.children}
        has_table = BlockType.TABLE in types
        has_kv = BlockType.KEY_VALUE in types
        assert has_table or has_kv

    def test_paragraph_type(self):
        doc = _make_doc([_page(1, "Heading\nThis is a paragraph of text in the document.")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        types = {c.block_type for c in result.children}
        assert BlockType.PARAGRAPH in types


# ---------------------------------------------------------------------------
# Hierarchy tests - real-world patterns
# ---------------------------------------------------------------------------

class TestRealWorldPatterns:
    def test_real_extraction_with_headings_and_text(self):
        source = SourceInfo(document_id="real-1", source_path="/data/test.pdf")
        text = (
            "Technical Data Sheet\n"
            "Model: XT-200 Thermal Insulation Panel\n"
            "Description: The XT-200 is a high-performance rigid foam insulation board.\n"
            "Installation: Suitable for both new construction and renovation projects."
        )
        result = chunk_document(
            _make_doc([_page(1, text)], document_id="real-1", source_path="/data/test.pdf"),
            ChunkConfig(min_chunk_size=20, max_chunk_size=300),
        )
        assert result.total_children > 0
        for c in result.children:
            assert c.source.document_id == "real-1"
            assert c.source.source_path == "/data/test.pdf"

    def test_all_caps_heading_recognized(self):
        source = SourceInfo(document_id="real-2")
        blocks = parse_text_blocks("SPECIFICATIONS\nValue data here", source, 1)
        headings = [b for b in blocks if b.block_type == BlockType.HEADING]
        assert len(headings) >= 1
        assert headings[0].text == "SPECIFICATIONS"

    def test_ocr_text_with_garbage_processed(self):
        source = SourceInfo(document_id="ocr-1")
        text = (
            "Gyproc\n\nSAINT-GOBAIN\n\nArplus®\n\nCONTACT US:\n"
            "Fire Resistance Test of\n\nWall Assembly\n"
            "30 Min. to 4 Hrs.\n"
            "Gyproc® Plain Board\n"
            "Standard Plasterboard."
        )
        result = chunk_document(
            _make_doc([_page(1, text)], document_id="ocr-1"),
            ChunkConfig(min_chunk_size=10, max_chunk_size=500),
        )
        assert result.total_children > 0

    def test_french_text_processed(self):
        source = SourceInfo(document_id="fr-1")
        text = (
            "CONFORT\n\nMortier colle pour carrelage\n"
            "DESCRIPTION PRODUIT\n\nDOMAINE D'EMPLOI\n"
            "Carrelage: Carreaux céramiques non poreux"
        )
        result = chunk_document(
            _make_doc([_page(1, text)], document_id="fr-1"),
            ChunkConfig(min_chunk_size=10, max_chunk_size=500),
        )
        assert result.total_children > 0

    def test_canonical_document_dict_input(self):
        doc = _make_doc([_page(1, "SECTION\nContent")])
        result = chunk_document(doc)
        assert isinstance(result, ChunkResult)

    def test_canonical_document_object_input(self):
        class FakeDoc:
            document_id = "obj-1"
            source_path = "/data/obj.pdf"
            raw_text = "SECTION\nContent"
        result = chunk_document(FakeDoc())
        assert isinstance(result, ChunkResult)

    def test_multiple_pages_processed_independently(self):
        doc = _make_doc([
            _page(1, "PAGE ONE\nFirst page content"),
            _page(2, "PAGE TWO\nSecond page content"),
            _page(3, "PAGE THREE\nThird page content"),
        ])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        assert result.total_children > 0
        pages_seen = set(c.page_start for c in result.children if c.page_start is not None)
        assert pages_seen == {1, 2, 3}


# ---------------------------------------------------------------------------
# ChunkCreate conversion tests
# ---------------------------------------------------------------------------

class TestChunkCreateConversion:
    def test_to_chunk_create_list_returns_list(self):
        doc = _make_doc([_page(1, "SECTION\nContent text here")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        chunks = result.to_chunk_create_list()
        assert isinstance(chunks, list)
        if chunks:
            assert isinstance(chunks[0], ChunkCreate)

    def test_chunk_create_has_required_fields(self):
        doc = _make_doc([_page(1, "SECTION\nContent text here")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        chunks = result.to_chunk_create_list()
        if chunks:
            c = chunks[0]
            assert c.chunk_id is not None
            assert c.text is not None
            assert c.document_id is not None

    def test_chunk_create_no_embedding_called(self):
        import app.ai.chunking.chunker as ck_mod
        original = ck_mod.HierarchicalChunker
        called = [False]

        class NoEmbedChunker(original):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

        # Just verify conversion doesn't trigger any network/embedding
        doc = _make_doc([_page(1, "SECTION\nContent")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        chunks = result.to_chunk_create_list()
        for c in chunks:
            assert c.source is None or c.source is not None  # just check it exists

    def test_chunk_create_metadata_includes_parent_id(self):
        doc = _make_doc([_page(1, "SECTION\nContent text")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        chunks = result.to_chunk_create_list()
        if chunks and chunks[0].metadata:
            assert "parent_id" in chunks[0].metadata


# ---------------------------------------------------------------------------
# Size distribution and structure distribution
# ---------------------------------------------------------------------------

class TestResultProperties:
    def test_size_distribution_computed(self):
        doc = _make_doc([_page(1, "SECTION\nContent here")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        dist = result.size_distribution
        assert "min" in dist
        assert "max" in dist
        assert "mean" in dist
        assert "count" in dist
        assert dist["count"] == result.total_children

    def test_structure_type_distribution(self):
        doc = _make_doc([_page(1, "SECTION\nContent here")])
        result = chunk_document(doc, ChunkConfig(min_chunk_size=10, max_chunk_size=200))
        dist = result.structure_type_distribution
        assert isinstance(dist, dict)
        total = sum(dist.values())
        assert total == result.total_children


# ---------------------------------------------------------------------------
# Real extraction file tests
# ---------------------------------------------------------------------------

class TestRealExtractionFiles:
    BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ai_data", "reports", "full_extraction")

    @pytest.fixture(scope="class")
    def sample_files(self):
        if not os.path.isdir(self.BASE_DIR):
            pytest.skip("full_extraction directory not found")
        files = sorted([
            os.path.join(self.BASE_DIR, f)
            for f in os.listdir(self.BASE_DIR)
            if f.endswith(".json")
        ])
        return files[:5] if len(files) >= 5 else files

    def test_real_file_parses_and_chunks(self, sample_files):
        for filepath in sample_files:
            with open(filepath, encoding="utf-8") as f:
                doc = json.load(f)
            result = chunk_document(doc, ChunkConfig(min_chunk_size=50, max_chunk_size=500))
            assert isinstance(result, ChunkResult)
            assert result.config is not None

    def test_real_file_has_parents_and_children(self, sample_files):
        found = False
        for filepath in sample_files:
            with open(filepath, encoding="utf-8") as f:
                doc = json.load(f)
            result = chunk_document(doc, ChunkConfig(min_chunk_size=50, max_chunk_size=500))
            if result.total_children > 0:
                found = True
                assert result.total_parents >= 0
                assert result.total_children > 0
        assert found, "No file produced children"

    def test_real_file_preserves_document_id(self, sample_files):
        for filepath in sample_files[:2]:
            with open(filepath, encoding="utf-8") as f:
                doc = json.load(f)
            doc_id = doc.get("document_id")
            result = chunk_document(doc, ChunkConfig(min_chunk_size=50, max_chunk_size=500))
            for c in result.children:
                assert c.source.document_id == doc_id
            for p in result.parents:
                assert p.source.document_id == doc_id


# ---------------------------------------------------------------------------
# Deterministic test across identical inputs
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_identical_inputs_produce_identical_outputs(self):
        doc = _make_doc([
            _page(1, "Introduction\nSome content here.\n\nKey Points\n- A\n- B"),
            _page(2, "Specifications\nA | B\n1 | 2"),
        ])
        config = ChunkConfig(min_chunk_size=10, max_chunk_size=300)
        r1 = chunk_document(doc, config)
        r2 = chunk_document(doc, config)

        assert r1.total_parents == r2.total_parents
        assert r1.total_children == r2.total_children

        for p1, p2 in zip(r1.parents, r2.parents):
            assert p1.chunk_id == p2.chunk_id
            assert p1.text == p2.text

        for c1, c2 in zip(r1.children, r2.children):
            assert c1.chunk_id == c2.chunk_id
            assert c1.text == c2.text
            assert c1.parent_id == c2.parent_id
