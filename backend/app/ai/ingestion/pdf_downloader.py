from __future__ import annotations

import hashlib
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.ai.scraping.sources.gypsobat import _get as _scraper_get
from app.ai.config import AI_RAW_DIR

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.gypsobat.com"
_USER_AGENT = "BuildLearn-AI-Scraper/1.0 (+https://buildlearn.ai/bot)"
_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": _USER_AGENT, "Accept": "application/pdf,application/octet-stream,*/*"})

_DOWNLOAD_DIR = AI_RAW_DIR / "gypsobat" / "documents"
_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

_PDF_MAGIC = b"%PDF-"


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


def _safe_filename(name: str) -> str:
    name = name.strip().replace(" ", "_")
    name = re.sub(r"[^\w.\-]", "", name)
    return name or "document.pdf"


def _content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def _is_pdf(data: bytes, content_type: str | None) -> bool:
    if content_type and "pdf" not in content_type.lower():
        return False
    return data[:5] == _PDF_MAGIC


def download_pdf(document_url: str, *, timeout: int = 60) -> dict[str, Any]:
    if not document_url:
        raise ValueError("document_url is required")

    _rate_limiter.wait()
    logger.info("Downloading PDF: %s", document_url)

    response = _SESSION.get(document_url, timeout=timeout, allow_redirects=True)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")
    raw_bytes = response.content

    if not _is_pdf(raw_bytes, content_type):
        raise ValueError(f"Downloaded content is not a PDF: {document_url} (Content-Type: {content_type})")

    filename = _safe_filename(Path(urlparse(document_url).path).name)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    target_path = _DOWNLOAD_DIR / filename
    if target_path.exists():
        existing_hash = _content_hash(target_path.read_bytes())
        new_hash = _content_hash(raw_bytes)
        if existing_hash == new_hash:
            logger.info("PDF already exists with matching hash: %s", target_path)
            return {
                "document_url": document_url,
                "file_path": str(target_path),
                "filename": filename,
                "content_hash": existing_hash,
                "size_bytes": target_path.stat().st_size,
                "content_type": "application/pdf",
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
            }
        stem = target_path.stem
        suffix = target_path.suffix
        target_path = _DOWNLOAD_DIR / f"{stem}_{new_hash}{suffix}"

    target_path.write_bytes(raw_bytes)
    content_hash = _content_hash(raw_bytes)

    logger.info("Saved PDF to %s (hash=%s, size=%d)", target_path, content_hash, len(raw_bytes))

    return {
        "document_url": document_url,
        "file_path": str(target_path),
        "filename": filename,
        "content_hash": content_hash,
        "size_bytes": len(raw_bytes),
        "content_type": "application/pdf",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
    }
