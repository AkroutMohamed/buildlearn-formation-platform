"""Offline metric/harness tests. Never contacts Ollama or Qdrant."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from scripts import evaluate_hierarchical_retrieval as evaluation


def evidence(cid="expected", text="fact", **overrides):
    return dict(document_id="doc", file_name="file.pdf", source_path="raw/file.pdf",
                chunk_ids=[cid], substring=text, **overrides)


def label(units=None):
    return dict(id="q", query="question", categories=["technical specifications"],
                evidence=units or [evidence()])


def hit(cid="expected", text="fact", score=.8, **overrides):
    return dict(document_id="doc", file_name="file.pdf", source_path="raw/file.pdf",
                chunk_id=cid, text=text, score=score) | overrides


def response(hits=None, parents=None):
    hits = hits or []
    return dict(hits=hits, contexts=[dict(document_id="doc", file_name="file.pdf",
        source_path="raw/file.pdf", chunk_ids=[h["chunk_id"] for h in hits], parents=parents or [])], warnings=[])


def test_perfect_metrics():
    m=evaluation.measure(label(),response([hit()]),False)
    assert all(m[k] == 1 for k in ("hit","reciprocal_rank","document_recall",
        "exact_evidence_recall","substring_evidence_recall","evidence_recall"))
    assert m["empty"] == 0


def test_rank_and_partial_required_evidence():
    m=evaluation.measure(label([evidence(),evidence("two","second")]),
                         response([hit("wrong","other"),hit()]),False)
    assert m["reciprocal_rank"] == .5
    assert m["evidence_recall"] == .5
    assert m["hit"] == 1


def test_alternative_ids_count_as_one_fact():
    unit=evidence();unit["chunk_ids"]=["expected","alternative"]
    assert evaluation.measure(label([unit]),response([hit("alternative")]),False)["evidence_recall"] == 1


def test_substring_alternative_and_case_sensitive_match():
    assert evaluation.measure(label(),response([hit("other","prefix fact suffix")]),False)["substring_evidence_recall"] == 1
    m=evaluation.measure(label(),response([hit("other","FACT")]),False)
    assert m["hit"] == 0 and m["exact_evidence_recall"] == 0


@pytest.mark.parametrize("field,value",[("document_id","wrong"),("source_path","elsewhere"),("file_name","other.pdf")])
def test_same_text_or_id_from_wrong_source_is_not_relevant(field,value):
    assert evaluation.measure(label(),response([hit(**{field:value})]),True)["hit"] == 0


def test_empty_results_have_zero_metrics():
    m=evaluation.measure(label(),response(),True)
    assert m["empty"] == 1
    assert not any(m[k] for k in m if k != "empty")


def test_verified_parent_improves_substring_not_exact_or_document_recall():
    parent=hit("parent","the fact is present")
    result=response([hit("different","heading")],[parent])
    child=evaluation.measure(label(),result,False)
    expanded=evaluation.measure(label(),result,True)
    assert child["hit"] == 0 and expanded["hit"] == 1
    assert expanded["exact_evidence_recall"] == 0
    assert child["document_recall"] == expanded["document_recall"] == 1


def test_parent_of_unselected_chunk_does_not_count():
    result=response([hit("different","heading")],[hit("parent","fact")])
    result["contexts"][0]["chunk_ids"]=["unselected"]
    assert evaluation.measure(label(),result,True)["hit"] == 0


def test_wrong_source_parent_does_not_count():
    result=response([hit("different","heading")],[hit("parent","fact",source_path="other")])
    assert evaluation.measure(label(),result,True)["hit"] == 0


def test_document_recall_multiple_sources_and_duplicates():
    unit=evidence();unit["source_path"]="other"
    m=evaluation.measure(label([evidence(),unit]),response([hit(),hit()]),False)
    assert m["document_recall"] == .5
    assert m["evidence_recall"] == .5


def test_aggregate_empty_queries_and_micro_average_scores():
    records=[dict(metrics=evaluation.measure(label(),response([hit(score=.9),hit(score=.7)]),False),
                  response=response([hit(score=.9),hit(score=.7)])),
             dict(metrics=evaluation.measure(label(),response(),False),response=response())]
    result=evaluation.aggregate(records)
    assert result["hit"] == .5 and result["empty_queries"] == 1
    assert result["average_returned_score"] == pytest.approx(.8)
    assert evaluation.aggregate([records[1]])["average_returned_score"] is None


def test_query_embedding_cache_uses_existing_service_once_per_exact_query():
    service=Mock(dimension=768);service.embed_single.return_value=[1.0]*768
    cache=evaluation.CachedQueries(service)
    v=cache.embed_single("query");v[0]=0
    assert cache.embed_single("query")[0] == 1
    cache.embed_single("other")
    assert service.embed_single.call_count == 2
    assert cache.dimension == 768


def test_collection_inventory_is_read_only_and_isolated():
    point=Mock(payload=hit());point.model_dump_json.return_value='{"id":1}'
    client=Mock();client.scroll.side_effect=[([point],"next"),([],None)]
    rows,digest=evaluation.read_collection(client)
    assert rows == [point.payload] and len(digest) == 64
    for call in client.scroll.call_args_list:
        assert call.args == ("buildlearn_products_hierarchical_v1",)
        assert call.kwargs["with_vectors"] is True
    assert [c[0] for c in client.method_calls] == ["scroll","scroll"]


def test_all_labels_have_real_evidence_and_category_coverage():
    labels=evaluation.LABELS
    assert len(labels) >= 30
    assert len({q["id"] for q in labels}) == len(labels)
    required={"product identification","technical specifications","application/use","consumption",
              "dimensions","standards/norms","substrate/support compatibility",
              "preparation/application instructions","safety/limitations","cross-document ambiguity",
              "vague/general","highly specific"}
    assert required <= {c for q in labels for c in q["categories"]}
    assert all(e["substring"] and e["chunk_ids"] and e["source_path"] for q in labels for e in q["evidence"])
    assert evaluation.LABELS[1]["query"].endswith("capacité ?")
    assert all("?" not in q["query"][:-1] for q in labels)


def test_label_validation_rejects_missing_or_changed_evidence():
    labels=[dict(label(),id=str(i)) for i in range(30)]
    row=hit()
    evaluation.validate_labels(labels,[row])
    with pytest.raises(ValueError,match="changed"):
        evaluation.validate_labels(labels,[hit(text="changed")])
    with pytest.raises(ValueError,match="Missing"):
        evaluation.validate_labels(labels,[])
    with pytest.raises(ValueError,match="uniquely"):
        evaluation.validate_labels([label()]*30,[row])


def test_failure_categories_are_overlapping_and_threshold_specific():
    q=label();q["categories"]=["vague/general"];q["parser_signal"]=True
    record=dict(label=q,metrics=dict(evidence_recall=0,hit=0))
    baseline=dict(metrics=dict(evidence_recall=1,hit=1))
    categories=evaluation.categorize(record,baseline,[hit(),hit(source_path="other")])
    assert set(categories) == {"threshold issue","label ambiguity","parser/chunking issue",
                               "duplicate/near-duplicate source issue"}
    assert evaluation.categorize(dict(label=label(),metrics=dict(evidence_recall=0,hit=0)),
        dict(metrics=dict(evidence_recall=0,hit=0)),[]) == ["embedding/retrieval issue"]


def test_recommendation_smallest_k_and_highest_lossless_threshold():
    summaries=[]
    for k,recall in [(1,.4),(3,.8),(5,.96),(10,1.0)]:
        for t in evaluation.THRESHOLDS:
            summaries.append(dict(mode="verified_parent",top_k=k,threshold=t,
                metrics=dict(evidence_recall=recall if t<.6 else recall-.1,
                    reciprocal_rank=.4,empty_queries=0)))
    result=evaluation.recommend(summaries)
    assert result["top_k"] == 5 and result["similarity_threshold"] == .5


def test_grid_uses_existing_retriever_at_all_k_thresholds(monkeypatch):
    monkeypatch.setattr(evaluation,"TOP_K",(1,3,5,10))
    retrievers={m:Mock() for m in evaluation.MODES}
    for retriever in retrievers.values():
        retriever.retrieve.return_value=SimpleNamespace(to_dict=lambda:response([hit()]))
    records,summaries=evaluation.run_evaluation(retrievers,[label()],[hit()])
    assert len(records) == len(summaries) == 48
    for retriever in retrievers.values():
        assert retriever.retrieve.call_count == 24
        assert {(c.kwargs["top_k"],c.kwargs["similarity_threshold"]) for c in retriever.retrieve.call_args_list} == {
            (k,t) for k in evaluation.TOP_K for t in evaluation.THRESHOLDS}
        assert all(c.args == ("question",) for c in retriever.retrieve.call_args_list)


def test_report_contains_metrics_labels_and_failure_diagnostics(tmp_path,monkeypatch):
    q=label();q["query"]="Une capacité inconnue ?"
    monkeypatch.setattr(evaluation,"LABELS",[q])
    h=hit("other","unknown");h.update(section_path=["SPECIFICATIONS"],block_type="paragraph")
    result=response([h])
    record=dict(mode="verified_parent",top_k=1,threshold=0.0,label=q,response=result,
                metrics=evaluation.measure(q,result,True),failure_categories=["embedding/retrieval issue"])
    child=dict(record,mode="child_only")
    summaries=[dict(mode=r["mode"],top_k=1,threshold=0.0,metrics=evaluation.aggregate([r])) for r in [record,child]]
    path=tmp_path/"report.md"
    evaluation.write_report(path,[record,child],summaries,dict(run_utc="test"))
    contents=path.read_text(encoding="utf-8")
    for expected in ("Une capacité inconnue ?","Mean score","Frozen labels","Complete per-query",
                     '"expected"','"section_path"','"block_type"',"embedding/retrieval issue",
                     "Measured findings","threshold-based abstention"):
        assert expected in contents
