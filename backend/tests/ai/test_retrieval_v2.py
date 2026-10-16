from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from qdrant_client.http import models
from app.ai.retrieval.retrieval_v2 import RetrievalV2, RetrievalV2Config, LexicalIndex, normalize, tokens, overview_priority
from app.ai.retrieval.hierarchical_models import ParentEvidence, SourceResolution
from app.ai.retrieval.hierarchical_retriever import COLLECTION


def payload(cid="a", file="AX123%20Data.pdf", text="  Consommation 25 kg\nBéton original.  "):
    return dict(chunk_id=cid, document_id=file, file_name=file, source_path="raw/"+file,
        text=text, parent_id="parent", section_path=["SPECIFICATIONS"], page_start=1,
        page_end=2, block_type="paragraph", extra={"nested": [1, 2]})


@pytest.fixture
def deps():
    rows=[payload(), payload("b", "BX456.pdf", "Autre produit 7 kg")]
    client=Mock()
    client.get_collection.return_value=SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(
        vectors=models.VectorParams(size=768, distance=models.Distance.COSINE))))
    client.scroll.return_value=([SimpleNamespace(payload=r) for r in rows],None)
    client.query_points.return_value=SimpleNamespace(points=[SimpleNamespace(payload=rows[1],score=.9)])
    embedding=Mock(dimension=768);embedding.embed_single.return_value=[1.0]+[0.0]*767
    resolver=Mock();resolver.resolve.return_value={}
    return RetrievalV2(client=client, embeddings=embedding, context_resolver=resolver),client,embedding,resolver,rows


def test_normalization_and_numeric_preservation():
    assert normalize("BÉTON œuvré") == "beton oeuvre"
    assert {"ax123","25","0,5","0.5"} <= tokens("AX123 25 kg 0,5 / 0.5")


def test_product_overview_selects_owned_facts_and_deduplicates(deps):
    v, client, _, resolver, _ = deps
    finishing = payload('finish', text='Finition avec OMEGA FINO.')
    spec = payload('spec', text='Pression : 10 bar.')
    duplicate = deepcopy(spec); duplicate['chunk_id'] = 'spec-copy'; duplicate['source_path'] = 'duplicate/AX123.pdf'
    other = payload('other', file='BX456.pdf', text='Pression : 99 bar.')
    second = payload('second', text='Puissance : 750 W.')
    client.scroll.return_value = ([SimpleNamespace(payload=r) for r in [finishing, spec, duplicate, other, second]], None)
    client.query_points.return_value = SimpleNamespace(points=[])
    identities = Mock()
    identities.resolve.return_value = SimpleNamespace(safe=True, resolved_product_ids=('product-a',))
    identities.ownership.side_effect = lambda source: {'product-a'} if source.file_name == spec['file_name'] else {'product-b'}
    v.identity_resolver = identities
    result = v.retrieve('Quelles sont les caractéristiques de AX123 ?', top_k=2)
    assert {h.text for h in result.hits} == {'Pression : 10 bar.', 'Puissance : 750 W.'}
    assert all(h.product_overview_match and h.overview_priority == 3 for h in result.hits)
    assert all(h.file_name == spec['file_name'] for h in result.hits)
    assert any('product_overview' in h.candidate_sources for h in result.candidates)
    assert len([h for h in result.candidates if h.text == spec['text']]) == 2
    again = v.retrieve('Quelles sont les caractéristiques de AX123 ?', top_k=2)
    assert [h.chunk_id for h in again.hits] == [h.chunk_id for h in result.hits]
    resolver.resolve.assert_called()
    assert result.hits[0].payload_metadata['text'] == result.hits[0].text


def test_overview_does_not_route_ambiguous_or_comparison_queries(deps):
    v, _, _, _, _ = deps
    identities = Mock()
    identities.resolve.return_value = SimpleNamespace(safe=False, resolved_product_ids=())
    v.identity_resolver = identities
    assert 'product_overview_ids' not in v.retrieve('caractéristiques AX123').query_analysis
    identities.resolve.return_value = SimpleNamespace(safe=True, resolved_product_ids=('a', 'b'))
    assert 'product_overview_ids' not in v.retrieve('specifications AX123 BX456').query_analysis
    identities.ownership.assert_not_called()


def test_specific_query_keeps_existing_retrieval_path(deps):
    v, _, _, _, _ = deps
    v.identity_resolver = Mock()
    result = v.retrieve('AX123 consommation 25')
    v.identity_resolver.resolve.assert_not_called()
    assert all(not h.product_overview_match for h in result.hits)
    v.retrieve('Quelles caractéristiques de pression maximale pour AX123 ?')
    v.identity_resolver.resolve.assert_not_called()


def test_overview_prefers_explicit_values_over_labels_and_ocr():
    assert overview_priority(payload(text='Pression : 10 bar.')) == 3
    assert overview_priority(payload(text='Conductivité (| = W/m.K) 0,39')) == 2
    label = payload(text='Consommation'); label['section_path'] = ['CARACTERISTIQUES']
    assert overview_priority(label) == 1
    storage = payload(text='Stockage au sec.'); storage['section_path'] = ['STOCKAGE']
    assert overview_priority(storage) == 0


def test_corpus_routing_and_url_decoding():
    idx=LexicalIndex([payload(file="AX123%20Data.pdf"),payload("b",file="BX7A30.pdf")])
    assert idx.analyze("ax123 produit")["route_status"] == "unique"
    assert idx.analyze("BX7A30")["identifiers"] == ["BX7A30"]
    assert idx.analyze("EN12004 2026")["route_source"] is None
    ranks=idx.rank("AX123 Data",idx.analyze("AX123 Data"))
    assert next(iter(ranks.values()))[1][2] == 1


def test_ambiguous_or_multiple_references_do_not_route():
    one=payload();two=deepcopy(one);two["source_path"]="elsewhere"
    idx=LexicalIndex([one,two,payload("b",file="BX456.pdf")])
    assert idx.analyze("AX123")["route_source"] is None
    assert idx.analyze("AX123 BX456")["route_source"] is None
    assert idx.analyze("BX456 ZZ999")["route_source"] is None


def test_union_ranking_and_all_provenance(deps):
    v,c,e,r,rows=deps
    result=v.retrieve("AX123 consommation 25",top_k=1)
    h=result.hits[0]
    assert h.chunk_id=="a" and h.identifier_route and h.identifier_match
    assert h.numeric_match==1 and h.filename_match>0
    assert h.lexical_rank==1 and h.lexical_score>0
    assert h.dense_rank is None and h.dense_score is None
    other=next(h for h in result.candidates if h.chunk_id=="b")
    assert other.dense_rank==1 and other.dense_score==.9
    assert "dense" in other.candidate_sources
    assert {h.chunk_id for h in result.candidates}=={"a","b"}
    e.embed_single.assert_called_once_with("AX123 consommation 25")


def test_union_deduplicates_branch_memberships(deps):
    v,c,e,r,rows=deps
    c.query_points.return_value.points=[SimpleNamespace(payload=rows[0],score=.8)]
    result=v.retrieve("AX123 consommation")
    h=next(h for h in result.candidates if h.chunk_id=="a")
    assert h.candidate_sources==["dense","identifier_route","lexical"]
    assert h.dense_score==.8 and h.dense_rank==1
    assert len([x for x in result.candidates if x.chunk_id=="a"])==1


def test_exact_text_and_metadata_are_preserved_and_detached(deps):
    v,c,e,r,rows=deps
    h=v.retrieve("AX123").hits[0]
    assert h.text==rows[0]["text"]
    assert h.payload_metadata==rows[0] and h.section_path==["SPECIFICATIONS"]
    assert (h.page_start,h.page_end,h.parent_id)==(1,2,"parent")
    h.payload_metadata["extra"]["nested"].append(3)
    assert v.retrieve("AX123").hits[0].payload_metadata["extra"]["nested"]==[1,2]


def test_verified_parent_expansion_only_after_final_selection(deps):
    v,c,e,r,rows=deps
    p=ParentEvidence("parent","EXACT parent body",rows[0]["document_id"],rows[0]["file_name"],
        rows[0]["source_path"],["SPECIFICATIONS"],1,2,"paragraph")
    r.resolve.return_value={(rows[0]["document_id"],rows[0]["source_path"],"a"):SourceResolution([], [p])}
    response=v.retrieve("AX123",top_k=1)
    assert [h.chunk_id for h in r.resolve.call_args.args[0]]==["a"]
    assert response.contexts[0].parents==[p]
    assert "EXACT parent body" in response.context_text and rows[0]["text"] in response.context_text
    assert response.hits[0].parent_id_path_source=="verified_source_child"


def test_unverified_parent_is_not_invented(deps):
    v,c,e,r,rows=deps;r.resolve.side_effect=ValueError("source changed")
    result=v.retrieve("AX123")
    assert result.warnings and all(not ctx.parents for ctx in result.contexts)
    assert result.hits[0].text==rows[0]["text"]


def test_lexical_modes_skip_embeddings_and_dense(deps):
    v,c,e,r,rows=deps
    for mode in ("lexical","identifier_lexical"):
        assert v.retrieve("AX123",mode=mode).hits
    e.embed_single.assert_not_called();c.query_points.assert_not_called()


def test_deterministic_ties_and_dense_tiebreak(deps):
    v,c,e,r,rows=deps
    one=payload("a",text="same fact");two=payload("z",text="same fact")
    c.scroll.return_value=([SimpleNamespace(payload=x) for x in [two,one]],None)
    assert [h.chunk_id for h in v.retrieve("same",mode="lexical").hits]==["a","z"]
    c.query_points.return_value.points=[SimpleNamespace(payload=two,score=.9),SimpleNamespace(payload=one,score=.8)]
    assert [h.chunk_id for h in v.retrieve("same").hits]==["z","a"]


def test_configurable_candidate_counts(deps):
    v,c,e,r,rows=deps
    v.config=RetrievalV2Config(lexical_candidates=1,dense_candidates=7,expand_parents=False)
    v.retrieve("consommation")
    assert c.query_points.call_args.kwargs["limit"]==7
    assert c.query_points.call_args.kwargs["score_threshold"]==0.0
    assert sum("lexical" in x.candidate_sources for x in v.retrieve("consommation").candidates)<=1


def test_collection_isolation_and_read_only_snapshot(deps):
    v,c,e,r,rows=deps;v.retrieve("AX123")
    assert c.scroll.call_args.args==(COLLECTION,)
    assert c.scroll.call_args.kwargs["with_vectors"] is False
    assert c.query_points.call_args.kwargs["collection_name"]==COLLECTION
    assert all(call[0] in {"scroll","query_points","get_collection"} for call in c.method_calls)


def test_snapshot_staleness_is_explicit(deps):
    v,c,e,r,rows=deps;v.refresh()
    changed=deepcopy(rows[0]);changed["text"]="changed"
    c.query_points.return_value.points=[SimpleNamespace(payload=changed,score=.9)]
    with pytest.raises(ValueError,match="refresh required"):v.retrieve("AX123")


def test_empty_lexical_results(deps):
    v,c,e,r,rows=deps
    result=v.retrieve("!!!",mode="lexical")
    assert not result.hits and not result.contexts and result.context_text==""


@pytest.mark.parametrize("field,value",[("top_k",0),("dense_candidates",False),("lexical_candidates",-1)])
def test_invalid_config(field,value):
    with pytest.raises(ValueError):RetrievalV2Config(**{field:value})


def test_conflicting_payload_identity_rejected():
    row=payload();other=deepcopy(row);other["text"]="conflict"
    with pytest.raises(ValueError,match="Conflicting"):LexicalIndex([row,other])


def test_validation_uses_cosine_collection(deps):
    v,c,e,r,rows=deps
    c.get_collection.return_value.config.params.vectors=models.VectorParams(size=768,distance=models.Distance.DOT)
    with pytest.raises(ValueError,match="COSINE"):v.refresh()
