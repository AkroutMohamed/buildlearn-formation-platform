"""Read-only verification of the indexed checkpoint subset and production content."""
import hashlib
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("QDRANT_URL", "http://127.0.0.1:6333")

from app.ai.indexing.hierarchical_pipeline import COLLECTION, HierarchicalPipeline
from app.ai.vectorstore.qdrant_provider import QdrantVectorStore, qdrant_models


def main():
    pipeline = HierarchicalPipeline(store=QdrantVectorStore(collection_name=COLLECTION))
    audit = pipeline.audit(221, 2637)
    envelope = json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))
    state = pipeline.read_checkpoint(envelope["state"]["identity"], audit)
    if state["identity"]["dataset_id"] != audit["dataset_id"]:
        raise ValueError("Dataset identity mismatch")
    client = pipeline.store._client
    params = client.get_collection(COLLECTION).config.params.vectors
    if not isinstance(params, qdrant_models.VectorParams) or params.size != 768 or params.distance != qdrant_models.Distance.COSINE:
        raise ValueError("Invalid collection vector configuration")
    successful = set(state["successful_chunks"])
    verified = 0
    for entry in audit["documents"]:
        if not successful.intersection(entry["chunk_ids"]):
            continue
        result = pipeline.chunker.chunk_from_dict(pipeline.load(pipeline.root / entry["file"]))
        children = [c for c in result.children if c.chunk_id in successful]
        for i in range(0, len(children), 10):
            pipeline.verify(children[i:i+10])
            verified += len(children[i:i+10])
    count = client.count(COLLECTION, exact=True).count
    if count != verified or verified != len(successful):
        raise ValueError("Indexed subset count mismatch")
    hashes, offset = [], None
    while True:
        records, offset = client.scroll("buildlearn_products", limit=100, offset=offset,
                                        with_payload=True, with_vectors=True)
        hashes.extend(hashlib.sha256(r.model_dump_json().encode()).hexdigest() for r in records)
        if offset is None:
            break
    production = {"points": len(hashes), "records_sha256": hashlib.sha256(json.dumps(sorted(hashes)).encode()).hexdigest()}
    before_path = pipeline.checkpoint.parent / "production_content_before.json"
    if not before_path.exists() or production != json.loads(before_path.read_text(encoding="utf-8")):
        raise ValueError("Production baseline missing or content changed")
    report = {"collection": COLLECTION, "qdrant_points": count, "verified_payloads_and_vectors": verified,
              "dimension": 768, "distance": "COSINE", "checkpoint_validation": "passed",
              "production_content_unchanged": True, "production": production,
              "fully_indexed_documents": len(state["successful_documents"]),
              "remaining_children": audit["total_children"]-verified,
              "uuid_overflow_point_ids": len(audit["legacy_integer_overflows"]),
              "failure_events": len(state["failures"]), "full_run_complete": verified == audit["total_children"]}
    path = pipeline.checkpoint.parent / "final_validation.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
