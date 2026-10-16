from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.ai.acquisition.external_search import SearchCandidate
from app.ai.acquisition.pipeline import AcquisitionPipeline, PipelineResult
from app.ai.acquisition.deduplicator import DocumentDeduplicator, DocumentRecord
from app.ai.acquisition.validator import DocumentValidator, ValidationResult
from app.ai.acquisition.classifier import DocumentClassifier
from app.ai.schemas.product import ProductCreate


def _make_product(name: str = "Test Product", url: str = "https://example.com/p1/", brand: str = "EMTOP"):
    return ProductCreate(
        product_id="1",
        name=name,
        brand=brand,
        manufacturer=brand,
        source_url=url,
        scraped_at=datetime.now(timezone.utc),
    )


def _make_product_dict_with_docs(name: str, docs: list[dict] | None = None):
    return {
        "product_id": "1",
        "name": name,
        "brand": "EMTOP",
        "manufacturer": "EMTOP",
        "source_url": f"https://example.com/{name}",
        "documents": docs or [],
    }


class TestPipelineInit:
    def test_init_default_components(self):
        pipeline = AcquisitionPipeline()
        assert isinstance(pipeline.validator, DocumentValidator)
        assert isinstance(pipeline.deduplicator, DocumentDeduplicator)
        assert pipeline.embedding_provider is None
        assert pipeline.vector_store is None

    def test_init_with_injected_components(self):
        mock_dedup = MagicMock(spec=DocumentDeduplicator)
        pipeline = AcquisitionPipeline(deduplicator=mock_dedup)
        assert pipeline.deduplicator is mock_dedup


class TestProcessBrandProducts:
    def test_process_valid_document_creates_record(self):
        validator = MagicMock(spec=DocumentValidator)
        validator.validate_and_download.return_value = ValidationResult(
            document_url="https://x.com/d.pdf",
            http_status=200,
            content_type="application/pdf",
            is_pdf=True,
            downloadable=True,
            content_hash="abc123",
            file_path="/tmp/d.pdf",
        )
        pipeline = AcquisitionPipeline(validator=validator)

        products = [_make_product_dict_with_docs("Plaque", docs=[{
            "document_url": "https://x.com/d.pdf",
            "product_name": "Plaque",
            "source": "gypsobat",
            "source_url": "https://gypsobat.fr/p/",
            "document_type": "technical_sheet",
        }])]

        result = pipeline._process_brand_products(products, "gypsobat", {"manufacturer": "Gypsobat"})

        records = result["records"]
        assert len(records) == 1
        assert records[0].document_url == "https://x.com/d.pdf"
        assert records[0].product_name == "Plaque"
        assert records[0].is_pdf is True
        assert records[0].downloadable is True
        assert records[0].content_hash == "abc123"

    def test_process_skips_products_without_docs(self):
        validator = MagicMock(spec=DocumentValidator)
        pipeline = AcquisitionPipeline(validator=validator)

        products = [_make_product_dict_with_docs("No Docs Product")]
        result = pipeline._process_brand_products(products, "gypsobat", {})

        assert len(result["records"]) == 0
        validator.validate_and_download.assert_not_called()

    def test_process_broken_document_creates_record(self):
        validator = MagicMock(spec=DocumentValidator)
        validator.validate_and_download.return_value = ValidationResult(
            document_url="https://x.com/broken.pdf",
            http_status=404,
            is_pdf=False,
            downloadable=False,
            error="HTTP 404",
        )
        pipeline = AcquisitionPipeline(validator=validator)

        products = [_make_product_dict_with_docs("Broken", docs=[{
            "document_url": "https://x.com/broken.pdf",
            "product_name": "Broken",
            "source": "gypsobat",
            "source_url": "",
        }])]

        result = pipeline._process_brand_products(products, "gypsobat", {})

        assert len(result["records"]) == 1
        assert result["records"][0].is_pdf is False
        assert result["records"][0].validation_error == "HTTP 404"


class TestHandleMissingDocuments:
    def test_product_with_valid_doc_not_missing(self):
        pipeline = AcquisitionPipeline()
        products = [{"name": "P1", "documents": [{"document_url": "https://x.com/d.pdf"}], "source_url": "https://x.com/p1/"}]
        record = DocumentRecord(
            document_url="https://x.com/d.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=True,
            text_extractable=True,
            processed=True,
            content_hash="h1",
            confidence="high",
        )
        pipeline.deduplicator.register(record)

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {})
        assert len(missing) == 0

    def test_product_without_docs_is_missing(self):
        pipeline = AcquisitionPipeline()
        products = [{"name": "P1", "documents": [], "source_url": "https://x.com/p1/"}]

        missing, _ = pipeline._handle_missing_documents(products, [], "gypsobat", {})

        assert len(missing) == 1
        assert missing[0].product_name == "P1"
        assert missing[0].status == "not_found"
        assert missing[0].missing_type == "technical_document"

    def test_product_with_broken_doc_is_missing(self):
        pipeline = AcquisitionPipeline()
        products = [{"name": "P1", "documents": [{"document_url": "https://x.com/broken.pdf"}], "source_url": "https://x.com/p1/"}]
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {})

        assert len(missing) == 1
        assert missing[0].status == "broken_link"

    def test_broken_doc_triggers_external_search(self):
        external_searcher = MagicMock()
        external_searcher.search.return_value = []
        pipeline = AcquisitionPipeline(external_searcher=external_searcher)
        products = [{"name": "P1", "documents": [{"document_url": "https://x.com/broken.pdf"}], "source_url": "https://x.com/p1/"}]
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {})

        assert len(missing) == 1
        assert missing[0].external_search_attempted is True
        external_searcher.search.assert_called()

    def test_no_external_search_when_searcher_is_none(self):
        pipeline = AcquisitionPipeline(external_searcher=None)
        products = [{"name": "P1", "documents": [{"document_url": "https://x.com/broken.pdf"}], "source_url": "https://x.com/p1/"}]
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {})

        assert len(missing) == 1
        assert missing[0].external_search_attempted is False

    def test_manufacturer_passed_to_external_search(self):
        external_searcher = MagicMock()
        external_searcher.search.return_value = []
        pipeline = AcquisitionPipeline(external_searcher=external_searcher)
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {"manufacturer": "Gypsobat"})

        assert len(missing) == 1
        assert missing[0].external_search_attempted is True
        all_query_text = " ".join(call.args[0] for call in external_searcher.search.call_args_list)
        assert "GYPROC" in all_query_text

    def test_external_candidate_retains_provenance(self):
        from app.ai.acquisition.external_search import SearchCandidate
        external_searcher = MagicMock()
        candidate = SearchCandidate(
            title="GYPROC BA13 Hydro Datasheet",
            url="https://gyproc.com/doc.pdf",
            domain="gyproc.com",
            source_type="external_official",
            confidence="high",
            evidence="Official domain",
            product_name="BA13 Hydro",
        )
        external_searcher.search.side_effect = [
            [candidate],
            [],
            [],
            [],
            [],
        ]
        pipeline = AcquisitionPipeline(external_searcher=external_searcher)
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {"manufacturer": "Gypsobat"})

        assert len(missing) == 1
        assert len(missing[0].external_candidates) == 1
        cand = missing[0].external_candidates[0]
        assert cand["source_type"] == "external_official"
        assert cand["url"] == "https://gyproc.com/doc.pdf"
        assert cand["domain"] == "gyproc.com"
        assert missing[0].original_document_url == "https://x.com/broken.pdf"

    def test_fallback_searcher_invoked_when_primary_blocked(self):
        primary_searcher = MagicMock()
        primary_searcher.search.return_value = []
        primary_searcher.provider_status = "blocked"

        fallback_searcher = MagicMock()
        fallback_candidate = SearchCandidate(
            title="Fallback Doc",
            url="https://gyproc.com/fallback.pdf",
            domain="gyproc.com",
            source_type="external_official",
            confidence="high",
            evidence="Fallback",
            product_name="BA13 Hydro",
            discovery_provider="manufacturer_targeted",
        )
        fallback_searcher.search.side_effect = [[fallback_candidate]] + [[] for _ in range(5)]

        def factory(manufacturer, product_name, model):
            return fallback_searcher

        pipeline = AcquisitionPipeline(
            external_searcher=primary_searcher,
            fallback_searcher_factory=factory,
        )
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {"manufacturer": "Gypsobat"})

        assert len(missing) == 1
        assert missing[0].external_search_attempted is True
        assert len(missing[0].external_candidates) == 1
        assert missing[0].external_candidates[0]["discovery_provider"] == "manufacturer_targeted"
        fallback_searcher.search.assert_called()

    def test_fallback_searcher_not_invoked_when_candidates_exist(self):
        primary_searcher = MagicMock()
        primary_searcher.provider_status = "ok"
        candidate = SearchCandidate(
            title="Primary Doc",
            url="https://primary.com/doc.pdf",
            domain="primary.com",
            source_type="external_official",
            confidence="high",
            evidence="Primary",
        )
        primary_searcher.search.side_effect = [[candidate]] + [[] for _ in range(5)]

        fallback_searcher = MagicMock()

        def factory(manufacturer, product_name, model):
            return fallback_searcher

        pipeline = AcquisitionPipeline(
            external_searcher=primary_searcher,
            fallback_searcher_factory=factory,
        )
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {"manufacturer": "Gypsobat"})

        assert len(missing) == 1
        assert len(missing[0].external_candidates) == 1
        fallback_searcher.search.assert_not_called()

    def test_fallback_searcher_receives_manufacturer(self):
        primary_searcher = MagicMock()
        primary_searcher.provider_status = "blocked"
        primary_searcher.search.return_value = []

        fallback_searcher = MagicMock()
        fallback_searcher.search.return_value = []

        def factory(manufacturer, product_name, model):
            assert manufacturer == "GYPROC"
            assert product_name == "BA13 Hydro"
            return fallback_searcher

        pipeline = AcquisitionPipeline(
            external_searcher=primary_searcher,
            fallback_searcher_factory=factory,
        )
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {"manufacturer": "Gypsobat"})
        assert len(missing) == 1
        fallback_searcher.search.assert_called()

    def test_skip_external_search_disables_both_providers(self):
        pipeline = AcquisitionPipeline(external_searcher=None, fallback_searcher_factory=lambda m, p, model: None)
        products = [{"name": "P1", "documents": [{"document_url": "https://x.com/broken.pdf"}], "source_url": "https://x.com/p1/"}]
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {})

        assert len(missing) == 1
        assert missing[0].external_search_attempted is False

    def test_provider_failure_does_not_crash_acquisition(self):
        primary_searcher = MagicMock()
        primary_searcher.provider_status = "blocked"
        primary_searcher.search.side_effect = RuntimeError("Unexpected error")

        pipeline = AcquisitionPipeline(external_searcher=primary_searcher)
        products = [{"name": "P1", "documents": [{"document_url": "https://x.com/broken.pdf"}], "source_url": "https://x.com/p1/"}]
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

        missing, _ = pipeline._handle_missing_documents(products, [record], "gypsobat", {})

        assert len(missing) == 1
        assert missing[0].external_search_attempted is True


class TestPipelineRun:
    def test_run_with_mocked_scrapers(self):
        mock_scraper = MagicMock()
        mock_scraper.source = "gypsobat"
        mock_scraper.discover_products.return_value = [{"id": "1", "url": "https://gypsobat.fr/p1/"}]

        mock_product = _make_product("Test Product", "https://gypsobat.fr/p1/", "Gypsobat")
        mock_scraper.scrape_product.return_value = mock_product
        mock_scraper.discover_documents.return_value = [{
            "document_url": "https://gypsobat.fr/doc.pdf",
            "product_name": "Test Product",
            "source": "gypsobat",
            "source_url": "https://gypsobat.fr/p1/",
            "document_type": "technical_sheet",
        }]

        validator = MagicMock(spec=DocumentValidator)
        validator.validate_and_download.return_value = ValidationResult(
            document_url="https://gypsobat.fr/doc.pdf",
            http_status=200,
            content_type="application/pdf",
            is_pdf=True,
            downloadable=True,
            content_hash="abc123",
            file_path=None,
        )

        pipeline = AcquisitionPipeline(validator=validator)

        with patch("app.ai.scraping.registry.get_scraper", return_value=mock_scraper):
            with patch.object(pipeline, "_process_document_content"):
                with patch.object(pipeline, "_index_documents"):
                    result = pipeline.run(brands=["gypsobat"])

        assert isinstance(result, PipelineResult)
        assert "gypsobat" in result.products_by_brand
        assert len(result.products_by_brand["gypsobat"]) == 1
        assert result.stats["total_products"] == 1


class TestPipelineOutput:
    def test_write_missing_documents(self, tmp_path):
        pipeline = AcquisitionPipeline()
        from app.ai.acquisition.registry_builder import MissingItem
        pipeline.registry.add_item(MissingItem(
            product_name="Missing Product",
            brand="gypsobat",
            product_url="https://gypsobat.fr/p/",
            missing_type="technical_document",
            original_source="https://gypsobat.fr/p/",
            original_document_url="",
            status="not_found",
            external_search_attempted=False,
        ))

        path = pipeline.registry.save(path=str(tmp_path / "missing_documents.json"))
        assert Path(path).exists()
        import json
        data = json.loads(Path(path).read_text())
        assert data["total_missing"] == 1
        assert data["items"][0]["product_name"] == "Missing Product"

    def test_write_dataset_manifest(self, tmp_path):
        pipeline = AcquisitionPipeline()
        record = DocumentRecord(
            document_url="https://gypsobat.fr/d.pdf",
            source="gypsobat",
            source_type="official",
            is_pdf=True,
            downloadable=True,
            text_extractable=True,
            processed=True,
            content_hash="h1",
            confidence="high",
            indexed=True,
            chunk_count=3,
            page_count=5,
        )
        pipeline.manifest.build_from_records(
            brand="gypsobat",
            total_products=1,
            products=[{"name": "P1", "documents": [{"document_url": "https://gypsobat.fr/d.pdf"}]}],
            records=[record],
            deduplicator=pipeline.deduplicator,
        )

        path = pipeline.manifest.save(path=str(tmp_path / "dataset_manifest.json"))
        assert Path(path).exists()
        import json
        data = json.loads(Path(path).read_text())
        assert data["summary"]["total_products"] == 1
        assert data["brands"]["gypsobat"]["total_documents_discovered"] == 1


class TestURLNormalization:
    def test_normalize_url_encodes_spaces(self):
        assert AcquisitionPipeline._normalize_url("https://example.com/path with spaces/file.pdf") == \
               "https://example.com/path%20with%20spaces/file.pdf"

    def test_normalize_url_preserves_ascii(self):
        assert AcquisitionPipeline._normalize_url("https://example.com/path/file.pdf") == \
               "https://example.com/path/file.pdf"

    def test_find_record_by_url_matches_encoded_and_unencoded(self):
        pipeline = AcquisitionPipeline()
        records = [DocumentRecord(document_url="https://example.com/path with spaces/file.pdf")]
        found = pipeline._find_record_by_url("https://example.com/path%20with%20spaces/file.pdf", records)
        assert found is not None
        assert found.document_url == "https://example.com/path with spaces/file.pdf"


class TestGyprocAliasRelevance:
    def test_ba13_hydro_accepts_gyproc_moisture_resistant_board(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Moisture Resistant Board 2024",
            url="https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in; matches product tokens",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="GYPROC") is True

    def test_ba13_hydro_accepts_gyproc_duraline(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Duraline Board",
            url="https://www.gyproc.in/pdf/PB05_Gyproc_Duraline_Board.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in; matches product tokens",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="GYPROC") is True

    def test_ba13_feu_accepts_gyproc_fireline(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Fireline Board 2024",
            url="https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in; matches product tokens",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Feu", None, manufacturer="GYPROC") is True

    def test_ba13_standard_accepts_gyproc_plain_board(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Plain Board 2024",
            url="https://www.gyproc.in/pdf/PB01_Gypboard_Plain.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in; matches product tokens",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Standard", None, manufacturer="GYPROC") is True

    def test_unrelated_gyproc_pdf_rejected_without_manufacturer(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Fireline Board 2024",
            url="https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in; matches product tokens",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer=None) is False

    def test_unrelated_gyproc_pdf_rejected_with_wrong_manufacturer(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Fireline Board 2024",
            url="https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in; matches product tokens",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="SINIAT") is False

    def test_gyproc_alias_rejected_without_manufacturer_targeted(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Moisture Resistant Board 2024",
            url="https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf",
            domain="gyproc.in",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in; matches product tokens",
            discovery_provider="web_search",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="GYPROC") is False

    def test_gyproc_alias_rejected_with_third_party_source(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Moisture Resistant Board 2024",
            url="https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf",
            domain="gyproc.in",
            source_type="third_party",
            confidence="medium",
            evidence="Found in sitemap for gyproc.in; matches product tokens",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="GYPROC") is False

    def test_gyproc_alias_rejected_with_unverified_domain(self):
        pipeline = AcquisitionPipeline()
        candidate = SearchCandidate(
            title="Gyproc Moisture Resistant Board 2024",
            url="https://www.example.com/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf",
            domain="example.com",
            source_type="external_official",
            confidence="medium",
            evidence="Found in sitemap for example.com; matches product tokens",
            discovery_provider="manufacturer_targeted",
        )
        assert pipeline._is_relevant_candidate(candidate, "BA13 Hydro", None, manufacturer="GYPROC") is False

    def test_lika_pap2_still_rejected_for_ba13_hydro(self):
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


from pathlib import Path
