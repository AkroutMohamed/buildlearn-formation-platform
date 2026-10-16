# Feature-flagged student chat integration for Hierarchical RAG V2

The integration is implemented with **`RAG_V2_ENABLED=false` by default and still disabled locally**. It preserves the existing legacy path, authentication, conversation ownership, message persistence and public response schema. Validated Retrieval V2 and both RAG V2 implementation/validation modules remain byte-for-byte unchanged.

## Existing application inspected

The browser page is `/student/chat`, but its established backend API is **`POST /ai/chat`**, via `frontend/src/services/chat.service.ts`. There is no existing backend `/student/chat` handler to replace. This integration uses the current `/ai/chat` route and its `/ai/conversations` endpoints; it adds no competing route and deletes no legacy implementation.

The existing request fields remain `question`, `conversation_id`, `top_k` and `messages`. Response fields remain exactly `answer`, `sources`, `conversation_id` and `created_at`. `sources` is already a list of arbitrary dictionaries, so citation metadata requires no response-schema or frontend type migration. Conversation/message schemas and database columns remain unchanged.

Before implementation, the endpoint/dependency, ChatService, repository/model behavior, request/response models, frontend source cards, legacy retriever/context/LLM and validated V2 configuration/validator were inspected.

## Flag and routing

`app/ai/api/rag_v2_endpoint.py` reads `RAG_V2_ENABLED`. Only the literal `true`, case-insensitively, enables it; absent, false and misspelled values retain legacy behavior. `.env.example` explicitly declares `RAG_V2_ENABLED=false`. No active `.env` or running application flag was enabled.

`get_chat_service` continues to supply the original RAGService unless both the flag is enabled and the authenticated role is `student`. Other previously authorized roles retain their legacy path. The existing `AI_ENABLED` gate and HTTP exception handling remain. The authenticated user dependency is reused through FastAPI dependency caching; no authentication or role permission is bypassed.

The V2 adapter is created lazily and cached. It calls the existing `HierarchicalRAGV2` with its unchanged configuration and shared underlying retriever/provider. Per-request observers wrap those dependencies without changing their arguments/results. There is no global validator monkeypatch, fallback retriever, new index or new collection.

RAG defaults remain top K=3, 6,000 context characters, 1,000 question characters, 600 output tokens, temperature 0 and seed 0. Retrieval candidate counts remain lexical 50 / dense 100; its existing dense threshold 0.0 and deterministic ranking remain unchanged. The adapter does **not** forward the chat request's `top_k` into the validated configuration. It accepts existing history/messages fields but does not add prior conversation text to the frozen evidence prompt. Stored conversation behavior remains; underspecified follow-ups may therefore abstain until the student names a product.

The optional integration-only `RAG_V2_OLLAMA_MODEL` selects the installed Qwen model, defaulting to the validated `qwen2.5-coder:7b`. Existing global Ollama/embedding settings, models and providers remain unchanged; no download or replacement occurs. This machine's existing legacy model also uses `qwen2.5-coder:7b`.

The flag-off question-length behavior remains the original 2,000-character ChatService limit. Flag-on V2 additionally enforces its unchanged 1,000-character limit and returns the existing 400 error shape for longer questions. No truncation or hidden fallback is introduced.

## Response and provenance mapping

Answered V2 output keeps its exact validated answer text and `[SOURCE N]` citations. Public sources include only sources actually cited by accepted claims. Each contains:

- `source_id`, anchoring `chunk_id`, actual `support_chunk_id`, `document_id`;
- a safe filename, page start/end and evidence kind;
- an existing `product_name` display label such as `SOURCE 1: AX123 Data.pdf` so current source cards identify the answer's citation.

No `source_path`, raw retrieval context, prompt, model output, internal warning or fabricated document URL is exposed. Filenames are URL-decoded and stripped of directory components, including encoded Windows paths. V2 reranking scores are omitted from public cards because the existing frontend multiplies scores by 100 and labels them as percentages; those scores are not calibrated probabilities. Exact scores and original filename metadata remain in internal provenance.

`V2ChatResponse` inherits the unchanged ChatResponse fields and stores audit data in a Pydantic PrivateAttr, which is absent from API serialization. ChatService stores a versioned JSON envelope in the existing nullable `Message.sources` text column:

```json
{
  "format": "rag_v2",
  "sources": ["safe public source dictionaries"],
  "provenance": {
    "request_id": "server-generated UUID",
    "status": "answered or insufficient",
    "abstention_reason": "controlled reason or null",
    "citations": ["accepted claims with exact quotes and support IDs"],
    "sources": ["internal source IDs, document/filename/page metadata and scores"],
    "telemetry": {"outcome": "answered or abstained"}
  }
}
```

This is a representation sketch, not a changed public API schema. Conversation history unwraps only the safe `sources` list. Existing legacy stored arrays/null values remain unchanged and readable. This avoids exposing provenance through `/ai/conversations/{id}/messages` and requires no migration. Ownership checks and existing commits/title/history handling remain in ChatService. Technical failures, as in the legacy flow, can leave the already-saved user message but do not invent or persist an assistant answer.

## Insufficiency versus technical failure

| Result | API behavior | Fallback |
|---|---|---|
| Supported, validated claims | 200, existing schema, exact answer/citations | None |
| Missing/ambiguous evidence or rejected support/claim | 200, original V2 abstention, no public citations | None |
| Qdrant/query-embedding failure | Existing 502 error shape, generic temporary-unavailability detail | None |
| Ollama/generation failure | Existing 502 error shape, generic temporary-unavailability detail | None |
| Malformed model JSON/schema or unexpected validator failure | Existing 502 error shape, generic temporary-unavailability detail | None |
| Empty/over-budget V2 question | Existing 400 error shape | None |
| Existing authentication/ownership/AI gate failures | Existing 401/404/422/503 handling | None |

The standalone validated RAG service catches generation errors into an insufficient response. The adapter's dependency observer records whether an actual provider exception occurred, allowing the endpoint to distinguish that technical failure from factual insufficiency without modifying RAG behavior. Validator-format warnings map to controlled technical-failure codes; ordinary evidence/support rejection maps to a safe abstention. Raw exception text and internal paths do not become response details.

## Observability

Each V2 attempt emits one structured `rag_v2_request` log with:

- server-generated request UUID;
- retrieval, generation, validation and total durations in milliseconds;
- `answered`, `abstained`, `technical_failure` or `invalid_request` outcome;
- retrieved child count, supplied-context source count and accepted claim count;
- controlled validation rejection and technical failure codes.

Generation/retrieval observers are per request. Validation timing uses a thread-local Python profiling scope around the existing validator, restoring/chaining any previous profiler. It changes neither validator inputs/results nor its implementation. Tests cover restoration and concurrent requests. An unexecuted stage records zero duration. Total duration covers the adapter, including cold initialization/mapping, rather than authentication/SQL/HTTP transport; existing request middleware separately measures the HTTP request.

Logs contain no new question, conversation history, source quote, raw model response, filesystem path or raw exception message. Successful/refused responses persist the request ID and telemetry in private provenance. Technical failures retain their observability log without persisting a fabricated assistant message. Existing legacy logging is untouched.

## Tests

The final broad relevant selection passed **475 tests, zero failures**, in 8.71 seconds, with **1,847 existing deprecation warnings**. It includes **19 new integration test cases**, existing chat API/service tests, validated RAG/validator tests, Retrieval V1/V2, legacy RAG/LLM, context/embedding/vector-store and hierarchical chunking/indexing regressions. The focused chat selection passed **38 tests**; counts overlap.

An additional attempt to collect all `tests/ai` stopped before execution with six pre-existing collection issues:

- `test_chunking.py` imports the no-longer-exported `BaseChunker`;
- `test_extraction.py`, `test_extraction_e2e.py`, `test_full_runner.py`, `test_pdf_inspector.py` and `test_renderer.py` require unavailable `fitz`/PyMuPDF.

Those unrelated components/dependencies were not changed. Existing warnings concern datetime/fixture deprecations and the Starlette TestClient/httpx deprecation.

New coverage includes default-off and explicit-on behavior, other roles, authentication/AI gate, supported answers, safe abstention, invalid support rejection, malformed JSON/schema, unavailable retrieval/Ollama/initialization, generic errors, no legacy fallback, persisted citations/pages/IDs, path-free immediate/history responses, encoded filename paths, mixed legacy/V2 conversations and ownership checks, schema compatibility, private observability, profiler restoration and concurrency. A real RetrievalV2 instance with a read-only mock client checks only `get_collection`/`scroll`/`query_points`, fixed candidate counts, threshold and hierarchical collection isolation. A fixture hashes validated/index/checkpoint components before/after the module.

## Files changed

- Added `backend/app/ai/api/rag_v2_endpoint.py`.
- Updated `backend/app/dependencies/chat.py`, `backend/app/services/chat_service.py` and `backend/app/ai/api/routes.py`.
- Updated `backend/.env.example` with the disabled flag and explicit V2 model option.
- Added `backend/tests/test_rag_v2_chat_integration.py`.
- Added `backend/scripts/shadow_rag_v2_chat.py` and `docs/ai/rag_v2_endpoint_shadow.json`.
- Added this substantial integration report.

Extraction, chunking, embeddings, indexing, Retrieval V2 ranking and RAG V2 validation behavior were not changed. Both validated RAG files and 271 pre-integration protected files matched their baseline hashes after implementation/testing. Final shadow integrity results and comparison are recorded below.

## Final local shadow comparison

The final replay completed **10 fresh synthetic questions** through the actual legacy RAGService and the V2 chat adapter, using identical requests and empty history. Six supported queries use six source files outside the consumed 34-query retrieval set, 20-query retrieval held-out set and eight-source independent RAG validation. Four new unsupported/ambiguous questions were included. Actual indexed filenames/evidence were inspected first, and queries were frozen in the harness before calling either model. No labels, prompts, ranking, thresholds or configurations were tuned from these results.

The harness calls services directly: it does not POST to a live student endpoint, create conversations, connect a production SQL session or toggle the flag. Both models use the existing installed Qwen coder model. The initial run was repeated after the final URL-decoded-filename privacy refinement so the saved adapter hash matches the delivered implementation. That refinement changes public filename projection only; it does not tune retrieval or generation. Full final results and internal citation/telemetry metadata are in `rag_v2_endpoint_shadow.json`.

| ID | Query scope | Legacy | V2 |
|---|---|---|---|
| S01 | EWPPJ15001 nominal power | Information not found | Exact 1500 W evidence |
| S02 | ECIWL42461 socket sizes | Information not found | Exact 14/15/17/19/21 mm evidence |
| S03 | EDMR5310002 maximum DC range | 1000 V answer | Exact range ending at 1000 V |
| S04 | ELWLI20885 voltage / LED power | 20 V and 22.5 W answer | Exact same evidence |
| S05 | EDMR762001 maximum AC-current range | Information not found | Exact 4A/40A/400A range |
| S06 | EWPPQD07501 applications | Information not found | Exact sewage-pumping / irrigation / domestic-use evidence |
| S07 | Unknown ABCXYZ957359 reference | Abstained | Abstained before generation |
| S08 | Unspecified tool voltage | Chose a particular 20 V blower | Abstained for ambiguous product identity |
| S09 | Unsupported intravenous pump use | Abstained | Abstained |
| S10 | Current ELWLI20885 price | Abstained | Abstained |

Observed results: legacy answered **2/6** supported questions and abstained on **3/4** negatives; V2 answered **6/6** supported questions and abstained on **4/4** negatives. All **6 accepted V2 claims** use explicitly allowed source IDs and exact indexed child text, verified against the source snapshot; each cited its expected file. There were **zero technical failures** and no unsupported returned V2 claims observed. All ten request IDs are distinct. This is a small qualitative shadow comparison, not a new comprehensive retrieval benchmark or universal semantic-correctness proof.

Measured V2 cold adapter latency was **43.38 seconds**, including **31.65 seconds** for first retrieval/snapshot initialization. Warm-request median was **16.45 seconds** (range **6.24?18.02 seconds**). Local latency remains a limitation; no networking/model/retrieval settings were changed to improve it. Stage durations and rejection reasons are saved for diagnosis.

## Final integrity and reproduction

The final shadow's before/after payload/vector digests match for both collections:

- Hierarchical: 2,637 points, SHA-256 `61e6cd658f7edde04d3bb7312b2cc01a1535ace38f23baea277ecab679748eb4`, matching the validated baseline.
- Legacy `buildlearn_products`: 624 points, SHA-256 `266b67d281d741c2d8b98b027b7bffffa9662a9e6942a2a8aa7606066c36e754` under the shadow harness's ID/payload/vector canonicalization.

Protected source/extraction/index/checkpoint hashes, the adapter hash and the disabled flag all passed the final guard. No Qdrant create/upsert/delete/collection-setting API was called. No extraction, embedding, indexing or checkpoint write was invoked. Process/access logs are outside the data-digest guard.

From `backend`, with the existing environment and venv:

```powershell
.\venv\Scripts\python.exe -B -m pytest tests/test_rag_v2_chat_integration.py tests/test_chat.py tests/test_chat_service.py -q -p no:cacheprovider
.\venv\Scripts\python.exe -B scripts/shadow_rag_v2_chat.py --restart --batch-size 10
```

Preserve reviewed artifacts before using `--restart`. Without it, the harness resumes only compatible implementation/data snapshots. It refuses to run with the feature flag enabled. This is an explicit local evaluation command, not automatic shadow traffic on user requests.

The broad successful pytest selection was:

```powershell
 .\venv\Scripts\python.exe -B -m pytest tests/test_chat.py tests/test_chat_service.py tests/test_rag_v2_chat_integration.py tests/ai/test_hierarchical_rag_v2.py tests/ai/test_rag_v2_answer_validation.py tests/ai/test_retrieval_v2.py tests/ai/test_hierarchical_retrieval_eval.py tests/ai/test_retriever.py tests/ai/test_context_builder.py tests/ai/test_embeddings.py tests/ai/test_vectorstore.py tests/ai/test_hierarchical_retriever.py tests/ai/test_hierarchical_indexer.py tests/ai/test_hierarchical_pipeline.py tests/ai/test_technical_chunker.py tests/ai/test_hierarchical_chunker.py tests/ai/test_rag_service.py tests/ai/test_llm_provider.py tests/ai/rag -q -p no:cacheprovider
```

## Disposition and remaining limitations

**Leave `RAG_V2_ENABLED=false`.** No deployment, flag activation, migration or user-visible shadow switching was performed. The integration is available for an explicitly controlled future enablement and can return to legacy by disabling the flag.

The previously documented missing HYDROMUR prohibition boundary, FINA1 reference false abstention, OCR readability, source-language/extractive answer limitations and lack of general semantic guarantees remain unchanged. Missing evidence is not repaired by fetching extra siblings or falling back to an uncited LLM. Current local latency and the unrelated full-AI collection errors remain reported. Existing conversation persistence/auth/schema behavior is preserved; V2's evidence-only treatment of history, fixed K and shorter validated question budget are explicit enabled-path limitations.
