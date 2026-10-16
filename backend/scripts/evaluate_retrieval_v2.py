"""Held-out live comparison; never tunes against held-out labels."""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

BACKEND=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BACKEND))
from qdrant_client import QdrantClient
from scripts import evaluate_hierarchical_retrieval as base
from app.ai.embeddings.service import EmbeddingService
from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.ai.retrieval.hierarchical_retriever import HierarchicalRetriever, HierarchicalRetrievalConfig
from app.ai.retrieval.retrieval_v2 import RetrievalV2, RetrievalV2Config


def digest_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    fixture=BACKEND/"tests/ai/fixtures/retrieval_v2_heldout.json"
    state=json.loads(fixture.read_text(encoding="utf-8"))
    labels=state["labels"];freeze=state["freeze"]
    implementation=BACKEND/"app/ai/retrieval/retrieval_v2.py"
    if digest_file(implementation)!=freeze["implementation"] or asdict(RetrievalV2Config())!=freeze["config"]:
        raise ValueError("Implementation/config changed after held-out labels were created; evaluation is invalid")
    if base.protected_snapshot()!=freeze["protected"]:
        raise ValueError("Protected pipeline changed after freeze")
    original={e["file_name"] for q in base.LABELS for e in q["evidence"]}
    if len(labels)<20 or original & {e["file_name"] for q in labels for e in q["evidence"]}:
        raise ValueError("Held-out set must contain 20 queries and disjoint source files")
    client=QdrantClient(url="http://127.0.0.1:6333")
    rows,before=base.read_collection(client)
    if before!=freeze["collection_digest"]:raise ValueError("Collection changed after freeze")
    # Existing validator has a 30-query minimum: validate each unit against the live corpus directly.
    for q in labels:
        for e in q["evidence"]:
            matches=[r for r in rows if base.source_key(r)==base.source_key(e) and r["chunk_id"] in e["chunk_ids"]]
            if {r["chunk_id"] for r in matches}!=set(e["chunk_ids"]) or not all(e["substring"] in r["text"] for r in matches):
                raise ValueError("Held-out indexed evidence changed")
    embeddings=base.CachedQueries(EmbeddingService(provider=OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",model="nomic-embed-text",normalize=True)))
    v1=HierarchicalRetriever(client=client,embeddings=embeddings,
        config=HierarchicalRetrievalConfig(expand_parents=False))
    v2=RetrievalV2(client=client,embeddings=embeddings)
    records=[]
    for q in labels:
        responses={"V1 dense-only":v1.retrieve(q["query"],top_k=5,similarity_threshold=0.0).to_dict()}
        for name,mode in (("lexical-only","lexical"),("identifier + lexical","identifier_lexical"),("full V2","v2")):
            responses[name]=v2.retrieve(q["query"],top_k=5,mode=mode).to_dict()
        for name,response in responses.items():
            records.append(dict(query_id=q["id"],query=q["query"],expected=q["evidence"],mode=name,
                identifier=bool(v2._index.analyze(q["query"])["identifiers"]),response=response,
                metrics={k:base.measure(q,dict(response,hits=response["hits"][:k]),False) for k in (1,3,5)}))
        print(q["id"]+" evaluated",flush=True)
    _,after=base.read_collection(client)
    if before!=after or base.protected_snapshot()!=freeze["protected"] or digest_file(implementation)!=freeze["implementation"]:
        raise RuntimeError("Protected state changed during evaluation")
    summary=[]
    for subset in ("all","identifier","non-identifier"):
        for mode in ("V1 dense-only","lexical-only","identifier + lexical","full V2"):
            selected=[r for r in records if r["mode"]==mode and (subset=="all" or r["identifier"]==(subset=="identifier"))]
            for k in (1,3,5):
                metric=base.aggregate([dict(metrics=r["metrics"][k],response=dict(r["response"],hits=r["response"]["hits"][:k])) for r in selected])
                summary.append(dict(subset=subset,mode=mode,top_k=k,metrics=metric))
    metadata=dict(run_utc=datetime.now(timezone.utc).isoformat(),implementation_sha256=freeze["implementation"],
        fixture_sha256=digest_file(fixture),collection=base.COLLECTION,points=len(rows),collection_sha256=before,
        protected_files_unchanged=True,collection_unchanged=True,labels=len(labels),source_overlap=0,
        config=freeze["config"],embedding_queries=len(embeddings.cache),parent_warnings=sum(bool(r["response"]["warnings"]) for r in records),
        parent_contexts=sum(bool(c["parents"]) for r in records for c in r["response"]["contexts"]))
    lines=["# Retrieval V2 held-out evaluation","", "## Protocol and integrity","",
        "V2 implementation/configuration was frozen before these 20 labels were created. All 20 queries use distinct source files absent from the original 34-query calibration set. Queries and evidence were authored from actual indexed payloads without retrieval feedback. The evaluator rejects changed implementation, configuration, protected pipeline or indexed corpus. No grid or tuning uses these labels. This set is now a consumed test set: future tuning requires a new independent set.","",
        "Source-disjoint does not mean language/template-disjoint: tool specifications and technical-sheet boilerplate contain near duplicates across products. Labels use exact source identity, alternative child IDs and exact full passages. Consequently unrelated useful sources may be unlabelled, and repeated boilerplate can make exact evidence matching stricter than answer relevance. This is a small positive-only evaluation, not an abstention or comprehensive relevance test.","",
        "All ranking metrics measure child evidence only, to compare like for like. Verified parent expansion runs after final selection for V2 modes and is reported separately; parents never change evidence ranks or inflate these metrics. Each mode retrieves K=5 and prefixes are measured at K=1/3/5. V1 threshold is 0.0, matching the diagnostics. V2 uses its frozen lexical-first configuration. MRR is truncated at the measured K; evidence/document recalls and Hit@K are macro-averaged, scoped to exact source identity. Identifier subsets use the corpus detector, not manually assigned labels.","",
        "```json",json.dumps(metadata,indent=2),"```","", "## Measured results","",
        "| Subset | Mode | K | Queries | Hit@K | Evidence recall | Document recall | MRR@K | Empty |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summary:
        m=s["metrics"]
        lines.append(f"| {s['subset']} | {s['mode']} | {s['top_k']} | {m['queries']} | {m['hit']:.4f} | {m['evidence_recall']:.4f} | {m['document_recall']:.4f} | {m['reciprocal_rank']:.4f} | {m['empty_queries']} |")
    at3={s["mode"]:s["metrics"] for s in summary if s["subset"]=="all" and s["top_k"]==3}
    lines += ["","## Interpretation","",
        f"Held-out evidence recall@3: V1 {at3['V1 dense-only']['evidence_recall']:.2%}, lexical-only {at3['lexical-only']['evidence_recall']:.2%}, identifier + lexical {at3['identifier + lexical']['evidence_recall']:.2%}, full V2 {at3['full V2']['evidence_recall']:.2%}. Full V2 changes evidence recall@3 versus lexical-only by {at3['full V2']['evidence_recall']-at3['lexical-only']['evidence_recall']:+.2%}. Interpret the dense branch's contribution using that measured difference, not the architecture diagram. No post-test weights, candidate budgets or normalization were changed.","",
        "V1 remains the existing baseline and is neither replaced nor wired to an endpoint. The separate V2 service is reviewable for adoption; these results do not justify an LLM integration or claim universal quality. Retain source and provenance diagnostics, and use a fresh evaluation set before any further ranking tuning.","",
        "## Frozen held-out labels","","```json",json.dumps(labels,ensure_ascii=False,indent=2),"```","",
        "## Every query and returned evidence","",
        "Provenance fields distinguish reranking score from COSINE similarity; absent dense scores/ranks are null, never fabricated. Candidate union is available from the service; this report records final top-five evidence and query analysis.",""]
    for r in records:
        detail={k:r[k] for k in ("query_id","query","expected","mode","identifier","metrics")}
        detail.update(hits=r["response"]["hits"],warnings=r["response"]["warnings"],
            query_analysis=r["response"].get("query_analysis"),
            parent_ids=[p["parent_id"] for c in r["response"]["contexts"] for p in c["parents"]])
        lines += ["```json",json.dumps(detail,ensure_ascii=False,indent=2),"```",""]
    lines += ["## Reproduction","", "Run from backend: `venv\\Scripts\\python.exe -B scripts/evaluate_retrieval_v2.py`. No collection writes, extraction/chunking/indexing changes, RAG calls, Qwen calls or student-chat integration occur."]
    report=BACKEND.parent/"docs/ai/RETRIEVAL_V2_EVALUATION.md"
    report.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,indent=2),flush=True)
    client.close()


if __name__=="__main__":main()
