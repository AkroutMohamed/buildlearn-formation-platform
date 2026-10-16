from __future__ import annotations

import hashlib
import logging
import os
import re
import time
import unicodedata
from datetime import datetime, timezone
from typing import Any
from urllib.parse import unquote, urljoin

import requests
from bs4 import BeautifulSoup

from app.ai.scraping.base import BaseProductScraper
from app.ai.schemas.document import DocumentCreate
from app.ai.schemas.product import ProductCreate
from app.ai.config import AI_RAW_DIR

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.gypsobat.com"
_USER_AGENT = "BuildLearn-AI-Scraper/1.0 (+https://buildlearn.ai/bot)"
_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": _USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})

_PRODUCTS_API = urljoin(_BASE_URL, "/wp-json/wp/v2/product")
_DOC_PAGES = [
    "/fiche-technique-systemes-humides/",
    "/fiche-technique-systemes-humides-exterieur/",
    "/bordereau-type-systemes-humides/",
    "/certifications-systemes-humides/",
    "/dossiers-techniques/",
    "/dossiers-techniques/dossier-technique-gyproc/",
    "/dossiers-techniques/dossier-technique-siniat/",
    "/dossiers-techniques/dossier-technique-tacer/",
    "/dossiers-techniques/plafonds-demontables-en-laine/",
    "/dossiers-techniques/plafonds-demontables-metalliques-thu/",
]

PRODUCT_ALIASES: dict[str, list[str]] = {
    "ba13-hydro": [
        "BA13 Hydro",
        "BA13 Hydrofuge",
        "BA13 hydrofuge",
        "HYDRO 13",
        "Hydro 13",
    ],
    "ba13-feu-2": [
        "BA13 Feu",
        "BA13 feu",
        "FIRELINE 13",
        "Fireline 13",
    ],
    "ba13-standard-2": [
        "BA13 Standard",
        "BA13 standard",
        "Wallboard 13",
        "WALLBOARD 13",
    ],
    "ba6-flex": [
        "BA6 Flex",
        "BA6 flex",
    ],
    "lika-pap-90": [
        "LIKA PAP 90",
        "Lika PAP90",
        "Lika Pap90",
        "LIKA PAP90",
    ],
}


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


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


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


def _normalize_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower()
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    name = name.replace("_", " ")
    name = re.sub(r"[^\w\s-]", " ", name)
    name = re.sub(r"[-\s]+", " ", name).strip()
    return name


def _slug_from_url(url: str) -> str:
    if not url:
        return ""
    return url.rstrip("/").split("/")[-1]


def _filename_tokens(url: str) -> set[str]:
    if not url:
        return set()
    filename = url.split("/")[-1].lower()
    filename = unquote(filename)
    filename = filename.replace(".pdf", "").replace(".doc", "").replace(".zip", "")
    filename = filename.replace("_", " ")
    tokens = re.sub(r"[^\w\s]", " ", filename).split()
    return set(tokens)


def _extract_category_names(product_data: dict[str, Any]) -> tuple[str | None, str | None]:
    category_ids = product_data.get("product_cat", [])
    if not category_ids:
        return None, None
    try:
        cats = _get(_BASE_URL + "/wp-json/wp/v2/product_cat", params={"include": ",".join(map(str, category_ids))}).json()
        if isinstance(cats, dict) and "id" in cats:
            cats = [cats]
        names = [c.get("name", "") for c in cats if c.get("name")]
        if not names:
            return None, None
        return names[0], names[1] if len(names) > 1 else None
    except Exception as exc:  # pragma: no cover - network fallback
        logger.debug("Failed to fetch categories: %s", exc)
        return None, None


def _extract_product_from_api(product_data: dict[str, Any]) -> ProductCreate:
    title = _clean_text(product_data.get("title", {}).get("rendered", "")) or "Unknown"
    content = _strip_html(product_data.get("content", {}).get("rendered", "")) or ""
    excerpt = _strip_html(product_data.get("excerpt", {}).get("rendered", "")) or ""
    link = product_data.get("link", "")
    category, subcategory = _extract_category_names(product_data)

    product_slug = _slug_from_url(link)
    return ProductCreate(
        product_id=str(product_data.get("id", "")),
        name=title,
        brand=None,
        manufacturer=_infer_manufacturer(title, product_slug),
        category=category,
        subcategory=subcategory,
        description=excerpt or content or None,
        applications=None,
        technical_specifications=None,
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


def _infer_document_type(link_text: str, fallback: str) -> str:
    text = link_text.lower()
    if "fiche technique" in text or "fiche produit" in text or "bordereau" in text:
        return "technical_sheet"
    if "certification" in text or "certificat" in text:
        return "certificate"
    if "brochure" in text:
        return "brochure"
    if "pr" in text and "sentation" in text:
        return "presentation"
    if "catalogue" in text:
        return "catalogue"
    if "guide de pose" in text or "carnet de pose" in text:
        return "installation_guide"
    if "documentation" in text:
        return "documentation"
    return fallback


def _parse_doc_table(page_url: str, doc_type_hint: str, html: str | None = None) -> list[dict[str, Any]]:
    if html is None:
        try:
            response = _get(page_url)
        except Exception as exc:
            logger.warning("Failed to fetch doc page %s: %s", page_url, exc)
            return []
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        soup = BeautifulSoup(html, "html.parser")
    documents: list[dict[str, Any]] = []

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue
        rows = rows[1:]  # skip header row
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            if len(cells) >= 4:
                product_name = _clean_text(cells[1].get_text()) or "Unknown"
                supplier = _clean_text(cells[2].get_text()) or "Gypsobat"
                doc_cell = cells[3]
            else:
                product_name = _clean_text(cells[0].get_text()) or "Unknown"
                supplier = _clean_text(cells[1].get_text()) or "Gypsobat"
                doc_cell = cells[2]

            links = doc_cell.find_all("a", href=True)
            for link_tag in links:
                doc_url = urljoin(_BASE_URL, link_tag["href"])
                mime_type = "application/pdf" if doc_url.lower().endswith(".pdf") else None
                link_text = _clean_text(link_tag.get_text()) or "Document"
                document_type = _infer_document_type(link_text, doc_type_hint)
                documents.append(
                    {
                        "product_name": product_name,
                        "supplier": supplier,
                        "document_url": doc_url,
                        "document_type": document_type,
                        "mime_type": mime_type,
                        "source_url": page_url,
                        "title": link_text,
                        "source_type": "official",
                        "confidence": "medium",
                        "evidence": f"Explicit product name '{product_name}' in {'table row' if tables else 'page anchor'}; link text '{link_text}'",
                    }
                )

    if not documents:
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if href.lower().endswith(".pdf"):
                doc_url = urljoin(_BASE_URL, href)
                documents.append(
                    {
                        "product_name": _clean_text(anchor.get_text()) or "Unknown",
                        "supplier": "Gypsobat",
                        "document_url": doc_url,
                        "document_type": doc_type_hint,
                        "mime_type": "application/pdf",
                        "source_url": page_url,
                        "title": _clean_text(anchor.get_text()) or doc_type_hint,
                        "source_type": "official",
                        "confidence": "medium",
                        "evidence": f"PDF link found via fallback anchor scan on {page_url}",
                    }
                )
    return documents


def _discover_all_documents() -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for page_path in _DOC_PAGES:
        page_url = urljoin(_BASE_URL, page_path)
        if page_path.endswith("fiche-technique-systemes-humides/"):
            doc_type = "technical_sheet"
        elif page_path.endswith("fiche-technique-systemes-humides-exterieur/"):
            doc_type = "technical_sheet"
        elif page_path.endswith("bordereau-type-systemes-humides/"):
            doc_type = "technical_sheet"
        elif page_path.endswith("certifications-systemes-humides/"):
            doc_type = "certificate"
        elif page_path.endswith("dossiers-techniques/"):
            doc_type = "technical_dossier"
        else:
            doc_type = "other"

        docs = _parse_doc_table(page_url, doc_type)
        for doc in docs:
            if doc["document_url"] not in seen_urls:
                seen_urls.add(doc["document_url"])
                documents.append(doc)
    return documents


_ALL_DOCUMENTS: list[dict[str, Any]] | None = None


def _get_all_documents() -> list[dict[str, Any]]:
    global _ALL_DOCUMENTS
    if _ALL_DOCUMENTS is None:
        _ALL_DOCUMENTS = _discover_all_documents()
    return _ALL_DOCUMENTS


_KNOWN_BRANDS = frozenset({
    "EMTOP",
    "GYPROC",
    "LIKA",
    "SINIAT",
    "SOFAP",
    "SIPS",
    "TACER",
})

_BRAND_TOKENS: dict[str, list[str]] = {
    "GYPROC": ["gyproc"],
    "SINIAT": ["siniat"],
    "LIKA": ["lika"],
    "SIPS": ["sips"],
    "SOFAP": ["sofap"],
    "TACER": ["tacer"],
    "RIGIPS": ["rigips"],
    "SEMIN": ["semin"],
    "AKIFIX": ["akifix"],
    "EUROCOUSTIC": ["eurocoustic"],
    "THU": ["thu"],
    "EMTOP": ["emtop"],
}


def _infer_manufacturer(product_name: str, product_slug: str) -> str:
    normalized = _normalize_name(product_name + " " + product_slug)
    for brand, tokens in _BRAND_TOKENS.items():
        for token in tokens:
            if token in normalized:
                return brand
    return "Gypsobat"


def _is_conflicting_supplier(doc_supplier: str | None, product_manufacturer: str) -> bool:
    if not doc_supplier:
        return False
    supplier_upper = doc_supplier.strip().upper()
    manufacturer_upper = product_manufacturer.strip().upper()
    if supplier_upper == "GYPOBAT":
        return False
    for brand in _KNOWN_BRANDS:
        if brand in supplier_upper:
            return brand not in manufacturer_upper
    return False


def _match_documents(product: ProductCreate, all_documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not product.name or not all_documents:
        return []

    product_slug = _slug_from_url(product.source_url or "")
    normalized_product = _normalize_name(product.name)
    aliases = PRODUCT_ALIASES.get(product_slug, [])
    alias_normalized = {_normalize_name(a) for a in aliases}
    product_tokens = set(normalized_product.split())
    product_manufacturer = getattr(product, "manufacturer", None) or "Gypsobat"

    matched: list[dict[str, Any]] = []
    for doc in all_documents:
        doc_name = doc.get("product_name", "")
        normalized_doc = _normalize_name(doc_name)
        doc_url = doc.get("document_url", "")
        doc_filename_tokens = _filename_tokens(doc_url)
        doc_supplier = _clean_text(doc.get("supplier")) or ""

        confidence = None

        if normalized_doc == normalized_product:
            confidence = "high"

        elif normalized_doc in alias_normalized:
            confidence = "high"

        elif product_slug:
            slug_no_dash = product_slug.replace("-", "")
            doc_name_no_separators = normalized_doc.replace("-", "").replace("_", "").replace(" ", "")
            if slug_no_dash in doc_name_no_separators:
                confidence = "medium"

        if confidence is None and product_tokens and doc_filename_tokens:
            overlap = product_tokens & doc_filename_tokens
            if overlap == product_tokens:
                confidence = "medium"
            elif len(overlap) >= 2 and len(overlap) / len(product_tokens) >= 0.7:
                confidence = "medium"

        if confidence == "high":
            matched.append({**doc, "match_confidence": confidence})
        elif confidence == "medium" and not _is_conflicting_supplier(doc_supplier, product_manufacturer):
            matched.append({**doc, "match_confidence": confidence})

    return matched


class GypsobatScraper(BaseProductScraper):
    source = "gypsobat"

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
                logger.info("Discovered %d products on page %d (total: %d)", len(batch), page, len(all_products))
                page += 1
        except Exception as exc:
            logger.error("Failed to discover products: %s", exc)
            return all_products or []

        return all_products

    def scrape_product(self, url: str) -> ProductCreate:
        api_url = urljoin(_BASE_URL, "/wp-json/wp/v2/product")
        try:
            response = _get(api_url, params={"slug": url.rstrip("/").split("/")[-1]})
            products = response.json()
            if isinstance(products, dict) and "id" in products:
                products = [products]
            if not products:
                raise ValueError(f"No product found for {url}")
            return _extract_product_from_api(products[0])
        except Exception as exc:
            logger.error("Failed to scrape product %s: %s", url, exc)
            raise

    def discover_documents(self, product: ProductCreate) -> list[dict[str, Any]]:
        all_docs = _get_all_documents()
        matched = _match_documents(product, all_docs)
        for doc in matched:
            doc["source_type"] = doc.get("source_type", "official")
            doc["evidence"] = doc.get("evidence", doc.get("association_evidence", "Matched via Gypsobat documentation pages"))
        return matched

    def discover_all_documents(self) -> list[dict[str, Any]]:
        """Return all discovered documents from documentation pages across the site.

        Each document dict includes source_type and confidence fields.
        """
        all_docs = _get_all_documents()
        for doc in all_docs:
            doc.setdefault("source_type", "official")
            doc.setdefault("confidence", "medium")
        return all_docs


def save_raw_sample(products: list[ProductCreate], documents: list[dict[str, Any]]) -> str:
    raw_dir = AI_RAW_DIR / "gypsobat"
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
