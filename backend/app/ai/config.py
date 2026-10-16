import os
from dataclasses import dataclass, field
from pathlib import Path


# This file lives at backend/app/ai/config.py. The project root ("backend/")
# is therefore three parents up.
BACKEND_DIR: Path = Path(__file__).resolve().parent.parent.parent
AI_DATA_DIR: Path = BACKEND_DIR / "ai_data"
AI_RAW_DIR: Path = AI_DATA_DIR / "raw"
AI_REPORTS_DIR: Path = AI_DATA_DIR / "reports"
DOCS_AI_DIR: Path = BACKEND_DIR.parent / "docs" / "ai"


@dataclass
class AISettings:
    enabled: bool = field(
        default_factory=lambda: os.environ.get("AI_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
    )
    ollama_base_url: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    ollama_model: str = field(
        default_factory=lambda: os.environ.get("OLLAMA_MODEL", "qwen2.5")
    )
    embedding_provider: str = field(
        default_factory=lambda: os.environ.get("EMBEDDING_PROVIDER", "")
    )
    embedding_model: str = field(
        default_factory=lambda: os.environ.get("EMBEDDING_MODEL", "")
    )
    embedding_normalize: bool = field(
        default_factory=lambda: os.environ.get("EMBEDDING_NORMALIZE", "true").lower() in {"1", "true", "yes", "on"}
    )
    vector_store: str = field(
        default_factory=lambda: os.environ.get("VECTOR_STORE", "")
    )
    qdrant_url: str = field(
        default_factory=lambda: os.environ.get("QDRANT_URL", "http://localhost:6333")
    )
    qdrant_collection: str = field(
        default_factory=lambda: os.environ.get("QDRANT_COLLECTION", "buildlearn_products")
    )
    qdrant_collection_hierarchical: str = field(
        default_factory=lambda: os.environ.get("QDRANT_COLLECTION_HIERARCHICAL", "buildlearn_products_hierarchical_v1")
    )
    retrieval_score_threshold: float = field(
        default_factory=lambda: float(os.environ.get("RETRIEVAL_SCORE_THRESHOLD", "0.3"))
    )
    ocr_enabled: bool = field(
        default_factory=lambda: os.environ.get("OCR_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
    )
    ocr_language: str = field(
        default_factory=lambda: os.environ.get("OCR_LANGUAGE", "fra")
    )
    ocr_engine: str = field(
        default_factory=lambda: os.environ.get("OCR_ENGINE", "tesseract")
    )


ai_settings = AISettings()
