import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.models.message import Message
from app.ai.api.routes import router
from app.ai.api.rag_v2_endpoint import RAGV2ChatAdapter, rag_v2_enabled
from app.ai.config import ai_settings
from app.ai.rag.hierarchical_rag_v2 import HierarchicalRAGV2, RAGV2Config
from app.ai.retrieval.retrieval_v2 import V2Child, V2Response, RetrievalV2
from app.ai.schemas.chat import ChatRequest, ChatResponse
from app.middleware.auth_middleware import get_current_user


@pytest.fixture(scope="module", autouse=True)
def protect_indexing_and_validated_components():
    import hashlib
    from scripts.evaluate_rag_v2 import protected
    before = protected()
    outputs = json.loads((Path(__file__).parents[2] / "docs/ai/rag_v2_answer_outputs.json").read_text(encoding="utf-8"))
    # Ownership is now a separately injected sidecar dependency. The unchanged
    # extractive validator remains pinned to its original validated digest.
    assert before["app/ai/rag/answer_validation_v2.py"] == outputs["validator_sha256"]
    yield
    assert protected() == before, "Index/checkpoint/validated source changed"


def make_pipeline():
    hit = V2Child(chunk_id="c1", document_id="doc1", file_name="AX123.pdf",
        source_path=r"C:\private\indexed\AX123.pdf", text="Couple maximal : 86 Nm.",
        score=1.0, parent_id=None, section_path=["SPECIFICATIONS"], page_start=1,
        page_end=2, block_type="paragraph", word_match=.5, candidate_sources=["lexical"])
    retriever = Mock()
    retriever.retrieve.return_value = V2Response([hit], [], "", [], [],
        dict(identifiers=["AX123"], unknown_identifiers=[], route_status="unique"))
    llm = Mock()
    llm.generate_grounded.return_value = json.dumps(dict(status="answered", claims=[
        dict(text=hit.text, support_chunk_ids=["c1"])]))
    service = HierarchicalRAGV2(retriever=retriever, llm=llm,
                              config=RAGV2Config(model="qwen2.5-coder:7b"))
    return service, retriever, llm


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("RAG_V2_ENABLED", "false")
    monkeypatch.setattr(ai_settings, "enabled", True)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    student = User(id=uuid4(), first_name="Test", last_name="Student", email="v2@example.test",
                   hashed_password="unused", role=UserRole.STUDENT, is_active=True)
    db.add(student); db.commit()
    legacy = Mock()
    legacy.run.return_value = ChatResponse(answer="unchanged legacy answer", sources=[dict(product_name="legacy")],
        conversation_id=str(uuid4()), created_at=datetime.now(timezone.utc))
    pipeline, retriever, llm = make_pipeline()
    adapter = RAGV2ChatAdapter(lambda: pipeline)
    v2_factory = Mock(return_value=adapter)
    monkeypatch.setattr("app.ai.api.routes.get_rag_service", lambda: legacy)
    monkeypatch.setattr("app.dependencies.chat.get_rag_v2_service", v2_factory)
    app = FastAPI(); app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: student
    client = TestClient(app)
    yield SimpleNamespace(client=client, app=app, db=db, student=student, legacy=legacy,
        adapter=adapter, pipeline=pipeline, retriever=retriever, llm=llm,
        v2_factory=v2_factory, monkeypatch=monkeypatch)
    db.close(); Base.metadata.drop_all(engine); engine.dispose()


def send(api, **kwargs):
    return api.client.post("/ai/chat", json=dict(question="Quel couple pour AX123 ?", **kwargs))


def enable(api):
    api.monkeypatch.setenv("RAG_V2_ENABLED", "true")


def test_flag_defaults_on_and_explicit_false_restores_legacy(monkeypatch):
    monkeypatch.delenv("RAG_V2_ENABLED", raising=False)
    assert rag_v2_enabled()
    for value in ["false", "flase", "", "1", "yes"]:
        monkeypatch.setenv("RAG_V2_ENABLED", value); assert not rag_v2_enabled()
    monkeypatch.setenv("RAG_V2_ENABLED", "true"); assert rag_v2_enabled()
    example = (Path(__file__).parents[1] / ".env.example").read_text()
    assert "RAG_V2_ENABLED=true" in example


def test_absent_flag_routes_student_chat_to_v2(api):
    api.monkeypatch.delenv("RAG_V2_ENABLED", raising=False)
    response = send(api)
    assert response.status_code == 200
    api.v2_factory.assert_called_once()
    api.legacy.run.assert_not_called()
    api.retriever.retrieve.assert_called_once()


def test_flag_off_preserves_legacy_output_and_history(api):
    response = send(api, top_k=7, messages=[dict(role="user", content="client history")])
    assert response.status_code == 200
    assert response.json()["answer"] == "unchanged legacy answer"
    assert response.json()["sources"] == [dict(product_name="legacy")]
    request = api.legacy.run.call_args.args[0]
    assert request.top_k == 7 and request.messages[0].content == "client history"
    assert api.legacy.run.call_args.kwargs["history"]
    api.v2_factory.assert_not_called()
    assert json.loads(api.db.query(Message).filter_by(role="assistant").one().sources) == response.json()["sources"]


def test_flag_on_invokes_validated_v2_and_keeps_response_schema(api):
    enable(api)
    response = send(api, top_k=20)
    assert response.status_code == 200
    assert set(response.json()) == {"answer", "sources", "conversation_id", "created_at"}
    assert "86 Nm" in response.json()["answer"] and "[SOURCE 1]" in response.json()["answer"]
    api.legacy.run.assert_not_called()
    api.retriever.retrieve.assert_called_once_with("Quel couple pour AX123 ?", top_k=3)
    assert api.pipeline.config.top_k == 3
    ChatResponse.model_validate(response.json())


def test_v2_does_not_change_other_roles(api):
    enable(api); api.student.role = UserRole.INSTRUCTOR
    assert send(api).json()["answer"] == "unchanged legacy answer"
    api.v2_factory.assert_not_called()


def test_ai_enabled_gate_and_auth_are_retained(api):
    enable(api); api.monkeypatch.setattr(ai_settings, "enabled", False)
    assert send(api).status_code == 503
    api.monkeypatch.setattr(ai_settings, "enabled", True)
    api.app.dependency_overrides.pop(get_current_user)
    assert send(api).status_code == 401
    api.llm.generate_grounded.assert_not_called()


def test_safe_abstention_saved_without_fallback(api):
    enable(api); api.llm.generate_grounded.return_value = '{"status":"insufficient","claims":[]}'
    response = send(api)
    assert response.status_code == 200 and response.json()["sources"] == []
    assert "insuffisantes" in response.json()["answer"]
    stored = json.loads(api.db.query(Message).filter_by(role="assistant").one().sources)
    assert stored["provenance"]["status"] == "insufficient"
    assert stored["provenance"]["abstention_reason"] == "insufficient_or_ambiguous_evidence"
    api.legacy.run.assert_not_called()


def test_invalid_support_is_rejected_by_unchanged_validator(api):
    enable(api)
    api.llm.generate_grounded.return_value = json.dumps(dict(status="answered", claims=[
        dict(text="Couple maximal : 86 Nm.", support_chunk_ids=["unlisted"])]))
    response = send(api)
    assert response.status_code == 200 and response.json()["sources"] == []
    stored = json.loads(api.db.query(Message).filter_by(role="assistant").one().sources)
    assert stored["provenance"]["abstention_reason"] == "support_not_allowed"
    assert stored["provenance"]["citations"] == []
    api.legacy.run.assert_not_called()


@pytest.mark.parametrize("raw", ["not JSON", "{}", '{"status":"answered","claims":[]}'])
def test_malformed_model_output_is_technical_502(api, raw):
    enable(api); api.llm.generate_grounded.return_value = raw
    response = send(api)
    assert response.status_code == 502 and "temporarily unavailable" in response.json()["detail"]
    assert not api.db.query(Message).filter_by(role="assistant").all()
    assert api.db.query(Message).filter_by(role="user").count() == 1
    api.legacy.run.assert_not_called()


@pytest.mark.parametrize("stage", ["retrieval", "generation", "initialization"])
def test_unavailable_dependencies_are_technical_without_private_errors(api, stage):
    enable(api)
    error = ConnectionError("private conversation SECRET C:\\internal\\storage")
    if stage == "retrieval":
        api.retriever.retrieve.side_effect = error
    elif stage == "generation":
        api.llm.generate_grounded.side_effect = error
    else:
        api.adapter._factory = Mock(side_effect=error)
    response = send(api)
    assert response.status_code == 502
    assert "SECRET" not in response.text and "internal" not in response.text
    assert api.db.query(Message).filter_by(role="assistant").count() == 0
    api.legacy.run.assert_not_called()


def test_provenance_persisted_but_paths_not_exposed_on_chat_or_history(api):
    enable(api); response = send(api)
    source = response.json()["sources"][0]
    assert source["chunk_id"] == source["support_chunk_id"] == "c1"
    assert source["document_id"] == "doc1" and source["file_name"] == "AX123.pdf"
    assert "SOURCE 1" in source["product_name"] and "score" not in source
    assert (source["page_start"], source["page_end"], source["source_id"]) == (1, 2, "SOURCE 1")
    stored = json.loads(api.db.query(Message).filter_by(role="assistant").one().sources)
    assert stored["provenance"]["citations"][0]["support_chunk_ids"] == ["c1"]
    assert stored["provenance"]["sources"][0]["document_id"] == "doc1"
    assert stored["provenance"]["request_id"]
    history = api.client.get(f"/ai/conversations/{response.json()['conversation_id']}/messages")
    assert history.status_code == 200 and history.json()[1]["sources"] == response.json()["sources"]
    assert all(s not in response.text + history.text for s in ["source_path", "private", "provenance", "telemetry"])


def test_encoded_filename_paths_are_not_exposed(api):
    enable(api)
    api.retriever.retrieve.return_value.hits[0].file_name = "C%3A%5Cprivate%5CAX123%20Data.pdf"
    response = send(api)
    assert response.status_code == 200
    assert response.json()["sources"][0]["file_name"] == "AX123 Data.pdf"
    assert "private" not in response.text and "%5C" not in response.text


def test_existing_conversation_and_flag_changes_preserve_messages(api):
    first = send(api); cid = first.json()["conversation_id"]
    enable(api); second = send(api, conversation_id=cid)
    assert second.json()["conversation_id"] == cid
    history = api.client.get(f"/ai/conversations/{cid}/messages").json()
    assert len(history) == 4 and history[1]["sources"] == first.json()["sources"]
    assert history[3]["sources"] == second.json()["sources"]
    api.student.id = uuid4()  # Different authenticated owner cannot reuse/delete/read.
    assert send(api, conversation_id=cid).status_code == 404
    assert api.client.get(f"/ai/conversations/{cid}/messages").status_code == 404
    assert api.client.delete(f"/ai/conversations/{cid}").status_code == 404


@pytest.mark.parametrize('v2_status', ['answered', 'insufficient'])
def test_release_flag_roundtrip_and_persisted_mixed_history_new_session(api, v2_status):
    first = send(api)
    cid = first.json()['conversation_id']
    api.v2_factory.assert_not_called()
    assert api.legacy.run.call_count == 1
    enable(api)
    if v2_status == 'insufficient':
        api.llm.generate_grounded.return_value = '{"status":"insufficient","claims":[]}'
    second = send(api, conversation_id=cid)
    assert second.status_code == 200
    api.v2_factory.assert_called_once()
    assert api.legacy.run.call_count == 1
    api.monkeypatch.setenv('RAG_V2_ENABLED', 'false')
    third = send(api, conversation_id=cid)
    assert third.json()['answer'] == first.json()['answer']
    assert api.legacy.run.call_count == 2
    api.retriever.retrieve.assert_called_once()
    stored = [json.loads(m.sources) if m.sources else None for m in
              api.db.query(Message).filter_by(role='assistant').order_by(Message.created_at).all()]
    assert isinstance(stored[0], list) and stored[1]['format'] == 'rag_v2' and isinstance(stored[2], list)
    assert stored[1]['provenance']['status'] == v2_status
    # Read committed history from a different SQLAlchemy session, as after request restart.
    bind = api.db.get_bind()
    student_id = api.student.id
    api.db.close()
    fresh = sessionmaker(bind=bind)()
    api.app.dependency_overrides[get_db] = lambda: fresh
    api.app.dependency_overrides[get_current_user] = lambda: fresh.get(User, student_id)
    try:
        history = api.client.get(f'/ai/conversations/{cid}/messages')
        assert history.status_code == 200 and len(history.json()) == 6
        for index, response in zip((1, 3, 5), (first, second, third)):
            assert history.json()[index]['content'] == response.json()['answer']
            assert history.json()[index]['sources'] == response.json()['sources']
        assert all(term not in history.text for term in ('provenance', 'source_path', 'telemetry', 'private'))
    finally:
        fresh.close()


def test_observability_is_complete_without_conversation_text(api, caplog):
    enable(api)
    with caplog.at_level(logging.INFO):
        send(api)
    event = next(r.message for r in caplog.records if r.message.startswith("rag_v2_request "))
    metrics = json.loads(event.removeprefix("rag_v2_request "))
    assert UUID(metrics["request_id"])
    assert metrics["outcome"] == "answered" and metrics["accepted_claims"] == 1
    assert metrics["retrieved_sources"] == metrics["supplied_sources"] == 1
    for stage in ["retrieval", "generation", "validation", "total"]:
        assert metrics[stage + "_duration_ms"] > 0
    assert "AX123" not in event and "86 Nm" not in event and "question" not in event


def test_existing_profiler_restored_after_success_and_failure():
    pipeline, retriever, _ = make_pipeline()
    adapter = RAGV2ChatAdapter(lambda: pipeline)
    original = sys.getprofile()
    callback = lambda *args: None
    try:
        sys.setprofile(callback)
        adapter.run(ChatRequest(question="AX123 couple ?"))
        assert sys.getprofile() is callback
        retriever.retrieve.side_effect = ConnectionError("offline")
        with pytest.raises(RuntimeError): adapter.run(ChatRequest(question="AX123 couple ?"))
        assert sys.getprofile() is callback
    finally:
        sys.setprofile(original)


def test_concurrent_requests_have_independent_observability():
    from concurrent.futures import ThreadPoolExecutor
    pipeline, _, _ = make_pipeline()
    adapter = RAGV2ChatAdapter(lambda: pipeline)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: adapter.run(ChatRequest(question="AX123 couple ?")), range(4)))
    assert len({r._rag_v2_provenance["request_id"] for r in results}) == 4
    assert all(r._rag_v2_provenance["telemetry"]["accepted_claims"] == 1 for r in results)


@pytest.mark.parametrize('workers', [2, 4, 8])
def test_release_concurrent_endpoint_requests_persist_independent_conversations(api, tmp_path, workers):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from fastapi import Depends
    engine = create_engine(f'sqlite:///{tmp_path / "release.db"}', connect_args={'check_same_thread': False})
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    student_id = uuid4()
    with sessions() as seed:
        seed.add(User(id=student_id, first_name='Release', last_name='Student', email='release@example.test',
                      hashed_password='unused', role=UserRole.STUDENT, is_active=True))
        seed.commit()
    def db_for_request():
        with sessions() as db: yield db
    def authenticated_student(db=Depends(get_db)):
        return db.get(User, student_id)
    api.app.dependency_overrides[get_db] = db_for_request
    api.app.dependency_overrides[get_current_user] = authenticated_student
    enable(api)
    barrier = Barrier(workers)
    def send_concurrent(_):
        barrier.wait(timeout=10)
        return send(api)
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            responses = list(pool.map(send_concurrent, range(workers)))
        assert all(r.status_code == 200 for r in responses)
        assert len({r.json()['conversation_id'] for r in responses}) == workers
        assert len({r.json()['answer'] for r in responses}) == 1
        assert all(r.json()['sources'] == responses[0].json()['sources'] for r in responses)
        with sessions() as db:
            assistants = db.query(Message).filter_by(role='assistant').all()
            assert len(assistants) == workers
            audits = [json.loads(m.sources)['provenance'] for m in assistants]
            assert len({a['request_id'] for a in audits}) == workers
            assert all(a['citations'][0]['support_chunk_ids'] == ['c1'] for a in audits)
        for response in responses:
            history = api.client.get(f"/ai/conversations/{response.json()['conversation_id']}/messages")
            assert history.status_code == 200 and len(history.json()) == 2
        api.legacy.run.assert_not_called()
        api.retriever.retrieve.assert_has_calls([call('Quel couple pour AX123 ?', top_k=3)] * workers)
    finally:
        engine.dispose()


def test_live_retrieval_code_uses_read_only_qdrant_and_keeps_fixed_counts():
    from qdrant_client.http import models
    row = dict(chunk_id="c1", document_id="doc1", file_name="AX123.pdf", source_path="raw/AX123.pdf",
               text="Couple maximal : 86 Nm.", parent_id=None, section_path=[], page_start=1,
               page_end=2, block_type="paragraph")
    client = Mock(spec=["get_collection", "scroll", "query_points"])
    client.get_collection.return_value = SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(
        vectors=models.VectorParams(size=768, distance=models.Distance.COSINE))))
    client.scroll.return_value = ([SimpleNamespace(payload=row)], None)
    client.query_points.return_value = SimpleNamespace(points=[SimpleNamespace(payload=row, score=.8)])
    embedding = Mock(dimension=768); embedding.embed_single.return_value = [1.] + [0.] * 767
    resolver = Mock(); resolver.resolve.return_value = {}
    pipeline, _, _ = make_pipeline()
    pipeline.retriever = RetrievalV2(client=client, embeddings=embedding, context_resolver=resolver)
    response = RAGV2ChatAdapter(lambda: pipeline).run(ChatRequest(question="Quel couple AX123 ?", top_k=999))
    assert response.sources[0]["chunk_id"] == "c1"
    assert {c[0] for c in client.method_calls} <= {"get_collection", "scroll", "query_points"}
    assert all(c.kwargs.get("collection_name", c.args[0] if c.args else None) == "buildlearn_products_hierarchical_v1" for c in client.method_calls)
    assert client.query_points.call_args.kwargs["limit"] == 100
    assert client.query_points.call_args.kwargs["score_threshold"] == 0.0
