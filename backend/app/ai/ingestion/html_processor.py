from abc import ABC, abstractmethod
from typing import Any


class BaseHtmlProcessor(ABC):
    @abstractmethod
    def extract(self, html: str, url: str) -> dict[str, Any]:
        ...
