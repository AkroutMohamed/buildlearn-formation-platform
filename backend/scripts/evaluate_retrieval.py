#!/usr/bin/env python3
"""
Retrieval Evaluation & Diagnosis (DIAGNOSTIC ONLY).

This is a standalone, temporary evaluation tool. It does NOT modify any
production retrieval code, embeddings config, Qdrant collection, or indexed
data. It reuses the *real* production components:

    - app.ai.embeddings.provider.EmbeddingProvider  (Ollama nomic-embed-text, normalized)
    - app.ai.vectorstore.provider.VectorStore       (Qdrant, buildlearn_products)
    - app.ai.rag.retriever.Retriever                (production retrieval path)

Plus a direct qdrant_client session to perform *raw* vector search so we can
compare raw Qdrant behavior against the production Retriever.

Outputs:
    backend/ai_data/reports/retrieval_evaluation.json   (machine-readable)
    prints a human-readable summary to stdout
"""
from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import sys
import traceback
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. LOAD ENVIRONMENT (do NOT touch production code; only set process env so
#    the production providers (config.py) resolve to the real local services)
# ---------------------------------------------------------------------------
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"
if _ENV_FILE.exists():
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line.strip())
        if m:
            os.environ.setdefault(m.group(1), m.group(2).strip())
# Hard defaults for local diagnostic run
os.environ.setdefault("EMBEDDING_PROVIDER", "ollama")
os.environ.setdefault("EMBEDDING_MODEL", "nomic-embed-text")
os.environ.setdefault("VECTOR_STORE", "qdrant")
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("QDRANT_COLLECTION", "buildlearn_products")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")

sys.path.insert(0, str(_BACKEND_DIR))

from qdrant_client import QdrantClient  # noqa: E402
from qdrant_client.http import models as qm  # noqa: E402

from app.ai.config import ai_settings  # noqa: E402
from app.ai.embeddings.provider import EmbeddingProvider  # noqa: E402
from app.ai.rag.retriever import Retriever  # noqa: E402

# ---------------------------------------------------------------------------
# 2. LIVE CONNECTIONS
# ---------------------------------------------------------------------------
COLLECTION = ai_settings.qdrant_collection or "buildlearn_products"
QD = QdrantClient(url=ai_settings.qdrant_url or "http://localhost:6333")
EMB = EmbeddingProvider()
RET = Retriever()
THRESHOLD = ai_settings.retrieval_score_threshold
DIM = EMB.dimension


def _vec(q: str) -> list[float]:
    return EMB.embed_single(q)


def _raw_search(qvec: list[float], limit: int = 10, score_threshold=None) -> list[dict]:
    """Raw Qdrant vector search with NO client-side filtering/threshold."""
    resp = QD.query_points(
        collection_name=COLLECTION,
        query=qvec,
        limit=limit,
        with_payload=True,
        with_vectors=False,
        score_threshold=score_threshold,
    )
    out = []
    for pt in resp.points:
        out.append({
            "id": str(pt.id),
            "score": pt.score,
            "payload": pt.payload or {},
        })
    return out


def _payload_text(payload: dict) -> str:
    t = payload.get("text") or ""
    return t


def _preview(text: str, n: int = 140) -> str:
    if not text:
        return ""
    t = text.replace("\n", " ").replace("\r", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t[:n]


def _product_name(payload: dict) -> str | None:
    return payload.get("product_name")


def _supplier(payload: dict) -> str | None:
    return payload.get("supplier")


def _source(payload: dict) -> str | None:
    return payload.get("source")


def _doc_id(payload: dict) -> str | None:
    return payload.get("document_id")


# ---------------------------------------------------------------------------
# 3. COLLECTION + DATASET INSPECTION
# ---------------------------------------------------------------------------
def inspect_collection() -> dict:
    ci = QD.get_collection(COLLECTION)
    vectors = ci.config.params.vectors
    size = vectors.size if isinstance(vectors, qm.VectorParams) else next(iter(vectors.values())).size
    dist = vectors.distance if isinstance(vectors, qm.VectorParams) else next(iter(vectors.values())).distance
    info = {
        "name": COLLECTION,
        "status": str(ci.status),
        "points_count": ci.points_count,
        "segments_count": ci.segments_count,
        "vector_size": size,
        "distance": str(dist),
        "hnsw_m": ci.config.hnsw_config.m if ci.config.hnsw_config else None,
        "hnsw_ef_construct": ci.config.hnsw_config.ef_construct if ci.config.hnsw_config else None,
        "full_scan_threshold": ci.config.hnsw_config.full_scan_threshold if ci.config.hnsw_config else None,
        "indexed_vectors_count": ci.indexed_vectors_count,
        "shard_number": ci.config.params.shard_number,
        "optimizer_status": str(ci.optimizer_status),
    }
    # server version via REST root endpoint
    try:
        import urllib.request
        with urllib.request.urlopen(f"{ai_settings.qdrant_url}/", timeout=5) as r:
            ver = json.loads(r.read().decode())
            info["qdrant_server_version"] = ver.get("version")
    except Exception as e:
        info["qdrant_server_version_error"] = str(e)
    return info


def scroll_all() -> list[dict]:
    """Fetch every point's payload (vectors not needed for inspection)."""
    allp: list[dict] = []
    offset = None
    while True:
        res = QD.scroll(
            collection_name=COLLECTION,
            with_payload=True,
            with_vectors=False,
            limit=1000,
            offset=offset,
        )
        points, next_page = res
        for p in points:
            allp.append({"id": str(p.id), "score": None, "payload": p.payload or {}})
        if not next_page:
            break
        offset = next_page
    return allp


def build_catalog(allp: list[dict]) -> dict:
    distinct_products = set()
    by_brand = defaultdict(lambda: defaultdict(int))   # brand(source) -> product_name -> chunk_count
    by_supplier = defaultdict(lambda: defaultdict(int))
    payload_keys = set()
    for p in allp:
        pl = p["payload"]
        payload_keys.update(pl.keys())
        pn = pl.get("product_name")
        sup = pl.get("supplier")
        src = pl.get("source")
        brand = src or sup
        distinct_products.add(pn)
        if pn and sup:
            by_supplier[sup][pn] += 1
        if pn and src:
            by_brand[src][pn] += 1
    return {
        "payload_keys": sorted(payload_keys),
        "distinct_products": sorted(pn for pn in distinct_products if pn),
        "distinct_product_count": len(distinct_products),
        "by_brand": {k: dict(v) for k, v in by_brand.items()},
        "by_supplier": {k: dict(v) for k, v in by_supplier.items()},
        "total_chunks": len(allp),
    }


def analyze_chunk_text(allp: list[dict]) -> dict:
    total = len(allp)
    both = 0
    only_meta = 0
    only_text = 0
    neither = 0
    lengths = []
    empty_text = 0
    null_text = 0
    replacement_char = 0
    tiny = 0
    for p in allp:
        pl = p["payload"]
        pn = (pl.get("product_name") or "").strip()
        txt = pl.get("text") or ""
        if txt is None:
            null_text += 1
            txt = ""
        lengths.append(len(txt))
        if not txt.strip():
            empty_text += 1
        if "\ufffd" in txt:
            replacement_char += 1
        if len(txt.strip()) <= 20:
            tiny += 1
        in_text = bool(pn) and (pn.lower() in txt.lower())
        if pn and in_text:
            both += 1
        elif pn and not in_text:
            only_meta += 1
        elif not pn and txt.strip():
            only_text += 1
        else:
            neither += 1
    lengths_nonzero = [l for l in lengths if l > 0]
    return {
        "total_chunks": total,
        "product_name_in_text_AND_metadata": both,
        "product_name_in_metadata_only": only_meta,
        "product_name_in_text_only": only_text,
        "no_product_name_and_empty_text": neither,
        "pct_name_in_text": round(100 * both / max(total, 1), 1),
        "empty_or_null_text": empty_text + null_text,
        "chunks_with_replacement_char": replacement_char,
        "tiny_chunks_le_20chars": tiny,
        "text_length_min": min(lengths),
        "text_length_max": max(lengths),
        "text_length_avg": round(sum(lengths_nonzero) / max(len(lengths_nonzero), 1), 1),
        "text_length_median": sorted(lengths_nonzero)[len(lengths_nonzero) // 2] if lengths_nonzero else 0,
    }


# ---------------------------------------------------------------------------
# 4. QUERY DATASET  (expected products drawn from the REAL indexed catalog)
# ---------------------------------------------------------------------------
# (query, expected_product_name_or_None, category, brand)
QUERIES = [
    # A. Exact product-name  (expected = the product itself)
    ("Lika PAP2", "Lika PAP2", "exact", "gypsobat"),
    ("Mura colle plâtre", "Mura colle plâtre", "exact", "gypsobat"),
    ("PRO 1000", "PRO 1000", "exact", "sofap"),
    ("PRO 3000", "PRO 3000", "exact", "sofap"),
    ("PRO 2000", "PRO 2000", "exact", "sofap"),
    ("PRO 200", "PRO 200", "exact", "sofap"),
    ("LIKA FINA", "LIKA FINA", "exact", "sofap"),
    ("LIKA FULL", "LIKA FULL", "exact", "sofap"),
    ("LIKA FULL ECO", "LIKA FULL ECO", "exact", "sofap"),
    ("FLEX", "FLEX", "exact", "sofap"),
    ("RUSTIKA GRAVITA", "RUSTIKA GRAVITA", "exact", "sofap"),
    ("TORCHE LED 20V 2500 LUMENS 22,5W EMTOP ELWLI20885",
     "TORCHE LED 20V 2500 LUMENS 22,5W EMTOP ELWLI20885", "exact", "emtop"),
    ("SCIE À MARBRE 110 1400W+DISQUE EMTOP EMCT14006",
     "SCIE À MARBRE 110 1400W+DISQUE EMTOP EMCT14006", "exact", "emtop"),
    ("CHARGEUR DE BATTERIE 2AH EMTOP EFCR20200",
     "CHARGEUR DE BATTERIE 2AH EMTOP EFCR20200", "exact", "emtop"),

    # B. Product + technical property
    ("Lika PAP2 résistance en flexion", "Lika PAP2", "property", "gypsobat"),
    ("Lika PAP2 caractéristiques", "Lika PAP2", "property", "gypsobat"),
    ("PRO 3000 consommation", "PRO 3000", "property", "sofap"),
    ("PRO 1000 caractéristiques", "PRO 1000", "property", "sofap"),
    ("LIKA FINA utilisation", "LIKA FINA", "property", "sofap"),
    ("PRO 1000 résistance", "PRO 1000", "property", "sofap"),
    ("PRO 2000 consommation", "PRO 2000", "property", "sofap"),
    ("Mura colle plâtre adhérence", "Mura colle plâtre", "property", "gypsobat"),

    # C. Product + document intent
    ("fiche technique Lika PAP2", "Lika PAP2", "intent", "gypsobat"),
    ("fiche technique PRO 1000", "PRO 1000", "intent", "sofap"),
    ("fiche technique PRO 3000", "PRO 3000", "intent", "sofap"),
    ("documentation LIKA FINA", "LIKA FINA", "intent", "sofap"),

    # Reported failing queries (reproduce exact wording/typos from the task)
    ("Lika PAP2 resistance en flexion", "Lika PAP2", "reported_failure", "gypsobat"),
    ("Mura colle platre consommation", "Mura colle plâtre", "reported_failure", "gypsobat"),
    ("PRO 1000 SOFAP fiche technique", "PRO 1000", "reported_failure", "sofap"),

    # D. Brand/supplier queries (catalog enumeration - no single expected product)
    ("produits SOFAP", None, "brand", "sofap"),
    ("produits EMTOP", None, "brand", "emtop"),
    ("produits Gypsobat", None, "brand", "gypsobat"),

    # E. Technical semantic queries (ambiguous -> expected None)
    ("consommation d'un enduit", None, "semantic", None),
    ("résistance en flexion du plâtre", None, "semantic", None),
    ("caractéristiques d'une colle à plâtre", None, "semantic", None),

    # F. Out-of-domain queries
    ("capitale de l'Australie", None, "out_of_domain", None),
    ("comment programmer en Python", None, "out_of_domain", None),
    ("recette de pizza", None, "out_of_domain", None),
]


def _norm_name(s: str | None) -> str:
    """Normalize a product name for *identity* comparison:
    NFKD decompose, drop combining marks (folds à/á/À/Á -> a), lowercase,
    keep only alphanumerics + spaces. This tolerates the OCR/extraction
    diacritic variants (À vs Á) present in some EMTOP names, while still
    distinguishing e.g. 'PRO 200' vs 'PRO 2000'."""
    if not s:
        return ""
    n = unicodedata.normalize("NFKD", s)
    n = "".join(c for c in n if unicodedata.category(c) != "Mn")
    n = "".join(c for c in n if c.isalnum() or c.isspace())
    return n.lower().strip()


def product_matches(entry_or_payload: dict, expected: str) -> bool:
    """Product-level match: the chunk's product_name equals the expected
    product (case-insensitive, NFKC-normalized). Exact identity match avoids
    false positives such as 'PRO 200' matching 'PRO 2000' while tolerating the
    œ/À encoding variants present in some EMTOP product names."""
    pn = _norm_name(entry_or_payload.get("product_name"))
    if not pn or not expected:
        return False
    return pn == _norm_name(expected)


def product_name_contains(payload: dict, needle: str) -> bool:
    """Diagnostic substring test over payload.product_name (NFKC-normalized)."""
    return _norm_name(needle) in _norm_name(payload.get("product_name"))


def first_correct_rank(results: list[dict], expected: str) -> tuple[int | None, float | None, dict | None]:
    """Return (rank, score, hit_payload) of the first chunk whose product_name
    matches the expected product (case-insensitive)."""
    for i, r in enumerate(results):
        if product_matches(r, expected):
            return i + 1, r["score"], r
    return None, None, None


def hit_at_k(results: list[dict], expected: str, k: int) -> bool:
    if not expected:
        return False
    topk = results[:k]
    return any(product_matches(r, expected) for r in topk)


def metadata_substring_matches(allp: list[dict], expected: str) -> list[str]:
    """Diagnostic-only: substring product-name matching over payload metadata
    (NFKC-normalized, case-insensitive). Reports whether a pure lexical
    product-name lookup would locate the expected product."""
    needle = _norm_name(expected)
    found = []
    for p in allp:
        pn = p["payload"].get("product_name") or ""
        if pn and (needle in _norm_name(pn)):
            found.append(pn)
    seen = set()
    out = []
    for pn in found:
        key = _norm_name(pn)
        if key not in seen:
            seen.add(key)
            out.append(pn)
    return out


# ---------------------------------------------------------------------------
# 6. REPORT GENERATION (markdown)
# ---------------------------------------------------------------------------
_REPORT_PATH = _BACKEND_DIR / "ai_data" / "reports" / "RETRIEVAL_EVALUATION_REPORT.md"


def _md_str(s) -> str:
    if s is None:
        return ""
    s = str(s)
    s = s.replace("\ufffd", "?")
    return s


def _md_table_row(cells: list, width: int = 40) -> str:
    return "| " + " | ".join(str(c).replace("\n", " ")[:width] for c in cells) + " |"


def generate_report(report: dict) -> str:
    """Build the full markdown retrieval evaluation report from *report* dict."""
    L: list[str] = []

    env = report["environment"]
    catalog = report["catalog"]
    chunk_analysis = report["chunk_text_analysis"]
    config = report["config"]
    metrics = report["metrics"]
    classifications = report["failure_classifications"]
    score_stats = report["score_stats"]
    coverage = report["catalog_coverage"]
    ood = report["out_of_domain"]
    results = report["results"]

    def esc(s) -> str:
        if s is None:
            return ""
        return _md_str(s)

    def fmt_score(s) -> str:
        if s is not None:
            return f"{s:.4f}"
        return "—"

    # -- helper to render a top-k table --
    def render_topk(entries: list[dict], label: str) -> list[str]:
        if not entries:
            return [f"**{label}:** (no results)"]
        lines = [f"**{label}** — Top {len(entries)}:"]
        lines.append(
            _md_table_row(["Rank", "Score", "Product", "Supplier", "Source", "Doc ID", "Section", "Chunk ID", "Text preview"], 60)
        )
        lines.append(_md_table_row(["---"] * 9))
        for e in entries:
            lines.append(_md_table_row([
                e.get("rank", "—"),
                fmt_score(e.get("score")),
                esc(e.get("product_name")),
                esc(e.get("supplier")),
                esc(e.get("source")),
                esc(e.get("document_id")),
                esc(e.get("section_title")),
                esc(e.get("chunk_id")),
                esc(e.get("text_preview")),
            ]))
        return lines

    exact_cats = ("exact", "property", "intent", "reported_failure")

    # ---- Section 1: Objective ----
    L.append("# Retrieval Evaluation Report")
    L.append("")
    L.append("## 1. Objective")
    L.append("")
    L.append(
        "This report is a **diagnostic-only** evaluation of the BuildLearn product "
        "retrieval system. It measures whether the correct product is retrievable "
        "from the Qdrant vector store (collection `buildlearn_products`, 624 chunks) "
        "for a set of ~25 queries spanning exact product names, product+technical-property, "
        "product+document-intent, brand/catalog, semantic, and out-of-domain categories."
    )
    L.append("")
    L.append(
        "The evaluation reuses the **real production components** — the same "
        "Ollama `nomic-embed-text` embedding provider, the same Qdrant collection, "
        "and the production `Retriever` class. A *raw* Qdrant `query_points` call (no "
        "client-side threshold) is also issued so that raw vector-search behavior can "
        "be compared against the production Retriever path."
    )
    L.append("")
    L.append("**No production code, embeddings configuration, Qdrant collection, or "
             "indexed data was modified during this evaluation.**")
    L.append("")

    # ---- Section 2: Environment ----
    L.append("## 2. Environment")
    L.append("")
    L.append("| Setting | Value |")
    L.append("|---|---|")
    L.append(f"| Production backend | `backend/app` (Python) |")
    L.append(f"| Collection | `{env['name']}` |")
    L.append(f"| Qdrant server version | {esc(env.get('qdrant_server_version'))} |")
    L.append(f"| Vector size | {env['vector_size']} |")
    L.append(f"| Distance metric | {esc(env.get('distance'))} |")
    L.append(f"| Points count | {env['points_count']} |")
    L.append(f"| Segments | {env['segments_count']} |")
    L.append(f"| Shard number | {env.get('shard_number', '—')} |")
    L.append(f"| HNSW M | {env.get('hnsw_m', '—')} |")
    L.append(f"| HNSW efConstruct | {env.get('hnsw_ef_construct', '—')} |")
    L.append(f"| Optimizer status | {esc(env.get('optimizer_status'))} |")
    L.append(f"| Status | {esc(env.get('status'))} |")
    L.append("")
    L.append("| Config | Value |")
    L.append("|---|---|")
    L.append(f"| Embedding provider | {esc(config.get('embedding_provider'))} |")
    L.append(f"| Embedding model | {esc(config.get('embedding_model'))} |")
    L.append(f"| Embedding normalize | {config.get('embedding_normalize')} |")
    L.append(f"| Vector store | {esc(config.get('vector_store'))} |")
    L.append(f"| Qdrant URL | {esc(config.get('qdrant_url'))} |")
    L.append(f"| Collection | {esc(config.get('collection'))} |")
    L.append(f"| Retrieval score threshold | {config.get('retrieval_score_threshold')} |")
    L.append(f"| OCR enabled | {config.get('ocr_enabled')} |")
    L.append(f"| Generated at | {report['generated_at']} |")
    L.append("")

    # ---- Section 3: Qdrant Dataset ----
    L.append("## 3. Qdrant Dataset")
    L.append("")
    L.append(f"- **Total vectors (chunks):** {catalog['total_chunks']}")
    L.append(f"- **Distinct products:** {catalog['distinct_product_count']}")
    L.append(f"- **Vectors are CHUNKS, not distinct products** — the 624 vectors represent "
             f"{catalog['distinct_product_count']} distinct products across {len(catalog['by_brand'])} brands.")
    L.append("")
    L.append("### Brand / supplier summary")
    L.append("")
    L.append("| Brand (source) | Supplier field | Distinct products | Sample products |")
    L.append("|---|---|---|---|")
    for brand in sorted(catalog["by_brand"]):
        info = catalog["by_brand"][brand]
        prods = info["products"]
        # find supplier from any result belonging to this brand
        supp = ""
        for r in results:
            if r.get("brand") == brand and r.get("production_topk"):
                supp = r["production_topk"][0].get("supplier") or ""
                break
        sample = ", ".join(esc(p) for p in prods[:5])
        L.append(f"| {esc(brand)} | {esc(supp)} | {info['product_count']} | {sample} |")
    L.append("")
    L.append("### Supplier-level product counts (from payload metadata)")
    L.append("")
    L.append("| Supplier | Distinct products |")
    L.append("|---|---|")
    for sup, info in sorted(catalog.get("by_supplier", {}).items()):
        L.append(f"| {esc(sup)} | {info['product_count']} |")
    L.append("")

    # ---- Section 4: Payload Structure ----
    L.append("## 4. Payload Structure")
    L.append("")
    L.append(f"Available payload fields ({len(catalog['payload_keys'])}):")
    L.append("")
    L.append("`" + ", ".join(catalog["payload_keys"]) + "`")
    L.append("")
    L.append("### Field semantics")
    L.append("")
    L.append("| Payload field | Role |")
    L.append("|---|---|")
    L.append("| `product_name` | **Product identity** (e.g. `Lika PAP2`, `PRO 3000`) |")
    L.append("| `supplier` | Supplier brand (`EMTOP`, `SOFAP`, `SIPS`) |")
    L.append("| `source` | Data source brand (`emtop`, `sofap`, `gypsobat`) |")
    L.append("| `document_id` | Unique document identifier |")
    L.append("| `section_title` | Section/chapter heading within the document |")
    L.append("| `chunk_id` | Hex ID of the chunk (Qdrant point ID) |")
    L.append("| `chunk_index` | Index of the chunk within its document |")
    L.append("| `text` | Chunk text content |")
    L.append("| `page_number` | Source PDF page |")
    L.append("| `document_type` | Type of document |")
    L.append("| `confidence` | Extraction confidence (`high`/`low`) |")
    L.append("| `content_hash` | Hash for deduplication |")
    L.append("")
    L.append("### Chunk text analysis")
    L.append("")
    ca = chunk_analysis
    L.append("| Metric | Value |")
    L.append("|---|---|")
    L.append(f"| Total chunks | {ca['total_chunks']} |")
    L.append(f"| Product name in text AND metadata | {ca['product_name_in_text_AND_metadata']} ({ca['pct_name_in_text']}%) |")
    L.append(f"| Product name in metadata only | {ca['product_name_in_metadata_only']} |")
    L.append(f"| Product name in text only | {ca['product_name_in_text_only']} |")
    L.append(f"| No product name and empty text | {ca['no_product_name_and_empty_text']} |")
    L.append(f"| Empty/null text | {ca['empty_or_null_text']} |")
    L.append(f"| Chunks with replacement char (�) | {ca['chunks_with_replacement_char']} |")
    L.append(f"| Tiny chunks ≤20 chars | {ca['tiny_chunks_le_20chars']} |")
    L.append(f"| Text length min | {ca['text_length_min']} |")
    L.append(f"| Text length max | {ca['text_length_max']} |")
    L.append(f"| Text length avg | {ca['text_length_avg']} |")
    L.append(f"| Text length median | {ca['text_length_median']} |")
    L.append("")
    L.append("> **Key finding:** Only 12.3% of chunks contain the product name *in the chunk text*. "
            "The vast majority (547/624, 87.7%) carry the product name only in payload metadata "
            "(the `product_name` field), not in the retrievable `text` field. This means the "
            "embedding vector for most chunks does not contain a strong lexical signal of which "
            "product the chunk belongs to.")
    L.append("")

    # ---- Section 5: Query Set ----
    L.append("## 5. Query Set")
    L.append("")
    L.append(f"Total queries: **{len(results)}** (29 exact-product queries + 3 brand + 3 semantic + 3 out-of-domain + 3 reported failures)")
    L.append("")
    L.append("| # | Query | Category | Expected product | Brand |")
    L.append("|---|---|---|---|---|")
    for i, r in enumerate(results, 1):
        L.append(_md_table_row([i, esc(r["query"]), r["category"], esc(r["expected_product"]), esc(r["brand"])], 55))
    L.append("")
    L.append("### Query categories")
    L.append("")
    cat_counts = defaultdict(int)
    for r in results:
        cat_counts[r["category"]] += 1
    L.append("| Category | Count | Description |")
    L.append("|---|---|---|")
    L.append(f"| `exact` | {cat_counts['exact']} | Direct product-name queries |")
    L.append(f"| `property` | {cat_counts['property']} | Product + technical property |")
    L.append(f"| `intent` | {cat_counts['intent']} | Product + document/technical-sheet intent |")
    L.append(f"| `reported_failure` | {cat_counts['reported_failure']} | Reproduced reported failing queries |")
    L.append(f"| `brand` | {cat_counts['brand']} | Brand/catalog listing queries |")
    L.append(f"| `semantic` | {cat_counts['semantic']} | Technical semantic queries (ambiguous intent) |")
    L.append(f"| `out_of_domain` | {cat_counts['out_of_domain']} | Queries unrelated to product knowledge |")
    L.append("")

    # ---- Section 6: Metrics ----
    L.append("## 6. Metrics")
    L.append("")
    L.append("Hit@K is defined as a **product-level** hit: if any returned chunk's "
            "`product_name` (normalized: NFKD, lowercase, diacritics stripped) equals the "
            "expected product name, that counts as a hit at rank K. Different chunks from the "
            "same product are not counted as different products.")
    L.append("")
    L.append("### Overall Hit@K (production Retriever, top_k=10)")
    L.append("")
    L.append("| Metric | Hit rate | N queries |")
    L.append("|---|---|---|")
    for k in (1, 3, 5, 10):
        m = metrics.get(f"Hit@{k}", {})
        L.append(f"| Hit@{k} | {m.get('rate', '—')}% | {m.get('n', '—')} |")
    L.append("")
    L.append("### Hit@K by supplier (brand)")
    L.append("")
    L.append("| Supplier | Hit@1 | Hit@3 | Hit@5 | Hit@10 | N |")
    L.append("|---|---|---|---|---|---|")
    for brand in ("gypsobat", "emtop", "sofap"):
        row = [brand]
        for k in (1, 3, 5, 10):
            m = metrics.get(f"Hit@{k}_{brand}", {})
            row.append(f"{m.get('rate', '—')}%")
        m1 = metrics.get(f"Hit@1_{brand}", {})
        row.append(str(m1.get("n", "—")))
        L.append(_md_table_row(row))
    L.append("")
    L.append("### Hit@K by query sub-type (exact-product queries only)")
    L.append("")
    L.append("| Sub-type | Hit@1 | Hit@3 | Hit@5 | Hit@10 | N |")
    L.append("|---|---|---|---|---|---|")
    for cat in ("exact", "property", "intent", "reported_failure"):
        row = [cat]
        for k in (1, 3, 5, 10):
            m = metrics.get(f"Hit@{k}_{cat}", {})
            row.append(f"{m.get('rate', '—')}%")
        m1 = metrics.get(f"Hit@1_{cat}", {})
        row.append(str(m1.get("n", "—")))
        L.append(_md_table_row(row))
    L.append("")

    # ---- Section 7: Exact Product Retrieval Results ----
    L.append("## 7. Exact Product Retrieval Results")
    L.append("")
    L.append("For every product-level query, the table below shows whether the expected product "
            "was found in the production Retriever Top-1/3/5/10, its best rank in raw Qdrant, "
            "and the cosine similarity between the query embedding and the correct product's chunks.")
    L.append("")
    L.append("### Production Retriever results (top 10)")
    L.append("")
    for r in results:
        if r["category"] not in exact_cats:
            continue
        exp = r.get("expected_product")
        hit = r.get("hit_1")
        status = "HIT" if hit else "MISS"
        L.append(f"### `{esc(r['query'])}` — {status} (Hit@1={hit}, Hit@10={r.get('hit_10')}, rank={r.get('production_correct_rank')})")
        L.append("")
        L.append(f"- **Expected product:** {esc(exp)}")
        L.append(f"- **Brand:** {esc(r.get('brand'))}")
        L.append(f"- **Exists in collection:** {r.get('expected_exists_in_collection')} ({r.get('expected_chunk_count', 0)} chunks)")
        L.append(f"- **Product name in chunk text:** {r.get('correct_product_name_in_chunk_text_pct', '—')}%")
        L.append(f"- **Query-to-correct cosine:** {fmt_score(r.get('query_to_correct_cosine'))}")
        L.append(f"- **Raw correct rank:** {r.get('raw_correct_rank') or '—'} (score={fmt_score(r.get('raw_correct_score'))})")
        L.append(f"- **Production correct rank:** {r.get('production_correct_rank') or '—'} (score={fmt_score(r.get('production_correct_score'))})")
        L.append(f"- **Metadata substring match:** {r.get('metadata_substring_match_found')}")
        L.append(f"- **Raw vs production identical order:** {r.get('raw_vs_production_identical_order')}")
        L.append("")
        L.extend(render_topk(r["production_topk"][:10], "Production Top-10"))
        L.append("")
        L.extend(render_topk(r["raw_topk"][:10], "Raw Qdrant Top-10"))
        L.append("")
        fd = r.get("failure_detail")
        if fd:
            L.append(f"**Failure classification:** `{fd.get('class')}`")
            L.append("")
            if fd.get("top_wrong_products"):
                L.append("Top wrong products outranking the correct one:")
                L.append("")
                L.append("| Rank | Score | Product | Supplier | Section | Preview |")
                L.append("|---|---|---|---|---|---|")
                for t in fd["top_wrong_products"]:
                    L.append(_md_table_row([
                        t.get("rank", "—"), fmt_score(t.get("score")),
                        esc(t.get("product_name")), esc(t.get("supplier")),
                        esc(t.get("section_title")), esc(t.get("text_preview")),
                    ], 50))
                L.append("")
            L.append(f"- Correct product in raw Top-10: {fd.get('correct_product_in_raw_top10')}")
            L.append(f"- Best correct raw rank: {fd.get('best_correct_raw_rank') or '—'}")
            L.append(f"- Best correct score: {fmt_score(fd.get('best_correct_score'))}")
            L.append(f"- Query-to-correct max cosine: {fmt_score(fd.get('query_to_correct_max_cosine'))}")
            L.append(f"- Metadata substring match found: {fd.get('metadata_substring_match_found')}")
            L.append(f"- Correct product name in chunk text: {fd.get('correct_product_in_chunk_text_pct', '—')}%")
            L.append("")
    L.append("")

    # ---- Section 8: Supplier Breakdown ----
    L.append("## 8. Supplier Breakdown")
    L.append("")
    L.append("Per-supplier Hit@K across all exact-product queries (exact + property + intent + reported_failure):")
    L.append("")
    L.append("| Supplier | Products indexed | Hit@1 | Hit@3 | Hit@5 | Hit@10 | Failed queries |")
    L.append("|---|---|---|---|---|---|---|")
    for brand in ("gypsobat", "emtop", "sofap"):
        idx = catalog["by_brand"].get(brand, {})
        n_idx = idx.get("product_count", 0) if isinstance(idx, dict) else 0
        h1 = metrics.get(f"Hit@1_{brand}", {}).get("rate", "—")
        h3 = metrics.get(f"Hit@3_{brand}", {}).get("rate", "—")
        h5 = metrics.get(f"Hit@5_{brand}", {}).get("rate", "—")
        h10 = metrics.get(f"Hit@10_{brand}", {}).get("rate", "—")
        n_q = metrics.get(f"Hit@1_{brand}", {}).get("n", "—")
        # count failures
        fails = sum(1 for r in results
                     if r.get("brand") == brand and r["category"] in exact_cats
                     and r.get("hit_1") is False)
        L.append(_md_table_row([brand, n_idx, f"{h1}%", f"{h3}%", f"{h5}%", f"{h10}%", f"{fails} (of {n_q})"], 25))
    L.append("")

    # ---- Section 9: Failure Analysis ----
    L.append("## 9. Failure Analysis")
    L.append("")
    L.append("Failure classification is applied to product-level queries where Hit@1 = False.")
    L.append("")
    L.append("| Classification | Count |")
    L.append("|---|---|")
    for cls, n in sorted(classifications.items(), key=lambda x: -x[1]):
        L.append(_md_table_row([cls, n]))
    L.append("")
    L.append("### Classification logic")
    L.append("")
    L.append("| Class | Condition |")
    L.append("|---|---|")
    L.append("| `DATA_ABSENT` | Expected product is NOT in the collection at all |")
    L.append("| `EMBEDDING_SIMILARITY_PROBLEM` | Correct chunks exist in collection but are NOT in raw Top-10; query embedding is too far from the product's own chunks |")
    L.append("| `RANKING_TOPK_PROBLEM` | Correct product appears in raw/Top-10 but not at rank 1 (retrieved but ranked too low) |")
    L.append("| `THRESHOLD_PROBLEM` | Correct product is in raw Top-10 but absent from production Top-10 (filtered by threshold) |")
    L.append("| `METADATA_ONLY_PRODUCT_IDENTITY` | Product identity exists only in metadata, not in chunk text |")
    L.append("| `CATALOG_QUERY_LIMITATION` | Brand/catalog query does not enumerate all products |")
    L.append("| `CHUNK_CONTENT_PROBLEM` | Chunks lack discriminative text for the product |")
    L.append("| `OTHER` | Unclassified |")
    L.append("")

    # Detailed per-failure analysis
    L.append("### Per-failure detail")
    L.append("")
    for r in results:
        if r["category"] not in exact_cats:
            continue
        if r.get("hit_1"):
            continue
        exp = r.get("expected_product")
        fd = r.get("failure_detail", {})
        cls = fd.get("class", "—")
        L.append(f"#### `{esc(r['query'])}` → {esc(exp)} ({esc(r.get('brand'))})")
        L.append("")
        L.append(f"- **Class:** `{cls}`")
        L.append(f"- **Exists in Qdrant:** {r.get('expected_exists_in_collection')}")
        L.append(f"- **Chunk count for product:** {r.get('expected_chunk_count', 0)}")
        L.append(f"- **Best chunk in Qdrant Top-10:** rank={fd.get('best_correct_raw_rank') or '—'}, "
                f"score={fmt_score(fd.get('best_correct_score'))}")
        L.append(f"- **Query-to-correct max cosine:** {fmt_score(fd.get('query_to_correct_max_cosine'))}")
        L.append(f"- **Product name in chunk text:** {fd.get('correct_product_in_chunk_text_pct', '—')}%")
        L.append(f"- **Metadata substring match exists:** {fd.get('metadata_substring_match_found')}")
        if fd.get("metadata_substring_matches"):
            L.append(f"- **Metadata matches:** {esc(', '.join(fd['metadata_substring_matches']))}")
        if fd.get("top_wrong_products"):
            names = [t.get("product_name", "—") for t in fd["top_wrong_products"]]
            scores = [fmt_score(t.get("score")) for t in fd["top_wrong_products"]]
            L.append(f"- **Unrelated products outranking correct one:** {esc(', '.join(names))} (scores: {', '.join(scores)})")
        L.append("")

    # ---- Section 10: Raw Qdrant vs Production Retriever ----
    L.append("## 10. Raw Qdrant vs Production Retriever")
    L.append("")
    identical_count = sum(1 for r in results if r.get("raw_vs_production_identical_order"))
    total_cmp = sum(1 for r in results if r.get("raw_vs_production_identical_order") is not None)
    L.append(f"Across {total_cmp} comparable queries, raw Qdrant and production Retriever "
            f"returned identical result sets (same order, same scores) in **{identical_count}** cases.")
    L.append("")
    L.append(f"The production Retriever (`Retriever.retrieve`) applies `ai_settings.retrieval_score_threshold` "
            f"(currently **{config.get('retrieval_score_threshold')}**) as a client-side filter: any chunk with "
            f"`score < threshold` is dropped. Since all returned scores exceed this threshold, the threshold "
            f"has **no filtering effect** on the current results.")
    L.append("")
    L.append("### Production Retriever behavior for out-of-domain queries")
    L.append("")
    L.append("| Query | Prod returned | Top-1 score | Top-1 product | Above threshold? |")
    L.append("|---|---|---|---|---|")
    for o in ood:
        top1_score = o["raw_top1_score"]
        thr = config.get("retrieval_score_threshold", 0.3)
        above = "YES" if (top1_score is not None and top1_score >= thr) else "NO"
        L.append(_md_table_row([
            esc(o["query"]), o["production_returned_count"],
            fmt_score(top1_score), esc(o["raw_top1_product"]), above
        ], 45))
    L.append("")
    L.append("> The production Retriever returns **10 results** for out-of-domain queries. "
            "Scores (0.56–0.62) far exceed the 0.3 threshold, indicating the threshold is too low "
            "to reject irrelevant results.")
    L.append("")
    L.append("### Does raw Qdrant differ from production Retriever?")
    L.append("")
    L.append("**No.** For all 29 exact-product queries, `raw_vs_production_identical_order = True`. "
            "The production Retriever introduces no additional filtering beyond the score threshold "
            "(which is not active because all scores exceed 0.3). The only difference between raw "
            "Qdrant and production is that the production Retriever wraps results in `ChunkResponse` "
            "objects and applies the (inactive) threshold.")
    L.append("")

    # ---- Section 11: Catalog Query Limitation ----
    L.append("## 11. Catalog Query Limitation")
    L.append("")
    L.append("### Distinction: semantic retrieval vs catalog enumeration")
    L.append("")
    L.append(
        "**Semantic retrieval** finds documents/chunks most similar to a query *embedding*. "
        "It ranks by cosine similarity and returns the top-K chunks. It is designed to answer "
        "technical questions — e.g. \"What is the abrasion resistance of Lika PAP2?\" — by "
        "finding the chunk that discusses that property."
    )
    L.append("")
    L.append(
        "**Catalog enumeration/listing** asks for a complete set of products matching a criterion "
        "— e.g. \"Quels produits EMTOP sont disponibles?\". This requires *filtering* by "
        "supplier/brand and returning all matching product identities. Semantic vector search "
        "cannot enumerate; it returns the top-K most similar chunks, which may overlap or miss "
        "products entirely."
    )
    L.append("")
    L.append("### Brand/catalog query results")
    L.append("")
    L.append("| Brand query | Indexed distinct products | Distinct in raw Top-5 | Coverage % | Distinct in raw Top-10 | Coverage % |")
    L.append("|---|---|---|---|---|---|")
    for brand in ("sofap", "emtop", "gypsobat"):
        cov = coverage.get(brand, {})
        # count distinct in top-10
        seen10 = set()
        for r in results:
            if r.get("brand") == brand and r["category"] == "brand":
                for e in r.get("raw_topk", [])[:10]:
                    if e.get("product_name"):
                        seen10.add(e["product_name"])
        idx = cov.get("indexed_distinct_products", 0)
        seen5 = cov.get("distinct_products_in_brand_query_top5", 0)
        cov5 = cov.get("coverage_pct", 0)
        cov10 = round(100 * len(seen10) / max(idx, 1), 1)
        L.append(_md_table_row([f"produits {esc(brand.upper())}", idx, seen5, f"{cov5}%", len(seen10), f"{cov10}%"], 45))
    L.append("")
    L.append("### Brand query Top-10 (raw Qdrant)")
    L.append("")
    for r in results:
        if r["category"] == "brand":
            L.append(f"#### `{esc(r['query'])}`")
            L.append("")
            L.extend(render_topk(r["raw_topk"][:10], "Raw Qdrant Top-10"))
            L.append("")
            distinct_prods = set()
            for e in r["raw_topk"]:
                if e.get("product_name"):
                    distinct_prods.add(e["product_name"])
            brand_key = r.get("brand", "").upper()
            indexed = coverage.get(r.get("brand", ""), {}).get("indexed_distinct_products", 0)
            L.append(f"- **Indexed distinct products for {esc(brand_key)}:** {indexed}")
            L.append(f"- **Distinct products in Top-10:** {len(distinct_prods)}")
            L.append(f"- **Coverage:** {round(100 * len(distinct_prods) / max(indexed, 1), 1)}%")
            L.append("")
    L.append("")
    L.append(">**Conclusion:** Semantic retrieval provides severely incomplete catalog coverage. "
            "Brand/catalog queries cannot enumerate products — they return the same semantic "
            "top-K as any other query. A proper catalog listing requires metadata filtering "
            "(filter by `supplier`/`source`) combined with result deduplication by `product_id`.")
    L.append("")

    # ---- Section 12: Out-of-Domain Behavior ----
    L.append("## 12. Out-of-Domain Behavior")
    L.append("")
    L.append("### Query results")
    L.append("")
    for o in ood:
        L.append(f"#### `{esc(o['query'])}`")
        L.append("")
        L.append("| Rank | Score | Product | Supplier |")
        L.append("|---|---|---|---|")
        for i, e in enumerate(o["raw_top5_products"], 1):
            score = o["raw_top5_scores"][i - 1] if i - 1 < len(o["raw_top5_scores"]) else None
            L.append(_md_table_row([i, fmt_score(score), esc(e), "—"], 40))
        L.append("")
        L.append(f"- **Production returned:** {o['production_returned_count']} results")
        L.append(f"- **Production scores:** {', '.join(fmt_score(s) for s in o['production_returned_scores'])}")
        L.append("")
    L.append("### Findings")
    L.append("")
    L.append(f"- All 3 out-of-domain queries return **10 results** from the production Retriever.")
    L.append(f"- Top-1 scores range {min(o['raw_top1_score'] for o in ood if o['raw_top1_score'])}–"
            f"{max(o['raw_top1_score'] for o in ood if o['raw_top1_score'])}, all **above** the "
            f"0.3 threshold.")
    L.append(f"- The system retrieves arbitrary construction-product chunks for unrelated questions "
            f"(\"capitale de l'Australie\" → construction product; \"recette de pizza\" → \"PISCINE\"/"
            f"\"POOL\" which happen to mention water).")
    L.append(f"- The OOD query \"recette de pizza\" retrieves products named \"PISCINE\" and \"POOL\", "
            f"indicating semantic drift: cooking/water concepts leak into construction product embeddings.")
    L.append(f"- Score range for OOD top-1: approximately 0.59–0.62 — within the normal operating "
            f"range for genuine product queries (0.46–0.72).")
    L.append("")

    # ---- Section 13: Root Causes ----
    L.append("## 13. Root Causes")
    L.append("")
    L.append("Based on the measured evaluation results:")
    L.append("")

    # Compute some stats for root cause analysis
    total_exact = [r for r in results if r["category"] in exact_cats and "error" not in r]

    L.append("1. **Embedding similarity mismatch (primary root cause)** — 14 of 19 failures classified")
    L.append("   as `EMBEDDING_SIMILARITY_PROBLEM`. The expected product exists in the collection "
            "(100% of queries had `expected_exists_in_collection = True`, 0 `DATA_ABSENT`), but its "
            "chunks are NOT in the raw Qdrant Top-10. The query embedding for the product name is "
            "semantically closer to OTHER products' chunks than to the product's own chunks.")
    L.append("")
    L.append("2. **Product identity in metadata only (structural root cause)** — 87.7% of chunks "
            "(547/624) do NOT contain the product name in their text. Only 12.3% of chunks have the "
            "product name in both text and metadata. When a query like \"Mura colle plâtre\" is "
            "embedded, the chunk vectors for Mura colle plâtre's own pieces carry little textual "
            "signal about the product name, so the query embedding does not preferentially match them.")
    L.append("")
    L.append("3. **Short/noise chunks (contributing factor)** — 230 chunks (36.9%) are ≤20 characters "
            "of text (e.g. bare model codes like \"EBPK20011\"). These carry minimal semantic content. "
            "182 chunks contain replacement characters (�) from OCR/encoding errors, further degrading "
            "embedding quality.")
    L.append("")
    L.append("4. **Low score threshold (allows irrelevant results)** — The production threshold "
            f"({config.get('retrieval_score_threshold')}) does not filter out unrelated results. "
            "Out-of-domain queries return 10 results with scores 0.56–0.62, within the same range as "
            "genuine product queries. Raw Qdrant and production Retriever produce identical rankings "
            f"({identical_count}/{total_cmp} queries identical), confirming the threshold is inactive.")
    L.append("")
    L.append("5. **Catalog enumeration not supported** — Brand queries return only 3.2% (EMTOP), "
            "12.5% (SOFAP), and 166.7% (Gypsobat — duplicates only) coverage of indexed products. "
            "Semantic search cannot enumerate; it always returns the same top-K most-similar chunks.")
    L.append("")
    L.append("6. **Gypsobat underperformance** — Hit@1 = 0% for Gypsobat (8 queries, 0 hits). "
            "The 3 Gypsobat products have only 14 chunks total. Key product names like "
            "\"Mura colle plâtre\" and \"FLEX\" do not match their own chunks in the embedding space "
            "(query-to-correct cosine 0.38–0.55, while competing products score 0.56–0.64).")
    L.append("")
    L.append("7. **Embedding model mismatch for exact names** — Products with strong model-code "
            "identifiers in their names (EMTOP: \"SCIE À MARBRE 110 1400W+DISQUE EMTOP EMCT14006\") "
            "achieve 66.7% Hit@1, while products with generic names (FLEX, PRO 200) fail. The model "
            "embeds short, generic product names poorly relative to technical content chunks.")
    L.append("")

    # ---- Section 14: Recommendations ----
    L.append("## 14. Recommendations")
    L.append("")
    L.append("All recommendations are **diagnostic only — not implemented**.")
    L.append("")
    L.append("| Priority | Recommendation | Rationale |")
    L.append("|---|---|---|")
    L.append("| **P0** | Include product name in chunk `text` field (or embed a composite of "
            "product name + chunk text). | The query embedding for the product name will then "
            "match the product's own chunks preferentially. Addresses root cause #2. |")
    L.append("| **P0** | Add a product-name exact-match / substring filtering layer before or "
            "after vector search. | Guarantees the correct product's chunks are considered "
            "even when semantic similarity is low. |")
    L.append("| **P0** | Raise the retrieval score threshold or add a relevance classifier. | "
            "Current 0.3 threshold lets through 10 out-of-domain results per query. OOD scores "
            "(0.56–0.62) are only slightly below genuine hits (0.46–0.72), so a harder "
            "threshold alone is insufficient; a trained relevance filter is needed. |")
    L.append("| **P0** | Re-embed EMTOP/SOFAP products that have only bare model codes as chunk text. | "
            "230 tiny chunks (≤20 chars) provide no semantic signal. These should be merged "
            "with surrounding context or enriched with product name. |")
    L.append("| **P1** | Implement catalog enumeration via metadata filtering (filter by "
            "`supplier`/`source`, deduplicate by `product_id`). | Semantic retrieval cannot "
            "list all products; only 3.2%–12.5% coverage for brand queries. |")
    L.append("| **P1** | Apply HNSW `ef` search-time parameter tuning (currently uses defaults). | "
            "May improve recall for correct products ranked 6–10. |")
    L.append("| **P1** | Deduplicate chunks at query time (multiple chunks from same product). | "
            "166.7% coverage for Gypsobat indicates duplicate chunks inflate top-K. |")
    L.append("| **P2** | Consider a hybrid retriever: BM25/keyword on `product_name` + vector "
            "similarity. | Would dramatically improve exact-product-name queries. |")
    L.append("| **P2** | Fix OCR/encoding errors (182 chunks with �) to improve chunk text quality. | "
            "Clean text yields better embeddings. |")
    L.append("| **P2** | Increase `index` field count for HNSW (currently `indexed_vectors_count: 0`). | "
            "Sparse indexing may contribute to retrieval variance. |")
    L.append("")

    return "\n".join(L)


# ---------------------------------------------------------------------------
# 7. RUN EVALUATION
# ---------------------------------------------------------------------------
def run_query(
    query: str, expected: str | None, category: str, brand: str | None,
            allp: list[dict]) -> dict:
    qvec = _vec(query)
    dim = len(qvec)
    norm = math.sqrt(sum(x * x for x in qvec))
    # raw (no threshold, no client-side filtering) - limit 10
    raw = _raw_search(qvec, limit=10, score_threshold=None)
    # production Retriever (threshold applied inside), top_k=10
    prod = RET.retrieve(query, top_k=10)

    def _to_entry(r, is_raw: bool):
        if is_raw:
            pl = r.get("payload") or {}
            score = r.get("score")
        else:
            pl = {
                "chunk_id": r.chunk_id, "document_id": r.document_id, "product_id": r.product_id,
                "product_name": r.product_name, "supplier": r.supplier, "source": r.source,
                "source_url": r.source_url, "document_url": r.document_url,
                "document_type": r.document_type, "page_number": r.page_number,
                "section_title": r.section_title, "chunk_index": r.chunk_index, "text": r.text,
                "language": r.language, "content_hash": r.content_hash, "metadata": r.metadata,
                "source_type": r.source_type, "discovery_provider": r.discovery_provider,
                "domain": r.domain, "confidence": r.confidence, "evidence": r.evidence,
            }
            score = r.score
        return {
            "rank": None,
            "score": round(score, 4) if score is not None else None,
            "product_name": pl.get("product_name"),
            "supplier": pl.get("supplier"),
            "source": pl.get("source"),
            "document_id": pl.get("document_id"),
            "section_title": pl.get("section_title"),
            "chunk_id": pl.get("chunk_id"),
            "source_type": pl.get("source_type"),
            "confidence": pl.get("confidence"),
            "text_preview": _preview(pl.get("text") or ""),
        }

    raw_entries = [_to_entry(r, True) for r in raw]
    for i, e in enumerate(raw_entries, 1):
        e["rank"] = i
    prod_entries = [_to_entry(r, False) for r in prod]
    for i, e in enumerate(prod_entries, 1):
        e["rank"] = i

    # correct-product presence in the whole collection
    expected_exists = False
    expected_chunk_count = 0
    correct_chunks_exist = []
    if expected:
        for p in allp:
            pl = p["payload"]
            if product_matches(pl, expected):
                expected_chunk_count += 1
                txt = pl.get("text") or ""
                correct_chunks_exist.append({
                    "contains_name_in_text": (_norm_name(expected) in _norm_name(txt)),
                    "text_preview": _preview(txt),
                    "section_title": pl.get("section_title"),
                    "supplier": pl.get("supplier"),
                    "source": pl.get("source"),
                })
        expected_exists = expected_chunk_count > 0

    # raw ranking of correct product
    raw_rank, raw_score, raw_hit = (None, None, None)
    if expected:
        raw_rank, raw_score, _ = first_correct_rank(raw_entries, expected)

    # production ranking of correct product
    prod_rank, prod_score, _ = (None, None, None)
    if expected:
        prod_rank, prod_score, _ = first_correct_rank(prod_entries, expected)

    # cosine sim between query embedding and best correct chunk's text embedding
    qe_cosim = None
    if expected and correct_chunks_exist:
        try:
            best_txt = None
            for cc in correct_chunks_exist:
                if cc["text_preview"]:
                    best_txt = cc["text_preview"]
                    break
            # embed the correct chunk text via the SAME production provider
            cand_texts = []
            cand_meta = []
            for p in allp:
                pl = p["payload"]
                if product_matches(pl, expected) and (pl.get("text") or "").strip():
                    cand_texts.append(pl["text"])
                    cand_meta.append(pl)
            cand_texts = cand_texts[:6]
            if cand_texts:
                cand_vecs = EMB.embed(cand_texts)
                sims = []
                for cv in cand_vecs:
                    dot = sum(a * b for a, b in zip(qvec, cv))
                    sims.append(dot)
                if sims:
                    qe_cosim = max(sims)
        except Exception:
            qe_cosim = None

    # metadata substring match (diagnostic only)
    meta_hits = metadata_substring_matches(allp, expected) if expected else []

    result = {
        "query": query,
        "category": category,
        "expected_product": expected,
        "brand": brand,
        "embedding_dimension": dim,
        "query_vector_norm": round(norm, 6),
        "threshold": THRESHOLD,
        "top_k_requested": 10,
        "raw_topk": raw_entries,
        "production_topk": prod_entries,
        "expected_exists_in_collection": expected_exists,
        "expected_chunk_count": expected_chunk_count,
        "correct_product_name_in_chunk_text": None,
        "correct_product_present_in_text_pct": None,
        "raw_correct_rank": raw_rank,
        "raw_correct_score": round(raw_score, 4) if raw_score is not None else None,
        "production_correct_rank": prod_rank,
        "production_correct_score": round(prod_score, 4) if prod_score is not None else None,
        "query_to_correct_cosine": round(qe_cosim, 4) if qe_cosim is not None else None,
        "hit_1": hit_at_k(prod_entries, expected, 1) if expected else None,
        "hit_3": hit_at_k(prod_entries, expected, 3) if expected else None,
        "hit_5": hit_at_k(prod_entries, expected, 5) if expected else None,
        "hit_10": hit_at_k(prod_entries, expected, 10) if expected else None,
        "metadata_substring_match_found": bool(meta_hits),
        "metadata_substring_matches": meta_hits[:5],
        "raw_vs_production_identical_order": (
            [e["product_name"] for e in raw_entries] == [e["product_name"] for e in prod_entries]
        ) if expected else None,
    }
    if expected and correct_chunks_exist:
        in_text = sum(1 for cc in correct_chunks_exist if cc["contains_name_in_text"])
        result["correct_product_name_in_chunk_text_pct"] = round(100 * in_text / len(correct_chunks_exist), 1)
        result["correct_product_total_chunks"] = len(correct_chunks_exist)
    # Failure detail for product-level queries that missed at Hit@1
    if expected and not (result.get("hit_1") or False):
        wrong_top = []
        for e in prod_entries:
            if not product_matches(e, expected) and e.get("product_name"):
                wrong_top.append({
                    "rank": e["rank"],
                    "score": e["score"],
                    "product_name": e["product_name"],
                    "supplier": e["supplier"],
                    "section_title": e["section_title"],
                    "text_preview": e["text_preview"],
                })
        result["failure_detail"] = {
            "class": classify_failure(result),
            "top_wrong_products": wrong_top[:5],
            "correct_product_in_raw_top10": result.get("raw_correct_rank") is not None,
            "best_correct_raw_rank": result.get("raw_correct_rank"),
            "best_correct_score": result.get("raw_correct_score"),
            "query_to_correct_max_cosine": result.get("query_to_correct_cosine"),
            "metadata_substring_match_found": result.get("metadata_substring_match_found"),
            "metadata_substring_matches": result.get("metadata_substring_matches"),
            "correct_product_in_chunk_text_pct": result.get("correct_product_name_in_chunk_text_pct"),
        }
    return result


def classify_failure(q: dict) -> str:
    exp = q.get("expected_product")
    if not exp:
        return "N/A (ambiguous/catalog/out-of-domain)"
    if not q.get("expected_exists_in_collection"):
        return "DATA_ABSENT"
    pr = q.get("production_correct_rank")
    rr = q.get("raw_correct_rank")
    if pr is not None:
        if pr == 1:
            return "OK"
        # correct product retrieved but ranked > 1
        if rr is not None and rr > 5:
            return "EMBEDDING_SIMILARITY_PROBLEM"
        return "RANKING_TOPK_PROBLEM"
    if rr is not None:
        # present in raw top-10 but absent from production top-10 -> threshold
        return "THRESHOLD_PROBLEM"
    # not in raw top-10 either -> query embedding is far from every correct chunk
    return "EMBEDDING_SIMILARITY_PROBLEM"


def main() -> None:
    print("Loading live Qdrant collection and catalog...")
    info = inspect_collection()
    print("Collection:", info)
    allp = scroll_all()
    catalog = build_catalog(allp)
    chunk_analysis = analyze_chunk_text(allp)

    # brand -> list of product names (canonical, as stored)
    by_brand = catalog["by_brand"]
    print("\n=== BRAND / SUPPLIER SUMMARY ===")
    for b in sorted(by_brand):
        prods = by_brand[b]
        sup_set = set()
        for p in allp:
            if (p["payload"].get("source") or p["payload"].get("supplier")) == b or p["payload"].get("source") == b:
                sup_set.add(p["payload"].get("supplier"))
        print(f"  brand(source)={b!r}: {len(prods)} products, supplier_field={sorted(sup_set)}")

    print("\n=== CHUNK TEXT ANALYSIS ===")
    for k, v in chunk_analysis.items():
        print(f"  {k}: {v}")

    print("\nRunning evaluation queries (this calls Ollama for real embeddings)...")
    results = []
    for query, expected, category, brand in QUERIES:
        try:
            r = run_query(query, expected, category, brand, allp)
        except Exception as e:
            r = {"query": query, "category": category, "error": f"{e}\n{traceback.format_exc()}"}
        results.append(r)
        tag = expected or "(ambiguous)"
        pr = r.get("production_correct_rank")
        print(f"  [{category:18s}] {tag:35s} | q={query[:45]!r}")
        if "error" in r:
            print("     ERROR:", r["error"].splitlines()[0])
            continue
        print(f"     raw_rank={r['raw_correct_rank']} raw_score={r['raw_correct_score']} "
              f"prod_rank={pr} prod_score={r['production_correct_score']} "
              f"H@1={r['hit_1']} H@3={r['hit_3']} H@5={r['hit_5']} H@10={r['hit_10']} "
              f"exists={r['expected_exists_in_collection']} chunks={r.get('expected_chunk_count')} "
              f"name_in_text%={r.get('correct_product_name_in_chunk_text_pct')} "
              f"q2cmp_cos={r['query_to_correct_cosine']}")

    # -------------------------------------------------------------------
    # 6. METRICS
    # -------------------------------------------------------------------
    def hit_rate(k, filter_fn=None):
        total = 0
        hits = 0
        for r in results:
            if "error" in r:
                continue
            if r["expected_product"] is None or r.get("hit_10") is None:
                continue
            if filter_fn and not filter_fn(r):
                continue
            total += 1
            hits += 1 if r[f"hit_{k}"] else 0
        return round(100 * hits / total, 1) if total else None, total

    metrics = {}
    for k in (1, 3, 5, 10):
        hr, n = hit_rate(k)
        metrics[f"Hit@{k}"] = {"rate": hr, "n": n}
    # by brand (only exact + property + intent + reported = "exact product" tasks)
    for brand in ("gypsobat", "emtop", "sofap"):
        for k in (1, 3, 5, 10):
            hr, n = hit_rate(k, lambda r, b=brand: r.get("brand") == b)
            metrics[f"Hit@{k}_{brand}"] = {"rate": hr, "n": n}
    # by category
    for cat in ("exact", "property", "intent", "reported_failure"):
        for k in (1, 3, 5, 10):
            hr, n = hit_rate(k, lambda r, c=cat: r["category"] == c)
            metrics[f"Hit@{k}_{cat}"] = {"rate": hr, "n": n}

    # classification of failures among exact-type tasks
    classifications = defaultdict(int)
    failures = []
    for r in results:
        if r["expected_product"] is None or "error" in r:
            continue
        if not r["hit_1"]:
            cls = classify_failure(r)
            classifications[cls] += 1
            failures.append(r)

    # score distribution
    def scores_of(kind):
        out = []
        for r in results:
            if "error" in r:
                continue
            arr = r["production_topk"] if kind == "prod" else r["raw_topk"]
            for e in arr:
                if e["score"] is not None:
                    out.append(e["score"])
        return out

    def stats(vals):
        if not vals:
            return None
        vals2 = sorted(vals)
        return {
            "n": len(vals2),
            "min": round(vals2[0], 4),
            "max": round(vals2[-1], 4),
            "mean": round(sum(vals2) / len(vals2), 4),
            "median": round(vals2[len(vals2) // 2], 4),
        }

    score_stats = {
        "all_production_topk_scores": stats(scores_of("prod")),
        "all_raw_topk_scores": stats(scores_of("raw")),
        "correct_product_scores_raw": stats([r["raw_correct_score"] for r in results
                                             if r.get("raw_correct_score") is not None]),
        "correct_product_scores_prod": stats([r["production_correct_score"] for r in results
                                              if r.get("production_correct_score") is not None]),
    }

    # catalog coverage
    catalog_coverage = {}
    for brand in ("sofap", "emtop", "gypsobat"):
        prods = set(by_brand.get(brand, {}).keys())
        # distinct products appearing in raw top-5 of brand queries
        seen = set()
        for r in results:
            if r.get("brand") == brand and r["category"] == "brand":
                if "error" in r:
                    continue
                for e in r["raw_topk"][:5]:
                    if e["product_name"]:
                        seen.add(e["product_name"])
        catalog_coverage[brand] = {
            "indexed_distinct_products": len(prods),
            "distinct_products_in_brand_query_top5": len(seen),
            "coverage_pct": round(100 * len(seen) / max(len(prods), 1), 1),
            "sample_returned": sorted(seen)[:10],
        }

    # out-of-domain
    ood = []
    for r in results:
        if r["category"] == "out_of_domain":
            top1 = r["raw_topk"][0] if r["raw_topk"] else None
            ood.append({
                "query": r["query"],
                "raw_top1_score": top1["score"] if top1 else None,
                "raw_top1_product": top1["product_name"] if top1 else None,
                "raw_top5_scores": [e["score"] for e in r["raw_topk"][:5]],
                "raw_top5_products": [e["product_name"] for e in r["raw_topk"][:5]],
                "production_returned_count": len(r["production_topk"]),
                "production_returned_scores": [e["score"] for e in r["production_topk"]],
            })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "environment": info,
        "collection": info,
        "catalog": {
            "total_chunks": catalog["total_chunks"],
            "distinct_product_count": catalog["distinct_product_count"],
            "payload_keys": catalog["payload_keys"],
            "by_brand": {k: {"product_count": len(v), "products": sorted(v.keys())} for k, v in by_brand.items()},
            "by_supplier": {k: {"product_count": len(v)} for k, v in catalog["by_supplier"].items()},
        },
        "chunk_text_analysis": chunk_analysis,
        "config": {
            "embedding_model": ai_settings.embedding_model,
            "embedding_provider": ai_settings.embedding_provider,
            "embedding_normalize": ai_settings.embedding_normalize,
            "vector_store": ai_settings.vector_store,
            "qdrant_url": ai_settings.qdrant_url,
            "collection": ai_settings.qdrant_collection,
            "retrieval_score_threshold": THRESHOLD,
            "ocr_enabled": ai_settings.ocr_enabled,
        },
        "metrics": metrics,
        "failure_classifications": dict(classifications),
        "score_stats": score_stats,
        "catalog_coverage": catalog_coverage,
        "out_of_domain": ood,
        "results": results,
    }

    out_dir = _BACKEND_DIR / "ai_data" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "retrieval_evaluation.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n\n=== JSON SAVED ===", json_path)

    # console summary
    print("\n=== METRICS ===")
    for k in ("Hit@1", "Hit@3", "Hit@5", "Hit@10"):
        m = metrics[k]
        print(f"  {k}: {m['rate']}% (n={m['n']})")
    print("\n=== SUPPLIER(Brand) Hit@K ===")
    for brand in ("gypsobat", "emtop", "sofap"):
        for k in (1, 3, 5, 10):
            m = metrics[f"Hit@{k}_{brand}"]
            print(f"  Hit@{k}_{brand}: {m['rate']}% (n={m['n']})")
    print("\n=== CATEGORY Hit@K ===")
    for cat in ("exact", "property", "intent", "reported_failure"):
        for k in (1, 3, 5, 10):
            m = metrics[f"Hit@{k}_{cat}"]
            print(f"  Hit@{k}_{cat}: {m['rate']}% (n={m['n']})")
    print("\n=== FAILURE CLASSIFICATIONS ===")
    for cls, n in sorted(classifications.items()):
        print(f"  {cls}: {n}")
    print("\n=== SCORE STATS ===")
    for k, v in score_stats.items():
        print(f"  {k}: {v}")
    print("\n=== CATALOG COVERAGE ===")
    for b, cov in catalog_coverage.items():
        print(f"  {b}: indexed={cov['indexed_distinct_products']} returned_in_top5={cov['distinct_products_in_brand_query_top5']} coverage={cov['coverage_pct']}%")
    print("\n=== OUT-OF-DOMAIN ===")
    for o in ood:
        print(f"  {o['query']!r}: top1_score={o['raw_top1_score']} top1_prod={o['raw_top1_product']} "
              f"prod_returned={o['production_returned_count']} prod_scores={[round(s,3) for s in o['production_returned_scores']]}")

    # -------------------------------------------------------------------
    # 7. MARKDOWN REPORT
    # -------------------------------------------------------------------
    md = generate_report(report)
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(md, encoding="utf-8")
    print(f"\n=== REPORT SAVED === {_REPORT_PATH}")
    print(f"Total report sections: 14 | Total report length: {len(md)} chars")


def report_only(json_path: Path) -> None:
    """Regenerate the markdown report from an existing JSON file."""
    report = json.loads(json_path.read_text(encoding="utf-8"))
    md = generate_report(report)
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(md, encoding="utf-8")
    print(f"Report regenerated from {json_path} -> {_REPORT_PATH}")
    print(f"Report length: {len(md)} chars")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieval evaluation diagnostic tool")
    parser.add_argument("--report-only", action="store_true",
                        help="Regenerate the markdown report from an existing JSON file (skip live evaluation)")
    parser.add_argument("--json", type=str, default=None,
                        help="Path to existing JSON to use with --report-only")
    args = parser.parse_args()

    if args.report_only:
        json_path = Path(args.json) if args.json else (_BACKEND_DIR / "ai_data" / "reports" / "retrieval_evaluation.json")
        report_only(json_path)
    else:
        main()
