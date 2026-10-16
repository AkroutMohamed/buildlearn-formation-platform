import os
os.environ.setdefault('EMBEDDING_PROVIDER','ollama')
os.environ.setdefault('EMBEDDING_MODEL','nomic-embed-text')
os.environ.setdefault('VECTOR_STORE','qdrant')
os.environ.setdefault('QDRANT_URL','http://localhost:6333')
os.environ.setdefault('QDRANT_COLLECTION','buildlearn_products')
os.environ.setdefault('OLLAMA_BASE_URL','http://localhost:11434')

from app.ai.rag.retriever import Retriever
from app.ai.vectorstore.provider import VectorStore
from app.ai.embeddings.provider import EmbeddingProvider

emb = EmbeddingProvider()
vs = VectorStore()
print('Dimension:', emb.dimension)
print('Vector store:', type(vs).__name__)
r = Retriever()
queries = [
    'Lika PAP2 resistance en flexion',
    'Mura colle platre consommation',
    'enduit SOFAP caracteristiques',
    'PRO 1000 SOFAP fiche technique',
    'Quels produits de Gypsobat sont documentes?',
    'Quels produits EMTOP sont documentes?',
    'Quels produits SOFAP sont documentes?',
    'Comment utiliser le produit FLEX?',
    'Quelle est la consommation de la colle?',
    'Quelles sont les proprietes du produit?',
]
for q in queries:
    res = r.retrieve(q)
    print('Q:', q)
    print('  Top hits:')
    for h in res[:3]:
        text = (h.text or '')[:80].replace(chr(10), ' ')
        score = h.score if h.score is not None else 0
        print(f'    - [{score:.3f}] {h.source}/{h.product_name}/{h.document_type} :: {text}')
    print()