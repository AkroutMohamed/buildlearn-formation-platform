"""Read-only corpus audit; writes only the new identity sidecar."""
import hashlib
import json
from pathlib import Path
import sys

BACKEND=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BACKEND))
from app.ai.rag.product_identity import build_catalog, CATALOG
from scripts.evaluate_hierarchical_retrieval import read_collection
from qdrant_client import QdrantClient


def main():
    checkpoint=BACKEND/'ai_data/indexing/hierarchical_index_checkpoint.json'
    raw=checkpoint.read_bytes()
    state=json.loads(raw)['state']
    documents=[]
    for item in state['dataset_manifest']:
        path=BACKEND/'ai_data/reports/full_extraction'/item['file']
        content=path.read_bytes(); digest=hashlib.sha256(content).hexdigest()
        if digest!=item['hash']: raise ValueError('Extraction digest mismatch')
        doc=json.loads(content)
        if doc['document_id']!=item['document_id']: raise ValueError('Document identity mismatch')
        doc['_chunk_ids']=item['chunk_ids']; doc['_extraction_sha256']=digest
        documents.append(doc)
    client=QdrantClient(url='http://127.0.0.1:6333')
    try: rows,digest=read_collection(client)
    finally: client.close()
    catalog=build_catalog(documents,rows,digest)
    if (len(documents),len(rows))!=(221,2637): raise ValueError('Unexpected frozen corpus inventory')
    catalog['checkpoint_sha256']=hashlib.sha256(raw).hexdigest()
    if checkpoint.read_bytes()!=raw: raise ValueError('Checkpoint changed during audit')
    CATALOG.parent.mkdir(parents=True,exist_ok=True)
    CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(catalog['summary'],indent=2))


if __name__=='__main__': main()
