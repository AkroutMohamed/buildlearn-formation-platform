import json
import os
import sys
from pathlib import Path

# Resolve BACKEND_DIR relative to this script so path lookups are
# independent of the shell's current working directory.
BACKEND_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BACKEND_DIR / "ai_data" / "raw" / "gypsobat"
DOCUMENTS_JSON = RAW_DATA / "ingested_documents.json"

os.environ.setdefault("AI_ENABLED", "true")
os.environ.setdefault("EMBEDDING_PROVIDER", "ollama")
os.environ.setdefault("EMBEDDING_MODEL", "nomic-embed-text")
os.environ.setdefault("VECTOR_STORE", "qdrant")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_COLLECTION", "buildlearn_products")

sys.path.insert(0, str(BACKEND_DIR))

# Validate that the centralized AI paths resolve to the same locations.
from app.ai.config import AI_DATA_DIR, AI_RAW_DIR  # noqa: E402

assert AI_DATA_DIR == BACKEND_DIR / "ai_data", (
    f"Centralized AI_DATA_DIR ({AI_DATA_DIR}) does not match script-resolved "
    f"BACKEND_DIR/ai_data ({BACKEND_DIR / 'ai_data'}). Check app/ai/config.py."
)
assert AI_RAW_DIR == BACKEND_DIR / "ai_data" / "raw", (
    f"Centralized AI_RAW_DIR ({AI_RAW_DIR}) does not match script-resolved "
    f"BACKEND_DIR/ai_data/raw ({BACKEND_DIR / 'ai_data' / 'raw'})."
)

from app.ai.chunking.technical_chunker import TechnicalDocumentChunker
from app.ai.config import ai_settings
from app.ai.embeddings.provider import EmbeddingProvider
from app.ai.ingestion.pdf_processor import PdfProcessor
from app.ai.ingestion.cleaner import BaseCleaner
from app.ai.indexing.service import IndexingService
from app.ai.vectorstore.provider import VectorStore

logging = __import__("logging")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_documents():
    with open(DOCUMENTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("documents", [])


def ensure_content(doc):
    content = doc.get("content", "")
    if content and content.strip():
        return content
    metadata = doc.get("metadata", {})
    file_path = metadata.get("file_path")
    if file_path and Path(file_path).exists():
        cleaner = BaseCleaner()
        processor = PdfProcessor(cleaner=cleaner)
        result = processor.extract(file_path)
        return result.get("cleaned_text", "") or result.get("raw_text", "")
    return ""


def main() -> None:
    """Rebuild the Qdrant collection from already-acquired documents."""
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    for d in docs:
        content = ensure_content(d)
        print(f"  - {d.get('title', '?')} | product={d.get('metadata', {}).get('product_name', '?')} | content_len={len(content)}")

    embedding_provider = EmbeddingProvider()
    vector_store = VectorStore()
    chunker = TechnicalDocumentChunker()
    indexing_service = IndexingService(vector_store, embedding_provider, chunker)

    dimension = embedding_provider.dimension
    print(f"Embedding dimension: {dimension}")

    if not vector_store.collection_exists():
        print(f"Creating collection '{ai_settings.qdrant_collection}'...")
        vector_store.create_collection(dimension)
    else:
        print(f"Collection already exists.")

    for doc in docs:
        content = ensure_content(doc)
        meta = doc.get("metadata", {})
        doc_dict = {
            "document_id": doc.get("document_id"),
            "product_id": doc.get("product_id"),
            "product_name": meta.get("product_name"),
            "supplier": meta.get("supplier"),
            "source": doc.get("source"),
            "source_url": doc.get("source_url"),
            "document_url": doc.get("document_url"),
            "document_type": doc.get("document_type"),
            "language": doc.get("language"),
            "content_hash": doc.get("content_hash"),
            "content": content,
            "metadata": meta,
        }
        indexing_service.index_document(doc_dict)
        print(f"Indexed: {doc.get('title', '?')}")

    info = vector_store.collection_info()
    print(f"Collection info: {info}")
    print("Done indexing!")


if __name__ == "__main__":
    main()
