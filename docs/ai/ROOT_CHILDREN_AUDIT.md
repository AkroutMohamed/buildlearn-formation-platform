# Root children audit

## Finding

The warning is reproducible: **239 of 2,637 ChildChunks (9.06%) have `parent_id=None`**. They occur in **41 extraction documents**, representing **39 distinct document_id values**, across **49 source pages**. All 239 have `section_path=[]`; all have nonempty text and preserved single-page ranges.

**Zero of the 239 violates the current page-local, forward-only recognized-heading assignment contract.** Every root child traces to a parsed non-container block that already has no parent: 166 occur before their page's first recognized heading, and 73 occur on pages with no recognized headings. No parent was lost during ParentChunk/ChildChunk conversion.

This does **not** establish that all 239 represent legitimate semantic top-level content. The set includes plausible document-level material, clearly structured technical content whose labels were not recognized as headings, detached property/table fragments, and OCR noise. The warning is an accurate description of optional parent references; it is neither proof of dangling links nor a sufficient semantic-quality verdict.

## Scope and read-only safeguards

All 221 complete success-status extraction JSON dictionaries under `backend/ai_data/reports/full_extraction/` were processed with the existing default `HierarchicalChunker.chunk_from_dict()`. `manifest.json` was excluded. This regenerated 1,115 ParentChunks and 2,637 ChildChunks in memory. The parser output and assigned SemanticBlocks were separately regenerated for trace comparisons.

Production Python source, extraction JSON, checkpoint files, and all existing indexing files were read only. No Qdrant client was instantiated or queried, no embedding service was invoked, no checkpoint was written, and no indexing command was run. Python ran with `-B` and bytecode writes disabled. The only intended filesystem output is this report.

Before/after content hashes of **2880 protected files** matched. Aggregate snapshot SHA-256: `06c203a1654528440959249b5810311f30d1ce819559ea4a633d05ade7d66ce2`. The protected file set covers `backend/app/ai/**/*.py`, extraction JSON files, and every existing file below `backend/ai_data/indexing/`. This establishes no content changes to those files during the audit; it does not audit unrelated external processes or filesystem access timestamps.

The completed checkpoint was read without modification: its checksum is valid and its 2,637 successful chunk IDs exactly match the regenerated set. A second regeneration verified all 239 report inventory records and their full texts against the source ChildChunks, confirmed ten example objects, and reproduced the same protected-file snapshot after report creation.

The analysis uses extraction text and implementation behavior. Original PDF visual layouts were not reviewed, so physical reading order and the visual ownership of ambiguous fragments are not claimed as established.

## Exhaustive quantitative results

| Check | Result |
|---|---:|
| Extraction documents | 221 |
| ParentChunks | 1,115 |
| ChildChunks | 2,637 |
| Unique ChildChunk IDs | 2,637 |
| Children with parent_id=None | 239 |
| Children with parent_id="" | 0 |
| Children with a non-null parent | 2,398 |
| Dangling non-null parent references | 0 |
| Root children matched to source parser blocks | 239 |
| Root children matched to assigned blocks with a non-null parent | 0 |
| Root children incorrectly listed in any ParentChunk.children | 0 |
| Root children with a preceding recognized heading on the same page | 0 |
| Root children with a nonempty section_path | 0 |
| Root text length | 1–1,269 characters |
| Root children with page_start=page_end | 239 |

All non-null parent references were checked against parents in the same source ChunkResult. Text/type/page matches were used to trace roots, including repeated text that has collision-suffixed child IDs. Where text matches multiple parsed blocks, all matching assigned blocks have null parents; no specific occurrence was inferred solely from identical text.

### Block type distribution

| block_type | Count | Share of 239 |
|---|---:|---:|
| paragraph | 212 | 88.70% |
| list_item | 25 | 10.46% |
| caption | 2 | 0.84% |
| All other block types | 0 | 0.00% |

There are no root `heading`, `list`, `table`, `key_value`, `raw_text`, `unknown`, or `page_break` children in this dataset. A `list_item` is not a `LIST` container in the current chunker.

### Section path distribution

| Exact section_path | Count | Share |
|---|---:|---:|
| [] | 239 | 100.00% |

There are no named section paths on any of these 239 roots.

### Structural and page distribution

| Observed cause | Count |
|---|---:|
| Before first recognized heading on source page | 166 |
| Source page has no recognized headings | 73 |
| After a recognized heading on source page | 0 |
| First document page | 142 |
| Later document page | 97 |

These are overlapping dimensions: the first three rows classify all 239; the final two independently classify all 239. The 73 roots on heading-free pages are 33 in `duraline-brochure.pdf` and 40 in `fireline-brochure.pdf`.

The 97 later-page roots comprise 7 in `CEM PRO FLEX 100 W Protection.pdf`, 48 in `duraline-brochure.pdf`, and 42 in `fireline-brochure.pdf`. All 97 have some recognized heading on an earlier document page, but this does not prove that heading owns the current content. For example, the remembered earlier heading for Duraline pages 2–4 is `% / SAINT-GOBAIN`, and for Fireline pages 3–4 it is `BEAM & COLUMN ENCASEMENT`; blindly treating these as semantic parents is unsupported by the current text.

### Document distribution

Each row is one extraction source document, not a deduplicated document_id. Two filename/document_id pairs occur twice with different extraction/source identities (`fiche_technique_Mura-colle-platre` and `fiche_technique_pap2`). They remain separate; their distinct child IDs are preserved. The other 180 extraction documents contain zero null-parent children.

| Extraction JSON | document_id | file_name | Root children | All children |
|---|---|---|---:|---:|
| Adhércol P-3000_Compressed_83adfa3e7537.json | full-Adhércol P-3000_Compressed-ae52c6b9 | Adhércol P-3000_Compressed.pdf | 8 | 38 |
| CEM PRO FLEX 100 W Protection_38f6e96e2685.json | full-CEM PRO FLEX 100 W Protection-2de0b296 | CEM PRO FLEX 100 W Protection.pdf | 11 | 25 |
| duraline-brochure_987c7dbb7b2c.json | full-duraline-brochure-b4427434 | duraline-brochure.pdf | 54 | 123 |
| duraline-datasheet_6e91b04bb672.json | full-duraline-datasheet-26655d11 | duraline-datasheet.pdf | 10 | 18 |
| ECO%20COLLE%20V4_5b062563b0ea.json | full-ECO%20COLLE%20V4-b4db0cfb | ECO%20COLLE%20V4.pdf | 2 | 46 |
| fiche%20Champion%204%20IN%201%20locale%201_3763a445a513.json | full-fiche%20Champion%204%20IN%201%20locale%201-26006ee2 | fiche%20Champion%204%20IN%201%20locale%201.pdf | 1 | 48 |
| fiche_technique_Mura-colle-platre_72dd6ab57ffd.json | full-fiche_technique_Mura-colle-platre-24ed7a37 | fiche_technique_Mura-colle-platre.pdf | 4 | 10 |
| fiche_technique_Mura-colle-platre_e33338600415.json | full-fiche_technique_Mura-colle-platre-24ed7a37 | fiche_technique_Mura-colle-platre.pdf | 4 | 10 |
| fiche_technique_pap2_0fdcc068fa57.json | full-fiche_technique_pap2-9b35b6f2 | fiche_technique_pap2.pdf | 5 | 34 |
| fiche_technique_pap2_d8b10a4cd962.json | full-fiche_technique_pap2-9b35b6f2 | fiche_technique_pap2.pdf | 5 | 34 |
| FINACEM BLEU_compressed_dc18c77cf4b8.json | full-FINACEM BLEU_compressed-9ca633ef | FINACEM BLEU_compressed.pdf | 8 | 24 |
| FINACEM ROUGE_compressed_4cf6135b9923.json | full-FINACEM ROUGE_compressed-b55c6bdb | FINACEM ROUGE_compressed.pdf | 9 | 24 |
| fireline-brochure_81e3b6597899.json | full-fireline-brochure-0d9a7f00 | fireline-brochure.pdf | 43 | 71 |
| FULL%201_4eb974b628dc.json | full-FULL%201-eb0d29c6 | FULL%201.pdf | 3 | 43 |
| FULL%20ECO1_c271ba8c4f2a.json | full-FULL%20ECO1-bfeacce9 | FULL%20ECO1.pdf | 1 | 44 |
| FULL_e40ec8236bb3.json | full-FULL-88a1b942 | FULL.pdf | 1 | 51 |
| HYDRO REP surfaçage_Compressed_2a50217df15b.json | full-HYDRO REP surfaçage_Compressed-8fb9c724 | HYDRO REP surfaçage_Compressed.pdf | 1 | 49 |
| HYDRO%20FAçADE1_5f7664a6ea8b.json | full-HYDRO%20FAçADE1-d78abedc | HYDRO%20FAçADE1.pdf | 1 | 30 |
| HYDROMUR%20B%20V4_e8b0dca99f5c.json | full-HYDROMUR%20B%20V4-ebcd1c8c | HYDROMUR%20B%20V4.pdf | 3 | 46 |
| hydromur%20R%20V4_cee5b740ce86.json | full-hydromur%20R%20V4-240171e4 | hydromur%20R%20V4.pdf | 1 | 50 |
| ISBAROC%20R1_b2dd6b1b970e.json | full-ISBAROC%20R1-1c9a7b6f | ISBAROC%20R1.pdf | 2 | 43 |
| ISBAROC-R_01f689d57d2e.json | full-ISBAROC-R-3a4b4eb9 | ISBAROC-R.pdf | 1 | 62 |
| jir%20pro%20etanche1_c8a53d60caec.json | full-jir%20pro%20etanche1-7c9a4574 | jir%20pro%20etanche1.pdf | 3 | 24 |
| LIKA%20FINA1_09598ce93790.json | full-LIKA%20FINA1-890840ee | LIKA%20FINA1.pdf | 1 | 37 |
| LIKA-FINA-1_1f6c5026dd24.json | full-LIKA-FINA-1-d813e596 | LIKA-FINA-1.pdf | 1 | 64 |
| MARBRE%20V4_85e87f0cf3ca.json | full-MARBRE%20V4-5e49c875 | MARBRE%20V4.pdf | 2 | 42 |
| MURENDUIT%20B%20V4_244d9743aed2.json | full-MURENDUIT%20B%20V4-a9608640 | MURENDUIT%20B%20V4.pdf | 1 | 38 |
| MURENDUIT%20R%20V4_6243d8c30239.json | full-MURENDUIT%20R%20V4-72cd5c90 | MURENDUIT%20R%20V4.pdf | 2 | 41 |
| MURENDUIT%20V%20V4_368b3c34e1ca.json | full-MURENDUIT%20V%20V4-93ec077e | MURENDUIT%20V%20V4.pdf | 1 | 47 |
| PDS-0305-Gyproc Easi-Fill Hydro JC_ebc9fb698902.json | full-PDS-0305-Gyproc Easi-Fill Hydro JC-fd99ebe7 | PDS-0305-Gyproc Easi-Fill Hydro JC.pdf | 5 | 11 |
| PISCINE%20V4_64ebcc3095fb.json | full-PISCINE%20V4-18fdf73d | PISCINE%20V4.pdf | 4 | 43 |
| POOL%20V2_708f448f1e47.json | full-POOL%20V2-9db8b280 | POOL%20V2.pdf | 1 | 43 |
| Pro 3000_Compressed_be5e239f4859.json | full-Pro 3000_Compressed-94812339 | Pro 3000_Compressed.pdf | 21 | 50 |
| PRO%20200%20V4_f0e2573ccc63.json | full-PRO%20200%20V4-8f310261 | PRO%20200%20V4.pdf | 4 | 45 |
| Rustika assila_Compressed_e26343052773.json | full-Rustika assila_Compressed-a2177721 | Rustika assila_Compressed.pdf | 2 | 3 |
| RUSTIKA%20GRAVITA1_1d84b8dadea0.json | full-RUSTIKA%20GRAVITA1-2cf866dc | RUSTIKA%20GRAVITA1.pdf | 1 | 41 |
| RUSTIKA%20TYROLIEN1_db7ed13fae9e.json | full-RUSTIKA%20TYROLIEN1-b9628ec3 | RUSTIKA%20TYROLIEN1.pdf | 1 | 40 |
| Supcoat M_Compressed_d8ee2139fb3b.json | full-Supcoat M_Compressed-0e58b4d7 | Supcoat M_Compressed.pdf | 7 | 8 |
| SUPERLITE1_9b4ec2071c8d.json | full-SUPERLITE1-8227dad4 | SUPERLITE1.pdf | 1 | 28 |
| Suplastic_Compressed_1da775a6cb76.json | full-Suplastic_Compressed-7e1bbfea | Suplastic_Compressed.pdf | 2 | 3 |
| SUPLATEX1_e9af72e07e7a.json | full-SUPLATEX1-c1a35954 | SUPLATEX1.pdf | 1 | 32 |

## Comparison with the current implementation

The following references use repository-relative files and current line positions.

1. [models.py](../../backend/app/ai/chunking/models.py#L151): `ChildChunk.parent_id` is explicitly `Optional[str] = None`, and `section_path` defaults to an empty list. `ChildChunk.is_embeddable` returns true regardless of parent presence. [test_hierarchical_chunker.py](../../backend/tests/ai/test_hierarchical_chunker.py#L317) expressly constructs an embeddable child with `parent_id=None`. Null parents are permitted by the model; a universal parent requirement is not implemented.
2. [chunker.py](../../backend/app/ai/chunking/chunker.py#L34): `chunk_from_dict()` builds hierarchy independently for each page's `raw_text`. It does not consume `ordered_elements` for layout ownership or carry section state between pages.
3. [hierarchy.py](../../backend/app/ai/chunking/hierarchy.py#L33): `current_section` begins as None for each page. At [line 69](../../backend/app/ai/chunking/hierarchy.py#L69), non-heading blocks encountered before a heading are appended to `body_blocks` without a parent or path. Once a heading is active, subsequent non-heading blocks receive the heading's block ID and path. Later headings do not retrospectively own earlier blocks.
4. [chunker.py](../../backend/app/ai/chunking/chunker.py#L73): recognized heading, list, table, and key/value containers become ParentChunks. Their emitted children get that container's ID. Non-container body blocks use `block.parent_id`; the code only resolves an already assigned block ID to its ParentChunk ID. It does not invent a document/page root or infer a parent from nearby containers.
5. [chunker.py](../../backend/app/ai/chunking/chunker.py#L415): `_block_to_child()` passes the supplied parent reference through. All 239 roots fit within the maximum size and directly retain their source text/type/page, rather than reaching the generic split path.
6. [parser.py](../../backend/app/ai/chunking/parser.py#L484): line detectors determine whether a heading exists. `_is_likely_heading()` rejects mixed-case text. Consequently, labels such as `Préparation du Support (DTU 59.1):`, `Applications:`, and `Non-Loadbearing Wall System` do not necessarily establish a section. This is upstream classification behavior, not parent loss in the chunk conversion stage.

`ParentChunk` represents recognized containers, and its `children` list identifies assigned/emitted child chunks; it is not an automatic owner of every paragraph in a document. Although `HierarchyLevel.DOCUMENT` exists in the enum, this chunking path does not create a synthetic document parent. The current container's own text supplies its emitted children; separately parsed nearby paragraphs are not automatically absorbed into that container.

## Semantic assessment and logical parent question

### Plausible document-level roots

Brand/contact details, revision notices, copyright statements, and short product introductions may legitimately be document-level content. For example, contact child `8b2edfada4e452af` does not intrinsically require a particular technical section. Product introduction `524dd4142eca2b0d` is coherent standalone prose, although a later `DESCRIPTION PRODUIT\nLES PLUS PRODUIT` parent also supplies a plausible semantic context. Without checking PDF layout, introduction status and reading-order displacement cannot be conclusively distinguished.

### Evidence of missed semantic grouping

Several concrete cases are not well described as independent top-level content:

- `dfba85eda9d3e8c7` contains the contraindication label; following list `66d066b55be291db` belongs semantically to that label. Neither creates a recognized heading parent. This is a classification/segmentation limitation.
- `f153903bddd627af` is `Préparation du Support (DTU 59.1):`; list `67f066024d5bc422` contains the associated support-preparation/application instructions. A recognized `MISE EN OEUVRE` ParentChunk (`281949feee65de5e`) exists later in that same extracted page and has zero children. Extracted order prevents the forward-only builder from associating the early instructions with it. This establishes an order/semantic mismatch in the extracted representation, not the physical PDF reading order.
- On Fireline page 3, `Gyproc Fire Rated Wall Systems` and `Non-Loadbearing Wall System` appear before detailed wall specifications but are parsed as paragraphs. The page has no recognized headings. The specification children are semantically grouped by those textual titles, even though no heading parents exist for them.
- In Duraline datasheet page 1, root `86824f204d97ba8c` (`Brown reverse side paper`) follows key/value parent `76abe1f9b77a2d24` (`Board Colour: Yellow face paper`). Similarly `52dafe39707ba7c1` (`Square edge along width of board`) follows parent `16df160217cad3d6` (`Edges: Taper edge along length of board`). These are strong semantic continuation candidates for existing key/value containers, but the design does not attach separately parsed paragraphs to those containers.
- Root `0f5cf214441d5311` is a flattened flexural-load measurement fragment; table parent `236e72f8c90d524f` appears later on the same page with related values. The semantic relationship is apparent, but current rules do not assign a root fragment to a later table.
- Root `bcce7103bb5271e8` in the Easi-Fill datasheet contains flattened table headers and rows (`Test Parameters Specification Minimum Maximum...`). Its paragraph classification indicates that structural content can be present without a table ParentChunk.

These observations show incomplete semantic grouping in part of the root set. They do not identify a defective block-ID-to-ParentChunk conversion or justify a claim that all 239 need parents.

### The two caption children

Both `39680e161334916a` and `a22b4b52017a8094` contain suitability/application prose. The current caption detector checks whether configured indicator `Table ` appears as a substring in the first 30 characters. It matches within `Suitable ` for both texts; this was reproduced directly with the unchanged detector. The caption labels therefore have a concrete false-positive explanation and are not evidence of true figure/table captions. Their null parents still follow the same page-local rules.

### Page boundaries and ambiguous fragments

Hierarchy state resets on every page. This explains why later pages can produce roots even when earlier pages had headings. In this dataset, the 97 later-page roots have no earlier recognized heading on their own page; an earlier page's heading does not satisfy the current assignment rule. Some content may belong to continuing document sections, but this audit cannot establish that all 97 are continuations.

Isolated fragments such as `18`, `3`, `p`, `w#) @`, and OCR-distorted branding lack enough context to name a dependable semantic parent. A quantitative partition into “genuinely top-level” versus “must have a semantic parent” would imply unsupported certainty, so no such invented total is given. Exact structural classifications are supplied for all 239 instead.

**Answer under the implemented design:** none of the 239 should have an assigned parent based on a preceding recognized heading or membership in the container block that generated it. There is no missing required link in that contract. **Answer under semantic document interpretation:** some clearly belong to an unrecognized label, adjacent property container, related table, or likely section; the examples above establish that the broad claim “all 239 are legitimate top-level content” is too strong. These two conclusions are compatible: current behavior is internally consistent while semantic hierarchy coverage is incomplete.

No code changes are proposed in this audit.

## Ten representative examples

Each JSON object below contains the exact source ChildChunk text without truncation or OCR correction. `chunk_id` and extraction filename are included to identify the precise occurrence. The examples cover plausible roots, missed labels, list content, technical specifications, caption false positives, property continuations, table fragments, and ambiguous numeric text.

### Example 1: 8b2edfada4e452af

```json
{
  "chunk_id": "8b2edfada4e452af",
  "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
  "file_name": "CEM PRO FLEX 100 W Protection.pdf",
  "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
  "block_type": "paragraph",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com",
  "parent_id": null
}
```

Assessment: Document-wide contact details; a plausible document-level root. A section parent is not required by the current contract.

### Example 2: 524dd4142eca2b0d

```json
{
  "chunk_id": "524dd4142eca2b0d",
  "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
  "file_name": "RUSTIKA%20GRAVITA1.pdf",
  "extraction_file": "RUSTIKA%20GRAVITA1_1d84b8dadea0.json",
  "block_type": "paragraph",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "RUSTIKA GRAVITA  est un enduit minéral de parement hydrofugé, de texture extra- rugeuse, teinté dans la masse pour applicaƟon manuelle sur les murs extérieurs. RUSTIKA GRAVITA est classé comme morƟer de type CR CS IΙI  W1 selon  la norme NF EN998-1.",
  "parent_id": null
}
```

Assessment: Product introduction before the recognized `DESCRIPTION PRODUIT\nLES PLUS PRODUIT` heading. Plausible introduction, but its subject matches that later heading; physical PDF reading order was not independently established.

### Example 3: dfba85eda9d3e8c7

```json
{
  "chunk_id": "dfba85eda9d3e8c7",
  "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
  "file_name": "Adhércol P-3000_Compressed.pdf",
  "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
  "block_type": "paragraph",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "Contre IndicaƟons :\nNe pas uƟliser dans les cas suivants :",
  "parent_id": null
}
```

Assessment: The mixed-case `Contre IndicaƟons` label and introductory sentence were classified together as a paragraph. This looks like a missed semantic section, not a dropped existing parent.

### Example 4: 66d066b55be291db

```json
{
  "chunk_id": "66d066b55be291db",
  "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
  "file_name": "Adhércol P-3000_Compressed.pdf",
  "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
  "block_type": "list_item",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "• Pose de carreaux non absorbants sur supports non absorbants\n• Sur les supports en béton préfabriqué\n• Sur les anciens carrelages\n• Sur les surfaces métalliques, en linoléum, PVC, caoutchoue et dérivés\n• Sur surfaces humides ou soumises à remontées d’humidité\n• Sur des supports pas encore sec ou sujets à des retraits importants;\n• Sur le bois peint ou traité avec des imprégnant\n• Sur les surfaces soumises à une immersion conƟnue\n• En extérieur.",
  "parent_id": null
}
```

Assessment: Contraindication list following the preceding unrecognized label. Semantically it belongs to that contraindication group; the current parser has not created a heading/container parent for it.

### Example 5: 67f066024d5bc422

```json
{
  "chunk_id": "67f066024d5bc422",
  "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
  "file_name": "FINACEM BLEU_compressed.pdf",
  "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
  "block_type": "list_item",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être nivelé, stable, propre, sans la présence de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer  FINACEM  CACHET  BLEU  dans  environ   2.3L d’eau pour 5 kg  de  poudre,  puis  mélanger  à  la  main ou à l’aide  d’un  malaxeur  jusqu’à l’obtention d’une pâte homo- -gène à la consistance souhaitée.\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\n• Il  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Répandre le produit sur la surface avec une spatule lisse pour assurer  une répartition et une couverture complète de la surface.\n• Le  produit  est  appliqué  d’un  à  deux  couches  pour une épaisseur  jusqu’à 2 à 3 mm.\n• Appliquer  une deuxième couche après le durcissement de la  première  ( après  2  à  24  heures )  en croisant le sens de l’application.\n• Lorsque  l’enduit  de  ﬁnition  commence  à  durcir,  lisser à l’aide d’une taloche lisseuse.\n• La  peinture  sera  appliquée lorsque le  taux d’humidité de support est inférieur à 5%.",
  "parent_id": null
}
```

Assessment: Support preparation/application instructions follow an unrecognized mixed-case label. The existing `MISE EN OEUVRE` ParentChunk appears later in the extraction order, so the forward-only builder does not attach this child to it.

### Example 6: 2450bb836e8f611e

```json
{
  "chunk_id": "2450bb836e8f611e",
  "document_id": "full-fireline-brochure-0d9a7f00",
  "file_name": "fireline-brochure.pdf",
  "extraction_file": "fireline-brochure_81e3b6597899.json",
  "block_type": "paragraph",
  "section_path": [],
  "page_start": 3,
  "page_end": 3,
  "text": "One layer of 12.55 mm Gyproc® Plain Board applied vertically to either side of 70mm x 0.5mm G.l. Metal Framingspaced at610mm centertocenter.",
  "parent_id": null
}
```

Assessment: Technical wall specification follows `Gyproc Fire Rated Wall Systems` and `Non-Loadbearing Wall System`, both parsed as paragraphs. The page has zero recognized headings. Semantically structured content remains parentless.

### Example 7: a22b4b52017a8094

```json
{
  "chunk_id": "a22b4b52017a8094",
  "document_id": "full-duraline-datasheet-26655d11",
  "file_name": "duraline-datasheet.pdf",
  "extraction_file": "duraline-datasheet_6e91b04bb672.json",
  "block_type": "caption",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "Suitable for applications where high level of acoustics and impact levels are specified",
  "parent_id": null
}
```

Assessment: Application suitability prose follows `Applications:`. It was labeled caption because `Table ` occurs inside `Suitable `. The root status is structurally expected; the caption label is not compelling semantic evidence of a genuine figure caption.

### Example 8: 86824f204d97ba8c

```json
{
  "chunk_id": "86824f204d97ba8c",
  "document_id": "full-duraline-datasheet-26655d11",
  "file_name": "duraline-datasheet.pdf",
  "extraction_file": "duraline-datasheet_6e91b04bb672.json",
  "block_type": "paragraph",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "Brown reverse side paper",
  "parent_id": null
}
```

Assessment: `Brown reverse side paper` immediately follows `Board Colour: Yellow face paper`. Existing key/value parent `76abe1f9b77a2d24` contains the latter text only. This is a strong semantic continuation candidate, but the current design does not attach a separately parsed paragraph to a prior key/value container.

### Example 9: 0f5cf214441d5311

```json
{
  "chunk_id": "0f5cf214441d5311",
  "document_id": "full-duraline-datasheet-26655d11",
  "file_name": "duraline-datasheet.pdf",
  "extraction_file": "duraline-datasheet_6e91b04bb672.json",
  "block_type": "paragraph",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "Longitudinal Direction (N) 13mm board 1220 2440 300 725",
  "parent_id": null
}
```

Assessment: A flattened measurement/table fragment. A separate table parent `236e72f8c90d524f` exists later on the page. Related content is evident, but the root fragment cannot be assigned to that later container by the current contract.

### Example 10: 23f6f130c4e5d8cb

```json
{
  "chunk_id": "23f6f130c4e5d8cb",
  "document_id": "full-Suplastic_Compressed-7e1bbfea",
  "file_name": "Suplastic_Compressed.pdf",
  "extraction_file": "Suplastic_Compressed_1da775a6cb76.json",
  "block_type": "paragraph",
  "section_path": [],
  "page_start": 1,
  "page_end": 1,
  "text": "18",
  "parent_id": null
}
```

Assessment: Standalone numeric fragment `18`. Its intended semantic owner cannot be established confidently from extracted text alone; an absent parent here is not proof of a hierarchy-link bug.

## Complete inventory: all 239 exact children

The following machine-readable array is exhaustive, in sorted extraction-file order and original ChildChunk order. Text is complete; duplicate-looking text and suffixed IDs remain separate. `structural_case` is an audit finding, not added production metadata. It denotes either content before a page's first recognized heading or content on a page with no recognized heading. Source context and the precise child ID identify every occurrence.

```json
[
  {
    "chunk_id": "830e0f8e93f5d9c1",
    "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
    "file_name": "Adhércol P-3000_Compressed.pdf",
    "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "• Prêt à l’emploi\n• Thixotrope : sans glissement",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "dfba85eda9d3e8c7",
    "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
    "file_name": "Adhércol P-3000_Compressed.pdf",
    "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Contre IndicaƟons :\nNe pas uƟliser dans les cas suivants :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "66d066b55be291db",
    "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
    "file_name": "Adhércol P-3000_Compressed.pdf",
    "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "• Pose de carreaux non absorbants sur supports non absorbants\n• Sur les supports en béton préfabriqué\n• Sur les anciens carrelages\n• Sur les surfaces métalliques, en linoléum, PVC, caoutchoue et dérivés\n• Sur surfaces humides ou soumises à remontées d’humidité\n• Sur des supports pas encore sec ou sujets à des retraits importants;\n• Sur le bois peint ou traité avec des imprégnant\n• Sur les surfaces soumises à une immersion conƟnue\n• En extérieur.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "6c00d5aefb631257",
    "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
    "file_name": "Adhércol P-3000_Compressed.pdf",
    "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Le support doit être plat, sain, solide, sec, stable (retraits de maturaƟon terminés) et sans poussière, parƟes friables et huiles, graisses,  décoﬀrant, cires, peintures et tout ce qui pourrait compromeƩre la bonne adhérence.\nLes supports à base de plâtre/anhydrite doivent être complètement secs (humidité max. 0,5%) et après maturaƟon.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "c7d781378e50fe20",
    "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
    "file_name": "Adhércol P-3000_Compressed.pdf",
    "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Température d’applicaƟon : En présence de températures élevées  (> 35°C) , humidiﬁer légèrement  le support.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "9bd12e595fbda7a8",
    "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
    "file_name": "Adhércol P-3000_Compressed.pdf",
    "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Colle adhésive en pâte à base de résine synthéƟque en dispersion aqueuse et d’addiƟfs spéciaux, prêt à l’emploi, à temps ouvert allongé et résistant au glissement, classé D1TE selon EN 12004.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "a017042d47894e42",
    "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
    "file_name": "Adhércol P-3000_Compressed.pdf",
    "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Supports admissibles :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "3388bc45392e2843",
    "document_id": "full-Adhércol P-3000_Compressed-ae52c6b9",
    "file_name": "Adhércol P-3000_Compressed.pdf",
    "extraction_file": "Adhércol P-3000_Compressed_83adfa3e7537.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Colle adhésive en pâte  -  D1TE",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "974b085da60f2336",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SOFAP BÂTIMENT est une marque du la société SOFAP.\nSfax: Route de Gabés km 4.5 - 3052 / Tunis: Route de Bizerte Km 8 - Mnihla",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "2170d9102f95834d",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les éditions précédentes. dition 1, 2025.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "8b2edfada4e452af",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "daf50cd7604394f7",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les éditions précédentes. dition 4, 2024.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "97d6e106d4c6d654",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "SOFAP BÂTIMENT est une marque du la société SOFAP.\nSfax: Route de Gabés km 4.5 - 3052 / Tunis: Route de Bizerte Km 8 - Mnihla",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "6ee0d181d0c7f20e",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": ".Le présent document annule et remplace les éditions précédentes. dition 1, 2025.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "973ee0cc55de841d",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "3ac3e37b9d27492d",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": ".Le présent document annule et remplace les éditions précédentes. dition 4, 2024.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "ca257ccf6af9ff8b",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "Préparation du support :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "060897ea2a172b7a",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "1bca5b1704c94391",
    "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
    "file_name": "CEM PRO FLEX 100 W Protection.pdf",
    "extraction_file": "CEM PRO FLEX 100 W Protection_38f6e96e2685.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "• Bien mélanger le contenu du seau avant usage.\n• Le produit étant prêt à l’emploi, ne pas ajouter d’eau.\n• Le port  des  protections individuelles ( gants,  lunettes ) est recommandé.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "bd2b5a958943f388",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "In 2015, Saint-Gobain is celebrating its 350\" anniversary, 350 reasons to believe in the future. Backed by its experience and its capacityto continuously innovate, Saint-Gobain , the world leader in the habitat and construction market, designs, manufactures and distributes high - performance and building materials providing innovative solutions to the challenges of growth, energy efficiency and environmental protection. With 2013 sales of €42 billion, Saint-Gobain operates in 64 countries and has nearly190,000 employees.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "22fe4e897059c99b",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "mm $ / saINT-GOBAIN",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "002837504e804b38",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Gyproc is a market leader in the interior construction space in India for the last 28 years. The ever expanding product range includes gypsum plaster board systems for false ceiling & drywall applications, ceiling tiles (gypsum, mineral fibre tiles, glass wool and metal) for grid ceiling applications, cement fibre boards, gypsum plasters forinternal wall finishes plus a complete range of accessory products.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "8930bde1853f9f34",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "The entire gypsum plaster board, ceiling tiles and gypsum plaster range of products are approved by CII-IGBC for consideration towards Green Building rating systems (LEED) points.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0bed7829625c538b",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "©",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "f6f0c9f6e1944ebe",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "The contents ofthis manual are covered by copyright laws. Reproduction of allorany part withoutthe owner’s permission is prohibited. Allillustrations are subject to change. Whilst every care has been taken inthe preparation ofthis product guide, Gyproc expressly disclaims all and any liabilityto any person whether a purchaser of any product details of which are set out in this product manual, or otherwise in respect of anything done or omitted to be done andthe consequences of anything done or omitted to be done, by any such person in reliance, whether in whole or in part upon the whole orpartofthewithininformation.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "b784933fbc9e10b8",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "Ever wondered howstrong your walls are?",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "a497f10a044cea6e",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "GypWall\"\" ROBUST which consist of Gyproc® Duraline Board, is a superior alternateto traditional brick and block walls. A high impact resistantinternal wall system is ideal for Office space, Hospital, School & Industrial buildings where strong and robust walls are required.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "64d15eff67cdc3f8",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "Let’s take a brief overview of these situations",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "99a25f581981cbb2",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "In a hospital during emergency, in the bargain to save lives; corridor, passages are exposed to\nAccidental Impacts on partitions due to moving equipments and staff.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "9d844a208205efcd",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "In an Industrial space, material movement is common in warehouse and shop floor; making walls more prone to Impact Damage due to fork-liftmovementetc.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "c61a64fcad330b8d",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "In Offices, need for Unplanned Loading on walls often arises in cabins, meeting rooms and common areas which require a strong wall substrate.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "48855e8f71f89318",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "Schools require a strong wall system to be able to accommodate the wear & tear caused due to Crowd Pressure and regular shifting of furniture.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "6a5f12bbf8cecd7d",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gyproc® Duraline Board GypWall\"\" ROBUST Systems",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "b3657f916df69e52",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gypsteel ULTRA® Ceiling Channel (fixed to soffit)",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "437223fa57c2d5c5",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": ".Key Performance S eve re D u ty",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "29eb0354c65a3701",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "HighImpact Resistance.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "e74012c6b281beee",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Satisfies BS 5234 Part 2 - 1992 Standards of Strength and Robustness of Severe DutyRating. a e a",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "39680e161334916a",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "caption",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "®  Suitable for application where weight of upto 32kg/m° can be directly service installedon the wall. cut-out",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "e5f478be3e19d490",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Achieves high level of sound insulation compared to standard board. GypWall\"\" ROBUST is high",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "9f67dd77eb1d861f",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gyproc® Duraline Board",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "852b4b8228f07cba",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gyproc® Joint Paper Tape",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "5878b6ee8fcf4808",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "impact-resistant partition G Gyproc®\nÎ Î . . ypsteel ULTRA®\nReady substrate for mosttype of paints, wall papers andlaminates. system complies with the u äŒ:2.ÏSËËm",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "cd757fd24f55a535",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "G © Duraline B i based interi Il lini t i yproc® Duraline Board is gypsum based interior wall lining product used in Severe Duty Rating.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "4909bc1a411e45b3",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "High Impact Resistant Partition System to provide a more durable surface for walls and partitions.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "0f619b8f08ecda7b",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gyproc® Pro-Fill Jointing Compound",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "52826fd77ec20709",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gyproc® Duraline Board’s gypsum core, incorporates glass fibre and other fire",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "0734b9263e43ff71",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "protective additives, which are encased and firmly bonded to, strong mustard lnsmtllaÿiclm",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "8141b96a8a964b03",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "E ellow coloured paperliners. Œ;tiec:lnaal)",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "f541f2c045a40982",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gypsteel ULTRA® Floor Channel (fixed to floor slab)",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "abfabe38b1db4737",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Performance of GypWall\"\" ROBUST System Designs",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "f41605ffc26008d6",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "9-® O -0 p",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "186c0a225fe00639",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": ") Es r 297 ——\nSingle Layer of Gyproc® Duraline Board Single Layer of Gyproc® Duraline Board Double Layer of Gyproc® Duraline Board\nÇ . 13mm on each side of Gypsteel ULTRA® C-Stud 13mm on each side of Gypsteel ULTRA® 13mm on each side of Gypsteel ULTRA®\nProduct Sp6CIfICBÎIOH with 50mm Insulation in the cavity Acou-Stud with 50mm Insulation in the cavity",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "bab3f0f9a2798028",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "æ  Thickness 13mm æ  EdgeType T.E/SÆ",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "f8faa23e4d6c27e1",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "æ  Dimensions1220mmx2440mm",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "9238c6aaf5a708c4",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Stud/ Lining Partition Max. Partition Fire Sound Partition",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "674efe1e803df9a4",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Track Thickness Thickness Height Resistance Insulation Duty",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "571cc2b800d8555c",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "#  Thermalconductivity (A)=0.24 W/mk Size (mm) (mm) (mm) (mm) (min) Rw (dB)\nThermal resistance (R)=0.05m° K/w 1 1x13 76 2500 30 38 Severe\nStandards IS 2095 & BS 5234 Part2-1992 2 1x13 76 2500 30 45 Severe",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "9241979029e93756",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "1 1x13 98 3600 30 40 Severe sectors 2 1x13 98 3600 60 48 Severe\n1 1x13 120 4500 30 41 Severe\n2 92/94 1x13 120 4500 60 50 Severe",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "ce32a740ed68a87c",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Test Parameters",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "9d1826e4c26d901b",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "GypWall\"\" ROBUST has been tested to the following tests and has passed all requirements of BS 5234: Part 2: 1992",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "c8084a70f856e5ee",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Requirement Tested Severe Duty",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "1d37b64dc23a477e",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Surface damage by small hard body impact:\nStraight Partition Passed Right angle partition Passed\nSurface damage by large soft body impact:\nStraight partition Passed Right angle partition Passed\nPerforation by small hard body impact:\nStraight partition Passed Right angle partition Passed",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "a848e50cae2f4611",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Door slamming Passed",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "099bb0e2cdbbbf3f",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Summary of other tests on partition specimen",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "1f644535a5ef8c00",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Requirement Tested Performance achieved",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "577aa2c60dfe892d",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Lightweight anchorage - Passed Pull out",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "c067a8c719ea9d98",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Lightweight anchorage - Passed Pull down",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "786fbbf1d0376797",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Heavy weight anchorage - Max Rating Wash basin",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "3079756711604996",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Heavy weight anchorage - Max Rating Wall cupboard",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "4b084fec440c9057",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Small Hard Body Impact Test Large Soft Body Impact Test",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "ce32a740ed68a87c_1",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Test Parameters",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "7cd99443a68cd092",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 5,
    "page_end": 5,
    "text": "Performance Certificate Case Studies",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "dabe7fe67d6e3c2a",
    "document_id": "full-duraline-brochure-b4427434",
    "file_name": "duraline-brochure.pdf",
    "extraction_file": "duraline-brochure_987c7dbb7b2c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 5,
    "page_end": 5,
    "text": "Test Report No. 54S075248/TWL dated 20 Sep 2007",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "62db7c47ac6480cd",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Made by :- Mayur Tikiwala                                       Approved by:- Shailendra Shinde",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "1c1fede9749c4fed",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Characteristics: Gyproc Duraline is higher density core with glass fiber and other additives firmly bonded with strong paper liners.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0a5e2c216b06aaa4",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Applications:",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "a22b4b52017a8094",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "caption",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Suitable for applications where high level of acoustics and impact levels are specified",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "2d8fdbcf1bd2601c",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Properties:",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "86824f204d97ba8c",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Brown reverse side paper",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "52dafe39707ba7c1",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Square edge along width of board",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "dfe78cc679933007",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Flexural breaking load of Gyproc Duraline as per Type- D, F, I & R",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0f5cf214441d5311",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Longitudinal Direction (N) 13mm board 1220 2440 300 725",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "744ab822268c1fc9",
    "document_id": "full-duraline-datasheet-26655d11",
    "file_name": "duraline-datasheet.pdf",
    "extraction_file": "duraline-datasheet_6e91b04bb672.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Product Data Sheet Sr No –",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "e0791ced31053ae7",
    "document_id": "full-ECO%20COLLE%20V4-b4db0cfb",
    "file_name": "ECO%20COLLE%20V4.pdf",
    "extraction_file": "ECO%20COLLE%20V4_5b062563b0ea.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les édiƟons précédentes.  diƟon 3, 2023.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "b7e58abd9d5e5091",
    "document_id": "full-ECO%20COLLE%20V4-b4db0cfb",
    "file_name": "ECO%20COLLE%20V4.pdf",
    "extraction_file": "ECO%20COLLE%20V4_5b062563b0ea.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SOFAP BâƟment est une marque du la société SOFAP\nUsine : Route de Gabes Km4.5 – 3052 – Sfax – Tunisie / Tél :00 216 74 453 983 / Fax : 00 216 74 453 397 E-mail : contact@sofap.com.tn  Site Web : www.sofap-baƟment.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "1d1a278c32f9995f",
    "document_id": "full-fiche%20Champion%204%20IN%201%20locale%201-26006ee2",
    "file_name": "fiche%20Champion%204%20IN%201%20locale%201.pdf",
    "extraction_file": "fiche%20Champion%204%20IN%201%20locale%201_3763a445a513.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "CHAMPION 4 IN 1 est un enduit en poudre de haute qualité mulƟfoncƟon : Rebouchage,  ragréage et ﬁniƟon ﬁne en applicaƟon manuelle sur les murs et les plafonds en intérieur.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "a72470427ac321ea",
    "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
    "file_name": "fiche_technique_Mura-colle-platre.pdf",
    "extraction_file": "fiche_technique_Mura-colle-platre_72dd6ab57ffd.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "NB: Les valeurs des caractéristiques techniques sont des valeurs statistiques moyennes  qui peuvent être mises à jours sans préavis.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "29ff750c3042ef89",
    "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
    "file_name": "fiche_technique_Mura-colle-platre.pdf",
    "extraction_file": "fiche_technique_Mura-colle-platre_72dd6ab57ffd.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Ce document est non contractuel, aucune responsabilité ne peut être acceptée de notre part en cas de dommage provenant d’une",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "dfcfcbcd59836ccc",
    "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
    "file_name": "fiche_technique_Mura-colle-platre.pdf",
    "extraction_file": "fiche_technique_Mura-colle-platre_72dd6ab57ffd.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "utilisation non appropriée de ce produit .",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "59a7b33d09b32c3c",
    "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
    "file_name": "fiche_technique_Mura-colle-platre.pdf",
    "extraction_file": "fiche_technique_Mura-colle-platre_72dd6ab57ffd.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Tèl.: +216 74 453 983 L.G / Fax: +216 74 453 397\nRoute de Gabès Km4,5 - B.P.3000 138 Sfax Tunisie sips.ksour@tunet.tn www.sips-platre.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "2ade8fbbfa344eb2",
    "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
    "file_name": "fiche_technique_Mura-colle-platre.pdf",
    "extraction_file": "fiche_technique_Mura-colle-platre_e33338600415.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "NB: Les valeurs des caractéristiques techniques sont des valeurs statistiques moyennes  qui peuvent être mises à jours sans préavis.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "736ce00d5eee2ae1",
    "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
    "file_name": "fiche_technique_Mura-colle-platre.pdf",
    "extraction_file": "fiche_technique_Mura-colle-platre_e33338600415.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Ce document est non contractuel, aucune responsabilité ne peut être acceptée de notre part en cas de dommage provenant d’une",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0072b26737bf35aa",
    "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
    "file_name": "fiche_technique_Mura-colle-platre.pdf",
    "extraction_file": "fiche_technique_Mura-colle-platre_e33338600415.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "utilisation non appropriée de ce produit .",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "81f91c4856b2893d",
    "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
    "file_name": "fiche_technique_Mura-colle-platre.pdf",
    "extraction_file": "fiche_technique_Mura-colle-platre_e33338600415.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Tèl.: +216 74 453 983 L.G / Fax: +216 74 453 397\nRoute de Gabès Km4,5 - B.P.3000 138 Sfax Tunisie sips.ksour@tunet.tn www.sips-platre.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "907af0ade6d5da36",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_0fdcc068fa57.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "$sirs",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "cc13052379e12d1a",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_0fdcc068fa57.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Enduit sous Emieke où monoccathe",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0aec40ab9a15aeeb",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_0fdcc068fa57.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "| Plôtre à dureté superfcialle renforcé",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "9d304be48a5b44e9",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_0fdcc068fa57.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Facie d'application",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "77bc82e9e7b14ac0",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_0fdcc068fa57.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SsIiPS",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "4e8148ad6a6565e0",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_d8b10a4cd962.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "$sirs",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "15f8f88e6bfc7053",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_d8b10a4cd962.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Enduit sous Emieke où monoccathe",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "35d09ab7f6426e60",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_d8b10a4cd962.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "| Plôtre à dureté superfcialle renforcé",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "9f87cf6f502e9181",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_d8b10a4cd962.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Facie d'application",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "41c492386057bc16",
    "document_id": "full-fiche_technique_pap2-9b35b6f2",
    "file_name": "fiche_technique_pap2.pdf",
    "extraction_file": "fiche_technique_pap2_d8b10a4cd962.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SsIiPS",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "3bdf7ad860ccaa11",
    "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
    "file_name": "FINACEM BLEU_compressed.pdf",
    "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SOFAP BÂTIMENT est une marque du la société SOFAP.\nSfax: Route de Gabés km 4.5 - 3052 / Tunis: Route de Bizerte Km 8 - Mnihla",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "29fd11eee259b8ac",
    "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
    "file_name": "FINACEM BLEU_compressed.pdf",
    "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les éditions précédentes. dition 1, 2025.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "1b1da5c657368fe8",
    "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
    "file_name": "FINACEM BLEU_compressed.pdf",
    "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "37fc65c352e3bf03",
    "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
    "file_name": "FINACEM BLEU_compressed.pdf",
    "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Bleu",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "ccd443393a80e8a2",
    "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
    "file_name": "FINACEM BLEU_compressed.pdf",
    "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Performances de l’enduit à l’état durci:",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "f153903bddd627af",
    "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
    "file_name": "FINACEM BLEU_compressed.pdf",
    "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Préparation du Support (DTU 59.1):",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "67f066024d5bc422",
    "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
    "file_name": "FINACEM BLEU_compressed.pdf",
    "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être nivelé, stable, propre, sans la présence de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer  FINACEM  CACHET  BLEU  dans  environ   2.3L d’eau pour 5 kg  de  poudre,  puis  mélanger  à  la  main ou à l’aide  d’un  malaxeur  jusqu’à l’obtention d’une pâte homo- -gène à la consistance souhaitée.\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\n• Il  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Répandre le produit sur la surface avec une spatule lisse pour assurer  une répartition et une couverture complète de la surface.\n• Le  produit  est  appliqué  d’un  à  deux  couches  pour une épaisseur  jusqu’à 2 à 3 mm.\n• Appliquer  une deuxième couche après le durcissement de la  première  ( après  2  à  24  heures )  en croisant le sens de l’application.\n• Lorsque  l’enduit  de  ﬁnition  commence  à  durcir,  lisser à l’aide d’une taloche lisseuse.\n• La  peinture  sera  appliquée lorsque le  taux d’humidité de support est inférieur à 5%.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "dd56a78e94abbae4",
    "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
    "file_name": "FINACEM BLEU_compressed.pdf",
    "extraction_file": "FINACEM BLEU_compressed_dc18c77cf4b8.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Caractéristiques d’emploi :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0cdf5b7369f85c1c",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SOFAP BÂTIMENT est une marque du la société SOFAP.\nSfax: Route de Gabés km 4.5 - 3052 / Tunis: Route de Bizerte Km 8 - Mnihla",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "3a78d938ba0bd37c",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les éditions précédentes. dition 1, 2025.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "fbe2b807d425b49f",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "3bc67ce5710b3476",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "426642fb845f122b",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Caractéristiques d’emploi :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "4c567ebaa62be3be",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "• Les caractéristiques de performance se réfèrent à des tests en laboratoire, des valeurs moyennes qui peuvent être modi- -ﬁées sans  préavis.  L’exploitant doit vériﬁer l’adéquation du produit en fonction de l’utilisation prévue.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "a94a0a9016ba5e5b",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Performances de l’enduit à l’état durci :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "946f03c3c8eb988a",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Supports Admissibles :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "402d3a316a635a65",
    "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
    "file_name": "FINACEM ROUGE_compressed.pdf",
    "extraction_file": "FINACEM ROUGE_compressed_4cf6135b9923.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "• Murs et plafonds remplis d’un mortier traditionnel (ciment, plâtre) ou un mortier chaux-ciment.\n• Les surfaces en béton\n• Béton cellulaire, enduit de ciment...\n• Maçonnerie soignée de bloc béton\n• Carreaux de plâtre, plaques de plâtre et plaques de plâtre cartonnées. Supports interdits :\n• Surfaces teintées.\n• Surfaces aux revêtements en plastique\n• Fer et acier.\n• Supports humides.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "b59d762876c30701",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Gyproc",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "e34c9c62e299d4ee",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "Our FIRE RATED OFFERING ranges from 30 Min. to 4 Hrs.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "84630383dc9af2c2",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 2,
    "page_end": 2,
    "text": "w#) @",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "18fde810d924d2a8",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gyproc Fire Rated Wall Systems",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "361516c04cef3474",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Non-Loadbearing Wall System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "2450bb836e8f611e",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "One layer of 12.55 mm Gyproc® Plain Board applied vertically to either side of 70mm x 0.5mm G.l. Metal Framingspaced at610mm centertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "95e139f787a50e5f",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "97 mm Acoustics (Rw) 43",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "361516c04cef3474_1",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Non-Loadbearing Wall System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "20a2b42a4886611e",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "One layer of 13mm Gyproc® Duraline Board applied vertically to either side of 70mM x 0.5mm G.l. Metal Framing spacedat610mm centertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "84c8bce8b1619cfd",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "98 mm Acoustics (Rw) 48",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "8aac6f3043913c25",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Max Reachable Height (mm) 3600 with 70mm metal stud ; 50mm with Insulation 20Kg/m°",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "4744097bac32cafe",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Two layer of 12.5mm Gyproc® Plain Board applied vertically to either side of 48mm x 0.5mm G.l. Metal Framingspaced at610mmcentertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "3115c4637c34f3ae",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "100 mm\nAcoustics (Rw) 50 Max Reachable Height (mm) 3400 with 70mm metal stud ; 50mm with Insulation 20Kg/m°",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "18fde810d924d2a8_1",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Gyproc Fire Rated Wall Systems",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "361516c04cef3474_2",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Non-Loadbearing Wall System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "545199157f2e0f43",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "One layer of 15mm Gyproc® Fireline Board applied vertically to either side of 70mM x 0.5mm G.l. Metal Framingspacedat610mm centertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "a11dad2d2ef3118a",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "102 mm\nAcoustics (Rw) 48 Max Reachable Height (mm) 3800 with 70mm metal stud ; 50mm with Insulation 20Kg/m°",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "32bed25da0bda48b",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Two layer of 12.5mm Gyproc® Plain Board applied vertically to either side of 70mm x 0.5mm G.l, Metal Framing spacedat610mmccentertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "559a2d8d14688a93",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "122 mm\nAcoustics (Rw) 50 Max Reachable Height (mm) 4600 with 70mm metal stud ; 50mm with Insulation 20Kg/m°",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "361516c04cef3474_3",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Non-Loadbearing Wall System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "e1d24fc0a9a2c3be",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Two layers of 12.5mm Gyproc® Fireline Board applied vertically to either side of 48mm x 0.5mm G.l, Metal Framingspaced at610mm centertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "974743913d5ef513",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "100 mm\nAcoustics (Rw) 50 Max Reachable Height (mm) 3400 with 70mm metal stud 50mm with",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "c68b71dcf9c0f238",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "Insulation",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "73afd93165372632",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 3,
    "page_end": 3,
    "text": "20Kg/m°",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "4386afbca4cadf23",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Gyproc Fire Rated Wall Systems",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "82bfe39c24e3142d",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Non-Loadbearing Wall System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "b378c4e5029c357d",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Two layers of 12.5mm Gyproc® Fireline Board applied vertically to either side of 70mm x 0.5mm G.l. Metal Framing spaced at610mm centertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "6322ec75f1379a1b",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Two layers of 15mm Gyproc® Fireline Board applied vertically to either side of 70mm x 0.5mm G.l. Metal Framing spacedat610mm centertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "46d9a83cbb9f8f54",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "122/132 mm\nAcoustics (Rw) 52 Max Reachable Height (mm) with 70mm metal stud 4600 ; 50mm with Insulation 20Kg/m°",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "82bfe39c24e3142d_1",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Non-Loadbearing Wall System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "8df0c0247f4257bd",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Three layers of 15mm Gyproc® Fireline Board applied\nVerticallyto either side of minimum 70mmx0.5mm G.\nTwin Metal Framing spacedat610mmcentertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "b7bdc06c7ee08b17",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "279 mm\nAcoustics (Rw) 60 Max Reachable Height (mm) with 70mm metal stud 4900 ; 50mm with Insulation 20Kg/m°",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "7b0b01d10c7a4fca",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Three layers of15mm Gyproc® Fireline Board applied\nVertically to either side of 146mm x 0.9mm G.l. Twin\nMetal Framing spaced at 407mm centertocenter.",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "3df12a344fd9e93d",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "431 mm",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "36d74955081b9c2b",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Acoustics (Rw) 66 Max Reachable Height (mm) with 70mm metal stud 11000 50mm with",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "22d84c2e8894f6b5",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Insulation 20Kg/m3",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "4386afbca4cadf23_1",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Gyproc Fire Rated Wall Systems",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "5b7f1b34befd0535",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Suspended Ceiling System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "5e829538dd786cc5",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "M/F Suspended Ceiling-One layer of15mm Gyproc®\nFireline Board suspended with help of Gyproc's Metal systems",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "5b7f1b34befd0535_1",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Suspended Ceiling System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "cc2190e5e86bc614",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "M/F Suspended Ceiling - Two layer of15mm Gyproc®\nFireline Board suspended with help of Gyproc's Metal systems",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "5b7f1b34befd0535_2",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "Suspended Ceiling System",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "fa6cc1bef07bfdb6",
    "document_id": "full-fireline-brochure-0d9a7f00",
    "file_name": "fireline-brochure.pdf",
    "extraction_file": "fireline-brochure_81e3b6597899.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 4,
    "page_end": 4,
    "text": "M/F Suspended Ceiling - Five layer of15mm Gyproc®\nFireline Board suspended with help of Gyproc's Metal systems",
    "parent_id": null,
    "structural_case": "page_without_recognized_headings"
  },
  {
    "chunk_id": "4a79607a16cd6cfc",
    "document_id": "full-FULL%201-eb0d29c6",
    "file_name": "FULL%201.pdf",
    "extraction_file": "FULL%201_4eb974b628dc.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "ConservaƟon :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "d7f6a4f6e90bdd4b",
    "document_id": "full-FULL%201-eb0d29c6",
    "file_name": "FULL%201.pdf",
    "extraction_file": "FULL%201_4eb974b628dc.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Couleur :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0ae808b09b5ac76b",
    "document_id": "full-FULL%201-eb0d29c6",
    "file_name": "FULL%201.pdf",
    "extraction_file": "FULL%201_4eb974b628dc.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "• 12 mois en emballage d’origine fermé à l’abri de l’humidité.\n40 Couleurs.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "ead4d9e0135d7215",
    "document_id": "full-FULL%20ECO1-bfeacce9",
    "file_name": "FULL%20ECO1.pdf",
    "extraction_file": "FULL%20ECO1_c271ba8c4f2a.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "LIKA FULL ECO est un enduit monocouche (OC2) blanc, hydrofugé, desƟné à l’applicaƟon mécanique sur les murs extérieurs.Il est classé comme morƟer de type OC CS IΙI W1 selon la norme NF ΕΝ 998-1.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0f5794e10cad319d",
    "document_id": "full-FULL-88a1b942",
    "file_name": "FULL.pdf",
    "extraction_file": "FULL_e40ec8236bb3.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les éditions précédentes. Édition 3, 2023.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "891f81591133c068",
    "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
    "file_name": "HYDRO REP surfaçage_Compressed.pdf",
    "extraction_file": "HYDRO REP surfaçage_Compressed_2a50217df15b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les éditions précédentes. Édition 1, 2024.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "e902281385b8b3b8",
    "document_id": "full-HYDRO%20FAçADE1-d78abedc",
    "file_name": "HYDRO%20FAçADE1.pdf",
    "extraction_file": "HYDRO%20FAçADE1_5f7664a6ea8b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "e1cbef3566016e7b",
    "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
    "file_name": "HYDROMUR%20B%20V4.pdf",
    "extraction_file": "HYDROMUR%20B%20V4_e8b0dca99f5c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Enduit de Finition Extérieur",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "93a8ff388abf2444",
    "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
    "file_name": "HYDROMUR%20B%20V4.pdf",
    "extraction_file": "HYDROMUR%20B%20V4_e8b0dca99f5c.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "- Catégorie 4c / Famille IV",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "11e0153c4d06938e",
    "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
    "file_name": "HYDROMUR%20B%20V4.pdf",
    "extraction_file": "HYDROMUR%20B%20V4_e8b0dca99f5c.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "HYDROMUR B est un enduit en poudre, de haute qualité, desƟné à la ﬁniƟon en applicaƟon manuelle sur les murs extérieurs.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "37e6cf0ec8aedca5",
    "document_id": "full-hydromur%20R%20V4-240171e4",
    "file_name": "hydromur%20R%20V4.pdf",
    "extraction_file": "hydromur%20R%20V4_cee5b740ce86.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "HYDROMUR R est un enduit en poudre, de haute qualité, desƟné au rebouchage et ragréage en applicaƟon manuelle sur les murs extérieurs.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "1e22000f776ecf87",
    "document_id": "full-ISBAROC%20R1-1c9a7b6f",
    "file_name": "ISBAROC%20R1.pdf",
    "extraction_file": "ISBAROC%20R1_b2dd6b1b970e.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "ISBAROC R est un enduit sous couche d’usage courant, desƟné à l’applicaƟon mécanique  sur les murs intérieurs et extérieurs.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "126e3e382dab64b2",
    "document_id": "full-ISBAROC%20R1-1c9a7b6f",
    "file_name": "ISBAROC%20R1.pdf",
    "extraction_file": "ISBAROC%20R1_b2dd6b1b970e.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Il est classé comme morƟer de type GP CS IIΙ W0 selon NF ΕΝ 998-1.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "da61e4e2c7b8c3f3",
    "document_id": "full-ISBAROC-R-3a4b4eb9",
    "file_name": "ISBAROC-R.pdf",
    "extraction_file": "ISBAROC-R_01f689d57d2e.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les éditions précédentes. Édition 3, 2023.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "fc97f8498c802043",
    "document_id": "full-jir%20pro%20etanche1-7c9a4574",
    "file_name": "jir%20pro%20etanche1.pdf",
    "extraction_file": "jir%20pro%20etanche1_c8a53d60caec.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "ère\nème",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "e9fc1b245a93501e",
    "document_id": "full-jir%20pro%20etanche1-7c9a4574",
    "file_name": "jir%20pro%20etanche1.pdf",
    "extraction_file": "jir%20pro%20etanche1_c8a53d60caec.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Environ 400 g / m2 pour les deux couches Sac de 20 kg",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "98a9f31addc01f9e",
    "document_id": "full-jir%20pro%20etanche1-7c9a4574",
    "file_name": "jir%20pro%20etanche1.pdf",
    "extraction_file": "jir%20pro%20etanche1_c8a53d60caec.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "•  Les valeurs des caractérisƟques techniques sont des valeurs staƟsƟques moyennes et qui peuvent être mises à jour sans préavis. Ce document est non contractuel, aucune responsabilité ne peut être acceptée de notre part en cas de dommage provenant d'un mauvais usage.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "e9d46a0389c69a9e",
    "document_id": "full-LIKA%20FINA1-890840ee",
    "file_name": "LIKA%20FINA1.pdf",
    "extraction_file": "LIKA%20FINA1_09598ce93790.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "LIKA FINA est un enduit mince  décoraƟf, hydrofugé, teinté dans la masse, desƟné à l’applicaƟon manuelle sur les murs extérieurs. il est classé comme morƟer de type CR CS IΙI W2 selon  la norme NF ΕΝ 998-1.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "451ecb13d0dfc99c",
    "document_id": "full-LIKA-FINA-1-d813e596",
    "file_name": "LIKA-FINA-1.pdf",
    "extraction_file": "LIKA-FINA-1_1f6c5026dd24.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les éditions précédentes. Édition 3, 2023.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "7f832f5c12110ca1",
    "document_id": "full-MARBRE%20V4-5e49c875",
    "file_name": "MARBRE%20V4.pdf",
    "extraction_file": "MARBRE%20V4_85e87f0cf3ca.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Mortier colle pour carrelage  -  C2TE",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "6367e5b3bcda2949",
    "document_id": "full-MARBRE%20V4-5e49c875",
    "file_name": "MARBRE%20V4.pdf",
    "extraction_file": "MARBRE%20V4_85e87f0cf3ca.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "MorƟer colle amélioré à base de ciment,  résistant au glissement, avec un temps ouvert allongé,desƟné à la pose de revêtements en marbre et granit  sur supports neufs en sols et murs intérieurs et extérieurs.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "bd968f099d113f43",
    "document_id": "full-MURENDUIT%20B%20V4-a9608640",
    "file_name": "MURENDUIT%20B%20V4.pdf",
    "extraction_file": "MURENDUIT%20B%20V4_244d9743aed2.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "MURENDUIT CACHET BLEU est un enduit en poudre de haute qualité desƟné à la ﬁniƟon ﬁne, en applicaƟon manuelle sur les murs et plafonds en intérieur.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "8af61d6e88d538da",
    "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
    "file_name": "MURENDUIT%20R%20V4.pdf",
    "extraction_file": "MURENDUIT%20R%20V4_6243d8c30239.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Enduit de Rebouchage   / Famille III - Catégorie 3",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "4d723f7a15ac728e",
    "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
    "file_name": "MURENDUIT%20R%20V4.pdf",
    "extraction_file": "MURENDUIT%20R%20V4_6243d8c30239.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "8bda7c941231c2b7",
    "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
    "file_name": "MURENDUIT%20V%20V4.pdf",
    "extraction_file": "MURENDUIT%20V%20V4_368b3c34e1ca.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "MURENDUIT cachet vert  est un enduit en poudre,  de haute qualité, desƟné au ragréage / garnissage et  éventuellement ﬁniƟon simple en applicaƟon manuelle sur les murs et plafonds en intérieur.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "177753bc81c924a9",
    "document_id": "full-PDS-0305-Gyproc Easi-Fill Hydro JC-fd99ebe7",
    "file_name": "PDS-0305-Gyproc Easi-Fill Hydro JC.pdf",
    "extraction_file": "PDS-0305-Gyproc Easi-Fill Hydro JC_ebc9fb698902.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Made by :- Amol Sonawane                                      Approved by:- Shailendra Shinde",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "dd83fef58eb9b29c",
    "document_id": "full-PDS-0305-Gyproc Easi-Fill Hydro JC-fd99ebe7",
    "file_name": "PDS-0305-Gyproc Easi-Fill Hydro JC.pdf",
    "extraction_file": "PDS-0305-Gyproc Easi-Fill Hydro JC_ebc9fb698902.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Application: - Gyproc Easi-Fill® Hydro is a gypsum based powdered Jointing Compound with a setting time of 90 to 110 minutes. Gyproc Easi-Fill® Hydro is a moisture resistant\nJointing Compound with reduced water absorption designed for quick jointing & finishing of\nGlasroc H & Moisture Resistant(MR) Gypsum board.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "bcce7103bb5271e8",
    "document_id": "full-PDS-0305-Gyproc Easi-Fill Hydro JC-fd99ebe7",
    "file_name": "PDS-0305-Gyproc Easi-Fill Hydro JC.pdf",
    "extraction_file": "PDS-0305-Gyproc Easi-Fill Hydro JC_ebc9fb698902.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Sr. No.\nTest Parameters Specification Minimum Maximum 1 Appearance Smooth white powder 2 Whiteness(Through whiteness meter) >85 3 Dry Bulk Density. Kg/m3 1000 1200 4 Passing through 150 micron 95% 5 pH 9 13 6 Total Water Absorption (EN 520) <5% 7 Water Gauge(Water to Powder ratio) 50 55",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "7db17610cefd29ef",
    "document_id": "full-PDS-0305-Gyproc Easi-Fill Hydro JC-fd99ebe7",
    "file_name": "PDS-0305-Gyproc Easi-Fill Hydro JC.pdf",
    "extraction_file": "PDS-0305-Gyproc Easi-Fill Hydro JC_ebc9fb698902.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "p",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "5895b33f90c49d73",
    "document_id": "full-PDS-0305-Gyproc Easi-Fill Hydro JC-fd99ebe7",
    "file_name": "PDS-0305-Gyproc Easi-Fill Hydro JC.pdf",
    "extraction_file": "PDS-0305-Gyproc Easi-Fill Hydro JC_ebc9fb698902.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Product Data Sheet",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "74f910036ef7579e",
    "document_id": "full-PISCINE%20V4-18fdf73d",
    "file_name": "PISCINE%20V4.pdf",
    "extraction_file": "PISCINE%20V4_64ebcc3095fb.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Piscine",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "b5cbb64bb2ad5dba",
    "document_id": "full-PISCINE%20V4-18fdf73d",
    "file_name": "PISCINE%20V4.pdf",
    "extraction_file": "PISCINE%20V4_64ebcc3095fb.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les édiƟons précédentes.  diƟon 3, 2023.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "3cd9494cf18c75b9",
    "document_id": "full-PISCINE%20V4-18fdf73d",
    "file_name": "PISCINE%20V4.pdf",
    "extraction_file": "PISCINE%20V4_64ebcc3095fb.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SOFAP BâƟment est une marque du la société SOFAP\nUsine : Route de Gabes Km4.5 – 3052 – Sfax – Tunisie / Tél :00 216 74 453 983 / Fax : 00 216 74 453 397 E-mail : contact@sofap.com.tn  Site Web : www.sofap-baƟment.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "c6d81f0912cce626",
    "document_id": "full-PISCINE%20V4-18fdf73d",
    "file_name": "PISCINE%20V4.pdf",
    "extraction_file": "PISCINE%20V4_64ebcc3095fb.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "MorƟer colle spécial piscine amélioré, déformable, résistant au glissement avec un temps ouvert allongé, à base de ciment, desƟné à la pose de carreaux céramiques (mosaïque) sur supports neufs et anciens.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "8b4ce74f4a2413f6",
    "document_id": "full-POOL%20V2-9db8b280",
    "file_name": "POOL%20V2.pdf",
    "extraction_file": "POOL%20V2_708f448f1e47.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "MorƟer colle spécial piscine amélioré, résistant au glissement avec un temps ouvert allongé, à base de ciment, desƟné à la pose de carreaux céramiques (mosaïque) sur supports neufs et anciens.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "cdb6488ac697de54",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "PréparaƟon du produit :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "7c1ecc2ec34eb57d",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Pour plus d’informaƟons se réferer au DTU 52.2 et /ou à notre guide de choix SOFAPCOL.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "7f6f38e289015721",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "•  Prêt à gâcher.\n•  MorƟer amélioré.\n•  Résistant au glissement des carreaux.\n•  Temps ouvert allongé.\n•  Résistant à la déformaƟon (ﬂexible).\n•  Supports neufs et anciens.\n•  Collages des grands formats.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "b1c0e2f619d3a28c",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "ComposiƟon :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "ed23a6d766301a12",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Couleur :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "675f4692fb2de719",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "•  Liant hydraulique, charges minérales et adjuvants.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "90435a4847f07288",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "•  Blanc.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "8c508438e4c1785a",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "ConservaƟon :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "6fd78c250bf0c8bd",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "•  12 mois en emballage d’origine fermé à l’abri de l’humidité.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "32caf9b02d454a5d",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "• Ne pas étaler le morƟer colle sur une grande surface (au delà de 2 m²) aﬁn d’éviter le dépassement du temps ouvert.\n• Ne pas uƟliser, en période de gel ou de forte chaleur, sous la pluie ou en plein soleil.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "e3affe0097a7f9dd",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "CaractérisƟques NormaƟves selon EN 12004 :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "4fe07fa9f0dac117",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Conseil :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "418d5385e2f229a8",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "•  Les valeurs des caractérisƟques techniques sont des valeurs staƟsƟques moyennes et qui peuvent être mises à jour sans préavis. Ce document est non contractuel, aucune responsabilité ne peut être acceptée de notre part en cas de dommage provenant d'un mauvais usage.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "8a051573207af188",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "≥   2.5 mm  et  < 5 mm",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "833baffb92b53025",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "≥ 1N/mm²",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "833baffb92b53025_1",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "≥ 1N/mm²",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "833baffb92b53025_2",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "≥ 1N/mm²",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "15317f873213ae0a",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "≥ 0.5N/mm²",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "833baffb92b53025_3",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "≥ 1N/mm²",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "ae71043c127ec352",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Toutes les valeurs indiquées dans ceƩe ﬁche technique sont basées sur des essais eﬀectués en laboratoires.\nElles peuvent être sensiblement modiﬁées par les condiƟons de mise en œuvre.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "5184421637e3564c",
    "document_id": "full-Pro 3000_Compressed-94812339",
    "file_name": "Pro 3000_Compressed.pdf",
    "extraction_file": "Pro 3000_Compressed_be5e239f4859.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "NB: L’épaisseur de la colle dépend de l’état du support, du format et du relief du carreau, du mode d’encollage et de la spatule uƟlisée.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "0c8507aa1ff4447d",
    "document_id": "full-PRO%20200%20V4-8f310261",
    "file_name": "PRO%20200%20V4.pdf",
    "extraction_file": "PRO%20200%20V4_f0e2573ccc63.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les édiƟons précédentes. diƟon 3, 2023.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "54245fe747e8009d",
    "document_id": "full-PRO%20200%20V4-8f310261",
    "file_name": "PRO%20200%20V4.pdf",
    "extraction_file": "PRO%20200%20V4_f0e2573ccc63.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SOFAP BâƟment est une marque du la société SOFAP\nUsine : Route de Gabes Km4.5 – 3052 – Sfax – Tunisie / Tél :00 216 74 453 983 / Fax : 00 216 74 453 397 E-mail : contact@sofap.com.tn  Site Web : www.sofap-baƟment.com",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "069c6da3d20518d3",
    "document_id": "full-PRO%20200%20V4-8f310261",
    "file_name": "PRO%20200%20V4.pdf",
    "extraction_file": "PRO%20200%20V4_f0e2573ccc63.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Couleur :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "7d4bcd3e706762b9",
    "document_id": "full-PRO%20200%20V4-8f310261",
    "file_name": "PRO%20200%20V4.pdf",
    "extraction_file": "PRO%20200%20V4_f0e2573ccc63.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "•  Blanc.\n•  Gris.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "05e4a3f302dd401d",
    "document_id": "full-Rustika assila_Compressed-a2177721",
    "file_name": "Rustika assila_Compressed.pdf",
    "extraction_file": "Rustika assila_Compressed_e26343052773.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les édiƟons précédentes.  diƟon 1, 2024.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "abb6a947c9597e64",
    "document_id": "full-Rustika assila_Compressed-a2177721",
    "file_name": "Rustika assila_Compressed.pdf",
    "extraction_file": "Rustika assila_Compressed_e26343052773.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Un sac peut couvrir environ 3.5m² pour épaisseur 3 à 6 mm ConsommaƟon  :",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "524dd4142eca2b0d",
    "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
    "file_name": "RUSTIKA%20GRAVITA1.pdf",
    "extraction_file": "RUSTIKA%20GRAVITA1_1d84b8dadea0.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "RUSTIKA GRAVITA  est un enduit minéral de parement hydrofugé, de texture extra- rugeuse, teinté dans la masse pour applicaƟon manuelle sur les murs extérieurs. RUSTIKA GRAVITA est classé comme morƟer de type CR CS IΙI  W1 selon  la norme NF EN998-1.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "fa9c97f5d5eb3ce6",
    "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
    "file_name": "RUSTIKA%20TYROLIEN1.pdf",
    "extraction_file": "RUSTIKA%20TYROLIEN1_db7ed13fae9e.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "RUSTIKA TYROLIEN est un enduit de parement décoraƟf en poudre, hautement hydrofugé qui s’applique à la tyrolienne. Il permet des ﬁniƟons « moucheƟs » brut ou écrasé, en intérieur et extérieur.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "456347894a551f12",
    "document_id": "full-Supcoat M_Compressed-0e58b4d7",
    "file_name": "Supcoat M_Compressed.pdf",
    "extraction_file": "Supcoat M_Compressed_d8ee2139fb3b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les édiƟons précédentes.  diƟon 1, 2024.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "03b2223adf6f43f5",
    "document_id": "full-Supcoat M_Compressed-0e58b4d7",
    "file_name": "Supcoat M_Compressed.pdf",
    "extraction_file": "Supcoat M_Compressed_d8ee2139fb3b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Extrait sec ( ISO 3251) 26.7 %",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "7e68948007e10185",
    "document_id": "full-Supcoat M_Compressed-0e58b4d7",
    "file_name": "Supcoat M_Compressed.pdf",
    "extraction_file": "Supcoat M_Compressed_d8ee2139fb3b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "0.88 g/cm\nMasse volumique (ISO 2811-1)",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "a035ba90eb7b82ba",
    "document_id": "full-Supcoat M_Compressed-0e58b4d7",
    "file_name": "Supcoat M_Compressed.pdf",
    "extraction_file": "Supcoat M_Compressed_d8ee2139fb3b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Adhérence (ISO 4624)",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "ee1f9cad3a9a2ecc",
    "document_id": "full-Supcoat M_Compressed-0e58b4d7",
    "file_name": "Supcoat M_Compressed.pdf",
    "extraction_file": "Supcoat M_Compressed_d8ee2139fb3b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "Perméabilité 0,11 kg/m²",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "1890e936b0b9e2b4",
    "document_id": "full-Supcoat M_Compressed-0e58b4d7",
    "file_name": "Supcoat M_Compressed.pdf",
    "extraction_file": "Supcoat M_Compressed_d8ee2139fb3b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "1,9 MPa rupture adhésive entre le revêtement et le support",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "14452eb1e39042d5",
    "document_id": "full-Supcoat M_Compressed-0e58b4d7",
    "file_name": "Supcoat M_Compressed.pdf",
    "extraction_file": "Supcoat M_Compressed_d8ee2139fb3b.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "3",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "8611aedfa0c5d261",
    "document_id": "full-SUPERLITE1-8227dad4",
    "file_name": "SUPERLITE1.pdf",
    "extraction_file": "SUPERLITE1_9b4ec2071c8d.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "SUPERLITE est un addiƟf hydrofuge de masse qui permet de limiter les remontées capillaires et les inﬁltraƟons d'eau dans les bétons et morƟers.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "62c4c225411ba091",
    "document_id": "full-Suplastic_Compressed-7e1bbfea",
    "file_name": "Suplastic_Compressed.pdf",
    "extraction_file": "Suplastic_Compressed_1da775a6cb76.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": ".Le présent document annule et remplace les édiƟons précédentes.  diƟon 1, 2024.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "23f6f130c4e5d8cb",
    "document_id": "full-Suplastic_Compressed-7e1bbfea",
    "file_name": "Suplastic_Compressed.pdf",
    "extraction_file": "Suplastic_Compressed_1da775a6cb76.json",
    "block_type": "paragraph",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "18",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  },
  {
    "chunk_id": "9aa14549171d9ea8",
    "document_id": "full-SUPLATEX1-c1a35954",
    "file_name": "SUPLATEX1.pdf",
    "extraction_file": "SUPLATEX1_e9af72e07e7a.json",
    "block_type": "list_item",
    "section_path": [],
    "page_start": 1,
    "page_end": 1,
    "text": "• AddiƟf pour morƟers et enduits (ciment, chaux).\n• Primaire d'adhérence avant morƟers et morƟers colles.\n•  Cure pour bétons et morƟers.",
    "parent_id": null,
    "structural_case": "before_first_recognized_heading"
  }
]
```

## Verification summary

- 221 successful extraction documents regenerated; 2,637 children and 1,115 parents.
- 239 exact null-parent children identified; all 239 accounted for in the inventory above.
- Block, source-document, section-path, and structural-cause distributions each reconcile to 239.
- Zero dangling non-null parents; zero root children with an assigned source-block parent; zero root children present in any parent's child list.
- Protected file content hashes unchanged before/after analysis. No production code, Qdrant, checkpoint, or indexing-data changes were made.
- Findings are observations and interpretations only; no implementation proposal is included.
