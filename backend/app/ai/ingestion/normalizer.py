from abc import ABC, abstractmethod
from typing import Any


class BaseNormalizer(ABC):
    @abstractmethod
    def normalize(self, data: Any) -> Any:
        ...
