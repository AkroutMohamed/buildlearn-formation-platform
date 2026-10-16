"""Temporary exploration: map the product catalog indexed in Qdrant."""
import sys
from collections import defaultdict

import os
os.environ.setdefault('EMBEDDING_PROVIDER', 'ollama')
os.environ.setdefault('EMBEDDING_MODEL', 'nomic-embed-text')
os.environ.setdefault('VECTOR_STORE', 'qdrant')
os.environ.setdefault('QDRANT_URL', 'http://localhost:6333')
os.environ.setdefault('QDRANT_COLLECTION', 'buildlearn_products')
os.environ.setdefault('OLLAMA_BASE_URL', 'http://localhost:11434')

from qdrant_client import QdrantClient
c = QdrantClient(url='http://localhost:6333')

ci = c.get_collection('buildlearn_products')
print("STATUS:", ci.status, "POINTS:", ci.points_count, "SEGMENTS:", ci.segments_count)

# Distinct suppliers and product names with document counts
by_supplier = defaultdict(lambda: defaultdict(set))  # supplier -> product_name -> set(doc_id)
text_len_samples = []
text_contains_product = 0
text_total = 0
prod_names_seen = set()

points, next_page = c.scroll(collection_name='buildlearn_products', with_payload=True, with_vectors=False, limit=1000)
all_points = list(points)

for p in all_points:
    payload = p.payload or {}
    pname = payload.get('product_name')
    supplier = payload.get('supplier')
    docid = payload.get('document_id')
    text = payload.get('text') or ''
    prod_names_seen.add(pname)
    if supplier and pname:
        by_supplier[supplier][pname].add(docid)
    text_total += 1
    if text:
        text_len_samples.append(len(text))
        if pname and pname.lower() in text.lower():
            text_contains_product += 1
    else:
        text_len_samples.append(0)

print("\n=== DISTINCT SUPPLIERS x PRODUCT_NAMES (document counts) ===")
for supplier in sorted(by_supplier):
    prods = by_supplier[supplier]
    print(f"\n[{supplier}] {len(prods)} distinct products")
    for pname in sorted(prods):
        print(f"   - {pname!r}  docs={len(prods[pname])}")

print("\n=== CHUNK TEXT QUALITY ===")
print("total chunks:", text_total)
print("chunks where text contains product_name:", text_contains_product,
      f"({100*text_contains_product/max(text_total,1):.1f}%)")
if text_len_samples:
    print("text length: min=%d max=%d avg=%.0f median=%.0f" % (
        min(text_len_samples), max(text_len_samples),
        sum(text_len_samples)/len(text_len_samples),
        sorted(text_len_samples)[len(text_len_samples)//2]))

print("\n=== ALL DISTINCT product_names ===")
for pn in sorted(prod_names_seen):
    print("  ", repr(pn))
