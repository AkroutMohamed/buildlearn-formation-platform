# Retrieval-v2 diagnostic

Run UTC: 2026-09-26T11:42:31.501013+00:00

## Scope and method

All 34 original frozen queries and labels are unchanged. The collection has 2637 child points, 221 source identities. Collection payload/vector SHA-256 before/after: `61e6cd658f7edde04d3bb7312b2cc01a1535ace38f23baea277ecab679748eb4` (identical). Protected extraction, chunking, embedding, indexing, vectorstore, RAG, retrieval, AI configuration, checkpoint, frozen evaluation harness and student-router hashes are unchanged. `buildlearn_products` was not accessed; hierarchical collection operations were read-only. No collection writes or LLM calls occurred. Qdrant server access logs are outside the integrity scope.

Existing HierarchicalRetriever and EmbeddingService/nomic-embed-text execute four independent dense searches per query: K=10/20/50/100, COSINE, threshold 0.0. Query embeddings are cached in memory across K. Child-only evidence metrics use the original frozen exact IDs/substring rules and exact source identity. MRR is truncated at each reported K. Rank null means outside the specified candidate pool, never proof of absence from the whole collection. Every expected evidence unit is present and validated in the indexed collection.

## Phase 1: dense candidate recall

| Experiment | K | Hit@K | Evidence recall | Document recall | MRR@K |
|---|---:|---:|---:|---:|---:|
| dense-only | 10 | 0.2941 | 0.2794 | 0.5588 | 0.1912 |
| dense-only | 20 | 0.5000 | 0.4853 | 0.6471 | 0.2061 |
| dense-only | 50 | 0.5882 | 0.5735 | 0.7647 | 0.2085 |
| dense-only | 100 | 0.6765 | 0.6618 | 0.8235 | 0.2098 |

Baseline top-10 failures: A=11 (no evidence in top 100); B=13 (evidence ranked 11–100); C=9 (expected document in top 10 but evidence missed). A/B are mutually exclusive; C can overlap either. Multi-unit queries can still lack other required facts even when one correct evidence unit is found.

Dense top-50 candidate evidence ceiling: **57.35%**. Reranking cannot exceed this ceiling without adding candidates. Dense top-100 evidence recall is **66.18%**.

## Phase 2: identifiers

Generic conservative rule derived from filename code shapes: token boundaries, 2–8 letters then a digit-led 3–12-character alphanumeric suffix containing at least three digits, case insensitive; accept only references observed in URL-decoded corpus filenames. This covers numeric and mixed letter/digit suffixes without guessing unknown codes. There are 157 recognized corpus references, 17 identifier queries. No evaluation identifier is hardcoded in the detector. Pure numbers, standard tokens absent from reference filenames, short platform names and free-form product names are not routed by this rule. All-letter names require separate metadata matching.

Exact identifier filtering identifies the expected source unambiguously for **17/17** detected-identifier queries. This is source routing accuracy, not evidence accuracy. Source identity includes source_path to disambiguate duplicate document IDs. Query identifiers are intersected; ambiguous/empty intersections fall back to dense retrieval.

| Experiment | K | Hit@K | Evidence recall | Document recall | MRR@K |
|---|---:|---:|---:|---:|---:|
| dense identifier subset | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| dense identifier subset | 3 | 0.1765 | 0.1765 | 0.2353 | 0.0784 |
| dense identifier subset | 5 | 0.1765 | 0.1765 | 0.2353 | 0.0784 |
| dense identifier subset | 10 | 0.1765 | 0.1765 | 0.2941 | 0.0784 |
| Experiment | K | Hit@K | Evidence recall | Document recall | MRR@K |
|---|---:|---:|---:|---:|---:|
| exact route + lexical identifier subset | 1 | 0.8824 | 0.8824 | 1.0000 | 0.8824 |
| exact route + lexical identifier subset | 3 | 1.0000 | 1.0000 | 1.0000 | 0.9412 |
| exact route + lexical identifier subset | 5 | 1.0000 | 1.0000 | 1.0000 | 0.9412 |
| exact route + lexical identifier subset | 10 | 1.0000 | 1.0000 | 1.0000 | 0.9412 |
| lexical identifier subset | 1 | 0.8824 | 0.8824 | 1.0000 | 0.8824 |
| lexical identifier subset | 3 | 1.0000 | 1.0000 | 1.0000 | 0.9412 |
| lexical identifier subset | 5 | 1.0000 | 1.0000 | 1.0000 | 0.9412 |
| lexical identifier subset | 10 | 1.0000 | 1.0000 | 1.0000 | 0.9412 |

For 17/17 identifier queries, none of the labeled evidence passages contains the requested code, although the filename does. Existing `EmbeddingService.embed_chunks` embeds only `chunk.text` (`app/ai/embeddings/service.py:68`); the provider passes that text unchanged (`ollama_provider.py:30`). Dense search therefore cannot directly use the exact reference stored only in payload metadata. This is a concrete representation gap, not proof that all semantic embedding quality is poor. Query and document text are passed without distinct task prefixes; no prefix/model ablation was performed, so the effect of that convention remains unmeasured.

Identifier validation is corpus-derived and evaluated over all labeled questions; full per-identifier matches and ranks appear below. This proves behavior on this corpus, not recall of every possible future identifier format.

## Phase 3: lexical signals

Normalization: URL decoding, Unicode NFKD, accent removal, casefolding, ligature expansion, set tokens. Reference tokens remain whole, and numeric/decimal tokens are retained. Minimal French stopwords are removed only from word overlap. Chunk tokens include original text plus filename; original text is never edited. No new dependency was installed; rank_bm25 is absent, so BM25 was not used.

Features are in [0,1]: identifier = any detected reference present in candidate text/filename; filename = fraction of query word tokens present in filename; lexical = IDF-weighted query-word overlap with chunk+filename, divided by all query-word IDF including unseen terms; numeric = fraction of exact numeric tokens present. IDF = log((N+1)/(df+1))+1 over all child records. Decimal comma/dot spellings remain distinct exact tokens. Offline lexical rank sums these four transparent features; it is a diagnostic fixed-weight reference, not a deployed score.

Full-corpus lexical top-100 evidence recall: **100.00%**. Full-corpus lexical and routing comparisons intentionally test candidate generation beyond the dense pool, entirely offline against the existing payload snapshot.

## Phase 4: deterministic reranking

Dense top-50 candidates only. Score = dense_score + wi*identifier + wf*filename + wl*IDF_overlap + wn*numeric. Grid: wi,wl in {0,.1,.25,.5,1}; wf in {0,.1,.25,.5}; wn in {0,.1,.25}. All 300 combinations, including the zero-bonus control, were evaluated. Select highest macro evidence recall@3, then MRR@3, then Hit@1; ties choose smallest sum of weights and lexicographic weights. Source/chunk identity breaks score ties. No label information enters scoring. Selection uses the same 34 labels, so gains are calibration-set gains and need held-out validation.

Selected weights (identifier, filename, word overlap, numbers): **(0, 0.5, 0.5, 0.25)**.

| Experiment | K | Hit@K | Evidence recall | Document recall | MRR@K |
|---|---:|---:|---:|---:|---:|
| dense-only | 1 | 0.1176 | 0.1029 | 0.1618 | 0.1176 |
| dense-only | 3 | 0.2941 | 0.2794 | 0.4265 | 0.1912 |
| dense-only | 5 | 0.2941 | 0.2794 | 0.4706 | 0.1912 |
| dense-only | 10 | 0.2941 | 0.2794 | 0.5588 | 0.1912 |
| dense-50 reranked | 1 | 0.4118 | 0.3971 | 0.5147 | 0.4118 |
| dense-50 reranked | 3 | 0.5588 | 0.5294 | 0.7353 | 0.4804 |
| dense-50 reranked | 5 | 0.5588 | 0.5441 | 0.7500 | 0.4804 |
| dense-50 reranked | 10 | 0.5882 | 0.5735 | 0.7647 | 0.4846 |
| offline lexical full corpus | 1 | 0.7059 | 0.6765 | 0.7941 | 0.7059 |
| offline lexical full corpus | 3 | 0.8824 | 0.8529 | 0.9412 | 0.7892 |
| offline lexical full corpus | 5 | 0.9706 | 0.9559 | 0.9853 | 0.8083 |
| offline lexical full corpus | 10 | 0.9706 | 0.9559 | 0.9853 | 0.8083 |
| unique identifier route + lexical, dense fallback | 1 | 0.5588 | 0.5441 | 0.6618 | 0.5588 |
| unique identifier route + lexical, dense fallback | 3 | 0.7059 | 0.6912 | 0.8088 | 0.6225 |
| unique identifier route + lexical, dense fallback | 5 | 0.7059 | 0.6912 | 0.8824 | 0.6225 |
| unique identifier route + lexical, dense fallback | 10 | 0.7059 | 0.6912 | 0.9412 | 0.6225 |
| dense-100 + lexical-50 RRF | 1 | 0.2941 | 0.2794 | 0.4265 | 0.2941 |
| dense-100 + lexical-50 RRF | 3 | 0.3235 | 0.3088 | 0.6176 | 0.3088 |
| dense-100 + lexical-50 RRF | 5 | 0.5882 | 0.5588 | 0.7500 | 0.3691 |
| dense-100 + lexical-50 RRF | 10 | 0.8529 | 0.8382 | 0.8971 | 0.4051 |

### Transparent single-signal controls

Each control adds one signal with unit weight to dense score on the same top-50 candidates. These controls explain signal effects and do not replace the grid-selected weights. Identifier and filename/word features are correlated because filenames contain references; a zero selected standalone identifier coefficient does not demonstrate that identifiers are unhelpful.

| Experiment | K | Hit@K | Evidence recall | Document recall | MRR@K |
|---|---:|---:|---:|---:|---:|
| identifier only bonus | 1 | 0.2353 | 0.2206 | 0.3971 | 0.2353 |
| identifier only bonus | 3 | 0.3824 | 0.3676 | 0.5441 | 0.2941 |
| identifier only bonus | 5 | 0.4118 | 0.3971 | 0.6471 | 0.3015 |
| identifier only bonus | 10 | 0.4118 | 0.3971 | 0.7059 | 0.3015 |
| filename only bonus | 1 | 0.2647 | 0.2500 | 0.5147 | 0.2647 |
| filename only bonus | 3 | 0.4118 | 0.3971 | 0.6618 | 0.3284 |
| filename only bonus | 5 | 0.4706 | 0.4559 | 0.6765 | 0.3417 |
| filename only bonus | 10 | 0.5000 | 0.4853 | 0.7353 | 0.3466 |
| word overlap only bonus | 1 | 0.3824 | 0.3676 | 0.4853 | 0.3824 |
| word overlap only bonus | 3 | 0.5588 | 0.5294 | 0.6765 | 0.4608 |
| word overlap only bonus | 5 | 0.5588 | 0.5441 | 0.7206 | 0.4608 |
| word overlap only bonus | 10 | 0.5588 | 0.5441 | 0.7353 | 0.4608 |
| numeric only bonus | 1 | 0.1176 | 0.1029 | 0.1912 | 0.1176 |
| numeric only bonus | 3 | 0.2941 | 0.2794 | 0.4559 | 0.1961 |
| numeric only bonus | 5 | 0.2941 | 0.2794 | 0.5294 | 0.1961 |
| numeric only bonus | 10 | 0.2941 | 0.2794 | 0.6176 | 0.1961 |

Dense-only K=1/3/5/10 uses prefixes of the independently retrieved top-10 pool, reproducing the original small-K baseline. Larger pools can change boundary tie ordering and document recall; those differences are not model improvements. Lexical-only source rows have placeholder score 0; reported ranking metrics do not use that placeholder. RRF uses equal reciprocal ranks 1/(60+rank), dense top-100 plus lexical top-50; c=60 was fixed as a transparent diagnostic, not tuned. Identifier-routing comparison lexically ranks children of a single matching source; ambiguous/missing identifiers use dense top-100. These two candidate-expansion experiments are diagnostic simulations, not implementation changes.

## Phase 5: architecture decision

Recommended next architecture: **C. True hybrid lexical + dense candidate generation**.

Measured evidence recall@3: dense 27.94%; dense-50 reranked 52.94%; unique-reference route 69.12%; lexical-only 85.29%; dense/lexical RRF 30.88%. 11 questions have evidence missing from dense top 100 but found by lexical top 50. Such misses cannot be repaired by dense-top-50 reranking alone.

Of those recoverable misses, 2 lack a route under the tested conservative detector (BL06, BL33). These include reference formats/product names outside that detector's scope. The tested option-B variant leaves candidate gaps; richer name/version-aware metadata routing was not evaluated and cannot be ruled out. C is justified by the measured lexical candidate gains, not proof that every possible metadata-only architecture must fail.

Next implementation should use exact-reference routing when the corpus metadata identifies one source, lexical candidates alongside dense candidates for other questions, and deterministic fusion/reranking with provenance preservation. The measured fusion is a reference, not proof that its fixed c=60 or learned-on-this-set bonuses are optimal. Keep source verification, child-text preservation and generation separation. Evaluate independent queries and ambiguous/negative cases before setting production weights or thresholds.

Equal-weight RRF should not be the next default based on these measurements: at K=3 it underperforms lexical-only and identifier routing substantially. The evidence favors a lexical-first/identifier-aware candidate layer with dense semantic candidates retained and reranking calibrated on independent questions. The current experiment does not establish optimal reranking weights for that expanded union.

D (embedding-model reconsideration) is not established: no alternative embedding model was tested. Dense misses and identifier sensitivity justify auditing query/document embedding conventions and evaluating alternative models on held-out data, but cannot establish that replacing the model is necessary. No embedding configuration, prefix or vector was changed in this experiment.

## Failure groups

Categories overlap and are conservative diagnostic signals, not proven causal assignments. Identifier failure means unambiguous correct reference routing but baseline dense evidence missed. Semantic embedding failure means dense top-10 evidence missed; lexical success strengthens evidence for a dense ranking/candidate problem without ruling out label incompleteness. This includes the two parser-flagged queries, so there are 24 dense misses rather than the prior report's 22 residual embedding/retrieval signals. Lexical mismatch means full-corpus lexical evidence rank >50. Source-document/evidence mismatch is recorded for baseline evidence failures when the correct document appears earlier within top 100 or its evidence is missing. C specifically uses the independently retrieved baseline top 10. Parser/OCR flags are the existing frozen source-damage signals, never changes to labels. Ambiguity flags come from the frozen question categories. Near-duplicate confusion requires word-token Jaccard >=.85 between labeled evidence and another-source baseline dense top-10 chunk; this ignores ordering and numbers remain tokens.

```json
{
  "identifier failure": 14,
  "semantic embedding failure": 24,
  "lexical mismatch": 0,
  "near-duplicate confusion": 3,
  "source-document found but evidence chunk missed": 13,
  "parser/OCR issue": 2,
  "ambiguous label": 5
}
```

## Verification

The frozen label digest is `3491d142f300521419074cec6bce2aa922855b375fb5dfc954ab47810e35f974`, matching the prior evaluation report. The final live run used 34 cached query embeddings and 136 independent dense retrieval calls. All 300 reranking weight combinations and single-signal controls were computed offline. The report was parsed and checked for all 34 unique query IDs, all four independently measured dense rank pairs per query, and lexical feature evidence for every expected unit.

Relevant existing retrieval/evaluation tests: **94 passed**, with 34 existing datetime deprecation warnings. Nine additional offline assertion groups passed for normalization, conservative corpus identifiers, source ambiguity, lexical features, evidence ranks, metrics, deterministic reranking, grid selection and frozen-label identity. No dependencies were installed. Only the standalone diagnostic script and this document were added; no validated production component was edited.

```powershell
.\venv\Scripts\python.exe -B -m pytest tests/ai/test_hierarchical_retrieval_eval.py tests/ai/test_hierarchical_retriever.py -q -p no:cacheprovider --basetemp C:\Users\user\Desktop\stage\.tmp\retrieval_v2_tests --tb=short
```

## All 34 query diagnostics

Ranks use dense top 100, full-corpus lexical ranking, and the selected dense-top-50 reranker respectively. Per-unit ranks expose partial multi-source misses; first ranks report any matching evidence. Lexical score and components are shown for every alternative labeled child. Null reranked position means the expected evidence was absent from dense top 50. Expected exact text/IDs are the original frozen labels.

```json
{
  "query_id": "BL01",
  "query": "Quel mortier colle convient aux grands formats sur des supports neufs et anciens ?",
  "categories": [
    "product identification",
    "vague/general"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-FLEX%20V4-afe87429",
        "file_name": "FLEX%20V4.pdf",
        "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
        "chunk_ids": [
          "6c394de6b51732a5"
        ],
        "substring": "MorƟer colle amélioré, déformable, résistant au glissement, à base de ciment avec un temps ouvert allongé desƟné à la pose de carreaux céramiques de grands formats en sols et murs intérieurs et extérieurs sur supports neufs et anciens."
      },
      "dense_document_rank": 4,
      "dense_chunk_rank": 11,
      "lexical_rank": 2,
      "reranked_position": 2,
      "lexical_features": [
        {
          "chunk_id": "6c394de6b51732a5",
          "identifier": 0.0,
          "filename": 0.0,
          "idf_overlap": 0.7530776090001219,
          "numeric": 0,
          "lexical_score": 0.7530776090001219
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 11,
  "first_correct_document_rank": 4,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 4,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 4
    },
    "20": {
      "first_evidence": 11,
      "first_document": 4
    },
    "50": {
      "first_evidence": 11,
      "first_document": 4
    },
    "100": {
      "first_evidence": 11,
      "first_document": 4
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 2,
  "reranked_first_evidence_position": 2,
  "diagnosis": [
    "B: correct evidence exists, below rank 10",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed",
    "ambiguous label",
    "near-duplicate confusion"
  ],
  "near_duplicate_sources": [
    [
      "full-FLEX%20PLUS%20V4-98e08a07",
      "FLEX%20PLUS%20V4.pdf",
      "ai_data\\raw\\sofap\\FLEX%20PLUS%20V4.pdf"
    ]
  ],
  "dense_top10": [
    {
      "file_name": "Pro 3000_Compressed.pdf",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "chunk_id": "7f6f38e289015721",
      "score": 0.7607002,
      "section_path": [],
      "block_type": "list_item"
    },
    {
      "file_name": "FINACEM BLEU_compressed.pdf",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "chunk_id": "80d6cf949e62c2cb",
      "score": 0.7579416,
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "chunk_id": "482181fd2a16eed3",
      "score": 0.7556249,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FLEX%20V4.pdf",
      "document_id": "full-FLEX%20V4-afe87429",
      "chunk_id": "7b920160bad39822",
      "score": 0.7525101,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "fiche%20Champion%204%20IN%201%20locale%201.pdf",
      "document_id": "full-fiche%20Champion%204%20IN%201%20locale%201-26006ee2",
      "chunk_id": "f7d7aed9d765d3a5",
      "score": 0.74809504,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "chunk_id": "a23fb71a6ff707c2",
      "score": 0.7468034,
      "section_path": [
        "FLEX PLUS"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "chunk_id": "f5bc6a620d7fbdcf",
      "score": 0.74250877,
      "section_path": [
        "• EN 16-566  - NFT 36-005 - DTU 59.1 - DTU 59.4"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "MARBRE%20V4.pdf",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "chunk_id": "4b1c90c0f116fda0",
      "score": 0.74227035,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "chunk_id": "9fc104a0b3b85789",
      "score": 0.741634,
      "section_path": [
        "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "chunk_id": "24e981c191415fd0",
      "score": 0.741634,
      "section_path": [
        "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
      ],
      "block_type": "list_item"
    }
  ]
}
```

```json
{
  "query_id": "BL02",
  "query": "Quelle est la tension de la batterie EBPK20021 et sa capacité ?",
  "categories": [
    "technical specifications"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EBPK20021%20Technical%20Data-e774e072",
        "file_name": "EBPK20021%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EBPK20021%20Technical%20Data.pdf",
        "chunk_ids": [
          "438169fa5ddf1d66"
        ],
        "substring": "Des cellules Li-Ion de haute qualité signifient aucun effet mémoire, une faible autodécharge et une puissance élevée et constante\nLe niveau de charge actuel est indiqué par un affichage LED à 3 niveaux\nBoîtier protégé contre la poussière, la corrosion et les dommages mécaniques Tension : 20 V Batterie lithium-ion 4,0 Ah\nVoyant LED de niveau de charge de la batterie Une seule batterie compatible avec tous les outils multiples P20S\nEmballé dans une boîte de couleur"
      },
      "dense_document_rank": 41,
      "dense_chunk_rank": 41,
      "lexical_rank": 1,
      "reranked_position": 2,
      "lexical_features": [
        {
          "chunk_id": "438169fa5ddf1d66",
          "identifier": 1.0,
          "filename": 0.2,
          "idf_overlap": 0.5754296013042163,
          "numeric": 0,
          "lexical_score": 1.7754296013042163
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 41,
  "first_correct_document_rank": 41,
  "identifier_detected": [
    "EBPK20021"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": 41,
      "first_document": 41
    },
    "100": {
      "first_evidence": 41,
      "first_document": 41
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "EBPK20021",
      "matches": [
        [
          "full-EBPK20021%20Technical%20Data-e774e072",
          "EBPK20021%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\EBPK20021%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 2,
  "diagnosis": [
    "B: correct evidence exists, below rank 10"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ELAP20151%20Technical%20Data.pdf",
      "document_id": "full-ELAP20151%20Technical%20Data-640eea36",
      "chunk_id": "19a9ef39a0cf9b7e",
      "score": 0.7871139,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ELBCPK2212%20Technical%20Data.pdf",
      "document_id": "full-ELBCPK2212%20Technical%20Data-9fbd74b3",
      "chunk_id": "854cec8546c7775d",
      "score": 0.7526158,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELSL203051%20Technical%20Data.pdf",
      "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
      "chunk_id": "f1837ea6d89afe65",
      "score": 0.7500777,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "chunk_id": "9e1c3c2d68230178",
      "score": 0.74851143,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EFCR20403%20Technical%20Data.pdf",
      "document_id": "full-EFCR20403%20Technical%20Data-22bae915",
      "chunk_id": "e2d717e72a39fd06",
      "score": 0.74220026,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ECIWL20455%20Technical%20Data.pdf",
      "document_id": "full-ECIWL20455%20Technical%20Data-791ec736",
      "chunk_id": "369529d501d6a52d",
      "score": 0.73966265,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ECIWL42461%20Technical%20Data.pdf",
      "document_id": "full-ECIWL42461%20Technical%20Data-a7e3fb17",
      "chunk_id": "184599223da34346",
      "score": 0.73465693,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ERHRP1801%20Technical%20Data.pdf",
      "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
      "chunk_id": "02dd0774ee118fee",
      "score": 0.7153337,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ELSL203051%20Technical%20Data.pdf",
      "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
      "chunk_id": "e5f78778d3c8ba00",
      "score": 0.71004766,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EDMR766001%20Technical%20Data.pdf",
      "document_id": "full-EDMR766001%20Technical%20Data-eeec9c03",
      "chunk_id": "09244a40949e66c2",
      "score": 0.7075522,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL03",
  "query": "À quoi sert le multimètre EDMR5110004 ?",
  "categories": [
    "application/use"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EDMR5110004%20Technical%20Data-0ce60f56",
        "file_name": "EDMR5110004%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EDMR5110004%20Technical%20Data.pdf",
        "chunk_ids": [
          "7446289f7f148334"
        ],
        "substring": "Utilisé pour les tests de circuits, le diagnostic des pannes, la mesure du courant, la détection de tension"
      },
      "dense_document_rank": null,
      "dense_chunk_rank": null,
      "lexical_rank": 2,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "7446289f7f148334",
          "identifier": 1.0,
          "filename": 0.3333333333333333,
          "idf_overlap": 0.28078537598935444,
          "numeric": 0,
          "lexical_score": 1.6141187093226876
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": null,
  "identifier_detected": [
    "EDMR5110004"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": null
    },
    "100": {
      "first_evidence": null,
      "first_document": null
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "EDMR5110004",
      "matches": [
        [
          "full-EDMR5110004%20Technical%20Data-0ce60f56",
          "EDMR5110004%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\EDMR5110004%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 2,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ENAL02271%20Technical%20Data.pdf",
      "document_id": "full-ENAL02271%20Technical%20Data-01ea6a48",
      "chunk_id": "993ba643ce5a6fe0",
      "score": 0.6941048,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EFC1352%20Technical%20Data.pdf",
      "document_id": "full-EFC1352%20Technical%20Data-962bf90b",
      "chunk_id": "3f24b579c6bd1fb5",
      "score": 0.6857588,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ENAL02271%20Technical%20Data.pdf",
      "document_id": "full-ENAL02271%20Technical%20Data-01ea6a48",
      "chunk_id": "d8ba72c03f7231e5",
      "score": 0.6818044,
      "section_path": [
        "ELCNLI9008, ELCNLI420602,\nELCNLI420602-4, ULCNLI9008,\nULCNLI420602"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "34795058e455162f",
      "score": 0.6783918,
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "chunk_id": "6a4ac21556997e08",
      "score": 0.6741837,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "chunk_id": "8e06b5a58c58ce48",
      "score": 0.6741837,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "chunk_id": "af07874b63ed5141",
      "score": 0.6741837,
      "section_path": [
        "MURENDUITCACHET BLEU"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "chunk_id": "1427ea575d844c48",
      "score": 0.6741837,
      "section_path": [
        "MURENDUITCACHET VERT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "fiche%20Champion%204%20IN%201%20locale%201.pdf",
      "document_id": "full-fiche%20Champion%204%20IN%201%20locale%201-26006ee2",
      "chunk_id": "474b1b019571198b",
      "score": 0.6741837,
      "section_path": [
        "CHAMPION 4 IN 1"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "hydromur%20R%20V4.pdf",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "chunk_id": "582d4be13bb883e8",
      "score": 0.6741837,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL04",
  "query": "Quelle est la consommation de HYDRO REP surfaçage par millimètre ?",
  "categories": [
    "consumption"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "chunk_ids": [
          "0edc15932b396769"
        ],
        "substring": "La consommation de l’HYDRO REP surfaçage varie selon le support (type, planéité, rugosité) env.1.15 kg / m?/mm."
      },
      "dense_document_rank": 1,
      "dense_chunk_rank": 1,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "0edc15932b396769",
          "identifier": 0.0,
          "filename": 0.6,
          "idf_overlap": 0.6981879709481728,
          "numeric": 0,
          "lexical_score": 1.2981879709481727
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 1,
  "first_correct_document_rank": 1,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 1,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 1,
      "first_document": 1
    },
    "20": {
      "first_evidence": 1,
      "first_document": 1
    },
    "50": {
      "first_evidence": 1,
      "first_document": 1
    },
    "100": {
      "first_evidence": 1,
      "first_document": 1
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "0edc15932b396769",
      "score": 0.8335085,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "d84c18a2bbfb26d5",
      "score": 0.79961324,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "5fcda73e77764500",
      "score": 0.7894975,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "2568dbcc81a0785f",
      "score": 0.7849463,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "db288555be8d569a",
      "score": 0.76701224,
      "section_path": [
        "DESCRIPTION PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "971e1b6068337e7f",
      "score": 0.7296021,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPERLITE1.pdf",
      "document_id": "full-SUPERLITE1-8227dad4",
      "chunk_id": "dd186286f02d463e",
      "score": 0.72879523,
      "section_path": [
        "SUPERLITE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPERLITE1.pdf",
      "document_id": "full-SUPERLITE1-8227dad4",
      "chunk_id": "8611aedfa0c5d261",
      "score": 0.71088207,
      "section_path": [],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "773d8cea09acd46b",
      "score": 0.6990737,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "MARBRE%20V4.pdf",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "chunk_id": "26ca29e335f59e35",
      "score": 0.6947934,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    }
  ]
}
```

```json
{
  "query_id": "BL05",
  "query": "Quelles sont les dimensions de la boîte à outils EMTB1322 ?",
  "categories": [
    "dimensions",
    "highly specific"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EMTB1322%20Technical%20Data-c1a8f553",
        "file_name": "EMTB1322%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EMTB1322%20Technical%20Data.pdf",
        "chunk_ids": [
          "05647b178a6474f2"
        ],
        "substring": "Dimensions : 345 mm * 280 mm * 110 mm Poignée large intégrée pour un transport facile et stable Compartiments à gobelets amovibles en 3 tailles différentes Avec 12 gobelets amovibles"
      },
      "dense_document_rank": 54,
      "dense_chunk_rank": 54,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "05647b178a6474f2",
          "identifier": 1.0,
          "filename": 0.25,
          "idf_overlap": 0.560510051950292,
          "numeric": 0,
          "lexical_score": 1.810510051950292
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 54,
  "first_correct_document_rank": 54,
  "identifier_detected": [
    "EMTB1322"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": null
    },
    "100": {
      "first_evidence": 54,
      "first_document": 54
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "EMTB1322",
      "matches": [
        [
          "full-EMTB1322%20Technical%20Data-c1a8f553",
          "EMTB1322%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\EMTB1322%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "B: correct evidence exists, below rank 10"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ENAL02271%20Technical%20Data.pdf",
      "document_id": "full-ENAL02271%20Technical%20Data-01ea6a48",
      "chunk_id": "d8ba72c03f7231e5",
      "score": 0.72950643,
      "section_path": [
        "ELCNLI9008, ELCNLI420602,\nELCNLI420602-4, ULCNLI9008,\nULCNLI420602"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMASC1251%20Technical%20Data.pdf",
      "document_id": "full-EMASC1251%20Technical%20Data-a4e9e6f5",
      "chunk_id": "4cc0049b007d4aec",
      "score": 0.7258905,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "caption"
    },
    {
      "file_name": "EASGW10011%20Technical%20Data.pdf",
      "document_id": "full-EASGW10011%20Technical%20Data-4053d736",
      "chunk_id": "6a751886e1fa5a30",
      "score": 0.71407247,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EHCS083502%20Technical%20Data.pdf",
      "document_id": "full-EHCS083502%20Technical%20Data-b719f5ea",
      "chunk_id": "e7819edfc3b4be53",
      "score": 0.70376885,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ECHS072822%20Technical%20Data.pdf",
      "document_id": "full-ECHS072822%20Technical%20Data-f7efae7f",
      "chunk_id": "eec9ae746d8aa904",
      "score": 0.7021761,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ETCS0402%20Technical%20Data.pdf",
      "document_id": "full-ETCS0402%20Technical%20Data-a72c933b",
      "chunk_id": "4b3eb9c29133ad5a",
      "score": 0.7019967,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ECUT451%20Technical%20Data.pdf",
      "document_id": "full-ECUT451%20Technical%20Data-d6d7ef3d",
      "chunk_id": "14533f81dec8e7d0",
      "score": 0.70114356,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EMGA4611%20Technical%20Data.pdf",
      "document_id": "full-EMGA4611%20Technical%20Data-8370abb0",
      "chunk_id": "ca37b1a51c4311a1",
      "score": 0.69700193,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EHCS082532%20Technical%20Data.pdf",
      "document_id": "full-EHCS082532%20Technical%20Data-c7bb4c80",
      "chunk_id": "a9e566ac59f583c2",
      "score": 0.6946104,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMNS1232%20Technical%20Data.pdf",
      "document_id": "full-EMNS1232%20Technical%20Data-35fbea12",
      "chunk_id": "5e72a4cf2467899e",
      "score": 0.69270086,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    }
  ]
}
```

```json
{
  "query_id": "BL06",
  "query": "Quelle norme et quelle classification sont indiquées pour Adhércol P-3000 ?",
  "categories": [
    "standards/norms"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
        "file_name": "Adhércol P-3000_Compressed.pdf",
        "source_path": "ai_data\\raw\\sofap\\Adhércol P-3000_Compressed.pdf",
        "chunk_ids": [
          "9bd12e595fbda7a8"
        ],
        "substring": "Colle adhésive en pâte à base de résine synthéƟque en dispersion aqueuse et d’addiƟfs spéciaux, prêt à l’emploi, à temps ouvert allongé et résistant au glissement, classé D1TE selon EN 12004."
      },
      "dense_document_rank": 24,
      "dense_chunk_rank": null,
      "lexical_rank": 25,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "9bd12e595fbda7a8",
          "identifier": 0.0,
          "filename": 0.4,
          "idf_overlap": 0.35034267897580473,
          "numeric": 1.0,
          "lexical_score": 1.7503426789758048
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": 24,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": 24
    },
    "100": {
      "first_evidence": null,
      "first_document": 24
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 25,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "EMRV2801%20Technical%20Data.pdf",
      "document_id": "full-EMRV2801%20Technical%20Data-19cf58ef",
      "chunk_id": "e5a287f9aa775bc6",
      "score": 0.759732,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMRV2802%20Technical%20Data.pdf",
      "document_id": "full-EMRV2802%20Technical%20Data-bd5c36a9",
      "chunk_id": "d51f83423074e8c1",
      "score": 0.759732,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "fiche_technique_pap2.pdf",
      "document_id": "full-fiche_technique_pap2-9b35b6f2",
      "chunk_id": "7a08902712732f92",
      "score": 0.7489412,
      "section_path": [
        "CARACTERISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "fiche_technique_pap2.pdf",
      "document_id": "full-fiche_technique_pap2-9b35b6f2",
      "chunk_id": "b0a2c435fa1c9bed",
      "score": 0.7489412,
      "section_path": [
        "CARACTERISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPERDUR1.pdf",
      "document_id": "full-SUPERDUR1-8aaac074",
      "chunk_id": "d546dc5ab14ea46c",
      "score": 0.7349566,
      "section_path": [
        "• EN 13813  _   DTU 26-2  _  DTU 13.3 ."
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "chunk_id": "e3511aaa87964a86",
      "score": 0.72358924,
      "section_path": [
        "MURENDUITCACHET VERT"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "chunk_id": "956b52cda2e6d3ff",
      "score": 0.7209128,
      "section_path": [
        "DESCRIPTION PRODUIT\nLES PLUS PRODUIT"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "754a782a4dcfb25e",
      "score": 0.72035336,
      "section_path": [
        "LIKA FINA"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "773d8cea09acd46b",
      "score": 0.71825624,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ENAL02271%20Technical%20Data.pdf",
      "document_id": "full-ENAL02271%20Technical%20Data-01ea6a48",
      "chunk_id": "993ba643ce5a6fe0",
      "score": 0.7172915,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    }
  ]
}
```

```json
{
  "query_id": "BL07",
  "query": "SOFAPCOL FLEX convient-il aux pierres naturelles et au grès cérame ?",
  "categories": [
    "substrate/support compatibility"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-FLEX%20V4-afe87429",
        "file_name": "FLEX%20V4.pdf",
        "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
        "chunk_ids": [
          "999bccf06fa6fd31"
        ],
        "substring": "• Pose de carrelages (grés cerame) et pierres naturelles (marbre, pierre, calcaire, granit) de toute porosité et de grands formats."
      },
      "dense_document_rank": 1,
      "dense_chunk_rank": 20,
      "lexical_rank": 2,
      "reranked_position": 2,
      "lexical_features": [
        {
          "chunk_id": "999bccf06fa6fd31",
          "identifier": 0.0,
          "filename": 0.14285714285714285,
          "idf_overlap": 0.7360135245807471,
          "numeric": 0,
          "lexical_score": 0.8788706674378899
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 20,
  "first_correct_document_rank": 1,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 1,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 1
    },
    "20": {
      "first_evidence": 20,
      "first_document": 1
    },
    "50": {
      "first_evidence": 20,
      "first_document": 1
    },
    "100": {
      "first_evidence": 20,
      "first_document": 1
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 2,
  "reranked_first_evidence_position": 2,
  "diagnosis": [
    "B: correct evidence exists, below rank 10",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "FLEX%20V4.pdf",
      "document_id": "full-FLEX%20V4-afe87429",
      "chunk_id": "073b9b2da7ef170a",
      "score": 0.7585247,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "de0931a97048d788",
      "score": 0.7388375,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "chunk_id": "f3dfa178191a32df",
      "score": 0.7180315,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "773d8cea09acd46b",
      "score": 0.7150586,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "Pro 3000_Compressed.pdf",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "chunk_id": "77736c0745034455",
      "score": 0.7149816,
      "section_path": [
        "PRO 3000"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "PRO%20200%20V4.pdf",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "chunk_id": "a91a20d4d58b4977",
      "score": 0.7140832,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ECO%20COLLE%20V4.pdf",
      "document_id": "full-ECO%20COLLE%20V4-b4db0cfb",
      "chunk_id": "c6f2a85f21142eb3",
      "score": 0.71028197,
      "section_path": [
        "• NF EN 12004 : 2017-04    . DTU 52.1     .  DTU 52.2"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "chunk_id": "0742076abc32d1e2",
      "score": 0.71028197,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MARBRE%20V4.pdf",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "chunk_id": "83cd53960bfa8d59",
      "score": 0.71028197,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "4e85828272934e10",
      "score": 0.71028197,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL08",
  "query": "Comment préparer un sac de 25 kg de SOFAPCOL FLEX et combien d’eau ajouter ?",
  "categories": [
    "preparation/application instructions"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-FLEX%20V4-afe87429",
        "file_name": "FLEX%20V4.pdf",
        "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
        "chunk_ids": [
          "073b9b2da7ef170a"
        ],
        "substring": "• Dans un récipient contenant environ 7 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL FLEX en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon."
      },
      "dense_document_rank": 1,
      "dense_chunk_rank": 1,
      "lexical_rank": 2,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "073b9b2da7ef170a",
          "identifier": 0.0,
          "filename": 0.125,
          "idf_overlap": 0.6329757106903388,
          "numeric": 1.0,
          "lexical_score": 1.7579757106903386
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 1,
  "first_correct_document_rank": 1,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 1,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 1,
      "first_document": 1
    },
    "20": {
      "first_evidence": 1,
      "first_document": 1
    },
    "50": {
      "first_evidence": 1,
      "first_document": 1
    },
    "100": {
      "first_evidence": 1,
      "first_document": 1
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 2,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [
    "near-duplicate confusion"
  ],
  "near_duplicate_sources": [
    [
      "full-MARBRE%20V4-5e49c875",
      "MARBRE%20V4.pdf",
      "ai_data\\raw\\sofap\\MARBRE%20V4.pdf"
    ],
    [
      "full-PISCINE%20V4-18fdf73d",
      "PISCINE%20V4.pdf",
      "ai_data\\raw\\sofap\\PISCINE%20V4.pdf"
    ],
    [
      "full-POOL%20V2-9db8b280",
      "POOL%20V2.pdf",
      "ai_data\\raw\\sofap\\POOL%20V2.pdf"
    ],
    [
      "full-PRO%20200%20V4-8f310261",
      "PRO%20200%20V4.pdf",
      "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf"
    ],
    [
      "full-Pro 3000_Compressed-94812339",
      "Pro 3000_Compressed.pdf",
      "ai_data\\raw\\sofap\\Pro 3000_Compressed.pdf"
    ]
  ],
  "dense_top10": [
    {
      "file_name": "FLEX%20V4.pdf",
      "document_id": "full-FLEX%20V4-afe87429",
      "chunk_id": "073b9b2da7ef170a",
      "score": 0.8177956,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "PRO%20200%20V4.pdf",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "chunk_id": "a91a20d4d58b4977",
      "score": 0.790308,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "Pro 3000_Compressed.pdf",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "chunk_id": "77736c0745034455",
      "score": 0.78996134,
      "section_path": [
        "PRO 3000"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "MARBRE%20V4.pdf",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "chunk_id": "26ca29e335f59e35",
      "score": 0.78268534,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "Rustika assila_Compressed.pdf",
      "document_id": "full-Rustika assila_Compressed-a2177721",
      "chunk_id": "c08f4c92cc8e8a8a",
      "score": 0.7825593,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "chunk_id": "9572fff3d98caa9e",
      "score": 0.7801583,
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "4b4648df10f53b4f",
      "score": 0.7789963,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "PISCINE%20V4.pdf",
      "document_id": "full-PISCINE%20V4-18fdf73d",
      "chunk_id": "adf774558b45ef2e",
      "score": 0.7759032,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "85aa3643e2d06a94",
      "score": 0.77584445,
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "70e5a48a7b1dfe77",
      "score": 0.7752737,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL09",
  "query": "Peut-on ajouter de l’eau à PRIMER CONTACT et quelles protections porter ?",
  "categories": [
    "safety/limitations"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-primer%20contact1-411ec87f",
        "file_name": "primer%20contact1.pdf",
        "source_path": "ai_data\\raw\\sofap\\primer%20contact1.pdf",
        "chunk_ids": [
          "013da106acce8f93"
        ],
        "substring": "• Bien mélanger le contenu du seau avant usage.\n• Le produit étant prêt à l’emploi, ne pas ajouter d’eau.\n• NeƩoyer les ouƟls immédiatement après applicaƟon avec de l’eau.\n• Le port des protecƟons individuelles (gants, luneƩes) est recommandé."
      },
      "dense_document_rank": 2,
      "dense_chunk_rank": 16,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "013da106acce8f93",
          "identifier": 0.0,
          "filename": 0.125,
          "idf_overlap": 0.5073074161666213,
          "numeric": 0,
          "lexical_score": 0.6323074161666213
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 16,
  "first_correct_document_rank": 2,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 2,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 2
    },
    "20": {
      "first_evidence": 16,
      "first_document": 2
    },
    "50": {
      "first_evidence": 16,
      "first_document": 2
    },
    "100": {
      "first_evidence": 16,
      "first_document": 2
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "B: correct evidence exists, below rank 10",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "chunk_id": "1bca5b1704c94391",
      "score": 0.78528184,
      "section_path": [],
      "block_type": "list_item"
    },
    {
      "file_name": "primer%20contact1.pdf",
      "document_id": "full-primer%20contact1-411ec87f",
      "chunk_id": "acc4b208ab89c4fe",
      "score": 0.7688025,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "chunk_id": "2585d4193f6dceb6",
      "score": 0.76527035,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FULL%20ECO1.pdf",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "chunk_id": "75968bb1fcbb8ab8",
      "score": 0.7644166,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "f5492bdf3d16e93e",
      "score": 0.762556,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "primer%20contact1.pdf",
      "document_id": "full-primer%20contact1-411ec87f",
      "chunk_id": "d59603e4e838b980",
      "score": 0.7619997,
      "section_path": [
        "PRIMER CONTACT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FULL%201.pdf",
      "document_id": "full-FULL%201-eb0d29c6",
      "chunk_id": "2b5908942f240115",
      "score": 0.75867534,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "chunk_id": "1415cb037decd94c",
      "score": 0.75341046,
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "primer%20contact1.pdf",
      "document_id": "full-primer%20contact1-411ec87f",
      "chunk_id": "d29563e990c09be0",
      "score": 0.7473438,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "e5811fdab98d582a",
      "score": 0.7470782,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL10",
  "query": "Comparer la consommation de SUPLATEX en primaire à celle de HYDRO REP surfaçage.",
  "categories": [
    "cross-document ambiguity",
    "consumption"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-SUPLATEX1-c1a35954",
        "file_name": "SUPLATEX1.pdf",
        "source_path": "ai_data\\raw\\sofap\\SUPLATEX1.pdf",
        "chunk_ids": [
          "3ffbfb4c1ebb40d8"
        ],
        "substring": "• En couche d'accrochage (gobeƟs, barboƟne) : environ 0,120 L / m².\n• En morƟer : environ 0,600 L / m².\n• En primaire : de 80 g à 150 g/m² environ selon la nature du support.\n• En produit de cure : 150 g/m² environ."
      },
      "dense_document_rank": 6,
      "dense_chunk_rank": null,
      "lexical_rank": 97,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "3ffbfb4c1ebb40d8",
          "identifier": 0.0,
          "filename": 0.0,
          "idf_overlap": 0.13204778271946466,
          "numeric": 0,
          "lexical_score": 0.13204778271946466
        }
      ]
    },
    {
      "expected": {
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "chunk_ids": [
          "0edc15932b396769"
        ],
        "substring": "La consommation de l’HYDRO REP surfaçage varie selon le support (type, planéité, rugosité) env.1.15 kg / m?/mm."
      },
      "dense_document_rank": 1,
      "dense_chunk_rank": 1,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "0edc15932b396769",
          "identifier": 0.0,
          "filename": 0.375,
          "idf_overlap": 0.39890417459842775,
          "numeric": 0,
          "lexical_score": 0.7739041745984278
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 1,
  "first_correct_document_rank": 1,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 1,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 1,
      "first_document": 1
    },
    "20": {
      "first_evidence": 1,
      "first_document": 1
    },
    "50": {
      "first_evidence": 1,
      "first_document": 1
    },
    "100": {
      "first_evidence": 1,
      "first_document": 1
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [
    "ambiguous label"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "0edc15932b396769",
      "score": 0.8080122,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "d84c18a2bbfb26d5",
      "score": 0.7963809,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "2568dbcc81a0785f",
      "score": 0.7607957,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "5fcda73e77764500",
      "score": 0.7594074,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "db288555be8d569a",
      "score": 0.75869524,
      "section_path": [
        "DESCRIPTION PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPLATEX1.pdf",
      "document_id": "full-SUPLATEX1-c1a35954",
      "chunk_id": "968b8614fe5a30ac",
      "score": 0.71938145,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "971e1b6068337e7f",
      "score": 0.71340585,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPLATEX1.pdf",
      "document_id": "full-SUPLATEX1-c1a35954",
      "chunk_id": "04258c193e904e1e",
      "score": 0.70728534,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "e117e2529af03f13",
      "score": 0.7064791,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "chunk_id": "2ff6b76c7f05cd1c",
      "score": 0.70282286,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "list_item"
    }
  ]
}
```

```json
{
  "query_id": "BL11",
  "query": "Je cherche un outil pour couper des branches : que peut-il couper et quelles sont ses limites ?",
  "categories": [
    "vague/general",
    "safety/limitations"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
        "file_name": "ELSL203051%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ELSL203051%20Technical%20Data.pdf",
        "chunk_ids": [
          "ae22722a9aeab3e8"
        ],
        "substring": "Cet équipement est conçu pour couper des branches et des plantes d’un diamètre maximal de 30 mm (bois tendre). Le diamètre est plus petit pour le bois dur. Cet équipement ne convient pas à la coupe du métal. L’équipement doit être utilisé uniquement pour l’usage prévu.\nMoteur sans balais haute efficacité offrant plus de puissance et maximisant l’autonomie"
      },
      "dense_document_rank": 11,
      "dense_chunk_rank": 11,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "ae22722a9aeab3e8",
          "identifier": 0.0,
          "filename": 0.0,
          "idf_overlap": 0.3123094298398941,
          "numeric": 0,
          "lexical_score": 0.3123094298398941
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 11,
  "first_correct_document_rank": 11,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": 11,
      "first_document": 11
    },
    "50": {
      "first_evidence": 11,
      "first_document": 11
    },
    "100": {
      "first_evidence": 11,
      "first_document": 11
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "B: correct evidence exists, below rank 10"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "ambiguous label"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "CONFORT%20PLUS%20V4.pdf",
      "document_id": "full-CONFORT%20PLUS%20V4-41c49bed",
      "chunk_id": "dd46b468f92226dc",
      "score": 0.73436517,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "CONFORT%20V4.pdf",
      "document_id": "full-CONFORT%20V4-577b657d",
      "chunk_id": "fc9f5e8767ea2792",
      "score": 0.73436517,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ECO%20COLLE%20V4.pdf",
      "document_id": "full-ECO%20COLLE%20V4-b4db0cfb",
      "chunk_id": "611f2da5f82bd904",
      "score": 0.73436517,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "chunk_id": "8779cc81e863dc56",
      "score": 0.73436517,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FLEX%20V4.pdf",
      "document_id": "full-FLEX%20V4-afe87429",
      "chunk_id": "dbd31a2942b925d6",
      "score": 0.73436517,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MARBRE%20V4.pdf",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "chunk_id": "5690ef200a268e37",
      "score": 0.73436517,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "PRO%201000%20V2.pdf",
      "document_id": "full-PRO%201000%20V2-467bc232",
      "chunk_id": "bfd26e2eddb9bfee",
      "score": 0.73436517,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "PRO%20200%20V4.pdf",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "chunk_id": "d61d1e9ec28a843a",
      "score": 0.73436517,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Pro 2000_Compressed.pdf",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "chunk_id": "0ccff9d7e8075d47",
      "score": 0.73436517,
      "section_path": [
        "PRO 2000"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Pro 3000_Compressed.pdf",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "chunk_id": "067db28072e479c1",
      "score": 0.73436517,
      "section_path": [
        "PRO 3000"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL12",
  "query": "Quelle pression et quelle consommation d’air demande la clé EATL341601 ?",
  "categories": [
    "highly specific",
    "technical specifications"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EATL341601%20Technical%20Data-7d7a619c",
        "file_name": "EATL341601%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EATL341601%20Technical%20Data.pdf",
        "chunk_ids": [
          "ac2941f29e389f39"
        ],
        "substring": "Entraînement carré : 19 mm (3/4\")\nVitesse à vide : 4 000 tr/min Couple maximum : 1 600 Nm (1 180 pieds)\nPoids : 6,0 kg Mécanisme à double marteau Avec connecteur universel.\nConsommation d'air : 256 l/min (9 cfm) Pression d'air : 6,2 bar (90 psi)\nLongueur : 234 mm (9,2\") Poids : 5,9 kg (13 lb) Entrée d'air : 3/8\" Tuyau d'air : 1/2\" Emballé par boîte de couleur"
      },
      "dense_document_rank": 16,
      "dense_chunk_rank": 16,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "ac2941f29e389f39",
          "identifier": 1.0,
          "filename": 0.14285714285714285,
          "idf_overlap": 0.6401371141485799,
          "numeric": 0,
          "lexical_score": 1.7829942570057227
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 16,
  "first_correct_document_rank": 16,
  "identifier_detected": [
    "EATL341601"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": 16,
      "first_document": 16
    },
    "50": {
      "first_evidence": 16,
      "first_document": 16
    },
    "100": {
      "first_evidence": 16,
      "first_document": 16
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "EATL341601",
      "matches": [
        [
          "full-EATL341601%20Technical%20Data-7d7a619c",
          "EATL341601%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\EATL341601%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "B: correct evidence exists, below rank 10"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "EMGG3550%20Technical%20Data.pdf",
      "document_id": "full-EMGG3550%20Technical%20Data-56663801",
      "chunk_id": "206c31312a3662f2",
      "score": 0.7300385,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EAPR15001%20Technical%20Data.pdf",
      "document_id": "full-EAPR15001%20Technical%20Data-4a46aca9",
      "chunk_id": "0c9d5f3b9fb24a25",
      "score": 0.7191226,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EASG04001%20Technical%20Data.pdf",
      "document_id": "full-EASG04001%20Technical%20Data-9561e471",
      "chunk_id": "dcc937063e54ae7f",
      "score": 0.71466565,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "chunk_id": "d867d5ac24847cda",
      "score": 0.71131516,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EAPR15001%20Technical%20Data.pdf",
      "document_id": "full-EAPR15001%20Technical%20Data-4a46aca9",
      "chunk_id": "39b44e9a5cbbe6ce",
      "score": 0.6953573,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EASGT8501%20Technical%20Data.pdf",
      "document_id": "full-EASGT8501%20Technical%20Data-b3c1195b",
      "chunk_id": "c767e3e9922ae9e7",
      "score": 0.68478477,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EAHE1001%20Technical%20Data.pdf",
      "document_id": "full-EAHE1001%20Technical%20Data-16bfc62e",
      "chunk_id": "a990882d346c46b0",
      "score": 0.68251145,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EAHE1501%20Technical%20Data.pdf",
      "document_id": "full-EAHE1501%20Technical%20Data-74ed339a",
      "chunk_id": "c59c9f6c8bdd4173",
      "score": 0.68251145,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPERDUR1.pdf",
      "document_id": "full-SUPERDUR1-8aaac074",
      "chunk_id": "d5730bec442a294e",
      "score": 0.6808648,
      "section_path": [
        "NB :"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ECUT451%20Technical%20Data.pdf",
      "document_id": "full-ECUT451%20Technical%20Data-d6d7ef3d",
      "chunk_id": "08e4a75b2204b5b8",
      "score": 0.6798242,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL13",
  "query": "Quelle est la puissance et la vitesse à vide de la scie ECSW1852 ?",
  "categories": [
    "technical specifications"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ECSW1852%20Technical%20Data-c3aa9e19",
        "file_name": "ECSW1852%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ECSW1852%20Technical%20Data.pdf",
        "chunk_ids": [
          "9c77702218b75b91"
        ],
        "substring": "Puissance d'entrée : 1400 W Vitesse à vide : 4800 tr/min Diamètre de la lame : 185 x 20 mm Capacité de coupe : 45 degrés : 45 mm 90 degrés : 65 mm Profondeur de coupe réglable Coupe en biseau réglable Avec 1 lame de 185 mm Avec 1 jeu de balais de charbon supplémentaires Emballé par boîte de couleur"
      },
      "dense_document_rank": null,
      "dense_chunk_rank": null,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "9c77702218b75b91",
          "identifier": 1.0,
          "filename": 0.2,
          "idf_overlap": 0.7696642009721505,
          "numeric": 0,
          "lexical_score": 1.9696642009721506
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": null,
  "identifier_detected": [
    "ECSW1852"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": null
    },
    "100": {
      "first_evidence": null,
      "first_document": null
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ECSW1852",
      "matches": [
        [
          "full-ECSW1852%20Technical%20Data-c3aa9e19",
          "ECSW1852%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ECSW1852%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "HYDRO%20FAçADE1.pdf",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "chunk_id": "031ad00d0540dd7d",
      "score": 0.67648673,
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "f2cdbbf3df18ee05",
      "score": 0.67485404,
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "chunk_id": "33262ba0f7af283e",
      "score": 0.67485404,
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "773d8cea09acd46b",
      "score": 0.6680756,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "hydromur%20R%20V4.pdf",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "chunk_id": "f128ab9f6123efac",
      "score": 0.66635406,
      "section_path": [
        "HYDROMUR R"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ELAB2078%20Technical%20Data.pdf",
      "document_id": "full-ELAB2078%20Technical%20Data-f807d4c7",
      "chunk_id": "0bca250d1cabc854",
      "score": 0.6623418,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "SUPERDUR1.pdf",
      "document_id": "full-SUPERDUR1-8aaac074",
      "chunk_id": "aa01dc4cb13f5865",
      "score": 0.6569576,
      "section_path": [
        "AR2"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FULL.pdf",
      "document_id": "full-FULL-88a1b942",
      "chunk_id": "076493283f1e2307",
      "score": 0.65676314,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "chunk_id": "924ba4a85a9bdb99",
      "score": 0.65676314,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPERLITE1.pdf",
      "document_id": "full-SUPERLITE1-8227dad4",
      "chunk_id": "3b57ed57aadd8934",
      "score": 0.65676314,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL14",
  "query": "Comment appliquer PRIMER CONTACT sur un support très lisse ?",
  "categories": [
    "preparation/application instructions"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-primer%20contact1-411ec87f",
        "file_name": "primer%20contact1.pdf",
        "source_path": "ai_data\\raw\\sofap\\primer%20contact1.pdf",
        "chunk_ids": [
          "90d0baaf325706fc"
        ],
        "substring": "•  Appliquer PRIMER CONTACT au rouleau (laine de préférence) ou à l’aide d’une brosse, en une couche régulière réalisée en passes croisées.\n•  En cas de support très lisse ou texturé, il est recommandé d’appliquer PRIMER CONTACT en couche croisée."
      },
      "dense_document_rank": 1,
      "dense_chunk_rank": 1,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "90d0baaf325706fc",
          "identifier": 0.0,
          "filename": 0.16666666666666666,
          "idf_overlap": 1.0,
          "numeric": 0,
          "lexical_score": 1.1666666666666667
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 1,
  "first_correct_document_rank": 1,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 1,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 1,
      "first_document": 1
    },
    "20": {
      "first_evidence": 1,
      "first_document": 1
    },
    "50": {
      "first_evidence": 1,
      "first_document": 1
    },
    "100": {
      "first_evidence": 1,
      "first_document": 1
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "primer%20contact1.pdf",
      "document_id": "full-primer%20contact1-411ec87f",
      "chunk_id": "90d0baaf325706fc",
      "score": 0.84812444,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FULL%20ECO1.pdf",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "chunk_id": "75968bb1fcbb8ab8",
      "score": 0.8268875,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "chunk_id": "2585d4193f6dceb6",
      "score": 0.82393795,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "f5492bdf3d16e93e",
      "score": 0.82092756,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FULL%201.pdf",
      "document_id": "full-FULL%201-eb0d29c6",
      "chunk_id": "2b5908942f240115",
      "score": 0.8183182,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "e5811fdab98d582a",
      "score": 0.7933945,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "primer%20contact1.pdf",
      "document_id": "full-primer%20contact1-411ec87f",
      "chunk_id": "d29563e990c09be0",
      "score": 0.7828393,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "jir%20pro%20etanche1.pdf",
      "document_id": "full-jir%20pro%20etanche1-7c9a4574",
      "chunk_id": "99b158dfb177514a",
      "score": 0.7787672,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "SUPERDUR1.pdf",
      "document_id": "full-SUPERDUR1-8aaac074",
      "chunk_id": "5e6b22e6c396db41",
      "score": 0.77788377,
      "section_path": [
        "SUPERDUR"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "PRO%201000%20V2.pdf",
      "document_id": "full-PRO%201000%20V2-467bc232",
      "chunk_id": "4e3832319058a64a",
      "score": 0.7758473,
      "section_path": [
        "• NF EN 12004 : 2017-04   _  DTU 52.1  _ DTU 52.2"
      ],
      "block_type": "list_item"
    }
  ]
}
```

```json
{
  "query_id": "BL15",
  "query": "Combien de temps peut-on conserver PRIMER CONTACT et dans quelles conditions ?",
  "categories": [
    "safety/limitations"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-primer%20contact1-411ec87f",
        "file_name": "primer%20contact1.pdf",
        "source_path": "ai_data\\raw\\sofap\\primer%20contact1.pdf",
        "chunk_ids": [
          "acc4b208ab89c4fe"
        ],
        "substring": "• PRIMER CONTACT  se compose d’un liant synthéƟque avec une stabilité alcaline, charges siliceuses, colorant. .ConservaƟon :\n• 12 mois en emballage d’origine, fermé à l’abri de l’humidité, protégé du gel et des excès de chaleur (soleil direct)."
      },
      "dense_document_rank": 1,
      "dense_chunk_rank": 2,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "acc4b208ab89c4fe",
          "identifier": 0.0,
          "filename": 0.16666666666666666,
          "idf_overlap": 0.419406897993156,
          "numeric": 0,
          "lexical_score": 0.5860735646598226
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 2,
  "first_correct_document_rank": 1,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 1,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 2,
      "first_document": 1
    },
    "20": {
      "first_evidence": 2,
      "first_document": 1
    },
    "50": {
      "first_evidence": 2,
      "first_document": 1
    },
    "100": {
      "first_evidence": 2,
      "first_document": 1
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "primer%20contact1.pdf",
      "document_id": "full-primer%20contact1-411ec87f",
      "chunk_id": "d59603e4e838b980",
      "score": 0.77064127,
      "section_path": [
        "PRIMER CONTACT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "primer%20contact1.pdf",
      "document_id": "full-primer%20contact1-411ec87f",
      "chunk_id": "acc4b208ab89c4fe",
      "score": 0.7684444,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "CONFORT%20PLUS%20V4.pdf",
      "document_id": "full-CONFORT%20PLUS%20V4-41c49bed",
      "chunk_id": "07007d33c86e226c",
      "score": 0.7515702,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ECO%20COLLE%20V4.pdf",
      "document_id": "full-ECO%20COLLE%20V4-b4db0cfb",
      "chunk_id": "cd4e058a96d140f6",
      "score": 0.7515702,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "chunk_id": "f3da65df9d943d2b",
      "score": 0.7515702,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FLEX%20V4.pdf",
      "document_id": "full-FLEX%20V4-afe87429",
      "chunk_id": "ba19cdce49b98060",
      "score": 0.7515702,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MARBRE%20V4.pdf",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "chunk_id": "390ea0aa088cda65",
      "score": 0.7515702,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "7a6852adcec66dda",
      "score": 0.7515702,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "PRO%201000%20V2.pdf",
      "document_id": "full-PRO%201000%20V2-467bc232",
      "chunk_id": "bf03cd2ddd44cb21",
      "score": 0.7515702,
      "section_path": [
        "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Pro 3000_Compressed.pdf",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "chunk_id": "adf4c8fd91f464a0",
      "score": 0.7515702,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL16",
  "query": "Quel délai minimum avant jointoiement avec SOFAPCOL FLEX ?",
  "categories": [
    "application/use",
    "highly specific"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-FLEX%20V4-afe87429",
        "file_name": "FLEX%20V4.pdf",
        "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
        "chunk_ids": [
          "ce25465f13a094bd"
        ],
        "substring": "ux de gâchage : | Environ 28%\nurée de malaxage : | Environ 3 min\nmps de maturaƟon : | Environ 5 min\nmps ouvert : | Environ 30 min\n\nurée praƟque d’uƟlisaƟ | on : Environ 3 heures\nélais avant jointoieme | nt : Minimum 24 heures\n\nccessibilité : | 24à 48 h après réalisaƟon des joints"
      },
      "dense_document_rank": 6,
      "dense_chunk_rank": 15,
      "lexical_rank": 5,
      "reranked_position": 7,
      "lexical_features": [
        {
          "chunk_id": "ce25465f13a094bd",
          "identifier": 0.0,
          "filename": 0.2,
          "idf_overlap": 0.35421933334671096,
          "numeric": 0,
          "lexical_score": 0.5542193333467109
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 15,
  "first_correct_document_rank": 6,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 6,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 6
    },
    "20": {
      "first_evidence": 15,
      "first_document": 6
    },
    "50": {
      "first_evidence": 15,
      "first_document": 6
    },
    "100": {
      "first_evidence": 15,
      "first_document": 6
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 5,
  "reranked_first_evidence_position": 7,
  "diagnosis": [
    "B: correct evidence exists, below rank 10",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed",
    "parser/OCR issue"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "PRO%201000%20V2.pdf",
      "document_id": "full-PRO%201000%20V2-467bc232",
      "chunk_id": "1eb986205f7e994b",
      "score": 0.7846732,
      "section_path": [
        "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "CONFORT%20PLUS%20V4.pdf",
      "document_id": "full-CONFORT%20PLUS%20V4-41c49bed",
      "chunk_id": "d2983c001ec87046",
      "score": 0.78170455,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "CONFORT%20V4.pdf",
      "document_id": "full-CONFORT%20V4-577b657d",
      "chunk_id": "e01d127ef86dcb4e",
      "score": 0.78170455,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ECO%20COLLE%20V4.pdf",
      "document_id": "full-ECO%20COLLE%20V4-b4db0cfb",
      "chunk_id": "2d806f6f56a5f3b0",
      "score": 0.78170455,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "chunk_id": "fe886cef4574047c",
      "score": 0.78170455,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FLEX%20V4.pdf",
      "document_id": "full-FLEX%20V4-afe87429",
      "chunk_id": "4f7d4ddd75712334",
      "score": 0.78170455,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MARBRE%20V4.pdf",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "chunk_id": "2eeac9df1ec2e611",
      "score": 0.78170455,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "1873ef801868ec6c",
      "score": 0.78170455,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Pro 2000_Compressed.pdf",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "chunk_id": "11dcfa0d8fb55539",
      "score": 0.78170455,
      "section_path": [
        "PRO 2000"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Pro 3000_Compressed.pdf",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "chunk_id": "1bf4218ba9db44d0",
      "score": 0.78170455,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL17",
  "query": "Comment préparer les supports ciment avant la pose avec FLEX ?",
  "categories": [
    "substrate/support compatibility",
    "preparation/application instructions"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-FLEX%20V4-afe87429",
        "file_name": "FLEX%20V4.pdf",
        "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
        "chunk_ids": [
          "ac36b959e19a154b"
        ],
        "substring": "• Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n• Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours, les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer."
      },
      "dense_document_rank": 3,
      "dense_chunk_rank": 3,
      "lexical_rank": 4,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "ac36b959e19a154b",
          "identifier": 0.0,
          "filename": 0.2,
          "idf_overlap": 0.6850099013959576,
          "numeric": 0,
          "lexical_score": 0.8850099013959576
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 3,
  "first_correct_document_rank": 3,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 3,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 3,
      "first_document": 3
    },
    "20": {
      "first_evidence": 3,
      "first_document": 3
    },
    "50": {
      "first_evidence": 3,
      "first_document": 3
    },
    "100": {
      "first_evidence": 3,
      "first_document": 3
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 4,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [
    "near-duplicate confusion"
  ],
  "near_duplicate_sources": [
    [
      "full-MARBRE%20V4-5e49c875",
      "MARBRE%20V4.pdf",
      "ai_data\\raw\\sofap\\MARBRE%20V4.pdf"
    ],
    [
      "full-PISCINE%20V4-18fdf73d",
      "PISCINE%20V4.pdf",
      "ai_data\\raw\\sofap\\PISCINE%20V4.pdf"
    ],
    [
      "full-POOL%20V2-9db8b280",
      "POOL%20V2.pdf",
      "ai_data\\raw\\sofap\\POOL%20V2.pdf"
    ],
    [
      "full-PRO%20200%20V4-8f310261",
      "PRO%20200%20V4.pdf",
      "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf"
    ],
    [
      "full-Pro 3000_Compressed-94812339",
      "Pro 3000_Compressed.pdf",
      "ai_data\\raw\\sofap\\Pro 3000_Compressed.pdf"
    ]
  ],
  "dense_top10": [
    {
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "chunk_id": "ca257ccf6af9ff8b",
      "score": 0.8052871,
      "section_path": [],
      "block_type": "paragraph"
    },
    {
      "file_name": "MARBRE%20V4.pdf",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "chunk_id": "301d91938bb3fb63",
      "score": 0.77258563,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FLEX%20V4.pdf",
      "document_id": "full-FLEX%20V4-afe87429",
      "chunk_id": "ac36b959e19a154b",
      "score": 0.77196825,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "PISCINE%20V4.pdf",
      "document_id": "full-PISCINE%20V4-18fdf73d",
      "chunk_id": "1019a5f113339ee8",
      "score": 0.77196825,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "7d6587bd4ab9a9d5",
      "score": 0.77196825,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "Pro 3000_Compressed.pdf",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "chunk_id": "8f1c03e0970e4e6f",
      "score": 0.77196825,
      "section_path": [
        "PRO 3000"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "PRO%20200%20V4.pdf",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "chunk_id": "7a9d5df8a3c81438",
      "score": 0.77139795,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "de0931a97048d788",
      "score": 0.7639587,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "chunk_id": "141e0f1f0585631f",
      "score": 0.75949246,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "chunk_id": "f3dfa178191a32df",
      "score": 0.7567497,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    }
  ]
}
```

```json
{
  "query_id": "BL18",
  "query": "À quelle norme est conforme Mura-colle-platre et quelle est sa consommation ?",
  "categories": [
    "standards/norms",
    "consumption"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
        "file_name": "fiche_technique_Mura-colle-platre.pdf",
        "source_path": "ai_data\\raw\\gypsobat\\documents\\fiche_technique_Mura-colle-platre.pdf",
        "chunk_ids": [
          "39a3d4120d0078db"
        ],
        "substring": "Consommation | 3 à 4 kg /m²\nTaux de gâchage | à consistance 25%±1\nConformité à la norme | EN12004\nAdhérance par traction | ≥ 0,5 N/mm²\nPropriétés | -Haute rétention d’eau. -Pouvoir liant trés efficace -Haute résistance en ambiance humide saturée.\n\nType de produit | mortiers de colle des carreaux faïence\nClassification | C1\nTemps ouvert | ≥ 30 mn\nTemps d’emploi 2 | h-3h\nTempérature d’application 5 | ° à 35° C"
      },
      "dense_document_rank": 3,
      "dense_chunk_rank": 89,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "39a3d4120d0078db",
          "identifier": 0.0,
          "filename": 0.42857142857142855,
          "idf_overlap": 0.6727373211009272,
          "numeric": 0,
          "lexical_score": 1.1013087496723557
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 89,
  "first_correct_document_rank": 3,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 3,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 3
    },
    "20": {
      "first_evidence": null,
      "first_document": 3
    },
    "50": {
      "first_evidence": null,
      "first_document": 3
    },
    "100": {
      "first_evidence": 89,
      "first_document": 3
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "B: correct evidence exists, below rank 10",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed",
    "parser/OCR issue"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "fiche_technique_pap2.pdf",
      "document_id": "full-fiche_technique_pap2-9b35b6f2",
      "chunk_id": "7a08902712732f92",
      "score": 0.8832691,
      "section_path": [
        "CARACTERISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "fiche_technique_pap2.pdf",
      "document_id": "full-fiche_technique_pap2-9b35b6f2",
      "chunk_id": "b0a2c435fa1c9bed",
      "score": 0.8832691,
      "section_path": [
        "CARACTERISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "fiche_technique_Mura-colle-platre.pdf",
      "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
      "chunk_id": "ecfd6a67c8a822d6",
      "score": 0.8075355,
      "section_path": [
        "STOCKAGE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "fiche_technique_Mura-colle-platre.pdf",
      "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
      "chunk_id": "2d280804ddcb1fa2",
      "score": 0.8075355,
      "section_path": [
        "STOCKAGE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EMRV2801%20Technical%20Data.pdf",
      "document_id": "full-EMRV2801%20Technical%20Data-19cf58ef",
      "chunk_id": "e5a287f9aa775bc6",
      "score": 0.7979171,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMRV2802%20Technical%20Data.pdf",
      "document_id": "full-EMRV2802%20Technical%20Data-bd5c36a9",
      "chunk_id": "d51f83423074e8c1",
      "score": 0.7979171,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "SUPERDUR1.pdf",
      "document_id": "full-SUPERDUR1-8aaac074",
      "chunk_id": "d546dc5ab14ea46c",
      "score": 0.75324285,
      "section_path": [
        "• EN 13813  _   DTU 26-2  _  DTU 13.3 ."
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA-FINA-1.pdf",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "chunk_id": "773d8cea09acd46b",
      "score": 0.7357313,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ISBAROC-R.pdf",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "chunk_id": "4dd5fdefca2bbe6f",
      "score": 0.73153824,
      "section_path": [
        ":| CSHI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ISBAROC-R.pdf",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "chunk_id": "f4729b6911c99328",
      "score": 0.73113227,
      "section_path": [
        ":| CSHI"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL19",
  "query": "Quelles sont les dimensions du chariot à sept tiroirs ETCS0701 avec ses roulettes ?",
  "categories": [
    "dimensions",
    "highly specific"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ETCS0701%20Technical%20Data-2f79a4f6",
        "file_name": "ETCS0701%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ETCS0701%20Technical%20Data.pdf",
        "chunk_ids": [
          "4cde6050e2f553a5"
        ],
        "substring": "1. Grand espace de stockage, poussoir confortable.\n2. Chaque tiroir est équipé d'une fonction d'auto-verrouillage pour éviter qu'il ne glisse automatiquement.\n3. Dispositif de frein pour roulettes multidirectionnelles.\n4. Conception de glissières à billes entièrement extensibles.\n5. Le corps du chariot est fabriqué en tôle d'acier laminée à froid de haute qualité, solide et robuste. Armoire à roulettes Avec 7 tiroirs Dimensions totales : 680*458*802mm Dimensions totales avec roulettes : 680*458*945mm"
      },
      "dense_document_rank": 2,
      "dense_chunk_rank": 2,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "4cde6050e2f553a5",
          "identifier": 1.0,
          "filename": 0.16666666666666666,
          "idf_overlap": 0.7976528894488619,
          "numeric": 0,
          "lexical_score": 1.9643195561155287
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 2,
  "first_correct_document_rank": 2,
  "identifier_detected": [
    "ETCS0701"
  ],
  "baseline_top10_first_document_rank": 2,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 2,
      "first_document": 2
    },
    "20": {
      "first_evidence": 2,
      "first_document": 2
    },
    "50": {
      "first_evidence": 2,
      "first_document": 2
    },
    "100": {
      "first_evidence": 2,
      "first_document": 2
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ETCS0701",
      "matches": [
        [
          "full-ETCS0701%20Technical%20Data-2f79a4f6",
          "ETCS0701%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ETCS0701%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ETDR7A30%20Technical%20Data.pdf",
      "document_id": "full-ETDR7A30%20Technical%20Data-fd99ae9f",
      "chunk_id": "83bbcde9f1cf5952",
      "score": 0.77782786,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ETCS0701%20Technical%20Data.pdf",
      "document_id": "full-ETCS0701%20Technical%20Data-2f79a4f6",
      "chunk_id": "4cde6050e2f553a5",
      "score": 0.770182,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ETCS0301%20Technical%20Data.pdf",
      "document_id": "full-ETCS0301%20Technical%20Data-595b4f13",
      "chunk_id": "cfc34d415a9c99eb",
      "score": 0.764422,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ETCS0402%20Technical%20Data.pdf",
      "document_id": "full-ETCS0402%20Technical%20Data-a72c933b",
      "chunk_id": "4b3eb9c29133ad5a",
      "score": 0.7634505,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ETCS0701%20Technical%20Data.pdf",
      "document_id": "full-ETCS0701%20Technical%20Data-2f79a4f6",
      "chunk_id": "f0b24f138d33128a",
      "score": 0.75973284,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ETCS0402%20Technical%20Data.pdf",
      "document_id": "full-ETCS0402%20Technical%20Data-a72c933b",
      "chunk_id": "33a5f2aa938de2e5",
      "score": 0.744274,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ETCS0301%20Technical%20Data.pdf",
      "document_id": "full-ETCS0301%20Technical%20Data-595b4f13",
      "chunk_id": "67ea3227ec08a7c0",
      "score": 0.73708355,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ETCS0402%20Technical%20Data.pdf",
      "document_id": "full-ETCS0402%20Technical%20Data-a72c933b",
      "chunk_id": "7109cea0144077fb",
      "score": 0.6997547,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EMTB1322%20Technical%20Data.pdf",
      "document_id": "full-EMTB1322%20Technical%20Data-c1a8f553",
      "chunk_id": "05647b178a6474f2",
      "score": 0.69695675,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EPBE820301%20Technical%20Data.pdf",
      "document_id": "full-EPBE820301%20Technical%20Data-a8cddda2",
      "chunk_id": "0f6e7cd838fcdeb7",
      "score": 0.6927042,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL20",
  "query": "Quelle est la capacité de charge du chariot ETDR7A30 ?",
  "categories": [
    "technical specifications"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ETDR7A30%20Technical%20Data-fd99ae9f",
        "file_name": "ETDR7A30%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ETDR7A30%20Technical%20Data.pdf",
        "chunk_ids": [
          "83bbcde9f1cf5952"
        ],
        "substring": "1. Matériau de haute qualité, solide et durable\n2. Avec frein à pied, facile à utiliser Charge : ≤300kg Dimensions du chariot : 1280*870*360mm"
      },
      "dense_document_rank": 2,
      "dense_chunk_rank": 2,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "83bbcde9f1cf5952",
          "identifier": 1.0,
          "filename": 0.25,
          "idf_overlap": 0.7878802741137897,
          "numeric": 0,
          "lexical_score": 2.03788027411379
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 2,
  "first_correct_document_rank": 2,
  "identifier_detected": [
    "ETDR7A30"
  ],
  "baseline_top10_first_document_rank": 2,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 2,
      "first_document": 2
    },
    "20": {
      "first_evidence": 2,
      "first_document": 2
    },
    "50": {
      "first_evidence": 2,
      "first_document": 2
    },
    "100": {
      "first_evidence": 2,
      "first_document": 2
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ETDR7A30",
      "matches": [
        [
          "full-ETDR7A30%20Technical%20Data-fd99ae9f",
          "ETDR7A30%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ETDR7A30%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ETCS0301%20Technical%20Data.pdf",
      "document_id": "full-ETCS0301%20Technical%20Data-595b4f13",
      "chunk_id": "cfc34d415a9c99eb",
      "score": 0.738901,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ETDR7A30%20Technical%20Data.pdf",
      "document_id": "full-ETDR7A30%20Technical%20Data-fd99ae9f",
      "chunk_id": "83bbcde9f1cf5952",
      "score": 0.7257961,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EHGN200318%20Technical%20Data.pdf",
      "document_id": "full-EHGN200318%20Technical%20Data-944a00c8",
      "chunk_id": "8390edb79dc569d6",
      "score": 0.6907685,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "jir%20pro%20etanche1.pdf",
      "document_id": "full-jir%20pro%20etanche1-7c9a4574",
      "chunk_id": "01f93d1eac95a9e9",
      "score": 0.68302184,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "chunk_id": "5cadd1d9038b030c",
      "score": 0.6811826,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "FULL.pdf",
      "document_id": "full-FULL-88a1b942",
      "chunk_id": "b48abcc218bcbcea",
      "score": 0.68114746,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ESHT0802%20Technical%20Data.pdf",
      "document_id": "full-ESHT0802%20Technical%20Data-e264929b",
      "chunk_id": "a1ba76c8658d7c4c",
      "score": 0.6751316,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ESHT0803%20Technical%20Data.pdf",
      "document_id": "full-ESHT0803%20Technical%20Data-280b34d0",
      "chunk_id": "4a92513c5b462822",
      "score": 0.6751316,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELAP20151%20Technical%20Data.pdf",
      "document_id": "full-ELAP20151%20Technical%20Data-640eea36",
      "chunk_id": "19a9ef39a0cf9b7e",
      "score": 0.6750516,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "chunk_id": "1427ea575d844c48",
      "score": 0.6720607,
      "section_path": [
        "MURENDUITCACHET VERT"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL21",
  "query": "La meuleuse ELAG4128112 est-elle utilisable avec de l’eau ?",
  "categories": [
    "safety/limitations"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ELAG4128112%20Technical%20Data-52718f1b",
        "file_name": "ELAG4128112%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ELAG4128112%20Technical%20Data.pdf",
        "chunk_ids": [
          "138f1d84eedd52dc"
        ],
        "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1280W Vitesse à vide : 3000/6500/10000 tr/min Diamètre du disque : 115mm"
      },
      "dense_document_rank": null,
      "dense_chunk_rank": null,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "138f1d84eedd52dc",
          "identifier": 1.0,
          "filename": 0.2,
          "idf_overlap": 0.6395213212457012,
          "numeric": 0,
          "lexical_score": 1.8395213212457011
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": null,
  "identifier_detected": [
    "ELAG4128112"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": null
    },
    "100": {
      "first_evidence": null,
      "first_document": null
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ELAG4128112",
      "matches": [
        [
          "full-ELAG4128112%20Technical%20Data-52718f1b",
          "ELAG4128112%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ELAG4128112%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "85aa3643e2d06a94",
      "score": 0.7193326,
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "a195b0a4c13f1604",
      "score": 0.7170285,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "chunk_id": "1bca5b1704c94391",
      "score": 0.7158653,
      "section_path": [],
      "block_type": "list_item"
    },
    {
      "file_name": "fiche%20Champion%204%20IN%201%20locale%201.pdf",
      "document_id": "full-fiche%20Champion%204%20IN%201%20locale%201-26006ee2",
      "chunk_id": "9971638ae796ea35",
      "score": 0.7102962,
      "section_path": [
        "CHAMPION 4 IN 1"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "chunk_id": "9572fff3d98caa9e",
      "score": 0.70865,
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "chunk_id": "5c855bad9c12198a",
      "score": 0.70105,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "primer%20contact1.pdf",
      "document_id": "full-primer%20contact1-411ec87f",
      "chunk_id": "013da106acce8f93",
      "score": 0.6993462,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "jir%20pro%20etanche1.pdf",
      "document_id": "full-jir%20pro%20etanche1-7c9a4574",
      "chunk_id": "bd3b202a7a984378",
      "score": 0.69501483,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ISBAROC-R.pdf",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "chunk_id": "bd2830ec79c8c28d",
      "score": 0.6907271,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "chunk_id": "635b48ca16bf2d25",
      "score": 0.6904613,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "list_item"
    }
  ]
}
```

```json
{
  "query_id": "BL22",
  "query": "Quelle batterie est compatible avec les outils P20S ?",
  "categories": [
    "product identification",
    "vague/general"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EBPK20011%20Technical%20Data-ac08f0ef",
        "file_name": "EBPK20011%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EBPK20011%20Technical%20Data.pdf",
        "chunk_ids": [
          "8f6935deb4a8474e"
        ],
        "substring": "Des cellules Li-Ion de haute qualité signifient pas d'effet mémoire, faible autodécharge et puissance élevée et constante\nNiveau de charge actuel indiqué par un affichage LED à 3 niveaux\nBoîtier protégé contre la poussière, la corrosion et les dommages mécaniques\nTension : batterie Lithium-ion 20 V 2,0 Ah Indicateur d'alimentation de la batterie LED Une batterie convient à tous les outils multiples P20S\nEmballé dans une boîte de couleur"
      },
      "dense_document_rank": 5,
      "dense_chunk_rank": 13,
      "lexical_rank": 4,
      "reranked_position": 4,
      "lexical_features": [
        {
          "chunk_id": "8f6935deb4a8474e",
          "identifier": 0.0,
          "filename": 0.0,
          "idf_overlap": 0.7193981054113523,
          "numeric": 0,
          "lexical_score": 0.7193981054113523
        }
      ]
    },
    {
      "expected": {
        "document_id": "full-EBPK20021%20Technical%20Data-e774e072",
        "file_name": "EBPK20021%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EBPK20021%20Technical%20Data.pdf",
        "chunk_ids": [
          "438169fa5ddf1d66"
        ],
        "substring": "Des cellules Li-Ion de haute qualité signifient aucun effet mémoire, une faible autodécharge et une puissance élevée et constante\nLe niveau de charge actuel est indiqué par un affichage LED à 3 niveaux\nBoîtier protégé contre la poussière, la corrosion et les dommages mécaniques Tension : 20 V Batterie lithium-ion 4,0 Ah\nVoyant LED de niveau de charge de la batterie Une seule batterie compatible avec tous les outils multiples P20S\nEmballé dans une boîte de couleur"
      },
      "dense_document_rank": 7,
      "dense_chunk_rank": 12,
      "lexical_rank": 1,
      "reranked_position": 3,
      "lexical_features": [
        {
          "chunk_id": "438169fa5ddf1d66",
          "identifier": 0.0,
          "filename": 0.0,
          "idf_overlap": 1.0,
          "numeric": 0,
          "lexical_score": 1.0
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 12,
  "first_correct_document_rank": 5,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 5,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 5
    },
    "20": {
      "first_evidence": 12,
      "first_document": 5
    },
    "50": {
      "first_evidence": 12,
      "first_document": 5
    },
    "100": {
      "first_evidence": 12,
      "first_document": 5
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 3,
  "diagnosis": [
    "B: correct evidence exists, below rank 10",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed",
    "ambiguous label"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ELBCPK1012%20Technical%20Data.pdf",
      "document_id": "full-ELBCPK1012%20Technical%20Data-566d4669",
      "chunk_id": "49c2b9fab7070ca8",
      "score": 0.7870142,
      "section_path": [
        "(EBPK20021)"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELBCPK2212%20Technical%20Data.pdf",
      "document_id": "full-ELBCPK2212%20Technical%20Data-9fbd74b3",
      "chunk_id": "854cec8546c7775d",
      "score": 0.78189135,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELSL203051%20Technical%20Data.pdf",
      "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
      "chunk_id": "f1837ea6d89afe65",
      "score": 0.7782988,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EFCR20403%20Technical%20Data.pdf",
      "document_id": "full-EFCR20403%20Technical%20Data-22bae915",
      "chunk_id": "e2d717e72a39fd06",
      "score": 0.76865286,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EBPK20011%20Technical%20Data.pdf",
      "document_id": "full-EBPK20011%20Technical%20Data-ac08f0ef",
      "chunk_id": "e59c4f92f0874838",
      "score": 0.7559639,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELBCPK1012%20Technical%20Data.pdf",
      "document_id": "full-ELBCPK1012%20Technical%20Data-566d4669",
      "chunk_id": "f71f4bafe77488d2",
      "score": 0.7559639,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EBPK20021%20Technical%20Data.pdf",
      "document_id": "full-EBPK20021%20Technical%20Data-e774e072",
      "chunk_id": "b1e9300f04af9b67",
      "score": 0.7513982,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELBCPK2212%20Technical%20Data.pdf",
      "document_id": "full-ELBCPK2212%20Technical%20Data-9fbd74b3",
      "chunk_id": "e40fd0d925e4e99f",
      "score": 0.7366701,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EFCR20200%20Technical%20Data.pdf",
      "document_id": "full-EFCR20200%20Technical%20Data-ba45c83b",
      "chunk_id": "a21be180a83e03d2",
      "score": 0.7234646,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EFCR20403%20Technical%20Data.pdf",
      "document_id": "full-EFCR20403%20Technical%20Data-22bae915",
      "chunk_id": "b0798255c18ecbc4",
      "score": 0.7234646,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL23",
  "query": "Quels matériaux la polisseuse ELAP20151 peut-elle polir ?",
  "categories": [
    "application/use"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ELAP20151%20Technical%20Data-640eea36",
        "file_name": "ELAP20151%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ELAP20151%20Technical%20Data.pdf",
        "chunk_ids": [
          "cc268fb57f689936"
        ],
        "substring": "L'outil électrique est destiné au polissage et au brossage des surfaces métalliques et revêtues ainsi qu'au polissage de la pierre.\nSolution sans fil pour une variété d'applications de polissage où la mobilité est importante\nPolisseuse à double action alimentée par batterie offrant une orbite aléatoire sélectionnable avec rotation forcée ou rotation libre\nLe design sans fil élimine les tracas de la gestion des câbles et les rayures accidentelles des surfaces délicates\nMolette de contrôle de vitesse variable située de manière pratique avec 6 réglages de vitesse (2000-4500 tr/min) OPM\nÉquipée de plaques de support pour tampons à boucle de 6\" Moteur sans balais Tension : 20V"
      },
      "dense_document_rank": 17,
      "dense_chunk_rank": null,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "cc268fb57f689936",
          "identifier": 1.0,
          "filename": 0.25,
          "idf_overlap": 0.5348950892305916,
          "numeric": 0,
          "lexical_score": 1.7848950892305915
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": 17,
  "identifier_detected": [
    "ELAP20151"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": 17
    },
    "50": {
      "first_evidence": null,
      "first_document": 17
    },
    "100": {
      "first_evidence": null,
      "first_document": 17
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ELAP20151",
      "matches": [
        [
          "full-ELAP20151%20Technical%20Data-640eea36",
          "ELAP20151%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ELAP20151%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "EAKB0502%20Technical%20Data.pdf",
      "document_id": "full-EAKB0502%20Technical%20Data-c80e003e",
      "chunk_id": "2acf99d82d8fb725",
      "score": 0.68343467,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EFDS1155%20Technical%20Data.pdf",
      "document_id": "full-EFDS1155%20Technical%20Data-c0f5111d",
      "chunk_id": "09b0e26afdc1a192",
      "score": 0.67007333,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EMCP5386%20Technical%20Data.pdf",
      "document_id": "full-EMCP5386%20Technical%20Data-47bc9c6f",
      "chunk_id": "86c7e980bf761112",
      "score": 0.66481805,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EFDS1154%20Technical%20Data.pdf",
      "document_id": "full-EFDS1154%20Technical%20Data-664427bd",
      "chunk_id": "026564c2d5e0523f",
      "score": 0.6597382,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EFDS1153%20Technical%20Data.pdf",
      "document_id": "full-EFDS1153%20Technical%20Data-68a834db",
      "chunk_id": "8825d9ee983b753a",
      "score": 0.6581967,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "chunk_id": "c8784751e5f68434",
      "score": 0.6573788,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "chunk_id": "e18f876b73c0bac9",
      "score": 0.6573788,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "a9d7a9a7d6342917",
      "score": 0.6573788,
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "hydromur%20R%20V4.pdf",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "chunk_id": "f9d6868075479388",
      "score": 0.6573788,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPERDUR1.pdf",
      "document_id": "full-SUPERDUR1-8aaac074",
      "chunk_id": "6c70ced802aacc1b",
      "score": 0.65721714,
      "section_path": [
        "• EN 13813  _   DTU 26-2  _  DTU 13.3 ."
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL24",
  "query": "Quel est le couple de serrage et de desserrage de ECIWL42602 ?",
  "categories": [
    "technical specifications"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ECIWL42602%20Technical%20Data-292a3638",
        "file_name": "ECIWL42602%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ECIWL42602%20Technical%20Data.pdf",
        "chunk_ids": [
          "28018b71f6582b5c"
        ],
        "substring": "La machine est destinée au vissage et au desserrage des vis et des boulons, ainsi qu’au serrage et au desserrage des écrous dans la plage de dimensions correspondante.\nLe moteur sans balais délivre un couple de serrage de 600 Nm et un couple de desserrage de 750 Nm\nInterrupteur de sélection de puissance à 3 vitesses (0-1700/0-2100 tr/min/0-2300 tr/min et 0-2400/0-2800/0-3300 coups/min) pour un contrôle précis du serrage dans une large gamme d’applications"
      },
      "dense_document_rank": 3,
      "dense_chunk_rank": 29,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "28018b71f6582b5c",
          "identifier": 1.0,
          "filename": 0.25,
          "idf_overlap": 1.0,
          "numeric": 0,
          "lexical_score": 2.25
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 29,
  "first_correct_document_rank": 3,
  "identifier_detected": [
    "ECIWL42602"
  ],
  "baseline_top10_first_document_rank": 3,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 3
    },
    "20": {
      "first_evidence": null,
      "first_document": 3
    },
    "50": {
      "first_evidence": 29,
      "first_document": 3
    },
    "100": {
      "first_evidence": 29,
      "first_document": 3
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ECIWL42602",
      "matches": [
        [
          "full-ECIWL42602%20Technical%20Data-292a3638",
          "ECIWL42602%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ECIWL42602%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "B: correct evidence exists, below rank 10",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ECIWL42461%20Technical%20Data.pdf",
      "document_id": "full-ECIWL42461%20Technical%20Data-a7e3fb17",
      "chunk_id": "6818d05d93fe2162",
      "score": 0.8282896,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ECIWL20455%20Technical%20Data.pdf",
      "document_id": "full-ECIWL20455%20Technical%20Data-791ec736",
      "chunk_id": "2219410cccc71221",
      "score": 0.75503546,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ECIWL42602%20Technical%20Data.pdf",
      "document_id": "full-ECIWL42602%20Technical%20Data-292a3638",
      "chunk_id": "9bded4c32bee3c62",
      "score": 0.7415453,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "chunk_id": "33528846f6661792",
      "score": 0.68479127,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "chunk_id": "417a91277e2fa7fb",
      "score": 0.6836415,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ECIWL42602%20Technical%20Data.pdf",
      "document_id": "full-ECIWL42602%20Technical%20Data-292a3638",
      "chunk_id": "96f5626cf4fa53f2",
      "score": 0.6808951,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "chunk_id": "8852467a2b9cee0c",
      "score": 0.6762543,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "chunk_id": "4d20acf2ffaa3626",
      "score": 0.66359186,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "chunk_id": "23b329e12ef306c3",
      "score": 0.6620687,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "1873ef801868ec6c",
      "score": 0.6619563,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL25",
  "query": "Quelles fonctions de protection possède le multimètre EDMR5110004 ?",
  "categories": [
    "safety/limitations"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EDMR5110004%20Technical%20Data-0ce60f56",
        "file_name": "EDMR5110004%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EDMR5110004%20Technical%20Data.pdf",
        "chunk_ids": [
          "ac5da251ccc4f1ba"
        ],
        "substring": "1. Modélisation spécialisée ;\n2. Affichage de la valeur efficace réelle ;\n3. Fonction Smart, reconnaissance automatique des tests de tension, résistance et continuité ;\n4. Protection intelligente contre la surchauffe, avec fonction de protection contre les surcharges, empêchant les opérations hors plage qui pourraient endommager le voltmètre et l'ampèremètre, protection complète contre les surcharges, utilisation sûre et fiable ;\n5. Coque en caoutchouc, sensation agréable au toucher Écran d'affichage couleur VA"
      },
      "dense_document_rank": null,
      "dense_chunk_rank": null,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "ac5da251ccc4f1ba",
          "identifier": 1.0,
          "filename": 0.2,
          "idf_overlap": 0.3211695461586842,
          "numeric": 0,
          "lexical_score": 1.5211695461586843
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": null,
  "identifier_detected": [
    "EDMR5110004"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": null
    },
    "100": {
      "first_evidence": null,
      "first_document": null
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "EDMR5110004",
      "matches": [
        [
          "full-EDMR5110004%20Technical%20Data-0ce60f56",
          "EDMR5110004%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\EDMR5110004%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "chunk_id": "905f7773c9625d7e",
      "score": 0.71841043,
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "chunk_id": "1721fac74c537e14",
      "score": 0.7071039,
      "section_path": [
        "CEM PRO-FLEX 100 W\nPROTECTION"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EFSD0101%20Technical%20Data.pdf",
      "document_id": "full-EFSD0101%20Technical%20Data-ee94ed3f",
      "chunk_id": "1814c7631c983f20",
      "score": 0.6897886,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EFSD0101%20Technical%20Data.pdf",
      "document_id": "full-EFSD0101%20Technical%20Data-ee94ed3f",
      "chunk_id": "6e135a1edab5c272",
      "score": 0.67327106,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "chunk_id": "32f126178b774b0b",
      "score": 0.66629803,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FULL%20ECO1.pdf",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "chunk_id": "5eca56a2e6353c0e",
      "score": 0.66578466,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "8ed2bc02e7f85eb2",
      "score": 0.66578466,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ISBAROC%20R1.pdf",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "chunk_id": "1977a381add0de0f",
      "score": 0.6643355,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "chunk_id": "281d37f692efa69a",
      "score": 0.6637959,
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "chunk_id": "2d13aad6e3293d4f",
      "score": 0.66306424,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    }
  ]
}
```

```json
{
  "query_id": "BL26",
  "query": "Quel chargeur fournit une sortie 20 V et 2 A ?",
  "categories": [
    "product identification",
    "cross-document ambiguity"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EFCR20200%20Technical%20Data-ba45c83b",
        "file_name": "EFCR20200%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EFCR20200%20Technical%20Data.pdf",
        "chunk_ids": [
          "c7e705cf2296d928"
        ],
        "substring": "Tension d'entrée : 220-240 V ~ 50/60\nHz Tension de sortie : 20 V Courant de sortie : 2 A Emballé dans une boîte de couleur."
      },
      "dense_document_rank": 3,
      "dense_chunk_rank": 3,
      "lexical_rank": 1,
      "reranked_position": 2,
      "lexical_features": [
        {
          "chunk_id": "c7e705cf2296d928",
          "identifier": 0.0,
          "filename": 0.0,
          "idf_overlap": 0.42206077295470096,
          "numeric": 1.0,
          "lexical_score": 1.422060772954701
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 3,
  "first_correct_document_rank": 3,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 3,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 3,
      "first_document": 3
    },
    "20": {
      "first_evidence": 3,
      "first_document": 3
    },
    "50": {
      "first_evidence": 3,
      "first_document": 3
    },
    "100": {
      "first_evidence": 3,
      "first_document": 3
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 2,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [
    "ambiguous label"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "EFCR20403%20Technical%20Data.pdf",
      "document_id": "full-EFCR20403%20Technical%20Data-22bae915",
      "chunk_id": "e2d717e72a39fd06",
      "score": 0.8204981,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELBCPK1012%20Technical%20Data.pdf",
      "document_id": "full-ELBCPK1012%20Technical%20Data-566d4669",
      "chunk_id": "84c1dc0ce1057dfc",
      "score": 0.7568391,
      "section_path": [
        "(EFCR20200) :"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EFCR20200%20Technical%20Data.pdf",
      "document_id": "full-EFCR20200%20Technical%20Data-ba45c83b",
      "chunk_id": "c7e705cf2296d928",
      "score": 0.7367526,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EFC1352%20Technical%20Data.pdf",
      "document_id": "full-EFC1352%20Technical%20Data-962bf90b",
      "chunk_id": "f3b576e421c404cf",
      "score": 0.7362679,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ELBCPK2212%20Technical%20Data.pdf",
      "document_id": "full-ELBCPK2212%20Technical%20Data-9fbd74b3",
      "chunk_id": "854cec8546c7775d",
      "score": 0.7073844,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELSL203051%20Technical%20Data.pdf",
      "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
      "chunk_id": "f1837ea6d89afe65",
      "score": 0.7050565,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ECIWL20455%20Technical%20Data.pdf",
      "document_id": "full-ECIWL20455%20Technical%20Data-791ec736",
      "chunk_id": "369529d501d6a52d",
      "score": 0.6996567,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ELBCPK2212%20Technical%20Data.pdf",
      "document_id": "full-ELBCPK2212%20Technical%20Data-9fbd74b3",
      "chunk_id": "6b06ef782e51762d",
      "score": 0.69936985,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ELAP20151%20Technical%20Data.pdf",
      "document_id": "full-ELAP20151%20Technical%20Data-640eea36",
      "chunk_id": "19a9ef39a0cf9b7e",
      "score": 0.69531715,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ELSL203051%20Technical%20Data.pdf",
      "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
      "chunk_id": "e5f78778d3c8ba00",
      "score": 0.69312805,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    }
  ]
}
```

```json
{
  "query_id": "BL27",
  "query": "Quelles sont les dimensions et la matière de l’arroseur ESNE13602 ?",
  "categories": [
    "dimensions"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ESNE13602%20Technical%20Data-608a536b",
        "file_name": "ESNE13602%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ESNE13602%20Technical%20Data.pdf",
        "chunk_ids": [
          "026697171fe34411"
        ],
        "substring": "Tête d'arroseur plastique Auto Gear Adaptateur d'outil 3/4\"\nPique en plastique à 3 broches Avec fonction rotative à 360° Réglez librement les portées/distance à ajuster Dimensions : 38*17,4*6,4 cm Composition matérielle : ABS+PP\nEmballé avec un cintre en papier"
      },
      "dense_document_rank": null,
      "dense_chunk_rank": null,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "026697171fe34411",
          "identifier": 1.0,
          "filename": 0.2,
          "idf_overlap": 0.6736838588985803,
          "numeric": 0,
          "lexical_score": 1.8736838588985802
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": null,
  "identifier_detected": [
    "ESNE13602"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": null
    },
    "100": {
      "first_evidence": null,
      "first_document": null
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ESNE13602",
      "matches": [
        [
          "full-ESNE13602%20Technical%20Data-608a536b",
          "ESNE13602%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ESNE13602%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ETCS0402%20Technical%20Data.pdf",
      "document_id": "full-ETCS0402%20Technical%20Data-a72c933b",
      "chunk_id": "4b3eb9c29133ad5a",
      "score": 0.74935126,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ETCS0301%20Technical%20Data.pdf",
      "document_id": "full-ETCS0301%20Technical%20Data-595b4f13",
      "chunk_id": "67ea3227ec08a7c0",
      "score": 0.7381302,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ENAL02271%20Technical%20Data.pdf",
      "document_id": "full-ENAL02271%20Technical%20Data-01ea6a48",
      "chunk_id": "d8ba72c03f7231e5",
      "score": 0.71017146,
      "section_path": [
        "ELCNLI9008, ELCNLI420602,\nELCNLI420602-4, ULCNLI9008,\nULCNLI420602"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ETBXS0301%20Technical%20Data.pdf",
      "document_id": "full-ETBXS0301%20Technical%20Data-c31b0c71",
      "chunk_id": "d50e0a110205194a",
      "score": 0.7041142,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ETCS0402%20Technical%20Data.pdf",
      "document_id": "full-ETCS0402%20Technical%20Data-a72c933b",
      "chunk_id": "33a5f2aa938de2e5",
      "score": 0.7025352,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMPN1023%20Technical%20Data.pdf",
      "document_id": "full-EMPN1023%20Technical%20Data-75f2148e",
      "chunk_id": "fb75847815d7ff3a",
      "score": 0.701236,
      "section_path": [
        "PVC"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "SUPERDUR1.pdf",
      "document_id": "full-SUPERDUR1-8aaac074",
      "chunk_id": "c389be24d0842850",
      "score": 0.7008233,
      "section_path": [
        "NB :"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EFSD0101%20Technical%20Data.pdf",
      "document_id": "full-EFSD0101%20Technical%20Data-ee94ed3f",
      "chunk_id": "2254331a64e79ed3",
      "score": 0.69843054,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ECSS11202%20Technical%20Data.pdf",
      "document_id": "full-ECSS11202%20Technical%20Data-bd3ef150",
      "chunk_id": "3be0016313579fee",
      "score": 0.69483817,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ETCS0701%20Technical%20Data.pdf",
      "document_id": "full-ETCS0701%20Technical%20Data-2f79a4f6",
      "chunk_id": "f0b24f138d33128a",
      "score": 0.6938468,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL28",
  "query": "Quelle énergie d’impact offre le perforateur ERHRP1801 ?",
  "categories": [
    "technical specifications",
    "highly specific"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
        "file_name": "ERHRP1801%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
        "chunk_ids": [
          "02dd0774ee118fee"
        ],
        "substring": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :"
      },
      "dense_document_rank": 2,
      "dense_chunk_rank": 3,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "02dd0774ee118fee",
          "identifier": 1.0,
          "filename": 0.16666666666666666,
          "idf_overlap": 0.5758681380300269,
          "numeric": 0,
          "lexical_score": 1.7425348046966935
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 3,
  "first_correct_document_rank": 2,
  "identifier_detected": [
    "ERHRP1801"
  ],
  "baseline_top10_first_document_rank": 2,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": 3,
      "first_document": 2
    },
    "20": {
      "first_evidence": 3,
      "first_document": 2
    },
    "50": {
      "first_evidence": 3,
      "first_document": 2
    },
    "100": {
      "first_evidence": 3,
      "first_document": 2
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ERHRP1801",
      "matches": [
        [
          "full-ERHRP1801%20Technical%20Data-111b1cac",
          "ERHRP1801%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "Correct evidence in dense top 10"
  ],
  "failure_groups": [],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ELSL203051%20Technical%20Data.pdf",
      "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
      "chunk_id": "f1837ea6d89afe65",
      "score": 0.69484335,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ERHRP1801%20Technical%20Data.pdf",
      "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
      "chunk_id": "0471f9362d12a62c",
      "score": 0.6854533,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ERHRP1801%20Technical%20Data.pdf",
      "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
      "chunk_id": "02dd0774ee118fee",
      "score": 0.6753347,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ISBAROC%20R1.pdf",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "chunk_id": "420c604d14aa7f2f",
      "score": 0.65942436,
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "ELAP20151%20Technical%20Data.pdf",
      "document_id": "full-ELAP20151%20Technical%20Data-640eea36",
      "chunk_id": "19a9ef39a0cf9b7e",
      "score": 0.65513754,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "EMRM1101%20Technical%20Data.pdf",
      "document_id": "full-EMRM1101%20Technical%20Data-f64d1947",
      "chunk_id": "29b7f908a5e3484a",
      "score": 0.6526922,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ELRH422682%20Technical%20Data.pdf",
      "document_id": "full-ELRH422682%20Technical%20Data-eee6a320",
      "chunk_id": "b441e6b4b59ed803",
      "score": 0.64726716,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMGG3550%20Technical%20Data.pdf",
      "document_id": "full-EMGG3550%20Technical%20Data-56663801",
      "chunk_id": "206c31312a3662f2",
      "score": 0.6472602,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "SUPLATEX1.pdf",
      "document_id": "full-SUPLATEX1-c1a35954",
      "chunk_id": "e92081f5dd50c95e",
      "score": 0.6466861,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "chunk_id": "9e1c3c2d68230178",
      "score": 0.6436972,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "list_item"
    }
  ]
}
```

```json
{
  "query_id": "BL29",
  "query": "Quelle est l’épaisseur maximale de coupe du découpeur ECUT451 ?",
  "categories": [
    "technical specifications"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-ECUT451%20Technical%20Data-d6d7ef3d",
        "file_name": "ECUT451%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ECUT451%20Technical%20Data.pdf",
        "chunk_ids": [
          "bcdeb2a5098c19e0"
        ],
        "substring": "Tension d'entrée (V) : 1~220-240 Fréquence (Hz) : 50/60\nCourant de sortie (A) : 15-40A Épaisseur de coupe : ≤12mm\nCycle de service (%) : 40%\nTension à vide (V) : 400"
      },
      "dense_document_rank": 63,
      "dense_chunk_rank": null,
      "lexical_rank": 2,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "bcdeb2a5098c19e0",
          "identifier": 1.0,
          "filename": 0.16666666666666666,
          "idf_overlap": 0.48612193992810054,
          "numeric": 0,
          "lexical_score": 1.6527886065947672
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": 63,
  "identifier_detected": [
    "ECUT451"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": null
    },
    "100": {
      "first_evidence": null,
      "first_document": 63
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "ECUT451",
      "matches": [
        [
          "full-ECUT451%20Technical%20Data-d6d7ef3d",
          "ECUT451%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\ECUT451%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 2,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "EMCT14006%20Technical%20Data.pdf",
      "document_id": "full-EMCT14006%20Technical%20Data-488d023a",
      "chunk_id": "e991da9bb634f90b",
      "score": 0.77494717,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "chunk_id": "c8784751e5f68434",
      "score": 0.6987726,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "chunk_id": "e18f876b73c0bac9",
      "score": 0.6987726,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "a9d7a9a7d6342917",
      "score": 0.6987726,
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "hydromur%20R%20V4.pdf",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "chunk_id": "f9d6868075479388",
      "score": 0.6987726,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EMSX3607%20Technical%20Data.pdf",
      "document_id": "full-EMSX3607%20Technical%20Data-d637e478",
      "chunk_id": "0a6d2f00aa55f5f5",
      "score": 0.69452506,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EACD101151%20Technical%20Data.pdf",
      "document_id": "full-EACD101151%20Technical%20Data-d7905468",
      "chunk_id": "573d97d7514ced5b",
      "score": 0.69276506,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ECSW1852%20Technical%20Data.pdf",
      "document_id": "full-ECSW1852%20Technical%20Data-c3aa9e19",
      "chunk_id": "9c77702218b75b91",
      "score": 0.6848758,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ESHT0801%20Technical%20Data.pdf",
      "document_id": "full-ESHT0801%20Technical%20Data-630b5958",
      "chunk_id": "b1739552fd4b144c",
      "score": 0.67393637,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EWPPJ15001%20Technical%20Data.pdf",
      "document_id": "full-EWPPJ15001%20Technical%20Data-6b64b909",
      "chunk_id": "9825ac72eae8b138",
      "score": 0.67080295,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    }
  ]
}
```

```json
{
  "query_id": "BL30",
  "query": "À quoi sert la plaque vibrante EPCT091611 ?",
  "categories": [
    "application/use"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EPCT091611%20Technical%20Data-04f35074",
        "file_name": "EPCT091611%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EPCT091611%20Technical%20Data.pdf",
        "chunk_ids": [
          "bc8f9e9b6d4111f6"
        ],
        "substring": "Convient pour la réparation des chaussées en sable, gravier et sols mélangés dans les travaux municipaux.\nAvancement bidirectionnel réversible.\nPosition d'opération modérée.\nLes grands supports d'amortissement réduisent les vibrations de la poignée.\nLes supports d'amortissement lourds réduisent les vibrations du pont supérieur.\nLa plaque inférieure résistante à l'usure prolonge la durée de vie, conception ouverte, réduit la saleté de construction.\nLa tige de levage en position centrale facilite l'entrée et la sortie des tranchées.\nUtilisation de la puissance Honda, pour une durée de vie plus longue du produit et une qualité plus garantie."
      },
      "dense_document_rank": null,
      "dense_chunk_rank": null,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "bc8f9e9b6d4111f6",
          "identifier": 1.0,
          "filename": 0.25,
          "idf_overlap": 0.4431978717058342,
          "numeric": 0,
          "lexical_score": 1.6931978717058342
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": null,
  "identifier_detected": [
    "EPCT091611"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": null
    },
    "100": {
      "first_evidence": null,
      "first_document": null
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "EPCT091611",
      "matches": [
        [
          "full-EPCT091611%20Technical%20Data-04f35074",
          "EPCT091611%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\EPCT091611%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ECSPAR151%20Technical%20Data.pdf",
      "document_id": "full-ECSPAR151%20Technical%20Data-aae71fc4",
      "chunk_id": "eef8ef55c9da5192",
      "score": 0.7048718,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "chunk_id": "9fc104a0b3b85789",
      "score": 0.70088565,
      "section_path": [
        "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "chunk_id": "24e981c191415fd0",
      "score": 0.70088565,
      "section_path": [
        "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "chunk_id": "c8784751e5f68434",
      "score": 0.6988242,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "chunk_id": "e18f876b73c0bac9",
      "score": 0.6988242,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "a9d7a9a7d6342917",
      "score": 0.6988242,
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "hydromur%20R%20V4.pdf",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "chunk_id": "f9d6868075479388",
      "score": 0.6988242,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "chunk_id": "f5bc6a620d7fbdcf",
      "score": 0.69630647,
      "section_path": [
        "• EN 16-566  - NFT 36-005 - DTU 59.1 - DTU 59.4"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "FINACEM BLEU_compressed.pdf",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "chunk_id": "dd56a78e94abbae4",
      "score": 0.68082476,
      "section_path": [],
      "block_type": "paragraph"
    },
    {
      "file_name": "ISBAROC-R.pdf",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "chunk_id": "3a6d98456c6ca487",
      "score": 0.68082476,
      "section_path": [
        "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL31",
  "query": "Quel diamètre de lame utilise la scie EMCT14006 ?",
  "categories": [
    "dimensions",
    "highly specific"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EMCT14006%20Technical%20Data-488d023a",
        "file_name": "EMCT14006%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EMCT14006%20Technical%20Data.pdf",
        "chunk_ids": [
          "7bd6cf9f6febf5fd"
        ],
        "substring": "Tension : 220-240V~50/60Hz Puissance d'entrée : 1400W\nVitesse à vide : 13000 tr/min\nDiamètre de la lame : 110x20mm"
      },
      "dense_document_rank": 45,
      "dense_chunk_rank": 45,
      "lexical_rank": 1,
      "reranked_position": 1,
      "lexical_features": [
        {
          "chunk_id": "7bd6cf9f6febf5fd",
          "identifier": 1.0,
          "filename": 0.2,
          "idf_overlap": 0.5968505775718932,
          "numeric": 0,
          "lexical_score": 1.7968505775718933
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 45,
  "first_correct_document_rank": 45,
  "identifier_detected": [
    "EMCT14006"
  ],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": 45,
      "first_document": 45
    },
    "100": {
      "first_evidence": 45,
      "first_document": 45
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "EMCT14006",
      "matches": [
        [
          "full-EMCT14006%20Technical%20Data-488d023a",
          "EMCT14006%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\EMCT14006%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": 1,
  "diagnosis": [
    "B: correct evidence exists, below rank 10"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ENAL02271%20Technical%20Data.pdf",
      "document_id": "full-ENAL02271%20Technical%20Data-01ea6a48",
      "chunk_id": "d8ba72c03f7231e5",
      "score": 0.70098114,
      "section_path": [
        "ELCNLI9008, ELCNLI420602,\nELCNLI420602-4, ULCNLI9008,\nULCNLI420602"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EACD101251%20Technical%20Data.pdf",
      "document_id": "full-EACD101251%20Technical%20Data-92d8d9e6",
      "chunk_id": "a0e67c2d1d801bcc",
      "score": 0.6971492,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EWPB25402%20Technical%20Data.pdf",
      "document_id": "full-EWPB25402%20Technical%20Data-526dd71a",
      "chunk_id": "c43160cf417aa9c2",
      "score": 0.6922772,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMSX3607%20Technical%20Data.pdf",
      "document_id": "full-EMSX3607%20Technical%20Data-d637e478",
      "chunk_id": "f08a596bdf109b15",
      "score": 0.6898756,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMHY2525%20Technical%20Data.pdf",
      "document_id": "full-EMHY2525%20Technical%20Data-01e7534e",
      "chunk_id": "79c71be2a3987ebd",
      "score": 0.6892079,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EFC1352%20Technical%20Data.pdf",
      "document_id": "full-EFC1352%20Technical%20Data-962bf90b",
      "chunk_id": "3f24b579c6bd1fb5",
      "score": 0.6880359,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "EMPT5310%20Technical%20Data.pdf",
      "document_id": "full-EMPT5310%20Technical%20Data-ce01c4d1",
      "chunk_id": "ac1aec7cae2f4797",
      "score": 0.6846757,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMPT5314%20Technical%20Data.pdf",
      "document_id": "full-EMPT5314%20Technical%20Data-11df53a7",
      "chunk_id": "1bae82a143fd7be8",
      "score": 0.6846757,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMPT5318%20Technical%20Data.pdf",
      "document_id": "full-EMPT5318%20Technical%20Data-8fba4034",
      "chunk_id": "564738d07f5294f3",
      "score": 0.6846757,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EMPT5324%20Technical%20Data.pdf",
      "document_id": "full-EMPT5324%20Technical%20Data-d30719e7",
      "chunk_id": "f776a92d526eb283",
      "score": 0.6846757,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    }
  ]
}
```

```json
{
  "query_id": "BL32",
  "query": "Quelle est la température maximale du décapeur thermique EHGN200318 ?",
  "categories": [
    "technical specifications"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-EHGN200318%20Technical%20Data-944a00c8",
        "file_name": "EHGN200318%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EHGN200318%20Technical%20Data.pdf",
        "chunk_ids": [
          "3aa2c41cf26d5229"
        ],
        "substring": "1. Élément chauffant à longue durée de vie\n2. Peut être utilisé en position inversée\n3. Divers accessoires adaptés à différents scénarios de travail\n4. Réglage en 2 niveaux du débit d'air, vitesse du vent, température maximale jusqu'à 550℃, vitesse maximale jusqu'à 200L/min\n5. Coque et poignée de conception développée, prise en main confortable\n6. Équipé de 2 batteries 5.0Ah, chargeur 4A, grande autonomie\n7. Affichage numérique LCD, surveillance en temps réel de la température de travail\n8. Corps principal et gaine du tuyau d'air séparables, protection contre les brûlures lors du Tension : 20V Température : 30-300℃/30-550°C"
      },
      "dense_document_rank": 7,
      "dense_chunk_rank": null,
      "lexical_rank": 1,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "3aa2c41cf26d5229",
          "identifier": 1.0,
          "filename": 0.2,
          "idf_overlap": 0.5554422916655268,
          "numeric": 0,
          "lexical_score": 1.7554422916655268
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": 7,
  "identifier_detected": [
    "EHGN200318"
  ],
  "baseline_top10_first_document_rank": 7,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 7
    },
    "20": {
      "first_evidence": null,
      "first_document": 7
    },
    "50": {
      "first_evidence": null,
      "first_document": 7
    },
    "100": {
      "first_evidence": null,
      "first_document": 7
    }
  },
  "identifier_expected_source_match": [
    {
      "identifier": "EHGN200318",
      "matches": [
        [
          "full-EHGN200318%20Technical%20Data-944a00c8",
          "EHGN200318%20Technical%20Data.pdf",
          "ai_data\\raw\\emtop\\EHGN200318%20Technical%20Data.pdf"
        ]
      ],
      "matches_expected": true,
      "unambiguous": true
    }
  ],
  "exact_identifier_route_correct_unambiguously": true,
  "lexical_first_evidence_rank": 1,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "identifier failure",
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "EMCT14006%20Technical%20Data.pdf",
      "document_id": "full-EMCT14006%20Technical%20Data-488d023a",
      "chunk_id": "e991da9bb634f90b",
      "score": 0.71227306,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Adhércol P-3000_Compressed.pdf",
      "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
      "chunk_id": "c7d781378e50fe20",
      "score": 0.70979303,
      "section_path": [],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA%20FINA1.pdf",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "chunk_id": "502a7a1d14f9cb60",
      "score": 0.7094482,
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "jir%20pro%20etanche1.pdf",
      "document_id": "full-jir%20pro%20etanche1-7c9a4574",
      "chunk_id": "7d8fc4841658d043",
      "score": 0.7094482,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "PISCINE%20V4.pdf",
      "document_id": "full-PISCINE%20V4-18fdf73d",
      "chunk_id": "fb433c94e993ae18",
      "score": 0.6939846,
      "section_path": [
        "• NF EN 12004 : 2017-04  _ DTU 52.1     _  DTU 52.2"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EWPPQD07501%20Technical%20Data.pdf",
      "document_id": "full-EWPPQD07501%20Technical%20Data-3fe10d3d",
      "chunk_id": "f02856f7fc445e6d",
      "score": 0.69187415,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "EHGN200318%20Technical%20Data.pdf",
      "document_id": "full-EHGN200318%20Technical%20Data-944a00c8",
      "chunk_id": "bc48f2deeee36208",
      "score": 0.6908001,
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "PRO%20200%20V4.pdf",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "chunk_id": "8f2158ae8ee24c8c",
      "score": 0.6904454,
      "section_path": [
        "NPD"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "chunk_id": "9e8b19cd5618f195",
      "score": 0.6879507,
      "section_path": [
        "• EN 16-566  - NFT 36-005 - DTU 59.1 - DTU 59.4"
      ],
      "block_type": "key_value"
    },
    {
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "chunk_id": "476149dfe6334e61",
      "score": 0.6879507,
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "block_type": "key_value"
    }
  ]
}
```

```json
{
  "query_id": "BL33",
  "query": "Quelle consommation prévoir pour SUPLATEX en mortier et en produit de cure ?",
  "categories": [
    "consumption"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-SUPLATEX1-c1a35954",
        "file_name": "SUPLATEX1.pdf",
        "source_path": "ai_data\\raw\\sofap\\SUPLATEX1.pdf",
        "chunk_ids": [
          "3ffbfb4c1ebb40d8"
        ],
        "substring": "• En couche d'accrochage (gobeƟs, barboƟne) : environ 0,120 L / m².\n• En morƟer : environ 0,600 L / m².\n• En primaire : de 80 g à 150 g/m² environ selon la nature du support.\n• En produit de cure : 150 g/m² environ."
      },
      "dense_document_rank": 3,
      "dense_chunk_rank": null,
      "lexical_rank": 3,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "3ffbfb4c1ebb40d8",
          "identifier": 0.0,
          "filename": 0.0,
          "idf_overlap": 0.28359871002659326,
          "numeric": 0,
          "lexical_score": 0.28359871002659326
        }
      ]
    }
  ],
  "first_correct_evidence_rank": null,
  "first_correct_document_rank": 3,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": 3,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": 3
    },
    "20": {
      "first_evidence": null,
      "first_document": 3
    },
    "50": {
      "first_evidence": null,
      "first_document": 3
    },
    "100": {
      "first_evidence": null,
      "first_document": 3
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 3,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "A: no correct evidence in dense top 100",
    "C: expected document in top 10, evidence chunk missed"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "SUPROTEC1.pdf",
      "document_id": "full-SUPROTEC1-ed82cb2d",
      "chunk_id": "dbaeb71b87e6dae7",
      "score": 0.78468585,
      "section_path": [
        "•  NF P 18 - 370."
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPERDUR1.pdf",
      "document_id": "full-SUPERDUR1-8aaac074",
      "chunk_id": "0e0eca26ad164a45",
      "score": 0.7411128,
      "section_path": [
        "NB :"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "SUPLATEX1.pdf",
      "document_id": "full-SUPLATEX1-c1a35954",
      "chunk_id": "e92081f5dd50c95e",
      "score": 0.73831093,
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "block_type": "list_item"
    },
    {
      "file_name": "SUPROTEC1.pdf",
      "document_id": "full-SUPROTEC1-ed82cb2d",
      "chunk_id": "7bb8f3db5f050597",
      "score": 0.72329533,
      "section_path": [
        "•  NF P 18 - 370."
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "chunk_id": "eb7841c9c9e0e217",
      "score": 0.70378894,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA-FINA.pdf",
      "document_id": "full-LIKA-FINA-69544727",
      "chunk_id": "acdf78a4d48714ac",
      "score": 0.70252883,
      "section_path": [
        "GESCRIPTION PROBUIT —  LESPLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "LIKA-FINA.pdf",
      "document_id": "full-LIKA-FINA-69544727",
      "chunk_id": "817400302cb13fa3",
      "score": 0.70252883,
      "section_path": [
        "GESCRIPTION PROBUIT —  LESPLUS PRODUIT"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FULL.pdf",
      "document_id": "full-FULL-88a1b942",
      "chunk_id": "076493283f1e2307",
      "score": 0.6999816,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "4f162e079b3b2090",
      "score": 0.6999816,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Pro 2000_Compressed.pdf",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "chunk_id": "469965daeffd0606",
      "score": 0.6999816,
      "section_path": [
        "PRO 2000"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

```json
{
  "query_id": "BL34",
  "query": "Comment réaliser l’encollage du carrelage avec SOFAPCOL CONFORT ?",
  "categories": [
    "preparation/application instructions",
    "standards/norms"
  ],
  "expected_units": [
    {
      "expected": {
        "document_id": "full-CONFORT%20V4-577b657d",
        "file_name": "CONFORT%20V4.pdf",
        "source_path": "ai_data\\raw\\sofap\\CONFORT%20V4.pdf",
        "chunk_ids": [
          "3b667fd34f972c32"
        ],
        "substring": "•  Appliquer le morƟer colle sur le support avec une taloche, puis l’épaisseur du morƟer colle sera réglée avec la spatule crantée adaptée à la dimension et au relief des carreaux.\n• Dans certains cas, la pose doit être eﬀectuée par double encollage (se référer au DTU 52.2)."
      },
      "dense_document_rank": 4,
      "dense_chunk_rank": 61,
      "lexical_rank": 5,
      "reranked_position": null,
      "lexical_features": [
        {
          "chunk_id": "3b667fd34f972c32",
          "identifier": 0.0,
          "filename": 0.16666666666666666,
          "idf_overlap": 0.3995823911688766,
          "numeric": 0,
          "lexical_score": 0.5662490578355432
        }
      ]
    }
  ],
  "first_correct_evidence_rank": 61,
  "first_correct_document_rank": 4,
  "identifier_detected": [],
  "baseline_top10_first_document_rank": null,
  "dense_ranks_by_k": {
    "10": {
      "first_evidence": null,
      "first_document": null
    },
    "20": {
      "first_evidence": null,
      "first_document": null
    },
    "50": {
      "first_evidence": null,
      "first_document": 4
    },
    "100": {
      "first_evidence": 61,
      "first_document": 4
    }
  },
  "identifier_expected_source_match": [],
  "exact_identifier_route_correct_unambiguously": false,
  "lexical_first_evidence_rank": 5,
  "reranked_first_evidence_position": null,
  "diagnosis": [
    "B: correct evidence exists, below rank 10"
  ],
  "failure_groups": [
    "semantic embedding failure",
    "source-document found but evidence chunk missed"
  ],
  "near_duplicate_sources": [],
  "dense_top10": [
    {
      "file_name": "ECO%20COLLE%20V4.pdf",
      "document_id": "full-ECO%20COLLE%20V4-b4db0cfb",
      "chunk_id": "4d02781e07590fd1",
      "score": 0.7136535,
      "section_path": [
        "NPD"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Pro 3000_Compressed.pdf",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "chunk_id": "00a464bde031d6cf",
      "score": 0.71147454,
      "section_path": [
        "PRO 3000"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "FULL.pdf",
      "document_id": "full-FULL-88a1b942",
      "chunk_id": "076493283f1e2307",
      "score": 0.7082488,
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "chunk_id": "d38d4c7e9cdb9a97",
      "score": 0.7082488,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "ISBAROC%20R1.pdf",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "chunk_id": "59e9f770b19d7730",
      "score": 0.7082488,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "chunk_id": "924ba4a85a9bdb99",
      "score": 0.7082488,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "POOL%20V2.pdf",
      "document_id": "full-POOL%20V2-9db8b280",
      "chunk_id": "4f162e079b3b2090",
      "score": 0.7082488,
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "PRO%201000%20V2.pdf",
      "document_id": "full-PRO%201000%20V2-467bc232",
      "chunk_id": "b4a5c0f90e01dd84",
      "score": 0.7082488,
      "section_path": [
        "• NF EN 12004 : 2017-04   _  DTU 52.1  _ DTU 52.2"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "Pro 2000_Compressed.pdf",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "chunk_id": "469965daeffd0606",
      "score": 0.7082488,
      "section_path": [
        "PRO 2000"
      ],
      "block_type": "paragraph"
    },
    {
      "file_name": "SUPERLITE1.pdf",
      "document_id": "full-SUPERLITE1-8227dad4",
      "chunk_id": "3b57ed57aadd8934",
      "score": 0.7082488,
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "block_type": "paragraph"
    }
  ]
}
```

## Complete reranking grid

Each row reports selection metrics at K=3 and Hit@1; selected scheme's four-K metrics appear above.

```json
[
  {
    "weights": [
      0,
      0.5,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7292972982352941,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.1,
      0.5,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7288181649019608,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.25,
      0.5,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7288181649019608,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0,
      0.5,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260104828431373,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.5,
      0.5,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7288181649019608,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.1,
      0.5,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260104828431373,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.25,
      0.5,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260104828431373,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.5,
      0.5,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260104828431373,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      1,
      0.5,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7288181649019608,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      1,
      0.5,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4803921568627451,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260104828431373,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0,
      0.5,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7304848300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0,
      0.5,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7304848300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.1,
      0.5,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.1,
      0.5,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.25,
      0.5,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.25,
      0.5,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0,
      0.5,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.5,
      0.5,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0,
      0.5,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.1,
      0.5,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.5,
      0.5,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.1,
      0.5,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.25,
      0.5,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.25,
      0.5,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.5,
      0.5,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      1,
      0.5,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.5,
      0.5,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      1,
      0.5,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      1,
      0.5,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      1,
      0.5,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.47549019607843135,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7271980147058823,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.4117647058823529
  },
  {
    "weights": [
      0.1,
      0,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293428499019607,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.1,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7281967054901961,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.25,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7307423423529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7278978057843137,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.25,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7288181649019608,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.1,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7281967054901961,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7275251742156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.25,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7288181649019608,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7278978057843137,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.1,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7275251742156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260801300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.1,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7281967054901961,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.1,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260801300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.25,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272703438235294,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260801300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.25,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7288181649019608,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.25,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7258252997058824,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.1,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260801300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.25,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7258252997058824,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260801300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7278978057843137,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.1,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260801300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.1,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7281967054901961,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.25,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7258252997058824,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.25,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7288181649019608,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260801300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.1,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7260801300980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.25,
      1,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46568627450980393,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7258252997058824,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.731264425882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7305303817647059,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.1,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293842373529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.25,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319298742156862,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7298193817647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.1,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293842373529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.25,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319298742156862,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.25,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7290853376470589,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.1,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293842373529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.25,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.1,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293842373529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7287127060784314,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.25,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7298193817647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7287127060784314,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.1,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7287127060784314,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.25,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7290853376470589,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.1,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293842373529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.1,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7287127060784314,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.1,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.1,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293842373529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.25,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7284578756862745,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.25,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.1,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0.25,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7284578756862745,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.25,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7270128315686275,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.1,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.25,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.1,
      0.25,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7270128315686275,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.1,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.25,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7270128315686275,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7298193817647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.25,
      0.25,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7270128315686275,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.1,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7290853376470589,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.1,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293842373529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.1,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.1,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7293842373529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.25,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7270128315686275,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.25,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0.5,
      0.25,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7270128315686275,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.25,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7300056967647058,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.1,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.1,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7272676619607843,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.25,
      1,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7270128315686275,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      1,
      0.25,
      1,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.46078431372549017,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7270128315686275,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.38235294117647056
  },
  {
    "weights": [
      0,
      0,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.45098039215686275,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7298219832352941,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.1,
      0.5,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.45098039215686275,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7301208829411765,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.5,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.45098039215686275,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7326766492156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.5,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.45098039215686275,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7307524717647059,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.5,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.45098039215686275,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7307524717647059,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.5,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.45098039215686275,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7307524717647059,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.5,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.45098039215686275,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7307524717647059,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7317435592156862,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7310095150980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.1,
      0.5,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7313084148039216,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.1,
      0.5,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7313084148039216,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.1,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7330386142156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.5,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7337856070588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.5,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7337856070588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.25,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7308446942156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.5,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7318614296078432,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.1,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7315935700980393,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.5,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7318614296078432,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.25,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7308446942156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.5,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7318614296078432,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.5,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7318614296078432,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.1,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7315935700980393,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.25,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7308446942156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.5,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7318614296078432,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.5,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7318614296078432,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.1,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7315935700980393,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.25,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7308446942156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.5,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7318614296078432,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.5,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.44607843137254904,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7318614296078432,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.1,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7348816161764706,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.1,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7341475720588235,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.25,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319536520588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.1,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7334365720588235,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.25,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319536520588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.1,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7327025279411765,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.25,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7327688716666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.25,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319536520588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0.25,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319536520588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.1,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7334365720588235,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.1,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7327025279411765,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.25,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319536520588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0.25,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319536520588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.1,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7334365720588235,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.1,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7327025279411765,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.25,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319536520588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0.25,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4411764705882353,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.7319536520588236,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.25,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4362745098039216,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.733877829509804,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.25,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5588235294117647,
      "reciprocal_rank": 0.4362745098039216,
      "document_recall": 0.7352941176470589,
      "exact_evidence_recall": 0.5294117647058824,
      "substring_evidence_recall": 0.5294117647058824,
      "evidence_recall": 0.5294117647058824,
      "average_returned_score": 0.733877829509804,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.43137254901960786,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7317797999019607,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.43137254901960786,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7317797999019607,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.43137254901960786,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7317797999019607,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4264705882352941,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7341609992156862,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.1,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4264705882352941,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7343071210784313,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4264705882352941,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7332248440196079,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.25,
      0,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4264705882352941,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.732888757745098,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4264705882352941,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7341609992156862,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.5,
      0,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4264705882352941,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.732888757745098,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4264705882352941,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7341609992156862,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      1,
      0,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4264705882352941,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.732888757745098,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.1,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4215686274509804,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7361501230392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4215686274509804,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7356060433333333,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0.1,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4215686274509804,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7354160789215686,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5294117647058824,
      "reciprocal_rank": 0.4215686274509804,
      "document_recall": 0.7058823529411765,
      "exact_evidence_recall": 0.5,
      "substring_evidence_recall": 0.5,
      "evidence_recall": 0.5,
      "average_returned_score": 0.7343338018627451,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0,
      0.25,
      0.25
    ],
    "metrics": {
      "hit": 0.5,
      "reciprocal_rank": 0.4166666666666667,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.47058823529411764,
      "substring_evidence_recall": 0.47058823529411764,
      "evidence_recall": 0.47058823529411764,
      "average_returned_score": 0.7344933508823529,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0,
      0.25,
      0
    ],
    "metrics": {
      "hit": 0.5,
      "reciprocal_rank": 0.4117647058823529,
      "document_recall": 0.6470588235294118,
      "exact_evidence_recall": 0.47058823529411764,
      "substring_evidence_recall": 0.47058823529411764,
      "evidence_recall": 0.47058823529411764,
      "average_returned_score": 0.7368745501960784,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0,
      0,
      0.25,
      0.1
    ],
    "metrics": {
      "hit": 0.5,
      "reciprocal_rank": 0.4117647058823529,
      "document_recall": 0.6764705882352942,
      "exact_evidence_recall": 0.47058823529411764,
      "substring_evidence_recall": 0.47058823529411764,
      "evidence_recall": 0.47058823529411764,
      "average_returned_score": 0.7356023087254902,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.35294117647058826
  },
  {
    "weights": [
      0.1,
      0.25,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.37254901960784315,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7362284727450981,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.25,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.37254901960784315,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7362284727450981,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0.5,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.37254901960784315,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7347141856862746,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.5,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.37254901960784315,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7347141856862746,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.25,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.37254901960784315,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7362284727450981,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.5,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.37254901960784315,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7347141856862746,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.25,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.37254901960784315,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7362284727450981,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.5,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.37254901960784315,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7347141856862746,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0.25,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7373374305882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0.25,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7373374305882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.25,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7373374305882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0.5,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7358231435294118,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.25,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7373374305882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0.5,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7358231435294118,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.5,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7358231435294118,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.25,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7373374305882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.5,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7358231435294118,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.25,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7373374305882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.5,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7358231435294118,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.5,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7358231435294118,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.25,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7373374305882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.25,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7373374305882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.5,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7358231435294118,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.5,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4411764705882353,
      "reciprocal_rank": 0.36764705882352944,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.4264705882352941,
      "substring_evidence_recall": 0.4264705882352941,
      "evidence_recall": 0.4264705882352941,
      "average_returned_score": 0.7358231435294118,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0,
      0.5,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3627450980392157,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7369719592156863,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0,
      0.5,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35784313725490197,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7380809170588235,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35784313725490197,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7373501537254902,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0,
      0.5,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35784313725490197,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7380809170588235,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.1,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35784313725490197,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7368966451960784,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35784313725490197,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7373501537254902,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.1,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35784313725490197,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7368966451960784,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35784313725490197,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7373501537254902,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.1,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35784313725490197,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7368966451960784,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7397313530392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7384591115686274,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.1,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7392778445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.1,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7380056030392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7397313530392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7384591115686274,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.1,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7392778445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.5,
      0.1,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7380056030392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7397313530392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7384591115686274,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.1,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7392778445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      1,
      0.1,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.35294117647058826,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7380056030392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.25,
      0.25,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.31862745098039214,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7365210438235295,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0.5,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.31862745098039214,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7339360866666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0.5,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.31862745098039214,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7339360866666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.25,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.31862745098039214,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7365210438235295,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.5,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.31862745098039214,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7339360866666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.25,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.31862745098039214,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7365210438235295,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.5,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.31862745098039214,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7339360866666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0.25,
      0,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7376300016666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0.5,
      0,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7350450445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0.25,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7376300016666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0.5,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7350450445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0.5,
      0,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7350450445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.25,
      0,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7376300016666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0.5,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7350450445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.25,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7376300016666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.5,
      0,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7350450445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.5,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7350450445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.25,
      0,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7376300016666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.25,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7376300016666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.5,
      0,
      0
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7350450445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.5,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.4117647058823529,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.39705882352941174,
      "substring_evidence_recall": 0.39705882352941174,
      "evidence_recall": 0.39705882352941174,
      "average_returned_score": 0.7350450445098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3480392156862745,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7391287939215686,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0.1,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3480392156862745,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7386752853921569,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0,
      0.25,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3480392156862745,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7392756198039215,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3431372549019608,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7415099932352941,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3431372549019608,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7402377517647059,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0.1,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3431372549019608,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7410564847058824,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0,
      0.25,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3431372549019608,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7403845776470588,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0.1,
      0.1,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3431372549019608,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7397842432352941,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0,
      0.25,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3431372549019608,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7403845776470588,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.3235294117647059
  },
  {
    "weights": [
      0,
      0.1,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3137254901960784,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7402893816666667,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.2647058823529412
  },
  {
    "weights": [
      0,
      0.1,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3088235294117647,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7426705809803922,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.2647058823529412
  },
  {
    "weights": [
      0,
      0.1,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3088235294117647,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7413983395098039,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.2647058823529412
  },
  {
    "weights": [
      0.1,
      0.25,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3088235294117647,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7382996840196079,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0,
      0.5,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.3088235294117647,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7361938601960785,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0.25,
      0,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.30392156862745096,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7394086418627451,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0.25,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.30392156862745096,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7394086418627451,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0,
      0.5,
      0,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.30392156862745096,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7373028180392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0,
      0.5,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.30392156862745096,
      "document_recall": 0.6617647058823529,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7373028180392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0.1,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.30392156862745096,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7388716410784314,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.1,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.30392156862745096,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7388716410784314,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.1,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.30392156862745096,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7388716410784314,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0.1,
      0,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7412528403921569,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0.1,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7399805989215686,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7391395912745098,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.1,
      0,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7412528403921569,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0.1,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7399805989215686,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7391395912745098,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.1,
      0,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7412528403921569,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0.1,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7399805989215686,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29901960784313725,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7391395912745098,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0,
      0,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29411764705882354,
      "document_recall": 0.5441176470588235,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7415207905882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.25,
      0,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29411764705882354,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.740248549117647,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0,
      0,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29411764705882354,
      "document_recall": 0.5441176470588235,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7415207905882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.5,
      0,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29411764705882354,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.740248549117647,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0,
      0,
      0
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29411764705882354,
      "document_recall": 0.5441176470588235,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.7415207905882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      1,
      0,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.38235294117647056,
      "reciprocal_rank": 0.29411764705882354,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.36764705882352944,
      "substring_evidence_recall": 0.36764705882352944,
      "evidence_recall": 0.36764705882352944,
      "average_returned_score": 0.740248549117647,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0.1,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.35294117647058826,
      "reciprocal_rank": 0.29411764705882354,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.3382352941176471,
      "substring_evidence_recall": 0.3382352941176471,
      "evidence_recall": 0.3382352941176471,
      "average_returned_score": 0.7406502812745098,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0.1,
      0,
      0
    ],
    "metrics": {
      "hit": 0.35294117647058826,
      "reciprocal_rank": 0.2892156862745098,
      "document_recall": 0.6029411764705882,
      "exact_evidence_recall": 0.3382352941176471,
      "substring_evidence_recall": 0.3382352941176471,
      "evidence_recall": 0.3382352941176471,
      "average_returned_score": 0.7430314805882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0.1,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.35294117647058826,
      "reciprocal_rank": 0.2892156862745098,
      "document_recall": 0.6323529411764706,
      "exact_evidence_recall": 0.3382352941176471,
      "substring_evidence_recall": 0.3382352941176471,
      "evidence_recall": 0.3382352941176471,
      "average_returned_score": 0.7417592391176471,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.35294117647058826,
      "reciprocal_rank": 0.2892156862745098,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.3382352941176471,
      "substring_evidence_recall": 0.3382352941176471,
      "evidence_recall": 0.3382352941176471,
      "average_returned_score": 0.7409182314705882,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0,
      0,
      0
    ],
    "metrics": {
      "hit": 0.35294117647058826,
      "reciprocal_rank": 0.28431372549019607,
      "document_recall": 0.5441176470588235,
      "exact_evidence_recall": 0.3382352941176471,
      "substring_evidence_recall": 0.3382352941176471,
      "evidence_recall": 0.3382352941176471,
      "average_returned_score": 0.7432994307843137,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0.1,
      0,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.35294117647058826,
      "reciprocal_rank": 0.28431372549019607,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.3382352941176471,
      "substring_evidence_recall": 0.3382352941176471,
      "evidence_recall": 0.3382352941176471,
      "average_returned_score": 0.7420271893137255,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0,
      0,
      0.1,
      0.25
    ],
    "metrics": {
      "hit": 0.3235294117647059,
      "reciprocal_rank": 0.27450980392156865,
      "document_recall": 0.5441176470588235,
      "exact_evidence_recall": 0.3088235294117647,
      "substring_evidence_recall": 0.3088235294117647,
      "evidence_recall": 0.3088235294117647,
      "average_returned_score": 0.7418680600980392,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0,
      0,
      0.1,
      0
    ],
    "metrics": {
      "hit": 0.3235294117647059,
      "reciprocal_rank": 0.2696078431372549,
      "document_recall": 0.5147058823529411,
      "exact_evidence_recall": 0.3088235294117647,
      "substring_evidence_recall": 0.3088235294117647,
      "evidence_recall": 0.3088235294117647,
      "average_returned_score": 0.7442492594117647,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0,
      0,
      0.1,
      0.1
    ],
    "metrics": {
      "hit": 0.3235294117647059,
      "reciprocal_rank": 0.2696078431372549,
      "document_recall": 0.5441176470588235,
      "exact_evidence_recall": 0.3088235294117647,
      "substring_evidence_recall": 0.3088235294117647,
      "evidence_recall": 0.3088235294117647,
      "average_returned_score": 0.7429770179411764,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.23529411764705882
  },
  {
    "weights": [
      0,
      0.25,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.23529411764705882,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.7413467426470588,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.17647058823529413
  },
  {
    "weights": [
      0,
      0.25,
      0,
      0
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.23039215686274508,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.742455700490196,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.17647058823529413
  },
  {
    "weights": [
      0,
      0.1,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.23039215686274508,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.7433160630392157,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.17647058823529413
  },
  {
    "weights": [
      0,
      0.25,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.23039215686274508,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.742455700490196,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.17647058823529413
  },
  {
    "weights": [
      0,
      0.1,
      0,
      0
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.22549019607843138,
      "document_recall": 0.5441176470588235,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.7456972623529412,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.17647058823529413
  },
  {
    "weights": [
      0,
      0.1,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.22549019607843138,
      "document_recall": 0.5735294117647058,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.744425020882353,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.17647058823529413
  },
  {
    "weights": [
      0,
      0,
      0,
      0.25
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.19607843137254902,
      "document_recall": 0.45588235294117646,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.7439982440196079,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.11764705882352941
  },
  {
    "weights": [
      0,
      0,
      0,
      0
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.19117647058823528,
      "document_recall": 0.4264705882352941,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.7463794433333334,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.11764705882352941
  },
  {
    "weights": [
      0,
      0,
      0,
      0.1
    ],
    "metrics": {
      "hit": 0.29411764705882354,
      "reciprocal_rank": 0.19117647058823528,
      "document_recall": 0.45588235294117646,
      "exact_evidence_recall": 0.27941176470588236,
      "substring_evidence_recall": 0.27941176470588236,
      "evidence_recall": 0.27941176470588236,
      "average_returned_score": 0.7451072018627451,
      "empty_queries": 0,
      "queries": 34
    },
    "hit1": 0.11764705882352941
  }
]
```

## Reproduction

Run from backend: `venv\Scripts\python.exe -B scripts/evaluate_retrieval_v2_diagnostic.py`. No network service other than the existing local Qdrant and Ollama embedding endpoint is used. This script writes only this report and performs read-only collection operations.
