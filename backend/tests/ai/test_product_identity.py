import copy
from dataclasses import replace
from hashlib import sha256
import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.ai.rag.product_identity import build_catalog, ProductIdentityResolver, COLLECTION, normalize
from app.ai.rag.hierarchical_rag_v2 import RAGSource
from app.ai.rag.answer_validation_v2 import validate_claims
from app.ai.rag.semantic_safety_v2 import check_context, validate_semantics, SemanticSafetyError


def corpus(specs):
    docs=[]; rows=[]; sources=[]
    for i,(filename,full,excerpt) in enumerate(specs):
        did=f'd{i}'; cid=f'c{i}'; path='raw/'+filename
        docs.append(dict(document_id=did,file_name=filename,source_path=path,pages=[dict(raw_text=full)],
            _chunk_ids=[cid],_extraction_sha256=sha256(full.encode()).hexdigest()))
        rows.append(dict(document_id=did,file_name=filename,source_path=path,chunk_id=cid,text=excerpt))
        sources.append(RAGSource(f'SOURCE {i+1}',cid,did,filename,path,1,1,[], 'paragraph',1,excerpt))
    catalog=build_catalog(docs,rows,'test-digest')
    return ProductIdentityResolver(catalog),sources,catalog


def claims(source, question):
    return validate_claims(json.dumps(dict(status='answered',claims=[dict(text=source.text,support_chunk_ids=[source.chunk_id])])),[source],question)


def test_exact_code_and_normalization():
    r,_,_=corpus([('AX123.pdf','AX123\nPoids : 2 kg.','Poids : 2 kg.')])
    for query in ('AX123','ax123','AX-123','AX 123'):
        assert r.resolve(query).safe
        assert r.resolve(query).resolved_product_ids==r.resolve('AX123').resolved_product_ids


def test_repeated_full_title_corroborates_short_filename():
    r, sources, catalog = corpus([
        ('fiche_technique_pap2.pdf', 'LIKA PAP2\n\nLIKA PAP2\nPLATRE A PROJETER\nPoids : 2 kg.', 'Poids : 2 kg.'),
        ('fiche_technique_fina.pdf', 'LIKA FINA est un enduit.', 'Poids : 3 kg.'),
    ])
    question = 'Quelles sont les caractéristiques de Lika PAP2 ?'
    assert r.resolve(question).safe
    assert catalog['documents'][0]['candidate_canonical_product_name'] == 'lika pap2'
    assert r.ownership(sources[0]) == set(r.resolve(question).resolved_product_ids)
    validate_semantics(claims(sources[0], question), sources, question, r)
    with pytest.raises(SemanticSafetyError, match='wrong_target_product'):
        validate_semantics(claims(sources[1], question), sources, question, r)
    assert not r.resolve('Lika PAP2 PLUS').safe


@pytest.mark.parametrize('text', [
    'Poids : 2 kg.',
    'LIKA PAP2\nPoids : 2 kg.',
    'Convient pour LIKA PAP2.\nConvient pour LIKA PAP2.',
    'LIKA PAP20\nLIKA PAP20',
    'LIKA PAP2\nLIKA PAP2\nOMEGA PAP2\nOMEGA PAP2',
])
def test_short_filename_does_not_license_unverified_title(text):
    r, sources, _ = corpus([('fiche_technique_pap2.pdf', text, 'Poids : 2 kg.')])
    assert not r.resolve('LIKA PAP2').safe
    assert not r.ownership(sources[0])


def test_alias_and_url_filename_equivalent():
    r,s,c=corpus([('OMEGA%20FULL%20V4.pdf','OMEGA FULL est un enduit.','Poids : 2 kg.')])
    for q in ('omega-full','OMEGA FULL V4.pdf','OMEGA%20FULL%20V4.pdf'):
        assert r.resolve(q).safe
    assert r.ownership(s[0])==set(r.resolve('OMEGA FULL').resolved_product_ids)


def test_distinct_family_and_partial_ambiguity():
    r,_,_=corpus([('OMEGA-FULL.pdf','OMEGA FULL est un enduit.','Poids : 2 kg.'),
        ('OMEGA-FINA.pdf','OMEGA FINA est un enduit.','Poids : 3 kg.')])
    assert r.resolve('OMEGA FULL').resolved_product_ids!=r.resolve('OMEGA FINA').resolved_product_ids
    assert not r.resolve('OMEGA').safe
    assert r.resolve('OMEGA').ambiguous_candidates
    for q in ('OMEGA PRO','omega full eco','OMEGA FULL ECO','AX999','AX 999'):
        assert not r.resolve(q).safe


def test_duplicate_identity_and_provenance():
    r,s,c=corpus([('OMEGA-FULL.pdf','OMEGA FULL est un enduit.','Poids : 2 kg.'),
        ('FULL.pdf','OMEGA FULL est un enduit.','Poids : 2 kg.')])
    assert len(c['products'])==1
    assert len(c['products'][0]['source_files'])==2
    assert c['documents'][0]['duplicate_documents']
    assert r.ownership(s[0])==r.ownership(s[1])


def test_accessory_reference_not_ownership():
    r,s,c=corpus([('AX123.pdf','AX123\nConvient pour BX456.\nBX456','Convient pour BX456.')])
    assert r.resolve('AX123').safe
    assert not r.resolve('BX456').safe
    assert c['documents'][0]['compatibility_references']==['bx456']
    assert r.ownership(s[0])


def test_mixed_headings_quarantined():
    r,s,c=corpus([('AX123.pdf','AX123\nBX456\nPoids : 2 kg.','Poids : 2 kg.')])
    assert not r.ownership(s[0]); assert not r.resolve('AX123').safe
    assert 'incompatible_owner_headings' in c['documents'][0]['ambiguity_conflict_flags']


def test_explicit_filename_disagreement():
    r,s,c=corpus([('OMEGA-FULL.pdf','OMEGA FINA est un enduit.','Poids : 2 kg.')])
    assert not r.ownership(s[0])
    assert 'filename_declaration_disagreement' in c['documents'][0]['ambiguity_conflict_flags']


def test_no_fragment_name_requirement_and_wrong_product_rejection():
    r,s,_=corpus([('OMEGA-FULL.pdf','OMEGA FULL est un enduit.','Poids : 2 kg.'),
        ('OMEGA-FINA.pdf','OMEGA FINA est un enduit.','Poids : 2 kg.')])
    question='Quel poids pour OMEGA FULL ?'
    validate_semantics(claims(s[0],question),s,question,r)
    with pytest.raises(SemanticSafetyError,match='wrong_target_product'):
        validate_semantics(claims(s[1],question),s,question,r)


def test_comparison_requires_both_identities():
    r,s,_=corpus([('AX123.pdf','AX123','Poids : 2 kg.'),('BX456.pdf','BX456','Poids : 3 kg.')])
    q='Compare AX123 et BX456.'
    assert len(r.resolve(q).resolved_product_ids)==2
    with pytest.raises(SemanticSafetyError): check_context(q,[s[0]],r)
    with pytest.raises(SemanticSafetyError,match='incomplete_target_coverage'):
        validate_semantics(claims(s[0],q),s,q,r)
    validate_semantics(claims(s[0],q)+claims(s[1],q),s,q,r)


def test_conflict_preserved_between_duplicate_documents():
    r,s,_=corpus([('OMEGA-FULL.pdf','OMEGA FULL est un enduit.','Puissance : 750 W.'),
        ('FULL.pdf','OMEGA FULL est un enduit.','Puissance : 900 W.')])
    with pytest.raises(SemanticSafetyError,match='contradictory'):
        check_context('Quelle puissance pour OMEGA FULL ?',s,r)


def test_exact_text_and_metadata_binding():
    r,s,_=corpus([('AX123.pdf','AX123','Poids : 2 kg.')])
    assert r.ownership(s[0])
    assert not r.ownership(replace(s[0],text=s[0].text+' '))
    assert not r.ownership(replace(s[0],source_path='other'))
    assert not r.ownership(replace(s[0],file_name='alias.pdf'))


def test_collection_isolation_and_defensive_copy():
    r,s,c=corpus([('AX123.pdf','AX123','Poids : 2 kg.')])
    c['documents'].clear(); assert r.ownership(s[0])
    bad=copy.deepcopy(r._catalog);bad['collection']='buildlearn_products'
    with pytest.raises(ValueError):ProductIdentityResolver(bad)


def test_concurrent_resolution_deterministic():
    r,_,_=corpus([('AX123.pdf','AX123','Poids : 2 kg.')])
    with ThreadPoolExecutor(max_workers=8) as pool:
        out=list(pool.map(r.resolve,['AX123']*40))
    assert all(x==out[0] for x in out)


def test_real_catalog_inventory_and_conflict_quarantine():
    r=ProductIdentityResolver.load()
    assert len(r._catalog['documents'])==221
    assert sum(len(d['child_text_sha256']) for d in r._catalog['documents'])==2637
    assert len({d['document_id'] for d in r._catalog['documents']})==218
    assert r.resolve('MURENDUIT B').safe
    assert r.resolve('MURENDUIT R').safe
    assert r.resolve('MURENDUIT B').resolved_product_ids!=r.resolve('MURENDUIT R').resolved_product_ids
    assert not r.resolve('MURENDUIT').safe
    assert not r.resolve('ETCT1653').safe


def test_no_standard_ids():
    assert not ProductIdentityResolver.load().resolve('EN12004 et DTU52').safe


def test_known_entity_does_not_hide_unknown():
    r,_,_=corpus([('AX123.pdf','AX123','Poids : 2 kg.')])
    assert not r.resolve('AX123 et OMEGA FULL').safe
    assert not r.resolve('AX123 et BX 999').safe


def test_exact_name_precedes_longer_family_prefix():
    r,_,_=corpus([('ALPHA.pdf','ALPHA est un enduit.','Poids : 2 kg.'),
        ('ALPHA-MAX.pdf','ALPHA MAX est un enduit.','Poids : 3 kg.')])
    assert r.resolve('ALPHA').safe
    assert r.resolve('ALPHA MAX').safe
    assert r.resolve('ALPHA').resolved_product_ids!=r.resolve('ALPHA MAX').resolved_product_ids


def test_question_grammar_and_numbers_are_not_unknown_entities():
    r,_,_=corpus([('CX789.pdf','CX789','Poids : 2 kg.'),
        ('SIGMA-FLEX-120-Z.pdf','SIGMA FLEX 120 Z est un enduit.','Poids : 3 kg.')])
    assert r.resolve('CX789 protects eyes?').safe
    assert r.resolve('CX789 a-t-il une protection ?').safe
    assert r.resolve('Quel volume de 25 litres pour CX789 ?').safe
    assert r.resolve('Quelle composition de SIGMA FLEX 120 Z ?').safe


def test_sidecar_rejects_stale_checkpoint_and_extraction(tmp_path):
    from app.ai.rag.product_identity import CATALOG
    original=json.loads(CATALOG.read_text(encoding='utf8'))
    bad=copy.deepcopy(original);bad['checkpoint_sha256']='stale'
    p=tmp_path/'catalog.json';p.write_text(json.dumps(bad),encoding='utf8')
    with pytest.raises(ValueError,match='checkpoint mismatch'):ProductIdentityResolver.load(p)
    bad=copy.deepcopy(original)
    for d in bad['documents']:d['extraction_sha256']='stale'
    p.write_text(json.dumps(bad),encoding='utf8')
    with pytest.raises(ValueError,match='corpus mismatch'):ProductIdentityResolver.load(p)


def test_permission_validator_still_requires_polarity_and_object():
    r,s,_=corpus([('AX123.pdf','AX123','Dimensions : 20 mm.')])
    with pytest.raises(SemanticSafetyError,match='unqualified_permission'):
        validate_semantics(claims(s[0],'Quelle dimension pour AX123 ?'),s,'Can AX123 be used on metal?',r)
    r,s,_=corpus([('AX123.pdf','AX123','Ne pas appliquer sur metal.')])
    validate_semantics(claims(s[0],'Can AX123 be used on metal?'),s,'Can AX123 be used on metal?',r)
