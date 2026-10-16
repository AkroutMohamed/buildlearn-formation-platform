from dataclasses import dataclass, field
from typing import Any


@dataclass
class GoldenCase:
    question: str
    expected_product_name: str | None
    expected_supplier: str | None = "GYPROC"
    expected_document_urls: list[str] = field(default_factory=list)
    expected_document_title_tokens: list[str] = field(default_factory=list)
    expected_top_k: int = 5
    behavior: str = "grounded"
    notes: str = ""


CASES = [
    GoldenCase(
        question="What is Gyproc Moisture Resistant Board?",
        expected_product_name="BA13 Hydro",
        expected_document_urls=[
            "https://www.gyproc.in/pdf/Gyproc_Moisture_Resistant_Board_2024.pdf",
            "https://www.gyproc.in/pdf/Gyproc_BA13_Hydro.pdf",
        ],
        expected_document_title_tokens=["Moisture", "Resistant", "Board"],
        behavior="grounded",
        notes="Hydro/Moisture Resistant product; should retrieve relevant documentation.",
    ),
    GoldenCase(
        question="What is Gyproc Fireline Board?",
        expected_product_name="BA13 Feu",
        expected_document_urls=[
            "https://www.gyproc.in/pdf/Gyproc_Fireline_Board_2024.pdf",
            "https://www.gyproc.in/pdf/PB03_GyprocFirelineBoard.pdf",
        ],
        expected_document_title_tokens=["Fireline", "Board"],
        behavior="grounded",
        notes="Fire-resistant board; should retrieve Fireline documentation.",
    ),
    GoldenCase(
        question="What is Gyproc Duraline Board?",
        expected_product_name="BA13 Hydro",
        expected_document_urls=[
            "https://www.gyproc.in/pdf/PB05_Gyproc_Duraline_Board.pdf",
            "https://www.gyproc.in/pdf/Gyproc_Duraline_Board.pdf",
        ],
        expected_document_title_tokens=["Duraline", "Board"],
        behavior="grounded",
        notes="Duraline is a GYPROC alias for BA13 Hydro per existing acquisition tests.",
    ),
    GoldenCase(
        question="What is the meaning of life?",
        expected_product_name=None,
        expected_document_urls=[],
        expected_document_title_tokens=[],
        behavior="refusal",
        notes="Out-of-context question; system must refuse / state information not found.",
    ),
    GoldenCase(
        question="What is Lika PAP2?",
        expected_product_name="Lika PAP2",
        expected_supplier="Gypsobat",
        expected_document_urls=[
            "https://www.gypsobat.com/wp-content/uploads/2024/11/fiche_technique_pap2.pdf",
        ],
        expected_document_title_tokens=["Lika", "PAP2"],
        behavior="grounded",
        notes="Existing indexed product from Gypsobat catalog.",
    ),
]


def get_case(question: str) -> GoldenCase | None:
    for case in CASES:
        if case.question == question:
            return case
    return None
