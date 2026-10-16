# RAG V2 answer validation and false-abstention audit

The same 20-positive / 10-negative regression now answers **19/20 positives**, reducing false abstentions from **8 to 1**, and preserves **10/10 negative/ambiguous abstentions**. All **29 returned claims** have allowed support IDs and exact original-evidence citations. No unsupported returned claims or prohibited-support acceptance were observed. The remaining HYDROMUR abstention is intentional: the context lacks the qualifier needed to answer safely.

A separately frozen validation set from eight previously unused source files answered **7/8 positives** and abstained on **8/8 negatives**. Its remaining positive failure exposes the existing RAG reference heuristic, rather than missing retrieval evidence. Neither set justifies a universal semantic-correctness claim. `/student/chat` remains unconnected.

## Scope and protected state

This change is confined to isolated RAG V2 generation, answer validation, tests, evaluation tooling and artifacts. Retrieval V1/V2, extraction, chunking, embeddings, indexing, legacy RAG/LLM behavior, Qdrant payloads/vectors, global configuration, Qwen installation and `/student/chat` were not edited. No new dependency or model was installed. The only collection read was `buildlearn_products_hierarchical_v1`; no collection write API was used.

The existing architecture and saved model outputs were inspected before changing validation. The previous complete reviewed 30-case output is preserved in `backend/tests/ai/fixtures/rag_v2_baseline_outputs.json`. Current complete outputs, raw attempted structured claims, sources, warnings, timings and assistant review annotations are in `rag_v2_answer_outputs.json`; separate validation outputs are in `rag_v2_independent_outputs.json`.

The collection payload/vector SHA-256 remained:

`61e6cd658f7edde04d3bb7312b2cc01a1535ace38f23baea277ecab679748eb4`

The unchanged validated Retrieval V2 SHA-256 is:

`bec257494381f2d42df473c1372013fb56183b4450860565c1d9013f9fac0c48`

Both live evaluations passed before/after collection and protected-file checks against the earlier retrieval freeze. The retrieved child-ID sequence was also compared with the saved baseline and is identical for **all 30 original queries**. No retrieval count, ranking, similarity threshold, embedding setting, indexing data or checkpoint was tuned.

## Individual audit of the eight baseline false abstentions

All eight baseline raw responses attempted answers; none was a model `insufficient` response or a JSON parsing failure. Seven were primarily exact-quote extraction mismatches. For HYDROMUR, the corpus contains evidence but the selected context lacks the prohibition boundary. Calling that case merely a quote problem would conceal the safety issue.

| ID / product | Relevant selected child IDs | Primary root cause | Additional diagnosis | Final replay |
|---|---|---|---|---|
| HV2-01 / FINACEM BLEU | `00c8d2bdbddae924`, `99cc92ba87a42ea0` | Quote extraction mismatch | Whitespace/ligature changes. Composition was supplied in SOURCE 3, but the baseline raw answer selected a description instead and omitted ingredients: evidence present but not selected by generation / incomplete answer. | Answered: white cement, mineral fillers, specific additives and 10-month storage |
| HV2-02 / PRO 2000 | `02f208fac8dbb8fd` | Quote extraction mismatch | Apostrophes, OCR and whitespace changed; raw prose contained Portuguese `obten??o`. Water/weight evidence was present. | Answered: approximately 6.25 litres for 25 kg |
| HV2-03 / CEM PRO FLEX 100 W | `060897ea2a172b7a`, `1bca5b1704c94391` | Quote extraction mismatch | Spacing, ligatures and apostrophes changed. Mixing/layer instructions were supplied. All three supplied children belong to this same file; this was not cross-document substitution. | Answered: B liquid then A powder, low-speed mixing, two layers and application details |
| HV2-07 / RUSTIKA TYROLIEN | `141e0f1f0585631f` | Quote extraction mismatch | Model normalized `sp?ci?ca?ons` and final punctuation. DTU 26.1 was present. | Answered: DTU 26.1 |
| HV2-08 / EMAT5541 | `16c3b9f4450fb430` | Quote extraction mismatch | Quote ordinal was changed from `4.` to `2.`. This is a model copying/formatting error, not a parser failure; the actual count of two mandrin types was present. | Answered: original line `4. Livr? avec 2 types ...` |
| HV2-15 / MURENDUIT V | `38c9503e6e3dc893` | Quote extraction mismatch | OCR specifications wording changed. Substrate state and DTU 59.1 were both present. | Answered: hard, cohesive, clean, sound, dry, dust-free substrates; DTU 59.1 |
| HV2-16 / FINACEM ROUGE | `3bc67ce5710b3476` | Quote extraction mismatch | Raw output also added unrequested MURENDUIT from selected SOURCE 2: product-scope contamination. That source was actually listed, not an unlisted fallback. | Answered from FINACEM only: interior filling/rendering and manual application |
| HV2-17 / HYDROMUR R | `3d78bc891b779755` | Evidence present but not selected | Missing prohibition heading plus semantic entailment failure: raw output inverted prohibited supports into permissions. Exact-quote rejection blocked it only incidentally. | Abstained explicitly because compatibility polarity is unavailable |

The seven copying failures were support-validator rejections at the quote check. No baseline false abstention was caused by absent retrieved product text, prompt-induced abstention, or a service JSON parser error. This does not mean the selected evidence was complete in HV2-17.

### Every rejected prohibited-substrate assertion

Across all saved baseline rejected outputs, **HV2-17 is the case with affirmative assertions about prohibited substrates**, containing two unsafe claims:

- ?HYDROMUR R peut ?tre utilis? sur une surface d?j? peinte.?
- ?HYDROMUR R peut ?tre utilis? sur un support horizontal.?

Both cite supplied SOURCE 1. The actual list includes `Surface d?ja peinte.` and `Supports horizontaux .`, but its selected body and `DOMAINE D?EMPLOI` parent do not say whether these are allowed or prohibited. The corpus prohibition heading is child `9fa81579423f5b70`, parent `c9da5f564f9a8786`; it was **not supplied**. Selected HYDROMUR B/PRO children repeat the same unqualified list and cannot establish permission for R. The implementation neither fetches that missing heading nor borrows a qualifier from another product.

The baseline blocked these claims because the model changed accent/spacing in the quotes. A matching quote would not have established entailment. Regressions now reject the affirmative paraphrases even with real quotes, reject bare-list answers to compatibility questions, reject the unseen heading ID, and reject attempts to borrow another selected document's heading.

### Unlisted evidence IDs versus prohibited substrates

These are separate failure classes. An audit of every baseline raw structured claim found **zero unlisted SOURCE aliases**. The old implementation already required the cited alias to exist; there is no evidence of an implemented alternate-source fallback in that baseline. Its actual weakness was accepting free-form interpretations when superficial quote checks happened to pass.

The new contract makes the requested boundary explicit in actual support IDs. Tests cover forged IDs, SOURCE aliases in place of chunk IDs, omitted/budget-dropped IDs, extra supports, ambiguous IDs and text that exists only in a different supplied source. No alternate-source search is performed when validation fails.

## Generation and validation architecture

Flow:

`unchanged Retrieval V2 -> existing whole-child/verified-parent context builder -> explicit allowed support IDs -> Qwen excerpt selection -> validate every proposed claim -> render original cited evidence`

The new validator is `backend/app/ai/rag/answer_validation_v2.py`; isolated integration remains in `hierarchical_rag_v2.py`. Existing whole-child ranked-prefix budgeting, verified-parent checks and body deduplication remain. Headers additionally expose `support_chunk_id`. A child uses its actual `chunk_id`; a verified parent uses its actual `parent_id`, rather than the anchoring child's ID. Only sources admitted to the final model context form the whitelist. Metadata exposes `allowed_support_chunk_ids`.

The structured generation contract is:

```json
{
  "status": "answered",
  "claims": [
    {
      "text": "original supporting evidence lines",
      "support_chunk_ids": ["explicitly supplied support ID"]
    }
  ]
}
```

`quote` is optional. An atomic extractive claim must have exactly one support ID; multi-source answers use separate claims. `insufficient` requires an empty claim list. Unknown/extra keys, malformed claims, invented support IDs, ambiguity or failed extraction fail closed before final rendering. One invalid factual claim prevents a partial answer; valid redundant heading-only selections are excluded as nonfacts. Heading-only output cannot answer a question.

This contract deliberately uses **extractive answers**, rather than attempting to prove arbitrary Qwen paraphrases with token overlap. Claim text is an evidence selector. The validator requires it to match the explicitly selected source and recovers complete original contiguous lines. Final claim text and quote are those original lines, not unchecked model prose. Partial-line selection expands to complete lines so the model cannot remove an on-line negation, numeric qualifier or condition. For compatibility answers, the selected source body must contain an explicit allowed/prohibited qualifier, and the original qualified passage remains attached to its list. A generic domain heading is insufficient. A qualifier only in another source or an unrendered section label is not silently borrowed.

Comparison normalization is bounded: whitespace, Unicode apostrophes, accent folding, Unicode ligatures, the corpus's `?`/`ti` OCR glyph, leading bullet layout and optional final period. It never deletes negation, numbers, units or list ordinals, never performs fuzzy matching, and never modifies stored/source text. Optional quotes must resolve within the same support and contain the selected text. Rendered quotes remain exact substrings of the original body.

Quantitative answers also refuse an unspecified product when the context contains multiple product references and the question identifies none. This blocks N06/IN04 even if Qwen chooses a structurally valid single source. Existing unknown/malformed-reference checks, usable-evidence gate and model insufficiency remain.

Defaults remain top K=3, context budget 6,000 characters, question budget 1,000 characters and 600 model-output tokens. Evaluation uses existing `qwen2.5-coder:7b`, temperature 0, seed 0, model context 8,192, local Ollama and normalized nomic query embeddings. No model/global-setting change is involved.

## Original 30-case regression results

These are consumed tests used for failure diagnosis and targeted regressions, **not a new held-out benchmark**. RAG-only contract/safety fixes address observed failure classes. Retrieval and thresholds remain fixed.

| Measure | Baseline | Final |
|---|---:|---:|
| Positive answers | 12/20 (60%) | **19/20 (95%)** |
| False abstentions | 8/20 | **1/20** |
| Negative/ambiguous abstentions | 10/10 | **10/10** |
| Returned claims with valid exact citations | 23/23 | **29/29** |
| Answered positives citing only labeled source identities | 11/12 | **19/19** |
| Unsupported returned claims observed | 0 | **0** |
| Prohibited/unlisted support-ID acceptance observed | 0 | **0** |
| HYDROMUR permission inversion accepted | No, incidental quote failure | **No, explicit context/interpretation checks** |

Seven original false abstentions now answer. All remaining originally answered positives still answer. HV2-01 now includes ingredients instead of substituting a product description; HV2-16 excludes the unrequested MURENDUIT claim; HV2-09 retains the prohibition qualifier with the R1 list and drops the redundant alternate-file heading citation.

HV2-17 remains a false abstention against the corpus-level positive label, but is the correct conservative behavior for the available context. Answering its compatibility question would require information excluded by the current selected pipeline. No retrieval/context fallback was added.

N01/04/05/08/09/10 report model insufficiency. N02/03/07 are refused by existing reference checks. N06 is rejected explicitly for ambiguous quantitative product identity; it is no longer protected only by an incidental copying/schema error. All original 30 final responses are French.

## Separate independent validation

Before additional markup/qualifier/ambiguity refinements, `backend/tests/ai/fixtures/rag_v2_independent_validation.json` was frozen with the pre-refinement RAG module hashes and actual corpus digest. It contains eight positive evidence labels from source files disjoint from both the earlier 34-query retrieval set and the 20-query retrieval held-out set, plus eight negative questions. Labels include actual source identity, chunk ID and indexed text. No model outputs or parameter search were used to assign labels. Warranty absence was checked in the actual source document. This set was evaluated once after refinements; **no changes were made to rescue its results**.

| Case | Question scope | Result |
|---|---|---|
| IV01 | ELAB2078 voltage/no-load speed | Answered |
| IV02 | ECIWL20455 tightening/breakaway torque | Answered |
| IV03 | ELBCPK1012 charge LED levels | Answered |
| IV04 | EFC1352 protective gas requirement | Answered, preserved negative wording |
| IV05 | ECIDL209686 torque/chuck diameter | Answered |
| IV06 | ELBCPK2212 voltage/battery count | Answered |
| IV07 | FULL ECO1 prohibited supports | Answered, explicit prohibition retained |
| IV08 | LIKA FINA1 file prohibited supports | Refused: existing RAG heuristic treats filename suffix `FINA1` as an unknown reference |
| IN01?IN08 | Price, warranty, medical use, unspecified tool, unknown reference, partially unknown comparison, weather, unavailable fire certification | All abstained |

Results: **7/8 positive answers, 8/8 negative abstentions, 8/8 exact returned citations**, no unsupported returned claims or unlisted-support acceptance observed. IV08 is reported rather than changing labels or tuning the heuristic after seeing this independent outcome. IN06 uses an English refusal for a French query because the existing refusal-language heuristic does not recognize its phrasing; it still abstains correctly. Further answer-quality tuning requires another independent validation set. These eight source files provide a small validation sample, not broad product/language coverage.

## Tests and reproduction

The broad relevant suite passed **435 tests, zero failures**, in 7.81 seconds, with 1,824 existing datetime/fixture deprecation warnings. Two additional test-only regressions were then added; the final focused RAG selection passed **63 tests, zero failures**, in 1.13 seconds. Counts overlap and must not be added as separate runs. This includes 37 new validator regression cases alongside the 26 existing RAG V2 cases, whose mocked contract was updated.

Coverage includes every original false-abstention class, real saved source text, composition/storage selection, OCR/spacing/bullet matching, changed ordinals, unit/number fabrication, prohibited-substrate inversion, exact quotes attached to wrong interpretations, absent qualifiers, alternate-file qualifiers, unknown/omitted/extra support IDs, no alternate-source fallback, ambiguous IDs, valid parent IDs, inability to justify a parent with its anchoring child ID, one-invalid-claim full refusal, deterministic duplicate removal, ambiguity, exact original-text/provenance preservation, context budgets and collection/legacy isolation. A fixture test verifies independent source disjointness.

From `backend`, preserving reviewed outputs first:

```powershell
.\venv\Scripts\python.exe -B scripts/evaluate_rag_v2.py --restart --batch-size 30
.\venv\Scripts\python.exe -B scripts/evaluate_rag_v2.py --restart --batch-size 16 --validation-set tests/ai/fixtures/rag_v2_independent_validation.json --output ../docs/ai/rag_v2_independent_outputs.json
.\venv\Scripts\python.exe -B -m pytest tests/ai/test_hierarchical_rag_v2.py tests/ai/test_rag_v2_answer_validation.py -q -p no:cacheprovider
```

The evaluator saves each case, supports batching/resume, verifies implementation/corpus compatibility and revalidates returned claims. `--restart` replaces the chosen output, so the reviewed baseline is retained separately. The JSON files record model status/claims only, not separate reasoning fields. Assistant qualitative annotations are not independent human certification.

## Limitations and disposition

The measured success criteria are met on the requested regression: no prohibited-support acceptance, seven fewer false abstentions, all ten negatives abstained, exact citations and no unsupported returned claims observed. This is an isolated RAG-only change; `/student/chat` remains untouched.

Extractive validation constrains new assertions but does not establish source-document truth, resolve contradictory source instructions or prove that every answer completely resolves an arbitrary question. Missing qualifiers outside selected evidence remain unavailable. Preserving exact OCR can produce awkward wording, repeated neighboring headings and extra adjacent facts. Answers follow the source language; translated/paraphrased answers are intentionally outside this conservative contract. The independent FINA1 false abstention and refusal-language issue remain documented. These limits prevent treating the finite evaluation as a universal semantic guarantee or authorization to connect the endpoint.
