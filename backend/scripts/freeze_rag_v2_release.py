"""Freeze fresh release labels from actual indexed evidence before any generation."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
import app.config
from qdrant_client import QdrantClient
from scripts.evaluate_hierarchical_retrieval import read_collection, LABELS
from scripts.evaluate_rag_v2 import protected, NEGATIVES
from scripts.shadow_rag_v2_chat import QUERIES
from app.ai.retrieval.retrieval_v2 import LexicalIndex


def main():
    target = BACKEND / 'tests/ai/fixtures/rag_v2_release_acceptance.json'
    if target.exists(): raise RuntimeError('Release acceptance already frozen; do not overwrite consumed labels')
    queries = {q['query'] for q in LABELS + NEGATIVES} | {q[1] for q in QUERIES}
    used = {e['file_name'] for q in LABELS for e in q['evidence']}
    prior = {}
    def walk(value):
        if isinstance(value, dict):
            for key in ('query', 'question'):
                if isinstance(value.get(key), str): queries.add(value[key])
            for e in value.get('evidence', []) if isinstance(value.get('evidence', []), list) else []:
                if isinstance(e, dict) and e.get('file_name'): used.add(e['file_name'])
            if value.get('expected_file'): used.add(value['expected_file'])
            for v in value.values(): walk(v)
        elif isinstance(value, list):
            for v in value: walk(v)
    for path in list((BACKEND / 'tests/ai/fixtures').glob('*.json')) + list((BACKEND.parent / 'docs/ai').glob('*.json')):
        prior[str(path.relative_to(BACKEND.parent))] = hashlib.sha256(path.read_bytes()).hexdigest()
        walk(json.loads(path.read_text(encoding='utf-8')))
    client = QdrantClient(url='http://127.0.0.1:6333')
    rows, digest = read_collection(client)
    by_id = {r['chunk_id']: r for r in rows}
    labels = []
    def add(qid, query, expected, category, chunks=(), required=(), rationale=''):
        assert query not in queries and query not in {q['query'] for q in labels}
        evidence = [{k: by_id[c][k] for k in ('chunk_id', 'document_id', 'file_name', 'source_path', 'text', 'page_start', 'page_end')}
                    for c in chunks]
        labels.append(dict(id=qid, query=query, expected=expected, category=category,
                           evidence=evidence, required_facts=list(required), rationale=rationale))
    positives = [
        ('What is the maximum speed in RPM for EACD101251?', 'English numeric', ['610d541b1302ab5e'], ['12200']),
        ('Quels diametres interieur et exterieur indique EAHE1001 ?', 'French multi-fact units', ['40c37a86a186b51f'], ['5mm', '8mm']),
        ('Pour EAHE1501, quelle longueur et quelle pression maximale sont indiquees ?', 'multi-fact', ['2d80fcb5cc71ea9d'], ['15M', '12 bar']),
        ('Quelle est la consommation d air de EAPR15001 en cfm et l/min ?', 'numeric units', ['0c9d5f3b9fb24a25'], ['3 cfm', '84 l/min']),
        ('What is the sanding pad size of EAPR15001?', 'English dimensions', ['1ccc59d0f4d6aae2'], ['150 mm']),
        ('Quelle capacite de peinture et quelle buse standard pour EASG04001 ?', 'multi-fact', ['64818adbd4b199c1'], ['400 cc', '1,5 mm']),
        ('Quelle longueur de buse indique EASGB0301 ?', 'supported product', ['20d881987a4e8551'], ['16 mm']),
        ('Quelle pression maximale en bars et psi pour EASGT8501 ?', 'numeric units', ['c767e3e9922ae9e7'], ['8,5 bars', '120 psi']),
        ('A quelles utilisations de nettoyage est destine EASGW10011 ?', 'application', ['9177945ad4f02c76'], ['voiture', 'mécaniques']),
        ('Quelle pression de fonctionnement et quelle capacite de lavage pour EASGW10011 ?', 'multi-fact', ['6a751886e1fa5a30'], ['4 bar', '0,75 L']),
        ('Quels materiaux peut couper EACDH302301 et quel diametre a le disque ?', 'multi-fact', ['5a22b32f02324b82'], ['acier inoxydable', '230mm']),
        ('Pour EACD601151, donne les trois dimensions du disque de meulage.', 'dimensions', ['99707463429445ca'], ['115mm', '6.0mm', '22.2mm']),
        ('Quel est le diametre exterieur du tuyau EAHE1501 ?', 'supported product', ['f5da3c0afdf1d435'], ['8 mm']),
        ('Quelle presssion maximale supportee indique EAHE1001 ?', 'misspelled common word', ['4e9656b6981faaa6'], ['12 bar']),
        ('Quel connecteur uniquement est indique pour EAHE1001 ?', 'compatibility limitation', ['4f4152f1086a9be0'], ['Europe']),
        ('Compare les longueurs indiquees pour EAHE1001 et EAHE1501.', 'comparison two sources', ['4e9656b6981faaa6', '2d80fcb5cc71ea9d'], ['10M', '15M']),
        ('Quel diametre et quelle epaisseur pour le disque EACD101151 ?', 'split evidence numeric', ['37b04944a8979c46', '573d97d7514ced5b'], ['115', '1,0 mm']),
        ('LIKA FULL : quels supports sont interdits, notamment les supports horizontaux ?', 'prohibited substrates', ['71e680d35400bbf3'], ['Supports Interdits', 'Support horizontal']),
        ('Peut-on utiliser LIKA FULL sur des supports metalliques ou peints ?', 'prohibited compatibility', ['71e680d35400bbf3'], ['Supports Interdits', 'métallique, peint']),
        ('JIR PRO ETANCHE peut-il etre applique directement sur les anciennes finitions organiques ?', 'prohibited compatibility', ['ad360a38e8ae8111'], ['Ne pas appliquer', 'organiques']),
        ('Pour quels murs est destine LIKA FULL et quelle norme le classe ?', 'allowed application multi-fact', ['ceaa0295d4a43ae2'], ['murs extérieurs', 'EN 998-1']),
        ('What connector type is permitted for EAHE1501 according to its limitation?', 'English compatibility', ['cfbce7863a8aa69e'], ['Europe']),
    ]
    for i, (query, category, chunks, facts) in enumerate(positives, 1):
        add(f'A{i:02}', query, 'answered', category, chunks, facts)
    negatives = [
        ('Quel est le prix de vente actuel du tuyau EAHE1001 en dinars ?', 'current price', [], 'No indexed price; technical sheet is not a current price list.'),
        ('How many years of manufacturer warranty are guaranteed for EASGT8501?', 'current warranty English', [], 'No warranty terms in this product sheet.'),
        ('Quelle est la tension de cet appareil sans autre precision ?', 'ambiguous identity French', [], 'No product specified.'),
        ('What voltage does that tool use?', 'ambiguous identity English', [], 'No product specified.'),
        ('Et quelle est sa longueur ?', 'vague follow-up', [], 'Standalone query has no explicit product; history must not silently select one.'),
        ('Can you give its maximum working pressure now?', 'vague follow-up English', [], 'No explicit product identity.'),
        ('Quelle pression pour EAHE10?? ?', 'partial identifier', [], 'Incomplete reference; no assumed repair.'),
        ('Quelle buse equipe EASG04 ?', 'truncated identifier', [], 'Reference is not an exact corpus identifier.'),
        ('Quelle longueur pour EAHE1O01 avec la lettre O ?', 'identifier typo', [], 'Unknown typo reference; no automatic identifier correction.'),
        ('What are the dimensions of ZZRX742839?', 'unknown reference English', [], 'Identifier absent from indexed filenames.'),
        ('Peut-on utiliser EAHE1001 comme tuyau pour une perfusion medicale ?', 'unsupported compatibility', [], 'No medical authorization or evidence.'),
        ('Quelle est la pression maximale de EAHE1501 et sa certification pour oxygenotherapie ?', 'partly unsupported multi-fact', [], 'Pressure exists but medical certification is absent; cannot answer all parts.'),
        ('Compare les pressions de EAHE1001 et ZZRX742839.', 'comparison unknown reference', [], 'Second product does not exist.'),
        ('Does EACD101251 have permission for underwater electrical use?', 'unsupported English', [], 'No authorization in evidence.'),
        ('ETCT1653 est-il sans aucun doute un poste de soudage et non une lame de scie ?', 'contradictory source', ['11eac5e8bb98fd1d', '3bf24376b9bbf086', '415ecffb919c713c'], 'Sheet mixes welding applications, blade dimensions and ELCS1652 identity; definitive product assertion is unsafe.'),
        ('Donne les dimensions exactes avec roulettes de ETCS0402 avec une preuve complete et non une ligne isolee.', 'incomplete source evidence', ['4b3eb9c29133ad5a', 'ef2b227172cdccac'], 'Label and dimensions are split; require complete attributable evidence or abstain, not an unqualified detached number.'),
        ('Peut-on appliquer LIKA FULL sur absolument tous les supports sans restriction ?', 'overbroad allowed compatibility', ['71e680d35400bbf3'], 'A blanket permission is contradicted; abstention or explicit cited refusal is safe.'),
        ('Quelle dose injectable de JIR PRO ETANCHE recommandez-vous a un enfant ?', 'unsupported safety', [], 'Construction coating, no medical dose.'),
    ]
    for i, (query, category, chunks, why) in enumerate(negatives, 1):
        # Explicit qualified refusal/conflict reporting is allowed for these cases;
        # arbitrary source excerpts are not automatically counted as safe refusals.
        expected = 'abstain_or_qualified_refusal' if i in (15, 16, 17) else 'insufficient'
        add(f'N{i:02}', query, expected, category, chunks, rationale=why)
    assert len(labels) == 40
    assert all(e['file_name'] not in used for q in labels if q['expected'] == 'answered' for e in q['evidence'])
    for ref in ('ZZRX742839', 'EAHE1O01', 'EASG04'):
        assert ref not in LexicalIndex(rows).catalog
    assert not any(w in r['text'].casefold() for r in rows if r['file_name'].startswith(('EAHE1001%', 'EASGT8501%'))
                   for w in ('prix', 'garantie', 'warranty'))
    output = dict(freeze=dict(utc=datetime.now(timezone.utc).isoformat(), collection_sha256=digest,
                             protected=protected(), prior_artifact_hashes=prior, prior_query_count=len(queries),
                             protocol='Frozen before generation. Fresh queries and supported evidence sources disjoint from earlier labels. No tuning.'),
                  labels=labels)
    target.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Frozen 40 release queries: ' + str(target))
    print('Acceptance SHA256: ' + hashlib.sha256(target.read_bytes()).hexdigest())
    client.close()


if __name__ == '__main__': main()
