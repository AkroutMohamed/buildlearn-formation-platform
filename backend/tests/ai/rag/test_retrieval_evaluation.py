import pytest
from unittest.mock import MagicMock, patch

from app.ai.config import ai_settings
from app.ai.rag.retriever import Retriever
from app.ai.schemas.chunk import ChunkResponse
from tests.ai.rag.evaluation_cases import CASES, get_case


def _make_qdrant_result(payload: dict[str, object], score: float = 0.9, point_id: int = 12345):
    return {
        "id": point_id,
        "score": score,
        "payload": payload,
    }


def _build_chunk_response(**kwargs) -> ChunkResponse:
    defaults = {
        "id": "chunk-001",
        "chunk_id": "chunk-001",
        "document_id": "doc-1",
        "product_id": "prod-1",
        "product_name": "Test Product",
        "supplier": "Test Supplier",
        "source": "test",
        "source_url": "https://example.com/p1",
        "document_url": "https://example.com/doc.pdf",
        "document_type": "technical_sheet",
        "page_number": 1,
        "section_title": "SECTION A",
        "chunk_index": 0,
        "text": "Test chunk text.",
        "language": "en",
        "content_hash": "hash001",
        "metadata": {},
        "source_type": "external_official",
        "discovery_provider": "manufacturer_targeted",
        "domain": "example.com",
        "confidence": "high",
        "evidence": "Found via test",
        "score": 0.95,
    }
    defaults.update(kwargs)
    return ChunkResponse(**defaults)


class TestRetrievalHitRate:
    @patch("app.ai.rag.retriever.EmbeddingProvider")
    @patch("app.ai.rag.retriever.VectorStore")
    def test_hydro_moisture_resistant_board_hit_at_3(self, mock_vector_store_cls, mock_embedding_cls):
        mock_embedding = MagicMock()
        mock_embedding.embed_single.return_value = [0.1] * 768
        mock_embedding_cls.return_value = mock_embedding

        hydro_payload = {
            "chunk_id": "hydro-1",
            "document_id": "doc-hydro",
            "product_id": "prod-hydro",
            "product_name": "BA13 Hydro",
            "supplier": "GYPROC",
            "source": "gypsobat",
            "source_url": "https://x.com/p1/",
            "document_url": "https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf",
            "document_type": "technical_sheet",
            "page_number": 1,
            "section_title": "MOISTURE RESISTANCE",
            "chunk_index": 0,
            "text": "BA13 Hydro is a moisture resistant plasterboard.",
            "language": "en",
            "content_hash": "hash-hydro",
            "metadata": {},
            "source_type": "external_official",
            "discovery_provider": "manufacturer_targeted",
            "domain": "www.gyproc.in",
            "confidence": "high",
            "evidence": "Found via gypsobat",
        }
        mock_store = MagicMock()
        mock_store.search.return_value = [_make_qdrant_result(hydro_payload, score=0.95, point_id=1)]
        mock_vector_store_cls.return_value = mock_store

        retriever = Retriever()
        results = retriever.retrieve("What is Gyproc Moisture Resistant Board?", top_k=3)

        assert len(results) >= 1
        product_names = {r.product_name for r in results}
        assert "BA13 Hydro" in product_names

    @patch("app.ai.rag.retriever.EmbeddingProvider")
    @patch("app.ai.rag.retriever.VectorStore")
    def test_fireline_board_hit_at_3(self, mock_vector_store_cls, mock_embedding_cls):
        mock_embedding = MagicMock()
        mock_embedding.embed_single.return_value = [0.1] * 768
        mock_embedding_cls.return_value = mock_embedding

        fireline_payload = {
            "chunk_id": "fireline-1",
            "document_id": "doc-fireline",
            "product_id": "prod-fireline",
            "product_name": "BA13 Feu",
            "supplier": "GYPROC",
            "source": "gypsobat",
            "source_url": "https://x.com/p2/",
            "document_url": "https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf",
            "document_type": "technical_sheet",
            "page_number": 1,
            "section_title": "FIRE RESISTANCE",
            "chunk_index": 0,
            "text": "BA13 Feu is a fire-resistant plasterboard.",
            "language": "en",
            "content_hash": "hash-fireline",
            "metadata": {},
            "source_type": "external_official",
            "discovery_provider": "manufacturer_targeted",
            "domain": "www.gyproc.in",
            "confidence": "high",
            "evidence": "Found via gypsobat",
        }
        mock_store = MagicMock()
        mock_store.search.return_value = [_make_qdrant_result(fireline_payload, score=0.95, point_id=2)]
        mock_vector_store_cls.return_value = mock_store

        retriever = Retriever()
        results = retriever.retrieve("What is Gyproc Fireline Board?", top_k=3)

        assert len(results) >= 1
        product_names = {r.product_name for r in results}
        assert "BA13 Feu" in product_names

    @patch("app.ai.rag.retriever.EmbeddingProvider")
    @patch("app.ai.rag.retriever.VectorStore")
    def test_duraline_board_hit_at_3(self, mock_vector_store_cls, mock_embedding_cls):
        mock_embedding = MagicMock()
        mock_embedding.embed_single.return_value = [0.1] * 768
        mock_embedding_cls.return_value = mock_embedding

        duraline_payload = {
            "chunk_id": "duraline-1",
            "document_id": "doc-duraline",
            "product_id": "prod-hydro",
            "product_name": "BA13 Hydro",
            "supplier": "GYPROC",
            "source": "gypsobat",
            "source_url": "https://x.com/p3/",
            "document_url": "https://www.gyproc.in/pdf/PB05_Gyproc_Duraline_Board.pdf",
            "document_type": "technical_sheet",
            "page_number": 1,
            "section_title": "DURALINE",
            "chunk_index": 0,
            "text": "Duraline is an enhanced moisture resistant board.",
            "language": "en",
            "content_hash": "hash-duraline",
            "metadata": {},
            "source_type": "external_official",
            "discovery_provider": "manufacturer_targeted",
            "domain": "www.gyproc.in",
            "confidence": "high",
            "evidence": "Found via gypsobat",
        }
        mock_store = MagicMock()
        mock_store.search.return_value = [_make_qdrant_result(duraline_payload, score=0.93, point_id=3)]
        mock_vector_store_cls.return_value = mock_store

        retriever = Retriever()
        results = retriever.retrieve("What is Gyproc Duraline Board?", top_k=3)

        assert len(results) >= 1
        product_names = {r.product_name for r in results}
        assert "BA13 Hydro" in product_names

    @patch("app.ai.rag.retriever.EmbeddingProvider")
    @patch("app.ai.rag.retriever.VectorStore")
    def test_lika_pap2_hit_at_3(self, mock_vector_store_cls, mock_embedding_cls):
        mock_embedding = MagicMock()
        mock_embedding.embed_single.return_value = [0.1] * 768
        mock_embedding_cls.return_value = mock_embedding

        lika_payload = {
            "chunk_id": "lika-1",
            "document_id": "doc-lika",
            "product_id": "prod-lika",
            "product_name": "Lika PAP2",
            "supplier": "Gypsobat",
            "source": "gypsobat",
            "source_url": "https://www.gypsobat.com/p/lika-pap2/",
            "document_url": "https://www.gypsobat.com/wp-content/uploads/2024/11/fiche_technique_pap2.pdf",
            "document_type": "technical_sheet",
            "page_number": 1,
            "section_title": "LIKA PAP2",
            "chunk_index": 0,
            "text": "Lika PAP2 is a finishing product.",
            "language": "en",
            "content_hash": "hash-lika",
            "metadata": {},
            "source_type": "external_official",
            "discovery_provider": "manufacturer_targeted",
            "domain": "www.gypsobat.com",
            "confidence": "high",
            "evidence": "Found via gypsobat",
        }
        mock_store = MagicMock()
        mock_store.search.return_value = [_make_qdrant_result(lika_payload, score=0.95, point_id=4)]
        mock_vector_store_cls.return_value = mock_store

        retriever = Retriever()
        results = retriever.retrieve("What is Lika PAP2?", top_k=3)

        assert len(results) >= 1
        product_names = {r.product_name for r in results}
        assert "Lika PAP2" in product_names

    @patch("app.ai.rag.retriever.EmbeddingProvider")
    @patch("app.ai.rag.retriever.VectorStore")
    def test_retrieval_tolerates_low_score_noise_results(self, mock_vector_store_cls, mock_embedding_cls, monkeypatch):
        monkeypatch.setattr(ai_settings, "retrieval_score_threshold", 0.3)

        mock_embedding = MagicMock()
        mock_embedding.embed_single.return_value = [0.1] * 768
        mock_embedding_cls.return_value = mock_embedding

        hydro_payload = {
            "chunk_id": "hydro-1",
            "document_id": "doc-hydro",
            "product_id": "prod-hydro",
            "product_name": "BA13 Hydro",
            "supplier": "GYPROC",
            "source": "gypsobat",
            "source_url": "https://x.com/p1/",
            "document_url": "https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf",
            "document_type": "technical_sheet",
            "page_number": 1,
            "section_title": "MOISTURE RESISTANCE",
            "chunk_index": 0,
            "text": "BA13 Hydro is a moisture resistant plasterboard.",
            "language": "en",
            "content_hash": "hash-hydro",
            "metadata": {},
            "source_type": "external_official",
            "discovery_provider": "manufacturer_targeted",
            "domain": "www.gyproc.in",
            "confidence": "high",
            "evidence": "Found via gypsobat",
        }
        noise_payload = {
            "chunk_id": "noise-1",
            "document_id": "doc-noise",
            "product_id": "prod-noise",
            "product_name": "Unrelated Product",
            "supplier": "Other",
            "source": "other",
            "source_url": "https://example.com/p1/",
            "document_url": "https://example.com/noise.pdf",
            "document_type": "technical_sheet",
            "page_number": 1,
            "section_title": "NOISE",
            "chunk_index": 0,
            "text": "Unrelated product information.",
            "language": "en",
            "content_hash": "hash-noise",
            "metadata": {},
            "source_type": "external_official",
            "discovery_provider": "manufacturer_targeted",
            "domain": "example.com",
            "confidence": "low",
            "evidence": "Noise",
        }
        mock_store = MagicMock()
        mock_store.search.return_value = [
            _make_qdrant_result(noise_payload, score=0.4, point_id=10),
            _make_qdrant_result(hydro_payload, score=0.95, point_id=1),
        ]
        mock_vector_store_cls.return_value = mock_store

        retriever = Retriever()
        results = retriever.retrieve("What is Gyproc Moisture Resistant Board?", top_k=5)

        assert len(results) == 2
        assert results[0].product_name == "BA13 Hydro"
        assert results[0].score == 0.95
        assert results[1].product_name == "Unrelated Product"
        assert results[1].score == 0.4
