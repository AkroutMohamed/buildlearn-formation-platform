# RAG V2 conversation and completeness UX

Date: 2026-09-27

## Behavior

The endpoint now resolves bounded elliptical questions from the saved conversation's user turns. It reuses the canonical identity resolver; it does not infer products from assistant prose, filename resemblance, or client-supplied messages. An explicitly named product is left unchanged. A new chat cannot inherit a product. A comparison, ambiguous family, or unknown variant blocks inheritance and requests clarification. The original user message remains persisted unchanged; only the internal retrieval/generation question receives the canonical product name. No shared mutable conversation state is introduced.

Identity supplied by history is not evidence. Retrieval runs afresh and all existing ownership, allowed-support-ID, extractive, semantic-safety, and requested-fact validators still apply. Retrieval ranking/configuration, context limits, model, generation settings, prompts, collection data, and feature flag settings are unchanged.

Completeness was already enforced by the requested-fact validator. This change retains full rejection of partial answers and gives a more useful explanation when fact alignment/completeness fails. It does not render a partially validated answer. Broad product overviews use separated bullet paragraphs for validated extracts; specific answers retain their previous rendering. No source excerpts are rewritten or supplemented.

## Validation evidence

New offline tests cover French/English follow-ups, product switching, comparison ambiguity, unknown variants, new-chat isolation, assistant-text exclusion, current-turn removal, explicit question preservation, and adapter routing/clarification without retrieval or generation.

The fresh live cases were frozen in `rag_v2_conversation_fresh_cases.json` before execution. Results are stored separately in `rag_v2_conversation_fresh_results.json`; prior artifacts were not overwritten. This eight-case run is a conversation smoke check, not a new labeled answer-quality benchmark:

- C01/C02 inherited the PAP2 identity correctly and conservatively abstained on consumption/weight requests.
- C03 clarified after a two-product comparison.
- C04 clarified in a new chat despite a supplied previous-history list.
- C05 switched to FINA correctly and rejected an unsupported generated claim.
- C06 clarified after an unknown product variant instead of restoring PAP2.
- C07 answered the standalone PAP2 resistance question with one validated cited claim (flexion >2 Mpa and compression >6 Mpa).
- C08 abstained on an unsupported weight/voltage request rather than presenting a partial answer.

No technical failures occurred. Three of three clarification cases clarified; three of three inheritance cases selected the intended canonical identity. Only one factual claim was returned, through the existing validators. This is not independent human adjudication of general answer completeness. Cold first case took 8.658 seconds; remaining cases took 0.116–2.970 seconds. No latency tuning was performed.

The stored live results predate a small telemetry correction: clarification abstention reasons are now recorded as `missing_conversation_product` or `ambiguous_conversation_product`, rather than the generic `no_usable_context`. The original result artifact is preserved.

## Limits and checks

History is limited to the existing six-turn window. If the explicit product has fallen out of that window, clarification is required. Arbitrary pronoun/coreference resolution is outside scope. Evidence absent from final selected context remains absent; this work does not fetch extra sources or relax completeness checks.

The existing short-question language heuristic can produce an English generic refusal for a French follow-up (observed C05); this limitation was recorded rather than tuned against the fresh run. Answer coverage remains conservative: safe product resolution does not guarantee that the requested fact can be answered.

Full AI test discovery encounters existing missing `fitz` imports and the obsolete `BaseChunker` test import. An expanded discovery attempt was stopped while unrelated acquisition/scraper tests were running. The focused retrieval/RAG/safety/identity/runtime/endpoint suite is the relevant regression check; its final result is recorded below. No extraction, chunking, embeddings, indexing, checkpoint, Qdrant, or frontend source was modified in this task. Live smoke calls use the adapter directly and do not persist conversations.

Files changed: `conversation_context_v2.py` (new), `product_identity.py` (display-name accessor only), `rag_v2_endpoint.py`, `hierarchical_rag_v2.py`, new conversation tests, the fresh cases/results, and `scripts/evaluate_conversation_ux_v2.py`.

Final focused regression result: **345 passed, 0 failed**, 35 existing deprecation warnings, 7.82 seconds. This includes 14 new conversation tests. The endpoint integration fixture's indexing/checkpoint/validated-component protection checks passed. No new model or retrieval tuning was performed.
