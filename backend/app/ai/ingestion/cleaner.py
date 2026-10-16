from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class BaseCleaner:
    @staticmethod
    def clean(raw: Any) -> Any:
        if isinstance(raw, str):
            return BaseCleaner._clean_text(raw)
        return raw

    @staticmethod
    def _clean_text(value: str) -> str:
        if not value:
            return ""
        text = value.replace("\x00", "")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = "\n".join(line.rstrip() for line in text.split("\n"))
        text = text.strip()
        return text
