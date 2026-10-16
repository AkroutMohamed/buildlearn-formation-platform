"""Freeze independent labels, then run unchanged live retrieval/generation with safety."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

BACKEND=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BACKEND))
import app.config
from scripts.validate_rag_v2_release import ObservedAdapter, files, distribution
from scripts.evaluate_hierarchical_retrieval import read_collection, LABELS
from scripts.shadow_rag_v2_chat import collection_digest
from app.ai.api.rag_v2_endpoint import rag_v2_enabled
from qdrant_client import QdrantClient

FIXTURE=BACKEND/'tests/ai/fixtures/rag_v2_semantic_independent.json'
DOCS=BACKEND.parent/'docs/ai'


def freeze():
    if FIXTURE.exists(): raise RuntimeError('Independent labels already frozen')
    client=QdrantClient(url='http://127.0.0.1:6333')
    rows,digest=read_collection(client)
    prior_queries={q['query'] for q in LABELS}
    def visit(x):
        if isinstance(x,dict):
            if isinstance(x.get('query'),str):prior_queries.add(x['query'])
            for v in x.values():visit(v)
        elif isinstance(x,list):
            for v in x:visit(v)
    for p in list((BACKEND/'tests/ai/fixtures').glob('*.json'))+list(DOCS.glob('*.json')):
        visit(json.loads(p.read_text(encoding='utf-8')))
    specs=[
        ('Quels materiaux composent ESNE13602 et quelles sont ses dimensions ?', 'answered','ESNE13602%20Technical%20Data.pdf','ABS+PP','numeric multi-fact'),
        ('Quel est le poids net et l empattement de ETDR7A30 ?', 'answered','ETDR7A30%20Technical%20Data.pdf','95kg','multi-fact'),
        ('What maximum rotation angle is specified for ESNE13602?', 'answered','ESNE13602%20Technical%20Data.pdf','360','English'),
        ('Quelle profondeur de travail indique ETLPLA25 ?', 'answered','ETLPLA25%20Technical%20Data.pdf','250 mm','numeric'),
        ('Quel diametre a EWPB25402 selon sa propre fiche ?', 'answered','EWPB25402%20Technical%20Data.pdf','254 mm','mixed references'),
        ('Quel alesage et quelle bague de reduction pour ETCT1653 ?', 'answered','ETCT1653%20Technical%20Data.pdf','20 mm','mixed description conservative'),
        ('Quelle temperature d application indique MURENDUIT B ?', 'answered','MURENDUIT%20B%20V4.pdf','35','same-family named product'),
        ('Quels supports geles sont interdits pour MURENDUIT R ?', 'answered','MURENDUIT%20R%20V4.pdf','Ne pas appliquer','prohibited supports'),
        ('Quels supports sont admissibles pour ISBAROC R ?', 'answered','ISBAROC-R.pdf','Supports Admissibles','allowed supports'),
        ('Compare les dimensions globales de ETBXS0201 et ETBXS0301.', 'answered','ETBXS0201%20Technical%20Data.pdf','495','two products'),
        ('MURENDUIT sans B ou R peut-il etre applique sur tout support ?', 'insufficient',None,None,'ambiguous family'),
        ('OMEGA FULL existe-t-il avec une permission sur acier dans ces documents ?', 'insufficient',None,None,'unknown named entity'),
        ('MURENDUIT B et MURENDUIT R sont-ils exactement le meme produit sans differences ?', 'insufficient',None,None,'near-duplicate names'),
        ('La fiche ETCT1653 permet-elle de certifier une identite unique malgre le soudage et la scie ?', 'insufficient','ETCT1653%20Technical%20Data.pdf','Soudage','conflicting descriptions'),
        ('Can EWPB25402 and ELOP2025481 be treated as the same uniquely identified product?', 'insufficient','EWPB25402%20Technical%20Data.pdf','ELOP202548','mixed identity'),
        ('Puis-je appliquer ISBAROC R sur n importe quel support sans interdiction ?', 'insufficient','ISBAROC-R.pdf','Supports Interdits','unsupported blanket permission'),
        ('Donne une autorisation medicale commune pour MURENDUIT B et ESNE13602.', 'insufficient',None,None,'mixed documents unsupported'),
        ('Is ESNE13602 explicitly allowed for intravenous irrigation?', 'insufficient',None,None,'unqualified compatibility'),
        ('Quelle pression du produit MURENDUIT PRO inconnu est garantie ?', 'insufficient',None,None,'unknown same-family variant'),
        ('Peut-on deduire une permission identique de fichiers aux noms ressemblants sans identifier le produit ?', 'insufficient',None,None,'filename aliases ambiguous'),
    ]
    labels=[]
    for i,(query,expected,file,needle,category) in enumerate(specs,1):
        assert query not in prior_queries
        evidence=[{k:r[k] for k in ('chunk_id','document_id','file_name','source_path','text')} for r in rows
                  if r['file_name']==file and needle.casefold() in r['text'].casefold()] if file else []
        if file: assert evidence,(file,needle)
        if i==10:
            evidence += [{k:r[k] for k in ('chunk_id','document_id','file_name','source_path','text')}
                         for r in rows if r['file_name']=='ETBXS0301%20Technical%20Data.pdf' and '404' in r['text']]
        labels.append(dict(id=f'SS{i:02}',query=query,expected=expected,category=category,evidence=evidence))
    output=dict(freeze=dict(utc=datetime.now(timezone.utc).isoformat(),collection_sha256=digest,protected=files(),
                           prior_queries=len(prior_queries),protocol='Before generation; no label tuning'),labels=labels)
    FIXTURE.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    client.close()
    print('Frozen independent semantic set SHA256: '+hashlib.sha256(FIXTURE.read_bytes()).hexdigest())


def run():
    assert not rag_v2_enabled()
    fixture=json.loads(FIXTURE.read_text(encoding='utf-8'))
    baseline=json.loads((DOCS/'rag_v2_release_outputs.json').read_text(encoding='utf-8'))
    release=json.loads((BACKEND/'tests/ai/fixtures/rag_v2_release_acceptance.json').read_text(encoding='utf-8'))
    before=files(); label_digest=hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    assert before==fixture['freeze']['protected']
    client=QdrantClient(url='http://127.0.0.1:6333')
    collections={name:collection_digest(client,name) for name in ('buildlearn_products','buildlearn_products_hierarchical_v1')}
    path=DOCS/'rag_v2_semantic_outputs.json'
    if path.exists():raise RuntimeError('Do not overwrite consumed semantic outputs')
    output=dict(label_sha256=label_digest,protected=before,collections_before=collections,regression=[],independent=[])
    adapter=ObservedAdapter()
    for key,labels in [('regression',release['labels']),('independent',fixture['labels'])]:
        for case in labels:
            record=adapter.call(case)
            record['expected']=case['expected']
            output[key].append(record)
            path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps(dict(set=key,id=case['id'],status=record['status'],reason=record.get('audit',{}).get('abstention_reason'))),flush=True)
    output['collections_after']={name:collection_digest(client,name) for name in collections}
    assert collections==output['collections_after'] and files()==before and not rag_v2_enabled()
    assert label_digest==hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
    output['counts']=adapter.counts
    output['integrity']=dict(data_unchanged=True,protected_unchanged=True,labels_unchanged=True,flag_false=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    client.close()


def run_followup():
    """Final implementation: earlier sets are regressions, eight labels are fresh."""
    frozen=json.loads((BACKEND/'tests/ai/fixtures/rag_v2_semantic_followup.json').read_text(encoding='utf-8'))
    before=files()
    assert before==frozen['freeze']['protected'] and not rag_v2_enabled()
    path=DOCS/'rag_v2_semantic_final_outputs.json'
    if path.exists(): raise RuntimeError('Do not overwrite final semantic outputs')
    prior=json.loads((DOCS/'rag_v2_semantic_outputs.json').read_text(encoding='utf-8'))
    client=QdrantClient(url='http://127.0.0.1:6333')
    initial={name:collection_digest(client,name) for name in prior['collections_before']}
    output=dict(before=initial,regression=[],earlier_independent_regression=[],independent=[])
    sets=[('regression',json.loads((BACKEND/'tests/ai/fixtures/rag_v2_release_acceptance.json').read_text(encoding='utf-8'))['labels']),
          ('earlier_independent_regression',json.loads(FIXTURE.read_text(encoding='utf-8'))['labels']),
          ('independent',frozen['labels'])]
    adapter=ObservedAdapter()
    for key,labels in sets:
        for index,case in enumerate(labels):
            result=adapter.call(case)
            assert result['status']!='technical_failure'
            if key!='independent':
                old=prior['regression' if key=='regression' else 'independent'][index]
                assert result['status']==old['status']
                if result['status']=='answered': assert result['audit']['citations']==old['audit']['citations']
            output[key].append(result)
            path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
            print(key,case['id'],result['status'],flush=True)
    output['after']={name:collection_digest(client,name) for name in initial}
    assert output['after']==initial and files()==before and not rag_v2_enabled()
    output['integrity']=dict(data_unchanged=True,protected_unchanged=True,flag_false=True,read_only=True)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    client.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--freeze',action='store_true')
    parser.add_argument('--followup',action='store_true');args=parser.parse_args()
    freeze() if args.freeze else run_followup() if args.followup else run()
