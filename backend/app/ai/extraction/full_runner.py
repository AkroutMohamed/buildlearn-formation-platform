from __future__ import annotations

import hashlib
import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import fitz

from app.ai.extraction.schema import CanonicalDocument, CanonicalPage
from app.ai.extraction.router import ExtractionRouter, route_page
from app.ai.ingestion.pdf_inspector import PdfInspector
from app.ai.extraction.renderer import render_document

logger = logging.getLogger(__name__)


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class DocumentResult:
    pdf_path: str
    status: str
    document_id: str | None = None
    error: str | None = None
    output_json: str | None = None
    output_markdown: str | None = None


class FullRunner:
    def __init__(
        self,
        output_dir: str | Path = "backend/ai_data/reports/full_extraction",
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "manifest.json"
        self.router = ExtractionRouter()
        self.inspector = PdfInspector()
        self.results: list[DocumentResult] = []

    @property
    def manifest(self) -> dict[str, Any]:
        return self._load_manifest()

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {"documents": {}, "total": 0, "completed": 0, "failed": 0}
        try:
            data = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or "documents" not in data:
                return {"documents": {}, "total": 0, "completed": 0, "failed": 0}
            return data
        except (json.JSONDecodeError, OSError):
            return {"documents": {}, "total": 0, "completed": 0, "failed": 0}

    def _save_manifest(self) -> None:
        existing: dict[str, Any] = {}
        if self.manifest_path.exists():
            try:
                existing = json.loads(self.manifest_path.read_text(encoding="utf-8"))
                existing = existing.get("documents", {}) if isinstance(existing, dict) else {}
            except (json.JSONDecodeError, OSError):
                existing = {}

        current: dict[str, Any] = {
            r.pdf_path: {
                "status": r.status,
                "document_id": r.document_id,
                "error": r.error,
                "output_json": r.output_json,
                "output_markdown": r.output_markdown,
            }
            for r in self.results
        }

        merged = {**existing, **current}

        data = {
            "documents": merged,
            "total": len(merged),
            "completed": sum(1 for v in merged.values() if v.get("status") == "completed"),
            "failed": sum(1 for v in merged.values() if v.get("status") == "failed"),
        }
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(self.output_dir), suffix=".tmp"
        )
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, str(self.manifest_path))
        except BaseException:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _is_already_completed(self, pdf_path: str) -> bool:
        manifest = self._load_manifest()
        entry = manifest.get("documents", {}).get(pdf_path)
        if entry is None:
            return False
        if entry.get("status") != "completed":
            return False
        if not entry.get("output_json"):
            return False
        if not entry.get("output_markdown"):
            return False
        json_path = self.output_dir / entry["output_json"]
        md_path = self.output_dir / entry["output_markdown"]
        if not json_path.exists() or not md_path.exists():
            return False
        return True

    def _process_single(self, pdf_path: str) -> DocumentResult:
        path = Path(pdf_path)
        if not path.exists():
            return DocumentResult(
                pdf_path=pdf_path,
                status="failed",
                error=f"File not found: {pdf_path}",
            )

        fhash = file_sha256(path)
        dims = self._get_page_dimensions(path)

        inspection = self.inspector.inspect(str(path))
        if inspection.error:
            return DocumentResult(
                pdf_path=pdf_path,
                status="failed",
                error=inspection.error,
            )

        doc_errors: list[str] = []
        doc_warnings: list[str] = []
        canonical_pages: list[CanonicalPage] = []

        for page in inspection.pages:
            page_dims = dims[page.page_number - 1] if page.page_number - 1 < len(dims) else (0.0, 0.0)
            try:
                backend_name = route_page(page)
            except Exception as exc:
                backend_name = "unrouted"
                doc_errors.append(f"Page {page.page_number}: routing error: {exc}")

            result = self.router.extract_page(str(path), page)

            pg_width = result.metadata.get("page_width") or page_dims[0]
            pg_height = result.metadata.get("page_height") or page_dims[1]

            canonical_page = CanonicalPage.from_extraction_result(
                result,
                classification=page.classification,
                page_width=float(pg_width),
                page_height=float(pg_height),
            )
            canonical_pages.append(canonical_page)

            if not result.success:
                doc_errors.extend(result.errors)
                doc_warnings.extend(result.warnings)

        if not canonical_pages:
            overall = "failed"
        elif all(p.extraction_status == "success" for p in canonical_pages):
            overall = "success"
        elif any(p.extraction_status == "success" for p in canonical_pages):
            overall = "partial"
        else:
            overall = "failed"

        document_id = f"full-{path.stem}-{fhash[:8]}"
        document = CanonicalDocument(
            document_id=document_id,
            source_path=str(path),
            file_name=path.name,
            file_hash=f"sha256:{fhash}",
            page_count=len(canonical_pages),
            extraction_status=overall,
            warnings=doc_warnings,
            errors=doc_errors,
            pages=canonical_pages,
        )

        markdown = render_document(document)

        safe_stem = path.stem.replace("/", "_").replace("\\", "_")
        path_hash = hashlib.sha256(os.path.abspath(str(path)).encode()).hexdigest()[:12]
        json_filename = f"{safe_stem}_{path_hash}.json"
        md_filename = f"{safe_stem}_{path_hash}.md"
        json_path = self.output_dir / json_filename
        md_path = self.output_dir / md_filename

        json_path.write_text(document.to_json(indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(markdown, encoding="utf-8")

        if overall == "failed":
            return DocumentResult(
                pdf_path=pdf_path,
                status="failed",
                document_id=document_id,
                error="; ".join(doc_errors) if doc_errors else "All pages failed extraction",
                output_json=json_filename,
                output_markdown=md_filename,
            )

        return DocumentResult(
            pdf_path=pdf_path,
            status="completed",
            document_id=document_id,
            output_json=json_filename,
            output_markdown=md_filename,
        )

    def _get_page_dimensions(self, path: Path) -> list[tuple[float, float]]:
        doc = fitz.open(str(path))
        dims = [(page.rect.width, page.rect.height) for page in doc]
        doc.close()
        return dims

    def process(self, pdf_paths: list[str]) -> dict[str, Any]:
        for pdf_path in pdf_paths:
            if self._is_already_completed(pdf_path):
                logger.info("Skipping already completed: %s", pdf_path)
                continue

            try:
                result = self._process_single(pdf_path)
            except Exception as exc:
                result = DocumentResult(
                    pdf_path=pdf_path,
                    status="failed",
                    error=f"Runner error: {exc}",
                )

            self.results.append(result)
            self._save_manifest()

        return {
            "processed": len(self.results),
            "completed": sum(1 for r in self.results if r.status == "completed"),
            "failed": sum(1 for r in self.results if r.status == "failed"),
            "results": [asdict(r) for r in self.results],
        }
