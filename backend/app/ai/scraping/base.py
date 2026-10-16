from abc import ABC, abstractmethod
from typing import Any

from app.ai.schemas.document import DocumentCreate
from app.ai.schemas.product import ProductCreate


class BaseProductScraper(ABC):
    source: str = ""

    @abstractmethod
    def discover_products(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def scrape_product(self, url: str) -> ProductCreate:
        ...

    @abstractmethod
    def discover_documents(self, product: ProductCreate) -> list[dict[str, Any]]:
        ...
