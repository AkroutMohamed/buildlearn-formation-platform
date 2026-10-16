# RAG V2 runtime performance

## Scope and outcome

Runtime-only optimization of the default-off student-chat adapter. Retrieval V2, RAG V2 generation/validation, extraction, chunking, embedding implementation, indexing, schemas and Qdrant data remain byte-for-byte unchanged. `RAG_V2_ENABLED=false` remains the default and the actual local setting. No final answers, query embeddings or retrieval results are cached.

The paired detailed replay reduced first process-cold latency from 45.82 s to 5.21 s and warm median from 10.44 s to 2.11 s. All ten frozen shadow cases retained exact decisions, accepted claim dictionaries/support IDs, quotes, rendered answers, public citations and internal selected-source provenance (including dense/lexical scores and ranks). Six supported cases answered; four negatives abstained.

## Profiling protocol and bottlenecks

The harness makes direct adapter calls with the flag disabled: one cold S01 request on a new adapter, then S01-S10 on that same adapter. It does not persist conversations, call the user-visible endpoint, unload models, warm a snapshot ahead of the cold call or tune on labels. Cold means a fresh process-local adapter, corpus snapshot and embedding provider; the already running Ollama service/model residency is outside this definition. Each warm distribution contains ten requests. p90 uses nearest rank (ninth sorted sample); median averages the middle two samples. Missing generation/validation stages, including early reference abstention S07, count as zero.

Detailed measurements use a thread-local profiler chained through existing validation telemetry. The stage durations are exclusive wall time: nested query embedding and parent construction are subtracted from dense retrieval/merge stages. Snapshot loading includes collection validation, eleven payload-only scroll pages, index construction and digest calculation. Dense Qdrant includes its per-request collection metadata check, dense search, hit validation, sorting and existing V1 rendering overhead. Parent/context includes per-request extraction/checkpoint/hash verification and unchanged RAG context construction. Public mapping measures `public_sources`; remaining response object/internal provenance work belongs to Other mapping/telemetry. Initialization after optimization includes constructing the unchanged EmbeddingService and its one-time dimension probe.

Before changes, snapshot loading took 25.68 s; warm dense Qdrant/metadata median was 4.13 s and query embedding median 2.05 s. Warm snapshots were already reused, and parent verification was only tens of milliseconds. No new parent cache or skipped metadata/source verification was justified.

A separate HTTP check measured collection metadata at 2.269 s via localhost versus 0.161 s via 127.0.0.1; Ollama tags took 2.326 s versus 0.156 s. Responses matched after excluding Qdrant's per-request `time` field. This identifies repeated local connection fallback as the main implementation overhead. Read-only full collection digests subsequently verified the same data through IPv4.

The earlier integration report measured cold 43.38 s and warm median 16.45 s (6.24-18.02 s). This task establishes a fresh paired baseline below, rather than combining independent timing distributions. Model residency, machine load and tracing overhead prevent treating these local samples as a production SLA or attributing every millisecond of generation improvement solely to transport.

## Before/after stage breakdown

All values are milliseconds. Warm median/p90/max are per-stage distributions, so their columns need not sum to total distributions.

| Stage | Before cold | After cold | Before warm median | After warm median | Before p90 | After p90 | Before max | After max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Adapter initialization | 181.462 | 937.591 | 0.007 | 0.005 | 0.009 | 0.006 | 0.009 | 0.007 |
| Snapshot/corpus loading | 25683.480 | 2058.898 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Query embedding | 6981.719 | 35.658 | 2049.488 | 15.864 | 2056.025 | 17.349 | 2072.500 | 17.445 |
| Lexical analysis/retrieval | 190.022 | 271.641 | 290.721 | 285.362 | 298.634 | 304.654 | 301.643 | 327.058 |
| Dense Qdrant + metadata | 4092.887 | 59.323 | 4133.560 | 56.841 | 4146.068 | 68.320 | 4182.525 | 76.550 |
| Candidate union/reranking | 40.287 | 38.302 | 35.769 | 34.652 | 42.349 | 37.102 | 43.243 | 37.991 |
| Verified parents/context | 15.571 | 21.310 | 19.222 | 18.144 | 40.438 | 35.676 | 59.996 | 36.454 |
| Qwen generation | 8621.776 | 1778.836 | 4163.544 | 1703.427 | 4466.118 | 1857.374 | 5078.725 | 2488.214 |
| Claim validation | 6.027 | 6.526 | 1.435 | 1.532 | 2.450 | 2.079 | 4.394 | 2.727 |
| Public provenance mapping | 0.040 | 0.036 | 0.035 | 0.044 | 0.057 | 0.074 | 0.120 | 0.131 |
| Other mapping/telemetry | 3.742 | 5.342 | 1.896 | 1.747 | 2.230 | 2.104 | 2.553 | 2.604 |
| Total | 45817.014 | 5213.463 | 10443.305 | 2113.183 | 10975.183 | 2269.024 | 11639.878 | 2949.505 |

## Runtime without detailed profiling

A second fixed replay retained existing application telemetry but removed the external detailed profiler. It again passed every exact answer, citation and selected-source assertion, with unchanged data digests. These measurements quantify tracing overhead rather than replacing the paired comparison above.

| Stage | Cold seconds | Warm median seconds | Warm p90 seconds | Warm max seconds |
|---|---:|---:|---:|---:|
| Retrieval, including snapshot on cold call | 1.052 | 0.201 | 0.213 | 0.229 |
| Qwen generation | 1.756 | 1.692 | 1.827 | 2.430 |
| Validation | 0.0045 | 0.0004 | 0.0007 | 0.0019 |
| Total | 3.634 | 1.894 | 2.060 | 2.631 |

Qwen now dominates warm request time: median generation is 1.69 s versus median retrieval of 0.20 s. Its measured method duration includes client construction, transport, model execution and response parsing; it is not a claim of isolated inference time. The detailed profiler particularly inflates CPU-bound lexical/index construction work. No model, prompt or generation setting was changed to reduce these numbers.

## Ten-query exact shadow replay

The original `rag_v2_endpoint_shadow.json` is unchanged. Before and after runs compare against it; the optimized run also compares against the freshly measured baseline. No labels or retrieval/model settings were tuned.

| Query | Before warm seconds | After warm seconds | Decision | Exact replay |
|---|---:|---:|---|---|
| S01 | 10.321 | 2.127 | answered | passed |
| S02 | 10.937 | 2.187 | answered | passed |
| S03 | 11.640 | 2.950 | answered | passed |
| S04 | 10.879 | 2.147 | answered | passed |
| S05 | 10.566 | 1.925 | answered | passed |
| S06 | 10.975 | 2.269 | answered | passed |
| S07 | 6.590 | 0.436 | insufficient | passed |
| S08 | 8.887 | 2.099 | insufficient | passed |
| S09 | 9.713 | 0.893 | insufficient | passed |
| S10 | 9.694 | 0.919 | insufficient | passed |

## Implementation and lifecycle

`rag_v2_endpoint._create_service` now constructs endpoint-owned Qdrant and existing embedding clients using IPv4 for plain HTTP localhost. The same transport address is supplied to the unchanged GroundedQwenProvider. Local application settings are not mutated. Remote hosts, HTTPS (including certificate host names), URLs containing credentials and localhost names resolving outside loopback are preserved. DNS failure also preserves the original URL. Ports, URL paths and query strings remain intact. This optimization assumes the configured localhost HTTP services are the validated local services; it does not reroute remote deployments.

`RuntimeRetrievalV2` subclasses the existing retriever without replacing query analysis, lexical/dense scoring, candidate counts, sorting, context selection or parent expansion. A per-instance reentrant lifecycle lock serializes initial snapshot/provider creation and explicit refresh. Warm embedding/search/generation run outside that lock; four concurrent requests reach dense search together in the regression test. The original adapter factory remains guarded by its own lock.

The existing lexical index remains instance-local and identified by its full payload digest and fixed collection/client binding. Replacing the client invalidates the snapshot and rebinds dense reads. Refresh builds a fully validated snapshot and publishes it only after success; a failed refresh leaves no reusable old snapshot. A dense payload/snapshot mismatch still fails the request through the existing consistency guard, evicts that exact stale snapshot and requires the next request to reload. There is no automatic retry or fallback inside the failed request. Returned objects remain detached from the shared snapshot.

The collection is still treated as the validated immutable corpus. No full corpus scroll is introduced on every warm request: an out-of-band payload edit absent from all returned dense candidates is not proactively detected, as in the existing retriever. Explicit refresh is required for an intentional corpus update. Observed digest/payload mismatch never returns stale evidence. Source/checkpoint/implementation hashes and child/parent comparisons remain checked on every parent resolution, including when the lexical snapshot is warm. No cached parent evidence can bypass them.

Qwen uses the same model, system/user prompts, JSON format, timeout, context/token limits, temperature and seed. Its unchanged method still creates its own client for generation; removing the large loopback fallback was sufficient without rewriting generation or validation. No answer/result cache or alternate evidence source was introduced.

## Verification and integrity

The final broad relevant selection passed **493 tests**, with 1,847 pre-existing deprecation warnings, in 9.40 s. It covers legacy chat/service behavior, endpoint integration, the new runtime tests, hierarchical RAG/validation, both retrieval paths, embeddings/vectorstore, hierarchical indexing/pipeline/chunkers and existing RAG/LLM tests. The focused initial runtime/integration run passed 36 tests before two additional transport/parent checks were added.

New tests exercise exact full retrieval response equivalence, original child text/metadata, unchanged candidate counts and thresholds, no result cache, concurrent cold initialization and parallel warm searches, lazy embedding initialization, client identity invalidation, changed payload/digest fail-closed eviction, failed refresh, explicit refresh and detached results, invalid requests without initialization, one adapter factory initialization, default-off flag, URL preservation/DNS safeguards and per-request parent revalidation. Existing endpoint tests retain unsupported-support rejection, malformed output/unavailable providers, safe abstention, provenance privacy, authentication/history and schema compatibility.

The live replay validates exact accepted extracts already supported by the unchanged validator and baseline; no newly unsupported claim was returned. All 273 protected source, extraction, indexing and checkpoint hashes match the original endpoint shadow artifact. The runtime hashes are captured and checked during the optimized benchmark. Collection payload/vector digests before/after match:

| Collection | Points | SHA-256 (ID/payload/vector canonicalization) |
|---|---:|---|
| `buildlearn_products` | 624 | `266b67d281d741c2d8b98b027b7bffffa9662a9e6942a2a8aa7606066c36e754` |
| `buildlearn_products_hierarchical_v1` | 2637 | `f0634b2003aa9d7d24b88233149943d3670a2be8bb06e2b690c8e3cc211b533f` |

Only read-only Qdrant metadata/scroll/query operations were used. No collection, payload, vector, extraction, indexing or checkpoint write was invoked. The existing shadow artifact and validated reports/fixtures were not altered. No feature flag was enabled.

## Files and reproduction

Changed: `backend/app/ai/api/rag_v2_endpoint.py`. Added: `backend/app/ai/api/rag_v2_runtime.py`, `backend/tests/test_rag_v2_runtime.py`, `backend/scripts/profile_rag_v2_chat.py`, this report, and the before/after/unprofiled JSON measurement artifacts in this directory. No public API schema or legacy route was modified.

From `backend`, with the existing environment and running local Qdrant/Ollama services:

```powershell
.\venv\Scripts\python.exe -B scripts/profile_rag_v2_chat.py --output ..\docs\ai\rag_v2_performance_after.json --compare ..\docs\ai\rag_v2_performance_before.json
.\venv\Scripts\python.exe -B scripts/profile_rag_v2_chat.py --no-profile --output ..\docs\ai\rag_v2_performance_unprofiled.json --compare ..\docs\ai\rag_v2_performance_before.json
```

These commands are explicit local validation, never user-visible shadow traffic. Preserve measured artifacts before rerunning. The before artifact captures the original factory; reproducing it requires that pre-optimization factory, not merely changing the output filename. The harness refuses enabled flags and fails on any answer/citation/source drift or collection/protected-file mutation.

## Remaining limits

The full AI directory previously had unrelated collection/import failures (missing fitz and removed BaseChunker imports); this task did not change those dependencies or production chunking. The broad relevant passing selection is not a claim that those unrelated failures disappeared. Existing RAG evidence/abstention limitations remain documented in RAG_V2_EVALUATION.md. Default-off endpoint behavior and public schemas are unchanged. Per-worker processes own independent clients/snapshots; no distributed cache was added. Cold-start benchmark excludes HTTP authentication/database latency and does not characterize Ollama model cold loading or production concurrent generation throughput.
