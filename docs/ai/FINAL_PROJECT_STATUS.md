# BuildLearn — final academic-submission status

Final verification date: **2026-09-27**. This document freezes and describes the existing implementation; it introduces no architecture, tuning, data update or feature activation.

**Disposition: validated academic prototype, with documented limits. `RAG_V2_ENABLED=false`. This submission does not claim production readiness or student readiness.** Final relevant tests: **599 passed, zero failures**. Live collection verification was unavailable during finalization because local Qdrant refused the connection; previous collection-integrity evidence is preserved and explicitly distinguished from today's local-file verification.

## A. Implemented architecture

1. **PDF acquisition and extraction.** Acquisition discovers manufacturer/product documents and records source provenance. Extraction produces canonical JSON with document metadata, pages, text/layout blocks and processing status. These persisted artifacts separate acquisition/extraction from downstream indexing and allow reproducible audits. OCR/layout quality remains a source limitation.
2. **Hierarchical chunking.** The parser and hierarchical chunker turn extraction blocks into ParentChunks and ChildChunks. Children retain exact source text, document/source metadata, block type, section path, page range, optional `parent_id` and ancestry. Parents provide structural context; they are not invented summaries. Recognized headings are assigned page-locally and forward-only.
3. **Embeddings and indexing.** Existing `EmbeddingService` uses Ollama `nomic-embed-text`. The checkpointed hierarchical index stores ChildChunks as Qdrant points with 768-dimensional COSINE vectors. Canonical extraction and checkpoints permit verification of parent context against its original corpus.
4. **Retrieval V2.** Query analysis → exact identifier routing → lexical and dense candidates → candidate union → deterministic reranking → selected ChildChunks → existing verified parent expansion. Candidate provenance records dense/lexical scores and ranks, identifier/filename/numeric matches and candidate sources. V1 remains separate. Existing lexical/dense candidate counts (50/100), ranking and thresholds were not changed during finalization. Expansion does not automatically fetch every sibling or invent context.
5. **RAG V2.** The selected evidence is supplied to the existing Ollama `qwen2.5-coder:7b` structured claim selector. The existing prompt, model, temperature/token settings and extraction requirements remain intact. Every returned factual claim must cite selected, explicitly allowed support IDs and pass exact-extractive validation. Unlisted/hidden fallback supports are prohibited. Insufficient evidence produces abstention; technical failure is handled separately without an uncited fallback answer.
6. **Safety and identity.** Semantic safety rejects wrong-product ownership and conflicting/mixed evidence conservatively. The canonical product catalog binds ownership to source/document metadata and exact child-text hashes, rather than a filename substring alone. Unknown/ambiguous variants fail closed. The current bounded requested-fact layer additionally checks attributes, qualifiers, units, application conditions, compatibility polarity and collective multi-fact/product coverage. It is not arbitrary natural-language entailment.
7. **Application integration.** The frontend `/student/chat` page uses the established backend **`POST /ai/chat`**. Its student-role V2 adapter is behind the explicit default-off flag; the legacy implementation remains. Authentication, authorization, public schemas and persisted conversation compatibility are preserved. Support IDs, document identity, pages, citations, abstention reasons and telemetry remain available internally; internal filesystem paths are excluded from student-facing projection. Flag-off behavior remains legacy. V2 does not use vague prior conversation text to manufacture a missing product identity.

The existing runtime reuses clients and an immutable lexical/corpus snapshot with synchronized initialization and integrity checks. It does not cache final answers or question-specific retrieval results.

## B. Dataset and hierarchy

| Item | Verified project inventory |
|---|---:|
| PDF/extraction source records | 221 |
| Distinct document IDs | 218 |
| Indexed unique ChildChunks | 2,637 |
| Reconstructed ParentChunks | 1,115 |
| Vector dimensions | 768 |
| Vector distance | COSINE |
| Hierarchical collection | `buildlearn_products_hierarchical_v1` |
| Separate legacy collection | `buildlearn_products` (624 points) |

Three repeated document IDs occur at different source paths; source-record count is therefore not a unique-document-ID count. The indexing report independently read back all hierarchical payloads/vectors with no missing points, duplicate child IDs, empty child texts or unresolved indexing failures.

The root-child audit found **239/2,637 children (9.06%)** with no parent, across 41 source records/39 document IDs. All have empty section paths. None violates the current heading-assignment contract or lost its parent during conversion. This does not prove every root fragment is semantically well structured: unrecognized headings, detached table fragments and OCR noise remain documented limitations.

## C. Validation milestones and interpretation

These measurements belong to their dated implementation snapshots and frozen sets. They are **not interchangeable current-state quality guarantees**. Consumed labels/artifacts were preserved; no experiment or tuning was performed during finalization.

| Milestone | Recorded result | Scope / limitation |
|---|---|---|
| Dense baseline, 34 queries | Hit@1 11.8%; Hit@3/5/10 29.4%; evidence recall@3 27.94%; MRR 0.1912 | Thresholds 0.0–0.6 did not improve results |
| Retrieval diagnostic | Lexical evidence recall@3 85.29%; identifier routing 69.12%; 17/17 identifier queries route unambiguously; 11 queries lack correct evidence in dense top 100 | Motivated lexical+dense candidate generation; calibration set is consumed |
| Retrieval V2, 20 source-disjoint held-out queries | Evidence recall@3 100%; document recall@3 100%; Hit@1 95%; MRR@3 0.9667 | Small positive-only set; source/template ambiguity remains |
| Original RAG validation after support fixes | 19/20 positives answered; 10/10 negatives abstained; 29/29 returned claims had valid allowed supports/exact citations | Historical snapshot before later conservative semantic/identity/fact gates |
| Independent original RAG validation | 7/8 positives answered; 8/8 negatives abstained | Historical snapshot; not evidence of universal safety |
| Endpoint/performance shadow replay | 6/6 supported answered; 4/4 negatives abstained; exact answers/citations/support IDs preserved by runtime optimization | Direct local services, not user-visible traffic |
| Fresh release acceptance, 40 queries | 15/22 correct supported answers; 17/18 negative/conflict abstentions; 32/40 functional acceptance | Discovered A18 wrong-product and N15 unqualified-conflict blockers |
| Semantic-safety consumed release regression | 14/22 supported answers; 18/18 negative/conflict abstentions; zero observed wrong-product/conflicting answers | Preserved 14/15 formerly correct supported answers; conservative A20 loss |
| Semantic independent / fresh follow-up | 2/10 supported and 10/10 negative abstentions; follow-up 3/4 supported and 4/4 negatives | Explicit evidence-coverage cost; no general readiness claim |
| Canonical identity, fresh 28-query set | 5/16 fully correct supported answers; 12/12 negatives abstained; zero wrong-product/unqualified-conflict claims; 6/6 returned supports/citations valid | 6/16 API answered, but PI14 answered the wrong requested fact; 10 false abstentions |

### Latest requested-fact work: incomplete independent confirmation

The frozen 30-query fact-alignment artifact records **16/20 supported queries answered**, four supported abstentions and **9/10 negative abstentions**, with no technical failures. Answered is an API status, not a claim that every answer received a completed independent completeness review. FA24 incorrectly accepted a voltage range for an explicitly requested unique exact value. This remains visible in the original artifact.

Subsequent bounded numeric-range/minute/qualifier corrections are present in the frozen code and covered by the final **61 fact-alignment tests**. There is **no new independent live validation of those final corrections**. Finalization intentionally stopped further experiments; the old artifact must not be relabeled as validating the corrected implementation. The prior fact-alignment reporting/evaluation cycle was unfinished when the submission freeze was requested; no standalone fact-alignment Markdown report was produced. Its JSON evidence is retained, and this document records the limitation.

Consumed product-identity regression with the fact layer recorded 4/16 positive answers and 12/12 negative abstentions: PI14's maximum-for-minimum answer was rejected; grammar examples PI05/PI12 recovered, while PI13 still failed the existing extractive validator. Other conservative coverage losses remain. These intermediate artifacts predate the final numeric correction and are regression evidence only.

## D. Recorded performance and concurrency

No new performance experiment was run for submission. These historical local measurements precede the latest identity/fact checks and do not certify the final state's latency or a production SLA.

| Measurement | Cold total | Warm median | Warm p90 | Warm maximum |
|---|---:|---:|---:|---:|
| Original integration shadow | 43.38 s | 16.45 s | Not reported here | 18.02 s |
| Paired runtime baseline | 45.817 s | 10.443 s | 10.975 s | 11.640 s |
| Optimized profiled replay | 5.213 s | 2.113 s | 2.269 s | 2.950 s |
| Release acceptance, mixed queries | 7.701 s | 2.090 s | 3.200 s | 4.160 s |

In the optimized replay, snapshot loading fell from 25.683 s to 2.059 s and warm snapshot work was zero. Warm generation median remained 1.703 s, versus approximately 0.286 s lexical work, 0.057 s dense/metadata work and 0.018 s verified-parent/context work. Model generation is a distinct latency component. Cold means fresh adapter/process state with local services/model residency as recorded, not a fully unloaded model/server restart.

Release concurrency succeeded on **28/28 requests** across cold and warm batches of 2, 4 and 8 simultaneous requests. No observed provider/Qdrant errors, races, duplicate initialization or answer/citation/support drift occurred; each batch level initialized one adapter/snapshot. Warm medians/p90s were respectively **3.247/4.074 s**, **3.716/5.988 s**, and **6.090/11.395 s**. Eight-worker queueing is a capacity limitation. Two fresh subprocesses also completed all four cold/warm calls with stable answers/citations. These small historical batches do not establish sustained throughput for the final state.

## E. Safety, correctness and remaining limits

- **Wrong-product blocker A18:** LIKA FULL could previously receive a LIKA FINA excerpt with syntactically valid citations. Ownership checks now reject cross-product substitution, including similar names and filename aliases without verified ownership.
- **Contradiction blocker N15:** mixed ETCT1653/ELCS1652 evidence previously produced an unqualified exact quotation. Conflicting ownership/evidence now causes a conservative refusal. Exact quotation alone is not sufficient for semantic correctness.
- **Canonical catalog:** 221 source records, 199 mapped records, **192 canonical products**, **22 quarantined ambiguous/mixed records**. Ownership binds source paths/document IDs, filename metadata, explicit references/declarations and child-text hashes. Catalog staleness against extraction/checkpoint identity fails closed.
- **Requested-fact correctness:** minimum/maximum, first-pass/total, exact/range and multi-fact coverage require explicit alignment. Latest independent confirmation remains unfinished as described above; zero citation errors is not equivalent to zero wrong-fact errors.
- **Coverage:** selected context may lack the requested fact or target identity even when the full corpus contains it. No hidden sources/siblings are fetched to mask that failure. False abstentions, model support-formatting failures, bounded entity grammar and truncated/OCR labels remain visible.
- **Scope:** bounded conflict/compatibility patterns do not prove unrestricted entailment. Conservative abstention protects safety at the cost of completeness. Current price/warranty, unsupported applications, ambiguous references and vague follow-ups may remain unanswered. Extractive responses can retain source-language/OCR artifacts.

## F. Final tests and integrity

Final broad relevant backend selection: **599 passed, 0 failed, 1,847 existing warnings, 12.45 s**. It covers legacy chat/service, flag integration and runtime lifecycle, identity/semantic/fact safety, grounded RAG/support validation, both retrieval paths, embedding/vectorstore behavior, hierarchical indexing/pipeline/chunkers and existing RAG/LLM tests. Tests use mocks/temporary data; this is not a fresh live LLM acceptance run.

Wider `tests/ai --collect-only`: **781 tests collected, six collection errors**. `test_chunking.py` imports the obsolete `BaseChunker`; `test_extraction.py`, `test_extraction_e2e.py`, `test_full_runner.py`, `test_pdf_inspector.py` and `test_renderer.py` require unavailable `fitz`/PyMuPDF. These previously documented issues were not repaired under the freeze. The passing selection does not mean the entire repository test suite passes. Warnings include existing datetime, Starlette/httpx and pytest-fixture deprecations.

Final integrity evidence is in [final_project_integrity.json](final_project_integrity.json):

- Effective feature flag is **false**; `.env.example` explicitly sets false, and active `.env` leaves it unset (default false).
- **291 protected file hashes unchanged** before/after final tests. **252 immutable pipeline/data files** also match the historical endpoint-shadow baseline, including indexed extraction/checkpoint material. Retrieval V2 retains SHA-256 `bec257494381f2d42df473c1372013fb56183b4450860565c1d9013f9fac0c48`.
- **31 pre-existing reports/artifacts unchanged** before/after finalization checks; consumed labels are in the protected inventory. No evaluation artifact was overwritten.
- No production code, ranking, RAG semantics, identity rules, model settings, API schema, indexing or checkpoint was modified by this finalization. No Qdrant mutation was invoked.
- **Today's live Qdrant digest check could not complete:** `127.0.0.1:6333` refused the connection. No server restart/data repair was performed. Therefore collection equality today is not asserted as freshly measured.

Last successful read-only ID/payload/vector digests, repeatedly preserved through prior evaluations:

| Collection | Points | SHA-256 |
|---|---:|---|
| `buildlearn_products` | 624 | `266b67d281d741c2d8b98b027b7bffffa9662a9e6942a2a8aa7606066c36e754` |
| `buildlearn_products_hierarchical_v1` | 2,637 | `f0634b2003aa9d7d24b88233149943d3670a2be8bb06e2b690c8e3cc211b533f` |

Earlier reports sometimes use a payload/vector canonicalization without point IDs; its hierarchical hash is `61e6cd658f7edde04d3bb7312b2cc01a1535ace38f23baea277ecab679748eb4`. Different digest formats must not be compared directly.

Reproduce the final passing selection from `backend` with the existing venv (use a fresh temporary directory):

```powershell
.\venv\Scripts\python.exe -B -m pytest tests/test_chat.py tests/test_chat_service.py tests/test_rag_v2_chat_integration.py tests/test_rag_v2_runtime.py tests/ai/test_fact_alignment_v2.py tests/ai/test_product_identity.py tests/ai/test_semantic_safety_v2.py tests/ai/test_hierarchical_rag_v2.py tests/ai/test_rag_v2_answer_validation.py tests/ai/test_retrieval_v2.py tests/ai/test_hierarchical_retrieval_eval.py tests/ai/test_retriever.py tests/ai/test_context_builder.py tests/ai/test_embeddings.py tests/ai/test_vectorstore.py tests/ai/test_hierarchical_retriever.py tests/ai/test_hierarchical_indexer.py tests/ai/test_hierarchical_pipeline.py tests/ai/test_technical_chunker.py tests/ai/test_hierarchical_chunker.py tests/ai/test_rag_service.py tests/ai/test_llm_provider.py tests/ai/rag -q -p no:cacheprovider --basetemp C:\Users\user\Desktop\stage\.tmp\academic_final_recheck --tb=short
```

## G. Final disposition

BuildLearn is submitted as a **validated academic prototype** demonstrating traceable hierarchical retrieval, grounded claim selection, conservative ownership/conflict checks and feature-isolated application integration. Retrieval quality is strong on its small frozen held-out set; answer safety and completeness require their own evaluation and remain limited. Historical successes are not used to conceal later failures or unfinished confirmation.

**`RAG_V2_ENABLED` remains false.** No production/student rollout, new tuning, new acceptance experiment or data mutation was performed. The frozen implementation and evidence are suitable for academic analysis; they are **not a claim of production readiness or student readiness**.

## H. Major reports, in development chronology

This is workflow chronology, not filesystem modification-time ordering (some reports were revised later).

1. [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) — original architecture overview; older route/config sketches are superseded by integration evidence.
2. [DATA_ACQUISITION_REPORT.md](DATA_ACQUISITION_REPORT.md) — acquisition reporting. Its current contents describe a small test-product run, not the authoritative 221-record final inventory; preserved unchanged.
3. [HIERARCHICAL_INDEXING_REPORT.md](HIERARCHICAL_INDEXING_REPORT.md) — completed indexing/readback and dataset inventory.
4. [ROOT_CHILDREN_AUDIT.md](ROOT_CHILDREN_AUDIT.md) — exhaustive root-child audit.
5. [RETRIEVAL_ARCHITECTURE.md](RETRIEVAL_ARCHITECTURE.md) — hierarchical Retrieval V1.
6. [RETRIEVAL_EVALUATION_REPORT.md](RETRIEVAL_EVALUATION_REPORT.md) — labeled dense baseline and threshold calibration.
7. [RETRIEVAL_V2_DIAGNOSTIC.md](RETRIEVAL_V2_DIAGNOSTIC.md) — candidate recall/identifier/lexical diagnosis.
8. [RETRIEVAL_V2_ARCHITECTURE.md](RETRIEVAL_V2_ARCHITECTURE.md) — separate deterministic hybrid path.
9. [RETRIEVAL_V2_EVALUATION.md](RETRIEVAL_V2_EVALUATION.md) — frozen source-disjoint held-out comparison.
10. [RAG_V2_EVALUATION.md](RAG_V2_EVALUATION.md) — generation/support validation and false-abstention work.
11. [RAG_V2_ENDPOINT_INTEGRATION.md](RAG_V2_ENDPOINT_INTEGRATION.md) — default-off `/ai/chat`, provenance/privacy and shadow comparison.
12. [RAG_V2_PERFORMANCE.md](RAG_V2_PERFORMANCE.md) — runtime overhead optimization and exact shadow equivalence.
13. [RAG_V2_RELEASE_READINESS.md](RAG_V2_RELEASE_READINESS.md) — fresh acceptance, concurrency/restarts and discovered blockers.
14. [RAG_V2_SEMANTIC_SAFETY.md](RAG_V2_SEMANTIC_SAFETY.md) — conservative ownership/conflict remediation and coverage costs.
15. [RAG_V2_PRODUCT_IDENTITY.md](RAG_V2_PRODUCT_IDENTITY.md) — canonical catalog/quarantine and independent identity results.
16. [FINAL_PROJECT_STATUS.md](FINAL_PROJECT_STATUS.md) — final submission disposition and verification.

Corresponding frozen fixtures, JSON evaluation outputs and integrity artifacts retain per-query evidence, rejected output and implementation/corpus hashes. The fact-alignment JSON artifacts are retained without a completed standalone report; their current confirmation limits are stated above. This final task added only this status report and its integrity evidence file.
