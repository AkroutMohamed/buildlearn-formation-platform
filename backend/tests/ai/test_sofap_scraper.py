from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.ai.scraping.sources import sofap as sofap_module
from app.ai.scraping.sources.sofap import SofapScraper
from app.ai.schemas.product import ProductCreate


_API_PRODUCTS_PAGE_1 = [
    {
        "id": 1,
        "slug": "plaque-gypseuse",
        "title": {"rendered": "Plaque Gypseuse"},
        "content": {"rendered": "<p>Description</p>"},
        "excerpt": {"rendered": "Plaque Gypseuse"},
        "status": "publish",
        "link": "https://sofapbatiment.com/plaque-gypseuse/",
    },
    {
        "id": 2,
        "slug": "jointoiement",
        "title": {"rendered": "Jointoiement"},
        "content": {"rendered": ""},
        "excerpt": {"rendered": "Joint"},
        "status": "publish",
        "link": "https://sofapbatiment.com/jointoiement/",
    },
]

_API_PRODUCTS_PAGE_2 = [
    {"id": 3, "slug": "p3", "title": {"rendered": "P3"}, "link": "https://sofapbatiment.com/p3/"},
]


class TestSofapScraperDiscoverProducts:
    def test_discover_products_pagination(self):
        scraper = SofapScraper()
        call_count = [0]

        def mock_get(url, **kwargs):
            call_count[0] += 1
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            if call_count[0] == 1:
                resp.json.return_value = _API_PRODUCTS_PAGE_1
            elif call_count[0] == 2:
                resp.json.return_value = _API_PRODUCTS_PAGE_2
            else:
                resp.json.return_value = []
            return resp

        with patch.object(sofap_module, "_get", side_effect=mock_get):
            products = scraper.discover_products()

        assert len(products) == 3
        assert products[0] == {"id": "1", "url": "https://sofapbatiment.com/plaque-gypseuse/"}
        assert products[1] == {"id": "2", "url": "https://sofapbatiment.com/jointoiement/"}
        assert products[2] == {"id": "3", "url": "https://sofapbatiment.com/p3/"}
        assert call_count[0] == 3

    def test_discover_products_single_page(self):
        scraper = SofapScraper()
        call_count = [0]

        def mock_get(url, **kwargs):
            call_count[0] += 1
            resp = MagicMock()
            resp.status_code = 200
            resp.raise_for_status = MagicMock()
            if call_count[0] == 1:
                resp.json.return_value = _API_PRODUCTS_PAGE_1
            else:
                resp.json.return_value = []
            return resp

        with patch.object(sofap_module, "_get", side_effect=mock_get):
            products = scraper.discover_products()

        assert len(products) == 2
        assert products[0]["id"] == "1"
        assert "sofapbatiment.com" in products[0]["url"]


class TestSofapScraperScrapeProduct:
    def test_scrape_product_with_pdf_links(self):
        scraper = SofapScraper()
        html_page = """
        <html><body>
            <h1 class="product_title">Plaque P6</h1>
            <a class="download-button" href="/wp-content/uploads/fiche-technique.pdf">Fiche Technique</a>
            <a class="download-button" href="/wp-content/uploads/dossier-technique.pdf">Dossier Technique</a>
        </body></html>
        """

        api_mock = MagicMock()
        api_mock.status_code = 200
        api_mock.raise_for_status = MagicMock()
        api_mock.json.return_value = [{
            "id": 42,
            "slug": "plaque-p6",
            "title": {"rendered": "Plaque P6"},
            "content": {"rendered": ""},
            "link": "https://sofapbatiment.com/plaque-p6/",
        }]

        html_mock = MagicMock()
        html_mock.status_code = 200
        html_mock.raise_for_status = MagicMock()
        html_mock.text = html_page

        def mock_get(url, **kwargs):
            if "wp-json" in url and url.endswith("product"):
                return api_mock
            return html_mock

        with patch.object(sofap_module, "_get", side_effect=mock_get):
            product = scraper.scrape_product("https://sofapbatiment.com/plaque-p6/")

        assert isinstance(product, ProductCreate)
        assert product.name == "Plaque P6"
        assert product.brand == "SOFAP"
        assert len(product.document_urls) == 2
        assert "fiche-technique.pdf" in product.document_urls[0]

    def test_scrape_product_api_only(self):
        scraper = SofapScraper()
        api_mock = MagicMock()
        api_mock.status_code = 200
        api_mock.raise_for_status = MagicMock()
        api_mock.json.return_value = [{
            "id": 99,
            "slug": "test-product",
            "title": {"rendered": "API Product"},
            "content": {"rendered": "<p>API content</p>"},
            "link": "https://sofapbatiment.com/test-product/",
        }]

        html_mock = MagicMock()
        html_mock.status_code = 200
        html_mock.raise_for_status = MagicMock()
        html_mock.text = "<html></html>"

        def mock_get(url, **kwargs):
            if "wp-json" in url and url.endswith("product"):
                return api_mock
            return html_mock

        with patch.object(sofap_module, "_get", side_effect=mock_get):
            product = scraper.scrape_product("https://sofapbatiment.com/test-product/")

        assert isinstance(product, ProductCreate)
        assert product.name == "API Product"

    def test_scrape_product_no_pdf_links(self):
        scraper = SofapScraper()
        html_page = """
        <html><body>
            <h1 class="product_title">Product No PDF</h1>
            <p>No downloads here</p>
        </body></html>
        """

        api_mock = MagicMock()
        api_mock.status_code = 200
        api_mock.raise_for_status = MagicMock()
        api_mock.json.return_value = [{
            "id": 1,
            "slug": "no-pdf",
            "title": {"rendered": "Product No PDF"},
            "content": {"rendered": "<p>Content</p>"},
            "link": "https://sofapbatiment.com/no-pdf/",
        }]

        html_mock = MagicMock()
        html_mock.status_code = 200
        html_mock.raise_for_status = MagicMock()
        html_mock.text = html_page

        def mock_get(url, **kwargs):
            if "wp-json" in url and url.endswith("product"):
                return api_mock
            return html_mock

        with patch.object(sofap_module, "_get", side_effect=mock_get):
            product = scraper.scrape_product("https://sofapbatiment.com/no-pdf/")

        assert isinstance(product, ProductCreate)
        assert not product.document_urls


class TestSofapScraperDiscoverDocuments:
    def test_discover_documents_from_product_page(self):
        scraper = SofapScraper()
        product = ProductCreate(
            name="Plaque Test",
            document_urls=["https://sofapbatiment.com/wp-content/uploads/fiche.pdf"],
        )

        docs = scraper.discover_documents(product)

        assert len(docs) == 1
        assert docs[0]["document_url"] == "https://sofapbatiment.com/wp-content/uploads/fiche.pdf"
        assert docs[0]["source_type"] == "official"
        assert docs[0]["confidence"] == "high"
        assert docs[0]["supplier"] == "SOFAP"

    def test_discover_documents_no_pdf_links(self):
        scraper = SofapScraper()
        product = ProductCreate(name="No Docs Product")

        doc_pages_response = MagicMock()
        doc_pages_response.status_code = 200
        doc_pages_response.raise_for_status = MagicMock()
        doc_pages_response.text = "<html><body><p>No PDFs here</p></body></html>"

        with patch.object(sofap_module, "_get", return_value=doc_pages_response):
            docs = scraper.discover_documents(product)

        assert len(docs) == 0

    def test_discover_all_documents(self):
        scraper = SofapScraper()
        doc_html = """
        <html><body>
            <a href="https://sofapbatiment.com/wp-content/uploads/fiche.pdf">Fiche</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.text = doc_html

        with patch.object(sofap_module, "_get", return_value=mock_response):
            docs = scraper.discover_all_documents()

        assert len(docs) >= 1
        assert docs[0]["supplier"] == "SOFAP"
        assert docs[0]["source_type"] == "official"
