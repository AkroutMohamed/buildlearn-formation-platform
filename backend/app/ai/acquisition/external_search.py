from __future__ import annotations

import logging
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode, urljoin, urlparse

import warnings
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning


def _parse_sitemap(text: str) -> BeautifulSoup:
    """Parse a sitemap XML document, suppressing the HTML-parser advisory.

    Sitemaps carry a default XML namespace (``xmlns="http://www.sitemaps.org/.../0.9"``).
    ``html.parser`` resolves ``<loc>`` and ``<sitemap>`` tags namespace-agnostically,
    which is more reliable here than the lxml ``xml`` builder (which would require
    explicit namespace handling and would silently drop bare-name ``find_all`` calls).
    The BeautifulSoup advisory is therefore intentionally suppressed for sitemap XML.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", XMLParsedAsHTMLWarning)
        return BeautifulSoup(text, "html.parser")


logger = logging.getLogger(__name__)


@dataclass
class SearchCandidate:
    """A candidate document discovered via external search."""
    title: str
    url: str
    domain: str
    source_type: str
    confidence: str
    evidence: str
    product_name: str | None = None
    http_status: int | None = None
    content_type: str | None = None
    content_hash: str | None = None
    downloaded: bool = False
    processed: bool = False
    discovery_provider: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "domain": self.domain,
            "source_type": self.source_type,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "product_name": self.product_name,
            "http_status": self.http_status,
            "content_type": self.content_type,
            "content_hash": self.content_hash,
            "downloaded": self.downloaded,
            "processed": self.processed,
            "discovery_provider": self.discovery_provider,
        }


class BaseExternalSearcher(ABC):
    """Abstract base for external search implementations."""

    @property
    def provider_status(self) -> str:
        return "ok"

    @abstractmethod
    def search(self, query: str, max_results: int = 20) -> list[SearchCandidate]:
        ...


class WebExternalSearcher(BaseExternalSearcher):
    """Performs web searches using DuckDuckGo's HTML interface."""

    USER_AGENT = "BuildLearn-AI-Scraper/1.0 (+https://buildlearn.ai/bot)"
    BASE_URL = "https://html.duckduckgo.com/html/"

    def __init__(self, rate_limit: float = 1.0) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        self._session.max_redirects = 5
        self._rate_limit = rate_limit
        self._last_request: float = 0.0
        self._provider_status: str = "ok"

    @property
    def provider_status(self) -> str:
        return self._provider_status

    def _wait(self) -> None:
        now = time.time()
        delta = now - self._last_request
        if delta < self._rate_limit:
            time.sleep(self._rate_limit - delta)
        self._last_request = time.time()

    def search(self, query: str, max_results: int = 20) -> list[SearchCandidate]:
        """Search DuckDuckGo and return parsed results.

        Each result is classified with a confidence level based on domain
        and result characteristics.
        """
        self._wait()
        params = {"q": query, "kl": "us-en"}
        try:
            response = self._session.get(self.BASE_URL, params=params, timeout=(10, 30), allow_redirects=True)
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.warning("External search failed for '%s': %s", query, exc)
            self._provider_status = "unavailable"
            return []

        if response.status_code == 202 or "anomaly.js" in response.text:
            logger.warning("DuckDuckGo returned anti-bot challenge for query: %s", query)
            self._provider_status = "blocked"
            return []

        if not response.text or "<div class=\"result\"" not in response.text:
            self._provider_status = "ok"
            return []

        self._provider_status = "ok"
        return self._parse_results(response.text, max_results)

    def _parse_results(self, html: str, max_results: int) -> list[SearchCandidate]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[SearchCandidate] = []

        result_blocks = soup.find_all("div", class_="result")
        if not result_blocks:
            result_divs = soup.find_all("div", attrs={"class": re.compile(r"^\S*result\S*$")})
            result_blocks = result_divs

        for block in result_blocks[:max_results]:
            title_tag = block.find("a", class_="result__a")
            if not title_tag:
                title_tag = block.find("a", href=True)
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True) or ""
            url = title_tag.get("href", "")

            snippet_tag = block.find("a", class_="result__snippet")
            if snippet_tag:
                snippet = snippet_tag.get_text(strip=True) or ""
            else:
                snippet_div = block.find("div", class_="result__snippet")
                snippet = snippet_div.get_text(strip=True) if snippet_div else ""

            if not url or not url.startswith("http"):
                continue

            domain = self._extract_domain(url)
            source_type, confidence, evidence = self._classify_search_result(
                title, snippet, url, domain
            )

            results.append(SearchCandidate(
                title=title,
                url=url,
                domain=domain,
                source_type=source_type,
                confidence=confidence,
                evidence=evidence,
            ))

        return results

    @staticmethod
    def _extract_domain(url: str) -> str:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc

    def _classify_search_result(
        self, title: str, snippet: str, url: str, domain: str
    ) -> tuple[str, str, str]:
        """Classify a search result into source_type and confidence level.

        Returns (source_type, confidence, evidence)
        """
        combined = (title + " " + snippet).lower()
        domain_lower = domain.lower()

        # Official manufacturer / brand domains
        known_official = [
            "gypsobat.com", "gyproc.com", "siniat.com", "tacer.com",
            "sofap-poudre.com", "sofapbatiment.com",
            "emtop.com", "emtoptunisie.com",
            "sips-platre.com",
            "comptoir-hammami.com",
        ]

        is_official = any(d in domain_lower for d in known_official)

        if is_official:
            if ".pdf" in url.lower() or "fiche" in combined or "pdf" in combined:
                return "external_official", "high", (
                    f"Document from official manufacturer/supplier domain '{domain}'. "
                    f"Title contains: '{title[:100]}'"
                )
            return "external_official", "medium", (
                f"Page from official domain '{domain}' but no direct PDF link in result. "
                f"Requires clicking through to verify."
            )

        # Trusted distributor / reseller domains
        trusted_distributors = [
            "comptoir-hammami.com", "btp-distribution.com",
            "leroymerlin", "castorama", "pointp", "gbh",
        ]
        is_distributor = any(d in domain_lower for d in trusted_distributors)

        if is_distributor:
            if ".pdf" in url.lower():
                return "external_distributor", "medium", (
                    f"PDF from trusted distributor '{domain}'. "
                    f"Title contains: '{title[:100]}'"
                )
            return "external_distributor", "medium", (
                f"Page from distributor '{domain}' but no direct PDF link. "
                f"Requires clicking through to verify."
            )

        # Everything else is low confidence
        if ".pdf" in url.lower():
            return "third_party", "low", (
                f"PDF from unverified third-party domain '{domain}'. "
                f"No verified manufacturer relationship."
            )

        return "third_party", "low", (
            f"Search result from unverified domain '{domain}'. "
            f"Title: '{title[:100]}'"
        )


_VERIFIED_MANUFACTURER_DOMAINS: dict[str, list[str]] = {
    "GYPROC": ["gyproc.com", "gyproc.in", "www.gyproc.in"],
    "SINIAT": ["siniat.com"],
    "TACER": ["tacer.com"],
    "SOFAP": ["sofap-poudre.com", "sofapbatiment.com"],
    "EMTOP": ["emtop.com", "emtoptunisie.com"],
    "SIPS": ["sips-platre.com"],
    "GYPSOBAT": ["gypsobat.com"],
}

_MANUFACTURER_PATHS: dict[str, list[str]] = {
    "TACER": ["/documents", "/en/documents", "/tr/documents"],
    "SINIAT": ["/documentation/", "/en-gb/documentation/", "/fr-fr/documentation/"],
    "GYPROC": ["/resources-downloads", "/pdf/", "/pdf-sitemap.xml"],
    "SOFAP": ["/produits/", "/productos/"],
}

_DOCUMENT_HOSTS: dict[str, list[str]] = {
    "SINIAT": ["media.siniat.com", "media.siniat.fr"],
    "GYPROC": ["cdn.prod.sgds.io", "dam.pim-cps.saint-gobain.com"],
    "RIGIPS": ["api.industriedatenpool.com", "rigips.ch"],
}

_GYPROC_ALIASES: dict[str, list[str]] = {
    "BA13 Hydro": ["moisture resistant board", "duraline"],
    "BA13 Feu": ["fireline"],
    "BA13 Standard": ["plain board", "gypboard plain"],
}


def is_gyproc_alias_match(candidate: SearchCandidate, product_name: str) -> bool:
    """Check if a candidate matches a GYPROC product alias."""
    if not product_name:
        return False
    aliases = _GYPROC_ALIASES.get(product_name.strip(), [])
    if not aliases:
        return False
    candidate_text = (candidate.title + " " + candidate.evidence + " " + candidate.url).lower()
    normalized_text = candidate_text.replace("_", " ").replace("-", " ")
    return any(alias in normalized_text for alias in aliases)


class ManufacturerTargetedSearcher(BaseExternalSearcher):
    """Discovers documents by targeting known manufacturer domains.

    Uses verified manufacturer-to-domain mappings to directly crawl
    official domains for technical document PDFs.
    """

    USER_AGENT = "BuildLearn-AI-Scraper/1.0 (+https://buildlearn.ai/bot)"
    COMMON_PATHS = [
        "/fiche-technique/",
        "/technical-datasheet/",
        "/documents/",
        "/downloads/",
        "/wp-content/uploads/",
    ]

    def __init__(self, manufacturer: str, product_name: str, model: str | None = None, rate_limit: float = 1.0) -> None:
        self._manufacturer = manufacturer.upper()
        self._product_name = product_name.strip()
        self._model = model.strip() if model else None
        self._rate_limit = rate_limit
        self._last_request: float = 0.0
        self._provider_status: str = "ok"
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        self._session.max_redirects = 5
        self._domains = _VERIFIED_MANUFACTURER_DOMAINS.get(self._manufacturer, [])
        self._manufacturer_paths = _MANUFACTURER_PATHS.get(self._manufacturer, [])
        self._document_hosts = _DOCUMENT_HOSTS.get(self._manufacturer, [])

    @property
    def provider_status(self) -> str:
        return self._provider_status

    def _wait(self) -> None:
        now = time.time()
        delta = now - self._last_request
        if delta < self._rate_limit:
            time.sleep(self._rate_limit - delta)
        self._last_request = time.time()

    def search(self, query: str, max_results: int = 20) -> list[SearchCandidate]:
        """Search verified manufacturer domains for document PDFs."""
        if not self._domains:
            logger.info("No verified domains for manufacturer %s", self._manufacturer)
            self._provider_status = "ok"
            return []

        candidates: list[SearchCandidate] = []
        product_tokens = set(re.findall(r"\w+", self._product_name.lower()))
        model_tokens = set(re.findall(r"\w+", self._model.lower())) if self._model else set()

        all_paths = list(self.COMMON_PATHS)
        all_paths.extend(self._manufacturer_paths)
        unique_paths: list[str] = []
        seen_paths: set[str] = set()
        for p in all_paths:
            if p not in seen_paths:
                seen_paths.add(p)
                unique_paths.append(p)

        for domain in self._domains[:3]:
            if len(candidates) >= max_results:
                break

            self._wait()
            try:
                sitemap_candidates = self._search_sitemap(domain, product_tokens, model_tokens)
                candidates.extend(sitemap_candidates)
            except Exception as exc:
                logger.debug("Sitemap search failed for %s: %s", domain, exc)

            if len(candidates) >= max_results:
                break

            for path in unique_paths[:6]:
                if len(candidates) >= max_results:
                    break
                self._wait()
                try:
                    page_candidates = self._search_page(domain, path, product_tokens, model_tokens)
                    candidates.extend(page_candidates)
                except Exception as exc:
                    logger.debug("Page search failed for %s%s: %s", domain, path, exc)

        for doc_host in self._document_hosts[:2]:
            if len(candidates) >= max_results:
                break
            self._wait()
            try:
                host_candidates = self._search_document_host(doc_host, product_tokens, model_tokens)
                candidates.extend(host_candidates)
            except Exception as exc:
                logger.debug("Document host search failed for %s: %s", doc_host, exc)

        seen_urls: set[str] = set()
        unique: list[SearchCandidate] = []
        for cand in candidates[:max_results]:
            if cand.url not in seen_urls:
                seen_urls.add(cand.url)
                unique.append(cand)

        self._provider_status = "ok" if candidates else "ok"
        return unique

    def _search_sitemap(self, domain: str, product_tokens: set[str], model_tokens: set[str]) -> list[SearchCandidate]:
        candidates: list[SearchCandidate] = []
        sitemap_candidates = self._fetch_sitemap_for_domain(domain, product_tokens, model_tokens)
        candidates.extend(sitemap_candidates)

        for path in self._manufacturer_paths:
            if not path.endswith(".xml"):
                continue
            sitemap_url = f"https://{domain}{path}"
            self._wait()
            try:
                sub_candidates = self._fetch_sitemap(sitemap_url, domain, product_tokens, model_tokens)
                candidates.extend(sub_candidates)
            except Exception as exc:
                logger.debug("Manufacturer sitemap fetch failed for %s: %s", sitemap_url, exc)

        seen_urls: set[str] = set()
        unique: list[SearchCandidate] = []
        for cand in candidates:
            if cand.url not in seen_urls:
                seen_urls.add(cand.url)
                unique.append(cand)
        return unique

    def _fetch_sitemap_for_domain(self, domain: str, product_tokens: set[str], model_tokens: set[str]) -> list[SearchCandidate]:
        candidates: list[SearchCandidate] = []
        sitemap_url = f"https://{domain}/sitemap.xml"
        self._wait()
        try:
            response = self._session.get(sitemap_url, timeout=(10, 30))
            if response.status_code != 200:
                return candidates
        except requests.RequestException:
            return candidates

        soup = _parse_sitemap(response.text)
        sitemap_urls = [loc.get_text(strip=True) for loc in soup.find_all("sitemap") if loc.get_text(strip=True)]
        if sitemap_urls:
            for sitemap_url in sitemap_urls[:3]:
                self._wait()
                try:
                    sub_candidates = self._fetch_sitemap(sitemap_url, domain, product_tokens, model_tokens)
                    candidates.extend(sub_candidates)
                except Exception as exc:
                    logger.debug("Sub-sitemap fetch failed for %s: %s", sitemap_url, exc)
        else:
            urls = [loc.get_text(strip=True) for loc in soup.find_all("loc") if loc.get_text(strip=True)]
            for url in urls:
                if not url.lower().endswith(".pdf"):
                    continue
                url_tokens = set(re.findall(r"\w+", url.lower()))
                overlap = product_tokens & url_tokens
                model_overlap = model_tokens & url_tokens
                alias_match = self._is_gyproc_alias_match(url)
                if overlap or model_overlap or self._matches_product_name(url) or alias_match:
                    confidence = "high" if (overlap and len(overlap) >= 2) or model_overlap or alias_match else "medium"
                    candidates.append(SearchCandidate(
                        title=self._extract_filename(url),
                        url=url,
                        domain=domain,
                        source_type="external_official",
                        confidence=confidence,
                        evidence=f"Found in sitemap for {domain}; matches product tokens",
                        product_name=self._product_name,
                        discovery_provider="manufacturer_targeted",
                    ))
        return candidates

    def _fetch_sitemap(self, sitemap_url: str, domain: str, product_tokens: set[str], model_tokens: set[str]) -> list[SearchCandidate]:
        candidates: list[SearchCandidate] = []
        self._wait()
        try:
            response = self._session.get(sitemap_url, timeout=(10, 30))
            if response.status_code != 200:
                return candidates
        except requests.RequestException:
            return candidates

        soup = _parse_sitemap(response.text)
        urls = [loc.get_text(strip=True) for loc in soup.find_all("loc") if loc.get_text(strip=True)]

        for url in urls:
            if not url.lower().endswith(".pdf"):
                continue
            url_tokens = set(re.findall(r"\w+", url.lower()))
            overlap = product_tokens & url_tokens
            model_overlap = model_tokens & url_tokens
            alias_match = self._is_gyproc_alias_match(url)
            if overlap or model_overlap or self._matches_product_name(url) or alias_match:
                confidence = "high" if (overlap and len(overlap) >= 2) or model_overlap or alias_match else "medium"
                candidates.append(SearchCandidate(
                    title=self._extract_filename(url),
                    url=url,
                    domain=domain,
                    source_type="external_official",
                    confidence=confidence,
                    evidence=f"Found in sitemap for {domain}; matches product tokens",
                    product_name=self._product_name,
                    discovery_provider="manufacturer_targeted",
                ))
        return candidates

    def _search_page(self, domain: str, path: str, product_tokens: set[str], model_tokens: set[str]) -> list[SearchCandidate]:
        candidates: list[SearchCandidate] = []
        encoded_path = quote(path, safe="/:")
        page_url = f"https://{domain}{encoded_path}"
        self._wait()
        try:
            response = self._session.get(page_url, timeout=(10, 30))
            if response.status_code != 200:
                return candidates
        except requests.RequestException:
            return candidates

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            href = link.get("href", "")
            if not href.lower().endswith(".pdf"):
                continue
            doc_url = urljoin(page_url, href)
            if not doc_url.startswith(f"https://{domain}"):
                continue

            link_text = link.get_text(strip=True) or ""
            url_tokens = set(re.findall(r"\w+", doc_url.lower()))
            text_tokens = set(re.findall(r"\w+", link_text.lower()))
            overlap = product_tokens & (url_tokens | text_tokens)
            model_overlap = model_tokens & (url_tokens | text_tokens)
            alias_match = self._is_gyproc_alias_match(link_text) or self._is_gyproc_alias_match(doc_url)

            if overlap or model_overlap or self._matches_product_name(link_text) or self._matches_product_name(doc_url) or alias_match:
                confidence = "high" if (overlap and len(overlap) >= 2) or model_overlap or alias_match else "medium"
                candidates.append(SearchCandidate(
                    title=link_text or self._extract_filename(doc_url),
                    url=doc_url,
                    domain=domain,
                    source_type="external_official",
                    confidence=confidence,
                    evidence=f"Found on {page_url}; matches product tokens",
                    product_name=self._product_name,
                    discovery_provider="manufacturer_targeted",
                ))
        return candidates

    def _search_document_host(self, doc_host: str, product_tokens: set[str], model_tokens: set[str]) -> list[SearchCandidate]:
        candidates: list[SearchCandidate] = []
        host_url = f"https://{doc_host}/"
        self._wait()
        try:
            response = self._session.get(host_url, timeout=(10, 30))
            if response.status_code != 200:
                return candidates
        except requests.RequestException:
            return candidates

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        for link in links:
            href = link.get("href", "")
            if not href.lower().endswith(".pdf"):
                continue
            doc_url = urljoin(host_url, href)
            if not doc_url.startswith(f"https://{doc_host}"):
                continue

            link_text = link.get_text(strip=True) or ""
            url_tokens = set(re.findall(r"\w+", doc_url.lower()))
            text_tokens = set(re.findall(r"\w+", link_text.lower()))
            overlap = product_tokens & (url_tokens | text_tokens)
            model_overlap = model_tokens & (url_tokens | text_tokens)
            alias_match = self._is_gyproc_alias_match(link_text) or self._is_gyproc_alias_match(doc_url)

            if overlap or model_overlap or self._matches_product_name(link_text) or self._matches_product_name(doc_url) or alias_match:
                confidence = "high" if (overlap and len(overlap) >= 2) or model_overlap or alias_match else "medium"
                candidates.append(SearchCandidate(
                    title=link_text or self._extract_filename(doc_url),
                    url=doc_url,
                    domain=doc_host,
                    source_type="external_official",
                    confidence=confidence,
                    evidence=f"Found on document host {doc_host}; matches product tokens",
                    product_name=self._product_name,
                    discovery_provider="manufacturer_targeted",
                ))
        return candidates

    def _matches_product_name(self, text: str) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        product_lower = self._product_name.lower()
        if product_lower in text_lower:
            return True
        if self._model and self._model.lower() in text_lower:
            return True
        return False

    def _is_gyproc_alias_match(self, text: str) -> bool:
        if self._manufacturer != "GYPROC":
            return False
        aliases = _GYPROC_ALIASES.get(self._product_name.strip(), [])
        if not aliases:
            return False
        text_lower = text.lower()
        normalized_text = text_lower.replace("_", " ").replace("-", " ")
        return any(alias in normalized_text for alias in aliases)

    @staticmethod
    def _extract_filename(url: str) -> str:
        parsed = urlparse(url)
        filename = Path(parsed.path).name
        return filename or url


def build_search_queries(product_name: str, model: str | None = None, manufacturer: str | None = None) -> list[str]:
    """Build a list of search queries for external document discovery."""
    queries: list[str] = []

    base = product_name.strip()
    if model:
        model = model.strip()

    if manufacturer:
        mfg_queries = [
            f'"{base}" {manufacturer} technical datasheet PDF',
            f'"{base}" {manufacturer} fiche technique PDF',
        ]
        if model:
            mfg_queries.extend([
                f'"{model}" {manufacturer} technical datasheet PDF',
                f'"{model}" {manufacturer} fiche technique PDF',
            ])
        queries.extend(mfg_queries)

    query_templates = [
        "{name} fiche technique PDF",
        "{name} fiche technique",
        "{name} technical data sheet",
        "{name} PDF",
        "{name} manufacturer",
    ]

    for template in query_templates:
        name_part = base if "{name}" in template else template
        if model:
            query = template.replace("{name}", base).replace("{name}", model)
            queries.append(query)
        else:
            query = template.replace("{name}", base)
        queries.append(query)

    if model:
        model_queries = [
            f"{model} PDF",
            f"{model} fiche technique",
            f"{model} technical data sheet",
            f"{base} {model} fiche technique PDF",
        ]
        queries.extend(model_queries)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique.append(q)
    return unique
