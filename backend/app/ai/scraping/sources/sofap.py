from __future__ import annotations

import logging
import os
import re
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

_BASE_URL = "https://sofapbatiment.com"
_USER_AGENT = "BuildLearn-AI-Scraper/1.0 (+https://buildlearn.ai/bot)"
_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": _USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})

_PRODUCTS_API = urljoin(_BASE_URL, "/wp-json/wp/v2/product")
_CATEGORIES_API = urljoin(_BASE_URL, "/wp-json/wp/v2/product_cat")

_DOC_PAGES = [
    "/fiche-technique-sofap-enduit/",
    "/fiche-technique-sofap-lika/",
    "/fiche-technique-sofap-col/",
    "/fiches-techniques/",
    "/fiche-technique-sofap-enduit/",
    "/fiche-technique-sofap-lika/",
]

_PDF_LINK_SELECTORS = [
    "a.download-button",
    "a[href*='fiches-techniques']",
    "a[href*='.pdf']",
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

    raw_meta = product_data.get("meta", [])
    specs: dict[str, str] = {}
    if isinstance(raw_meta, list):
        for meta_item in raw_meta:
            if isinstance(meta_item, str):
                if ":" in meta_item:
                    parts = meta_item.split(":", 1)
                    key = parts[0].strip()
                    val = parts[1].strip()
                    if key and val:
                        specs[key] = val
            elif isinstance(meta_item, dict):
                for key, value in meta_item.items():
                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value)
                    if isinstance(value, str) and value.strip():
                        specs[key.strip()] = value.strip()
    elif isinstance(raw_meta, dict):
        for key, value in raw_meta.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            if isinstance(value, str) and value.strip():
                specs[key.strip()] = value.strip()

    class_list = product_data.get("class_list", {})
    category = None
    if isinstance(class_list, dict):
        for cls in class_list.values():
            if isinstance(cls, str) and cls.startswith("product_cat-"):
                category = cls.replace("product_cat-", "")

    excerpt_from_meta = None
    if isinstance(raw_meta, list):
        for meta_item in raw_meta:
            if isinstance(meta_item, str) and ("fiche" in meta_item.lower() or "produit" in meta_item.lower()):
                excerpt_from_meta = meta_item
                break

    return ProductCreate(
        product_id=str(product_data.get("id", "")),
        name=title,
        brand="SOFAP",
        manufacturer="SOFAP",
        category=category,
        subcategory=None,
        description=excerpt or content or excerpt_from_meta or None,
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
    """Parse a SOFAP product page HTML to extract metadata and PDF links."""
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("h1", class_="product_title")
    if not title_tag:
        h1 = soup.find("h1")
        title_tag = h1
    name = _clean_text(title_tag.get_text()) if title_tag else "Unknown"

    description = None
    desc_div = soup.find("div", class_="woocommerce-tabs") or soup.find("div", class_="description")
    if desc_div:
        description = _clean_text(desc_div.get_text())
    if not description:
        content_div = soup.find("div", class_="product-meta")
        if content_div:
            description = _clean_text(content_div.get_text())

    specs: dict[str, str] = {}
    table = soup.find("table", class_="woocommerce-product-attributes")
    if table:
        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                key = _clean_text(cells[0].get_text())
                val = _clean_text(cells[1].get_text())
                if key and val:
                    specs[key] = val

    document_urls: list[str] = []
    for selector in _PDF_LINK_SELECTORS:
        for link in soup.select(selector):
            href = link.get("href", "")
            if href.lower().endswith(".pdf"):
                doc_url = urljoin(_BASE_URL, href)
                if doc_url not in document_urls:
                    document_urls.append(doc_url)

    if not document_urls:
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.lower().endswith(".pdf"):
                doc_url = urljoin(_BASE_URL, href)
                if doc_url not in document_urls:
                    document_urls.append(doc_url)

    category = None
    cat_links = soup.find_all("a", rel="up")
    if cat_links:
        category = _clean_text(cat_links[0].get_text())

    product_id = ""
    for cls in (soup.find("body", class_=True) or []):
        pass
    body_tag = soup.find("body")
    if body_tag and body_tag.get("class"):
        for cls in body_tag["class"]:
            if cls.startswith("post-"):
                product_id = cls.replace("post-", "")
                break

    if not product_id:
        pid_input = soup.find("input", attrs={"name": "add-to-cart"})
        if pid_input:
            product_id = pid_input.get("value", "")

    return ProductCreate(
        product_id=product_id or None,
        name=name,
        brand="SOFAP",
        manufacturer="SOFAP",
        category=category,
        subcategory=None,
        description=description,
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


def _extract_category_names(product_data: dict[str, Any]) -> str | None:
    category_ids = product_data.get("product_cat", [])
    if not category_ids:
        return None
    try:
        response = _SESSION.get(
            _CATEGORIES_API,
            params={"include": ",".join(str(c) for c in category_ids)},
            headers={"User-Agent": _USER_AGENT},
            timeout=30,
        )
        cats = response.json()
        if isinstance(cats, dict) and "id" in cats:
            cats = [cats]
        names = [c.get("name", "") for c in cats if c.get("name")]
        if not names:
            return None
        return names[0]
    except Exception as exc:
        logger.debug("Failed to fetch SOFAP categories: %s", exc)
        return None


def _discover_doc_pages() -> list[dict[str, Any]]:
    """Discover documents from SOFAP documentation/fiches-techniques pages."""
    documents: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    unique_pages = list(dict.fromkeys(_DOC_PAGES))

    for page_path in unique_pages:
        page_url = urljoin(_BASE_URL, page_path)
        page_dir = page_path.strip("/").replace("/", "-")

        doc_type_map = {
            "fiche-technique-sofap-enduit": "technical_sheet",
            "fiche-technique-sofap-lika": "technical_sheet",
            "fiche-technique-sofap-col": "technical_sheet",
            "fiches-techniques": "documentation",
        }
        doc_type = "documentation"
        for key, val in doc_type_map.items():
            if key in page_dir:
                doc_type = val
                break

        try:
            response = _get(page_url)
        except Exception as exc:
            logger.warning("SOFAP: Failed to fetch doc page %s: %s", page_url, exc)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        page_base = page_dir

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if href.lower().endswith(".pdf"):
                doc_url = urljoin(_BASE_URL, href)
                if doc_url not in seen_urls:
                    seen_urls.add(doc_url)
                    link_text = _clean_text(anchor.get_text()) or "Document"
                    filename = unquote(urlparse(doc_url).path.split("/")[-1].replace(".pdf", ""))

                    product_name = _guess_product_name(filename, link_text, page_base)

                    documents.append({
                        "product_name": product_name,
                        "supplier": "SOFAP",
                        "document_url": doc_url,
                        "document_type": doc_type,
                        "mime_type": "application/pdf",
                        "source_url": page_url,
                        "title": link_text,
                        "source_type": "official",
                        "confidence": "medium",
                        "evidence": f"PDF link found on SOFAP documentation page {page_url}",
                    })

    return documents


def _guess_product_name(filename: str, link_text: str, page_base: str) -> str:
    filename_lower = filename.lower()
    if "superlite" in filename_lower:
        return "SUPERLITE"
    if "superdur" in filename_lower:
        return "SUPERDUR"
    if "rustika" in filename_lower:
        if "gravita" in filename_lower:
            return "RUSTIKA GRAVITA"
        if "tyrolien" in filename_lower:
            return "RUSTIKA TYROLIEN"
        if "assila" in filename_lower:
            return "RUSTIKA ASSILA"
        return "RUSTIKA"
    if "lika" in filename_lower:
        if "fina" in filename_lower:
            return "LIKA FINA"
        if "full" in filename_lower:
            return "LIKA FULL"
        return "LIKA"
    if "hydro" in filename_lower:
        if "facade" in filename_lower or "façade" in filename_lower:
            return "HYDRO-FAÇADE"
        return "HYDRO"
    if "isbaroc" in filename_lower:
        return "ISBAROC R"
    if "flex" in filename_lower:
        if "plus" in filename_lower:
            return "FLEX PLUS"
        return "FLEX"
    if "pro" in filename_lower:
        if "3000" in filename_lower:
            return "PRO 3000"
        if "2000" in filename_lower:
            return "PRO 2000"
        if "1000" in filename_lower:
            return "PRO 1000"
        if "200" in filename_lower:
            return "PRO 200"
        return "PRO"
    if "confort" in filename_lower:
        if "plus" in filename_lower:
            return "CONFORT PLUS"
        return "CONFORT"
    if "adhercol" in filename_lower:
        return "ADHERCOL P-3000"
    if "supcoat" in filename_lower:
        return "SUPCOAT M"
    if "suplastic" in filename_lower:
        return "SUPLASTIC"
    if "suplatex" in filename_lower:
        return "SUPLATEX"
    if "primer" in filename_lower:
        return "PRIMER CONTACT"
    if "suprotec" in filename_lower:
        return "SUPROTEC"
    if "jir" in filename_lower:
        return "JIR PRO ÉTANCHE"
    if "hydro-mur" in filename_lower:
        if "pro" in filename_lower:
            return "HYDROMUR PRO"
        if "r" in filename_lower and "b" not in filename_lower:
            return "HYDROMUR R"
        return "HYDROMUR B"
    if "champion" in filename_lower:
        return "CHAMPION 4 IN 1"
    if "murenduit" in filename_lower:
        if "rouge" in filename_lower:
            return "MURENDUIT CACHET ROUGE"
        if "vert" in filename_lower:
            return "MURENDUIT CACHET VERT"
        if "bleu" in filename_lower:
            return "MURENDUIT CACHET BLEU"
        return "MURENDUIT CACHET"
    if "ecocolle" in filename_lower:
        return "ECOCOLLE 100"
    if "finacem" in filename_lower:
        if "rouge" in filename_lower:
            return "FINACEM CACHET ROUGE"
        return "FINACEM CACHET BLEU"
    if "marbre" in filename_lower:
        return "MARBRE"
    if "pool" in filename_lower:
        return "POOL"
    if "piscine" in filename_lower:
        return "PISCINE"
    if "carreau" in filename_lower:
        return "CARREAU JOINT"
    if "supdur" in filename_lower or "supdur" in filename_lower:
        return "SUPCOAT M"

    if link_text and link_text.upper() != filename.upper():
        return _clean_text(link_text) or "Unknown"
    return filename or "Unknown"


class SofapScraper(BaseProductScraper):
    source = "sofap"

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
                logger.info("SOFAP: Discovered %d products on page %d (total: %d)",
                            len(batch), page, len(all_products))
                page += 1
        except Exception as exc:
            logger.error("SOFAP: Failed to discover products: %s", exc)
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
                raise ValueError(f"No SOFAP product found for {url}")

            product_data = products[0]
            product = _extract_product_from_api(product_data)
            product.category = _extract_category_names(product_data)

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
                logger.warning("SOFAP: Failed to fetch product page HTML for %s: %s", url, exc)

            return product
        except Exception as exc:
            logger.error("SOFAP: Failed to scrape product %s: %s", url, exc)
            raise

    def discover_documents(self, product: ProductCreate) -> list[dict[str, Any]]:
        documents: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        if product.document_urls:
            for doc_url in product.document_urls:
                if doc_url not in seen_urls:
                    seen_urls.add(doc_url)
                    documents.append({
                        "product_name": product.name,
                        "supplier": "SOFAP",
                        "document_url": doc_url,
                        "document_type": "technical_sheet",
                        "mime_type": "application/pdf",
                        "source_url": product.source_url or "",
                        "title": product.name,
                        "source_type": "official",
                        "confidence": "high",
                        "evidence": f"PDF link found on SOFAP product page for '{product.name}'",
                    })

        all_docs = _discover_doc_pages()
        product_slug = _slug_from_url(product.source_url or "")
        product_name_normalized = product.name.upper() if product.name else ""

        for doc in all_docs:
            if doc["document_url"] in seen_urls:
                continue

            doc_title = doc.get("title", "").upper()
            doc_url_lower = doc["document_url"].lower()
            doc_product = doc.get("product_name", "").upper()

            strong_match = False
            if product_name_normalized and (
                product_name_normalized in doc_title
                or product_name_normalized in doc_product
                or product_name_normalized in doc_url_lower
            ):
                strong_match = True

            if product_slug and product_slug in doc_url_lower:
                strong_match = True

            if strong_match:
                doc_copy = dict(doc)
                doc_copy["product_name"] = product.name
                doc_copy["source_type"] = "official"
                doc_copy["confidence"] = "high" if strong_match else "medium"
                doc_copy["evidence"] = f"Document from SOFAP documentation pages matches product '{product.name}'"
                documents.append(doc_copy)
                seen_urls.add(doc["document_url"])

        return documents

    def discover_all_documents(self) -> list[dict[str, Any]]:
        return _discover_doc_pages()


def save_raw_sample(products: list[ProductCreate], documents: list[dict[str, Any]]) -> str:
    raw_dir = AI_RAW_DIR / "sofap"
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
