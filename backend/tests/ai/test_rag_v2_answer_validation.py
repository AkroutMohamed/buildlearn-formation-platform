"""Observed failures and adversarial context-scoped support regressions."""
import json
from pathlib import Path
import pytest
from app.ai.rag.hierarchical_rag_v2 import RAGSource
from app.ai.rag.answer_validation_v2 import canonical, support_id, validate_claims

BASELINE = json.loads((Path(__file__).parent / "fixtures/rag_v2_baseline_outputs.json").read_text(encoding="utf-8"))
RECORDS = {r["case"]["id"]: r for r in BASELINE["records"]}


def raw(text, sid, quote=None):
    claim = dict(text=text, support_chunk_ids=[sid])
    if quote is not None:
        claim["quote"] = quote
    return json.dumps(dict(status="answered", claims=[claim]))


def sources(case):
    return [RAGSource(**s) for s in RECORDS[case]["response"]["sources"]]


@pytest.mark.parametrize("case,index,selector", [
    ("HV2-01", 2, "Composition :"),
    ("HV2-02", 0, "6.25 Litres"),
    ("HV2-03", 0, "Verser  le composant  B"),
    ("HV2-07", 0, "DTU 26.1"),
    ("HV2-08", 0, "2 types de mandrins différents"),
    ("HV2-15", 0, "DTU 59.1"),
    ("HV2-16", 0, "FINACEM CACHET ROUGE est un enduit de rebouchage"),
])
def test_seven_observed_quote_failures_have_valid_extractive_evidence(case, index, selector):
    allowed = sources(case)
    result = validate_claims(raw(selector, support_id(allowed[index])), allowed, RECORDS[case]["case"]["query"])
    assert len(result) == 1 and result[0]["quote"] in allowed[index].text
    assert result[0]["text"] == result[0]["quote"]
    assert result[0]["support_chunk_ids"] == [support_id(allowed[index])]


def test_composition_and_conservation_can_both_be_selected():
    allowed = sources("HV2-01")
    result = validate_claims(raw(allowed[2].text, support_id(allowed[2])), allowed)
    assert all(word in result[0]["text"] for word in ["Ciment blanc", "Charges minérales", "10 mois"])


def test_bullet_layout_can_be_resolved_without_changing_original_text():
    allowed = sources("HV2-01")
    selector = "Composition : Ciment blanc. Charges minérales. Additifs spécifiques."
    result = validate_claims(raw(selector, support_id(allowed[2])), allowed)
    assert result[0]["text"] in allowed[2].text
    assert "• Ciment blanc." in result[0]["text"]


def test_unspecified_drill_cannot_answer_by_selecting_one_valid_product():
    allowed = sources("N06")
    with pytest.raises(ValueError, match="identity is ambiguous"):
        validate_claims(raw(allowed[0].text, support_id(allowed[0])), allowed, RECORDS["N06"]["case"]["query"])


def test_prohibition_heading_in_an_alternate_file_cannot_qualify_bare_list():
    allowed = sources("HV2-17")
    allowed[1].text = "Supports Interdits :"
    with pytest.raises(ValueError, match="polarity"):
        validate_claims(raw("Supports horizontaux .", support_id(allowed[0])), allowed, RECORDS["HV2-17"]["case"]["query"])


def test_section_only_prohibition_cannot_be_dropped_from_rendered_fact():
    allowed = sources("HV2-17")
    allowed[0].section_path = ["Supports Interdits"]
    with pytest.raises(ValueError, match="polarity"):
        validate_claims(raw("Supports horizontaux .", support_id(allowed[0])), allowed, RECORDS["HV2-17"]["case"]["query"])


def test_valid_prohibition_qualifier_remains_with_list():
    allowed = sources("HV2-09")
    result = validate_claims(raw("Support horizontal.", support_id(allowed[0])), allowed, RECORDS["HV2-09"]["case"]["query"])
    assert "Supports Interdits :" in result[0]["text"]
    assert result[0]["quote"] in allowed[0].text


def test_redundant_heading_from_other_document_is_not_rendered_as_fact():
    allowed = sources("HV2-09")
    data = json.loads(raw("Support horizontal.", support_id(allowed[0])))
    data["claims"].append(dict(text=allowed[1].text, support_chunk_ids=[support_id(allowed[1])]))
    result = validate_claims(json.dumps(data), allowed, RECORDS["HV2-09"]["case"]["query"])
    assert len(result) == 1 and result[0]["source_id"] == "SOURCE 1"


@pytest.mark.parametrize("selector", [
    "HYDROMUR R peut être utilisé sur une surface déjà peinte.",
    "HYDROMUR R peut être utilisé sur un support horizontal.",
    "Surface déja peinte.", "Supports horizontaux .",
])
def test_hydromur_prohibited_support_inversion_and_unlabelled_list_fail_closed(selector):
    allowed = sources("HV2-17")
    with pytest.raises(ValueError):
        validate_claims(raw(selector, support_id(allowed[0])), allowed, RECORDS["HV2-17"]["case"]["query"])


def test_unselected_hydromur_prohibition_heading_cannot_be_borrowed():
    allowed = sources("HV2-17")
    with pytest.raises(ValueError, match="explicitly allowed"):
        validate_claims(raw("Supports Interdits :", "9fa81579423f5b70"), allowed)


def test_no_fallback_to_different_selected_source():
    allowed = sources("HV2-16")
    with pytest.raises(ValueError, match="not an extract"):
        validate_claims(raw(allowed[1].text, support_id(allowed[0])), allowed)


def test_omitted_or_unretrieved_source_not_allowed_even_when_text_matches():
    allowed = sources("HV2-15")
    with pytest.raises(ValueError, match="explicitly allowed"):
        validate_claims(raw(allowed[0].text, "omitted-child"), allowed)


@pytest.mark.parametrize("ids", [[], ["SOURCE 1"], [None], "38c9503e6e3dc893",
                                     ["38c9503e6e3dc893", "4650unknown"]])
def test_invalid_or_extra_support_ids_fail_closed(ids):
    allowed = sources("HV2-15")
    data = json.loads(raw(allowed[0].text, support_id(allowed[0])))
    data["claims"][0]["support_chunk_ids"] = ids
    with pytest.raises(ValueError):
        validate_claims(json.dumps(data), allowed)


def test_one_invalid_claim_prevents_any_partial_answer():
    allowed = sources("HV2-15")
    data = json.loads(raw(allowed[0].text, support_id(allowed[0])))
    data["claims"].append(dict(text="Invented", support_chunk_ids=["unlisted"]))
    with pytest.raises(ValueError):
        validate_claims(json.dumps(data), allowed)


def test_parent_uses_actual_parent_id_and_heading_cannot_answer_alone():
    allowed = sources("HV2-15")
    parent = allowed[3]
    assert support_id(parent) == parent.parent_id != parent.chunk_id
    with pytest.raises(ValueError, match="Heading alone"):
        validate_claims(raw(parent.text, support_id(parent)), allowed)


def test_verified_parent_body_requires_its_explicit_parent_support_id():
    allowed = sources("HV2-15")
    parent = allowed[3]
    parent.block_type = "paragraph"
    parent.text = "Application uniquement sur des fonds secs."
    result = validate_claims(raw(parent.text, parent.parent_id), allowed)
    assert result[0]["support_chunk_ids"] == [parent.parent_id]
    with pytest.raises(ValueError, match="not an extract"):
        validate_claims(raw(parent.text, parent.chunk_id), allowed)


def test_ambiguous_support_identity_fails_closed():
    allowed = sources("HV2-15")
    with pytest.raises(ValueError, match="ambiguous"):
        validate_claims(raw(allowed[0].text, support_id(allowed[0])), allowed + [allowed[0]])


def test_ocr_and_whitespace_are_comparison_only_original_text_is_rendered():
    allowed = sources("HV2-15")
    selector = "Les supports doivent être préparés conformément aux spécifications du DTU 59.1."
    result = validate_claims(raw(selector, support_id(allowed[0])), allowed)
    assert "spéciﬁcaƟons" in result[0]["text"]
    assert result[0]["quote"] in allowed[0].text


def test_wrong_list_ordinal_rejected_but_optional_quote_not_required():
    allowed = sources("HV2-08")
    claim = RECORDS["HV2-08"]["model_output_for_review"]["claims"][0]
    with pytest.raises(ValueError):
        validate_claims(raw(claim["text"], support_id(allowed[0]), claim["quote"]), allowed)
    result = validate_claims(raw(claim["text"], support_id(allowed[0])), allowed)
    assert result[0]["text"].startswith("4. Livré avec 2 types")


def test_lexically_present_affirmative_selector_cannot_remove_negation():
    source = sources("HV2-16")[0]
    source.text = "Ne pas utiliser sur un support horizontal."
    result = validate_claims(raw("utiliser sur un support horizontal", support_id(source)), [source], "Peut-on utiliser sur un support horizontal ?")
    assert result[0]["text"].startswith("Ne pas")


def test_normalization_does_not_delete_negation_numbers_or_units():
    assert canonical("Ne pas utiliser 86 Nm") != canonical("Utiliser 86 V")


def test_exact_substrate_permission_inversion_rejected_even_with_valid_quote():
    source = sources("HV2-17")[0]
    source.text = "Supports Interdits :\n• Supports horizontaux."
    with pytest.raises(ValueError):
        validate_claims(raw("Peut être utilisé sur des supports horizontaux.", support_id(source), source.text), [source], RECORDS["HV2-17"]["case"]["query"])
    result = validate_claims(raw("Supports horizontaux.", support_id(source)), [source], RECORDS["HV2-17"]["case"]["query"])
    assert result[0]["text"] == source.text


def test_duplicate_claims_deterministically_removed():
    allowed = sources("HV2-15")
    data = json.loads(raw("DTU 59.1", support_id(allowed[0])))
    data["claims"] *= 2
    assert len(validate_claims(json.dumps(data), allowed)) == 1


def test_independent_validation_sources_are_disjoint_and_evidence_is_frozen():
    independent = json.loads((Path(__file__).parent / "fixtures/rag_v2_independent_validation.json").read_text(encoding="utf-8"))
    original = {s["file_name"] for r in BASELINE["records"] if r["case"]["category"] == "positive" for s in r["case"]["evidence"]}
    from scripts.evaluate_hierarchical_retrieval import LABELS
    original.update(e["file_name"] for q in LABELS for e in q["evidence"])
    positives = [q for q in independent["labels"] if q["expected"] == "answered"]
    assert len(positives) == 8 and len(independent["labels"]) == 16
    assert independent["freeze"]["collection_sha256"] == BASELINE["collection_sha256"]
    assert all(e["file_name"] not in original and e["chunk_id"] and e["text"] for q in positives for e in q["evidence"])
