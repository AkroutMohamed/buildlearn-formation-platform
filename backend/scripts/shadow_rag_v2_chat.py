"""Compare local legacy and V2 services without endpoint/DB writes or flag changes."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter
from uuid import uuid4

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
# Match application startup's environment loading; never set an enable flag.
import app.config
from app.ai.config import ai_settings
from app.ai.api.rag_v2_endpoint import RAGV2ChatAdapter, rag_v2_enabled
from app.ai.rag.rag_service import RAGService
from app.ai.schemas.chat import ChatRequest
from qdrant_client import QdrantClient
from scripts.evaluate_rag_v2 import protected
from scripts.evaluate_hierarchical_retrieval import read_collection, LABELS

QUERIES = [
    ("S01", "Quelle puissance nominale indique EWPPJ15001 ?", "EWPPJ15001%20Technical%20Data.pdf"),
    ("S02", "Quelles tailles de douilles sont livrées avec ECIWL42461 ?", "ECIWL42461%20Technical%20Data.pdf"),
    ("S03", "Quel calibre maximal de tension DC affiche EDMR5310002 ?", "EDMR5310002%20Technical%20Data.pdf"),
    ("S04", "Quelle tension et quelle puissance LED indique ELWLI20885 ?", "ELWLI20885%20Technical%20Data.pdf"),
    ("S05", "Quel calibre maximal de courant alternatif indique EDMR762001 ?", "EDMR762001%20Technical%20Data.pdf"),
    ("S06", "À quelles applications est destinée EWPPQD07501 ?", "EWPPQD07501%20Technical%20Data.pdf"),
    ("S07", "Quelle tension a ABCXYZ957359 ?", None),
    ("S08", "J’ai besoin d’un outil, quelle est sa tension ?", None),
    ("S09", "EWPPJ15001 peut-il servir de pompe pour injection intraveineuse ?", None),
    ("S10", "Quel est le prix actuel de ELWLI20885 ?", None),
]


def collection_digest(client, name):
    records, offset = [], None
    while True:
        points, offset = client.scroll(name, limit=256, offset=offset, with_payload=True, with_vectors=True)
        records.extend(dict(id=str(p.id), payload=p.payload, vector=p.vector) for p in points)
        if offset is None:
            break
    records.sort(key=lambda r: r["id"])
    digest = hashlib.sha256(json.dumps(records, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    return dict(points=len(records), sha256=digest)


def call(service, request):
    started = perf_counter()
    try:
        response = service.run(request, history=[])
        record = dict(status="response", response=response.model_dump(mode="json"))
        audit = getattr(response, "_rag_v2_provenance", None)
        if audit is not None:
            record.update(status=audit["status"], provenance=audit)
        return record
    except Exception as exc:
        # Preserve technical failures separately; no guessed answer or fallback.
        return dict(status="technical_failure", error_type=type(exc).__name__)
    finally:
        print("shadow service duration_ms=" + str(round((perf_counter() - started) * 1000, 2)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restart", action="store_true")
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()
    if rag_v2_enabled():
        raise RuntimeError("Shadow evaluation requires RAG_V2_ENABLED to remain false")
    if args.batch_size < 1:
        parser.error("batch-size must be positive")
    before_files = protected()
    adapter_hash = hashlib.sha256((BACKEND / "app/ai/api/rag_v2_endpoint.py").read_bytes()).hexdigest()
    client = QdrantClient(url=ai_settings.qdrant_url)
    rows, hierarchical_digest = read_collection(client)
    before_legacy = collection_digest(client, ai_settings.qdrant_collection)
    excluded = {e["file_name"] for q in LABELS for e in q["evidence"]}
    old_queries = {q["query"] for q in LABELS}
    for name in ("retrieval_v2_heldout.json", "rag_v2_independent_validation.json"):
        fixture = json.loads((BACKEND / "tests/ai/fixtures" / name).read_text(encoding="utf-8"))
        excluded.update(e["file_name"] for q in fixture["labels"] for e in q.get("evidence", []))
        old_queries.update(q["query"] for q in fixture["labels"])
    assert all(q not in old_queries and (file is None or file not in excluded) for _, q, file in QUERIES)
    assert all(file is None or any(r["file_name"] == file for r in rows) for _, _, file in QUERIES)
    assert not any("ABCXYZ957359" in r["file_name"] for r in rows)
    path = BACKEND.parent / "docs/ai/rag_v2_endpoint_shadow.json"
    output = dict(run_utc=datetime.now(timezone.utc).isoformat(), feature_flag_enabled=False,
        protocol="direct service calls; no HTTP-visible switching or conversation persistence; no tuning",
        legacy_collection=ai_settings.qdrant_collection, hierarchical_collection="buildlearn_products_hierarchical_v1",
        collection_sha256=hierarchical_digest, legacy_integrity_before=before_legacy,
        adapter_sha256=adapter_hash, protected_hashes=before_files,
        legacy_model=ai_settings.ollama_model, v2_model="qwen2.5-coder:7b", records=[])
    if path.exists() and not args.restart:
        output = json.loads(path.read_text(encoding="utf-8"))
        if (output["protected_hashes"] != before_files or output["adapter_sha256"] != adapter_hash
                or output["collection_sha256"] != hierarchical_digest or output["legacy_integrity_before"] != before_legacy):
            raise RuntimeError("Cannot resume changed shadow implementation/data")
    legacy, v2 = RAGService(), RAGV2ChatAdapter()
    completed = {r["id"] for r in output["records"]}
    for qid, question, filename in [q for q in QUERIES if q[0] not in completed][:args.batch_size]:
        request = ChatRequest(question=question, conversation_id=str(uuid4()))
        record = dict(id=qid, query=question, expected_file=filename,
                      legacy=call(legacy, request), v2=call(v2, request))
        output["records"].append(record)
        path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(dict(id=qid, legacy=record["legacy"]["status"], v2=record["v2"]["status"])), flush=True)
    _, after_hierarchical = read_collection(client)
    after_legacy = collection_digest(client, ai_settings.qdrant_collection)
    if (before_files != protected() or after_hierarchical != hierarchical_digest
            or after_legacy != before_legacy or rag_v2_enabled()
            or hashlib.sha256((BACKEND / "app/ai/api/rag_v2_endpoint.py").read_bytes()).hexdigest() != adapter_hash):
        raise RuntimeError("Protected data or feature flag changed")
    output["integrity"] = dict(protected_files_unchanged=True, hierarchical_unchanged=True,
                               legacy_unchanged=True, flag_still_disabled=True)
    output["complete"] = len(output["records"]) == len(QUERIES)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    client.close()
    print("Shadow results: " + str(path), flush=True)


if __name__ == "__main__":
    main()
