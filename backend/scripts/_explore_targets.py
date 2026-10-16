"""Diagnostic: full chunk text + document urls for failing products, UTF-8 safe."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

for line in open(r"C:\Users\user\Desktop\stage\formation-platform/backend/.env", encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

from qdrant_client import QdrantClient

c = QdrantClient(url=os.environ.get("QDRANT_URL", "http://localhost:6333"))
COL = os.environ.get("QDRANT_COLLECTION", "buildlearn_products")

points, _ = c.scroll(collection_name=COL, with_payload=True, with_vectors=False, limit=1000)

targets = ["Lika PAP2", "LIKA PAP2", "Mura colle plâtre", "PRO 1000", "PRO 3000",
           "PRO 2000", "PRO 200", "LIKA FINA", "LIKA FULL", "LIKA FULL ECO",
           "FLEX", "FLEX PLUS", "RUSTIKA GRAVITA", "HYDROMUR PRO", "ADHERCOL P-3000",
           "MURENDUIT CACHET BLEU", "FINACEM CACHET BLEU"]

print("=== TARGET PRODUCT CHUNKS (FULL TEXT + META) ===")
for tgt in targets:
    matches = [p for p in points if (p.payload or {}).get("product_name") == tgt]
    print(f"\n--- {tgt!r} : {len(matches)} chunks ---")
    for p in matches:
        pl = p.payload or {}
        txt = pl.get("text") or ""
        in_text = tgt.lower() in txt.lower()
        print(f"  doc_id={pl.get('document_id')} sup={pl.get('supplier')} src={pl.get('source')}")
        print(f"  doc_url={pl.get('document_url')}")
        print(f"  src_url={pl.get('source_url')}")
        print(f"  evidence={pl.get('evidence')!r}")
        print(f"  source_type={pl.get('source_type')} confidence={pl.get('confidence')}")
        print(f"  page={pl.get('page_number')} sec={pl.get('section_title')!r} txtlen={len(txt)} name_in_text={in_text}")
        print(f"  TEXT({len(txt)}): {txt!r}")
        print()
