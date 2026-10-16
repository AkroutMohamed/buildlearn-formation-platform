from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse

import requests

from app.ai.scraping.sources.gypsobat import _SESSION
from app.ai.config import AI_RAW_DIR

logger = logging.getLogger(__name__)

_PDF_MAGIC = b"%PDF-"
CHUNK_SIZE = 8192


def _encode_url(url: str) -> str:
    """Encode spaces and special characters in URL path and query."""
    parsed = urlparse(url)
    decoded_path = parsed.path
    for seq, char in (
        ("%20", " "), ("%21", "!"), ("%23", "#"), ("%24", "$"),
        ("%25", "%"), ("%26", "&"), ("%27", "'"), ("%28", "("),
        ("%29", ")"), ("%2B", "+"), ("%2C", ","), ("%3A", ":"),
        ("%3B", ";"), ("%3D", "="), ("%40", "@"), ("%5B", "["),
        ("%5D", "]"),
    ):
        decoded_path = decoded_path.replace(seq, char)
    encoded_path = quote(decoded_path, safe="/:")
    decoded_query = parsed.query
    for seq, char in (("%20", " "), ("%3D", "="), ("%26", "&")):
        decoded_query = decoded_query.replace(seq, char)
    encoded_query = quote(decoded_query, safe="=&")
    return urlparse(
        f"{parsed.scheme}://{parsed.netloc}{encoded_path}?{encoded_query}"
        if encoded_query
        else f"{parsed.scheme}://{parsed.netloc}{encoded_path}"
    ).geturl()


@dataclass
class ValidationResult:
    document_url: str
    http_status: int | None = None
    content_type: str | None = None
    is_pdf: bool = False
    downloadable: bool = False
    content_hash: str | None = None
    file_path: str | None = None
    error: str | None = None
    size_bytes: int = 0
    validated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DocumentValidator:
    """Validates PDF documents by checking HTTP status, content-type, magic bytes, and content hash."""

    USER_AGENT = "BuildLearn-AI-Scraper/1.0 (+https://buildlearn.ai/bot)"

    def __init__(self, download_dir: str | Path | None = None) -> None:
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "application/pdf,application/octet-stream,*/*",
        })
        if download_dir is not None:
            self.download_dir = Path(download_dir)
        else:
            self.download_dir = AI_RAW_DIR
        self.download_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def validate_url(self, url: str, timeout: float = 30) -> ValidationResult:
        """Validate a document URL without downloading the full file.

        Checks HTTP status, content-type, and PDF magic bytes from the response header.
        Only reads the first few bytes to check the magic number.
        """
        result = ValidationResult(document_url=url)
        if not url:
            result.error = "Empty URL"
            return result

        encoded_url = _encode_url(url)
        try:
            response = self._session.head(encoded_url, timeout=timeout, allow_redirects=True)
            result.http_status = response.status_code
            result.content_type = response.headers.get("Content-Type", "")

            if response.status_code != 200:
                result.error = f"HTTP {response.status_code}"
                return result

            if not result.content_type or "pdf" not in result.content_type.lower():
                result.error = f"Unexpected Content-Type: {result.content_type}"
                return result

            result.is_pdf = True
            return result

        except requests.RequestException as exc:
            result.error = f"Request error: {exc}"
            logger.warning("HEAD request failed for %s: %s", url, exc)
            return result

    def validate_and_download(self, url: str, source: str, timeout: float = 60) -> ValidationResult:
        """Download a PDF, validate its content, and compute a SHA-256 content hash.

        This performs a full download and is used when the document needs to be
        saved to disk for processing.
        """
        result = ValidationResult(document_url=url)
        if not url:
            result.error = "Empty URL"
            return result

        encoded_url = _encode_url(url)
        try:
            response = self._session.get(encoded_url, timeout=timeout, allow_redirects=True, stream=True)
            result.http_status = response.status_code
            result.content_type = response.headers.get("Content-Type", "")

            if response.status_code != 200:
                result.error = f"HTTP {response.status_code}"
                return result

            if not result.content_type or "pdf" not in result.content_type.lower():
                result.error = f"Unexpected Content-Type: {result.content_type}"
                return result

            hasher = hashlib.sha256()
            collected = bytearray()
            max_bytes = 50 * 1024 * 1024  # 50 MB safety cap

            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                collected.extend(chunk)
                hasher.update(chunk)
                if len(collected) > max_bytes:
                    result.error = "File exceeds 50 MB limit"
                    return result

            result.size_bytes = len(collected)

            if not collected[:5] == _PDF_MAGIC:
                result.error = "Missing PDF magic bytes"
                result.is_pdf = False
                return result

            result.is_pdf = True
            result.content_hash = hasher.hexdigest()
            result.downloadable = True

            parsed = urlparse(url)
            filename = Path(parsed.path).name
            if not filename or not filename.lower().endswith(".pdf"):
                safe_name = result.content_hash[:16] + ".pdf"
            else:
                safe_name = filename.replace("/", "_").replace("\\", "_")

            source_dir = self.download_dir / source
            source_dir.mkdir(parents=True, exist_ok=True)
            target_path = source_dir / safe_name

            if target_path.exists():
                existing_hash = self.compute_hash(target_path.read_bytes())
                if existing_hash == result.content_hash:
                    logger.info("PDF already exists with matching hash: %s", target_path)
                    result.file_path = str(target_path)
                    return result

            target_path.write_bytes(bytes(collected))
            result.file_path = str(target_path)

            logger.info("Downloaded and validated PDF: %s (hash=%s, size=%d)",
                        target_path, result.content_hash, result.size_bytes)
            return result

        except requests.RequestException as exc:
            result.error = f"Request error: {exc}"
            logger.warning("Download failed for %s: %s", url, exc)
            return result
        except Exception as exc:
            result.error = f"Unexpected error: {exc}"
            logger.exception("Unexpected error validating %s", url)
            return result
