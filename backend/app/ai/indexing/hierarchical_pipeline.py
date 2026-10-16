"""Incremental hierarchical indexing. Never deletes points or collections."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import time
from urllib.parse import urlsplit

from app.ai.chunking.chunker import HierarchicalChunker
from app.ai.chunking.config import ChunkConfig
from app.ai.config import ai_settings
from app.ai.embeddings.service import EmbeddingService
from app.ai.vectorstore.qdrant_provider import QdrantVectorStore, qdrant_models

COLLECTION = "buildlearn_products_hierarchical_v1"
BACKEND = Path(__file__).resolve().parents[3]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical_endpoint(url):
    """Treat the local hostname and its IPv4 loopback address as one endpoint."""
    parsed = urlsplit(url)
    if parsed.hostname == "localhost" and parsed.username is None and parsed.password is None:
        address = "127.0.0.1" + (f":{parsed.port}" if parsed.port is not None else "")
        return parsed._replace(netloc=address).geturl()
    return url


@dataclass(frozen=True)
class IndexConfig:
    embedding_batch_size: int = 10
    upsert_batch_size: int = 10
    upsert_attempts: int = 3
    retry_delay: float = 1.0

    def __post_init__(self):
        if min(self.embedding_batch_size, self.upsert_batch_size, self.upsert_attempts) < 1:
            raise ValueError("Batch sizes and attempts must be positive")
        if not math.isfinite(self.retry_delay) or self.retry_delay < 0:
            raise ValueError("Retry delay must be finite and nonnegative")


@contextmanager
def checkpoint_lock(path):
    """OS lock releases on process death; lock file is intentionally retained."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(path.suffix + ".lock").open("a+b") as handle:
        handle.seek(0)
        handle.write(b"0")
        handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


class HierarchicalPipeline:
    def __init__(self, extraction_root=BACKEND / "ai_data/reports/full_extraction",
                 checkpoint=BACKEND / "ai_data/indexing/hierarchical_index_checkpoint.json",
                 *, config=None, chunker=None, embeddings=None, store=None):
        self.root, self.checkpoint = Path(extraction_root), Path(checkpoint)
        self.config = config or IndexConfig()
        self.chunker = chunker or HierarchicalChunker(ChunkConfig())
        self.embeddings, self.store = embeddings, store

    def discover(self):
        files = sorted(p for p in self.root.glob("*.json") if p.name != "manifest.json")
        if not files:
            raise ValueError(f"No extraction documents in {self.root}")
        return files

    def load(self, path):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("extraction_status") != "success":
            raise ValueError(f"Invalid extraction status: {path}")
        if not data.get("document_id") or not data.get("source_path"):
            raise ValueError(f"Missing source identity: {path}")
        return data

    def audit(self, expected_documents=None, expected_children=None):
        files = self.discover()
        inventory, chunks, point_ids = [], {}, set()
        incompatible_ids = []
        parents = root_children = 0
        for path in files:
            data = self.load(path)
            result = self.chunker.chunk_from_dict(data)
            parent_ids = {p.chunk_id for p in result.parents}
            parents += len(result.parents)
            ids = []
            for child in result.children:
                cid = child.chunk_id
                legacy_pid = QdrantVectorStore._get_chunk_id(child)
                pid = QdrantVectorStore._get_child_point_id(child)
                if not 0 <= legacy_pid <= (1 << 64) - 1:
                    incompatible_ids.append({"file": path.name, "chunk_id": cid, "point_id": pid,
                                             "legacy_point_id": legacy_pid,
                                             "bit_length": legacy_pid.bit_length()})
                if cid in chunks or pid in point_ids:
                    raise ValueError(f"Duplicate child/point ID: {cid} ({path})")
                if (child.parent_id is not None and child.parent_id not in parent_ids) or not child.text.strip():
                    raise ValueError(f"Invalid child text or parent: {cid}")
                root_children += child.parent_id is None
                payload = QdrantVectorStore._build_child_chunk_payload(child)
                chunks[cid] = digest(payload)
                point_ids.add(pid)
                ids.append(cid)
            inventory.append({"file": path.name, "hash": hashlib.sha256(path.read_bytes()).hexdigest(),
                              "document_id": data["document_id"], "chunk_ids": ids})
        if expected_documents is not None and len(files) != expected_documents:
            raise ValueError(f"Document baseline mismatch: {len(files)} != {expected_documents}")
        if expected_children is not None and len(chunks) != expected_children:
            raise ValueError(f"Child baseline mismatch: {len(chunks)} != {expected_children}")
        return {"dataset_id": digest(inventory), "documents": inventory, "chunks": chunks,
                "total_documents": len(files), "total_children": len(chunks), "total_parents": parents,
                "root_children_without_parent": root_children,
                "legacy_integer_overflows": incompatible_ids}

    def save(self, state):
        state["timestamp"] = now()
        state["statistics"] = {"indexed_chunks": len(state["successful_chunks"]),
                               "completed_documents": len(state["successful_documents"]),
                               "failure_events": len(state["failures"])}
        envelope = {"state": state, "sha256": digest(state)}
        fd, name = tempfile.mkstemp(dir=self.checkpoint.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(envelope, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            # Windows readers/antivirus can briefly deny replacement. Retry
            # the same durable temporary file; never truncate the old file.
            for attempt in range(1, 6):
                try:
                    os.replace(name, self.checkpoint)
                    break
                except PermissionError:
                    if attempt == 5:
                        raise
                    time.sleep(0.05 * attempt)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def read_checkpoint(self, identity, audit):
        try:
            envelope = json.loads(self.checkpoint.read_text(encoding="utf-8"))
            state = envelope["state"]
            if digest(state) != envelope["sha256"]:
                raise ValueError("Checksum mismatch")
            stored_identity = dict(state["identity"])
            for key in ("qdrant_url", "ollama_url"):
                stored_identity[key] = canonical_endpoint(stored_identity[key])
            # Upgrade the pre-overflow checkpoint only when every successful
            # key retains its exact old integer mapping and all other identity
            # fields match. No re-embedding or remote migration is needed.
            old_identity = dict(identity)
            old_identity.pop("point_id_mapping", None)
            if stored_identity == old_identity:
                if any(not 0 <= int(cid, 16) <= (1 << 64)-1 for cid in state["successful_chunks"]):
                    raise ValueError("Cannot migrate checkpoint with overflow point keys")
                stored_identity = identity
            if stored_identity != identity:
                raise ValueError("Checksum or dataset/configuration mismatch")
            state["identity"] = identity
            if state["dataset_manifest"] != audit["documents"]:
                raise ValueError("Dataset manifest mismatch")
            ids = state["successful_chunks"]
            if not isinstance(ids, list) or len(set(ids)) != len(ids) or not set(ids) <= set(audit["chunks"]):
                raise ValueError("Invalid successful chunk inventory")
            docs = state["successful_documents"]
            if not isinstance(docs, list) or len(set(docs)) != len(docs):
                raise ValueError("Invalid successful document inventory")
            by_file = {d["file"]: d for d in audit["documents"]}
            if any(f not in by_file or not set(by_file[f]["chunk_ids"]) <= set(ids) for f in docs):
                raise ValueError("Incomplete successful document")
            if not isinstance(state["failures"], list):
                raise ValueError("Invalid failures")
            return state
        except Exception as exc:
            raise ValueError(f"Unsafe checkpoint; use intentional --reset-checkpoint: {exc}") from exc

    def ensure_collection(self):
        if self.store._collection != COLLECTION:
            raise ValueError(f"Only {COLLECTION} is authorized")
        self.store.create_collection(768)
        vectors = self.store._client.get_collection(COLLECTION).config.params.vectors
        if not isinstance(vectors, qdrant_models.VectorParams) or vectors.size != 768 or vectors.distance != qdrant_models.Distance.COSINE:
            raise ValueError("Collection requires unnamed 768-dimensional COSINE vectors")

    @staticmethod
    def validate_embeddings(children, results):
        if [r.chunk_id for r in results] != [c.chunk_id for c in children]:
            raise ValueError("Embedding count/ID/order mismatch")
        for result in results:
            vector = result.vector
            if len(vector) != 768 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in vector):
                raise ValueError("Invalid embedding dimension or nonfinite values")
            if not math.isclose(math.sqrt(sum(v*v for v in vector)), 1.0, abs_tol=1e-5):
                raise ValueError("Embedding is not L2 normalized")

    def verify(self, children):
        records = self.store._client.retrieve(COLLECTION, ids=[self.store._get_child_point_id(c) for c in children],
                                               with_payload=True, with_vectors=True)
        by_id = {r.id: r for r in records}
        if len(by_id) != len(children):
            raise ValueError("Missing Qdrant points")
        for child in children:
            record = by_id[self.store._get_child_point_id(child)]
            if record.payload != self.store._build_child_chunk_payload(child):
                raise ValueError(f"Qdrant payload mismatch: {child.chunk_id}")
            vector = record.vector
            if not isinstance(vector, list) or len(vector) != 768 or not all(math.isfinite(v) for v in vector):
                raise ValueError("Invalid stored vector")
            if not math.isclose(math.sqrt(sum(v*v for v in vector)), 1.0, abs_tol=1e-5):
                raise ValueError("Stored vector is not normalized")

    def run(self, *, resume=False, reset_checkpoint=False, limit_documents=None,
            expected_documents=None, expected_children=None):
        if resume and reset_checkpoint:
            raise ValueError("Resume and reset are mutually exclusive")
        if limit_documents is not None and limit_documents < 1:
            raise ValueError("Document limit must be positive")
        with checkpoint_lock(self.checkpoint):
            return self._run(resume, reset_checkpoint, limit_documents, expected_documents, expected_children)

    def _run(self, resume, reset, limit, expected_documents, expected_children):
        started = time.monotonic()
        audit = self.audit(expected_documents, expected_children)
        if self.embeddings is None:
            if ai_settings.embedding_provider != "ollama" or ai_settings.embedding_model != "nomic-embed-text" or not ai_settings.embedding_normalize:
                raise ValueError("Requires configured Ollama/nomic-embed-text with normalization")
            self.embeddings = EmbeddingService()
        if self.embeddings.dimension != 768:
            raise ValueError("Embedding dimension must be 768")
        self.store = self.store or QdrantVectorStore(collection_name=COLLECTION)
        identity = {"version": 1, "dataset_id": audit["dataset_id"], "collection": COLLECTION,
                    "point_id_mapping": "uint64_or_uuid5_overflow_v1",
                    "dimension": 768, "distance": "Cosine", "model": "nomic-embed-text",
                    "normalize": True, "config": asdict(self.config), "chunk_config": asdict(ChunkConfig()),
                    "qdrant_url": canonical_endpoint(ai_settings.qdrant_url),
                    "ollama_url": canonical_endpoint(ai_settings.ollama_base_url),
                    "implementation": digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for folder in ("chunking", "embeddings")
                        for p in sorted((BACKEND / "app/ai" / folder).glob("*.py"))})}
        # JSON round-trip canonicalizes tuple-valued ChunkConfig fields.
        identity = json.loads(json.dumps(identity))
        if self.checkpoint.exists() and not reset:
            if not resume:
                raise ValueError("Checkpoint exists: specify --resume or --reset-checkpoint")
            state = self.read_checkpoint(identity, audit)
        elif resume:
            raise ValueError("No checkpoint to resume")
        else:
            state = {"identity": identity, "dataset_manifest": audit["documents"],
                     "successful_chunks": [], "successful_documents": [], "failures": []}
        self.save(state)
        successful = set(state["successful_chunks"])
        embedded = upserted = processed = 0
        selected = audit["documents"][:limit] if limit else audit["documents"]
        stage, batch_ids, current = "collection_setup", [], None
        try:
            self.ensure_collection()
            for current in selected:
                stage, batch_ids = "chunking", []
                path = self.root / current["file"]
                if hashlib.sha256(path.read_bytes()).hexdigest() != current["hash"]:
                    raise ValueError("Dataset changed during indexing")
                result = self.chunker.chunk_from_dict(self.load(path))
                children = result.children
                if [c.chunk_id for c in children] != current["chunk_ids"] or any(
                    digest(self.store._build_child_chunk_payload(c)) != audit["chunks"][c.chunk_id] for c in children):
                    raise ValueError("Chunk output changed since audit")
                stage = "resume_verification"
                saved = [c for c in children if c.chunk_id in successful]
                for i in range(0, len(saved), self.config.upsert_batch_size):
                    self.verify(saved[i:i+self.config.upsert_batch_size])
                pending = [c for c in children if c.chunk_id not in successful]
                for i in range(0, len(pending), self.config.embedding_batch_size):
                    batch = pending[i:i+self.config.embedding_batch_size]
                    batch_ids = [c.chunk_id for c in batch]
                    stage = "embedding"
                    results = self.embeddings.embed_chunks(batch)
                    self.validate_embeddings(batch, results)
                    embedded += len(batch)
                    for j in range(0, len(batch), self.config.upsert_batch_size):
                        part = batch[j:j+self.config.upsert_batch_size]
                        vectors = [r.vector for r in results[j:j+self.config.upsert_batch_size]]
                        batch_ids = [c.chunk_id for c in part]
                        stage = "upsert"
                        for attempt in range(1, self.config.upsert_attempts+1):
                            try:
                                self.store.upsert_child_chunks(part, vectors)
                                self.verify(part)
                                break
                            except Exception:
                                if attempt == self.config.upsert_attempts:
                                    raise
                                time.sleep(self.config.retry_delay * attempt)
                        successful.update(batch_ids)
                        state["successful_chunks"] = sorted(successful)
                        stage = "checkpoint"
                        self.save(state)
                        upserted += len(part)
                if current["file"] not in state["successful_documents"]:
                    state["successful_documents"].append(current["file"])
                self.save(state)
                processed += 1
                print(f"Documents: {processed}/{len(selected)} Children: {len(successful)}/{audit['total_children']} "
                      f"Embedded: {embedded} Upserted: {upserted} Failures: 0 Elapsed: {time.monotonic()-started:.1f}s", flush=True)
            stage, batch_ids = "final_validation", []
            count = self.store._client.count(COLLECTION, exact=True).count
            if limit is None and (count != len(successful) or len(successful) != audit["total_children"]):
                raise ValueError(f"Final count mismatch: Qdrant={count}, checkpoint={len(successful)}, dataset={audit['total_children']}")
            if limit is not None and count < len(successful):
                raise ValueError("Collection count below checkpoint count")
            report = {k: audit[k] for k in ("dataset_id", "total_documents", "total_children", "total_parents", "root_children_without_parent")}
            report.update(documents_processed=processed, indexed_chunks=len(successful), embedded=embedded,
                          upserted=upserted, qdrant_points=count, collection=COLLECTION, dimension=768,
                          distance="COSINE", payload_validation="passed", failed_chunks=0,
                          elapsed_seconds=round(time.monotonic()-started, 2), timestamp=now())
            state["last_run"] = report
            self.save(state)
            return report
        except Exception as exc:
            state["failures"].append({"timestamp": now(), "document": current, "stage": stage,
                                      "chunk_ids": batch_ids, "error": str(exc),
                                      "run_embedded": embedded, "run_upserted": upserted,
                                      "run_documents_processed": processed})
            self.save(state)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit-documents", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reset-checkpoint", action="store_true")
    parser.add_argument("--expected-documents", type=int)
    parser.add_argument("--expected-children", type=int)
    parser.add_argument("--embedding-batch-size", type=int, default=10)
    parser.add_argument("--upsert-batch-size", type=int, default=10)
    parser.add_argument("--upsert-attempts", type=int, default=3)
    parser.add_argument("--retry-delay", type=float, default=1.0)
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--report", type=Path, help="Write verified run statistics as JSON")
    args = parser.parse_args()
    pipeline = HierarchicalPipeline(config=IndexConfig(args.embedding_batch_size, args.upsert_batch_size,
                                                     args.upsert_attempts, args.retry_delay))
    if args.audit_only:
        report = pipeline.audit(args.expected_documents, args.expected_children)
        report = {k: v for k, v in report.items() if k not in ("documents", "chunks")}
    else:
        report = pipeline.run(resume=args.resume, reset_checkpoint=args.reset_checkpoint,
                              limit_documents=args.limit_documents, expected_documents=args.expected_documents,
                              expected_children=args.expected_children)
    print(json.dumps(report, indent=2), flush=True)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
