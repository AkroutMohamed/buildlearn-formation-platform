from dataclasses import dataclass, field


@dataclass
class ChunkConfig:
    min_chunk_size: int = 100
    max_chunk_size: int = 1500
    max_parent_depth: int = 3
    heading_min_length: int = 3
    heading_max_length: int = 100
    heading_word_count_min: int = 1
    heading_word_count_max: int = 15
    all_caps_min_length: int = 3
    all_caps_max_length: int = 60
    separator: str = "\n\n"
    list_bullet_prefixes: tuple[str, ...] = ("•", "-", "*", "\u2022", "○", "▪", "◻", "◈")
    list_number_prefixes: tuple[str, ...] = (
        "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "0.",
        "1)", "2)", "3)", "4)", "5)", "6)", "7)", "8)", "9)", "0)",
        "i.", "ii.", "iii.", "iv.", "v.", "vi.", "vii.", "viii.",
        "a.", "b.", "c.", "d.", "e.", "f.", "g.", "h.",
        "a)", "b)", "c)", "d)", "e)", "f)", "g)", "h)",
    )
    kv_separators: tuple[str, ...] = (":", "\t", "|")
    table_min_columns: int = 2
    table_max_rows_before_split: int = 8
    caption_indicators: tuple[str, ...] = ("Fig.", "Figure", "Table ", "Photo", "Photo.", "Img.", "Image", "Illustration")
    page_break_marker: str = "\f"
    preserve_original_text: bool = True

    @property
    def effective_min(self) -> int:
        return max(self.min_chunk_size, 1)

    @property
    def effective_max(self) -> int:
        return max(self.max_chunk_size, self.effective_min + 1)
