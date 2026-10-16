from copy import deepcopy
import json
from types import SimpleNamespace
from unittest.mock import Mock, patch
import pytest

from app.ai.rag.hierarchical_rag_v2 import (
    HierarchicalRAGV2,RAGV2Config,GroundedQwenProvider,build_context,
)
from app.ai.retrieval.retrieval_v2 import V2Child,V2Response
from app.ai.retrieval.hierarchical_models import ParentEvidence


def hit(cid="a",file="AX123.pdf",text="  Couple maximal : 86 Nm. Tension : 20 V.\n"):
    return V2Child(chunk_id=cid,document_id=file,file_name=file,source_path="raw/"+file,
        text=text,score=1.2,parent_id="p1",section_path=["SPECIFICATIONS"],page_start=1,page_end=2,
        block_type="paragraph",word_match=.5,lexical_score=1.2,lexical_rank=1,
        candidate_sources=["lexical"],parent_id_path=[])


def retrieval(hits=None,contexts=None):
    return V2Response(hits or [hit()],contexts or [],"",[],[],
        dict(identifiers=["AX123"],unknown_identifiers=[],route_status="unique"))


def claims(text="Couple maximal : 86 Nm.",quote="Couple maximal : 86 Nm.",sid="SOURCE 1"):
    return json.dumps(dict(status="answered",claims=[dict(text=text,quote=quote,support_chunk_ids=[{"SOURCE 1":"a","SOURCE 2":"b"}.get(sid,"unlisted")])]))


@pytest.fixture
def deps():
    r=Mock();r.retrieve.return_value=retrieval()
    llm=Mock();llm.generate_grounded.return_value=claims()
    s=HierarchicalRAGV2(retriever=r,llm=llm,config=RAGV2Config(model="qwen2.5-coder:7b"))
    return s,r,llm


def test_v2_integration_and_exact_sources(deps):
    s,r,llm=deps;result=s.run("Quel couple pour AX123 ?")
    r.retrieve.assert_called_once_with("Quel couple pour AX123 ?",top_k=3)
    assert result.grounded and result.status=="answered" and "[SOURCE 1]" in result.answer
    source=result.sources[0]
    assert source.text==r.retrieve.return_value.hits[0].text
    assert (source.chunk_id,source.file_name,source.page_start,source.page_end)==("a","AX123.pdf",1,2)
    assert source.section_path==["SPECIFICATIONS"] and source.score==1.2
    context=llm.generate_grounded.call_args.args[1]
    assert source.text in context and "file_name:" in context and "END SOURCE 1" in context


def test_duplicate_body_retains_each_source_identity_once():
    data=retrieval([hit(),hit("b","BX456.pdf")])
    context,sources,omitted=build_context(data,6000)
    assert context.count(hit().text)==1 and len(sources)==2
    assert sources[0].text==sources[1].text
    assert "identical original text as SOURCE 1" in context
    assert sources[1].file_name=="BX456.pdf"


def test_parent_context_uses_own_pages_and_exact_text():
    child=hit();parent=ParentEvidence("p1","Exact original parent body",child.document_id,
        child.file_name,child.source_path,["PARENT"],1,3,"paragraph")
    ctx=SimpleNamespace(chunk_ids=["a"],document_id=child.document_id,file_name=child.file_name,
        source_path=child.source_path,parents=[parent])
    context,sources,omissions=build_context(retrieval([child],[ctx]),6000)
    assert sources[1].evidence_kind=="verified_parent" and sources[1].page_end==3
    assert sources[1].parent_id=="p1" and parent.text in context


def test_parent_rejected_if_hierarchy_is_wrong():
    child=hit();p=ParentEvidence("wrong","invented",child.document_id,child.file_name,
        child.source_path,[],1,1,"paragraph")
    ctx=SimpleNamespace(chunk_ids=["a"],document_id=child.document_id,file_name=child.file_name,
        source_path=child.source_path,parents=[p])
    context,sources,omissions=build_context(retrieval([child],[ctx]),6000)
    assert "invented" not in context and len(sources)==1 and omissions[0]["reason"]=="unverified hierarchy/source"


def test_budget_keeps_children_before_parent_and_never_truncates():
    children=[hit(),hit("b","BX456.pdf","Second child exact text")]
    just,sources,_=build_context(retrieval(children),6000)
    p=ParentEvidence("p1","P"*4000,children[0].document_id,children[0].file_name,children[0].source_path,[],1,1,"paragraph")
    ctx=SimpleNamespace(chunk_ids=["a"],document_id=p.document_id,file_name=p.file_name,source_path=p.source_path,parents=[p])
    context,sources,omissions=build_context(retrieval(children,[ctx]),len(just))
    assert context==just and len(sources)==2 and omissions
    assert all(c.text in context for c in children)


def test_child_budget_prefix_omits_lower_chunks_explicitly():
    one,_,_=build_context(retrieval([hit()]),6000)
    context,sources,omitted=build_context(retrieval([hit(),hit("b",text="B"*1000),hit("c",text="small")]),len(one))
    assert context==one and [s.chunk_id for s in sources]==["a"]
    assert {x["chunk_id"] for x in omitted}=={"b","c"}


def test_oversize_first_child_abstains_without_llm(deps):
    s,r,llm=deps;s.config=RAGV2Config(max_context_chars=10)
    result=s.run("Quel couple pour AX123 ?")
    assert not result.grounded and result.omissions and not result.sources
    llm.generate_grounded.assert_not_called()


def test_empty_retrieval(deps):
    s,r,llm=deps;r.retrieve.return_value.hits=[]
    result=s.run("Quel couple ?")
    assert not result.grounded and not result.sources
    llm.generate_grounded.assert_not_called()


@pytest.mark.parametrize("question,unknown",[("Quel couple pour ZZZZ999999 ?",["ZZZZ999999"]),
    ("Quel couple pour EBPK20??",[]),("Comparer AX123 et ZZZZ999999",["ZZZZ999999"])])
def test_unknown_malformed_and_partial_product_questions_abstain(deps,question,unknown):
    s,r,llm=deps;r.retrieve.return_value.query_analysis["unknown_identifiers"]=unknown
    result=s.run(question)
    assert not result.grounded and "reference" in " ".join(result.warnings).lower()
    llm.generate_grounded.assert_not_called()


def test_insufficient_llm_response(deps):
    s,r,llm=deps;llm.generate_grounded.return_value='{"status":"insufficient","claims":[]}'
    assert s.run("Quel prix pour AX123 ?").status=="insufficient"


@pytest.mark.parametrize("raw",["not JSON",'{}','{"status":"answered","claims":[]}',
    claims(quote="fabricated quote"),claims(sid="SOURCE 99"),claims(text="Couple maximal de 999 Nm."),
    claims(text="Tension de 86 V.",quote="Couple maximal : 86 Nm. Tension : 20 V."),
    claims(text="BX456 : couple maximal de 86 Nm."),
    '{"status":"insufficient","claims":[],"reasoning":"secret"}'])
def test_invalid_unsupported_or_malformed_output_fails_closed(deps,raw):
    s,r,llm=deps;llm.generate_grounded.return_value=raw
    result=s.run("Quel couple pour AX123 ?")
    assert not result.grounded and not result.claims and result.warnings
    assert "secret" not in result.answer


def test_llm_failure_returns_explicit_abstention(deps):
    s,r,llm=deps;llm.generate_grounded.side_effect=RuntimeError("offline")
    result=s.run("Quel couple pour AX123 ?")
    assert not result.grounded and any("RuntimeError" in w for w in result.warnings)


def test_multiple_documents_do_not_merge_citations(deps):
    s,r,llm=deps;r.retrieve.return_value=retrieval([hit(),hit("b","BX456.pdf","Couple maximal : 42 Nm.")])
    llm.generate_grounded.return_value=json.dumps(dict(status="answered",claims=[
        dict(text="86 Nm",quote="86 Nm",support_chunk_ids=["a"]),
        dict(text="42 Nm",quote="42 Nm",support_chunk_ids=["b"])]))
    result=s.run("Quels couples pour AX123 et BX456 ?")
    assert result.grounded and len(result.claims)==2 and result.sources[1].file_name=="BX456.pdf"


def test_reference_only_relevance_does_not_bypass_no_word_gate(deps):
    s,r,llm=deps;r.retrieve.return_value.hits[0].word_match=0
    assert not s.run("AX123 météo ?").grounded
    llm.generate_grounded.assert_not_called()


def test_provider_json_prompt_and_isolation():
    config=RAGV2Config(model="qwen2.5-coder:7b",base_url="http://test:11434")
    with patch("ollama.Client") as factory:
        factory.return_value.chat.return_value={"message":{"content":"{}"}}
        provider=GroundedQwenProvider(config)
        assert provider.generate_grounded("Question","SOURCE 1\n86 Nm")=="{}"
        args=factory.return_value.chat.call_args.kwargs
        assert args["model"]==config.model and args["format"]=="json"
        assert args["options"]["temperature"]==0
        assert "chain-of-thought" in args["messages"][0]["content"]
        assert "SOURCE 1\n86 Nm" in args["messages"][1]["content"]


def test_config_and_question_limits(deps):
    s,r,llm=deps
    with pytest.raises(ValueError):s.run(" " )
    with pytest.raises(ValueError):s.run("x"*1001)
    with pytest.raises(ValueError):RAGV2Config(model="other")
    r.retrieve.assert_not_called()
