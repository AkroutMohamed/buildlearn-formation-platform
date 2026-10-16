"""Read-only cold/warm profiling and exact shadow replay; never enables V2."""
import argparse
from collections import defaultdict
import hashlib
import json
import statistics
from pathlib import Path
import sys
from time import perf_counter

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
import app.config
from app.ai.api.rag_v2_endpoint import RAGV2ChatAdapter, rag_v2_enabled
from app.ai.schemas.chat import ChatRequest
from app.ai.config import ai_settings
from qdrant_client import QdrantClient
from scripts.shadow_rag_v2_chat import QUERIES, collection_digest
from scripts.evaluate_rag_v2 import protected


def stage(frame):
    module = frame.f_globals.get('__name__', '')
    name = frame.f_code.co_name
    if module == 'app.ai.api.rag_v2_endpoint':
        if name == '_get_service': return 'adapter_initialization'
        if name == 'public_sources': return 'response_mapping'
    if module == 'app.ai.retrieval.retrieval_v2':
        if name == 'refresh': return 'snapshot_loading'
        if name in ('rank', 'analyze'): return 'lexical_retrieval'
        if name == 'retrieve': return 'candidate_merge_rerank'
    if module == 'app.ai.retrieval.hierarchical_retriever':
        if name == '_embedding_service': return 'query_embedding'
        if name == '_contexts': return 'parent_context'
        if name == 'retrieve': return 'dense_qdrant'
    if module == 'app.ai.embeddings.service' and name == 'embed_single': return 'query_embedding'
    if module == 'app.ai.retrieval.source_context' and name == 'resolve': return 'parent_context'
    if module == 'app.ai.rag.hierarchical_rag_v2':
        if name == 'build_context': return 'parent_context'
        if name == 'generate_grounded': return 'qwen_generation'
    if module == 'app.ai.rag.answer_validation_v2' and name == 'validate_claims': return 'validation'
    return None


class Profiler:
    """Exclusive wall times: nested stages subtract from their enclosing stage."""
    def __init__(self):
        self.times = defaultdict(float)
        self.stack = []
    def __call__(self, frame, event, arg):
        key = stage(frame)
        if key is None: return
        if event == 'call': self.stack.append([id(frame), key, perf_counter(), 0.0])
        elif event == 'return' and self.stack and self.stack[-1][0] == id(frame):
            _, key, started, nested = self.stack.pop()
            elapsed = perf_counter() - started
            self.times[key] += (elapsed - nested) * 1000
            if self.stack: self.stack[-1][3] += elapsed


def signature(record):
    return dict(status=record['status'], answer=record['answer'], citations=record['citations'], sources=record['sources'])


def summarize(records):
    keys = sorted({k for r in records for k in r['stages_ms']})
    summary = {}
    for key in keys:
        warm = sorted(r['stages_ms'].get(key, 0.0) for r in records if not r['cold'])
        summary[key] = dict(cold_ms=records[0]['stages_ms'].get(key, 0.0),
                            warm_median_ms=statistics.median(warm),
                            warm_p90_ms=warm[8], warm_max_ms=max(warm))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--compare')
    parser.add_argument('--no-profile', action='store_true', help='Existing telemetry only; measures profiling overhead')
    args = parser.parse_args()
    assert not rag_v2_enabled()
    before = protected()
    runtime_hashes = {name: hashlib.sha256((BACKEND / 'app/ai/api' / name).read_bytes()).hexdigest()
                      for name in ('rag_v2_endpoint.py', 'rag_v2_runtime.py') if (BACKEND / 'app/ai/api' / name).exists()}
    client = QdrantClient(url=ai_settings.qdrant_url.replace('://localhost:', '://127.0.0.1:'))
    integrity_before = {name: collection_digest(client, name) for name in
                        ('buildlearn_products', 'buildlearn_products_hierarchical_v1')}
    adapter = RAGV2ChatAdapter()
    output = dict(protocol='one cold S01, followed by ten warm S01-S10; exclusive profiled wall time; no tuning',
                  flag_enabled=False, integrity_before=integrity_before, records=[], runtime_hashes=runtime_hashes,
                  detailed_profiling=not args.no_profile)
    baseline = json.loads(Path(args.compare).read_text(encoding='utf-8')) if args.compare else None
    shadow = json.loads((BACKEND.parent / 'docs/ai/rag_v2_endpoint_shadow.json').read_text(encoding='utf-8'))
    for index, (qid, question, _) in enumerate([QUERIES[0]] + QUERIES):
        profiler = Profiler()
        started = perf_counter()
        previous = sys.getprofile()
        if not args.no_profile: sys.setprofile(profiler)
        try:
            response = adapter.run(ChatRequest(question=question), history=[])
        finally:
            sys.setprofile(previous)
        elapsed = (perf_counter() - started) * 1000
        audit = response._rag_v2_provenance
        times = dict(profiler.times) if not args.no_profile else {
            'retrieval': audit['telemetry']['retrieval_duration_ms'],
            'qwen_generation': audit['telemetry']['generation_duration_ms'],
            'validation': audit['telemetry']['validation_duration_ms']}
        times['other_mapping_telemetry'] = elapsed - sum(times.values())
        times['total'] = elapsed
        record = dict(id=qid, cold=index == 0, stages_ms=times, telemetry=audit['telemetry'],
                      status=audit['status'], answer=response.answer,
                      citations=audit['citations'], sources=response.sources,
                      internal_sources=audit['sources'])
        expected = next(r for r in shadow['records'] if r['id'] == qid)['v2']
        assert record['status'] == expected['status'], qid
        assert record['citations'] == expected['provenance']['citations'], qid
        assert record['sources'] == expected['response']['sources'], qid
        assert record['answer'] == expected['response']['answer'], qid
        assert audit['sources'] == expected['provenance']['sources'], qid
        if baseline:
            assert signature(record) == signature(baseline['records'][index]), qid
        output['records'].append(record)
        Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(dict(id=qid, cold=index == 0, status=record['status'], stages_ms=times)), flush=True)
    output['integrity_after'] = {name: collection_digest(client, name) for name in integrity_before}
    assert output['integrity_after'] == integrity_before
    assert before == protected() and not rag_v2_enabled()
    assert all(hashlib.sha256((BACKEND / 'app/ai/api' / name).read_bytes()).hexdigest() == digest
               for name, digest in runtime_hashes.items())
    output['integrity'] = dict(protected_files_unchanged=True, collections_unchanged=True,
                               exact_shadow_replay=True, flag_disabled=True)
    output['summary_ms'] = summarize(output['records'])
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(output['summary_ms'], indent=2), flush=True)
    client.close()


if __name__ == '__main__': main()
