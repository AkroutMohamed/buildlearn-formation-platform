import json
from pathlib import Path
import pytest
from app.ai.rag.hierarchical_rag_v2 import RAGSource
from app.ai.rag.answer_validation_v2 import validate_claims
from app.ai.rag.semantic_safety_v2 import validate_semantics, check_context, SemanticSafetyError


def source(text, filename='AX123.pdf', sid='a', doc='doc', sections=None):
    return RAGSource(sid,sid,doc,filename,'raw/'+filename,1,1,sections or [],'paragraph',1.,text)


def check(question, chosen, sources):
    raw=json.dumps(dict(status='answered',claims=[dict(text=chosen.text,support_chunk_ids=[chosen.chunk_id])]))
    claims=validate_claims(raw,sources,question)
    return validate_semantics(claims,sources,question)


def test_valid_same_product_unchanged_extract():
    s=source('Puissance : 750 W.')
    assert check('Quelle puissance AX123 ?',s,[s])[0]['text']==s.text


def test_wrong_product_no_substitution_even_identical_text():
    a=source('Puissance : 750 W.'); b=source(a.text,'BX456.pdf','b','other')
    with pytest.raises(SemanticSafetyError,match='wrong_target_product'):
        check('Quelle puissance AX123 ?',b,[a,b])


def test_named_product_requires_declaration_and_alias_is_not_identity():
    full=source('OMEGA FULL est un enduit.','manual.pdf')
    fina=source('OMEGA FINA est un enduit.','OMEGA FULL.pdf','b','other')
    assert check('Que dit OMEGA FULL ?',full,[full,fina])
    with pytest.raises(SemanticSafetyError,match='wrong_target_product'):
        check('Que dit OMEGA FULL ?',fina,[full,fina])


def test_near_duplicate_names_do_not_alias():
    one=source('OMEGA FULL est un enduit.','one.pdf')
    two=source('OMEGA FULL ECO est un enduit.','two.pdf','b','two')
    with pytest.raises(SemanticSafetyError,match='wrong_target_product'):
        check('Que dit OMEGA FULL ?',two,[one,two])


def test_missing_named_identity_fails_closed():
    s=source('Support horizontal interdit.','OMEGA FULL.pdf')
    with pytest.raises(SemanticSafetyError,match='unresolved'):check('Que dit OMEGA FULL ?',s,[s])


def test_mixed_reference_heading_fails_closed():
    s=source('Coupe du bois.','AX123.pdf',sections=['BX456'])
    with pytest.raises(SemanticSafetyError,match='mixed'):check('Que dit AX123 ?',s,[s])


def test_unrelated_mixed_document_does_not_change_requested_product():
    a=source('Puissance : 750 W.')
    b=source('Coupe du bois.','BX456.pdf','b','other',['CX789'])
    assert check('Quelle puissance AX123 ?',a,[a,b])


def test_contradictory_numeric_field():
    a=source('Puissance : 750 W.')
    b=source('Puissance : 900 W.','AX123.pdf','b')
    with pytest.raises(SemanticSafetyError,match='contradictory'):check('Quelle puissance AX123 ?',a,[a,b])


def test_contradictory_declarations():
    a=source('AX123 est un poste de soudage.')
    b=source('AX123 est une lame de scie.','AX123.pdf','b')
    with pytest.raises(SemanticSafetyError,match='contradictory'):check('Que dit AX123 ?',a,[a,b])


def test_unqualified_yes_no_excerpt_rejected():
    s=source('Diametre : 16 mm.')
    with pytest.raises(SemanticSafetyError,match='unqualified_permission'):
        check('Peut-on utiliser AX123 sur du metal ?',s,[s])


def test_valid_extractive_qualified_refusal():
    s=source('Ne pas appliquer sur le metal.')
    assert check('Peut-on appliquer AX123 sur le metal ?',s,[s])[0]['quote']==s.text


def test_permission_for_unrelated_object_cannot_justify_yes_no():
    s=source('Convient pour le bois.')
    with pytest.raises(SemanticSafetyError,match='permission_object'):
        check('Peut-on appliquer AX123 sur le metal ?',s,[s])


def test_real_identity_allows_filename_aliases():
    a=source('OMEGA FULL est un enduit.','OMEGA_FULL%201.pdf')
    b=source('OMEGA FULL est un enduit.','catalogue-v2.pdf','b','alias')
    assert check('Que dit OMEGA FULL ?',b,[a,b])


def test_two_product_comparison_accepts_both_without_false_conflict():
    a=source('Longueur : 10 mm.');b=source('Longueur : 15 mm.','BX456.pdf','b','other')
    raw=json.dumps(dict(status='answered',claims=[dict(text=s.text,support_chunk_ids=[s.chunk_id]) for s in [a,b]]))
    claims=validate_claims(raw,[a,b],'Compare AX123 et BX456.')
    assert len(validate_semantics(claims,[a,b],'Compare AX123 et BX456.'))==2


def test_unknown_or_ambiguous_identity_fails_closed():
    s=source('Puissance : 750 W.')
    for question in ('Quelle puissance pour CX789 ?', 'Quelle puissance pour cet appareil ?'):
        with pytest.raises(SemanticSafetyError,match='unresolved'):check(question,s,[s])


def test_known_code_cannot_hide_unknown_named_comparison_target():
    s=source('Puissance : 750 W.')
    with pytest.raises(SemanticSafetyError,match='unresolved'):
        check('Compare AX123 et OMEGA FULL.',s,[s])


def test_opposed_permission_same_object():
    a=source('Allowed on metal.'); b=source('Prohibited on metal.','AX123.pdf','b')
    with pytest.raises(SemanticSafetyError,match='contradictory_permission'):
        check('Can AX123 be used on metal?',a,[a,b])


def test_comparisons_require_all_requested_entities():
    a=source('Longueur : 10 mm.');b=source('Longueur : 15 mm.','BX456.pdf','b','other')
    check_context('Compare AX123 et BX456.',[a,b])
    with pytest.raises(SemanticSafetyError,match='incomplete_target_coverage'):
        check('Compare AX123 et BX456.',a,[a,b])


@pytest.mark.parametrize('case', ['A18','N15'])
def test_frozen_release_blocker_exact_old_claim_rejected(case):
    outputs=json.loads((Path(__file__).parents[3]/'docs/ai/rag_v2_release_outputs.json').read_text(encoding='utf-8'))
    labels=json.loads((Path(__file__).parent/'fixtures/rag_v2_release_acceptance.json').read_text(encoding='utf-8'))
    record=next(r for r in outputs['acceptance'] if r['id']==case)
    question=next(q['query'] for q in labels['labels'] if q['id']==case)
    with pytest.raises(SemanticSafetyError):
        validate_semantics(record['audit']['citations'],[RAGSource(**s) for s in record['selected_sources']],question)
