"""Extract failure details + SCIE encoding check from evaluation JSON.
Writes output to a utf-8 file to avoid console cp1252 encoding errors."""
import json, os, re, sys, unicodedata
from pathlib import Path

OUT = sys.stdout = open(
    Path(r"C:\Users\user\Desktop\stage/formation-platform/backend/scripts/_extract_out.txt"),
    "w", encoding="utf-8")
def log(*a):
    print(*a); OUT.flush()

p = Path(r"C:\Users\user\Desktop\stage\formation-platform/backend/ai_data/reports/retrieval_evaluation.json")
rep = json.loads(p.read_text(encoding="utf-8"))

log("=== raw_vs_production_identical_order (per query) ===")
same = 0; diff = 0
for r in rep["results"]:
    if r.get("expected_product") and r.get("raw_vs_production_identical_order") is not None:
        if r["raw_vs_production_identical_order"]:
            same += 1
        else:
            diff += 1
            log("  DIFF order:", r["query"])
log(f"identical_order: same={same} diff={diff}")

# Verify threshold is a no-op: every production top-k score >= threshold
all_prod_scores = [e["score"] for r in rep["results"] for e in r["production_topk"] if e["score"]]
log(f"\n=== threshold check (threshold={rep['config']['retrieval_score_threshold']}) ===")
log(f"min production top-k score={min(all_prod_scores):.4f}  (must be >= threshold for threshold to be a no-op)")
log(f"count prod scores below threshold: {sum(1 for s in all_prod_scores if s < rep['config']['retrieval_score_threshold'])}/{len(all_prod_scores)}")
# count how many results produced exactly 10 production items (threshold did not truncate)
counts = [len(r["production_topk"]) for r in rep["results"]]
from collections import Counter
log("production_topk length distribution:", Counter(counts))

# SCIE source literal
scr = Path(r"C:\Users\user\Desktop\stage/formation-platform/backend/scripts/evaluate_retrieval.py")
for ln in scr.read_text(encoding="utf-8").splitlines():
    if "SCIE" in ln and "MARBRE" in ln:
        log("\nSCIE source line repr:", repr(ln))

# Pull SCIE product name directly from Qdrant
for line in (Path(r"C:\Users\user\Desktop/stage/formation-platform/backend/.env").read_text(encoding="utf-8").splitlines()):
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line.strip())
    if m:
        os.environ.setdefault(m.group(1), m.group(2).strip())
from qdrant_client import QdrantClient
c = QdrantClient(url=os.environ.get("QDRANT_URL","http://localhost:6333"))
COL = os.environ.get("QDRANT_COLLECTION","buildlearn_products")
pts, _ = c.scroll(collection_name=COL, with_payload=True, with_vectors=False, limit=1000)
scie = [ (pt.id, (pt.payload or {}).get("product_name")) for pt in pts
         if (pt.payload or {}).get("product_name") and "scie" in (pt.payload or {}).get("product_name","").lower()
         and "marbre" in (pt.payload or {}).get("product_name","").lower()]
log("\nSCIE MARBRE stored names (id, repr, NFKC-repr, has U+FFFD):")
for i, pn in scie:
    has_fffd = "\ufffd" in pn
    log(f"  id={i} repr={pn!r} NFKC={unicodedata.normalize('NFKC', pn)!r} has_U+FFFD={has_fffd}")
# also search "SCIE À MARBRE" without replacement char
scie2 = [ (pt.id, (pt.payload or {}).get("product_name")) for pt in pts
          if (pt.payload or {}).get("product_name") and "scie" in (pt.payload or {}).get("product_name","").lower()
          and "marbre" in (pt.payload or {}).get("product_name","").lower() and "\ufffd" not in (pt.payload or {}).get("product_name","")]
log(f"  SCIE MARBRE WITHOUT U+FFFD count={len(scie2)}")

log("\n=== FAILURE DETAILS (reported + exact SOFAP/GYPSOBAT) ===")
for r in rep["results"]:
    if r["category"] in ("reported_failure","exact") and r.get("expected_product") and not r["hit_1"]:
        fd = r.get("failure_detail", {})
        log(f"\nQ: {r['query']!r}  expected={r['expected_product']!r}")
        log(f"  class={fd.get('class')} raw_rank={r['raw_correct_rank']} prod_rank={r['production_correct_rank']} "
            f"raw_score={r['raw_correct_score']} q2cmp_cos={r['query_to_correct_cosine']}")
        log(f"  exists={r['expected_exists_in_collection']} chunks={r.get('expected_chunk_count')} name_in_text%={r.get('correct_product_name_in_chunk_text_pct')}")
        log(f"  meta_substring_found={fd.get('metadata_substring_match_found')} matches={fd.get('metadata_substring_matches')}")
        log(f"  identical_raw_prod={r.get('raw_vs_production_identical_order')}")
        log("  TOP WRONG (prod top-k):")
        for w in fd.get("top_wrong_products", [])[:5]:
            log(f"    #{w['rank']} score={w['score']} {w['product_name']!r} sup={w['supplier']} sec={w.get('section_title')!r} :: {w['text_preview'][:90]!r}")

log("\n=== SUCCESSFUL exact queries (rank 1) score contrast ===")
for r in rep["results"]:
    if r["category"]=="exact" and r.get("expected_product") and r["hit_1"]:
        log(f"  OK {r['expected_product']!r}: top1_score={r['production_correct_score']} name_in_text%={r.get('correct_product_name_in_chunk_text_pct')}")

log("\n=== Distinct products per brand (ground truth counts) ===")
for b, d in rep["catalog"]["by_brand"].items():
    log(f"  {b}: {d['product_count']} distinct products")
log(f"  TOTAL distinct products: {rep['catalog']['distinct_product_count']}")

log("\n=== Catalog coverage detail (brand queries, raw top-5) ===")
for b, cov in rep["catalog_coverage"].items():
    log(f"  {b}: indexed={cov['indexed_distinct_products']} returned_top5={cov['distinct_products_in_brand_query_top5']} ({cov['coverage_pct']}%) sample={cov['sample_returned']}")

log("\n=== Score contrast: exact queries, hit (top-1) vs miss ===")
hits_sc, miss_sc, chits, cmiss = [], [], [], []
for r in rep["results"]:
    if r.get("category") == "exact" and r.get("expected_product") is not None and "error" not in r:
        s1 = r["production_topk"][0]["score"] if r["production_topk"] else None
        if r["hit_1"]:
            hits_sc.append(s1); chits.append(r["production_correct_score"])
        else:
            miss_sc.append(s1); cmiss.append(r["query_to_correct_cosine"])
def _st(v):
    v2=sorted(v)
    return {"n":len(v2),"min":round(v2[0],4),"max":round(v2[-1],4),"mean":round(sum(v2)/len(v2),4),"median":round(v2[len(v2)//2],4)} if v2 else None
log(f"  exact top-1 (retrieved) scores  HIT: {_st(hits_sc)}")
log(f"  exact top-1 (retrieved) scores  MISS: {_st(miss_sc)}")
log(f"  correct-product cosine, HITS: {_st(chits)}  MISSES: {_st(cmiss)}")
