"""No tuning: consumed regression, then separately frozen live identity validation."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

BACKEND=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BACKEND))
import app.config
from app.ai.rag.product_identity import ProductIdentityResolver, CATALOG
from app.ai.api.rag_v2_endpoint import rag_v2_enabled
from scripts.validate_rag_v2_release import ObservedAdapter, files, distribution
from scripts.shadow_rag_v2_chat import collection_digest
from scripts.evaluate_hierarchical_retrieval import read_collection
from scripts.evaluate_rag_v2 import NEGATIVES
from qdrant_client import QdrantClient

FIXTURES=BACKEND/'tests/ai/fixtures'
DOCS=BACKEND.parent/'docs/ai'
FROZEN=FIXTURES/'rag_v2_product_identity_validation.json'


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def protected():
    result=files()
    for path in [CATALOG,BACKEND/'app/ai/rag/product_identity.py',*FIXTURES.glob('*.json')]:
        result[str(path.relative_to(BACKEND))]=digest(path)
    return result


def run(independent=False):
    path=DOCS/('rag_v2_product_identity_validation_outputs.json' if independent else 'rag_v2_product_identity_regression_outputs.json')
    if path.exists():raise RuntimeError('Do not overwrite consumed evaluation output')
    assert not rag_v2_enabled()
    before=protected(); resolver=ProductIdentityResolver.load()
    if independent:
        frozen=json.loads(FROZEN.read_text(encoding='utf8'))
        assert all(before[k]==v for k,v in frozen['freeze']['protected'].items())
        sets=[('independent',frozen['labels']),('selected_context_control',frozen['labels'])]
    else:
        sets=[]
        for name in ('rag_v2_release_acceptance','rag_v2_semantic_independent','rag_v2_semantic_followup','rag_v2_independent_validation'):
            sets.append((name,json.loads((FIXTURES/(name+'.json')).read_text(encoding='utf8'))['labels']))
        heldout=json.loads((FIXTURES/'retrieval_v2_heldout.json').read_text(encoding='utf8'))['labels']
        sets.append(('original_positive',[dict(q,expected='answered') for q in heldout]))
        sets.append(('original_negative',NEGATIVES))
    client=QdrantClient(url='http://127.0.0.1:6333')
    collections={n:collection_digest(client,n) for n in ('buildlearn_products','buildlearn_products_hierarchical_v1')}
    output=dict(utc=datetime.now(timezone.utc).isoformat(),protected_before=before,collections_before=collections,sets={})
    adapter=ObservedAdapter()
    for name,labels in sets:
        if name=='selected_context_control':
            class SelectedContextControl(ObservedAdapter):
                def factory(self):
                    service=super().factory()
                    service.identity_resolver=None
                    return service
            adapter=SelectedContextControl()
        output['sets'][name]=[]
        for q in labels:
            r=adapter.call(q);r['query']=q['query'];r['expected']=q['expected']
            r['resolution']=asdict(resolver.resolve(q['query']))
            output['sets'][name].append(r)
            path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
            print(name,q['id'],r['status'],flush=True)
    output['collections_after']={n:collection_digest(client,n) for n in collections}
    assert output['collections_after']==collections and protected()==before and not rag_v2_enabled()
    output['integrity']=dict(collections_unchanged=True,protected_unchanged=True,flag_false=True,read_only_client=True)
    output['counts']=adapter.counts
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
    client.close()


def freeze():
    if FROZEN.exists():raise RuntimeError('Labels already frozen')
    regression=DOCS/'rag_v2_product_identity_regression_outputs.json'
    assert regression.exists() and json.loads(regression.read_text(encoding='utf8'))['integrity']['protected_unchanged']
    # Labels are added from actual indexed evidence before any execution of this
    # set. Deliberately no parameter search or acceptance-result optimization.
    specs_path=BACKEND/'ai_data/identity/validation_specs.json'
    specs=json.loads(specs_path.read_text(encoding='utf8'))
    client=QdrantClient(url='http://127.0.0.1:6333')
    try:rows,collection_hash=read_collection(client)
    finally:client.close()
    prior=set()
    def visit(x):
        if isinstance(x,dict):
            if isinstance(x.get('query'),str):prior.add(x['query'])
            for v in x.values():visit(v)
        elif isinstance(x,list):
            for v in x:visit(v)
    for p in [*FIXTURES.glob('*.json'),*DOCS.glob('*.json')]:visit(json.loads(p.read_text(encoding='utf8')))
    labels=[]
    for i,spec in enumerate(specs,1):
        assert spec['query'] not in prior
        evidence=[{k:r[k] for k in ('chunk_id','document_id','file_name','source_path','text')} for r in rows
            if r['file_name']==spec.get('file_name') and spec.get('substring','').casefold() in r['text'].casefold()]
        if spec.get('file_name'):assert evidence,spec
        labels.append(dict(id=f'PI{i:02}',query=spec['query'],expected=spec['expected'],category=spec['category'],evidence=evidence))
    frozen=dict(freeze=dict(utc=datetime.now(timezone.utc).isoformat(),protected=protected(),collection_sha256=collection_hash,
        evaluator_sha256=digest(Path(__file__)),specs_sha256=digest(specs_path),
        protocol='New query wording, labels from indexed evidence; implementation frozen; consumed sets only regression; no tuning; shared products explicitly permitted'),labels=labels)
    FROZEN.write_text(json.dumps(frozen,ensure_ascii=False,indent=2),encoding='utf8')
    print('Frozen '+str(len(labels))+' queries; SHA256 '+digest(FROZEN))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--independent',action='store_true');a=p.parse_args()
    freeze() if a.freeze else run(a.independent)
