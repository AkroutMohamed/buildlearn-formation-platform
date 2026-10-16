from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.ai.scraping.sources import emtop as emtop_module
from app.ai.scraping.sources.emtop import EmtopScraper
from app.ai.schemas.product import ProductCreate


_API_PRODUCTS_PAGE_1 = [
    {
        "id": 1,
        "slug": "cable-ethernet-cat6",
        "title": {"rendered": "Câble Ethernet Cat6"},
        "content": {"rendered": "<p>Description du câble</p>"},
        "excerpt": {"rendered": "Câble Ethernet Cat6"},
        "status": "publish",
        "link": "https://emtoptunisie.com/cable-ethernet-cat6/",
    },
    {
        "id": 2,
        "slug": "connecteur-rj45",
        "title": {"rendered": "Connecteur RJ45"},
        "content": {"rendered": ""},
        "excerpt": {"rendered": "Connecteur RJ45"},
        "status": "publish",
        "link": "https://emtoptunisie.com/connecteur-rj45/",
    },
]

_API_PRODUCTS_PAGE_2 = [
    {"id": 3, "slug": "produit-3", "title": {"rendered": "Produit 3"}, "link": "https://emtoptunisie.com/produit-3/"},
]


class TestEmtopScraperDiscoverProducts:
    def test_discover_products_pagination(self):
        scraper = EmtopScraper()
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

        with patch.object(emtop_module, "_get", side_effect=mock_get):
            products = scraper.discover_products()

        assert len(products) == 3
        assert products[0] == {"id": "1", "url": "https://emtoptunisie.com/cable-ethernet-cat6/"}
        assert products[1] == {"id": "2", "url": "https://emtoptunisie.com/connecteur-rj45/"}
        assert products[2] == {"id": "3", "url": "https://emtoptunisie.com/produit-3/"}
        assert call_count[0] == 3

    def test_discover_products_single_page(self):
        scraper = EmtopScraper()
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

        with patch.object(emtop_module, "_get", side_effect=mock_get):
            products = scraper.discover_products()

        assert len(products) == 2
        assert products[0]["id"] == "1"
        assert "emtoptunisie.com" in products[0]["url"]


class TestEmtopScraperScrapeProduct:
    def test_scrape_product_from_api(self):
        scraper = EmtopScraper()
        api_response = {
            "id": 123,
            "slug": "test-product",
            "title": {"rendered": "Test Product"},
            "content": {"rendered": "<p>Full description</p>"},
            "excerpt": {"rendered": "Short excerpt"},
            "status": "publish",
            "link": "https://emtoptunisie.com/test-product/",
        }
        api_mock = MagicMock()
        api_mock.status_code = 200
        api_mock.raise_for_status = MagicMock()
        api_mock.json.return_value = [api_response]

        with patch.object(emtop_module, "_get", return_value=api_mock):
            product = scraper.scrape_product("https://emtoptunisie.com/test-product/")

        assert isinstance(product, ProductCreate)
        assert product.name == "Test Product"
        assert product.brand == "EMTOP"
        assert product.manufacturer == "EMTOP"
        assert product.source_url == "https://emtoptunisie.com/test-product/"

    def test_scrape_product_falls_back_to_html(self):
        scraper = EmtopScraper()
        api_response = MagicMock()
        api_response.status_code = 200
        api_response.raise_for_status = MagicMock()
        api_response.json.return_value = []

        html_page = """
        <html><body>
            <h1 class="product_title">HTML Title Product</h1>
            <p>Some description</p>
        </body></html>
        """
        html_mock = MagicMock()
        html_mock.status_code = 200
        html_mock.raise_for_status = MagicMock()
        html_mock.text = html_page

        def mock_get(url, **kwargs):
            if "wp-json" in url:
                return api_response
            return html_mock

        with patch.object(emtop_module, "_get", side_effect=mock_get):
            with pytest.raises(ValueError, match="No EMTOP product found"):
                scraper.scrape_product("https://emtoptunisie.com/html-product/")


class TestEmtopScraperDiscoverDocuments:
    def test_discover_documents_from_product_page(self):
        scraper = EmtopScraper()
        product = ProductCreate(
            name="Test Product 1",
            document_urls=["https://emtoptunisie.com/wp-content/uploads/doc1.pdf"],
        )

        docs = scraper.discover_documents(product)

        assert len(docs) == 1
        assert docs[0]["document_url"] == "https://emtoptunisie.com/wp-content/uploads/doc1.pdf"
        assert docs[0]["source_type"] == "official"
        assert docs[0]["confidence"] == "high"
        assert docs[0]["supplier"] == "EMTOP"

    def test_discover_documents_no_pdf_links(self):
        scraper = EmtopScraper()
        product = ProductCreate(name="No Docs Product")

        doc_pages_response = MagicMock()
        doc_pages_response.status_code = 200
        doc_pages_response.raise_for_status = MagicMock()
        doc_pages_response.text = "<html><body><p>No PDFs here</p></body></html>"

        with patch.object(emtop_module, "_get", return_value=doc_pages_response):
            docs = scraper.discover_documents(product)

        assert len(docs) == 0

    def test_discover_documents_external_catalogue(self):
        scraper = EmtopScraper()
        product = ProductCreate(
            name="Catalogue",
            source_url="https://emtoptunisie.com/catalogue/catalogue/",
            document_urls=None,
        )

        doc_pages_html = """
        <html><body>
            <a href="https://emtoptunisie.com/wp-content/uploads/catalogue.pdf">Catalogue</a>
        </body></html>
        """
        doc_pages_response = MagicMock()
        doc_pages_response.status_code = 200
        doc_pages_response.raise_for_status = MagicMock()
        doc_pages_response.text = doc_pages_html

        with patch.object(emtop_module, "_get", return_value=doc_pages_response):
            docs = scraper.discover_documents(product)

        pdf_docs = [d for d in docs if d.get("mime_type") == "application/pdf"]
        assert len(pdf_docs) == 1
        assert "catalogue.pdf" in pdf_docs[0]["document_url"]
        assert pdf_docs[0]["confidence"] == "medium"


class TestEmtopScraperDiscoverAllDocuments:
    def test_discover_all_documents(self):
        scraper = EmtopScraper()
        doc_html = """
        <html><body>
            <a href="https://emtoptunisie.com/wp-content/uploads/doc1.pdf">Fiche</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.text = doc_html

        with patch.object(emtop_module, "_get", return_value=mock_response):
            docs = scraper.discover_all_documents()

        assert len(docs) >= 1
        assert docs[0]["supplier"] == "EMTOP"
        assert docs[0]["source_type"] == "official"
