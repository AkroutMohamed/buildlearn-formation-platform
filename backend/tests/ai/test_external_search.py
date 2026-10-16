from __future__ import annotations

from unittest.mock import MagicMock, patch

import requests

from app.ai.acquisition.external_search import (
    BaseExternalSearcher,
    ManufacturerTargetedSearcher,
    SearchCandidate,
    WebExternalSearcher,
    build_search_queries,
)


class TestSearchCandidate:
    def test_defaults(self):
        c = SearchCandidate(
            title="Test",
            url="https://example.com",
            domain="example.com",
            source_type="third_party",
            confidence="low",
            evidence="test",
        )
        assert c.title == "Test"
        assert c.url == "https://example.com"
        assert c.domain == "example.com"
        assert c.source_type == "third_party"
        assert c.confidence == "low"
        assert c.evidence == "test"
        assert c.product_name is None
        assert c.processed is False

    def test_to_dict(self):
        c = SearchCandidate(
            title="Doc PDF",
            url="https://gypsobat.fr/fiche.pdf",
            domain="gypsobat.fr",
            source_type="external_official",
            confidence="high",
            evidence="Official site",
            product_name="Plaque",
        )
        d = c.to_dict()
        assert d["title"] == "Doc PDF"
        assert d["url"] == "https://gypsobat.fr/fiche.pdf"
        assert d["domain"] == "gypsobat.fr"
        assert d["confidence"] == "high"
        assert d["product_name"] == "Plaque"


class TestBuildSearchQueries:
    def test_queries_generated_for_product(self):
        queries = build_search_queries("Plaque de plâtre")
        assert len(queries) >= 2
        assert any("Plaque de plâtre" in q for q in queries)
        assert any("fiche technique" in q for q in queries)

    def test_queries_with_model(self):
        queries = build_search_queries("Produit", "REF-123")
        assert any("REF-123" in q for q in queries)
        assert any("Produit" in q for q in queries)

    def test_queries_are_unique(self):
        queries = build_search_queries("Produit", "REF-123")
        assert len(queries) == len(set(queries))

    def test_queries_for_empty_model(self):
        queries = build_search_queries("Produit", model=None)
        assert len(queries) > 0
        assert all("Produit" in q for q in queries)

    def test_queries_with_manufacturer(self):
        queries = build_search_queries("BA13 Hydro", manufacturer="GYPROC")
        assert any("GYPROC" in q for q in queries)
        assert any("BA13 Hydro" in q for q in queries)

    def test_queries_with_manufacturer_and_model(self):
        queries = build_search_queries("Produit", "REF-123", manufacturer="GYPROC")
        assert any("GYPROC" in q for q in queries)
        assert any("REF-123" in q for q in queries)
        assert any("Produit" in q for q in queries)

    def test_queries_without_manufacturer_unchanged(self):
        queries = build_search_queries("Produit")
        assert not any("manufacturer" in q.lower() for q in queries if q != "Produit manufacturer")


class TestClassifySearchResult:
    def test_official_pdf_high(self):
        searcher = WebExternalSearcher()
        source_type, confidence, evidence = searcher._classify_search_result(
            "Gypsobat Fiche Technique PDF", "", "https://gypsobat.com/doc.pdf", "gypsobat.com"
        )
        assert source_type == "external_official"
        assert confidence == "high"

    def test_official_non_pdf_medium(self):
        searcher = WebExternalSearcher()
        source_type, confidence, evidence = searcher._classify_search_result(
            "Page produit", "", "https://emtoptunisie.com/produit", "emtoptunisie.com"
        )
        assert source_type == "external_official"
        assert confidence == "medium"

    def test_distributor_pdf_medium(self):
        searcher = WebExternalSearcher()
        source_type, confidence, evidence = searcher._classify_search_result(
            "Catalogue", "", "https://leroymerlin.fr/doc.pdf", "leroymerlin.fr"
        )
        assert source_type == "external_distributor"
        assert confidence == "medium"

    def test_unknown_pdf_low(self):
        searcher = WebExternalSearcher()
        source_type, confidence, evidence = searcher._classify_search_result(
            "Random doc", "", "https://randomblog.com/doc.pdf", "randomblog.com"
        )
        assert source_type == "third_party"
        assert confidence == "low"

    def test_unknown_non_pdf_low(self):
        searcher = WebExternalSearcher()
        source_type, confidence, evidence = searcher._classify_search_result(
            "Blog post", "", "https://randomblog.com/post", "randomblog.com"
        )
        assert source_type == "third_party"
        assert confidence == "low"


class TestWebExternalSearcher:
    def test_search_returns_candidates(self):
        html = """
        <html><body>
            <div class="result">
                <a class="result__a" href="https://gypsobat.com/fiche/Doc.pdf">Gypsobat Technical Sheet</a>
                <a class="result__snippet">Fiche technique PDF</a>
            </div>
            <div class="result">
                <a class="result__a" href="https://randomblog.com/post">Random Blog Post</a>
                <a class="result__snippet">Some blog content</a>
            </div>
        </body></html>
        """
        searcher = WebExternalSearcher()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher.search("Gypsobat Plaque de plâtre", max_results=5)

        assert len(candidates) == 2
        assert candidates[0].url == "https://gypsobat.com/fiche/Doc.pdf"
        assert candidates[0].confidence == "high"
        assert candidates[0].domain == "gypsobat.com"
        assert candidates[1].confidence == "low"

    def test_search_empty_response(self):
        searcher = WebExternalSearcher()
        html = "<html><body></body></html>"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher.search("Brand Product")

        assert len(candidates) == 0

    def test_search_request_error_returns_empty(self):
        searcher = WebExternalSearcher()
        with patch.object(searcher._session, "get", side_effect=requests.ConnectionError("Network error")):
            candidates = searcher.search("Brand Product")
        assert len(candidates) == 0

    def test_extract_domain(self):
        assert WebExternalSearcher._extract_domain("https://example.com/path") == "example.com"
        assert WebExternalSearcher._extract_domain("https://sub.example.com/path") == "sub.example.com"


class TestWebExternalSearcherTimeout:
    def test_request_uses_bounded_timeout_tuple(self):
        searcher = WebExternalSearcher()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response) as mock_get:
            searcher.search("test query")

        timeout = mock_get.call_args.kwargs.get("timeout")
        assert isinstance(timeout, tuple)
        assert len(timeout) == 2
        assert timeout[0] == 10
        assert timeout[1] == 30

    def test_timeout_is_not_scalar(self):
        searcher = WebExternalSearcher()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response) as mock_get:
            searcher.search("test query")

        timeout = mock_get.call_args.kwargs.get("timeout")
        assert not isinstance(timeout, (int, float))

    def test_max_redirects_is_five(self):
        searcher = WebExternalSearcher()
        assert searcher._session.max_redirects == 5

    def test_allow_redirects_explicitly_true(self):
        searcher = WebExternalSearcher()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response) as mock_get:
            searcher.search("test query")

        assert mock_get.call_args.kwargs.get("allow_redirects") is True


class TestProviderStatus:
    def test_base_provider_status_is_ok(self):
        searcher = WebExternalSearcher()
        assert searcher.provider_status == "ok"

    def test_web_searcher_blocked_on_http_202(self):
        searcher = WebExternalSearcher()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.text = "<html><body>anomaly.js</body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher.search("test query")

        assert len(candidates) == 0
        assert searcher.provider_status == "blocked"

    def test_web_searcher_blocked_on_anomaly_js(self):
        searcher = WebExternalSearcher()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><script>anomaly.js</script></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher.search("test query")

        assert len(candidates) == 0
        assert searcher.provider_status == "blocked"

    def test_web_searcher_normal_empty_not_blocked(self):
        searcher = WebExternalSearcher()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher.search("test query")

        assert len(candidates) == 0
        assert searcher.provider_status == "ok"

    def test_web_searcher_reset_status_after_success(self):
        searcher = WebExternalSearcher()
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.text = "anomaly.js"
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response):
            searcher.search("blocked query")
        assert searcher.provider_status == "blocked"

        mock_response2 = MagicMock()
        mock_response2.status_code = 200
        mock_response2.text = '<html><body><div class="result"><a class="result__a" href="https://example.com/doc.pdf">Doc</a></div></body></html>'
        mock_response2.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response2):
            candidates = searcher.search("success query")

        assert len(candidates) == 1
        assert searcher.provider_status == "ok"


class TestSearchCandidateProvenance:
    def test_discovery_provider_defaults_none(self):
        c = SearchCandidate(
            title="Test",
            url="https://example.com",
            domain="example.com",
            source_type="third_party",
            confidence="low",
            evidence="test",
        )
        assert c.discovery_provider is None

    def test_discovery_provider_in_to_dict(self):
        c = SearchCandidate(
            title="Test",
            url="https://example.com",
            domain="example.com",
            source_type="external_official",
            confidence="high",
            evidence="test",
            discovery_provider="manufacturer_targeted",
        )
        d = c.to_dict()
        assert d["discovery_provider"] == "manufacturer_targeted"


class TestManufacturerTargetedSearcher:
    def test_unknown_manufacturer_returns_empty(self):
        searcher = ManufacturerTargetedSearcher("UNKNOWN", "Product X")
        assert searcher.provider_status == "ok"
        candidates = searcher.search("Product X")
        assert candidates == []

    def test_verified_manufacturer_has_domains(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        assert "gyproc.com" in searcher._domains

    def test_search_with_no_verified_domains(self):
        searcher = ManufacturerTargetedSearcher("LIKA", "LIKA PAP 90")
        assert searcher._domains == []
        candidates = searcher.search("LIKA PAP 90")
        assert candidates == []
        assert searcher.provider_status == "ok"

    def test_tacer_has_manufacturer_paths(self):
        searcher = ManufacturerTargetedSearcher("TACER", "T-15")
        assert "/documents" in searcher._manufacturer_paths

    def test_siniat_has_document_hosts(self):
        searcher = ManufacturerTargetedSearcher("SINIAT", "BA13")
        assert "media.siniat.com" in searcher._document_hosts

    def test_gyproc_has_manufacturer_paths(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        assert "/resources-downloads" in searcher._manufacturer_paths

    def test_search_page_encodes_special_characters_in_path(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response) as mock_get:
            searcher._search_page("example.com", "/path with spaces/", set(), set())

        called_url = mock_get.call_args.args[0]
        assert "%20" in called_url or " " not in called_url

    def test_sitemap_index_follows_sub_sitemaps(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        sitemap_index = """<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex>
            <sitemap><loc>https://example.com/sitemap1.xml</loc></sitemap>
            <sitemap><loc>https://example.com/sitemap2.xml</loc></sitemap>
        </sitemapindex>"""
        sub_sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset>
            <url><loc>https://example.com/files/BA13-Hydro.pdf</loc></url>
        </urlset>"""
        mock_responses = [
            MagicMock(status_code=200, text=sitemap_index, headers={"Content-Type": "application/xml"}, raise_for_status=MagicMock()),
            MagicMock(status_code=200, text=sub_sitemap, headers={"Content-Type": "application/xml"}, raise_for_status=MagicMock()),
        ]

        with patch.object(searcher._session, "get", side_effect=mock_responses) as mock_get:
            candidates = searcher._search_sitemap("example.com", {"ba13", "hydro"}, set())

        assert len(candidates) == 1
        assert candidates[0].url == "https://example.com/files/BA13-Hydro.pdf"

    def test_document_host_search_finds_pdfs(self):
        searcher = ManufacturerTargetedSearcher("SINIAT", "BA13")
        html = """
        <html><body>
            <a href="/media/siniat-datasheet.pdf">Siniat Datasheet</a>
            <a href="/media/other.pdf">Other Doc</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html
        mock_response.raise_for_status = MagicMock()

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher._search_document_host("media.siniat.com", {"siniat", "datasheet"}, set())

        assert len(candidates) >= 1
        assert any("siniat-datasheet.pdf" in c.url for c in candidates)

    def test_gyproc_has_gyproc_in_domain(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        assert "gyproc.in" in searcher._domains
        assert "gyproc.com" in searcher._domains

    def test_gyproc_has_pdf_sitemap_path(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        assert "/pdf-sitemap.xml" in searcher._manufacturer_paths

    def test_gyproc_alias_match_moisture_resistant_board(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        assert searcher._is_gyproc_alias_match("Gyproc Moisture Resistant Board 2024")
        assert searcher._is_gyproc_alias_match("https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf")

    def test_gyproc_alias_match_duraline(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        assert searcher._is_gyproc_alias_match("Gyproc Duraline Board")
        assert searcher._is_gyproc_alias_match("https://www.gyproc.in/pdf/PB05_Gyproc_Duraline_Board.pdf")

    def test_gyproc_alias_match_fireline(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Feu")
        assert searcher._is_gyproc_alias_match("Gyproc Fireline Board 2024")
        assert searcher._is_gyproc_alias_match("https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf")

    def test_gyproc_alias_match_plain_board(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Standard")
        assert searcher._is_gyproc_alias_match("Gyproc Plain Board 2024")
        assert searcher._is_gyproc_alias_match("https://www.gyproc.in/pdf/PB01_Gypboard_Plain.pdf")

    def test_gyproc_alias_match_gypboard_plain(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Standard")
        assert searcher._is_gyproc_alias_match("Gypboard Plain")
        assert searcher._is_gyproc_alias_match("https://www.gyproc.in/pdf/data-sheet-plain-board.pdf")

    def test_gyproc_alias_no_match_for_unrelated_product(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "Habito Forte")
        assert not searcher._is_gyproc_alias_match("Gyproc Fireline Board 2024")
        assert not searcher._is_gyproc_alias_match("Gyproc Moisture Resistant Board 2024")

    def test_non_gyproc_manufacturer_no_gyproc_aliases(self):
        searcher = ManufacturerTargetedSearcher("SINIAT", "BA13 Hydro")
        assert not searcher._is_gyproc_alias_match("Gyproc Moisture Resistant Board 2024")
        assert not searcher._is_gyproc_alias_match("https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf")

    def test_gyproc_sitemap_discovers_ba13_hydro_pdf(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset>
            <url><loc>https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf</loc></url>
            <url><loc>https://www.gyproc.in/pdf/mr-product-data-sheet.pdf</loc></url>
        </urlset>"""
        mock_response = MagicMock(status_code=200, text=sitemap, headers={"Content-Type": "application/xml"}, raise_for_status=MagicMock())

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher._search_sitemap("gyproc.in", {"ba13", "hydro"}, set())

        assert len(candidates) == 1
        urls = [c.url for c in candidates]
        assert "https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf" in urls
        assert all(c.confidence == "high" for c in candidates)

    def test_gyproc_sitemap_discovers_ba13_feu_pdf(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Feu")
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset>
            <url><loc>https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf</loc></url>
        </urlset>"""
        mock_response = MagicMock(status_code=200, text=sitemap, headers={"Content-Type": "application/xml"}, raise_for_status=MagicMock())

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher._search_sitemap("gyproc.in", {"ba13", "feu"}, set())

        assert len(candidates) == 1
        assert candidates[0].url == "https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf"
        assert candidates[0].confidence == "high"

    def test_gyproc_unrelated_pdf_rejected_by_sitemap(self):
        searcher = ManufacturerTargetedSearcher("GYPROC", "BA13 Hydro")
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
        <urlset>
            <url><loc>https://www.gyproc.in/pdf/Gyproc_Plain_Board_2024.pdf</loc></url>
        </urlset>"""
        mock_response = MagicMock(status_code=200, text=sitemap, headers={"Content-Type": "application/xml"}, raise_for_status=MagicMock())

        with patch.object(searcher._session, "get", return_value=mock_response):
            candidates = searcher._search_sitemap("gyproc.in", {"ba13", "hydro"}, set())

        assert len(candidates) == 0
