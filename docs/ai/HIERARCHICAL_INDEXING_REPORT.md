# Hierarchical indexing report

## Verified outcome

**Full indexing completed and independently verified on 2026-09-26.** All 221 documents and 2,637 unique ChildChunks are checkpointed. Qdrant contains exactly 2,637 points in **`buildlearn_products_hierarchical_v1`**, using unnamed 768-dimensional COSINE vectors. Every payload and vector was read back and validated. Zero duplicate ChildChunk/point IDs, missing points, empty child texts, or unresolved failed chunks remain.

The existing production collection `buildlearn_products` received no write/delete/recreate requests from this work. All 624 production records, including payloads and vectors, match the read-only baseline taken before the full run. Record digest before/after: `f57760cc820397bc60062291054182dcd9598e049df2f05e0df226136c6cc89b`.

## Architecture and files

Complete extraction JSON -> existing `HierarchicalChunker.chunk_from_dict()` -> original ChildChunks -> existing `EmbeddingService.embed_chunks()` -> `QdrantVectorStore.upsert_child_chunks()` -> hierarchical collection. Retrieval and RAG were not implemented.

Added:

- `backend/app/ai/indexing/hierarchical_pipeline.py`: incremental workflow, dataset audit, collection checks, batches, checkpoint/resume, retries, readback validation, CLI.
- `backend/run_hierarchical_indexing.py`: executable wrapper with task-specific Ollama/nomic-embed-text and IPv4 loopback defaults. Explicit process environment takes precedence; `.env` is not loaded or changed.
- `backend/scripts/validate_hierarchical_indexing.py`: read-only verification of the checkpointed dataset and production content against the captured baseline.
- `backend/tests/ai/test_hierarchical_pipeline.py`: 43 mocked tests independent of live Ollama/Qdrant.
- `docs/ai/HIERARCHICAL_INDEXING_REPORT.md`: this report.

Modified:

- `backend/app/ai/vectorstore/qdrant_provider.py`: a hierarchical-only point-ID helper and its use in `upsert_child_chunks()`, required by a real uint64 overflow. Legacy `_get_chunk_id()`, `upsert_chunks()`, and both payload builders remain unchanged.

The existing chunk-only indexer/tests are retained. Extraction outputs/backends, parser heuristics, chunking logic, embedding providers/model/normalization, legacy payload behavior, retrieval, and RAG were not modified. Runtime evidence lives under `backend/ai_data/indexing/`.

## Dataset and chunk statistics

Sorted discovery found 221 extraction documents, excluding `manifest.json` (222 JSON files including the manifest). Every document has `extraction_status=success`. The complete dictionary is passed to the existing chunker. Documents are loaded individually; batches of vectors are retained only for the current document. The audit retains hashes and IDs rather than all document texts or embeddings.

Verified: **1,115 parents, 2,637 children, zero duplicate child IDs, zero duplicate mapped point IDs, zero empty children, zero dangling non-null parent references**. Dataset identity: `dd2f0aa67f24fcc769a9c8cb6ed35f01d9842c1a1006d54b629dc4462a71004c`.

There are **239 existing root children with `parent_id=None`**. These are preserved. The prior audit checked only non-null references; the stronger assertion that every child has a parent does not hold for this validated chunker. Section paths, source information, page ranges, text, and IDs remain unchanged. The baseline of 2,637 is an optional dataset-version validation argument, not a permanent invariant.

## Embedding and Qdrant configuration

Ollama, `nomic-embed-text`, L2 normalization enabled, dimension 768. Indexer embedding batch size 10; service/provider architecture is unchanged. Each result must match the exact input count, chunk IDs, and order; have 768 finite values; and have L2 norm within `1e-5` of 1. Exactly **2,637 unique children have validated stored embeddings**. This counts unique successful children, not every provider invocation across retries and interrupted runs.

Qdrant target: **`buildlearn_products_hierarchical_v1`**, COSINE, 768 dimensions, upsert batch size 10, three attempts, linear retry delays of 1 and 2 seconds. Missing collections are created. Existing collections are checked without deletion/recreation. Named vectors and incompatible dimensions/distances are rejected. An explicit guard rejects stores configured for any other collection.

The successful completion used `http://127.0.0.1:6333` and Ollama at `http://127.0.0.1:11434`. On this Windows host, three read-only Qdrant requests measured 6.126 seconds via `localhost` and 0.025 seconds via IPv4 loopback. The wrapper defaults avoid that connection delay. Checkpoint identity canonicalizes `localhost` and `127.0.0.1` as equivalent; other endpoints remain distinct and are rejected on resume if changed.

Payload remains exactly ten fields: `chunk_id`, `document_id`, `source_path`, `file_name`, `parent_id`, `section_path`, `page_start`, `page_end`, `block_type`, `text`. Readback checks exact equality with the source ChildChunk and finite normalized 768-dimensional vectors. Checkpoint success is recorded only after acknowledged upsert and successful readback.

## Required point-ID compatibility fix

The first full attempt stopped at a concrete incompatibility that the earlier 50-point validation did not cover. The existing chunker emits collision-suffixed IDs such as `ce32a740ed68a87c_1`. Python accepts underscores in `int(chunk_id, 16)`, yielding `237729952287223875521` (68 bits), beyond Qdrant's unsigned 64-bit limit. Qdrant returned HTTP 400; the failed ten-point batch was not checkpointed.

The dataset has **21 such overflow IDs** across four documents: `duraline-brochure_987c7dbb7b2c.json` (7), `fireline-brochure_81e3b6597899.json` (9), `Pro 2000_Compressed_9f40c1b536de.json` (2), and `Pro 3000_Compressed_be5e239f4859.json` (3).

The hierarchical helper retains the exact existing integer point ID whenever it fits uint64. Only overflow cases use UUID5 with `NAMESPACE_URL` and the full original ID prefixed by `buildlearn:hierarchical:child:`. The original ChildChunk ID remains unchanged in the payload. No truncation, modulo operation, deduplication, payload schema change, or legacy mapping change was made. All mapped IDs are audited for collisions. Exact overflow IDs, old integer values, and replacement UUIDs are recorded in `dataset_audit.json`. All 21 UUID points were verified live.

## Checkpoint and retry design

Checkpoint: `backend/ai_data/indexing/hierarchical_index_checkpoint.json`. It has a SHA-256 checked envelope; dataset inventory with file hashes, source document IDs and ordered chunk IDs; dataset/configuration identity; successful chunk IDs; completed document filenames; timestamps; statistics; failure events; and the last verified run report. Completed document IDs resolve through the stored inventory without assuming source document IDs are globally unique.

Identity includes model, normalization, collection, dimensions, distance, endpoint URLs, batch/retry configuration, chunk configuration, chunking/embedding source hashes, and point-ID mapping version. Corruption, inconsistent success inventories, or incompatible configuration changes fail safely. The pre-UUID checkpoint was upgraded only after proving all saved point IDs retained their existing uint64 mapping and all other identity fields matched. No existing points required migration.

Writes use a same-directory temporary file, flush, `fsync`, and `os.replace`. Windows can briefly deny replacement when another reader or antivirus holds the destination; replacement of the same durable temporary file has five bounded attempts with delays of 0.05, 0.10, 0.15, and 0.20 seconds. Exhaustion raises and preserves the previous checkpoint. An OS lock prevents concurrent writers using the same checkpoint and releases on process death; the lock file is retained.

Successfully checkpointed points are regenerated and read back before being skipped. Missing/changed points fail instead of silently reporting success. A crash between remote acknowledgement and checkpoint replacement can replay a batch safely because IDs are deterministic. Exhausted embedding/upsert failures are recorded with document, batch IDs, stage, error, timestamp, and available run counters; policy is fail-fast, then explicit resume. Historical errors are retained after recovery.

`--reset-checkpoint` intentionally starts a fresh checkpoint without deleting any points or collection. It is mutually exclusive with `--resume`. An existing checkpoint requires an explicit resume/reset choice. Full-run count mismatches are reported without deleting unexpected points. No Qdrant cleanup operations were attempted; the known Windows collection-delete issue is separate and was not bypassed.

## Executed validation and tests

- Initial focused selection: **130 passed**.
- Expanded existing selection including the technical chunker: **141 passed**.
- Final focused selection plus 43 new tests: **184 passed** (`focused_test_results.txt`).
- Broader `tests/ai` execution before the later compatibility tests: **491 passed, one failed, six collection errors**. Five errors are missing PyMuPDF (`fitz`); the sixth is existing `test_chunking.py` importing absent `BaseChunker`. The failing scraper needed external network access; its isolated outside-sandbox rerun passed (1 passed). The broader suite is not claimed fully green. Protected extraction/chunking components were not changed to repair these unrelated issues.
- Existing `datetime.utcnow()` and pytest fixture deprecation warnings remain. The initial default Windows pytest temporary directory denied access, so verification used fresh workspace temporary directories. New unit tests require neither live Ollama nor live Qdrant.

Coverage includes discovery/manifest exclusion, complete loading/chunking integration, embedding/upsert batches, ordering/IDs/counts, finite normalized vectors, payload mapping/readback, collection creation/configuration, production isolation, retries, atomic checkpoint failure/retry, concurrent writers, checksum/semantic corruption, partial-document resume, lost upsert responses, missing remote points, final counts, numeric collisions, UUID overflow mapping, guarded checkpoint upgrades, and equivalent/distinct endpoint identities.

## Dry run, full run, and resume results

The initial Qdrant connection failed inside and outside the sandbox (Windows 10061). The repository-documented Qdrant 1.19.0 executable was started in the background from the documented repository working directory and existing storage. No storage repair or collection recreation occurred. The server is left running.

**Dry run:** 3 documents, 105 embeddings, 105 upserts, exact collection count 105, ten-field payload/vector checks passed, zero failed batches; elapsed 83.1 seconds. Evidence: `dry_run.json`.

**Full run:** after recovery/resume, 221 documents completed, 2,637 unique chunks and vectors indexed, exact point count 2,637, all payload/vector checks passed, zero unresolved failed chunks. The final completion invocation added 1,180 points to 1,457 retained checkpointed points and took 29.79 seconds; this is the final invocation duration, not the elapsed time of all earlier attempts. Evidence: `full_run.json` and `full_run_progress.txt`.

Two historical failure events remain: the original overflow upsert and one Windows checkpoint replacement failure. Both were resolved, and their successful subsets were retained. An additional performance restart switched equivalent loopback addresses without changing embeddings or point IDs.

**Independent final live validation:** every one of the 2,637 payloads/vectors verified, 221 completed document entries, zero remaining children, 21 valid UUID overflow points, unchanged 624 production records. Evidence: `final_validation.json`.

**Completed-dataset resume:** all 221 documents verified; **zero embeddings and zero upserts**, exact point count 2,637; elapsed 9.67 seconds. Evidence: `resume_validation.json` and `resume_progress.txt`. Checkpoint creation, resume, corruption, atomic replacement, and partial-document recovery passed unit/live checks as applicable.

## Commands and limitations

Run from `formation-platform/backend`:

```powershell
.\venv\Scripts\python.exe run_hierarchical_indexing.py --audit-only --expected-documents 221 --expected-children 2637 --report ai_data/indexing/dataset_audit.json
.\venv\Scripts\python.exe run_hierarchical_indexing.py --limit-documents 3 --resume --expected-documents 221 --expected-children 2637
.\venv\Scripts\python.exe run_hierarchical_indexing.py --resume --expected-documents 221 --expected-children 2637 --report ai_data/indexing/full_run.json
.\venv\Scripts\python.exe scripts/validate_hierarchical_indexing.py
```

For a deliberately fresh checkpoint, use `--reset-checkpoint`; it re-embeds existing deterministic points and never deletes collections. Batch sizes, upsert attempts and retry delay are configurable CLI flags. The read-only verifier is scoped to this validated dataset and requires the captured production baseline.

The local lock coordinates one checkpoint, not arbitrary external writers or separate checkpoints targeting the same collection. Atomic local replacement and remote writes are not one distributed transaction; deterministic replay handles acknowledgement gaps. Existing unrelated collection points cause a full-count discrepancy and are not removed automatically. Configuration/source hashing does not detect a different remote model installed under the same model tag. Parent existence is verified for non-null references; the 239 preserved root children have no parent by the validated chunker's design. The broader legacy suite still has the six unrelated collection errors described above.
