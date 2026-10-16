from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.ai.config import AI_REPORTS_DIR

logger = logging.getLogger(__name__)


@dataclass
class MissingItem:
    product_name: str
    brand: str
    product_url: str
    missing_type: str
    original_source: str
    original_document_url: str
    status: str
    external_search_attempted: bool
    external_candidates: list[dict[str, Any]] = field(default_factory=list)
    recommended_action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "product_name": self.product_name,
            "brand": self.brand,
            "product_url": self.product_url,
            "missing_type": self.missing_type,
            "original_source": self.original_source,
            "original_document_url": self.original_document_url,
            "status": self.status,
            "external_search_attempted": self.external_search_attempted,
            "external_candidates": self.external_candidates,
            "recommended_action": self.recommended_action,
        }


class MissingDataRegistry:
    """Builds and persists the missing documents registry.

    Output: backend/ai_data/reports/missing_documents.json
    """

    REPORT_DIR = AI_REPORTS_DIR

    def __init__(self) -> None:
        self.REPORT_DIR.mkdir(parents=True, exist_ok=True)
        self._items: list[MissingItem] = []

    def add_item(self, item: MissingItem) -> None:
        self._items.append(item)

    def add_items(self, items: list[MissingItem]) -> None:
        self._items.extend(items)

    def get_items(self) -> list[MissingItem]:
        return list(self._items)

    def get_items_by_brand(self, brand: str) -> list[MissingItem]:
        return [item for item in self._items if item.brand.lower() == brand.lower()]

    def get_items_by_missing_type(self, missing_type: str) -> list[MissingItem]:
        return [item for item in self._items if item.missing_type == missing_type]

    @property
    def missing_count(self) -> int:
        return len(self._items)

    def save(self, path: str | Path | None = None) -> str:
        target = Path(path) if path else self.REPORT_DIR / "missing_documents.json"
        target.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_missing": len(self._items),
            "brands": self._group_by_brand(),
            "items": [item.to_dict() for item in self._items],
        }

        with open(target, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)

        logger.info("Missing documents registry saved to %s (%d items)", target, len(self._items))
        return str(target)

    def _group_by_brand(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self._items:
            counts[item.brand] = counts.get(item.brand, 0) + 1
        return counts
