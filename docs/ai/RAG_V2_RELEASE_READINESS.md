# RAG V2 release-readiness validation

## Release decision

**NO-GO for unrestricted staging enablement. Keep `RAG_V2_ENABLED=false`.** Runtime, concurrency, rollback and persistence checks passed, but fresh acceptance exposed a wrong-product cited answer (A18) and an unqualified answer from contradictory evidence (N15). Valid support IDs and exact quotes did not prevent these failures. The integration is operationally suitable for isolated internal staging evaluation; it is not yet ready to be enabled for student use. No automatic enablement was performed.

No production code changed. Ranking, prompts, model, validators, embeddings, indexing, schemas, feature-flag defaults and data are unchanged. No release/integration defect requiring a production fix was identified. The quality failures require separately authorized semantic work and a new independent validation set; this acceptance set is now consumed and was not used to tune the system.

## Frozen acceptance protocol

Frozen before any generation at `2026-09-26T20:47:38.073537+00:00`: `backend/tests/ai/fixtures/rag_v2_release_acceptance.json`, SHA-256 `f3ec3ede6c963c75eeeca06076ffda79b3338d31fa172b53ac56d5d6f898abef`. Forty unique questions: 22 answerable cases, 15 strict negative/ambiguous cases, and 3 conflict/incomplete/overbroad cases whose pre-execution labels permit abstention or an explicit qualified refusal. All question strings and supported evidence filenames were checked against previous labeled fixtures/reports and earlier evaluation/shadow questions. Expected supported sources are disjoint from 60 previously labeled filenames; 90 earlier question strings were excluded.

Labels were derived from the live 2,637-child corpus, with original document/file/path/chunk IDs and evidence text. No extraction or indexing was run. The freezer fails rather than overwrites labels. The executor checks label/protected hashes, refuses an enabled flag, and writes outputs without overwriting a previous run. The only pre-freeze correction changed an absent-reference assertion from substring matching to the existing exact identifier catalog; no generated output existed then.

Coverage includes supported products and numeric units, dimensions, French/English, misspelled ordinary words, typo and partial identifiers, multi-fact questions, known/unknown comparisons, permission/prohibition, vague standalone follow-ups, price/warranty, unsupported medical/electrical uses and mixed/incomplete evidence. English questions retain French original evidence excerpts, matching the unchanged extractive contract. No conversational identity carryover was added.

Live requests use the actual endpoint adapter/service factory and unchanged Ollama/Qdrant providers; per-request observers only record existing outputs and selected context. A read-only Qdrant proxy rejects operations other than metadata/scroll/search and rejects other collections. It never caches queries, answers or retrieval results. Acceptance is sequential on one new adapter; concurrency and restart are additional repetitions of four/one frozen cases for stability, not additional independently scored labels.

## Acceptance results

| Metric | Result |
|---|---:|
| Supported questions receiving an answered response | 16/22 (72.7%) |
| Supported answers correct for requested product and facts | 15/22 (68.2%) |
| False abstentions | 6/22 (27.3%) |
| Wrong-product supported-case answers | 1 |
| Negative/ambiguous/conflict questions abstaining | 17/18 (94.4%) |
| Strict unsupported/ambiguous abstentions | 15/15 (100%) |
| Qualified-refusal/conflict cases passing review | 2/3 |
| Returned claims | 18 |
| Exact quote/citation validity | 18/18 |
| Explicitly allowed support-ID validity | 18/18 |
| Claims unsupported for the requested target product | 1/18 (A18) |
| Fabricated/non-extractive returned passages | 0 |
| Technical failures, acceptance | 0/40 |
| Reviewed overall acceptance passes | 32/40 (80%) |

Exact citation checks independently compare each returned quote with the actual selected source text and source alias; allowed-ID checks use only selected child/verified-parent IDs. Manual source/identity/completeness review separately assesses whether that passage answers the requested product and every required fact. A valid exact quotation is not automatically a correct answer.

## Blocking findings

**A18: wrong product, despite valid citation.** The query asks LIKA FULL for prohibited supports, including horizontal supports. The final context includes the expected FULL source `71e680d35400bbf3` from `FULL%201.pdf`, but Qwen chooses `8ed2bc02e7f85eb2` from `LIKA%20FINA1.pdf`. The rendered restriction list is an exact excerpt and its ID is allowed. Its similar text is not proof for LIKA FULL. This is counted as one unsupported target-product claim, not hidden inside the quote-validity metric. The source identity was independently confirmed: `e9d46a0389c69a9e` explicitly describes LIKA FINA as a thin manually applied decorative render, while FULL's description specifies mechanical application. This is not merely an alternate filename for FULL. No parser/ranker/prompt/validator fix was attempted.

**N15: contradictory-source qualification.** The ETCT1653 sheet contains welding applications in `11eac5e8bb98fd1d`, blade dimensions in `3bf24376b9bbf086`, and a wood-cutting section under ELCS1652 in `415ecffb919c713c`. All are supplied. The query asks whether it is definitely a welder rather than a saw blade. Returned answer:

> Bague de réduction : 16 mm Épaisseur : 1,0 mm Convient pour la scie circulaire [SOURCE 1]

The excerpt itself is source-supported and does not affirm welding permission, but the response is marked answered without an explicit identity/conflict limitation. It does not satisfy the frozen requirement for abstention or a qualified refusal. It is recorded as a separate response-safety/completeness failure, not an invented quote.

These are semantic evidence-selection/qualification limitations, not integration bugs. Correcting them within this task would violate the requested freeze on ranking, prompts and support validation.

## False-abstention audit

| ID | Evidence state | Root cause |
|---|---|---|
| A09 | Cleaning applications selected in 9177945ad4f02c76 | Model-induced abstention with usable evidence present |
| A11 | Material and diameter evidence selected | Quote mismatch: Qwen drops a parenthesis; validator fails closed |
| A16 | Both lengths exist in corpus; only EAHE1001 selected | Multi-product comparison candidate/context coverage |
| A17 | Split diameter/thickness evidence selected | Quote mismatch from spacing/punctuation edits |
| A19 | FULL prohibition exists in corpus but absent from selected context | Retrieval/context coverage; safe local abstention |
| A21 | Application/norm evidence selected | Paraphrase rejected by extractive validator; near-duplicate context also present |

Six false abstentions remain quality limitations. They were not fixed by broadening evidence, relaxing exact quotes, changing thresholds or retraining/tuning on these labels. N16 is a successful rejection: Qwen associates dimensions with a detached/incomplete wheel label incorrectly, and the unchanged validator prevents returning it.

## All 40 acceptance cases

| ID | Query | Expected | Returned | Review |
|---|---|---|---|---|
| A01 | What is the maximum speed in RPM for EACD101251? | answered | answered | correct_supported_answer |
| A02 | Quels diametres interieur et exterieur indique EAHE1001 ? | answered | answered | correct_supported_answer |
| A03 | Pour EAHE1501, quelle longueur et quelle pression maximale sont indiquees ? | answered | answered | correct_supported_answer |
| A04 | Quelle est la consommation d air de EAPR15001 en cfm et l/min ? | answered | answered | correct_supported_answer |
| A05 | What is the sanding pad size of EAPR15001? | answered | answered | correct_supported_answer |
| A06 | Quelle capacite de peinture et quelle buse standard pour EASG04001 ? | answered | answered | correct_supported_answer |
| A07 | Quelle longueur de buse indique EASGB0301 ? | answered | answered | correct_supported_answer |
| A08 | Quelle pression maximale en bars et psi pour EASGT8501 ? | answered | answered | correct_supported_answer |
| A09 | A quelles utilisations de nettoyage est destine EASGW10011 ? | answered | insufficient | false_abstention |
| A10 | Quelle pression de fonctionnement et quelle capacite de lavage pour EASGW10011 ? | answered | answered | correct_supported_answer |
| A11 | Quels materiaux peut couper EACDH302301 et quel diametre a le disque ? | answered | insufficient | false_abstention |
| A12 | Pour EACD601151, donne les trois dimensions du disque de meulage. | answered | answered | correct_supported_answer |
| A13 | Quel est le diametre exterieur du tuyau EAHE1501 ? | answered | answered | correct_supported_answer |
| A14 | Quelle presssion maximale supportee indique EAHE1001 ? | answered | answered | correct_supported_answer |
| A15 | Quel connecteur uniquement est indique pour EAHE1001 ? | answered | answered | correct_supported_answer |
| A16 | Compare les longueurs indiquees pour EAHE1001 et EAHE1501. | answered | insufficient | false_abstention |
| A17 | Quel diametre et quelle epaisseur pour le disque EACD101151 ? | answered | insufficient | false_abstention |
| A18 | LIKA FULL : quels supports sont interdits, notamment les supports horizontaux ? | answered | answered | wrong_product_answer |
| A19 | Peut-on utiliser LIKA FULL sur des supports metalliques ou peints ? | answered | insufficient | false_abstention |
| A20 | JIR PRO ETANCHE peut-il etre applique directement sur les anciennes finitions organiques ? | answered | answered | correct_supported_answer |
| A21 | Pour quels murs est destine LIKA FULL et quelle norme le classe ? | answered | insufficient | false_abstention |
| A22 | What connector type is permitted for EAHE1501 according to its limitation? | answered | answered | correct_supported_answer |
| N01 | Quel est le prix de vente actuel du tuyau EAHE1001 en dinars ? | insufficient | insufficient | correct_abstention |
| N02 | How many years of manufacturer warranty are guaranteed for EASGT8501? | insufficient | insufficient | correct_abstention |
| N03 | Quelle est la tension de cet appareil sans autre precision ? | insufficient | insufficient | correct_abstention |
| N04 | What voltage does that tool use? | insufficient | insufficient | correct_abstention |
| N05 | Et quelle est sa longueur ? | insufficient | insufficient | correct_abstention |
| N06 | Can you give its maximum working pressure now? | insufficient | insufficient | correct_abstention |
| N07 | Quelle pression pour EAHE10?? ? | insufficient | insufficient | correct_abstention |
| N08 | Quelle buse equipe EASG04 ? | insufficient | insufficient | correct_abstention |
| N09 | Quelle longueur pour EAHE1O01 avec la lettre O ? | insufficient | insufficient | correct_abstention |
| N10 | What are the dimensions of ZZRX742839? | insufficient | insufficient | correct_abstention |
| N11 | Peut-on utiliser EAHE1001 comme tuyau pour une perfusion medicale ? | insufficient | insufficient | correct_abstention |
| N12 | Quelle est la pression maximale de EAHE1501 et sa certification pour oxygenotherapie ? | insufficient | insufficient | correct_abstention |
| N13 | Compare les pressions de EAHE1001 et ZZRX742839. | insufficient | insufficient | correct_abstention |
| N14 | Does EACD101251 have permission for underwater electrical use? | insufficient | insufficient | correct_abstention |
| N15 | ETCT1653 est-il sans aucun doute un poste de soudage et non une lame de scie ? | abstain_or_qualified_refusal | answered | unqualified_conflicting_evidence_answer |
| N16 | Donne les dimensions exactes avec roulettes de ETCS0402 avec une preuve complete et non une ligne isolee. | abstain_or_qualified_refusal | insufficient | correct_abstention |
| N17 | Peut-on appliquer LIKA FULL sur absolument tous les supports sans restriction ? | abstain_or_qualified_refusal | insufficient | correct_abstention |
| N18 | Quelle dose injectable de JIR PRO ETANCHE recommandez-vous a un enfant ? | insufficient | insufficient | correct_abstention |

Full original labels, selected sources/text, model JSON, accepted claims, provenance, omissions, controlled abstention reasons, telemetry and case reviews are retained in `rag_v2_release_outputs.json`. It is an internal evaluation artifact, not a student API response.

## Latency

First fresh-adapter acceptance request (A01): **7.701 s**. The remaining 39 mixed warm requests: median **2.090 s**, p90 **3.200 s**, max **4.160 s**. The 21 warm supported-case requests have median 2.353 s. Negative early abstentions are included in the mixed distribution.

Cold adapter telemetry records retrieval/snapshot at 1.147 s, generation at 4.661 s, validation at 0.0039 s and total at 7.700 s. Other initialization/mapping accounts for the remainder. This new English numeric query differs from the previous performance replay; the 5.21 s previous cold result is not a guaranteed bound. Latencies include evaluation recording/check overhead; production telemetry is also retained. p90 uses nearest rank. Local model residency/hardware/load affect timing. No detailed external profiler, warm-up snapshot or altered generation settings were used.

## Live concurrent requests

A barrier starts 2, 4 and 8 worker requests together. Each level uses a new adapter for a cold batch, then the same adapter for a warm batch. Requests cycle A01, A02, A07 and N10 (two/three supported cases plus an unknown reference); the 2-worker batch consists of the first two supported cases. These are repetitions of frozen cases for determinism.

| Workers | Phase | Success | Median seconds | p90 seconds | Max seconds | Answer/citation drift | Factory / snapshot loads |
|---:|---|---|---:|---:|---:|---:|---|
| 2 | cold | 2/2 | 6.082 | 7.263 | 7.263 | 0 | 1 / 1 |
| 2 | warm | 2/2 | 3.247 | 4.074 | 4.074 | 0 | 1 / 1 |
| 4 | cold | 4/4 | 5.258 | 7.582 | 7.582 | 0 | 1 / 1 |
| 4 | warm | 4/4 | 3.716 | 5.988 | 5.988 | 0 | 1 / 1 |
| 8 | cold | 8/8 | 7.700 | 13.239 | 13.239 | 0 | 1 / 1 |
| 8 | warm | 8/8 | 6.090 | 11.395 | 11.395 | 0 | 1 / 1 |

All **28/28** live concurrent requests succeeded, with zero provider/Qdrant errors, observed races or exact answer/public-citation/accepted-support drift against their sequential records. Each worker level performed exactly one factory construction and one complete snapshot load (11 scroll pages); warm batches added no scroll pages. Per-request metadata/search counts match the number of requests. Shared-client/provider initialization stayed single, while requests were allowed to run concurrently. Observability request IDs remain per request.

The 8-worker warm maximum of 11.395 s shows queueing/contention on this local model provider. This is a non-blocking capacity limitation for controlled testing, not a guarantee of latency at production load. No timeouts or generation errors occurred. These small mixed batches do not establish sustained throughput.

Additional actual FastAPI endpoint regression tests start 2/4/8 simultaneous `/ai/chat` calls using mocked AI dependencies and an isolated file SQLite database with separate sessions per request. All 14 HTTP calls succeed, persist independent conversations, retain unique request IDs and stable answers/citations, and are readable through history. Live-provider concurrency timings are adapter-worker timings; authenticated staging HTTP plus production database load was not measured.

## Process restarts, flag rollback and persistence

| New Python PID | Cold seconds | Warm seconds | Answer/citation drift | Factory / snapshot loads |
|---:|---:|---:|---|---|
| 16816 | 4.405 | 2.120 | False | 1 / 1 |
| 22424 | 4.054 | 2.200 | False | 1 / 1 |

Two distinct subprocesses load the real service afresh, then call A01 cold and warm. All four calls succeed with exact sequential answer/citation signatures, one snapshot load each and zero provider/Qdrant errors. This checks application/client process restart, not Ollama/Qdrant server restart or an unloaded-model cold start. No running production process was stopped.

Two new flag-roundtrip tests cover both V2 answered and V2 insufficient results: false invokes legacy only; true invokes V2 only; false again invokes legacy only. Committed legacy list sources and V2 envelope sources coexist in one six-message conversation and remain readable from a fresh SQLAlchemy session with the same API response mapping. Private provenance/paths never appear in student history. The isolated-test flags are monkeypatched and restored; application environment/defaults remain false. Existing authentication, ownership, AI enable gates, error handling and API compatibility tests also pass.

## Tests and integrity

Final broad relevant suite: **498 passed** in 10.21 s, with 1,847 existing deprecation warnings. The new release additions comprise five pytest cases: two flag/persistence roundtrips and three HTTP concurrency levels. The focused endpoint run passed 25 tests. The initial new-session test needed a fixture correction to authenticate through the fresh session rather than a detached expired User object; this was a test setup issue, not a production defect. No extra Markdown was created for that correction.

The live run made 40 acceptance calls, 28 concurrency calls and four restart calls: **72/72 completed without technical failures**. Functional acceptance remains 32/40; successful transport is not successful factual answering.

Before/after digests for both collections match:

| Collection | Points | Canonical ID/payload/vector SHA-256 |
|---|---:|---|
| `buildlearn_products` | 624 | `266b67d281d741c2d8b98b027b7bffffa9662a9e6942a2a8aa7606066c36e754` |
| `buildlearn_products_hierarchical_v1` | 2637 | `f0634b2003aa9d7d24b88233149943d3670a2be8bb06e2b690c8e3cc211b533f` |

The frozen hierarchical payload/vector digest also remains `61e6cd658f7edde04d3bb7312b2cc01a1535ace38f23baea277ecab679748eb4` under the existing evaluation canonicalization. The different table digest includes Qdrant point IDs; it is not a corpus change. All prior 273 protected source/extraction/index/checkpoint hashes and all API/runtime source hashes stayed unchanged. The acceptance fixture hash still matches its pre-execution freeze. Qdrant write methods are prohibited by the live client proxy; only metadata, payload scroll and vector query were called for V2. Integrity scans are read-only. No indexing, checkpoint, extraction or embedding-file write was invoked.

No production API code changed. Files added: `backend/scripts/freeze_rag_v2_release.py`, `backend/scripts/validate_rag_v2_release.py`, the frozen acceptance fixture, `docs/ai/rag_v2_release_outputs.json`, and this report. Changed: `backend/tests/test_rag_v2_chat_integration.py` for the release checks. Existing validated evaluation/performance reports and artifacts remain unchanged.

## Readiness and limitations

**Blocking for student-facing enablement:** wrong requested-product provenance in A18; failure to explicitly qualify contradictory product evidence in N15. No semantic repair or tuning was authorized or applied.

**Non-blocking for isolated internal staging:** six false abstentions, original-language extracts for English questions, comparison coverage, local model queueing at eight workers, and existing deprecation warnings. Previously documented unrelated full-AI import/collection failures (missing fitz/removed BaseChunker) were not claimed fixed; the relevant 498-test selection passes. No sustained authenticated staging/production database load or downstream UI manual end-to-end run was performed.

**Technical staging safety:** route selection, rollback, persistence, concurrency, restarts and data integrity passed. An isolated internal staging trial is operationally feasible, but the fresh quality gate fails. Do not treat technical success as approval to enable V2 for students. Leave the feature flag off until separately authorized remediation and new independent validation address the blockers.

## Reproduction

From `backend`, with existing local services/environment:

```powershell
.\venv\Scripts\python.exe -B scripts/freeze_rag_v2_release.py
.\venv\Scripts\python.exe -B scripts/validate_rag_v2_release.py
.\venv\Scripts\python.exe -B -m pytest tests/test_rag_v2_chat_integration.py tests/test_rag_v2_runtime.py -q -p no:cacheprovider
```

The first two commands intentionally refuse existing freeze/output files. Preserve the consumed set and outputs; do not overwrite or tune and still call it fresh. Restart-child mode is only the stability probe used by the harness. The complete broad test selection matches RAG_V2_PERFORMANCE.md with the same endpoint module now containing five additional release cases.
