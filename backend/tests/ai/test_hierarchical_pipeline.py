import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.ai.chunking.models import BlockType, ChildChunk, ChunkResult, ParentChunk, SourceInfo
from app.ai.embeddings.service import EmbeddingResult
from app.ai.indexing.hierarchical_pipeline import COLLECTION, HierarchicalPipeline, IndexConfig
from app.ai.indexing.hierarchical_pipeline import checkpoint_lock, digest
from app.ai.vectorstore.qdrant_provider import QdrantVectorStore, qdrant_models


@pytest.fixture
def pipeline(tmp_path):
    root = tmp_path / "data"
    root.mkdir()
    for i in range(3):
        (root / f"{i}.json").write_text(json.dumps({"document_id": str(i), "source_path": f"{i}.pdf",
                                                   "extraction_status": "success", "pages": []}))
    (root / "manifest.json").write_text("{}")
    def chunk(data):
        source = SourceInfo(document_id=data["document_id"], source_path=data["source_path"], file_name="test.pdf")
        parent = ParentChunk("parent", BlockType.HEADING, "Heading", source)
        children = [ChildChunk(f"{int(data['document_id'])*10+j+1:016x}", BlockType.PARAGRAPH,
                               f"Complete original text {j}", source, parent_id="parent",
                               section_path=["Heading"], page_start=1, page_end=2) for j in range(5)]
        return ChunkResult(parents=[parent], children=children)
    chunker = Mock()
    chunker.chunk_from_dict.side_effect = chunk
    embed = Mock(dimension=768)
    embed.embed_chunks.side_effect = lambda cs: [EmbeddingResult(c.chunk_id, [1.0]+[0.0]*767) for c in cs]
    points = {}
    store = Mock()
    store._collection = COLLECTION
    store._get_chunk_id = QdrantVectorStore._get_chunk_id
    store._get_child_point_id = QdrantVectorStore._get_child_point_id
    store._build_child_chunk_payload = QdrantVectorStore._build_child_chunk_payload
    store._client.get_collection.return_value = SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(
        vectors=qdrant_models.VectorParams(size=768, distance=qdrant_models.Distance.COSINE))))
    def upsert(cs, vectors):
        for c, v in zip(cs, vectors):
            points[store._get_child_point_id(c)] = SimpleNamespace(id=store._get_child_point_id(c), vector=v,
                                                           payload=store._build_child_chunk_payload(c))
    store.upsert_child_chunks.side_effect = upsert
    store._client.retrieve.side_effect = lambda collection, ids, **kw: [points[i] for i in ids if i in points]
    store._client.count.side_effect = lambda *a, **kw: SimpleNamespace(count=len(points))
    p = HierarchicalPipeline(root, tmp_path / "checkpoint.json", config=IndexConfig(4, 2, 3, 0),
                             chunker=chunker, embeddings=embed, store=store)
    p.points = points
    return p


def test_audit_discovery_and_complete_input(pipeline):
    audit = pipeline.audit(3, 15)
    assert audit["total_parents"] == 3
    assert [p.name for p in pipeline.discover()] == ["0.json", "1.json", "2.json"]
    assert pipeline.chunker.chunk_from_dict.call_args_list[0].args[0] == pipeline.load(pipeline.root / "0.json")


def test_batches_payload_checkpoint_and_resume(pipeline):
    report = pipeline.run()
    assert report["qdrant_points"] == report["indexed_chunks"] == 15
    assert [len(c.args[0]) for c in pipeline.embeddings.embed_chunks.call_args_list] == [4, 1]*3
    assert all(len(c.args[0]) <= 2 for c in pipeline.store.upsert_child_chunks.call_args_list)
    payload = next(iter(pipeline.points.values())).payload
    assert len(payload) == 10 and payload["section_path"] == ["Heading"] and payload["page_end"] == 2
    pipeline.embeddings.embed_chunks.reset_mock()
    pipeline.store.upsert_child_chunks.reset_mock()
    report = pipeline.run(resume=True)
    assert report["embedded"] == report["upserted"] == 0
    pipeline.embeddings.embed_chunks.assert_not_called()
    pipeline.store.upsert_child_chunks.assert_not_called()
    assert len(json.loads(pipeline.checkpoint.read_text())["state"]["successful_documents"]) == 3


def test_dry_run_then_full(pipeline):
    assert pipeline.run(limit_documents=1)["indexed_chunks"] == 5
    assert pipeline.run(resume=True)["upserted"] == 10


def test_reset_does_not_delete(pipeline):
    pipeline.run()
    assert pipeline.run(reset_checkpoint=True)["upserted"] == 15
    pipeline.store._client.delete_collection.assert_not_called()
    pipeline.store._client.delete.assert_not_called()


@pytest.mark.parametrize("bad", ["{", '{}', '{"state": {}, "sha256": "wrong"}'])
def test_corrupt_checkpoint(pipeline, bad):
    pipeline.checkpoint.write_text(bad)
    with pytest.raises(ValueError, match="Unsafe checkpoint"):
        pipeline.run(resume=True)
    pipeline.store.create_collection.assert_not_called()
    pipeline.store.upsert_child_chunks.assert_not_called()


def test_changed_dataset_rejects_resume(pipeline):
    pipeline.run()
    path = pipeline.root / "0.json"
    path.write_text(path.read_text()+" ")
    with pytest.raises(ValueError, match="mismatch"):
        pipeline.run(resume=True)


def test_embedding_failure_checkpoint_and_resume(pipeline):
    normal = pipeline.embeddings.embed_chunks.side_effect
    calls = 0
    def fail(cs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("embedding down")
        return normal(cs)
    pipeline.embeddings.embed_chunks.side_effect = fail
    with pytest.raises(RuntimeError, match="embedding down"):
        pipeline.run()
    state = json.loads(pipeline.checkpoint.read_text())["state"]
    assert len(state["successful_chunks"]) == 4
    assert state["successful_documents"] == []
    assert state["failures"][-1]["stage"] == "embedding"
    pipeline.embeddings.embed_chunks.side_effect = normal
    assert pipeline.run(resume=True)["upserted"] == 11


def test_retry_success(pipeline):
    normal = pipeline.store.upsert_child_chunks.side_effect
    calls = 0
    def flaky(cs, vectors):
        nonlocal calls
        calls += 1
        if calls < 3:
            raise RuntimeError("transient")
        normal(cs, vectors)
    pipeline.store.upsert_child_chunks.side_effect = flaky
    assert pipeline.run()["indexed_chunks"] == 15
    assert calls == 11


def test_exhausted_upsert_fail_stops(pipeline):
    pipeline.store.upsert_child_chunks.side_effect = RuntimeError("Qdrant down")
    with pytest.raises(RuntimeError, match="Qdrant down"):
        pipeline.run()
    assert pipeline.store.upsert_child_chunks.call_count == 3
    state = json.loads(pipeline.checkpoint.read_text())["state"]
    assert state["successful_chunks"] == [] and state["failures"][-1]["chunk_ids"]


@pytest.mark.parametrize("kind", ["order", "count", "dimension", "nan", "inf", "norm"])
def test_invalid_embeddings(pipeline, kind):
    children = pipeline.chunker.chunk_from_dict(pipeline.load(pipeline.root / "0.json")).children
    results = [EmbeddingResult(c.chunk_id, [1.0]+[0.0]*767) for c in children]
    if kind == "order":
        results.reverse()
    elif kind == "count":
        results.pop()
    elif kind == "dimension":
        results[0].vector.pop()
    elif kind in ("nan", "inf"):
        results[0].vector[0] = float(kind)
    else:
        results[0].vector[0] = 2.0
    with pytest.raises(ValueError):
        pipeline.validate_embeddings(children, results)


@pytest.mark.parametrize("kind", ["production", "dimension", "distance", "named"])
def test_collection_safety(pipeline, kind):
    if kind == "production":
        pipeline.store._collection = "buildlearn_products"
    else:
        vectors = qdrant_models.VectorParams(size=4 if kind == "dimension" else 768,
                                            distance=qdrant_models.Distance.DOT if kind == "distance" else qdrant_models.Distance.COSINE)
        pipeline.store._client.get_collection.return_value.config.params.vectors = {"named": vectors} if kind == "named" else vectors
    with pytest.raises(ValueError):
        pipeline.run()
    pipeline.store.upsert_child_chunks.assert_not_called()


def test_final_count_mismatch(pipeline):
    pipeline.store._client.count.return_value = SimpleNamespace(count=16)
    pipeline.store._client.count.side_effect = None
    with pytest.raises(ValueError, match="Final count mismatch"):
        pipeline.run()


def test_missing_remote_resume_fails(pipeline):
    pipeline.run()
    pipeline.points.clear()
    with pytest.raises(ValueError, match="Missing Qdrant"):
        pipeline.run(resume=True)


@pytest.mark.parametrize("kind", ["status", "duplicate", "parent", "empty", "baseline"])
def test_preflight_failures(pipeline, kind):
    if kind == "status":
        path = pipeline.root / "0.json"
        data = json.loads(path.read_text())
        data["extraction_status"] = "failed"
        path.write_text(json.dumps(data))
    elif kind != "baseline":
        normal = pipeline.chunker.chunk_from_dict.side_effect
        def bad(data):
            r = normal(data)
            if kind == "duplicate":
                r.children.append(r.children[0])
            elif kind == "parent":
                r.children[0].parent_id = "missing"
            else:
                r.children[0].text = " "
            return r
        pipeline.chunker.chunk_from_dict.side_effect = bad
    with pytest.raises(ValueError):
        pipeline.run(expected_children=16 if kind == "baseline" else None)
    pipeline.store.upsert_child_chunks.assert_not_called()


def test_payload_readback_failure(pipeline):
    normal = pipeline.store.upsert_child_chunks.side_effect
    def wrong(cs, vs):
        normal(cs, vs)
        pipeline.points[pipeline.store._get_child_point_id(cs[0])].payload["text"] = "changed"
    pipeline.store.upsert_child_chunks.side_effect = wrong
    with pytest.raises(ValueError, match="payload mismatch"):
        pipeline.run()
    assert json.loads(pipeline.checkpoint.read_text())["state"]["successful_chunks"] == []


def test_checkpoint_requires_explicit_action(pipeline):
    pipeline.run()
    with pytest.raises(ValueError, match="Checkpoint exists"):
        pipeline.run()


def test_collection_creation_real_provider_mocked_client(pipeline):
    store = object.__new__(QdrantVectorStore)
    store._collection = COLLECTION
    store._client = Mock()
    store._client.collection_exists.return_value = False
    store.create_collection(768)
    assert store._client.create_collection.call_args.kwargs["collection_name"] == COLLECTION
    store._client.delete_collection.assert_not_called()


def test_atomic_write_failure_keeps_previous_checkpoint(pipeline, monkeypatch):
    pipeline.run(limit_documents=1)
    original = pipeline.checkpoint.read_bytes()
    state = json.loads(original)["state"]
    def fail(*args):
        raise OSError("replace failed")
    monkeypatch.setattr("app.ai.indexing.hierarchical_pipeline.os.replace", fail)
    with pytest.raises(OSError, match="replace failed"):
        pipeline.save(state)
    assert pipeline.checkpoint.read_bytes() == original
    assert not list(pipeline.checkpoint.parent.glob("*.tmp"))


def test_concurrent_writer_rejected(pipeline):
    with checkpoint_lock(pipeline.checkpoint):
        with pytest.raises(OSError):
            pipeline.run()


def test_checkpoint_semantically_invalid_even_with_checksum(pipeline):
    pipeline.run(limit_documents=1)
    envelope = json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))
    envelope["state"]["successful_chunks"].append("ffffffffffffffff")
    envelope["sha256"] = digest(envelope["state"])
    pipeline.checkpoint.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="Invalid successful chunk"):
        pipeline.run(resume=True)


def test_upsert_write_then_response_failure_is_safely_replayed(pipeline):
    normal = pipeline.store.upsert_child_chunks.side_effect
    def ambiguous(cs, vs):
        normal(cs, vs)
        raise RuntimeError("response lost")
    pipeline.store.upsert_child_chunks.side_effect = ambiguous
    with pytest.raises(RuntimeError):
        pipeline.run()
    assert len(pipeline.points) == 2
    assert json.loads(pipeline.checkpoint.read_text())["state"]["successful_chunks"] == []
    pipeline.store.upsert_child_chunks.side_effect = normal
    assert pipeline.run(resume=True)["qdrant_points"] == 15


def test_collection_failure_is_checkpointed(pipeline):
    pipeline.store.create_collection.side_effect = RuntimeError("connection refused")
    with pytest.raises(RuntimeError):
        pipeline.run()
    state = json.loads(pipeline.checkpoint.read_text())["state"]
    assert state["failures"][-1]["stage"] == "collection_setup"
    assert state["successful_chunks"] == []


def test_numeric_point_collision_preflight(pipeline):
    normal = pipeline.chunker.chunk_from_dict.side_effect
    def collision(data):
        r = normal(data)
        r.children[1].chunk_id = "0" + r.children[0].chunk_id
        return r
    pipeline.chunker.chunk_from_dict.side_effect = collision
    with pytest.raises(ValueError, match="Duplicate child/point"):
        pipeline.run()


def test_suffixed_id_uses_deterministic_uuid_preserving_payload(pipeline):
    normal = pipeline.chunker.chunk_from_dict.side_effect
    def suffixed(data):
        r = normal(data)
        r.children[0].chunk_id = "ce32a740ed68a87c_1"
        # Only one document: preserve global uniqueness for this range check.
        return r
    pipeline.chunker.chunk_from_dict.side_effect = suffixed
    for name in ("1.json", "2.json"):
        (pipeline.root / name).unlink()
    assert pipeline.audit()["legacy_integer_overflows"][0]["bit_length"] == 68
    from uuid import UUID
    assert pipeline.run()["qdrant_points"] == 5
    child = suffixed(pipeline.load(pipeline.root / "0.json")).children[0]
    pid = pipeline.store._get_child_point_id(child)
    assert str(UUID(pid)) == pid
    assert pipeline.store._get_child_point_id(child) == pid
    assert pipeline.points[pid].payload["chunk_id"] == "ce32a740ed68a87c_1"
    assert QdrantVectorStore._get_chunk_id(child) == 237729952287223875521


def test_checkpoint_upgrade_preserves_existing_integer_points(pipeline):
    pipeline.run(limit_documents=1)
    envelope = json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))
    envelope["state"]["identity"].pop("point_id_mapping")
    envelope["sha256"] = digest(envelope["state"])
    pipeline.checkpoint.write_text(json.dumps(envelope), encoding="utf-8")
    assert pipeline.run(resume=True)["upserted"] == 10
    state = json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))["state"]
    assert state["identity"]["point_id_mapping"] == "uint64_or_uuid5_overflow_v1"


def test_checkpoint_upgrade_rejects_saved_overflow_keys(pipeline):
    pipeline.run(limit_documents=1)
    envelope = json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))
    envelope["state"]["identity"].pop("point_id_mapping")
    envelope["state"]["successful_chunks"].append("ce32a740ed68a87c_1")
    envelope["sha256"] = digest(envelope["state"])
    pipeline.checkpoint.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(ValueError, match="Cannot migrate checkpoint"):
        pipeline.run(resume=True)


def test_hierarchical_provider_overflow_upsert_keeps_original_schema(pipeline):
    child = pipeline.chunker.chunk_from_dict(pipeline.load(pipeline.root / "0.json")).children[0]
    child.chunk_id = "ce32a740ed68a87c_1"
    store = object.__new__(QdrantVectorStore)
    store._collection = COLLECTION
    store._client = Mock()
    store.upsert_child_chunks([child], [[1.0]+[0.0]*767])
    point = store._client.upsert.call_args.kwargs["points"][0]
    assert point.id == store._get_child_point_id(child)
    assert point.payload == store._build_child_chunk_payload(child)
    assert len(point.payload) == 10


def test_atomic_replace_retries_temporary_windows_sharing_violation(pipeline, monkeypatch):
    import os
    pipeline.run(limit_documents=1)
    state = json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))["state"]
    original_replace = os.replace
    calls = 0
    def transient(source, target):
        nonlocal calls
        calls += 1
        if calls < 3:
            raise PermissionError("sharing violation")
        original_replace(source, target)
    monkeypatch.setattr("app.ai.indexing.hierarchical_pipeline.os.replace", transient)
    pipeline.save(state)
    assert calls == 3
    assert json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))["sha256"] == digest(state)


def test_loopback_alias_resume_but_different_endpoint_rejected(pipeline):
    pipeline.run(limit_documents=1)
    envelope = json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))
    for key in ("qdrant_url", "ollama_url"):
        envelope["state"]["identity"][key] = envelope["state"]["identity"][key].replace("127.0.0.1", "localhost")
    envelope["sha256"] = digest(envelope["state"])
    pipeline.checkpoint.write_text(json.dumps(envelope), encoding="utf-8")
    assert pipeline.run(resume=True)["qdrant_points"] == 15
    envelope = json.loads(pipeline.checkpoint.read_text(encoding="utf-8"))
    envelope["state"]["identity"]["qdrant_url"] = "http://remote.example:6333"
    envelope["sha256"] = digest(envelope["state"])
    pipeline.checkpoint.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(ValueError, match="mismatch"):
        pipeline.run(resume=True)
