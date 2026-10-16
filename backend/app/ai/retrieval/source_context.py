"""Read-only, verified parent evidence from the indexed extraction artifacts."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from app.ai.chunking.chunker import HierarchicalChunker
from app.ai.chunking.config import ChunkConfig
from app.ai.retrieval.hierarchical_models import ParentEvidence, RetrievedChild, SourceResolution

BACKEND = Path(__file__).resolve().parents[3]


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class ExtractionContextResolver:
    """Resolve only parents of selected hits; never queries Qdrant siblings.

    No persistent cache: source hashes/configuration are rechecked per request.
    Unavailable or changed evidence raises; the retriever keeps the search hits
    and exposes a warning rather than inventing context.
    """

    def __init__(self, extraction_root=BACKEND / "ai_data/reports/full_extraction",
                 checkpoint_path=BACKEND / "ai_data/indexing/hierarchical_index_checkpoint.json"):
        self.root = Path(extraction_root)
        self.checkpoint = Path(checkpoint_path)

    def resolve(self, hits: list[RetrievedChild]) -> dict[tuple[str, str, str], SourceResolution]:
        envelope = json.loads(self.checkpoint.read_text(encoding="utf-8"))
        state = envelope["state"]
        if envelope["sha256"] != _digest(state):
            raise ValueError("Source checkpoint checksum mismatch")
        identity = state["identity"]
        if identity["collection"] != "buildlearn_products_hierarchical_v1":
            raise ValueError("Source checkpoint targets another collection")
        config = ChunkConfig()
        if identity["chunk_config"] != json.loads(json.dumps(asdict(config))):
            raise ValueError("Source chunking configuration changed")
        implementation = _digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("chunking", "embeddings")
            for p in sorted((BACKEND / "app/ai" / folder).glob("*.py"))})
        if identity["implementation"] != implementation:
            raise ValueError("Source chunking/embedding implementation changed")
        successful = set(state["successful_chunks"])
        entries = state["dataset_manifest"]
        if identity["dataset_id"] != _digest(entries):
            raise ValueError("Source dataset identity mismatch")
        grouped: dict[tuple[str, str], list[RetrievedChild]] = {}
        for hit in hits:
            grouped.setdefault((hit.document_id, hit.source_path), []).append(hit)
        resolutions = {}
        for (document_id, source_path), selected in grouped.items():
            matched = None
            for entry in entries:
                if entry["document_id"] != document_id:
                    continue
                filename = entry["file"]
                if Path(filename).name != filename or not filename.endswith(".json") or filename == "manifest.json":
                    raise ValueError("Unsafe extraction filename in checkpoint")
                content = (self.root / filename).read_bytes()
                if hashlib.sha256(content).hexdigest() != entry["hash"]:
                    raise ValueError(f"Extraction changed: {filename}")
                data = json.loads(content)
                if data.get("document_id") == document_id and data.get("source_path") == source_path:
                    if matched is not None:
                        raise ValueError("Ambiguous extraction source identity")
                    if data.get("extraction_status") != "success":
                        raise ValueError("Source extraction is not successful")
                    matched = (data, entry)
            if matched is None:
                raise ValueError(f"Extraction source unavailable: {source_path}")
            data, entry = matched
            result = HierarchicalChunker(config).chunk_from_dict(data)
            children = {c.chunk_id: c for c in result.children}
            parents = {p.chunk_id: p for p in result.parents}
            if [c.chunk_id for c in result.children] != entry["chunk_ids"]:
                raise ValueError("Source child inventory changed")
            for hit in selected:
                if hit.chunk_id not in successful or hit.chunk_id not in children:
                    raise ValueError("Hit absent from indexed source inventory")
                child = children[hit.chunk_id]
                actual = {"chunk_id": child.chunk_id, "document_id": child.source.document_id,
                          "source_path": child.source.source_path, "file_name": child.source.file_name,
                          "parent_id": child.parent_id, "section_path": child.section_path,
                          "page_start": child.page_start, "page_end": child.page_end,
                          "block_type": child.block_type.value, "text": child.text}
                if any(hit.payload_metadata[k] != v for k, v in actual.items()):
                    raise ValueError("Indexed child payload does not match source")
                if hit.parent_id_path is not None and hit.parent_id_path != child.parent_id_path:
                    raise ValueError("Indexed ancestor path does not match source")
                path = list(child.parent_id_path)
                requested = list(dict.fromkeys(path + ([child.parent_id] if child.parent_id else [])))
                evidence = []
                for pid in requested:
                    if pid not in parents:
                        raise ValueError("Parent absent from verified source")
                    parent = parents[pid]
                    evidence.append(ParentEvidence(pid, parent.text, parent.source.document_id,
                        parent.source.file_name, parent.source.source_path, list(parent.section_path),
                        parent.page_start, parent.page_end, parent.chunk_type.value))
                resolutions[(document_id, source_path, hit.chunk_id)] = SourceResolution(path, evidence)
        return resolutions
