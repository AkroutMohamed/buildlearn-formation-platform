from abc import ABC, abstractmethod
from typing import Any

from app.ai.schemas.document import DocumentCreate


class BaseDocumentLoader(ABC):
    @abstractmethod
    def load(self, source: str) -> DocumentCreate:
        ...
