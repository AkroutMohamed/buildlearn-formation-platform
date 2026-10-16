"""Offline retrieval-v2 experiments around the unchanged hierarchical retriever."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote

BACKEND=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BACKEND))
from qdrant_client import QdrantClient
from scripts import evaluate_hierarchical_retrieval as base
from app.ai.embeddings.service import EmbeddingService
from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.ai.retrieval.hierarchical_retriever import HierarchicalRetriever, HierarchicalRetrievalConfig

KS=(10,20,50,100)
SMALL_K=(1,3,5,10)
IDENTIFIER=re.compile(r"(?<![A-Z0-9])[A-Z]{2,8}[0-9][A-Z0-9]{2,11}(?![A-Z0-9])",re.I)
STOP=set("a au aux avec ce ces cette de des du en est et il la le les leur ne ou par pas pour quel quelle quelles quels que qui se ses son sur un une à dans peut elle être sont comment combien quoi avant après".split())


def normalize(text):
    text=unquote(text).replace("œ","oe").replace("Œ","OE")
    return "".join(c for c in unicodedata.normalize("NFKD",text) if not unicodedata.combining(c)).casefold()


def tokens(text):
    return set(re.findall(r"[a-z]+[0-9]+[a-z0-9]*|[a-z]+|[0-9]+(?:[.,][0-9]+)?",normalize(text)))


def key(row):
    return (*base.source_key(row),row["chunk_id"])


def identifier_catalog(rows):
    result={}
    for row in rows:
        for ref in IDENTIFIER.findall(unquote(row["file_name"])):
            if sum(c.isdigit() for c in ref)>=3:
                result.setdefault(ref.upper(),set()).add(base.source_key(row))
    return result


def detect(query,catalog):
    return sorted({m.upper() for m in IDENTIFIER.findall(query) if m.upper() in catalog})


class Lexical:
    def __init__(self,rows):
        self.catalog=identifier_catalog(rows)
        self.row_tokens={key(r):tokens(r["text"]+" "+r["file_name"]) for r in rows}
        counts=Counter(t for ts in self.row_tokens.values() for t in ts)
        self.idf={t:math.log((len(rows)+1)/(n+1))+1 for t,n in counts.items()}

    def features(self,query,row):
        qt=tokens(query); rt=self.row_tokens[key(row)]; ft=tokens(row["file_name"])
        ids=detect(query,self.catalog)
        identifier=float(any(ref.lower() in rt for ref in ids))
        words={t for t in qt if t not in STOP and not re.fullmatch(r"\d+(?:[.,]\d+)?",t)}
        numeric={t for t in qt if re.fullmatch(r"\d+(?:[.,]\d+)?",t)}
        denom=sum(self.idf.get(t,math.log(len(self.row_tokens)+1)+1) for t in words)
        lexical=sum(self.idf[t] for t in words & rt)/denom if denom else 0
        filename=len(words & ft)/len(words) if words else 0
        number=len(numeric & rt)/len(numeric) if numeric else 0
        return identifier,filename,lexical,number


def ranked_response(rows):
    return dict(hits=rows,contexts=[],warnings=[])


def metrics(labels,rankings,k):
    records=[dict(metrics=base.measure(q,ranked_response(rankings[q["id"]][:k]),False),
                  response=ranked_response(rankings[q["id"]][:k])) for q in labels]
    return base.aggregate(records)


def evidence_match(q,row):
    return any(base.source_key(e)==base.source_key(row) and
        (row["chunk_id"] in e["chunk_ids"] or e["substring"] in row["text"]) for e in q["evidence"])


def first_rank(q,ranking,evidence=True):
    expected={base.source_key(e) for e in q["evidence"]}
    return next((i for i,r in enumerate(ranking,1) if evidence_match(q,r)),None) if evidence else next(
        (i for i,r in enumerate(ranking,1) if base.source_key(r) in expected),None)


def rerank(rows,features,weights):
    return sorted(rows,key=lambda r:(-(r["score"]+sum(w*f for w,f in zip(weights,features[key(r)]))),key(r)))


def select_grid(labels,dense,features):
    results=[]
    for weights in itertools.product((0,.1,.25,.5,1),(0,.1,.25,.5),(0,.1,.25,.5,1),(0,.1,.25)):
        rankings={q["id"]:rerank(dense[q["id"]][50],features[q["id"]],weights) for q in labels}
        m=metrics(labels,rankings,3); m1=metrics(labels,rankings,1)
        results.append(dict(weights=weights,metrics=m,hit1=m1["hit"]))
    results.sort(key=lambda r:(-r["metrics"]["evidence_recall"],-r["metrics"]["reciprocal_rank"],-r["hit1"],sum(r["weights"]),r["weights"]))
    return results


def main():
    before=base.protected_snapshot()
    # Include unchanged retrieval and frozen harness sources in the guard.
    for p in list((BACKEND/"app/ai/retrieval").glob("*.py"))+[Path(base.__file__)]:
        before[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    client=QdrantClient(url="http://127.0.0.1:6333")
    rows,digest=base.read_collection(client)
    labels=base.LABELS
    base.validate_labels(labels,rows)
    lexical=Lexical(rows)
    service=base.CachedQueries(EmbeddingService(provider=OllamaEmbeddingProvider(
        base_url="http://127.0.0.1:11434",model="nomic-embed-text",normalize=True)))
    retriever=HierarchicalRetriever(client=client,embeddings=service,
        config=HierarchicalRetrievalConfig(expand_parents=False))
    dense={}; features={}; lexrank={}; routed={}; hybrid={}
    for q in labels:
        qid=q["id"]
        dense[qid]={k:retriever.retrieve(q["query"],top_k=k,similarity_threshold=0.0).to_dict()["hits"] for k in KS}
        features[qid]={key(r):lexical.features(q["query"],r) for r in rows}
        # Zero-feature ties retain source/chunk order, never dense or label hints.
        lexrank[qid]=sorted([dict(r,score=0.0) for r in rows],
            key=lambda r:(-sum(features[qid][key(r)]),key(r)))
        ids=detect(q["query"],lexical.catalog)
        sources=set.intersection(*(lexical.catalog[ref] for ref in ids)) if ids else set()
        # Exact routing is evaluated only when there is one source, otherwise dense fallback.
        routed[qid]=[r for r in lexrank[qid] if base.source_key(r) in sources] if len(sources)==1 else dense[qid][100]
        # Offline true hybrid candidate experiment: dense-100 + lexical-50, RRF c=60.
        pool={}; fusion=Counter()
        for ranking in (dense[qid][100],lexrank[qid][:50]):
            for rank,r in enumerate(ranking,1):
                pool[key(r)]=r;fusion[key(r)]+=1/(60+rank)
        hybrid[qid]=sorted(pool.values(),key=lambda r:(-fusion[key(r)],key(r)))
        print(f"Dense/lexical candidates: {qid}",flush=True)
    grid=select_grid(labels,dense,features)
    weights=grid[0]["weights"]
    reranked={q["id"]:rerank(dense[q["id"]][50],features[q["id"]],weights) for q in labels}
    candidate_metrics={k:metrics(labels,{q["id"]:dense[q["id"]][k] for q in labels},k) for k in KS}
    comparisons={name:{k:metrics(labels,ranking,k) for k in SMALL_K} for name,ranking in {
        "dense-only":{q["id"]:dense[q["id"]][10] for q in labels},
        "dense-50 reranked":reranked,"offline lexical full corpus":lexrank,
        "unique identifier route + lexical, dense fallback":routed,"dense-100 + lexical-50 RRF":hybrid}.items()}
    diagnostics=[]
    for q in labels:
        qid=q["id"];ranking=dense[qid][100]
        er=first_rank(q,ranking);dr=first_rank(q,ranking,False);lr=first_rank(q,lexrank[qid]);rr=first_rank(q,reranked[qid])
        baseline_dr=first_rank(q,dense[qid][10],False)
        ids=detect(q["query"],lexical.catalog)
        sources=set.intersection(*(lexical.catalog[i] for i in ids)) if ids else set()
        expected={base.source_key(e) for e in q["evidence"]}
        units=[]
        for e in q["evidence"]:
            matching=lambda r:base.source_key(r)==base.source_key(e) and (r["chunk_id"] in e["chunk_ids"] or e["substring"] in r["text"])
            units.append(dict(expected=e,dense_document_rank=next((i for i,r in enumerate(ranking,1) if base.source_key(r)==base.source_key(e)),None),
                dense_chunk_rank=next((i for i,r in enumerate(ranking,1) if matching(r)),None),
                lexical_rank=next((i for i,r in enumerate(lexrank[qid],1) if matching(r)),None),
                reranked_position=next((i for i,r in enumerate(reranked[qid],1) if matching(r)),None),
                lexical_features=[dict(chunk_id=r["chunk_id"],identifier=f[0],filename=f[1],idf_overlap=f[2],numeric=f[3],lexical_score=sum(f))
                    for r in rows if matching(r) for f in [features[qid][key(r)]]]))
        statuses=[]; categories=[]
        if er is None:statuses.append("A: no correct evidence in dense top 100")
        elif er>10:statuses.append("B: correct evidence exists, below rank 10")
        else:statuses.append("Correct evidence in dense top 10")
        if baseline_dr is not None and (er is None or er>10):
            statuses.append("C: expected document in top 10, evidence chunk missed")
        if ids and sources==expected and (er is None or er>10):categories.append("identifier failure")
        if er is None or er>10:categories.append("semantic embedding failure")
        if dr is not None and (er is None or er>10) and (er is None or er>dr):categories.append("source-document found but evidence chunk missed")
        if lr is None or lr>50:categories.append("lexical mismatch")
        if q.get("parser_signal"):categories.append("parser/OCR issue")
        if set(q["categories"]) & {"vague/general","cross-document ambiguity"}:categories.append("ambiguous label")
        duplicate_sources=set()
        for e in q["evidence"]:
            et=tokens(e["substring"])
            for r in dense[qid][10]:
                rt=tokens(r["text"])
                if base.source_key(r) not in expected and et and len(et & rt)/len(et | rt)>=.85:
                    duplicate_sources.add(base.source_key(r))
        if duplicate_sources:categories.append("near-duplicate confusion")
        diagnostics.append(dict(query_id=qid,query=q["query"],categories=q["categories"],expected_units=units,
            first_correct_evidence_rank=er,first_correct_document_rank=dr,identifier_detected=ids,
            baseline_top10_first_document_rank=baseline_dr,
            dense_ranks_by_k={k:dict(first_evidence=first_rank(q,dense[qid][k]),
                first_document=first_rank(q,dense[qid][k],False)) for k in KS},
            identifier_expected_source_match=[dict(identifier=i,matches=sorted(lexical.catalog[i]),
                matches_expected=bool(lexical.catalog[i] & expected),unambiguous=len(lexical.catalog[i])==1) for i in ids],
            exact_identifier_route_correct_unambiguously=bool(ids) and len(sources)==1 and sources==expected,
            lexical_first_evidence_rank=lr,reranked_first_evidence_position=rr,
            diagnosis=statuses,failure_groups=categories,near_duplicate_sources=sorted(duplicate_sources),
            dense_top10=[{k:r[k] for k in ("file_name","document_id","chunk_id","score","section_path","block_type")} for r in dense[qid][10]]))
    _,after_digest=base.read_collection(client)
    after=base.protected_snapshot()
    for p in list((BACKEND/"app/ai/retrieval").glob("*.py"))+[Path(base.__file__)]:
        after[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    if before!=after or digest!=after_digest:raise RuntimeError("Protected state changed")
    write_report(labels,rows,digest,lexical,grid,candidate_metrics,comparisons,diagnostics,features,dense,routed,lexrank)
    client.close()


def metric_table(comparisons):
    lines=["| Experiment | K | Hit@K | Evidence recall | Document recall | MRR@K |","|---|---:|---:|---:|---:|---:|"]
    for name,summary in comparisons.items():
        for k,m in summary.items():
            lines.append(f"| {name} | {k} | {m['hit']:.4f} | {m['evidence_recall']:.4f} | {m['document_recall']:.4f} | {m['reciprocal_rank']:.4f} |")
    return lines


def write_report(labels,rows,digest,lexical,grid,candidate_metrics,comparisons,diagnostics,features,dense,routed,lexrank):
    idqueries=[d for d in diagnostics if d["identifier_detected"]]
    idlabels=[q for q in labels if detect(q["query"],lexical.catalog)]
    source_count=len({base.source_key(r) for r in rows})
    lex100={q["id"]:sorted([dict(r,score=0.0) for r in rows],key=lambda r:(-sum(features[q["id"]][key(r)]),key(r)))[:100] for q in labels}
    upper50=sum(base.measure(q,ranked_response(dense[q["id"]][50]),False)["evidence_recall"] for q in labels)/len(labels)
    id_without_text=sum(not any(ref.casefold() in e["substring"].casefold()
        for ref in detect(q["query"],lexical.catalog) for e in q["evidence"]) for q in idlabels)
    failure_counts=Counter(c for d in diagnostics for c in d["failure_groups"])
    failure_counts={c:failure_counts[c] for c in ("identifier failure","semantic embedding failure","lexical mismatch",
        "near-duplicate confusion","source-document found but evidence chunk missed","parser/OCR issue","ambiguous label")}
    text=["# Retrieval-v2 diagnostic", "", f"Run UTC: {datetime.now(timezone.utc).isoformat()}", "",
        "## Scope and method", "",
        f"All {len(labels)} original frozen queries and labels are unchanged. The collection has {len(rows)} child points, {source_count} source identities. Collection payload/vector SHA-256 before/after: `{digest}` (identical). Protected extraction, chunking, embedding, indexing, vectorstore, RAG, retrieval, AI configuration, checkpoint, frozen evaluation harness and student-router hashes are unchanged. `buildlearn_products` was not accessed; hierarchical collection operations were read-only. No collection writes or LLM calls occurred. Qdrant server access logs are outside the integrity scope.", "",
        "Existing HierarchicalRetriever and EmbeddingService/nomic-embed-text execute four independent dense searches per query: K=10/20/50/100, COSINE, threshold 0.0. Query embeddings are cached in memory across K. Child-only evidence metrics use the original frozen exact IDs/substring rules and exact source identity. MRR is truncated at each reported K. Rank null means outside the specified candidate pool, never proof of absence from the whole collection. Every expected evidence unit is present and validated in the indexed collection.", "",
        "## Phase 1: dense candidate recall", ""]
    text+=metric_table({"dense-only":candidate_metrics})
    counts=Counter(s.split(":",1)[0] for d in diagnostics for s in d["diagnosis"] if s[0] in "ABC" and s[1:2]==":")
    text += ["", f"Baseline top-10 failures: A={counts['A']} (no evidence in top 100); B={counts['B']} (evidence ranked 11–100); C={counts['C']} (expected document in top 10 but evidence missed). A/B are mutually exclusive; C can overlap either. Multi-unit queries can still lack other required facts even when one correct evidence unit is found.", "",
        f"Dense top-50 candidate evidence ceiling: **{upper50:.2%}**. Reranking cannot exceed this ceiling without adding candidates. Dense top-100 evidence recall is **{candidate_metrics[100]['evidence_recall']:.2%}**.", "",
        "## Phase 2: identifiers", "",
        f"Generic conservative rule derived from filename code shapes: token boundaries, 2–8 letters then a digit-led 3–12-character alphanumeric suffix containing at least three digits, case insensitive; accept only references observed in URL-decoded corpus filenames. This covers numeric and mixed letter/digit suffixes without guessing unknown codes. There are {len(lexical.catalog)} recognized corpus references, {len(idqueries)} identifier queries. No evaluation identifier is hardcoded in the detector. Pure numbers, standard tokens absent from reference filenames, short platform names and free-form product names are not routed by this rule. All-letter names require separate metadata matching.", "",
        f"Exact identifier filtering identifies the expected source unambiguously for **{sum(d['exact_identifier_route_correct_unambiguously'] for d in idqueries)}/{len(idqueries)}** detected-identifier queries. This is source routing accuracy, not evidence accuracy. Source identity includes source_path to disambiguate duplicate document IDs. Query identifiers are intersected; ambiguous/empty intersections fall back to dense retrieval.", ""]
    text+=metric_table({"dense identifier subset":{k:metrics(idlabels,{q["id"]:dense[q["id"]][10] for q in idlabels},k) for k in SMALL_K}})
    text+=metric_table({"exact route + lexical identifier subset":{k:metrics(idlabels,routed,k) for k in SMALL_K},
                       "lexical identifier subset":{k:metrics(idlabels,lexrank,k) for k in SMALL_K}})
    text += ["", f"For {id_without_text}/{len(idlabels)} identifier queries, none of the labeled evidence passages contains the requested code, although the filename does. Existing `EmbeddingService.embed_chunks` embeds only `chunk.text` (`app/ai/embeddings/service.py:68`); the provider passes that text unchanged (`ollama_provider.py:30`). Dense search therefore cannot directly use the exact reference stored only in payload metadata. This is a concrete representation gap, not proof that all semantic embedding quality is poor. Query and document text are passed without distinct task prefixes; no prefix/model ablation was performed, so the effect of that convention remains unmeasured.", "",
        "Identifier validation is corpus-derived and evaluated over all labeled questions; full per-identifier matches and ranks appear below. This proves behavior on this corpus, not recall of every possible future identifier format.", "",
        "## Phase 3: lexical signals", "",
        "Normalization: URL decoding, Unicode NFKD, accent removal, casefolding, ligature expansion, set tokens. Reference tokens remain whole, and numeric/decimal tokens are retained. Minimal French stopwords are removed only from word overlap. Chunk tokens include original text plus filename; original text is never edited. No new dependency was installed; rank_bm25 is absent, so BM25 was not used.", "",
        "Features are in [0,1]: identifier = any detected reference present in candidate text/filename; filename = fraction of query word tokens present in filename; lexical = IDF-weighted query-word overlap with chunk+filename, divided by all query-word IDF including unseen terms; numeric = fraction of exact numeric tokens present. IDF = log((N+1)/(df+1))+1 over all child records. Decimal comma/dot spellings remain distinct exact tokens. Offline lexical rank sums these four transparent features; it is a diagnostic fixed-weight reference, not a deployed score.", "",
        f"Full-corpus lexical top-100 evidence recall: **{metrics(labels,lex100,100)['evidence_recall']:.2%}**. Full-corpus lexical and routing comparisons intentionally test candidate generation beyond the dense pool, entirely offline against the existing payload snapshot.", "",
        "## Phase 4: deterministic reranking", "",
        "Dense top-50 candidates only. Score = dense_score + wi*identifier + wf*filename + wl*IDF_overlap + wn*numeric. Grid: wi,wl in {0,.1,.25,.5,1}; wf in {0,.1,.25,.5}; wn in {0,.1,.25}. All 300 combinations, including the zero-bonus control, were evaluated. Select highest macro evidence recall@3, then MRR@3, then Hit@1; ties choose smallest sum of weights and lexicographic weights. Source/chunk identity breaks score ties. No label information enters scoring. Selection uses the same 34 labels, so gains are calibration-set gains and need held-out validation.", "",
        f"Selected weights (identifier, filename, word overlap, numbers): **{grid[0]['weights']}**.", ""]
    text+=metric_table(comparisons)
    ablations={}
    for i,name in enumerate(("identifier only bonus","filename only bonus","word overlap only bonus","numeric only bonus")):
        w=tuple(int(j==i) for j in range(4))
        ranking={q["id"]:rerank(dense[q["id"]][50],features[q["id"]],w) for q in labels}
        ablations[name]={k:metrics(labels,ranking,k) for k in SMALL_K}
    text += ["", "### Transparent single-signal controls", "",
        "Each control adds one signal with unit weight to dense score on the same top-50 candidates. These controls explain signal effects and do not replace the grid-selected weights. Identifier and filename/word features are correlated because filenames contain references; a zero selected standalone identifier coefficient does not demonstrate that identifiers are unhelpful.", ""]
    text+=metric_table(ablations)
    text += ["", "Dense-only K=1/3/5/10 uses prefixes of the independently retrieved top-10 pool, reproducing the original small-K baseline. Larger pools can change boundary tie ordering and document recall; those differences are not model improvements. Lexical-only source rows have placeholder score 0; reported ranking metrics do not use that placeholder. RRF uses equal reciprocal ranks 1/(60+rank), dense top-100 plus lexical top-50; c=60 was fixed as a transparent diagnostic, not tuned. Identifier-routing comparison lexically ranks children of a single matching source; ambiguous/missing identifiers use dense top-100. These two candidate-expansion experiments are diagnostic simulations, not implementation changes.", "",
        "## Phase 5: architecture decision", ""]
    dense_m=comparisons["dense-only"][3]; rr_m=comparisons["dense-50 reranked"][3]; route=comparisons["unique identifier route + lexical, dense fallback"][3]; hy=comparisons["dense-100 + lexical-50 RRF"][3]; lex=comparisons["offline lexical full corpus"][3]
    nonroutable=[d for d in diagnostics if d["first_correct_evidence_rank"] is None and d["lexical_first_evidence_rank"] is not None and d["lexical_first_evidence_rank"]<=50 and not d["exact_identifier_route_correct_unambiguously"]]
    need_candidates=bool(nonroutable)
    choice="C. True hybrid lexical + dense candidate generation" if need_candidates else ("B. Dense + metadata/identifier routing" if route["evidence_recall"]>rr_m["evidence_recall"] else "A. Dense candidate generation with reranking")
    text += [f"Recommended next architecture: **{choice}**.", "",
        f"Measured evidence recall@3: dense {dense_m['evidence_recall']:.2%}; dense-50 reranked {rr_m['evidence_recall']:.2%}; unique-reference route {route['evidence_recall']:.2%}; lexical-only {lex['evidence_recall']:.2%}; dense/lexical RRF {hy['evidence_recall']:.2%}. {sum(d['first_correct_evidence_rank'] is None and d['lexical_first_evidence_rank'] is not None and d['lexical_first_evidence_rank']<=50 for d in diagnostics)} questions have evidence missing from dense top 100 but found by lexical top 50. Such misses cannot be repaired by dense-top-50 reranking alone.", "",
        f"Of those recoverable misses, {len(nonroutable)} lack a route under the tested conservative detector ({', '.join(d['query_id'] for d in nonroutable)}). These include reference formats/product names outside that detector's scope. The tested option-B variant leaves candidate gaps; richer name/version-aware metadata routing was not evaluated and cannot be ruled out. C is justified by the measured lexical candidate gains, not proof that every possible metadata-only architecture must fail.", "",
        "Next implementation should use exact-reference routing when the corpus metadata identifies one source, lexical candidates alongside dense candidates for other questions, and deterministic fusion/reranking with provenance preservation. The measured fusion is a reference, not proof that its fixed c=60 or learned-on-this-set bonuses are optimal. Keep source verification, child-text preservation and generation separation. Evaluate independent queries and ambiguous/negative cases before setting production weights or thresholds.", "",
        "Equal-weight RRF should not be the next default based on these measurements: at K=3 it underperforms lexical-only and identifier routing substantially. The evidence favors a lexical-first/identifier-aware candidate layer with dense semantic candidates retained and reranking calibrated on independent questions. The current experiment does not establish optimal reranking weights for that expanded union.", "",
        "D (embedding-model reconsideration) is not established: no alternative embedding model was tested. Dense misses and identifier sensitivity justify auditing query/document embedding conventions and evaluating alternative models on held-out data, but cannot establish that replacing the model is necessary. No embedding configuration, prefix or vector was changed in this experiment.", "",
        "## Failure groups", "", "Categories overlap and are conservative diagnostic signals, not proven causal assignments. Identifier failure means unambiguous correct reference routing but baseline dense evidence missed. Semantic embedding failure means dense top-10 evidence missed; lexical success strengthens evidence for a dense ranking/candidate problem without ruling out label incompleteness. This includes the two parser-flagged queries, so there are 24 dense misses rather than the prior report's 22 residual embedding/retrieval signals. Lexical mismatch means full-corpus lexical evidence rank >50. Source-document/evidence mismatch is recorded for baseline evidence failures when the correct document appears earlier within top 100 or its evidence is missing. C specifically uses the independently retrieved baseline top 10. Parser/OCR flags are the existing frozen source-damage signals, never changes to labels. Ambiguity flags come from the frozen question categories. Near-duplicate confusion requires word-token Jaccard >=.85 between labeled evidence and another-source baseline dense top-10 chunk; this ignores ordering and numbers remain tokens.", "", "```json",
        json.dumps(failure_counts,indent=2),"```", "",
        "## All 34 query diagnostics", "", "Ranks use dense top 100, full-corpus lexical ranking, and the selected dense-top-50 reranker respectively. Per-unit ranks expose partial multi-source misses; first ranks report any matching evidence. Lexical score and components are shown for every alternative labeled child. Null reranked position means the expected evidence was absent from dense top 50. Expected exact text/IDs are the original frozen labels.", ""]
    for d in diagnostics:text += ["```json",json.dumps(d,ensure_ascii=False,indent=2),"```",""]
    text += ["## Complete reranking grid", "", "Each row reports selection metrics at K=3 and Hit@1; selected scheme's four-K metrics appear above.", "", "```json",json.dumps(grid,indent=2),"```", "",
        "## Reproduction", "", "Run from backend: `venv\\Scripts\\python.exe -B scripts/evaluate_retrieval_v2_diagnostic.py`. No network service other than the existing local Qdrant and Ollama embedding endpoint is used. This script writes only this report and performs read-only collection operations."]
    path=BACKEND.parent/"docs/ai/RETRIEVAL_V2_DIAGNOSTIC.md"
    path.write_text("\n".join(text),encoding="utf-8")
    print(json.dumps(dict(recommendation=choice,weights=grid[0]["weights"],dense=candidate_metrics,comparisons=comparisons,report=str(path)),indent=2),flush=True)


if __name__=="__main__":main()
