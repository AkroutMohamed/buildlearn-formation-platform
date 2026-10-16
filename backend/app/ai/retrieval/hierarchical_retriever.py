"""Read-only hierarchical retrieval. No LLM, indexing, or API integration."""
from copy import deepcopy
from dataclasses import dataclass
import json
import math

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.ai.chunking.models import BlockType
from app.ai.config import ai_settings
from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.ai.embeddings.service import EmbeddingService
from app.ai.retrieval.hierarchical_models import (
    ContextFragment, RetrievalResponse, RetrievedChild, RetrievedContext,
)
from app.ai.retrieval.source_context import ExtractionContextResolver

COLLECTION = "buildlearn_products_hierarchical_v1"
FIELDS = ("chunk_id", "document_id", "file_name", "source_path", "parent_id", "section_path",
          "page_start", "page_end", "block_type", "text")


def _top_k(value):
    if type(value) is not int or value < 1:
        raise ValueError("top_k must be a positive integer")


def _threshold(value):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not -1 <= value <= 1:
        raise ValueError("similarity_threshold must be finite and between -1 and 1")


@dataclass(frozen=True)
class HierarchicalRetrievalConfig:
    top_k: int = 5
    similarity_threshold: float = 0.3
    expand_parents: bool = True
    max_parent_chars: int = 6000

    def __post_init__(self):
        _top_k(self.top_k)
        _threshold(self.similarity_threshold)
        if type(self.expand_parents) is not bool:
            raise ValueError("expand_parents must be boolean")
        if type(self.max_parent_chars) is not int or self.max_parent_chars < 0:
            raise ValueError("max_parent_chars must be a nonnegative integer")


class HierarchicalRetriever:
    def __init__(self, *, config=None, embeddings=None, client=None, context_resolver=None):
        self.config = config or HierarchicalRetrievalConfig()
        self._embeddings = embeddings
        self._client = client
        self._resolver = context_resolver if context_resolver is not None else ExtractionContextResolver()

    def _embedding_service(self):
        if self._embeddings is None:
            if ai_settings.embedding_provider not in ("", "ollama") or ai_settings.embedding_model not in ("", "nomic-embed-text") or not ai_settings.embedding_normalize:
                raise ValueError("Hierarchical retrieval requires normalized Ollama/nomic-embed-text")
            self._embeddings = EmbeddingService(provider=OllamaEmbeddingProvider(
                base_url=ai_settings.ollama_base_url, model="nomic-embed-text", normalize=True))
        return self._embeddings

    @staticmethod
    def _hit(point):
        payload = deepcopy(point.payload)
        if not isinstance(payload, dict) or any(k not in payload for k in FIELDS):
            raise ValueError("Incomplete hierarchical payload")
        for k in ("chunk_id", "document_id", "file_name", "source_path", "block_type", "text"):
            if not isinstance(payload[k], str) or not payload[k].strip():
                raise ValueError(f"Invalid hierarchical payload field: {k}")
        if payload["block_type"] not in {t.value for t in BlockType}:
            raise ValueError("Unknown block_type")
        if payload["parent_id"] is not None and (not isinstance(payload["parent_id"], str) or not payload["parent_id"]):
            raise ValueError("Invalid parent_id")
        for k in ("section_path", "parent_id_path"):
            if k not in payload:
                continue
            if not isinstance(payload[k], list) or not all(isinstance(v, str) for v in payload[k]):
                raise ValueError(f"Invalid {k}")
        for k in ("page_start", "page_end"):
            if payload[k] is not None and (type(payload[k]) is not int or payload[k] < 1):
                raise ValueError(f"Invalid {k}")
        if payload["page_start"] is not None and payload["page_end"] is not None and payload["page_end"] < payload["page_start"]:
            raise ValueError("Invalid page range")
        score = point.score
        if isinstance(score, bool) or not isinstance(score, (float, int)) or not math.isfinite(score):
            raise ValueError("Invalid similarity score")
        return RetrievedChild(score=float(score), **{k: payload[k] for k in FIELDS},
            parent_id_path=deepcopy(payload.get("parent_id_path")),
            parent_id_path_source="payload" if "parent_id_path" in payload else "unavailable",
            payload_metadata=payload)

    def retrieve(self, query: str, *, top_k=None, similarity_threshold=None) -> RetrievalResponse:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must not be empty or whitespace")
        k = self.config.top_k if top_k is None else top_k
        threshold = self.config.similarity_threshold if similarity_threshold is None else similarity_threshold
        _top_k(k)
        _threshold(threshold)
        client = self._client
        if client is None:
            client = self._client = QdrantClient(url=ai_settings.qdrant_url or "http://localhost:6333")
        # Read only: never create, repair, upsert, or delete a collection.
        params = client.get_collection(COLLECTION).config.params.vectors
        if not isinstance(params, models.VectorParams) or params.size != 768 or params.distance != models.Distance.COSINE:
            raise ValueError("Hierarchical collection requires unnamed 768-dimensional COSINE vectors")
        embeddings = self._embedding_service()
        if embeddings.dimension != 768:
            raise ValueError("Query embedding dimension must be 768")
        vector = embeddings.embed_single(query)
        if len(vector) != 768 or not all(type(v) in (float, int) and math.isfinite(v) for v in vector):
            raise ValueError("Invalid query embedding")
        if not math.isclose(math.sqrt(sum(v*v for v in vector)), 1.0, abs_tol=1e-5):
            raise ValueError("Query embedding must be L2 normalized")
        response = client.query_points(collection_name=COLLECTION, query=vector, limit=k,
            score_threshold=threshold, with_payload=True, with_vectors=False)
        hits = [self._hit(point) for point in response.points]
        hits.sort(key=lambda h: (-h.score, h.document_id, h.source_path, h.chunk_id))
        unique = {}
        for hit in hits:
            if hit.score < threshold:
                continue
            key = (hit.document_id, hit.source_path, hit.chunk_id)
            if key in unique:
                if unique[key].payload_metadata != hit.payload_metadata:
                    raise ValueError("Conflicting payloads for the same source chunk")
                continue
            unique[key] = hit
        hits = list(unique.values())[:k]
        warnings, resolved = [], {}
        if hits and self.config.expand_parents:
            try:
                resolved = self._resolver.resolve(hits)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                warnings.append(f"Parent context unavailable: {exc}")
        for hit in hits:
            evidence = resolved.get((hit.document_id, hit.source_path, hit.chunk_id))
            if evidence is not None and hit.parent_id_path is None:
                hit.parent_id_path = list(evidence.parent_id_path)
                hit.parent_id_path_source = "verified_source_child"
        contexts = self._contexts(hits, resolved, warnings)
        rendered = []
        for context in contexts:
            header = {"document_id": context.document_id, "file_name": context.file_name,
                      "source_path": context.source_path, "parent_id": context.parent_id,
                      "parent_id_path": context.parent_id_path, "section_path": context.section_path,
                      "page_start": context.page_start, "page_end": context.page_end,
                      "chunk_ids": context.chunk_ids}
            texts = list(dict.fromkeys([p.text for p in context.parents] + [f.text for f in context.fragments]))
            rendered.append(json.dumps(header, ensure_ascii=False) + "\n" + "\n\n".join(texts))
        return RetrievalResponse(hits, contexts, "\n\n".join(rendered), list(dict.fromkeys(warnings)))

    def _contexts(self, hits, resolved, warnings):
        groups = {}
        for hit in hits:
            root_location = None
            if hit.parent_id is None:
                root_location = (hit.page_start, hit.page_end) if hit.page_start is not None or hit.page_end is not None else hit.chunk_id
            key = (hit.document_id, hit.source_path, hit.file_name, hit.parent_id,
                   tuple(hit.section_path), None if hit.parent_id_path is None else tuple(hit.parent_id_path), root_location)
            groups.setdefault(key, []).append(hit)
        contexts = []
        for selected in groups.values():
            first = selected[0]
            fragments, parents = {}, {}
            parent_chars = 0
            for hit in sorted(selected, key=lambda h: (h.page_start or 0, h.page_end or 0, h.chunk_id)):
                # Identical text at another location/source remains distinct.
                key = (hit.text, hit.page_start, hit.page_end, hit.block_type)
                if key in fragments:
                    fragments[key].chunk_ids.append(hit.chunk_id)
                else:
                    fragments[key] = ContextFragment(hit.text, [hit.chunk_id], hit.page_start, hit.page_end, hit.block_type)
                evidence = resolved.get((hit.document_id, hit.source_path, hit.chunk_id))
                if evidence is None:
                    continue
                allowed = set(hit.parent_id_path or []) | ({hit.parent_id} if hit.parent_id else set())
                for parent in evidence.parents:
                    if parent.parent_id not in allowed or parent.document_id != hit.document_id or parent.source_path != hit.source_path or parent.file_name != hit.file_name:
                        raise ValueError("Parent evidence does not belong to retrieved source/hierarchy")
                    if parent.parent_id in parents:
                        if parent != parents[parent.parent_id]:
                            raise ValueError("Conflicting parent evidence")
                        continue
                    if parent_chars + len(parent.text) > self.config.max_parent_chars:
                        warnings.append(f"Parent context omitted by character budget: {parent.parent_id}")
                        continue
                    parents[parent.parent_id] = deepcopy(parent)
                    parent_chars += len(parent.text)
            starts = [h.page_start for h in selected if h.page_start is not None]
            ends = [h.page_end for h in selected if h.page_end is not None]
            contexts.append(RetrievedContext(first.document_id, first.file_name, first.source_path,
                first.parent_id, deepcopy(first.parent_id_path), list(first.section_path),
                min(starts) if starts else None, max(ends) if ends else None,
                [h.chunk_id for h in selected], list(fragments.values()), list(parents.values())))
        return contexts
