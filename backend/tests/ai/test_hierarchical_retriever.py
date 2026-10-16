from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from qdrant_client.http import models

from app.ai.chunking.chunker import HierarchicalChunker
from app.ai.chunking.config import ChunkConfig
from app.ai.retrieval.hierarchical_models import ParentEvidence, SourceResolution
from app.ai.retrieval.hierarchical_retriever import (
    COLLECTION, HierarchicalRetriever, HierarchicalRetrievalConfig,
)
from app.ai.retrieval.source_context import BACKEND, ExtractionContextResolver, _digest


def payload(cid="c1", **changes):
    result = dict(chunk_id=cid, document_id="doc-1", file_name="one.pdf", source_path="raw/one.pdf",
                  parent_id="p1", section_path=["SPECIFICATIONS"], page_start=1, page_end=2,
                  block_type="paragraph", text="  Original text.\nSecond line.  ")
    result.update(changes)
    return result


def point(cid="c1", score=0.9, **changes):
    return SimpleNamespace(id="different-Qdrant-UUID", score=score, payload=payload(cid, **changes))


@pytest.fixture
def deps():
    embeddings = Mock(dimension=768)
    embeddings.embed_single.return_value = [1.0]+[0.0]*767
    client = Mock()
    client.get_collection.return_value = SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(
        vectors=models.VectorParams(size=768, distance=models.Distance.COSINE))))
    client.query_points.return_value = SimpleNamespace(points=[])
    resolver = Mock()
    resolver.resolve.return_value = {}
    retriever = HierarchicalRetriever(embeddings=embeddings, client=client, context_resolver=resolver)
    return retriever, embeddings, client, resolver


def test_query_embedding_top_k_and_threshold(deps):
    retriever, embeddings, client, _ = deps
    retriever.retrieve("  query text  ", top_k=7, similarity_threshold=0.7)
    embeddings.embed_single.assert_called_once_with("  query text  ")
    client.get_collection.assert_called_once_with(COLLECTION)
    client.query_points.assert_called_once_with(collection_name=COLLECTION, query=[1.0]+[0.0]*767,
        limit=7, score_threshold=0.7, with_payload=True, with_vectors=False)


def test_score_order_threshold_boundary_and_top_k(deps):
    retriever, _, client, _ = deps
    client.query_points.return_value.points = [point("z", .6), point("a", .9), point("b", .9), point("low", .59)]
    assert [h.chunk_id for h in retriever.retrieve("query", top_k=2, similarity_threshold=.6).hits] == ["a", "b"]
    result = retriever.retrieve("query", top_k=4, similarity_threshold=.6)
    assert [h.score for h in result.hits] == [.9, .9, .6]
    assert [h.chunk_id for h in result.hits] == ["a", "b", "z"]


def test_configured_defaults_and_negative_cosine_scores(deps):
    retriever, _, client, _ = deps
    retriever.config = HierarchicalRetrievalConfig(top_k=2, similarity_threshold=-.5, expand_parents=False)
    client.query_points.return_value.points = [point("neg", -.4), point("low", -.6)]
    assert retriever.retrieve("query").hits[0].score == -.4
    assert client.query_points.call_args.kwargs["limit"] == 2


def test_full_payload_metadata_exact_text_and_independent_copy(deps):
    retriever, _, client, _ = deps
    item = point(parent_id_path=["ancestor"], metadata={"original": ["é", 1]}, extra="preserved")
    original = deepcopy(item.payload)
    client.query_points.return_value.points = [item]
    response = retriever.retrieve("query")
    hit = response.hits[0]
    for field in original:
        if field not in ("metadata", "extra"):
            assert getattr(hit, field) == original[field]
    assert hit.payload_metadata == original
    assert hit.parent_id_path_source == "payload"
    assert original["text"] in response.context_text
    assert response.to_dict()["hits"][0]["text"] == original["text"]
    hit.payload_metadata["metadata"]["original"].append("changed response")
    assert item.payload == original


def test_original_payload_has_no_ancestor_path_and_no_invented_parent(deps):
    retriever, _, client, _ = deps
    client.query_points.return_value.points = [point()]
    response = retriever.retrieve("query")
    assert response.hits[0].parent_id_path is None
    assert response.hits[0].parent_id_path_source == "unavailable"
    assert response.contexts[0].parents == []
    assert response.hits[0].parent_id == "p1"


def parent(pid="p1", text="Actual parent text", **changes):
    fields = dict(parent_id=pid, text=text, document_id="doc-1", file_name="one.pdf", source_path="raw/one.pdf",
                  section_path=[], page_start=1, page_end=2, block_type="heading")
    fields.update(changes)
    return ParentEvidence(**fields)


def test_parent_ancestor_expansion_once_and_no_sibling_fetches(deps):
    retriever, _, client, resolver = deps
    client.query_points.return_value.points = [point("c2", .8), point("c1", .9)]
    evidence = SourceResolution(["ancestor"], [parent("ancestor", "Exact ancestor"), parent()])
    resolver.resolve.return_value = {("doc-1", "raw/one.pdf", cid): evidence for cid in ("c1", "c2")}
    result = retriever.retrieve("query")
    assert len(result.contexts) == 1
    assert [p.parent_id for p in result.contexts[0].parents] == ["ancestor", "p1"]
    assert result.context_text.count("Actual parent text") == 1
    assert result.context_text.count("Exact ancestor") == 1
    assert all(h.parent_id_path == ["ancestor"] for h in result.hits)
    assert len(result.contexts[0].fragments) == 1
    assert result.contexts[0].fragments[0].chunk_ids == ["c1", "c2"]
    client.query_points.assert_called_once()
    client.scroll.assert_not_called()
    client.retrieve.assert_not_called()


def test_duplicate_chunks_keep_best_score_context_aliases_and_sources(deps):
    retriever, _, client, _ = deps
    client.query_points.return_value.points = [point("c1", .7), point("c2", .8), point("c1", .9),
        point("c3", .85, source_path="raw/other.pdf")]
    result = retriever.retrieve("query")
    assert [h.chunk_id for h in result.hits] == ["c1", "c3", "c2"]
    assert len(result.contexts) == 2
    assert len(result.contexts[0].fragments) == 1
    assert result.contexts[0].fragments[0].chunk_ids == ["c1", "c2"]
    assert result.contexts[1].source_path == "raw/other.pdf"


def test_duplicate_conflicting_payload_is_error(deps):
    retriever, _, client, _ = deps
    client.query_points.return_value.points = [point(), point(text="different")]
    with pytest.raises(ValueError, match="Conflicting payloads"):
        retriever.retrieve("query")


def test_roots_on_different_pages_and_parents_do_not_merge(deps):
    retriever, _, client, _ = deps
    client.query_points.return_value.points = [point("c1", parent_id=None, section_path=[], page_start=1, page_end=1),
        point("c2", parent_id=None, section_path=[], page_start=2, page_end=2), point("c3", parent_id="p2")]
    result = retriever.retrieve("query")
    assert len(result.contexts) == 3
    assert result.hits[0].parent_id is None


def test_parent_budget_omits_whole_parent_never_truncates_child(deps):
    retriever, _, client, resolver = deps
    retriever.config = HierarchicalRetrievalConfig(max_parent_chars=5)
    client.query_points.return_value.points = [point(text="x"*10000)]
    resolver.resolve.return_value = {("doc-1", "raw/one.pdf", "c1"): SourceResolution([], [parent()])}
    result = retriever.retrieve("query")
    assert result.contexts[0].parents == []
    assert "x"*10000 in result.context_text
    assert "character budget" in result.warnings[0]


def test_expand_parents_disabled(deps):
    retriever, _, client, resolver = deps
    retriever.config = HierarchicalRetrievalConfig(expand_parents=False)
    client.query_points.return_value.points = [point()]
    assert retriever.retrieve("query").contexts[0].parents == []
    resolver.resolve.assert_not_called()


def test_missing_source_keeps_child_and_explicit_warning(deps):
    retriever, _, client, resolver = deps
    client.query_points.return_value.points = [point()]
    resolver.resolve.side_effect = FileNotFoundError("source missing")
    result = retriever.retrieve("query")
    assert len(result.hits) == 1 and result.contexts[0].parents == []
    assert "source missing" in result.warnings[0]


def test_cross_document_parent_is_rejected(deps):
    retriever, _, client, resolver = deps
    client.query_points.return_value.points = [point()]
    resolver.resolve.return_value = {("doc-1", "raw/one.pdf", "c1"): SourceResolution([], [parent(source_path="other")])}
    with pytest.raises(ValueError, match="does not belong"):
        retriever.retrieve("query")


def test_empty_results_no_context_or_resolver(deps):
    retriever, _, _, resolver = deps
    result = retriever.retrieve("query")
    assert result.hits == result.contexts == result.warnings == []
    assert result.context_text == ""
    resolver.resolve.assert_not_called()


def test_all_below_threshold_returns_empty(deps):
    retriever, _, client, resolver = deps
    client.query_points.return_value.points = [point(score=.1)]
    assert retriever.retrieve("query").hits == []
    resolver.resolve.assert_not_called()


def test_production_isolation_ignores_collection_settings(deps, monkeypatch):
    from app.ai.config import ai_settings
    monkeypatch.setattr(ai_settings, "qdrant_collection", "buildlearn_products")
    monkeypatch.setattr(ai_settings, "qdrant_collection_hierarchical", "buildlearn_products")
    retriever, _, client, _ = deps
    retriever.retrieve("query")
    client.get_collection.assert_called_once_with(COLLECTION)
    assert client.query_points.call_args.kwargs["collection_name"] == COLLECTION
    for method in ("create_collection", "delete_collection", "upsert", "delete", "get_collections", "scroll"):
        getattr(client, method).assert_not_called()


@pytest.mark.parametrize("query", ["", "   ", None, 123])
def test_invalid_query_no_service_calls(deps, query):
    retriever, embeddings, client, _ = deps
    with pytest.raises(ValueError):
        retriever.retrieve(query)
    embeddings.embed_single.assert_not_called()
    client.get_collection.assert_not_called()


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_invalid_k(deps, value):
    with pytest.raises(ValueError, match="top_k"):
        deps[0].retrieve("query", top_k=value)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.1, 1.1, True])
def test_invalid_threshold(deps, value):
    with pytest.raises(ValueError, match="similarity_threshold"):
        deps[0].retrieve("query", similarity_threshold=value)


@pytest.mark.parametrize("kind", ["dimension", "distance", "named"])
def test_collection_configuration_rejected_before_embedding(deps, kind):
    retriever, embeddings, client, _ = deps
    p = models.VectorParams(size=1 if kind == "dimension" else 768,
                            distance=models.Distance.DOT if kind == "distance" else models.Distance.COSINE)
    client.get_collection.return_value.config.params.vectors = {"named": p} if kind == "named" else p
    with pytest.raises(ValueError, match="COSINE"):
        retriever.retrieve("query")
    embeddings.embed_single.assert_not_called()
    client.query_points.assert_not_called()


@pytest.mark.parametrize("kind", ["dimension", "nan", "inf", "zero", "unnormalized"])
def test_invalid_query_vector_no_search(deps, kind):
    retriever, embeddings, client, _ = deps
    vector = [1.0]+[0.0]*767
    if kind == "dimension":
        vector.pop()
    elif kind in ("nan", "inf"):
        vector[0] = float(kind)
    else:
        vector[0] = 0 if kind == "zero" else 2
    embeddings.embed_single.return_value = vector
    with pytest.raises(ValueError):
        retriever.retrieve("query")
    client.query_points.assert_not_called()


@pytest.mark.parametrize("field,value", [("text", ""), ("chunk_id", None), ("section_path", "fake"),
    ("page_start", True), ("page_end", 0), ("parent_id", ""), ("parent_id_path", "fake"), ("block_type", "bogus")])
def test_bad_payload_is_not_silently_skipped(deps, field, value):
    retriever, _, client, _ = deps
    client.query_points.return_value.points = [point(**{field: value})]
    with pytest.raises(ValueError):
        retriever.retrieve("query")


def test_errors_propagate_without_fabricated_results(deps):
    retriever, embeddings, client, _ = deps
    embeddings.embed_single.side_effect = RuntimeError("Ollama unavailable")
    with pytest.raises(RuntimeError, match="Ollama unavailable"):
        retriever.retrieve("query")
    client.query_points.assert_not_called()
    embeddings.embed_single.side_effect = None
    client.query_points.side_effect = RuntimeError("Qdrant unavailable")
    with pytest.raises(RuntimeError, match="Qdrant unavailable"):
        retriever.retrieve("query")


def test_default_creation_uses_existing_embedding_service_nomic(deps, monkeypatch):
    from app.ai.config import ai_settings
    retriever, embeddings, client, _ = deps
    retriever._embeddings = None
    monkeypatch.setattr(ai_settings, "embedding_provider", "")
    monkeypatch.setattr(ai_settings, "embedding_model", "")
    with patch("app.ai.retrieval.hierarchical_retriever.OllamaEmbeddingProvider") as provider, \
         patch("app.ai.retrieval.hierarchical_retriever.EmbeddingService", return_value=embeddings) as service:
        retriever.retrieve("query")
    assert provider.call_args.kwargs["model"] == "nomic-embed-text"
    assert provider.call_args.kwargs["normalize"] is True
    service.assert_called_once_with(provider=provider.return_value)


@pytest.fixture
def source_fixture(tmp_path):
    root = tmp_path / "extraction"
    root.mkdir()
    doc = dict(document_id="source-doc", source_path="raw/source.pdf", file_name="source.pdf",
               extraction_status="success", pages=[dict(page_number=1, raw_text="SPECIFICATIONS\nOriginal source body.")])
    path = root / "source.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    result = HierarchicalChunker().chunk_from_dict(doc)
    child = result.children[0]
    p = payload(child.chunk_id, document_id=child.source.document_id, source_path=child.source.source_path,
        file_name=child.source.file_name, text=child.text, parent_id=child.parent_id, section_path=child.section_path,
        page_start=child.page_start, page_end=child.page_end, block_type=child.block_type.value)
    hit = HierarchicalRetriever._hit(SimpleNamespace(payload=p, score=.9))
    inventory = [{"file": "source.json", "document_id": doc["document_id"],
                  "hash": hashlib.sha256(path.read_bytes()).hexdigest(), "chunk_ids": [child.chunk_id]}]
    state = {"identity": {"collection": COLLECTION, "dataset_id": _digest(inventory),
        "chunk_config": json.loads(json.dumps(asdict(ChunkConfig()))),
        "implementation": _digest({p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("chunking", "embeddings") for p in sorted((BACKEND / "app/ai" / folder).glob("*.py"))})},
        "successful_chunks": [child.chunk_id], "dataset_manifest": inventory}
    checkpoint = tmp_path / "checkpoint.json"
    checkpoint.write_text(json.dumps({"state": state, "sha256": _digest(state)}), encoding="utf-8")
    return ExtractionContextResolver(root, checkpoint), hit, result, path, checkpoint


def test_actual_source_parent_resolver_read_only(source_fixture):
    resolver, hit, result, path, checkpoint = source_fixture
    before = (path.read_bytes(), checkpoint.read_bytes())
    resolution = resolver.resolve([hit])[(hit.document_id, hit.source_path, hit.chunk_id)]
    assert resolution.parent_id_path == []
    assert resolution.parents[0].text == result.parents[0].text == "SPECIFICATIONS"
    assert resolution.parents[0].parent_id == hit.parent_id
    assert before == (path.read_bytes(), checkpoint.read_bytes())


@pytest.mark.parametrize("kind", ["source", "checksum", "config", "implementation", "payload", "collection", "ancestor"])
def test_source_evidence_changes_are_rejected(source_fixture, kind):
    resolver, hit, _, path, checkpoint = source_fixture
    if kind == "source":
        path.write_text(path.read_text()+" ")
    elif kind == "payload":
        hit.payload_metadata["text"] = "not original"
    elif kind == "ancestor":
        hit.parent_id_path = ["invented"]
    else:
        e = json.loads(checkpoint.read_text())
        if kind == "checksum":
            e["sha256"] = "corrupt"
        else:
            e["state"]["identity"]["chunk_config" if kind == "config" else kind] = "changed"
            e["sha256"] = _digest(e["state"])
        checkpoint.write_text(json.dumps(e))
    with pytest.raises(ValueError):
        resolver.resolve([hit])


def test_retrieval_with_actual_verified_parent_source(deps, source_fixture):
    retriever, _, client, _ = deps
    resolver, hit, _, _, _ = source_fixture
    retriever._resolver = resolver
    client.query_points.return_value.points = [SimpleNamespace(payload=hit.payload_metadata, score=.9)]
    response = retriever.retrieve("query")
    assert response.hits[0].text == "Original source body."
    assert response.hits[0].parent_id_path == []
    assert response.hits[0].parent_id_path_source == "verified_source_child"
    assert response.contexts[0].parents[0].text == "SPECIFICATIONS"
    assert response.warnings == []


def test_service_dimension_mismatch_no_query(deps):
    retriever, embeddings, client, _ = deps
    embeddings.dimension = 4
    with pytest.raises(ValueError, match="dimension"):
        retriever.retrieve("query")
    client.query_points.assert_not_called()


@pytest.mark.parametrize("kind", ["missing", "score_nan", "score_inf", "reversed_pages"])
def test_invalid_search_evidence_fails(deps, kind):
    retriever, _, client, _ = deps
    item = point()
    if kind == "missing":
        del item.payload["source_path"]
    elif kind in ("score_nan", "score_inf"):
        item.score = float(kind.removeprefix("score_"))
    else:
        item.payload["page_start"], item.payload["page_end"] = 3, 1
    client.query_points.return_value.points = [item]
    with pytest.raises(ValueError):
        retriever.retrieve("query")


def test_tie_order_and_context_order_independent_of_server_order(deps):
    retriever, _, client, _ = deps
    points = [point("b", .8), point("a", .8), point("c", .8, parent_id="p2")]
    client.query_points.return_value.points = points
    first = retriever.retrieve("query").to_dict()
    client.query_points.return_value.points = list(reversed(points))
    assert retriever.retrieve("query").to_dict() == first


def test_parent_text_equal_to_child_is_rendered_once(deps):
    retriever, _, client, resolver = deps
    text = "Exact container content"
    client.query_points.return_value.points = [point(text=text, block_type="table")]
    resolver.resolve.return_value = {("doc-1", "raw/one.pdf", "c1"): SourceResolution([], [parent(text=text)])}
    response = retriever.retrieve("query")
    assert response.context_text.count(text) == 1
    assert response.hits[0].text == text
    assert response.contexts[0].parents[0].text == text


def test_unrequested_parent_evidence_is_rejected(deps):
    retriever, _, client, resolver = deps
    client.query_points.return_value.points = [point()]
    resolver.resolve.return_value = {("doc-1", "raw/one.pdf", "c1"): SourceResolution([], [parent("other")])}
    with pytest.raises(ValueError, match="does not belong"):
        retriever.retrieve("query")


@pytest.mark.parametrize("changes", [{"top_k": 0}, {"similarity_threshold": float("nan")},
    {"max_parent_chars": -1}, {"expand_parents": "yes"}])
def test_invalid_constructor_configuration(changes):
    with pytest.raises(ValueError):
        HierarchicalRetrievalConfig(**changes)


def test_default_client_still_pins_only_hierarchical_collection(deps):
    retriever, _, client, _ = deps
    retriever._client = None
    with patch("app.ai.retrieval.hierarchical_retriever.QdrantClient", return_value=client):
        retriever.retrieve("query")
    client.get_collection.assert_called_once_with(COLLECTION)
    assert client.query_points.call_args.kwargs["collection_name"] == COLLECTION


def test_unsupported_default_model_is_rejected(deps, monkeypatch):
    from app.ai.config import ai_settings
    retriever, _, client, _ = deps
    retriever._embeddings = None
    monkeypatch.setattr(ai_settings, "embedding_model", "qwen2.5")
    with pytest.raises(ValueError, match="nomic-embed-text"):
        retriever.retrieve("query")
    client.query_points.assert_not_called()


def test_resolver_disambiguates_reused_document_id_by_source_path(source_fixture):
    resolver, hit, _, _, checkpoint = source_fixture
    envelope = json.loads(checkpoint.read_text())
    other = dict(document_id=hit.document_id, source_path="raw/other.pdf", file_name="other.pdf",
                 extraction_status="success", pages=[dict(page_number=1, raw_text="OTHER HEADING\nOther body.")])
    other_path = resolver.root / "other.json"
    other_path.write_text(json.dumps(other))
    other_result = HierarchicalChunker().chunk_from_dict(other)
    state = envelope["state"]
    state["dataset_manifest"].insert(0, {"file": "other.json", "document_id": hit.document_id,
        "hash": hashlib.sha256(other_path.read_bytes()).hexdigest(),
        "chunk_ids": [c.chunk_id for c in other_result.children]})
    state["successful_chunks"].extend(c.chunk_id for c in other_result.children)
    state["identity"]["dataset_id"] = _digest(state["dataset_manifest"])
    envelope["sha256"] = _digest(state)
    checkpoint.write_text(json.dumps(envelope))
    evidence = resolver.resolve([hit])[(hit.document_id, hit.source_path, hit.chunk_id)]
    assert evidence.parents[0].file_name == "source.pdf"
    assert evidence.parents[0].text == "SPECIFICATIONS"


def test_changed_source_parent_warning_protects_qdrant_text(deps, source_fixture):
    retriever, _, client, _ = deps
    resolver, hit, _, path, _ = source_fixture
    retriever._resolver = resolver
    client.query_points.return_value.points = [SimpleNamespace(payload=hit.payload_metadata, score=.9)]
    path.write_text(path.read_text().replace("SPECIFICATIONS", "NEW HEADING"))
    result = retriever.retrieve("query")
    assert result.hits[0].text == hit.text
    assert result.contexts[0].parents == []
    assert "Extraction changed" in result.warnings[0]
    assert "NEW HEADING" not in result.context_text


def test_roots_with_unknown_page_location_are_not_assumed_related(deps):
    retriever, _, client, _ = deps
    client.query_points.return_value.points = [point(cid, parent_id=None, section_path=[], page_start=None, page_end=None)
                                               for cid in ("c1", "c2")]
    result = retriever.retrieve("query")
    assert len(result.contexts) == 2
    assert all(c.page_start is None and c.page_end is None for c in result.contexts)
