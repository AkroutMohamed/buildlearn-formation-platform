from typing import Any


class RetrievalFilters:
    @staticmethod
    def build(source: str | None = None, manufacturer: str | None = None, category: str | None = None) -> dict[str, Any]:
        filters: dict[str, Any] = {}
        if source:
            filters["source"] = source
        if manufacturer:
            filters["manufacturer"] = manufacturer
        if category:
            filters["category"] = category
        return filters
