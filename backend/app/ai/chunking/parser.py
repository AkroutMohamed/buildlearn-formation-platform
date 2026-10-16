from __future__ import annotations

import re

from dataclasses import dataclass, field

from typing import Optional

from app.ai.chunking.config import ChunkConfig
from app.ai.chunking.models import BlockType, SemanticBlock, SourceInfo


_HEADING_RE = re.compile(
    r"^(?P<text>[A-Z][A-Z\s\-\(\)/'\.,&]+(?:\s+[A-Z][A-Z\s\-\(\)/'\.,&]*)*)$",
    re.MULTILINE,
)

_CAPTION_RE = re.compile(
    r"^.*?(?:Fig\.|Figure|Table\s|Photo|Img\.|Image|Illustration).*(?:\d|[\u00C0-\u024F])",
    re.IGNORECASE | re.MULTILINE,
)

_LIST_BULLET_RE = re.compile(
    r"^\s*[•\-\*▪◻◈○]\s+",
    re.MULTILINE,
)

_LIST_NUMBER_RE = re.compile(
    r"^\s*(?:\d{1,2}|[ivxlcdm]+|[a-h])[\.\)]?\s+",
    re.IGNORECASE | re.MULTILINE,
)

_KV_RE = re.compile(
    r"^([A-Za-z][A-Za-z\s\-\u00C0-\u024F]{1,60})([:\t|])",
    re.MULTILINE,
)

_PIPE_TABLE_RE = re.compile(
    r"^\s*\|.*\|",
    re.MULTILINE,
)

_WHITESPACE_RE = re.compile(r"\s+")


def _clean_text(text: str) -> str:
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


@dataclass
class ParsedElement:
    element_type: BlockType
    text: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    metadata: dict = field(default_factory=dict)


class StructureParser:
    def __init__(self, config: Optional[ChunkConfig] = None) -> None:
        self.config = config or ChunkConfig()

    def parse_page(
        self,
        raw_text: str,
        source: SourceInfo,
        page_number: int,
    ) -> list[ParsedElement]:
        if not raw_text or not raw_text.strip():
            return []

        text = raw_text.rstrip()

        elements: list[ParsedElement] = []

        if self.config.page_break_marker in text:
            parts = text.split(self.config.page_break_marker)

            for i, part in enumerate(parts):
                part = part.strip()

                if part:
                    elements.append(
                        ParsedElement(
                            element_type=BlockType.PAGE_BREAK,
                            text=part,
                            page_start=page_number,
                            page_end=page_number + i,
                        )
                    )

            if elements and elements[-1].element_type == BlockType.PAGE_BREAK:
                return elements

            if elements:
                elements.append(
                    ParsedElement(
                        element_type=BlockType.PAGE_BREAK,
                        text="",
                        page_start=page_number,
                        page_end=page_number,
                    )
                )

            return elements

        # ---------------------------------------------------------
        # NEW:
        # Reconstruct physical PDF lines into logical lines before
        # structural classification.
        # ---------------------------------------------------------
        logical_lines = self._reconstruct_logical_lines(text)

        current_block: list[str] = []
        current_type: BlockType = BlockType.UNKNOWN

        for line in logical_lines:
            stripped = line.strip()

            if not stripped:
                if current_block:
                    elements.append(
                        self._finalize_block(
                            current_block,
                            current_type,
                            source,
                            page_number,
                        )
                    )

                    current_block = []
                    current_type = BlockType.UNKNOWN

                continue

            detected = self._detect_line_type(stripped)

            if current_type == BlockType.UNKNOWN:
                current_type = detected
                current_block.append(stripped)

            elif detected == current_type:
                current_block.append(stripped)

            else:
                elements.append(
                    self._finalize_block(
                        current_block,
                        current_type,
                        source,
                        page_number,
                    )
                )

                current_block = [stripped]
                current_type = detected

        if current_block:
            elements.append(
                self._finalize_block(
                    current_block,
                    current_type,
                    source,
                    page_number,
                )
            )

        return elements

    # =============================================================
    # Logical-line reconstruction
    # =============================================================

    def _reconstruct_logical_lines(self, text: str) -> list[str]:
        """
        Convert physical PDF-extraction lines into logical lines.

        PDF extraction frequently introduces artificial line breaks:

            • Sur les surfaces métalliques, en linoléum, PVC,
            caoutchoue et dérivés

        should become:

            • Sur les surfaces métalliques, en linoléum, PVC, caoutchoue et dérivés

        The reconstruction is intentionally conservative.
        """

        physical_lines = text.splitlines()

        if not physical_lines:
            return []

        logical_lines: list[str] = []
        current: Optional[str] = None

        for raw_line in physical_lines:
            line = raw_line.strip()

            # -----------------------------------------------------
            # Blank line = hard semantic boundary.
            # -----------------------------------------------------
            if not line:
                if current is not None:
                    logical_lines.append(current)
                    current = None

                logical_lines.append("")
                continue

            # -----------------------------------------------------
            # Strong structural start.
            # These should never be appended to the previous line.
            # -----------------------------------------------------
            if self._is_strong_structure_start(line):
                if current is not None:
                    logical_lines.append(current)

                current = line
                continue

            # -----------------------------------------------------
            # First line.
            # -----------------------------------------------------
            if current is None:
                current = line
                continue

            # -----------------------------------------------------
            # Explicit table rows should remain independent.
            # -----------------------------------------------------
            if self._is_explicit_table_row(line):
                logical_lines.append(current)
                current = line
                continue

            # -----------------------------------------------------
            # If the current line clearly represents a list item,
            # continuation text should remain part of that item.
            # -----------------------------------------------------
            if self._is_list_item(current):
                if self._is_probable_list_continuation(line):
                    current = self._join_wrapped_lines(current, line)
                    continue

                logical_lines.append(current)
                current = line
                continue

            # -----------------------------------------------------
            # General paragraph continuation.
            # -----------------------------------------------------
            if self._should_merge_paragraph_line(current, line):
                current = self._join_wrapped_lines(current, line)
                continue

            # -----------------------------------------------------
            # Otherwise start a new logical line.
            # -----------------------------------------------------
            logical_lines.append(current)
            current = line

        if current is not None:
            logical_lines.append(current)

        return logical_lines

    def _is_strong_structure_start(self, line: str) -> bool:
        """
        Detect structures that should begin a new logical line.
        """

        if not line:
            return False

        if self._is_list_item(line):
            return True

        if self._is_caption(line):
            return True

        if self._is_explicit_table_row(line):
            return True

        if self._is_strong_heading(line):
            return True

        return False

    def _is_strong_heading(self, line: str) -> bool:
        """
        Only use strong heading evidence here.

        We deliberately avoid _is_likely_heading() because its
        heuristics are exactly what currently classify wrapped
        continuation lines as headings.
        """

        if self._is_all_caps_heading(line):
            return True

        # Do not treat ordinary mixed-case short lines as strong
        # headings during reconstruction.
        return False

    def _is_explicit_table_row(self, line: str) -> bool:
        """
        Strong table evidence only.

        Pipes and tabs are reliable structural signals.
        Multiple spaces are intentionally NOT sufficient.
        """

        stripped = line.strip()

        if not stripped:
            return False

        # Explicit pipe-separated row.
        if "|" in stripped:
            parts = [part.strip() for part in stripped.split("|")]

            non_empty = [part for part in parts if part]

            if len(non_empty) >= 2:
                return True

        # Explicit tab-separated row.
        if "\t" in line:
            parts = [part.strip() for part in line.split("\t")]

            non_empty = [part for part in parts if part]

            if len(non_empty) >= 2:
                return True

        return False

    def _is_probable_list_continuation(self, line: str) -> bool:
        """
        Determine whether a line is likely continuation text for
        the current list item.

        A new bullet/numbered item is handled before this function.
        """

        if not line:
            return False

        if self._is_list_item(line):
            return False

        if self._is_caption(line):
            return False

        if self._is_explicit_table_row(line):
            return False

        if self._is_strong_heading(line):
            return False

        # A short lowercase/fragment-like line is strong evidence
        # of continuation.
        first_alpha = next(
            (char for char in line if char.isalpha()),
            "",
        )

        if first_alpha and first_alpha.islower():
            return True

        # Continuation punctuation.
        if line.endswith(
            (
                ",",
                ";",
                ":",
                "-",
                "/",
                "(",
            )
        ):
            return True

        # Very short fragments are commonly wrapped continuations.
        words = line.split()

        if len(words) <= 4 and not line.endswith((".", "!", "?")):
            return True

        return False

    def _should_merge_paragraph_line(
        self,
        previous: str,
        current: str,
    ) -> bool:
        """
        Decide whether `current` continues `previous`.

        Conservative rules are preferred because merging two genuine
        semantic blocks is more harmful than leaving a possible wrap.
        """

        if not previous or not current:
            return False

        # A paragraph line must never be merged into a heading.
        # If the previous line is already a heading candidate, start a
        # new logical line so the heading is preserved as its own block.
        if self._is_all_caps_heading(previous) or self._is_likely_heading(previous):
            return False

        if self._is_list_item(current):
            return False

        if self._is_caption(current):
            return False

        if self._is_explicit_table_row(current):
            return False

        if self._is_strong_heading(current):
            return False

        # If previous ends with punctuation that strongly terminates
        # a sentence, don't automatically merge.
        if previous.endswith((".", "!", "?", ":", ";")):
            return False

        # A lowercase beginning is strong continuation evidence.
        first_alpha = next(
            (char for char in current if char.isalpha()),
            "",
        )

        if first_alpha and first_alpha.islower():
            return True

        # Common technical/document continuation patterns.
        if previous.endswith(
            (
                ",",
                "-",
                "/",
                "(",
            )
        ):
            return True

        # If the current line is clearly a short fragment and does not
        # look like a standalone heading, merge it.
        words = current.split()

        if len(words) <= 5:
            if not self._is_likely_heading(current):
                return True

        return False

    @staticmethod
    def _join_wrapped_lines(previous: str, current: str) -> str:
        """
        Join two physical lines without altering their words.
        """

        previous = previous.rstrip()
        current = current.lstrip()

        if not previous:
            return current

        if not current:
            return previous

        return f"{previous} {current}"

    # =============================================================
    # Classification
    # =============================================================

    def _detect_line_type(self, line: str) -> BlockType:
        if self._is_all_caps_heading(line):
            return BlockType.HEADING

        if self._is_caption(line):
            return BlockType.CAPTION

        if self._is_pipe_table_row(line):
            return BlockType.TABLE

        if self._is_list_item(line):
            return BlockType.LIST_ITEM

        if self._is_key_value(line):
            return BlockType.KEY_VALUE

        if self._is_likely_heading(line):
            # A line whose first alphabetic character is lowercase is body
            # prose (typically a wrapped continuation), not a heading.
            # This prevents lowercase fragments such as "perçage, vissage..."
            # from being absorbed into a multi-line heading block.
            first_alpha = next((c for c in line if c.isalpha()), "")
            if first_alpha and first_alpha.islower():
                return BlockType.PARAGRAPH
            return BlockType.HEADING

        return BlockType.PARAGRAPH

    def _finalize_block(
        self,
        lines: list[str],
        block_type: BlockType,
        source: SourceInfo,
        page_number: int,
    ) -> SemanticBlock:

        text = "\n".join(lines)

        return SemanticBlock.from_text(
            text=text,
            block_type=block_type,
            source=source,
            page_start=page_number,
            page_end=page_number,
        )

    # =============================================================
    # Existing structural detectors
    # =============================================================

    def _is_all_caps_heading(self, text: str) -> bool:
        if len(text) < self.config.all_caps_min_length:
            return False

        if len(text) > self.config.all_caps_max_length:
            return False

        if not text.strip():
            return False

        alpha_chars = [c for c in text if c.isalpha()]

        if len(alpha_chars) < 2:
            return False

        has_lowercase = any(c.islower() for c in text)

        if has_lowercase:
            return False

        words = text.split()

        if len(words) < 1:
            return False

        if len(text) > 20 and len(words) == 1:
            return False

        return True

    def _is_likely_heading(self, text: str) -> bool:
        if len(text) < self.config.heading_min_length:
            return False

        if len(text) > self.config.heading_max_length:
            return False

        words = text.split()

        if len(words) < self.config.heading_word_count_min:
            return False

        if len(words) > self.config.heading_word_count_max:
            return False

        alpha_chars = [c for c in text if c.isalpha()]

        if not alpha_chars:
            return False

        if len(words) == 1 and len(text) > 12:
            return False

        if re.match(r"^[0-9]+$", text.strip()):
            return False

        if text.strip().startswith(
            ("•", "-", "*", "©", "™", "®")
        ):
            return False

        has_mixed_case = (
            any(c.islower() for c in text)
            and any(c.isupper() for c in text)
        )

        if has_mixed_case:
            return False

        return True

    def _is_caption(self, text: str) -> bool:
        text_stripped = text.strip()

        if len(text_stripped) < 5:
            return False

        for indicator in self.config.caption_indicators:
            if indicator.lower() in text_stripped[:30].lower():
                return True

        if re.match(
            r"^(Fig\.|Figure|Table|Photo|Image)\s*\d",
            text_stripped,
            re.IGNORECASE,
        ):
            return True

        return False

    def _is_list_item(self, line: str) -> bool:
        stripped = line.strip()

        if _LIST_BULLET_RE.match(line):
            return True

        if _LIST_NUMBER_RE.match(line):
            number_part = _LIST_NUMBER_RE.match(line).group(0).strip()

            if "." in number_part or ")" in number_part:
                return True

            words = stripped.split()

            if len(words) >= 2 and len(stripped) > 3:
                return True

        return False

    def _is_key_value(self, line: str) -> bool:
        stripped = line.strip()

        if not stripped:
            return False

        if len(stripped) > 200:
            return False

        for sep in self.config.kv_separators:
            if sep in stripped:
                parts = stripped.split(sep, 1)

                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""

                if 1 <= len(key) <= 60 and len(value) > 0:
                    # A colon alone is not sufficient evidence of a
                    # structured key/value pair. Long sentence-like values
                    # with only one or two colons are typically prose,
                    # notes (e.g. "NB: ...") or contact/address lines
                    # (e.g. "Tèl.: ... / E-mail: ... / Site Web: ...").
                    colon_count = stripped.count(":")

                    if colon_count <= 2 and len(value) > 70:
                        continue

                    if "@" in value or "http://" in value or "https://" in value:
                        continue

                    # Contact/address lines (Tél/Fax/E-mail/Site Web) are
                    # prose, not structured key/value data.
                    contact_indicators = (
                        "tél", "tel", "fax", "e-mail", "email",
                        "site web", "www.",
                    )

                    if any(ind in value.lower() for ind in contact_indicators):
                        continue

                    # Street addresses ("Sfax: Route de Gabés km 4.5 /
                    # Tunis: ...") are prose, not key/value data.
                    if " / " in value and "km" in value.lower():
                        continue

                    return True

        return False

    def _is_pipe_table_row(self, line: str) -> bool:
        """
        Detect explicit table rows.

        IMPORTANT:
        Multiple spaces are no longer sufficient evidence of a table.
        PDF text extraction commonly introduces multiple spaces inside
        ordinary prose.
        """

        stripped = line.strip()

        if not stripped:
            return False

        # Pipe-separated structure.
        if "|" in stripped:
            # A colon immediately followed by a pipe (e.g. "Consommation : | Varie...")
            # is a single-pipe key/value artifact from OCR, not a real table.
            # Genuine multi-column tables have pipes between columns with no
            # colon adjacent to a pipe.
            if re.search(r":\s*\|", stripped):
                return False

            parts = stripped.split("|")

            non_empty = [
                part.strip()
                for part in parts
                if part.strip()
            ]

            if (
                len(non_empty) >= 2
                and all(len(part) <= 100 for part in non_empty)
            ):
                return True

        # Tab-separated structure.
        if "\t" in line:
            parts = line.split("\t")

            non_empty = [
                part.strip()
                for part in parts
                if part.strip()
            ]

            if len(non_empty) >= 2:
                return True

        return False


def parse_text_blocks(
    raw_text: str,
    source: SourceInfo,
    page_number: int = 1,
    config: Optional[ChunkConfig] = None,
) -> list[SemanticBlock]:

    parser = StructureParser(config=config)

    return parser.parse_page(
        raw_text,
        source,
        page_number,
    )