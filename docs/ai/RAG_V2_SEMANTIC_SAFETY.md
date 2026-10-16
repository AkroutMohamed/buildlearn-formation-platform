# RAG V2 semantic safety

## Outcome and scope

Both frozen release blockers now abstain: A18 cannot justify LIKA FULL with LIKA FINA evidence; N15 cannot answer definitively from a document with conflicting product-reference headings. No hidden sources, alternative support substitution or broader retrieval were introduced. The unchanged exact-extractive/support-ID validator remains the first claim validator; the new module runs beside it before generation and after claim validation.

**Safety improved with an explicit coverage cost.** The consumed release regression retains 14/15 previously correct supported answers and introduces one conservative loss, A20. The independent set answers only 2/10 supported questions; all 10 negatives abstain. Zero wrong-product accepted claims and zero unqualified conflicting answers were observed in either run. These results do not justify broad student-facing enablement. `RAG_V2_ENABLED=false` remains unchanged.

## Identity and conflict contract

Only final selected ChildChunks and already verified parent sources participate. Each source is bound to its exact document ID and source path. Product codes are matched as complete normalized tokens, not filename substrings; standard/norm codes are excluded. Owning codes from filename metadata are cross-checked against standalone product-reference headings and explicit selected product declarations. A different standalone owning reference within the same document creates a mixed-identity rejection. A body reference such as compatible-with another tool does not automatically make that tool the document owner.

Named products require an explicit selected declaration such as PRODUCT NAME est/is. Filename aliases alone do not resolve a family name, missing variant or revision. Alias filenames can refer to the same real declared identity; similar filenames and near-duplicate family names cannot substitute for a different declaration. The longest fully requested declared name is used, avoiding a broad family prefix standing in for a specific variant. If identification is unavailable or ambiguous, the result is insufficient.

Every validated claim must belong to a document whose resolved identity includes the asked target. Comparisons require coverage of all resolved requested entities. Claim text and support IDs are never replaced with another selected source, even if its wording is identical. Incorrect selected claims cause abstention rather than fallback. Unrelated mixed documents do not block a separately resolved target; target-document conflicts do.

Conflict checks cover mixed standalone reference headings, incompatible explicit welder/saw-blade descriptions, opposing explicit permissions for the same object, and unequal values for the same short numeric field with the same unit. Different products in a comparison are evaluated separately, avoiding treating legitimate product differences as contradictions. These are bounded transparent checks, not unrestricted natural-language entailment or automatic unit conversion.

Yes/no permission answers need explicit permission/prohibition/limitation language in the accepted extract and a relevant object when the question names an on/with/sur/avec object. A dimensions-only or unrelated exact excerpt cannot establish permission. An exact same-product prohibition such as Ne pas appliquer sur le metal is a valid qualified refusal. Mixed/conflicting contexts return the existing insufficient response; no synthetic uncited caveat is generated.

## Frozen evaluation protocol

The consumed 40-case release labels and original release outputs were preserved. They were rerun only as regression evidence, with no ranking, prompt, generation or threshold tuning. The 20-case independent set was frozen before live execution at 2026-09-26T21:17:16.802192+00:00. Fixture SHA-256: `903b1d5c755f4f2fe0b4359718830425546a652d43f431b77c08d214b7a5d2a9`. Query strings were checked against prior labeled fixtures/reports; the set covers same-family named products, filenames/reference aliases, mixed descriptions, allowed/prohibited support questions, comparisons, mixed documents and unknown/ambiguous entities. Some corpus sources are reused with new questions; this is a query-independent set, not a claim of source-disjointness.

The first 20-case set was not used for tuning. A separate specification counterexample then showed that a known code could mask an additional unknown uppercase named target in a comparison. The resolver now rejects such unresolved targets (excluding standard/norm names). The first 20 labels remain unchanged and are now regression evidence; eight fresh follow-up questions were frozen before final execution. No implementation changed after those final outputs. All fixture and implementation/data hashes stayed fixed within each run. Observers delegate the exact existing retrieval/generation calls, then record selected sources and validate returned source identity/citations independently. The read-only Qdrant wrapper permits only metadata/scroll/search on the hierarchical collection.

## Consumed release regression

| Metric | Before | After |
|---|---:|---:|
| Correct supported answers | 15/22 | 14/22 |
| Supported-case answered responses | 16/22 | 14/22 |
| Supported-case abstentions | 6/22 | 8/22 |
| Negative/conflict abstentions | 17/18 | 18/18 |
| Wrong requested-product accepted claims | 1 | 0 |
| Unqualified contradictory-source answers | 1 | 0 |

A18 now fails closed because LIKA FULL has no explicit owning named declaration in the final selected restriction fragments; LIKA FINA cannot be substituted. It does not fetch the unseen FULL description or silently choose another support. N15 rejects ETCT1653/ELCS1652 mixed owner headings in the same selected document before generation. Its old unqualified blade excerpt never reaches rendering.

All 14 retained answers have exactly the same accepted claim dictionaries, support IDs and public citations as the original release outputs. There are 15 accepted regression claims (A10 contributes two); all quotes and allowed IDs pass independent checks. The six previously observed false abstentions remain. A18 is an intentional safety abstention replacing the incorrect answer. A20 is the only loss of a previously correct answer: its selected JIR PRO ETANCHE prohibition excerpt lacks a safely resolved explicit named declaration, and filename guessing is prohibited. This conservative abstention is documented rather than repaired with unseen evidence.

## New independent validation

| Metric | Result |
|---|---:|
| Supported questions answered correctly | 2/10 |
| Supported questions abstained | 8/10 |
| Negative/ambiguous/conflict questions abstained | 10/10 |
| Wrong-product accepted claims | 0 |
| Unqualified conflicting answers | 0 |
| Accepted quotes/support IDs valid | 2/2 |
| Technical failures | 0/20 |

| ID | Category | Expected | Returned | Context safety check |
|---|---|---|---|---|
| SS01 | numeric multi-fact | answered | answered | passed |
| SS02 | multi-fact | answered | insufficient | passed |
| SS03 | English | answered | answered | passed |
| SS04 | numeric | answered | insufficient | product_identity_unresolved |
| SS05 | mixed references | answered | insufficient | mixed_product_identity |
| SS06 | mixed description conservative | answered | insufficient | mixed_product_identity |
| SS07 | same-family named product | answered | insufficient | product_identity_unresolved |
| SS08 | prohibited supports | answered | insufficient | product_identity_unresolved |
| SS09 | allowed supports | answered | insufficient | product_identity_unresolved |
| SS10 | two products | answered | insufficient | product_identity_unresolved |
| SS11 | ambiguous family | insufficient | insufficient | product_identity_unresolved |
| SS12 | unknown named entity | insufficient | insufficient | product_identity_unresolved |
| SS13 | near-duplicate names | insufficient | insufficient | product_identity_unresolved |
| SS14 | conflicting descriptions | insufficient | insufficient | mixed_product_identity |
| SS15 | mixed identity | insufficient | insufficient | mixed_product_identity |
| SS16 | unsupported blanket permission | insufficient | insufficient | product_identity_unresolved |
| SS17 | mixed documents unsupported | insufficient | insufficient | passed |
| SS18 | unqualified compatibility | insufficient | insufficient | passed |
| SS19 | unknown same-family variant | insufficient | insufficient | product_identity_unresolved |
| SS20 | filename aliases ambiguous | insufficient | insufficient | product_identity_unresolved |

False abstentions are not hidden by safety-only metrics: SS02 passes the identity layer but Qwen reorders a weight/empattement excerpt, and the existing extractive validator rejects it. SS04 has a pre-existing short-reference recognition problem for ETLPLA25. SS05 and SS06 conservatively reject mixed owning references in EWPB25402 and ETCT1653 documents. SS07-SS09 cannot establish the named entity from selected declarations. SS10 lacks all requested comparison identities in the final context. These eight are failures against answerable corpus labels; without a pre-layer live comparison for this independent set, none is falsely attributed entirely to the new layer.

No tuning was performed to improve these measured numbers. This set is now consumed. Improving named-product coverage, context identity metadata or comparison coverage requires separately scoped work and another independent set; broadening retrieval was outside this task.

## Final independent follow-up validation

The final code also rejects a recognized code paired with an unresolved uppercase named entity, so a partial comparison cannot silently become an answer about only the recognized product. This came from a focused specification test, not a change to improve a consumed label. Eight new questions were frozen before final execution: four supported questions and four unknown/mixed-identity negatives. SHA-256: `fba872f7d31f92c53a08bfab4f1a3c23abee171ba699aff00add0e0643e2effd`.

Final results: **3/4 supported answered, 4/4 negatives abstained**, zero wrong-product accepted claims, zero unqualified contradictory answers and zero technical failures. SF04 is the sole supported abstention; its raw output and controlled refusal reason are preserved in the final artifact. This smaller follow-up checks the new resolver edge case and does not erase the poor named-product coverage measured by the original 20-case set.

| ID | Expected | Final result |
|---|---|---|
| SF01 | answered | answered |
| SF02 | answered | answered |
| SF03 | answered | answered |
| SF04 | answered | insufficient |
| SF05 | insufficient | insufficient |
| SF06 | insufficient | insufficient |
| SF07 | insufficient | insufficient |
| SF08 | insufficient | insufficient |

The final implementation also replays all 40 consumed release cases and all 20 earlier independent cases. Every status and every retained accepted claim remains exactly the same as the first semantic-layer run. A18/N15 remain insufficient; A20 remains the one conservative loss of a previously correct supported answer. Both collections, all protected sources, consumed labels and the disabled flag match before/after.

## Tests and integrity

Final broad relevant suite: **518 passed**, 1,847 existing deprecation warnings, 10.60 s. Twenty focused semantic cases cover both exact old blocker outputs; same-product acceptance; wrong-product rejection without substitution; near-duplicate names; explicit real identity versus filename aliases; missing/unknown identities; mixed relevant and unrelated sources; numeric/descriptive and permission conflicts; unqualified/irrelevant yes/no excerpts; valid exact qualified refusal; and complete/incomplete comparisons. Existing RAG, extractive validator, endpoint/auth/flag/persistence/concurrency, retrieval, embeddings/vectorstore and hierarchical indexing/chunking tests also pass.

The original answer_validation_v2.py is byte-for-byte unchanged. Reconstructing the prior hierarchical_rag_v2.py by removing only the new import, context/claim checks and safety-exception handler matches its pre-change SHA-256, proving prompt, model/provider/configuration and generation settings were preserved. The endpoint remains unchanged; its existing generic abstention reason is retained, while the internal RAG warning uses a controlled semantic safety reason.

All 277 previously guarded files other than the authorized RAG integration module match their release hashes. This includes extraction, chunking, embeddings, indexing/checkpoint artifacts, both retrievers, endpoint/runtime code, API configuration and consumed labels. Collection ID/payload/vector digests match before/after:

| Collection | Points | SHA-256 |
|---|---:|---|
| `buildlearn_products` | 624 | `266b67d281d741c2d8b98b027b7bffffa9662a9e6942a2a8aa7606066c36e754` |
| `buildlearn_products_hierarchical_v1` | 2637 | `f0634b2003aa9d7d24b88233149943d3670a2be8bb06e2b690c8e3cc211b533f` |

No Qdrant/index/checkpoint write was invoked. No model, generation temperature/token limit, retrieval ranking/candidate count/top-K/threshold, prompt, schema or feature-flag default changed. No answer or retrieval-result cache was added.

## Files changed and reproduction

Modified: `backend/app/ai/rag/hierarchical_rag_v2.py` (layer integration only); `backend/tests/test_rag_v2_chat_integration.py` (authorized current-RAG hash guard tied to the new freeze, while retaining the unchanged validator guard).

Added: `backend/app/ai/rag/semantic_safety_v2.py`, `backend/tests/ai/test_semantic_safety_v2.py`, `backend/scripts/evaluate_semantic_safety_v2.py`, `backend/tests/ai/fixtures/rag_v2_semantic_independent.json`, `backend/tests/ai/fixtures/rag_v2_semantic_followup.json`, `docs/ai/rag_v2_semantic_outputs.json`, `docs/ai/rag_v2_semantic_final_outputs.json`, and this report. Existing consumed labels/reports/results were not overwritten.

From backend with the existing local services:

```powershell
.\venv\Scripts\python.exe -B scripts/evaluate_semantic_safety_v2.py --freeze
.\venv\Scripts\python.exe -B scripts/evaluate_semantic_safety_v2.py
.\venv\Scripts\python.exe -B scripts/evaluate_semantic_safety_v2.py --followup
.\venv\Scripts\python.exe -B -m pytest tests/ai/test_semantic_safety_v2.py tests/ai/test_hierarchical_rag_v2.py tests/ai/test_rag_v2_answer_validation.py tests/test_rag_v2_chat_integration.py -q -p no:cacheprovider
```

Freeze/execution commands intentionally refuse existing artifacts. Preserve these consumed results rather than overwriting them. The final broad selection matches the previous relevant release suite with test_semantic_safety_v2.py added.

## Remaining limitation

The two observed semantic blockers are fixed through conservative rejection. Named declarations currently require explicit uppercase entity declarations in selected text; missing declarations, spelling/OCR variations, ambiguous headings and unsupported aliases can cause abstention. Conflict and object-relevance checks are bounded lexical checks and do not prove every conceivable entailment, polarity, qualifier or contradiction. The independent 20% supported answer rate is a material usability limitation. Keep V2 disabled; the task does not establish unrestricted staging/student readiness or authorize activation.
