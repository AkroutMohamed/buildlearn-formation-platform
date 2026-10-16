from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import asdict
from threading import Barrier
from time import sleep
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from qdrant_client.http import models
from app.ai.api.rag_v2_runtime import RuntimeRetrievalV2, local_transport_url
from app.ai.api.rag_v2_endpoint import RAGV2ChatAdapter, rag_v2_enabled
from app.ai.retrieval.retrieval_v2 import RetrievalV2
from app.ai.retrieval.hierarchical_retriever import COLLECTION


def dependencies(text='  Puissance nominale : 750 W.\nExact original.  '):
    row = dict(chunk_id='c1', document_id='doc1', file_name='AX123%20Data.pdf',
        source_path='private/AX123.pdf', text=text, parent_id=None, section_path=['TECHNICAL'],
        page_start=1, page_end=2, block_type='paragraph', parent_id_path=[])
    client = Mock(spec=['get_collection', 'scroll', 'query_points'])
    client.get_collection.return_value = SimpleNamespace(config=SimpleNamespace(params=SimpleNamespace(
        vectors=models.VectorParams(size=768, distance=models.Distance.COSINE))))
    client.scroll.return_value = ([SimpleNamespace(payload=row)], None)
    client.query_points.return_value = SimpleNamespace(points=[SimpleNamespace(payload=row, score=.8)])
    embedding = Mock(dimension=768)
    embedding.embed_single.return_value = [1.] + [0.] * 767
    resolver = Mock(); resolver.resolve.return_value = {}
    return dict(client=client, embeddings=embedding, context_resolver=resolver), row


@pytest.mark.parametrize('original,expected', [
    ('http://localhost:6333', 'http://127.0.0.1:6333'),
    ('http://localhost:11434/base?x=1', 'http://127.0.0.1:11434/base?x=1'),
    ('https://localhost:6333', 'https://localhost:6333'),
    ('http://remote:6333', 'http://remote:6333'),
    ('http://localhost.example:6333', 'http://localhost.example:6333'),
    ('http://user:secret@localhost:6333', 'http://user:secret@localhost:6333'),
    ('http://[::1]:6333', 'http://[::1]:6333'),
])
def test_transport_address_only(original, expected):
    assert local_transport_url(original) == expected


def test_non_loopback_localhost_or_dns_failure_preserves_address(monkeypatch):
    lookup = Mock(return_value=[(None, None, None, None, ('192.0.2.1', 6333))])
    monkeypatch.setattr('app.ai.api.rag_v2_runtime.socket.getaddrinfo', lookup)
    assert local_transport_url('http://localhost:6333') == 'http://localhost:6333'
    lookup.side_effect = OSError('DNS failure')
    assert local_transport_url('http://localhost:6333') == 'http://localhost:6333'


def test_parents_are_reverified_and_never_cached():
    from app.ai.retrieval.hierarchical_models import ParentEvidence, SourceResolution
    deps, row = dependencies(); row['parent_id'] = 'p1'; row['parent_id_path'] = ['p1']
    parent = ParentEvidence('p1', 'Exact parent body.', row['document_id'], row['file_name'],
                            row['source_path'], ['TECHNICAL'], 1, 2, 'paragraph')
    deps['context_resolver'].resolve.return_value = {
        (row['document_id'], row['source_path'], row['chunk_id']): SourceResolution(['p1'], [parent])}
    original = RetrievalV2(**deps); optimized = RuntimeRetrievalV2(**deps)
    assert asdict(original.retrieve('AX123 puissance')) == asdict(optimized.retrieve('AX123 puissance'))
    deps['context_resolver'].resolve.side_effect = ValueError('Extraction changed')
    changed = optimized.retrieve('AX123 puissance')
    assert changed.warnings and all(not ctx.parents for ctx in changed.contexts)
    assert changed.hits[0].text == row['text']


def test_exact_determinism_and_no_result_cache():
    deps, row = dependencies()
    original = RetrievalV2(**deps)
    optimized = RuntimeRetrievalV2(**deps)
    expected = asdict(original.retrieve('Quelle puissance pour AX123 ?', top_k=3))
    for _ in range(2):
        actual = optimized.retrieve('Quelle puissance pour AX123 ?', top_k=3)
        assert asdict(actual) == expected
        assert actual.hits[0].text == row['text']
        assert actual.hits[0].payload_metadata == row
    assert deps['embeddings'].embed_single.call_count == 3
    assert deps['client'].query_points.call_count == 3
    assert deps['context_resolver'].resolve.call_count == 3
    assert deps['client'].scroll.call_count == 2  # once for each independent retriever
    assert all(c[0] in {'scroll', 'get_collection', 'query_points'} for c in deps['client'].method_calls)
    assert deps['client'].query_points.call_args.kwargs['collection_name'] == COLLECTION
    assert deps['client'].query_points.call_args.kwargs['limit'] == 100
    assert deps['client'].query_points.call_args.kwargs['score_threshold'] == 0.0


def test_concurrent_cold_initialization_and_parallel_warm_requests():
    deps, _ = dependencies()
    retriever = RuntimeRetrievalV2(**deps)
    response = deps['client'].query_points.return_value
    barrier = Barrier(4)
    def query(**kwargs):
        barrier.wait(timeout=5)  # would fail if entire requests were serialized
        return response
    deps['client'].query_points.side_effect = query
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: asdict(retriever.retrieve('Puissance AX123')), range(4)))
    assert all(r == results[0] for r in results)
    deps['client'].scroll.assert_called_once()
    assert deps['embeddings'].embed_single.call_count == 4


def test_lazy_embedding_initializes_once_concurrently():
    deps, _ = dependencies()
    embedding = deps.pop('embeddings')
    retriever = RuntimeRetrievalV2(**deps)
    def initialize():
        sleep(.02)
        retriever._v1._embeddings = embedding
        return embedding
    retriever._v1._embedding_service = Mock(side_effect=initialize)
    # Subsequent calls from the original dense path access the same initialized object.
    def service():
        if retriever._v1._embeddings is None: return initialize()
        return retriever._v1._embeddings
    retriever._v1._embedding_service.side_effect = service
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: retriever.retrieve('AX123 puissance'), range(4)))
    assert all(r.hits[0].chunk_id == 'c1' for r in results)
    assert retriever._v1._embedding_service.call_count == 5  # one init plus four dense calls
    assert embedding.embed_single.call_count == 4


def test_client_identity_invalidates_snapshot():
    deps, _ = dependencies()
    retriever = RuntimeRetrievalV2(**deps)
    retriever.retrieve('AX123 puissance')
    changed, row = dependencies('Puissance nominale : 900 W.')
    retriever.client = changed['client']
    result = retriever.retrieve('AX123 puissance')
    assert result.hits[0].text == row['text']
    changed['client'].scroll.assert_called_once()
    changed['client'].query_points.assert_called_once()


def test_digest_mismatch_fails_closed_and_evicts_snapshot():
    deps, row = dependencies()
    retriever = RuntimeRetrievalV2(**deps)
    retriever.retrieve('AX123 puissance')
    digest = retriever._index.digest
    changed = deepcopy(row); changed['text'] = 'Puissance nominale : 900 W.'
    deps['client'].query_points.return_value.points[0].payload = changed
    with pytest.raises(ValueError, match='refresh required'):
        retriever.retrieve('AX123 puissance')
    assert retriever._index is None
    deps['client'].scroll.return_value = ([SimpleNamespace(payload=changed)], None)
    result = retriever.retrieve('AX123 puissance')
    assert result.hits[0].text == changed['text']
    assert retriever._index.digest != digest


def test_failed_refresh_cannot_reuse_old_snapshot():
    deps, _ = dependencies()
    retriever = RuntimeRetrievalV2(**deps); retriever.refresh()
    deps['client'].scroll.side_effect = RuntimeError('unavailable')
    with pytest.raises(RuntimeError): retriever.refresh()
    assert retriever._index is None
    with pytest.raises(RuntimeError): retriever.retrieve('AX123')
    deps['client'].query_points.assert_not_called()


def test_explicit_refresh_changes_digest_and_does_not_mutate_returns():
    deps, _ = dependencies(); retriever = RuntimeRetrievalV2(**deps)
    first = retriever.retrieve('AX123 puissance')
    first.hits[0].section_path.append('caller mutation')
    digest = retriever.refresh()
    assert retriever._index.digest == digest
    assert retriever.retrieve('AX123 puissance').hits[0].section_path == ['TECHNICAL']


def test_invalid_request_does_not_load_snapshot():
    deps, _ = dependencies(); retriever = RuntimeRetrievalV2(**deps)
    for kwargs in ({'query': ''}, {'query': 'AX123', 'top_k': 0}, {'query': 'AX123', 'mode': 'other'}):
        with pytest.raises(ValueError): retriever.retrieve(**kwargs)
    deps['client'].scroll.assert_not_called()


def test_adapter_factory_single_initialization_and_default_on(monkeypatch):
    monkeypatch.delenv('RAG_V2_ENABLED', raising=False)
    assert rag_v2_enabled()
    factory = Mock(return_value=object()); adapter = RAGV2ChatAdapter(factory)
    with ThreadPoolExecutor(max_workers=4) as pool:
        services = list(pool.map(lambda _: adapter._get_service(), range(12)))
    assert all(s is services[0] for s in services)
    factory.assert_called_once()
