from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractionResult:
    page_number: int
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    backend_name: str = ""
    success: bool = True


class ExtractionBackend(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def extract_page(self, file_path: str, page_number: int) -> ExtractionResult: ...

    def extract(
        self,
        file_path: str,
        page_numbers: list[int] | None = None,
    ) -> list[ExtractionResult]:
        if page_numbers is None:
            raise NotImplementedError(
                f"{self.name} backend does not support full-document extraction"
            )
        return [self.extract_page(file_path, pn) for pn in page_numbers]


class UnsupportedBackendError(Exception):
    pass


class ExtractionFailedError(Exception):
    pass
