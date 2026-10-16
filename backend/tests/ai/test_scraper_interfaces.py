from app.ai.scraping.registry import list_sources, get_scraper


def test_scraper_registry_has_sources():
    sources = list_sources()
    assert "gypsobat" in sources
    assert "emtop" in sources
    assert "sofap" in sources


def test_gypsobat_scraper_has_methods():
    scraper = get_scraper("gypsobat")
    assert hasattr(scraper, "discover_products")
    assert hasattr(scraper, "scrape_product")
    assert hasattr(scraper, "discover_documents")
    assert scraper.source == "gypsobat"


def test_gypsobat_scraper_discover_returns_list():
    scraper = get_scraper("gypsobat")
    products = scraper.discover_products()
    assert isinstance(products, list)
    assert len(products) > 0
    assert all("id" in p and "url" in p for p in products)
