import json, sys
from pathlib import Path

out = open(Path(r"C:\Users/user/Desktop/stage/formation-platform/backend/scripts/_probe2_out.txt"),
           "w", encoding="utf-8")
def log(*a):
    print(*a, file=out); out.flush()

d = json.loads(Path(r"C:\Users/user/Desktop/stage/formation-platform/backend/ai_data/reports/retrieval_evaluation.json").read_text(encoding="utf-8"))

for q in ("PRO 1000", "FLEX", "produits EMTOP", "produits Gypsobat", "Lika PAP2"):
    r = [x for x in d["results"] if x["query"] == q][0]
    log(f"\n=== Q: {q!r}  expected={r.get('expected_product')} category={r['category']} ===")
    for e in r["production_topk"][:6]:
        log(f"  #{e['rank']} score={e['score']} {e['product_name']!r} sup={e['supplier']} src={e['source']} sec={e.get('section_title')!r}")
        log(f"        txt: {e['text_preview'][:100]!r}")

# brand query distinct-product analysis (raw top-10)
for q in ("produits EMTOP", "produits SOFAP", "produits Gypsobat"):
    r = [x for x in d["results"] if x["query"] == q][0]
    raw = r["raw_topk"][:10]
    brands = [e["source"] for e in raw]
    log(f"\n=== {q!r} RAW top-10 brand(s) distribution ===")
    from collections import Counter
    log(f"  brands={dict(Counter(brands))}")
    for e in raw:
        log(f"    {e['score']} {e['product_name']!r} src={e['source']} sup={e['supplier']}")
