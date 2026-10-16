"""Save live RAG V2 outputs and deterministic checks for independent manual review."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

BACKEND=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BACKEND))
from qdrant_client import QdrantClient
from scripts import evaluate_hierarchical_retrieval as base
from app.ai.embeddings.service import EmbeddingService
from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.ai.retrieval.retrieval_v2 import RetrievalV2,LexicalIndex
from app.ai.rag.hierarchical_rag_v2 import HierarchicalRAGV2,RAGV2Config,GroundedQwenProvider,validate_claims

NEGATIVES=[
    dict(id="N01",query="Quel sera le cours du bitcoin demain ?",category="outside corpus",expected="insufficient"),
    dict(id="N02",query="Quel couple maximal offre ZZZZ999999 ?",category="unknown reference",expected="insufficient"),
    dict(id="N03",query="Quelle tension a EBPK20?? ?",category="malformed reference",expected="insufficient"),
    dict(id="N04",query="Quelle est la durée exacte de garantie de ECIDL208689 ?",category="unavailable fact",expected="insufficient"),
    dict(id="N05",query="Quel est le prix de FINACEM CACHET BLEU aujourd’hui ?",category="unavailable price",expected="insufficient"),
    dict(id="N06",query="Quel couple maximal a la perceuse ?",category="ambiguous product",expected="insufficient"),
    dict(id="N07",query="Compare les couples de ECIDL208689 et ZZZZ999999.",category="one supported product",expected="insufficient"),
    dict(id="N08",query="Quelle norme médicale et quelle dose injectable pour FINACEM ROUGE ?",category="unsupported application",expected="insufficient"),
    dict(id="N09",query="Quelle est la résistance au feu de ECIDL208689 en minutes ?",category="unavailable technical fact",expected="insufficient"),
    dict(id="N10",query="Quelle est la consommation du FLEX ?",category="ambiguous product family",expected="clarify or explicitly scoped evidence-supported answer"),
]


class ReviewQwen(GroundedQwenProvider):
    """Save final structured claims, including rejected ones; never reasoning fields."""
    last_output=None

    def generate_grounded(self,question,context):
        raw=super().generate_grounded(question,context)
        try:
            parsed=json.loads(raw)
            self.last_output={k:parsed[k] for k in ("status","claims") if k in parsed} if isinstance(parsed,dict) else dict(format="invalid")
        except ValueError:
            self.last_output=dict(format="invalid",sha256=hashlib.sha256(raw.encode()).hexdigest())
        return raw


def protected():
    result=base.protected_snapshot()
    for folder in ("retrieval","llm"):
        for p in (BACKEND/"app/ai"/folder).glob("*.py"):
            result[str(p.relative_to(BACKEND))]=hashlib.sha256(p.read_bytes()).hexdigest()
    for p in (BACKEND/"tests/ai/fixtures/retrieval_v2_heldout.json",):
        result[str(p.relative_to(BACKEND))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return {k.replace("\\","/"):v for k,v in result.items()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-size",type=int,default=30)
    parser.add_argument("--restart",action="store_true")
    parser.add_argument("--output",type=Path)
    parser.add_argument("--validation-set",type=Path)
    args=parser.parse_args()
    if args.batch_size<1:parser.error("batch-size must be positive")
    before_files=protected()
    fixture=json.loads((BACKEND/"tests/ai/fixtures/retrieval_v2_heldout.json").read_text(encoding="utf-8"))
    old=fixture["freeze"]
    # New isolated RAG module is allowed; all previously protected files must still match.
    if any(before_files[k.replace("\\","/")]!=v for k,v in old["protected"].items()):
        raise ValueError("Previously validated pipeline changed")
    if before_files["app/ai/retrieval/retrieval_v2.py"]!=old["implementation"]:
        raise ValueError("Validated V2 implementation changed")
    client=QdrantClient(url="http://127.0.0.1:6333")
    rows,before=base.read_collection(client)
    if before!=old["collection_digest"]:raise ValueError("Validated collection changed")
    catalog=LexicalIndex(rows).catalog
    assert "ZZZZ999999" not in catalog
    warranty_rows=[r for r in rows if r["file_name"]=="ECIDL208689%20Technical%20Data.pdf"]
    assert not any("garantie" in r["text"].casefold() or "warranty" in r["text"].casefold() for r in warranty_rows)
    positives=[dict(id=q["id"],query=q["query"],evidence=q["evidence"],expected="answered",category="positive") for q in fixture["labels"]]
    cases=positives+NEGATIVES
    if args.validation_set:
        independent=json.loads(args.validation_set.read_text(encoding="utf-8"))
        if independent["freeze"]["collection_sha256"]!=before:
            raise ValueError("Independent validation collection changed")
        cases=independent["labels"]
    config=RAGV2Config(model="qwen2.5-coder:7b",base_url="http://127.0.0.1:11434")
    retriever=RetrievalV2(client=client,embeddings=base.CachedQueries(EmbeddingService(provider=OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",model="nomic-embed-text",normalize=True))))
    review_llm=ReviewQwen(config)
    service=HierarchicalRAGV2(retriever=retriever,llm=review_llm,config=config)
    path=args.output or BACKEND.parent/"docs/ai/rag_v2_answer_outputs.json"
    output=dict(run_utc=datetime.now(timezone.utc).isoformat(),model=config.model,
        rag_implementation_sha256=before_files["app/ai/rag/hierarchical_rag_v2.py"],
        validator_sha256=before_files["app/ai/rag/answer_validation_v2.py"],
        validation_set_sha256=hashlib.sha256(args.validation_set.read_bytes()).hexdigest() if args.validation_set else None,
        retrieval_implementation_sha256=old["implementation"],collection=base.COLLECTION,
        collection_sha256=before,records=[],manual_review_required=True)
    if path.exists() and not args.restart:
        output=json.loads(path.read_text(encoding="utf-8"))
        if output["rag_implementation_sha256"]!=before_files["app/ai/rag/hierarchical_rag_v2.py"] or output.get("validator_sha256")!=before_files["app/ai/rag/answer_validation_v2.py"] or output["collection_sha256"]!=before:
            raise ValueError("Cannot resume results against changed implementation/corpus")
    completed={r["case"]["id"] for r in output["records"]}
    pending=[q for q in cases if q["id"] not in completed]
    for q in pending[:args.batch_size]:
        started=time.monotonic()
        review_llm.last_output=None
        response=service.run(q["query"])
        quote_checks=None
        if response.claims:
            quote_checks=True
            try:validate_claims(json.dumps(dict(status="answered",claims=[{k:c[k] for k in ("text","support_chunk_ids","quote")} for c in response.claims])),response.sources,q["query"])
            except ValueError:quote_checks=False
        relevant=None
        if q["category"]=="positive":
            expected={(e["document_id"],e["file_name"],e["source_path"]) for e in q["evidence"]}
            used={c["source_id"] for c in response.claims}
            relevant=bool(used) and all((s.document_id,s.file_name,s.source_path) in expected for s in response.sources if s.source_id in used)
        output["records"].append(dict(case=q,response=response.to_dict(),seconds=round(time.monotonic()-started,2),
            model_output_for_review=review_llm.last_output,
            deterministic_checks=dict(exact_quote_citation_numeric_unit_reference_checks=quote_checks,
                cited_expected_source=relevant,status=response.status),
            manual_review=dict(factual_correctness="pending",evidence_support="pending",completeness="pending",
                product_identity="pending",answer_language="pending",hallucination="pending",abstention="pending")))
        path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps(dict(id=q["id"],status=response.status,answer=response.answer,warnings=response.warnings,
                             seconds=output["records"][-1]["seconds"]),ensure_ascii=True),flush=True)
    _,after=base.read_collection(client)
    if before!=after or protected()!=before_files:raise RuntimeError("Protected state changed")
    output["integrity"]=dict(collection_unchanged=True,protected_files_unchanged=True)
    output["complete"]=len(output["records"])==len(cases)
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
    client.close()
    print("Saved outputs for manual review: "+str(path),flush=True)


if __name__=="__main__":main()
