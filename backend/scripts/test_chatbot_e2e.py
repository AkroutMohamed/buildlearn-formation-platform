import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('AI_ENABLED','true')

from app.config import _load_dotenv
_load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.ai.rag.rag_service import RAGService
from app.ai.schemas.chat import ChatRequest, ChatResponse

engine = create_engine(os.environ['DATABASE_URL'])
SessionLocal = sessionmaker(bind=engine)

queries = [
    'Bonjour',
    'Quelles sont les caracteristiques du Lika PAP2?',
    'Donnez-moi la consommation du Mura colle platre',
    'Quels produits SOFAP sont documentes?',
    'Quels produits EMTOP sont documentes?',
    'Quels produits de Gypsobat sont documentes?',
    'Quelle est la consommation du produit?',
    'Comment utiliser le PRO 3000 de SOFAP?',
    'Quels sont les produits de construction?',
    'Parlez-moi de la resistance en flexion',
]

rag = RAGService()
db = SessionLocal()

for q in queries:
    try:
        req = ChatRequest(question=q)
        resp = rag.run(req, history=[])
        print('Q:', q)
        print('A:', (resp.answer or '')[:500].replace(chr(10), ' '))
        print('Sources:', len(resp.sources or []))
        for s in (resp.sources or [])[:3]:
            score = s.get('score')
            score_str = f' score={score:.3f}' if isinstance(score, (int, float)) else ''
            print(f'  - {s.get("product_name")} ({s.get("document_type","?")}, conf={s.get("confidence")}){score_str} supplier={s.get("supplier")}')
        print()
    except Exception as exc:
        print('Q:', q)
        print('  ERROR:', exc)
        print()