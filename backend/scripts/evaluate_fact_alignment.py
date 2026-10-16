"""Read-only live fact alignment regression, then a new frozen validation set."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from types import SimpleNamespace

BACKEND=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BACKEND))
import app.config
from scripts.evaluate_product_identity import protected, digest, FIXTURES, DOCS
from scripts.validate_rag_v2_release import ObservedAdapter
from scripts.evaluate_rag_v2 import NEGATIVES
from scripts.evaluate_hierarchical_retrieval import read_collection
from scripts.shadow_rag_v2_chat import collection_digest
from app.ai.api.rag_v2_endpoint import rag_v2_enabled
from app.ai.rag.product_identity import ProductIdentityResolver
from app.ai.rag.fact_alignment_v2 import requested_facts, context_coverage, validate_fact_alignment
from app.ai.rag.semantic_safety_v2 import resolve_targets, validate_semantics
from app.ai.rag.semantic_safety_v2 import check_context
from app.ai.rag.answer_validation_v2 import validate_claims
from qdrant_client import QdrantClient

FIXTURE=FIXTURES/'rag_v2_fact_alignment_validation.json'
SPECS=BACKEND/'ai_data/identity/fact_alignment_validation_specs.json'


def annotate(record,case,resolver):
    record.update(query=case['query'],expected=case['expected'],resolution=asdict(resolver.resolve(case['query'])))
    sources=[SimpleNamespace(**s) for s in record.get('selected_sources',[])]
    try:
        products,owners=resolve_targets(case['query'],sources,resolver)
        facts=requested_facts(case['query'],products)
        record['requested_facts']=[asdict(f)for f in facts]
        record['missing_context_facts']=context_coverage(facts,sources,owners)
    except ValueError as exc:
        record['entity_failure']=str(exc)
    if record['status']=='answered':
        claims=record['audit']['citations']
        validate_semantics(claims,sources,case['query'],resolver)
        validate_fact_alignment(claims,sources,case['query'],resolver)
        assert record['checks']['claim_count']==record['checks']['valid_supports']==record['checks']['valid_citations']


def run(independent, live_regression=False):
    assert not rag_v2_enabled()
    path=DOCS/('rag_v2_fact_alignment_validation_outputs.json' if independent else 'rag_v2_fact_alignment_live_regression_outputs.json' if live_regression else 'rag_v2_fact_alignment_regression_outputs.json')
    if path.exists():raise RuntimeError('Do not overwrite historical outputs')
    before=protected(); resolver=ProductIdentityResolver.load()
    if independent:
        frozen=json.loads(FIXTURE.read_text(encoding='utf8'))
        assert all(before[k]==v for k,v in frozen['freeze']['protected'].items())
        sets=[('independent',frozen['labels'])]
    elif live_regression:
        sets=[('product_identity_regression',json.loads((FIXTURES/'rag_v2_product_identity_validation.json').read_text(encoding='utf8'))['labels'])]
    else:
        sets=[]
        for name in ('rag_v2_release_acceptance','rag_v2_semantic_independent','rag_v2_semantic_followup','rag_v2_independent_validation','rag_v2_product_identity_validation'):
            sets.append((name,json.loads((FIXTURES/(name+'.json')).read_text(encoding='utf8'))['labels']))
        sets.append(('original_positive',[dict(q,expected='answered')for q in json.loads((FIXTURES/'retrieval_v2_heldout.json').read_text(encoding='utf8'))['labels']]))
        sets.append(('original_negative',NEGATIVES))
    client=QdrantClient(url='http://127.0.0.1:6333')
    collections={n:collection_digest(client,n)for n in ('buildlearn_products','buildlearn_products_hierarchical_v1')}
    output=dict(utc=datetime.now(timezone.utc).isoformat(),protected_before=before,collections_before=collections,sets={})
    adapter=ObservedAdapter()
    for name,labels in sets:
        output['sets'][name]=[]
        for case in labels:
            record=adapter.call(case);annotate(record,case,resolver)
            output['sets'][name].append(record)
            path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
            print(name,case['id'],record['status'],record.get('audit',{}).get('telemetry',{}).get('validation_rejection_reason'),flush=True)
    output['collections_after']={n:collection_digest(client,n)for n in collections}
    assert collections==output['collections_after'] and protected()==before and not rag_v2_enabled()
    output['counts']=adapter.counts
    output['integrity']=dict(collections_unchanged=True,protected_unchanged=True,labels_unchanged=True,flag_false=True,read_only_client=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
    client.close()


def replay():
    """Post-generation filters only: same recorded supports/claims, no tuning."""
    import copy
    original=json.loads((DOCS/'rag_v2_fact_alignment_regression_outputs.json').read_text(encoding='utf8'))
    path=DOCS/'rag_v2_fact_alignment_final_regression_outputs.json'
    if path.exists():raise RuntimeError('Do not overwrite final regression replay')
    before=protected();resolver=ProductIdentityResolver.load()
    output=dict(protocol='Offline post-generation validator replay of all 142 captured live requests; no regeneration, ranking or model-output changes',
        protected_before=before,sets={})
    for name,records in original['sets'].items():
        output['sets'][name]=[]
        for captured in records:
            r=copy.deepcopy(captured);sources=[SimpleNamespace(**s)for s in r.get('selected_sources',[])]
            r['status']='insufficient';claims=[];reason=None
            old_reason=captured.get('audit',{}).get('telemetry',{}).get('validation_rejection_reason')
            if captured.get('model_output') and old_reason in (None,'requested_fact_mismatch','incomplete_requested_fact_coverage'):
                try:
                    check_context(r['query'],sources,resolver)
                    claims=validate_claims(json.dumps(captured['model_output']),sources,r['query'])
                    if claims:
                        validate_semantics(claims,sources,r['query'],resolver)
                        validate_fact_alignment(claims,sources,r['query'],resolver)
                        r['status']='answered'
                except ValueError as exc:
                    reason=str(exc);claims=[]
            r['audit']['citations']=claims
            r['audit']['status']=r['status']
            r['checks']=dict(claim_count=len(claims),valid_supports=len(claims),valid_citations=len(claims))
            r['replay_rejection']=reason or old_reason
            if claims:r['response']['answer']='\n'.join(f"{c['text']} [{c['source_id']}]"for c in claims)
            else:
                r['response']['answer']='Insufficient evidence (offline validator replay).'
                r['response']['sources']=[]
            annotate(r,dict(query=r['query'],expected=r['expected']),resolver)
            output['sets'][name].append(r)
    client=QdrantClient(url='http://127.0.0.1:6333')
    try:current={n:collection_digest(client,n)for n in original['collections_after']}
    finally:client.close()
    assert current==original['collections_after'] and protected()==before and not rag_v2_enabled()
    output['collections_before']=current;output['collections_after']=current
    output['integrity']=dict(collections_unchanged=True,protected_unchanged=True,labels_unchanged=True,flag_false=True,offline_replay=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
    print('Final offline regression:',sum(len(rs)for rs in output['sets'].values()),'captured requests')


def freeze():
    if FIXTURE.exists():raise RuntimeError('Independent labels already frozen')
    regression=json.loads((DOCS/'rag_v2_fact_alignment_final_regression_outputs.json').read_text(encoding='utf8'))
    assert regression['integrity']['protected_unchanged'] and protected()==regression['protected_before']
    prior=set()
    def visit(value):
        if isinstance(value,dict):
            if isinstance(value.get('query'),str):prior.add(value['query'])
            for v in value.values():visit(v)
        elif isinstance(value,list):
            for v in value:visit(v)
    for path in [*FIXTURES.glob('*.json'),*DOCS.glob('*.json')]:visit(json.loads(path.read_text(encoding='utf8')))
    client=QdrantClient(url='http://127.0.0.1:6333')
    try:rows,collection_hash=read_collection(client)
    finally:client.close()
    labels=[]
    for i,spec in enumerate(json.loads(SPECS.read_text(encoding='utf8')),1):
        assert spec['query'] not in prior
        evidence=[]
        for label in spec.get('evidence',[]):
            found=[{k:r[k]for k in ('chunk_id','document_id','file_name','source_path','text')}for r in rows
                if r['file_name']==label['file_name'] and label['substring'].casefold() in r['text'].casefold()]
            assert found,label
            evidence.extend(found)
        labels.append(dict(id=f'FA{i:02}',query=spec['query'],expected=spec['expected'],category=spec['category'],evidence=evidence))
    fixture=dict(freeze=dict(utc=datetime.now(timezone.utc).isoformat(),protected=protected(),collection_sha256=collection_hash,
        evaluator_sha256=digest(Path(__file__)),specs_sha256=digest(SPECS),
        protocol='New queries; actual indexed labels; frozen implementation before execution; shared corpus; no tuning'),labels=labels)
    FIXTURE.write_text(json.dumps(fixture,ensure_ascii=False,indent=2),encoding='utf8')
    print('Frozen',len(labels),'queries, SHA256',digest(FIXTURE))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--freeze',action='store_true');p.add_argument('--independent',action='store_true')
    p.add_argument('--replay',action='store_true');p.add_argument('--live-regression',action='store_true');a=p.parse_args()
    freeze() if a.freeze else replay() if a.replay else run(a.independent,a.live_regression)
