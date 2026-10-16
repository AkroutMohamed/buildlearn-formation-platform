import json
from pathlib import Path
d = json.loads(Path(r"C:\Users\user\Desktop\stage/formation-platform/backend/ai_data/reports/retrieval_evaluation.json").read_text(encoding="utf-8"))
print("DISTINCT:", d["catalog"]["distinct_product_count"])
for b, v in d["catalog"]["by_brand"].items():
    print(f"  brand={b} -> {v['product_count']} products: {v['products']}")
print("---by_supplier---")
for k, v in d["catalog"]["by_supplier"].items():
    print(f"  supplier={k} -> {v['product_count']} products")
print("payload_keys:", d["catalog"]["payload_keys"])
print("config:", json.dumps(d["config"], ensure_ascii=False))
print("collection:", json.dumps(d["collection"], ensure_ascii=False))

print("\n--- SCIE exact top-5 ---")
scie = [r for r in d["results"] if "SCIE" in r["query"]][0]
for e in scie["production_topk"][:5]:
    print(f"  #{e['rank']} {e['score']} {e['product_name']!r} sup={e['supplier']} :: {e['text_preview'][:55]!r}")

print("\n--- FLEX exact top-5 ---")
flex = [r for r in d["results"] if r["query"] == "FLEX"][0]
for e in flex["production_topk"][:5]:
    print(f"  #{e['rank']} {e['score']} {e['product_name']!r} sup={e['supplier']} :: {e['text_preview'][:55]!r}")

print("\n--- PRO 1000 exact (hit) top-3 ---")
p1000 = [r for r in d["results"] if r["query"] == "PRO 1000"][0]
for e in p1000["production_topk"][:3]:
    print(f"  #{e['rank']} {e['score']} {e['product_name']!r} sup={e['supplier']} :: {e['text_preview'][:55]!r}")

print("\n--- PRO 1000 SOFAP fiche technique (miss) top-5 ---")
pf = [r for r in d["results"] if r["query"] == "PRO 1000 SOFAP fiche technique"][0]
for e in pf["production_topk"][:5]:
    print(f"  #{e['rank']} {e['score']} {e['product_name']!r} sup={e['supplier']} :: {e['text_preview'][:55]!r}")

print("\n--- brand query 'produits EMTOP' top-5 ---")
em = [r for r in d["results"] if r["query"] == "produits EMTOP"][0]
for e in em["production_topk"][:5]:
    print(f"  #{e['rank']} {e['score']} {e['product_name']!r} sup={e['supplier']} src={e['source']}")

print("\n--- brand query 'produits Gypsobat' top-5 ---")
gy = [r for r in d["results"] if r["query"] == "produits Gypsobat"][0]
for e in gy["production_topk"][:5]:
    print(f"  #{e['rank']} {e['score']} {e['product_name']!r} sup={e['supplier']} src={e['source']}")
