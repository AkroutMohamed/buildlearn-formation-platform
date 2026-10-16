# RAG V2 canonical product identity

## Outcome and scope

Implemented a read-only product-ownership sidecar and an explicit `ProductIdentityResolver` dependency in the V2 student-chat service factory. Retrieval, evidence selection, generation prompts/settings, exact-extractive support validation and public schemas are unchanged. `RAG_V2_ENABLED` remains false.

Ownership improved safe answer coverage on a new frozen query set: **5/16 fully correct supported answers versus 1/16 with the previous selected-excerpt identity policy**. API answered status was 6/16 versus 2/16; both policies returned a maximum instead of the requested minimum for PI14. All 12 negative/ambiguous queries abstained. There were zero observed wrong-product accepted claims and zero unqualified conflicting answers. This demonstrates an ownership improvement, not release readiness: coverage, entity syntax and answer completeness still need work on a future independent set.

## Read-only corpus identity audit

All 221 checkpoint extraction records were read and their SHA256 hashes verified against the checkpoint manifest. All 2,637 live indexed child payloads/vectors were read from `buildlearn_products_hierarchical_v1`. Every record's child-ID inventory and filename/source-path provenance were matched to the index. The collection digest equals the previously frozen corpus digest.

There are **218 distinct document IDs and 221 source records**. Three IDs occur at multiple source paths; a document-ID-only dictionary would overwrite ownership provenance. The resolver therefore binds `(document_id, source_path)`, original filename and each child's exact-text SHA256. Full source paths stay internal.

The complete per-record inventory is in [product_identity_catalog.json](../../backend/ai_data/identity/product_identity_catalog.json), including detected apparent references, declarations, candidate name, aliases, compatibility references, duplicate/near-duplicate relationships, ambiguity flags, source metadata, extraction hash and every indexed child's text hash. Declarations are ownership metadata, never extra answer evidence.

| Audit measure | Count |
|---|---:|
| Source records | 221 |
| Indexed children | 2637 |
| Mapped source records | 199 |
| Quarantined/ambiguous source records | 22 |
| Canonical products | 192 |
| Records with multiple apparent code references | 35 |
| Filename/declaration or owner-heading disagreement records | 14 |
| Identity groups across different document IDs | 4 |
| Identity groups across multiple source records | 5 |

All 155 mapped code-based source records independently contain their owning reference as a standalone full-document heading. Other mapped sources use an explicit corroborated declaration or a complete corroborating title. These are deterministic rule outcomes, not a human certification of every document. Detected references are candidates, not necessarily products: EN/DTU/ISO/IEC/DIN/NF/PDS standards/document codes never become owning product codes; foreign material grades and certificate references may conservatively quarantine a source.

Duplicate identity groups include LIKA FULL (2 source records), LIKA FINA (4), PB05 (2), MURA COLLE PLATRE (2) and ISBAROC R (2). Similar text alone never merges identities. Near duplicates use a transparent normalized token-set Jaccard >= 0.90 for audit only; exact duplicates use raw-text SHA256. LIKA FULL, LIKA FULL ECO and LIKA FINA remain separate products.

Quarantined sources:

| File | Flags |
|---|---|
| ECO%20COLLE%20V4.pdf | identity_unresolved |
| ELBCPK1012%20Technical%20Data.pdf | incompatible_owner_headings |
| EMRM1101%20Technical%20Data.pdf | incompatible_owner_headings |
| ENAL02271%20Technical%20Data.pdf | incompatible_owner_headings |
| ETCT123523%20Technical%20Data.pdf | incompatible_product_descriptions |
| ETCT1653%20Technical%20Data.pdf | incompatible_owner_headings |
| EWPB25402%20Technical%20Data.pdf | incompatible_owner_headings |
| Gyproc_Duraline_Board_2024.pdf | incompatible_owner_headings |
| Gyproc_Fireline_Board_2024.pdf | incompatible_owner_headings |
| Gyproc_Fireline_MR_Board_2024.pdf | incompatible_owner_headings |
| Gyproc_Moisture_Resistant_Board_2024.pdf | incompatible_owner_headings |
| PDS-0305-Gyproc Easi-Fill Hydro JC.pdf | filename_declaration_disagreement, non_entity_declaration |
| Rustika assila_Compressed.pdf | identity_unresolved |
| duraline-brochure.pdf | non_entity_declaration |
| duraline-datasheet.pdf | identity_unresolved |
| fiche_technique_pap2.pdf | identity_unresolved |
| fiche_technique_pap2.pdf | identity_unresolved |
| fireline-brochure.pdf | identity_unresolved |
| gyproc-duraline-certificate.pdf | identity_unresolved, incompatible_owner_headings |
| gyproc-fireline-certificate.pdf | identity_unresolved, incompatible_owner_headings |
| gyproc-fireline-mr-certificate.pdf | identity_unresolved, incompatible_owner_headings |
| jir%20pro%20etanche1.pdf | filename_declaration_disagreement |

## Catalog and resolution contract

`product_id = "product-" + SHA256(normalized canonical identity)[:20]`. Each product records its canonical name, owning codes, observed normalized aliases, document IDs and original source-file records. Each inventory record explains its mapping and retains conflicting/unresolved evidence explicitly. A foreign standalone owner heading without an explicit compatibility relation, multiple declarations, incompatible product descriptions or a filename/declaration disagreement quarantines ownership. Compatible/accessory references remain references; they do not become aliases or owners.

Names normalize URL decoding, Unicode accents, punctuation, spacing and case. Complete known reference codes also accept a separator between letter prefix and numeric suffix. Exact canonical names/observed aliases take precedence over longer-product family prefixes; a family prefix shared by multiple products is ambiguous. Unknown references, unknown named variants and alias collisions fail closed.

`resolve(question)` returns `IdentityResolution(resolved_product_ids, unresolved_requested_entities, ambiguous_candidates)`. A safe result needs at least one resolved ID and no unresolved entities/collisions. Comparison claims must cover every resolved requested product. Query parsing is intentionally conservative and has limited grammar handling: PI05/12/13 were wrongly treated as unknown suffixes. Arbitrary natural-language entity recognition is not solved here.

On startup `ProductIdentityResolver.load()` checks the collection name, checkpoint SHA256 and all extraction manifest hashes. A mismatch fails initialization. The resolver copies the catalog and has no request-specific mutable state. Adapter initialization loads it once under the existing lock; concurrent resolutions are deterministic. Deploy a catalog with its matching corpus/checkpoint and restart the service after a sidecar/corpus change. Selected child hashes and provenance fail closed on mismatches; this layer does not silently reload or migrate Qdrant.

## Safety integration

The V2 factory injects the resolver into `HierarchicalRAGV2`; per-request observation copies retain that same dependency. Isolated dependency-injected services may explicitly use the earlier selected-context identity checks (`identity_resolver=None`), which also provides the evaluation control. The actual V2 endpoint factory always loads the catalog and never falls back when catalog loading fails.

For each selected source, ownership comes from its audited source record rather than an arbitrary child fragment. A factual claim's selected allowed support must belong to a requested canonical product. No alternate source substitution, sibling fetch, hidden fallback content or factual context expansion is introduced. Parent evidence still comes exclusively from the existing verified hierarchy pipeline. Original ChildChunk text is unchanged.

The previous support-ID/extractive validator is unchanged and remains pinned to its validated digest by tests. Existing context contradiction, permission-polarity and object checks remain beside it. Missing ownership, quarantined sources, incomplete comparison coverage and selected contradictory evidence abstain. The legacy flag-off path and API schemas are unchanged.

## Evaluation protocol and integrity

An initial consumed-set replay exposed implementation bugs (exact-name/family-prefix collision and reference scanning of ordinary words/numbers). Those were fixed using synthetic resolver regression tests before the independent freeze. No labels, retrieval parameters, prompts or generation settings were changed; no parameter search was performed. Both initial and final consumed outputs are preserved. No implementation changes followed the new independent freeze.

Consumed sets were regression evidence only. After the final regression replay, 28 new query strings were frozen from actual indexed evidence: 16 positive and 12 negative/ambiguous. They cover same-family names, aliases, numeric and multi-fact questions, comparisons, mixed sources, unsupported compatibility and unknown identities. These are new questions with shared-corpus/source overlap, **not a source-disjoint evaluation**. Every positive label includes actual indexed chunk/document IDs and exact source text. Labels were frozen before either canonical or selected-context-control generation.

Frozen label SHA256: `fdf56b15bacdcb89c18edfe9ac371c1be7b0d554935b7926a4bbe4293f2a19e0`.

Artifacts:

- [Frozen independent labels](../../backend/tests/ai/fixtures/rag_v2_product_identity_validation.json)
- [Final consumed regression outputs](rag_v2_product_identity_regression_outputs.json): all 114 requests, selected context, model outputs, citations, resolution results and integrity snapshots.
- [Initial regression outputs](rag_v2_product_identity_initial_regression_outputs.json): retained diagnostic history.
- [Independent and control outputs](rag_v2_product_identity_validation_outputs.json): all 56 requests and separate manual requested-fact review.

## Consumed regression results

| Set | Supported answered | Strict negative abstentions | Notes |
|---|---:|---:|---|
| rag_v2_release_acceptance | 14/22 | 18/18 | A18 and N15 still rejected; all 14 previously safe answers/citations unchanged |
| rag_v2_semantic_independent | 4/10 | 9/10 | 4/10 versus previous 2/10; SS16 returns an exact prohibition, a safe qualified refusal |
| rag_v2_semantic_followup | 3/4 | 4/4 | Same 3/4 supported and 4/4 negative decisions |
| rag_v2_independent_validation | 7/8 | 8/8 | Same 7/8 positives; conservative negatives |
| original_positive | 16/20 | 0/0 | Older 19/20 result predates the selected-context semantic guard; current 4 abstentions documented below |
| original_negative | 0/0 | 10/10 | N10 permits clarification/scoped evidence; this run abstains |

All 56 returned regression claims had valid allowed support IDs/exact citations and requested-product ownership. There were zero technical failures or observed unqualified conflict answers. Release A18 and N15 remain insufficient. SS16 is a strict status change from insufficient to answered, but the answer is solely "Ne pas appliquer sur supports geles ...": it denies blanket permission instead of affirming it. The consumed label remains unchanged; this is separately adjudicated as a qualified refusal, not counted as a strict abstention.

The older original positive set currently abstains on HV2-01, HV2-02, HV2-16 and HV2-17. Its old 19/20 score is not the immediate pre-catalog baseline; the earlier semantic safety layer had already introduced conservative abstentions. There is no newly lost supported answer in the 40-case release regression: all 14 prior safe answers retain exact citations. The newer catalog does not restore JIR PRO ETANCHE while its filename/declaration OCR disagreement is quarantined.

## New independent results

| Measure | Canonical ownership | Selected-excerpt control |
|---|---:|---:|
| API answered status on positives | 6/16 (37.5%) | 2/16 (12.5%) |
| Fully correct requested-fact answers | 5/16 (31.25%) | 1/16 (6.25%) |
| Positive abstentions | 10/16 | 14/16 |
| Answered but wrong requested fact | 1 (PI14) | 1 (PI14) |
| Negative/ambiguous abstentions | 12/12 | 12/12 |
| Returned claims | 6 | 2 |
| Wrong-product accepted claims | 0/6 | 0/2 |
| Exact citations / allowed support IDs | 6/6 | 2/2 |
| Unqualified conflicting answers | 0 | 0 |
| Technical failures | 0 | 0 |

Canonical identity safely resolves 13/16 positive queries (81.25%) and 15/28 total queries (53.57%; negatives intentionally include unresolved/ambiguous identities). Three positive false abstentions are entity syntax failures. The returned PI14 excerpt correctly states a maximum 20 mm for LIKA FULL ECO, but the question asks minimum first-pass thickness (label: minimum 7 mm). Count this as an answer-relevance failure, not a supported-answer success. No factual value was invented, but citation/identity validity alone is insufficient for answer completeness. No tuning/fix was made against this frozen case.

New independent per-query review:

| ID | Expected | API status | Diagnosis / review |
|---|---|---|---|
| PI01 | answered | answered | Correct water quantity, correct HYDROMUR B identity |
| PI02 | answered | answered | Correct water quantity, distinct HYDROMUR R identity |
| PI03 | answered | answered | Correct HYDROMUR PRO coverage |
| PI04 | answered | insufficient | Old validator rejects multiple support IDs for one claim |
| PI05 | answered | insufficient | False unresolved entity: ordinary word combien treated as suffix |
| PI06 | answered | insufficient | Old validator rejects multiple support IDs for one claim |
| PI07 | answered | insufficient | Qwen reports insufficient; ownership gate passed |
| PI08 | answered | insufficient | Selected evidence has no verified requested-product ownership |
| PI09 | answered | answered | Correct SUPERLITE identification |
| PI10 | answered | insufficient | Selected evidence lacks requested SUPROTEC ownership |
| PI11 | answered | insufficient | Selected evidence lacks requested SUPROTEC ownership |
| PI12 | answered | insufficient | False unresolved entity: ordinary word faut treated as suffix |
| PI13 | answered | insufficient | False unresolved entity: ordinary word permet treated as suffix |
| PI14 | answered | answered | Incorrect requested fact: maximum 20 mm instead of minimum first pass 7 mm |
| PI15 | answered | insufficient | Extractive validator retains no qualifying claim from model selector |
| PI16 | answered | answered | Correct FINACEM ROUGE 5 mm; exact OCR text preserved |
| PI17 | insufficient | insufficient | Ambiguous HYDROMUR family |
| PI18 | insufficient | insufficient | Unknown MURENDUIT variant |
| PI19 | insufficient | insufficient | Unsupported substitution; conservative unresolved query suffix |
| PI20 | insufficient | insufficient | Distinct ownership; conservative unresolved query suffix |
| PI21 | insufficient | insufficient | Unsupported medical permission; model insufficient |
| PI22 | insufficient | insufficient | Unsupported mixed-product permission; conservative unresolved suffix |
| PI23 | insufficient | insufficient | Quarantined contradictory/mixed ETCT document |
| PI24 | insufficient | insufficient | Quarantined mixed product-reference source |
| PI25 | insufficient | insufficient | Unknown PRIMER CONTACT variant / alias collision |
| PI26 | insufficient | insufficient | Comparison contains unknown reference |
| PI27 | insufficient | insufficient | No current price/warranty evidence; model insufficient |
| PI28 | insufficient | insufficient | Ambiguous LIKA family |

Thus the observed correct supported-answer gain is +25 percentage points (5 versus 1), while negatives remain conservative. The 10 false abstentions and PI14 relevance failure prevent a general quality/readiness claim. Conservative negative abstentions often occur before generation; they are not proof that every unsupported question or contradiction can be recognized. Conflict detection remains bounded to the existing patterns plus audited identity quarantine.

## Tests and protected components

**538 tests passed**, with 1,847 existing deprecation warnings, in the broad relevant backend suite. New identity tests cover exact/spaced codes, aliases, punctuation/URL filenames, distinct and prefix-related family names, duplicates, compatibility/accessory references, mixed-reference quarantine, unknown variants/partial families, filename disagreement, comparison coverage, nameless child evidence, wrong-product rejection, conflict preservation, exact text/provenance binding, stale checkpoint/extraction rejection, concurrent deterministic resolution and collection isolation. Existing semantic safety tests and default-off/legacy endpoint, schema, persistence and runtime lifecycle tests pass.

Reproduce with the backend venv:

```powershell
.\venv\Scripts\python.exe -B scripts/build_product_identity_catalog.py
.\venv\Scripts\python.exe -B -m pytest tests/ai/test_product_identity.py tests/ai/test_semantic_safety_v2.py tests/test_rag_v2_chat_integration.py tests/test_rag_v2_runtime.py -q -p no:cacheprovider
```

The builder writes only the sidecar. Evaluation scripts refuse to overwrite frozen labels or historical outputs; use a new independent fixture/artifact for future semantic changes. Frozen evaluator and spec digests are recorded in the independent fixture.

Both evaluations used read-only Qdrant clients allowing only get_collection/scroll/query_points on the hierarchical collection. No indexing, extraction, checkpoint, embedding, vector, ranking or model-setting writes occurred. File snapshots and both collections' complete ID/payload/vector digests were equal before and after. Legacy collection count remains 624; hierarchical remains 2,637. Protected support validator and Retrieval V2 hashes remain unchanged from their validated versions.

Files added/updated:

- `backend/app/ai/rag/product_identity.py` (new resolver and pure audit/catalog builder).
- `backend/app/ai/rag/semantic_safety_v2.py`, `hierarchical_rag_v2.py` and `backend/app/ai/api/rag_v2_endpoint.py` (explicit ownership dependency; existing checks retained).
- `backend/ai_data/identity/product_identity_catalog.json` and `validation_specs.json` (sidecar inventory and pre-execution evidence specifications).
- `backend/scripts/build_product_identity_catalog.py`, `evaluate_product_identity.py` (read-only audit/evaluation).
- `backend/tests/ai/test_product_identity.py`, `backend/tests/test_rag_v2_chat_integration.py` and the frozen independent fixture (focused tests; validator pin retained, obsolete whole-RAG hash pin replaced by protected-run integrity).
- This report and the three linked evaluation JSON artifacts.

**Keep the feature flag false.** Canonical ownership materially improves safe coverage, but grammar-driven false abstentions, unretrieved target evidence, model support formatting and answer completeness remain limitations requiring a future independent validation cycle.
