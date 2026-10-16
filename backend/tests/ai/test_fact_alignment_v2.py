from hashlib import sha256
import json

import pytest

from app.ai.rag.fact_alignment_v2 import requested_facts, matches, validate_fact_alignment, context_coverage
from app.ai.rag.hierarchical_rag_v2 import RAGSource
from app.ai.rag.product_identity import build_catalog, ProductIdentityResolver
from app.ai.rag.semantic_safety_v2 import validate_semantics, SemanticSafetyError, resolve_targets
from app.ai.rag.answer_validation_v2 import validate_claims


def setup(texts, filenames=None):
    sources=[];docs=[];rows=[]
    for i,text in enumerate(texts):
        filename=(filenames or ['AX123.pdf']*len(texts))[i];did=f'd{i}';cid=f'c{i}';path=f'raw/{i}/{filename}'
        code=filename.split('.')[0];full=code+'\n'+text
        docs.append(dict(document_id=did,file_name=filename,source_path=path,pages=[dict(raw_text=full)],_chunk_ids=[cid],_extraction_sha256=sha256(full.encode()).hexdigest()))
        rows.append(dict(document_id=did,file_name=filename,source_path=path,chunk_id=cid,text=text))
        sources.append(RAGSource(f'SOURCE {i+1}',cid,did,filename,path,1,1,[], 'paragraph',1,text))
    resolver=ProductIdentityResolver(build_catalog(docs,rows,'test'))
    return resolver,sources


def validate(q,texts,filenames=None,choose=None):
    resolver,sources=setup(texts,filenames)
    selected=[sources[i] for i in (choose if choose is not None else range(len(sources)))]
    raw=json.dumps(dict(status='answered',claims=[dict(text=s.text,support_chunk_ids=[s.chunk_id])for s in selected]))
    claims=validate_claims(raw,sources,q)
    validate_semantics(claims,sources,q,resolver)
    return validate_fact_alignment(claims,sources,q,resolver)


@pytest.mark.parametrize('q,text',[
    ('What minimum thickness for AX123?','Maximum thickness : 20 mm.'),
    ('What maximum pressure for AX123?','Minimum pressure : 2 bar.'),
    ('What minimum first-pass thickness for AX123?','Maximum total thickness : 20 mm.'),
    ('Quelle epaisseur pour la premiere passe de AX123 ?','Epaisseur totale : 20 mm.'),
    ('What exact voltage for AX123?','Voltage : 220-240 V.'),
    ('What voltage range for AX123?','Voltage : 230 V.'),
    ('What pressure in psi for AX123?','Pressure : 8 bar.'),
    ('Quelle puissance pour AX123 ?','Tension : 20 V.'),
    ('Quels supports sont interdits pour AX123 ?','AX123 est un enduit decoratif.'),
])
def test_requested_fact_mismatches_rejected(q,text):
    with pytest.raises(ValueError):validate(q,[text])


@pytest.mark.parametrize('q,text',[
    ('What minimum first-pass thickness for AX123?','First pass (minimum 7 mm) is applied with a trowel.'),
    ('What maximum pressure in bar for AX123?','Maximum pressure : 8 bar.'),
    ('What exact voltage for AX123?','Voltage : 230 V.'),
    ('What voltage range for AX123?','Voltage : 220-240 V.'),
    ('Quelle consommation en kg/m2 pour AX123 ?','Consommation : 2 kg/m2.'),
])
def test_aligned_values_accepted(q,text):
    assert validate(q,[text])


def test_two_facts_require_all_slots():
    with pytest.raises(SemanticSafetyError,match='incomplete_requested_fact_coverage'):
        validate('Quelle tension et quelle puissance pour AX123 ?',['Tension : 20 V.'])
    assert len(validate('Quelle tension et quelle puissance pour AX123 ?',['Tension : 20 V.','Puissance : 900 W.']))==2


def test_two_units_require_all_slots():
    q='What pressure in bar and psi for AX123?'
    with pytest.raises(SemanticSafetyError,match='incomplete_requested_fact_coverage'):validate(q,['Pressure : 8 bar.'])
    assert validate(q,['Pressure : 8 bar / 116 psi.'])


def test_two_units_with_second_attribute():
    facts=requested_facts('Pressure in bar and psi and voltage in V?',{'p'})
    assert {(f.attribute,f.unit)for f in facts}=={('pressure','bar'),('pressure','psi'),('voltage','v')}


def test_attribute_local_qualifiers():
    f=requested_facts('Minimum pressure and exact voltage for AX123?',{'p'})
    assert [(s.attribute,s.numeric_qualifier)for s in f]==[('pressure','minimum'),('voltage','exact')]


def test_allowed_prohibited_polarity():
    with pytest.raises(SemanticSafetyError):validate('Quels supports sont interdits pour AX123 ?',['Supports admissibles : beton.'])
    assert validate('Quels supports sont interdits pour AX123 ?',['Supports interdits : metal.'])
    with pytest.raises(SemanticSafetyError):validate('What supports are allowed for AX123?',['Prohibited supports : metal.'])
    assert validate('What supports are allowed for AX123?',['Allowed supports : concrete.'])


def test_comparison_covers_facts_for_each_product():
    q='Compare voltage and power of AX123 and BX456.'
    texts=['Voltage : 20 V.\nPower : 900 W.','Voltage : 18 V.']
    with pytest.raises(SemanticSafetyError,match='incomplete_requested_fact_coverage'):validate(q,texts,['AX123.pdf','BX456.pdf'])
    assert validate(q,[texts[0],'Voltage : 18 V.\nPower : 700 W.'],['AX123.pdf','BX456.pdf'])


def test_wrong_product_not_rescued_by_matching_fact():
    with pytest.raises(SemanticSafetyError,match='wrong_target_product'):
        validate('Quelle tension pour AX123 ?',['Tension : 20 V.','Tension : 20 V.'],['AX123.pdf','BX456.pdf'],choose=[1])


def test_context_gap_recorded_separately():
    r,s=setup(['Tension : 20 V.']);targets,owners=resolve_targets('Tension et puissance pour AX123 ?',s,r)
    missing=context_coverage(requested_facts('Tension et puissance pour AX123 ?',targets),s,owners)
    assert [f['attribute']for f in missing]==['power']


@pytest.mark.parametrize('word',['combien','faut','permet','quelle','quels','quelles'])
def test_french_question_words_are_not_entity_suffixes(word):
    r=ProductIdentityResolver.load()
    assert r.resolve(f'MURENDUIT B : {word} de poudre ?').safe


@pytest.mark.parametrize('q',['MURENDUIT GOLD','MURENDUIT B PRO','MURENDUIT','LIKA FULL UNKNOWN','PRIMER CONTACT PRO-X'])
def test_unknown_variants_and_families_still_fail_closed(q):
    assert not ProductIdentityResolver.load().resolve(q).safe


def test_no_unrequested_numeric_fact_or_claim_can_hide_in_answer():
    with pytest.raises(SemanticSafetyError,match='requested_fact_mismatch'):
        validate('What voltage for AX123?',['Voltage : 20 V.','Pressure : 8 bar.'])


def test_attribute_cannot_use_digits_in_product_code_as_numeric_value():
    fact=requested_facts('Quelle tension pour AX123 ?',{'p'})[0]
    assert not matches(fact,'AX123 tension inconnue.')


def test_no_load_and_bore_conditions():
    assert not matches(requested_facts('What no-load speed?',{'p'})[0],'Speed : 500 rpm.')
    assert not matches(requested_facts('Quel alesage ?',{'p'})[0],'Diametre exterieur : 20 mm.')


def test_unknown_fact_type_is_explicitly_out_of_scope():
    assert requested_facts('De quelle couleur est AX123 ?',{'p'})==()


def test_repeated_attribute_and_shared_attribute_min_max_slots():
    for q in ('Minimum pressure and maximum pressure for AX123?', 'Minimum and maximum pressure for AX123?'):
        assert {f.numeric_qualifier for f in requested_facts(q,{'p'})}=={'minimum','maximum'}
        with pytest.raises(SemanticSafetyError):validate(q,['Maximum pressure : 8 bar.'])
        assert validate(q,['Minimum pressure : 2 bar.','Maximum pressure : 8 bar.'])


def test_standard_and_classification_are_distinct_required_facts():
    q='What standard and classification for AX123?'
    facts=requested_facts(q,{'p'})
    assert {f.condition for f in facts}=={'standard','classification'}
    with pytest.raises(SemanticSafetyError):validate(q,['Standard : EN12004.'])
    assert validate(q,['Standard : EN12004.','Class C2TE.'])


def test_width_and_height_are_distinct_dimension_slots():
    q='What width and height for AX123?'
    with pytest.raises(SemanticSafetyError):validate(q,['Width : 20 mm.'])
    assert validate(q,['Width : 20 mm.','Height : 30 mm.'])


def test_tolerance_is_not_an_exact_value():
    f=requested_facts('What exact weight?',{'p'})[0]
    assert not matches(f,'Weight : 5 +/- 2 kg.')


def test_recorded_context_metadata_and_rejection_are_private_api_fields():
    from app.ai.api.rag_v2_endpoint import _rejection_reason, V2ChatResponse
    assert _rejection_reason(['Semantic safety rejected: incomplete_requested_fact_coverage'])=='incomplete_requested_fact_coverage'
    assert 'requested_facts' not in V2ChatResponse.model_fields
    assert 'missing_context_facts' not in V2ChatResponse.model_fields


@pytest.mark.parametrize('q,text',[
    ('What voltage in V for AX123?','Voltage : 18V.'),
    ('What torque in Nm for AX123?','Torque : 75Nm.'),
    ('What length in mm for AX123?','Length : 234mm.'),
    ('What maximum pressure in bar for AX123?','Maximum pressure : 8 bars.'),
    ('What maximum pressure in bar and psi for AX123?','Maximum pressure :\n8 bars (116psi).'),
])
def test_attached_and_multiline_units(q,text):
    assert validate(q,[text])


def test_numbered_description_does_not_establish_numeric_pressure():
    f=requested_facts('What pressure for AX123?',{'p'})[0]
    assert not matches(f,'2. Material has high resistance to pressure.')


def test_numeric_fact_needs_a_dimensionally_appropriate_unit():
    assert not matches(requested_facts('What pressure?',{'p'})[0],'Pressure : 20 V.')


def test_two_diameter_conditions_require_both():
    q='What inner diameter and outer diameter for AX123?'
    with pytest.raises(SemanticSafetyError):validate(q,['Inner diameter : 5 mm.'])
    assert validate(q,['Inner diameter : 5 mm; outer diameter : 8 mm.'])


def test_unit_cannot_be_borrowed_from_another_attribute():
    f=requested_facts('What exact voltage in V?',{'p'})[0]
    assert not matches(f,'Voltage : unknown. Power : 20 V.')


def test_attribute_cannot_borrow_another_dimensions_value():
    f=requested_facts('What outer diameter?',{'p'})[0]
    assert not matches(f,'Inner diameter : 5 mm; outer diameter : unknown.')


def test_first_pass_and_total_are_two_required_stages():
    q='What first-pass and total thickness for AX123?'
    with pytest.raises(SemanticSafetyError):validate(q,['Total thickness : 20 mm.'])
    assert validate(q,['First pass : 7 mm.','Total thickness : 20 mm.'])


def test_negated_range_is_not_a_required_range_slot():
    f=requested_facts('What exact voltage without a range?',{'p'})[0]
    assert f.numeric_qualifier=='exact'
    assert not matches(f,'Voltage : 220-240 V.')


@pytest.mark.parametrize('value',['110-120V','110–120V','110 to 120V','between 110 and 120V'])
def test_attached_range_cannot_satisfy_exact_value(value):
    text='Voltage : '+value+'.'
    assert not matches(requested_facts('What exact voltage in V?',{'p'})[0],text)
    assert matches(requested_facts('What voltage range in V?',{'p'})[0],text)


def test_minute_unit_does_not_become_minimum_qualifier():
    f=requested_facts('What maximum speed in tr/min?',{'p'})[0]
    assert f.numeric_qualifier=='maximum'
    assert matches(f,'Maximum speed : 1200 tr/min.')
    assert requested_facts('What speed range in tr/min?',{'p'})[0].numeric_qualifier=='range'


def test_abbreviated_maximum_does_not_split_attribute_from_value():
    assert matches(requested_facts('What maximum torque in Nm?',{'p'})[0],'Torque max. : 75Nm.')


def test_range_word_without_two_bounds_is_not_a_numeric_range():
    assert not matches(requested_facts('What voltage range?',{'p'})[0],'Voltage range : 230 V.')
