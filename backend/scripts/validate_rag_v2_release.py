"""Frozen live release acceptance, concurrent cold/warm batches and process restarts."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys
from threading import Barrier, Lock, local
from time import perf_counter

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
import app.config
from app.ai.api.rag_v2_endpoint import RAGV2ChatAdapter, _create_service, rag_v2_enabled
from app.ai.rag.hierarchical_rag_v2 import build_context
from app.ai.rag.answer_validation_v2 import support_id
from app.ai.schemas.chat import ChatRequest
from qdrant_client import QdrantClient
from scripts.evaluate_rag_v2 import protected
from scripts.shadow_rag_v2_chat import collection_digest

FIXTURE = BACKEND / 'tests/ai/fixtures/rag_v2_release_acceptance.json'
OUTPUT = BACKEND.parent / 'docs/ai/rag_v2_release_outputs.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def files():
    result = protected()
    for path in (BACKEND / 'app/ai/api').glob('*.py'):
        result[str(path.relative_to(BACKEND))] = sha(path)
    result['tests/ai/fixtures/rag_v2_release_acceptance.json'] = sha(FIXTURE)
    return result


class ReadOnlyClient:
    def __init__(self, client, counts, lock): self.client, self.counts, self.lock = client, counts, lock
    def __getattr__(self, name):
        if name not in ('get_collection', 'scroll', 'query_points'):
            raise RuntimeError('Release harness prohibits Qdrant operation: ' + name)
        def call(*args, **kwargs):
            collection = kwargs.get('collection_name', args[0] if args else None)
            if collection != 'buildlearn_products_hierarchical_v1': raise RuntimeError('Collection isolation failure')
            with self.lock: self.counts[name] = self.counts.get(name, 0) + 1
            try: return getattr(self.client, name)(*args, **kwargs)
            except Exception:
                with self.lock: self.counts['qdrant_errors'] = self.counts.get('qdrant_errors', 0) + 1
                raise
        return call


class ObservedAdapter:
    def __init__(self):
        self.trace = local()
        self.lock = Lock()
        self.counts = dict(factory=0, snapshot_refresh=0, qdrant_errors=0, provider_errors=0)
        self.adapter = RAGV2ChatAdapter(self.factory)
    def factory(self):
        with self.lock: self.counts['factory'] += 1
        service = _create_service()
        retriever = service.retriever
        retriever.client = ReadOnlyClient(retriever.client, self.counts, self.lock)
        refresh = retriever.refresh
        def counted_refresh():
            with self.lock: self.counts['snapshot_refresh'] += 1
            return refresh()
        retriever.refresh = counted_refresh
        retrieve, generate = retriever.retrieve, service.llm.generate_grounded
        def observed_retrieve(*args, **kwargs):
            result = retrieve(*args, **kwargs)
            self.trace.retrieval = result
            return result
        def observed_generate(*args, **kwargs):
            try:
                raw = generate(*args, **kwargs)
            except Exception:
                with self.lock: self.counts['provider_errors'] += 1
                raise
            try:
                parsed = json.loads(raw)
                self.trace.model_output = {k: parsed[k] for k in ('status', 'claims') if k in parsed}
            except (ValueError, TypeError): self.trace.model_output = dict(malformed=True)
            return raw
        retriever.retrieve = observed_retrieve
        service.llm.generate_grounded = observed_generate
        return service
    def call(self, case, barrier=None):
        self.trace.retrieval, self.trace.model_output = None, None
        if barrier: barrier.wait(timeout=30)
        started = perf_counter()
        try:
            response = self.adapter.run(ChatRequest(question=case['query']), history=[])
            audit = response._rag_v2_provenance
            result = dict(id=case['id'], status=audit['status'], response=response.model_dump(mode='json'),
                          audit=audit, model_output=self.trace.model_output)
            retrieval = self.trace.retrieval
            _, sources, omissions = build_context(retrieval, self.adapter._service.config.max_context_chars)
            result['selected_sources'] = [asdict(s) for s in sources]
            result['retrieved_hits'] = [asdict(h) for h in retrieval.hits]
            result['warnings'] = retrieval.warnings
            result['omissions'] = omissions
            allowed = {support_id(s): s for s in sources}
            citation_checks, support_checks = [], []
            for claim in audit['citations']:
                ids = claim['support_chunk_ids']
                valid_id = len(ids) == 1 and ids[0] in allowed
                support_checks.append(valid_id)
                source = allowed[ids[0]] if valid_id else None
                citation_checks.append(bool(source and claim['source_id'] == source.source_id and
                                            claim['quote'] == claim['text'] and claim['quote'] in source.text))
            result['checks'] = dict(claim_count=len(audit['citations']),
                                   valid_supports=sum(support_checks), valid_citations=sum(citation_checks))
        except Exception as exc:
            result = dict(id=case['id'], status='technical_failure', error_type=type(exc).__name__)
        result['latency_seconds'] = perf_counter() - started
        return result


def signature(record):
    if record['status'] == 'technical_failure': return dict(status=record['status'])
    return dict(status=record['status'], answer=record['response']['answer'],
                sources=record['response']['sources'], citations=record['audit']['citations'])


def distribution(records):
    values = sorted(r['latency_seconds'] for r in records)
    return dict(n=len(values), median=statistics.median(values),
                p90=values[math.ceil(.9 * len(values)) - 1], max=max(values), min=min(values))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--restart-child', action='store_true')
    args = parser.parse_args()
    assert not rag_v2_enabled()
    frozen = json.loads(FIXTURE.read_text(encoding='utf-8'))
    if args.restart_child:
        adapter = ObservedAdapter()
        result = dict(pid=__import__('os').getpid(), cold=adapter.call(frozen['labels'][0]),
                      warm=adapter.call(frozen['labels'][0]), counts=adapter.counts)
        print(json.dumps(result, ensure_ascii=True))
        return
    if OUTPUT.exists(): raise RuntimeError('Release outputs already exist; do not overwrite acceptance history')
    before = files()
    assert all(before[k] == v for k, v in frozen['freeze']['protected'].items())
    client = QdrantClient(url='http://127.0.0.1:6333')
    collections = ('buildlearn_products', 'buildlearn_products_hierarchical_v1')
    initial = {name: collection_digest(client, name) for name in collections}
    output = dict(utc=datetime.now(timezone.utc).isoformat(), frozen_set_sha256=sha(FIXTURE),
                  protected_before=before, collections_before=initial, acceptance=[], concurrency=[], restarts=[])
    def save(): OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    adapter = ObservedAdapter()
    for case in frozen['labels']:
        record = adapter.call(case)
        output['acceptance'].append(record)
        save()
        print(json.dumps(dict(id=case['id'], status=record['status'], seconds=round(record['latency_seconds'], 3))), flush=True)
    output['acceptance_counts'] = adapter.counts
    output['cold_seconds'] = output['acceptance'][0]['latency_seconds']
    output['warm_latency'] = distribution(output['acceptance'][1:])
    by_id = {r['id']: r for r in output['acceptance']}
    cases = {q['id']: q for q in frozen['labels']}
    batch_ids = ['A01', 'A02', 'A07', 'N10']
    for count in (2, 4, 8):
        concurrent = ObservedAdapter()
        for phase in ('cold', 'warm'):
            barrier = Barrier(count)
            ids = [batch_ids[i % len(batch_ids)] for i in range(count)]
            with ThreadPoolExecutor(max_workers=count) as pool:
                pending = [pool.submit(concurrent.call, cases[qid], barrier) for qid in ids]
                results = [job.result() for job in pending]
            drift = [r['id'] for r in results if signature(r) != signature(by_id[r['id']])]
            output['concurrency'].append(dict(requests=count, phase=phase, results=results,
                latency=distribution(results), counts=dict(concurrent.counts), drift=drift,
                success=sum(r['status'] != 'technical_failure' for r in results)))
            save()
            print(json.dumps(dict(concurrency=count, phase=phase, latency=distribution(results),
                                  counts=concurrent.counts, drift=drift)), flush=True)
    for _ in range(2):
        run = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--restart-child'],
                             cwd=BACKEND, capture_output=True, text=True, encoding='utf-8', timeout=240)
        if run.returncode: raise RuntimeError('Restart child failed: ' + run.stderr[-1000:])
        record = json.loads(run.stdout)
        record['drift'] = any(signature(record[k]) != signature(by_id['A01']) for k in ('cold', 'warm'))
        output['restarts'].append(record)
        save()
        print(json.dumps(dict(restart_pid=record['pid'], cold=record['cold']['latency_seconds'],
                              warm=record['warm']['latency_seconds'], drift=record['drift'])), flush=True)
    output['collections_after'] = {name: collection_digest(client, name) for name in collections}
    assert output['collections_after'] == initial and files() == before and not rag_v2_enabled()
    output['integrity'] = dict(collections_unchanged=True, protected_files_unchanged=True,
                               labels_unchanged=True, flag_disabled=True, qdrant_operations_read_only=True)
    output['complete'] = True
    save()
    client.close()
    print('Completed frozen release validation: ' + str(OUTPUT), flush=True)


if __name__ == '__main__': main()
