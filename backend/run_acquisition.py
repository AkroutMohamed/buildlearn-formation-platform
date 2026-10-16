#!/usr/bin/env python3
"""Entry point for Phase 6.5: Complete Product & Technical Document Acquisition.

Usage:
    venv/Scripts/python.exe run_acquisition.py [--brands gypsobat,emtop,sofap] [--skip-index] [--skip-external-search]

Environment variables:
    OLLAMA_BASE_URL      - Ollama server URL (default: http://localhost:11434)
    OLLAMA_MODEL         - Ollama LLM model (default: qwen2.5)
    EMBEDDING_PROVIDER   - "ollama" to enable embeddings
    EMBEDDING_MODEL      - "nomic-embed-text"
    VECTOR_STORE         - "qdrant" to enable Qdrant indexing
    QDRANT_URL           - Qdrant server URL (default: http://localhost:6333)
    QDRANT_COLLECTION    - Qdrant collection name (default: buildlearn_products)
    OCR_ENABLED           - "true" to enable OCR processing
"""
import argparse
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Load .env before importing AI modules that read os.environ at import time
from app.config import _load_dotenv
_load_dotenv(Path(__file__).resolve().parent / ".env")

from app.ai.acquisition.pipeline import AcquisitionPipeline
from app.ai.acquisition.external_search import WebExternalSearcher
from app.ai.chunking.technical_chunker import TechnicalDocumentChunker
from app.ai.embeddings.provider import EmbeddingProvider
from app.ai.ingestion.cleaner import BaseCleaner
from app.ai.ingestion.ocr_processor import OcrProcessor
from app.ai.vectorstore.provider import VectorStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("buildlearn_acquisition")


def parse_args():
    parser = argparse.ArgumentParser(description="BuildLearn AI Data Acquisition Pipeline")
    parser.add_argument(
        "--brands",
        type=str,
        default="gypsobat,emtop,sofap",
        help="Comma-separated list of brands to process (default: gypsobat,emtop,sofap)",
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="Skip Qdrant indexing (download and process documents only)",
    )
    parser.add_argument(
        "--skip-external-search",
        action="store_true",
        help="Skip external web search for missing documents",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scrape and validate only; do not download or process",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    brands = [b.strip() for b in args.brands.split(",") if b.strip()]

    print("=" * 70)
    print("BuildLearn AI — Phase 6.5: Complete Data Acquisition Pipeline")
    print(f"Brands: {', '.join(brands)}")
    print(f"Skip indexing: {args.skip_index}")
    print(f"Skip external search: {args.skip_external_search}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 70)

    cleaner = BaseCleaner()
    ocr_processor = OcrProcessor()

    embedding_provider = None
    vector_store = None
    if not args.skip_index:
        try:
            embedding_provider = EmbeddingProvider()
            logger.info("Embedding provider configured (dimension=%d)", embedding_provider.dimension)
        except Exception as exc:
            logger.warning("Embedding provider not available: %s", exc)

        try:
            vector_store = VectorStore()
            if not vector_store.collection_exists():
                vector_store.create_collection(embedding_provider.dimension)
                logger.info("Created Qdrant collection with dimension %d", embedding_provider.dimension)
            else:
                logger.info("Qdrant collection already exists")
        except Exception as exc:
            logger.warning("Vector store not available: %s", exc)
            vector_store = None

    external_searcher = None
    if not args.skip_external_search:
        external_searcher = WebExternalSearcher(rate_limit=1.0)
        logger.info("External searcher configured (DuckDuckGo)")

    chunker = TechnicalDocumentChunker()

    pipeline = AcquisitionPipeline(
        cleaner=cleaner,
        ocr_processor=ocr_processor,
        chunker=chunker,
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        external_searcher=external_searcher,
    )

    result = pipeline.run(brands=brands)

    print("\n" + "=" * 70)
    print("ACQUISITION COMPLETE — Final Report")
    print("=" * 70)

    stats = result.stats
    print(f"\n1. Total products discovered: {stats.get('total_products', 0)}")
    print(f"2. Total technical documents discovered: {stats.get('total_documents_discovered', 0)}")
    print(f"3. Accessible PDFs: {stats.get('accessible_documents', 0)}")
    print(f"4. Broken PDFs: {stats.get('broken_documents', 0)}")
    print(f"5. Duplicate PDFs: {stats.get('duplicate_documents', 0)}")
    print(f"6. OCR-required PDFs: {stats.get('ocr_required_documents', 0)}")
    print(f"7. Successfully processed PDFs: {stats.get('successfully_processed_documents', 0)}")
    print(f"8. Successfully chunked documents: {stats.get('successfully_chunked_documents', 0)}")
    print(f"9. Total chunks: {stats.get('successfully_indexed_chunks', 0)}")
    print(f"10. Total Qdrant vectors: {stats.get('successfully_indexed_chunks', 0)}")
    print(f"11. Products without technical documentation: {stats.get('products_without_technical_documentation', 0)}")
    print(f"12. Products with external official documents: {stats.get('external_official_documents', 0)}")
    print(f"13. Products with only third-party candidates: {stats.get('low_confidence_candidates', 0)}")
    print(f"14. Documents requiring manual review: {stats.get('documents_requiring_manual_review', 0)}")
    print(f"15. External sources used: {stats.get('external_sources_used', 0)}")

    print(f"\n--- Output Files ---")
    print(f"  Missing documents: {result.registry_path}")
    print(f"  Dataset manifest: {result.manifest_path}")
    print(f"  Human review report: {result.report_path}")

    print(f"\n--- Per-Brand Breakdown ---")
    for brand, products in result.products_by_brand.items():
        print(f"  {brand}: {len(products)} products")

    print("\n" + "=" * 70)
    print("Known Limitations:")
    print("  1. EMTOP product pages typically do not include direct PDF downloads.")
    print("  2. SOFAP API content may be empty; product pages are scraped for PDF links.")
    print("  3. External search uses DuckDuckGo HTML; JavaScript-only sites may not be indexed.")
    print("  4. OCR depends on local tesseract installation.")
    print("  5. Re-running the pipeline uses deterministic chunk IDs and SHA-256")
    print("     deduplication to prevent duplicate vectors.")
    print("=" * 70)


if __name__ == "__main__":
    main()
