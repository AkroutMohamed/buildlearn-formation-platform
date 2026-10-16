from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.ai.scraping.base import BaseProductScraper
from app.ai.schemas.product import ProductCreate
from app.ai.config import AI_RAW_DIR

logger = logging.getLogger(__name__)

_BASE_URL = "https://emtoptunisie.com"
_USER_AGENT = "BuildLearn-AI-Scraper/1.0 (+https://buildlearn.ai/bot)"
_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": _USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

_PRODUCTS_API = urljoin(_BASE_URL, "/wp-json/wp/v2/product")
_CATEGORIES_API = urljoin(_BASE_URL, "/wp-json/wp/v2/product_cat")
_BRANDS_API = urljoin(_BASE_URL, "/wp-json/wp/v2/product_brands")
_CATALOGUE_URL = urljoin(_BASE_URL, "/catalogue/")
_SAV_URL = urljoin(_BASE_URL, "/sav/")

_DOC_PAGES = [
    _CATALOGUE_URL,
    _SAV_URL,
]


class _RateLimiter:
    def __init__(self, min_interval: float = 1.0) -> None:
        self.min_interval = min_interval
        self._last: float = 0.0

    def wait(self) -> None:
        now = time.time()
        delta = now - self._last
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta)
        self._last = time.time()


_rate_limiter = _RateLimiter(min_interval=1.0)


def _get(url: str, **kwargs: Any) -> requests.Response:
    _rate_limiter.wait()
    logger.info("GET %s", url)
    response = _SESSION.get(url, timeout=30, **kwargs)
    response.raise_for_status()
    return response


def _clean_text(value: str | None) -> str | None:
    if not value:
        return None
    return " ".join(value.split())


def _strip_html(html: str | None) -> str | None:
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    return _clean_text(text)


def _slug_from_url(url: str) -> str:
    if not url:
        return ""
    return url.rstrip("/").split("/")[-1]


def _extract_product_from_api(product_data: dict[str, Any]) -> ProductCreate:
    title = _clean_text(product_data.get("title", {}).get("rendered", "")) or "Unknown"
    content = _strip_html(product_data.get("content", {}).get("rendered", "")) or ""
    excerpt = _strip_html(product_data.get("excerpt", {}).get("rendered", "")) or ""
    link = product_data.get("link", "")
    slug = product_data.get("slug", "")

    raw_meta = product_data.get("meta", {}) or {}
    specs: dict[str, str] = {}
    if isinstance(raw_meta, dict):
        for key, value in raw_meta.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            if isinstance(value, str) and value.strip() and key.strip():
                specs[key.strip()] = value.strip()

    for attr_name in ("_sku", "_model", "sku", "model"):
        val = raw_meta.get(attr_name)
        if val and isinstance(val, (str, list)):
            val = val[0] if isinstance(val, list) else val
            if val and val.strip():
                specs["model_or_sku"] = val.strip()
                break

    if not specs and content:
        lines = content.split("\n")
        current_key = None
        for line in lines:
            line = line.strip()
            if ":" in line and len(line) < 100:
                parts = line.split(":", 1)
                key = parts[0].strip()
                val = parts[1].strip() if len(parts) > 1 else ""
                if key and val and len(key) < 50:
                    specs[key] = val
                    current_key = key
            elif current_key and line and len(line) < 200:
                specs[current_key] = f"{specs[current_key]} {line}"

    return ProductCreate(
        product_id=str(product_data.get("id", "")),
        name=title,
        brand="EMTOP",
        manufacturer="EMTOP",
        category=None,
        subcategory=None,
        description=excerpt or content or None,
        applications=None,
        technical_specifications=specs if specs else None,
        usage_instructions=None,
        limitations=None,
        standards=None,
        certifications=None,
        packaging=None,
        storage=None,
        shelf_life=None,
        source_url=link or None,
        technical_document_url=None,
        document_urls=None,
        language="fr",
        scraped_at=datetime.now(timezone.utc),
    )


def _extract_product_from_html(html: str, url: str) -> ProductCreate:
    """Parse a product page HTML to extract metadata including PDF links and specs."""
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1", class_="product_title")
    if not title_tag:
        title_tag = soup.find("h1")
    name = _clean_text(title_tag.get_text()) if title_tag else "Unknown"

    price_tag = soup.find("span", class_="price")
    price = _clean_text(price_tag.get_text()) if price_tag else None

    sku = None
    sku_tag = soup.find("span", class_="sku")
    if sku_tag:
        sku = _clean_text(sku_tag.get_text())

    categories = [a.get("aria-label") or _clean_text(a.get_text()) for a in soup.find_all("a", rel="tag")]
    category = categories[0] if categories else None

    description_parts: list[str] = []
    for selector in ("div.woocommerce-tabs", "div.product_meta", "div.wpb_wrapper", "div.short-description"):
        block = soup.select_one(selector)
        if block:
            description_parts.append(_clean_text(block.get_text()))

    if not description_parts:
        desc_div = soup.find("div", class_="description")
        if desc_div:
            description_parts.append(_clean_text(desc_div.get_text()))

    description = " ".join(p for p in description_parts if p) if description_parts else None

    specs: dict[str, str] = {}
    spec_blocks = soup.find_all("div", class_="summary")
    for block in spec_blocks:
        rows = block.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = _clean_text(cells[0].get_text())
                val = _clean_text(cells[1].get_text())
                if key and val:
                    specs[key] = val

    if not specs:
        for selector in ("div.meta", "ul.product-attributes", "table.variations"):
            block = soup.select_one(selector)
            if block:
                rows = block.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td", "label"])
                    if len(cells) >= 2:
                        key = _clean_text(cells[0].get_text())
                        val = _clean_text(cells[1].get_text())
                        if key and val:
                            specs[key] = val

    document_urls: list[str] = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.lower().endswith(".pdf"):
            document_urls.append(urljoin(_BASE_URL, href))

    product_id = ""
    pid_tag = soup.find("input", attrs={"name": "add-to-cart"})
    if pid_tag:
        product_id = pid_tag.get("value", "")
    if not product_id:
        body_classes = soup.find("body", class_=True)
        if body_classes:
            for cls in body_classes.get("class", []):
                if cls.startswith("post-"):
                    product_id = cls.replace("post-", "")

    return ProductCreate(
        product_id=product_id or None,
        name=name,
        brand="EMTOP",
        manufacturer="EMTOP",
        category=category,
        subcategory=None,
        description=description or None,
        applications=None,
        technical_specifications=specs if specs else None,
        usage_instructions=None,
        limitations=None,
        standards=None,
        certifications=None,
        packaging=None,
        storage=None,
        shelf_life=None,
        source_url=url,
        technical_document_url=document_urls[0] if document_urls else None,
        document_urls=document_urls if document_urls else None,
        language="fr",
        scraped_at=datetime.now(timezone.utc),
    )


def _extract_category_names(product_data: dict[str, Any]) -> tuple[str | None, str | None]:
    category_ids = product_data.get("product_cat", [])
    product_brands = product_data.get("product_brand", [])
    if not category_ids:
        return None, None
    try:
        cats_response = _SESSION.get(
            _CATEGORIES_API,
            params={"include": ",".join(str(c) for c in category_ids)},
            headers={"User-Agent": _USER_AGENT},
            timeout=30,
        )
        cats = cats_response.json()
        if isinstance(cats, dict) and "id" in cats:
            cats = [cats]
        names = [c.get("name", "") for c in cats if c.get("name")]
        if not names:
            return None, None
        return names[0], names[1] if len(names) > 1 else None
    except Exception as exc:
        logger.debug("Failed to fetch EMTOP categories: %s", exc)
        return None, None


def _discover_doc_pages() -> list[dict[str, Any]]:
    """Discover documents from EMTOP documentation/catalogue pages."""
    documents: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for page_url in _DOC_PAGES:
        try:
            response = _get(page_url)
        except Exception as exc:
            logger.warning("Failed to fetch doc page %s: %s", page_url, exc)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if href.lower().endswith(".pdf"):
                doc_url = urljoin(_BASE_URL, href)
                if doc_url not in seen_urls:
                    seen_urls.add(doc_url)
                    link_text = _clean_text(anchor.get_text()) or "Document"
                    documents.append({
                        "product_name": link_text,
                        "supplier": "EMTOP",
                        "document_url": doc_url,
                        "document_type": "catalogue",
                        "mime_type": "application/pdf",
                        "source_url": page_url,
                        "title": link_text,
                        "source_type": "official",
                        "confidence": "medium",
                        "evidence": f"PDF link found on EMTOP documentation page {page_url}",
                    })

    return documents


class EmtopScraper(BaseProductScraper):
    source = "emtop"

    def discover_products(self, max_pages: int = 50) -> list[dict[str, Any]]:
        all_products: list[dict[str, Any]] = []
        try:
            page = 1
            per_page = 100
            while page <= max_pages:
                response = _get(_PRODUCTS_API, params={"per_page": per_page, "page": page})
                products = response.json()
                if isinstance(products, dict) and "id" in products:
                    products = [products]
                if not products:
                    break
                batch = [{"id": str(p.get("id", "")), "url": p.get("link", "")} for p in products if p.get("link")]
                if not batch:
                    break
                all_products.extend(batch)
                logger.info("EMTOP: Discovered %d products on page %d (total: %d)",
                            len(batch), page, len(all_products))
                page += 1
        except Exception as exc:
            logger.error("EMTOP: Failed to discover products: %s", exc)
            return all_products or []

        return all_products

    def scrape_product(self, url: str) -> ProductCreate:
        api_url = urljoin(_BASE_URL, "/wp-json/wp/v2/product")
        slug = _slug_from_url(url)
        try:
            response = _get(api_url, params={"slug": slug})
            products = response.json()
            if isinstance(products, dict) and "id" in products:
                products = [products]
            if not products:
                raise ValueError(f"No EMTOP product found for {url}")

            product_data = products[0]
            product = _extract_product_from_api(product_data)
            category, subcategory = _extract_category_names(product_data)
            product.category = category
            product.subcategory = subcategory

            if not product.technical_specifications:
                try:
                    page_response = _get(url)
                    html_product = _extract_product_from_html(page_response.text, url)
                    if not product.description:
                        product.description = html_product.description
                    if not product.technical_specifications and html_product.technical_specifications:
                        product.technical_specifications = html_product.technical_specifications
                    if html_product.document_urls:
                        product.document_urls = html_product.document_urls
                        product.technical_document_url = html_product.document_urls[0]
                except Exception as exc:
                    logger.warning("EMTOP: Failed to fetch product page HTML for %s: %s", url, exc)

            return product
        except Exception as exc:
            logger.error("EMTOP: Failed to scrape product %s: %s", url, exc)
            raise

    def discover_documents(self, product: ProductCreate) -> list[dict[str, Any]]:
        """Discover documents for a specific EMTOP product.

        Checks:
        1. Product page for embedded PDF links
        2. Category documentation pages
        """
        documents: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        if product.document_urls:
            for doc_url in product.document_urls:
                if doc_url not in seen_urls:
                    seen_urls.add(doc_url)
                    documents.append({
                        "product_name": product.name,
                        "supplier": "EMTOP",
                        "document_url": doc_url,
                        "document_type": "technical_sheet",
                        "mime_type": "application/pdf",
                        "source_url": product.source_url or "",
                        "title": product.name,
                        "source_type": "official",
                        "confidence": "high",
                        "evidence": f"PDF link found on EMTOP product page for '{product.name}'",
                    })

        doc_pages = _discover_doc_pages()
        product_slug = _slug_from_url(product.source_url or "")
        for doc in doc_pages:
            if doc["document_url"] not in seen_urls:
                doc_title_lower = doc.get("title", "").lower()
                doc_url_lower = doc["document_url"].lower()
                if product_slug and (product_slug in doc_url_lower or product_slug in doc_title_lower):
                    doc_copy = dict(doc)
                    doc_copy["product_name"] = product.name
                    doc_copy["source_type"] = "official"
                    doc_copy["confidence"] = "medium"
                    doc_copy["evidence"] = f"Catalogue PDF matching product slug '{product_slug}' for '{product.name}'"
                    documents.append(doc_copy)
                    seen_urls.add(doc["document_url"])

        return documents

    def discover_all_documents(self) -> list[dict[str, Any]]:
        return _discover_doc_pages()


def save_raw_sample(products: list[ProductCreate], documents: list[dict[str, Any]]) -> str:
    raw_dir = AI_RAW_DIR / "emtop"
    raw_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "count": len(products),
        "products": [p.model_dump(mode="json") for p in products],
        "documents": documents,
    }

    path = raw_dir / "products.json"
    with open(path, "w", encoding="utf-8") as fh:
        import json
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)

    logger.info("Saved raw sample to %s", path)
    return str(path)
