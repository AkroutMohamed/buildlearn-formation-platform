# Retrieval V2 held-out evaluation

## Protocol and integrity

V2 implementation/configuration was frozen before these 20 labels were created. All 20 queries use distinct source files absent from the original 34-query calibration set. Queries and evidence were authored from actual indexed payloads without retrieval feedback. The evaluator rejects changed implementation, configuration, protected pipeline or indexed corpus. No grid or tuning uses these labels. This set is now a consumed test set: future tuning requires a new independent set.

Source-disjoint does not mean language/template-disjoint: tool specifications and technical-sheet boilerplate contain near duplicates across products. Labels use exact source identity, alternative child IDs and exact full passages. Consequently unrelated useful sources may be unlabelled, and repeated boilerplate can make exact evidence matching stricter than answer relevance. This is a small positive-only evaluation, not an abstention or comprehensive relevance test.

All ranking metrics measure child evidence only, to compare like for like. Verified parent expansion runs after final selection for V2 modes and is reported separately; parents never change evidence ranks or inflate these metrics. Each mode retrieves K=5 and prefixes are measured at K=1/3/5. V1 threshold is 0.0, matching the diagnostics. V2 uses its frozen lexical-first configuration. MRR is truncated at the measured K; evidence/document recalls and Hit@K are macro-averaged, scoped to exact source identity. Identifier subsets use the corpus detector, not manually assigned labels.

```json
{
  "run_utc": "2026-09-26T12:30:05.667152+00:00",
  "implementation_sha256": "bec257494381f2d42df473c1372013fb56183b4450860565c1d9013f9fac0c48",
  "fixture_sha256": "2b1c8ab34a9e294466fe4dae48df73c5c16eb04604045df46b6d289fd822970e",
  "collection": "buildlearn_products_hierarchical_v1",
  "points": 2637,
  "collection_sha256": "61e6cd658f7edde04d3bb7312b2cc01a1535ace38f23baea277ecab679748eb4",
  "protected_files_unchanged": true,
  "collection_unchanged": true,
  "labels": 20,
  "source_overlap": 0,
  "config": {
    "dense_candidates": 100,
    "expand_parents": true,
    "lexical_candidates": 50,
    "max_parent_chars": 6000,
    "top_k": 5
  },
  "embedding_queries": 20,
  "parent_warnings": 0,
  "parent_contexts": 186
}
```

## Measured results

| Subset | Mode | K | Queries | Hit@K | Evidence recall | Document recall | MRR@K | Empty |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| all | V1 dense-only | 1 | 20 | 0.1500 | 0.1500 | 0.3000 | 0.1500 | 0 |
| all | V1 dense-only | 3 | 20 | 0.4000 | 0.4000 | 0.6000 | 0.2500 | 0 |
| all | V1 dense-only | 5 | 20 | 0.4000 | 0.4000 | 0.6500 | 0.2500 | 0 |
| all | lexical-only | 1 | 20 | 0.9000 | 0.9000 | 0.9500 | 0.9000 | 0 |
| all | lexical-only | 3 | 20 | 1.0000 | 1.0000 | 1.0000 | 0.9417 | 0 |
| all | lexical-only | 5 | 20 | 1.0000 | 1.0000 | 1.0000 | 0.9417 | 0 |
| all | identifier + lexical | 1 | 20 | 0.9000 | 0.9000 | 0.9500 | 0.9000 | 0 |
| all | identifier + lexical | 3 | 20 | 1.0000 | 1.0000 | 1.0000 | 0.9417 | 0 |
| all | identifier + lexical | 5 | 20 | 1.0000 | 1.0000 | 1.0000 | 0.9417 | 0 |
| all | full V2 | 1 | 20 | 0.9500 | 0.9500 | 1.0000 | 0.9500 | 0 |
| all | full V2 | 3 | 20 | 1.0000 | 1.0000 | 1.0000 | 0.9667 | 0 |
| all | full V2 | 5 | 20 | 1.0000 | 1.0000 | 1.0000 | 0.9667 | 0 |
| identifier | V1 dense-only | 1 | 10 | 0.2000 | 0.2000 | 0.2000 | 0.2000 | 0 |
| identifier | V1 dense-only | 3 | 10 | 0.3000 | 0.3000 | 0.5000 | 0.2500 | 0 |
| identifier | V1 dense-only | 5 | 10 | 0.3000 | 0.3000 | 0.5000 | 0.2500 | 0 |
| identifier | lexical-only | 1 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| identifier | lexical-only | 3 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| identifier | lexical-only | 5 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| identifier | identifier + lexical | 1 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| identifier | identifier + lexical | 3 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| identifier | identifier + lexical | 5 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| identifier | full V2 | 1 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| identifier | full V2 | 3 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| identifier | full V2 | 5 | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| non-identifier | V1 dense-only | 1 | 10 | 0.1000 | 0.1000 | 0.4000 | 0.1000 | 0 |
| non-identifier | V1 dense-only | 3 | 10 | 0.5000 | 0.5000 | 0.7000 | 0.2500 | 0 |
| non-identifier | V1 dense-only | 5 | 10 | 0.5000 | 0.5000 | 0.8000 | 0.2500 | 0 |
| non-identifier | lexical-only | 1 | 10 | 0.8000 | 0.8000 | 0.9000 | 0.8000 | 0 |
| non-identifier | lexical-only | 3 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.8833 | 0 |
| non-identifier | lexical-only | 5 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.8833 | 0 |
| non-identifier | identifier + lexical | 1 | 10 | 0.8000 | 0.8000 | 0.9000 | 0.8000 | 0 |
| non-identifier | identifier + lexical | 3 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.8833 | 0 |
| non-identifier | identifier + lexical | 5 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.8833 | 0 |
| non-identifier | full V2 | 1 | 10 | 0.9000 | 0.9000 | 1.0000 | 0.9000 | 0 |
| non-identifier | full V2 | 3 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.9333 | 0 |
| non-identifier | full V2 | 5 | 10 | 1.0000 | 1.0000 | 1.0000 | 0.9333 | 0 |

## Interpretation

Held-out evidence recall@3: V1 40.00%, lexical-only 100.00%, identifier + lexical 100.00%, full V2 100.00%. Full V2 changes evidence recall@3 versus lexical-only by +0.00%. Interpret the dense branch's contribution using that measured difference, not the architecture diagram. No post-test weights, candidate budgets or normalization were changed.

V1 remains the existing baseline and is neither replaced nor wired to an endpoint. The separate V2 service is reviewable for adoption; these results do not justify an LLM integration or claim universal quality. Retain source and provenance diagnostics, and use a fresh evaluation set before any further ranking tuning.

The dense branch adds no evidence recall@3 here, but improves overall Hit@1 from lexical-only's 90% to V2's 95%, and MRR@3 from 0.9417 to 0.9667. For identifier queries all lexical/V2 modes already reach 100% Hit@1; the dense contribution occurs in the non-identifier subset. Identifier route priority adds no measured gain over lexical-only on this set. These outcomes support the separate lexical-first path while limiting claims about additional branch benefits.

## Executed validation

Final regression result: **374 passed, 0 failures**, including **19 new V2 offline tests**, in 7.16 seconds. There were 1,824 existing datetime/fixture deprecation warnings. The initial focused selection passed 113 tests. No implementation changes were made after the held-out freeze or in response to held-out results.

```powershell
.\venv\Scripts\python.exe -B -m pytest tests/ai/test_retrieval_v2.py tests/ai/test_hierarchical_retrieval_eval.py tests/ai/test_retriever.py tests/ai/test_context_builder.py tests/ai/test_embeddings.py tests/ai/test_vectorstore.py tests/ai/test_hierarchical_retriever.py tests/ai/test_hierarchical_indexer.py tests/ai/test_hierarchical_pipeline.py tests/ai/test_technical_chunker.py tests/ai/test_hierarchical_chunker.py tests/ai/test_rag_service.py tests/ai/test_llm_provider.py tests/ai/rag -q -p no:cacheprovider --basetemp C:\Users\user\Desktop\stage\.tmp\v2_regression --tb=short
```

Only the separate V2 implementation, new tests/fixture, evaluation script, and the two substantial V2 documents were added. The running Qdrant server can append read-request logs; collection content and protected source/checkpoint artifacts remained unchanged.

## Frozen held-out labels

```json
[
  {
    "id": "HV2-01",
    "query": "Que contient FINACEM CACHET BLEU et combien de mois peut-on le conserver ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "chunk_ids": [
          "00c8d2bdbddae924"
        ],
        "substring": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec."
      }
    ]
  },
  {
    "id": "HV2-02",
    "query": "Quel volume d’eau utiliser pour un sac de 25 kg de SOFAPCOL PRO 2000 ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "file_name": "Pro 2000_Compressed.pdf",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "chunk_ids": [
          "02f208fac8dbb8fd"
        ],
        "substring": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
      }
    ]
  },
  {
    "id": "HV2-03",
    "query": "Comment mélanger les composants de CEM PRO FLEX 100 W PROTECTION et appliquer les couches ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "chunk_ids": [
          "060897ea2a172b7a"
        ],
        "substring": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
      }
    ]
  },
  {
    "id": "HV2-04",
    "query": "Quel couple maximal et quel diamètre de mandrin a la perceuse ECIDL208689 ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "chunk_ids": [
          "076ff7276b9dc660"
        ],
        "substring": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V"
      }
    ]
  },
  {
    "id": "HV2-05",
    "query": "La meuleuse ELAG4108112 a-t-elle une protection contre le redémarrage ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "chunk_ids": [
          "07b34086a7c41e34"
        ],
        "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W"
      }
    ]
  },
  {
    "id": "HV2-06",
    "query": "En quel acier sont fabriquées les douilles EMSS12102L ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "chunk_ids": [
          "0a001bc9ecfb185c"
        ],
        "substring": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail."
      }
    ]
  },
  {
    "id": "HV2-07",
    "query": "À quel DTU se référer pour préparer les supports de RUSTIKA TYROLIEN ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "chunk_ids": [
          "141e0f1f0585631f"
        ],
        "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
      }
    ]
  },
  {
    "id": "HV2-08",
    "query": "Combien de types de mandrins sont fournis avec EMAT5541 ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "chunk_ids": [
          "16c3b9f4450fb430"
        ],
        "substring": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules"
      }
    ]
  },
  {
    "id": "HV2-09",
    "query": "Quels supports sont interdits pour ISBAROC R selon sa fiche R1 ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "file_name": "ISBAROC%20R1.pdf",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "chunk_ids": [
          "1977a381add0de0f"
        ],
        "substring": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
      }
    ]
  },
  {
    "id": "HV2-10",
    "query": "LIKA FULL est-il prévu pour une application manuelle ou mécanique, et sur quels murs ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-FULL-88a1b942",
        "file_name": "FULL.pdf",
        "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
        "chunk_ids": [
          "1aa4f45f7ad68d38"
        ],
        "substring": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
      }
    ]
  },
  {
    "id": "HV2-11",
    "query": "HYDRO FAÇADE laisse-t-il des taches blanches et modifie-t-il la perméabilité à la vapeur ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "chunk_ids": [
          "1cdfe98fdc496aa3"
        ],
        "substring": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:"
      }
    ]
  },
  {
    "id": "HV2-12",
    "query": "Quel couple maximal et combien de vitesses mécaniques offre ECIDL426981 ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "chunk_ids": [
          "23b329e12ef306c3"
        ],
        "substring": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
      }
    ]
  },
  {
    "id": "HV2-13",
    "query": "Quels dispositifs du touret EBGR61501 protègent les yeux et empêchent la poussière d’entrer ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "chunk_ids": [
          "2d13aad6e3293d4f"
        ],
        "substring": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W"
      }
    ]
  },
  {
    "id": "HV2-14",
    "query": "Pour quel type de structures les consommables EEWSFC08101 sont-ils destinés ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "chunk_ids": [
          "2d2de2c8733e630e"
        ],
        "substring": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
      }
    ]
  },
  {
    "id": "HV2-15",
    "query": "Dans quel état doivent être les fonds avant MURENDUIT V et quel DTU appliquer ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "chunk_ids": [
          "38c9503e6e3dc893"
        ],
        "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      }
    ]
  },
  {
    "id": "HV2-16",
    "query": "FINACEM CACHET ROUGE convient-il au rebouchage intérieur et à la pose manuelle ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "chunk_ids": [
          "3bc67ce5710b3476"
        ],
        "substring": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
      }
    ]
  },
  {
    "id": "HV2-17",
    "query": "HYDROMUR R peut-il être utilisé sur une surface déjà peinte ou un support horizontal ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "file_name": "hydromur%20R%20V4.pdf",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "chunk_ids": [
          "3d78bc891b779755"
        ],
        "substring": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      }
    ]
  },
  {
    "id": "HV2-18",
    "query": "Quelle tension et quelle puissance maximale sont indiquées pour ELAG2120252 ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "chunk_ids": [
          "4035aaf42a8f2aec"
        ],
        "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W"
      }
    ]
  },
  {
    "id": "HV2-19",
    "query": "Quel couple maximal et quelle vitesse à vide donne la clé EATL12001 ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "chunk_ids": [
          "417a91277e2fa7fb"
        ],
        "substring": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
      }
    ]
  },
  {
    "id": "HV2-20",
    "query": "Quel couple maximal et quel réglage de positions offre ECIDL208682 ?",
    "categories": [
      "held-out"
    ],
    "evidence": [
      {
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "chunk_ids": [
          "4443ce1dbfc8797c"
        ],
        "substring": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V"
      }
    ]
  }
]
```

## Every query and returned evidence

Provenance fields distinguish reranking score from COSINE similarity; absent dense scores/ranks are null, never fabricated. Candidate union is available from the service; this report records final top-five evidence and query analysis.

```json
{
  "query_id": "HV2-01",
  "query": "Que contient FINACEM CACHET BLEU et combien de mois peut-on le conserver ?",
  "expected": [
    {
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "chunk_ids": [
        "00c8d2bdbddae924"
      ],
      "substring": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "99cc92ba87a42ea0",
      "score": 0.70925367,
      "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "99cc92ba87a42ea0",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs."
      }
    },
    {
      "chunk_id": "bd2830ec79c8c28d",
      "score": 0.67461133,
      "text": "Conservation :\no 12 mois en emballage d'origine fermé à l’abri de l’'humidité.",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "file_name": "ISBAROC-R.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
      "parent_id": "5d206368c625978e",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "bd2830ec79c8c28d",
        "document_id": "full-ISBAROC-R-3a4b4eb9",
        "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
        "file_name": "ISBAROC-R.pdf",
        "parent_id": "5d206368c625978e",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conservation :\no 12 mois en emballage d'origine fermé à l’abri de l’'humidité."
      }
    },
    {
      "chunk_id": "c61b2702ba910c19",
      "score": 0.66480017,
      "text": "Durée de conservation :\n° 6 mois en emballage d’origine fermé à l’abri de l’humidité.",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
      "parent_id": "e6f68dfdf81aa764",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "c61b2702ba910c19",
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "parent_id": "e6f68dfdf81aa764",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Durée de conservation :\n° 6 mois en emballage d’origine fermé à l’abri de l’humidité."
      }
    },
    {
      "chunk_id": "01f93d1eac95a9e9",
      "score": 0.6629187,
      "text": "•  Le JIR PRO TANCHE s’applique à la brosse ou au rouleau à poil long en deux couches croisées avec un pinceau à rechampir charger les coins.",
      "document_id": "full-jir%20pro%20etanche1-7c9a4574",
      "file_name": "jir%20pro%20etanche1.pdf",
      "source_path": "ai_data\\raw\\sofap\\jir%20pro%20etanche1.pdf",
      "parent_id": "1b92a2f13da77008",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "01f93d1eac95a9e9",
        "document_id": "full-jir%20pro%20etanche1-7c9a4574",
        "source_path": "ai_data\\raw\\sofap\\jir%20pro%20etanche1.pdf",
        "file_name": "jir%20pro%20etanche1.pdf",
        "parent_id": "1b92a2f13da77008",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "•  Le JIR PRO TANCHE s’applique à la brosse ou au rouleau à poil long en deux couches croisées avec un pinceau à rechampir charger les coins."
      }
    },
    {
      "chunk_id": "3bc67ce5710b3476",
      "score": 0.6603399,
      "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs.",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "3bc67ce5710b3476",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-01",
  "query": "Que contient FINACEM CACHET BLEU et combien de mois peut-on le conserver ?",
  "expected": [
    {
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "chunk_ids": [
        "00c8d2bdbddae924"
      ],
      "substring": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec."
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "67f066024d5bc422",
      "score": 0.7074547022937835,
      "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être nivelé, stable, propre, sans la présence de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer  FINACEM  CACHET  BLEU  dans  environ   2.3L d’eau pour 5 kg  de  poudre,  puis  mélanger  à  la  main ou à l’aide  d’un  malaxeur  jusqu’à l’obtention d’une pâte homo- -gène à la consistance souhaitée.\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\n• Il  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Répandre le produit sur la surface avec une spatule lisse pour assurer  une répartition et une couverture complète de la surface.\n• Le  produit  est  appliqué  d’un  à  deux  couches  pour une épaisseur  jusqu’à 2 à 3 mm.\n• Appliquer  une deuxième couche après le durcissement de la  première  ( après  2  à  24  heures )  en croisant le sens de l’application.\n• Lorsque  l’enduit  de  ﬁnition  commence  à  durcir,  lisser à l’aide d’une taloche lisseuse.\n• La  peinture  sera  appliquée lorsque le  taux d’humidité de support est inférieur à 5%.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "67f066024d5bc422",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être nivelé, stable, propre, sans la présence de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer  FINACEM  CACHET  BLEU  dans  environ   2.3L d’eau pour 5 kg  de  poudre,  puis  mélanger  à  la  main ou à l’aide  d’un  malaxeur  jusqu’à l’obtention d’une pâte homo- -gène à la consistance souhaitée.\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\n• Il  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Répandre le produit sur la surface avec une spatule lisse pour assurer  une répartition et une couverture complète de la surface.\n• Le  produit  est  appliqué  d’un  à  deux  couches  pour une épaisseur  jusqu’à 2 à 3 mm.\n• Appliquer  une deuxième couche après le durcissement de la  première  ( après  2  à  24  heures )  en croisant le sens de l’application.\n• Lorsque  l’enduit  de  ﬁnition  commence  à  durcir,  lisser à l’aide d’une taloche lisseuse.\n• La  peinture  sera  appliquée lorsque le  taux d’humidité de support est inférieur à 5%."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7074547022937835,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.4217404165794978,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "99cc92ba87a42ea0",
      "score": 0.7074547022937835,
      "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "99cc92ba87a42ea0",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7074547022937835,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.4217404165794978,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "00c8d2bdbddae924",
      "score": 0.6703633622654468,
      "text": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "00c8d2bdbddae924",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6703633622654468,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.38464907655116104,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1b1da5c657368fe8",
      "score": 0.5478192804462161,
      "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1b1da5c657368fe8",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5478192804462161,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.2621049947319304,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "25d3d28bc0c33872",
      "score": 0.5478192804462161,
      "text": "Temps de mise en peinture Après séchage complet",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "25d3d28bc0c33872",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Temps de mise en peinture Après séchage complet"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5478192804462161,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.2621049947319304,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "bleu",
      "cachet",
      "combien",
      "conserver",
      "contient",
      "de",
      "et",
      "finacem",
      "le",
      "mois",
      "on",
      "peut",
      "que"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "0ea9ff06e37f196f"
  ]
}
```

```json
{
  "query_id": "HV2-01",
  "query": "Que contient FINACEM CACHET BLEU et combien de mois peut-on le conserver ?",
  "expected": [
    {
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "chunk_ids": [
        "00c8d2bdbddae924"
      ],
      "substring": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "67f066024d5bc422",
      "score": 0.7074547022937835,
      "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être nivelé, stable, propre, sans la présence de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer  FINACEM  CACHET  BLEU  dans  environ   2.3L d’eau pour 5 kg  de  poudre,  puis  mélanger  à  la  main ou à l’aide  d’un  malaxeur  jusqu’à l’obtention d’une pâte homo- -gène à la consistance souhaitée.\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\n• Il  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Répandre le produit sur la surface avec une spatule lisse pour assurer  une répartition et une couverture complète de la surface.\n• Le  produit  est  appliqué  d’un  à  deux  couches  pour une épaisseur  jusqu’à 2 à 3 mm.\n• Appliquer  une deuxième couche après le durcissement de la  première  ( après  2  à  24  heures )  en croisant le sens de l’application.\n• Lorsque  l’enduit  de  ﬁnition  commence  à  durcir,  lisser à l’aide d’une taloche lisseuse.\n• La  peinture  sera  appliquée lorsque le  taux d’humidité de support est inférieur à 5%.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "67f066024d5bc422",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être nivelé, stable, propre, sans la présence de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer  FINACEM  CACHET  BLEU  dans  environ   2.3L d’eau pour 5 kg  de  poudre,  puis  mélanger  à  la  main ou à l’aide  d’un  malaxeur  jusqu’à l’obtention d’une pâte homo- -gène à la consistance souhaitée.\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\n• Il  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Répandre le produit sur la surface avec une spatule lisse pour assurer  une répartition et une couverture complète de la surface.\n• Le  produit  est  appliqué  d’un  à  deux  couches  pour une épaisseur  jusqu’à 2 à 3 mm.\n• Appliquer  une deuxième couche après le durcissement de la  première  ( après  2  à  24  heures )  en croisant le sens de l’application.\n• Lorsque  l’enduit  de  ﬁnition  commence  à  durcir,  lisser à l’aide d’une taloche lisseuse.\n• La  peinture  sera  appliquée lorsque le  taux d’humidité de support est inférieur à 5%."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7074547022937835,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.4217404165794978,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "99cc92ba87a42ea0",
      "score": 0.7074547022937835,
      "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "99cc92ba87a42ea0",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7074547022937835,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.4217404165794978,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "00c8d2bdbddae924",
      "score": 0.6703633622654468,
      "text": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "00c8d2bdbddae924",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6703633622654468,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.38464907655116104,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1b1da5c657368fe8",
      "score": 0.5478192804462161,
      "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1b1da5c657368fe8",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Tèl.:  (+216) 74 453 983 / (+216) 74 453 984 / (+216) 71 100 803 E-mail: contact@sofap-poudre.com / www.sofapbatiment.com"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5478192804462161,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.2621049947319304,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "25d3d28bc0c33872",
      "score": 0.5478192804462161,
      "text": "Temps de mise en peinture Après séchage complet",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "25d3d28bc0c33872",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Temps de mise en peinture Après séchage complet"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5478192804462161,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.2621049947319304,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "bleu",
      "cachet",
      "combien",
      "conserver",
      "contient",
      "de",
      "et",
      "finacem",
      "le",
      "mois",
      "on",
      "peut",
      "que"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "0ea9ff06e37f196f"
  ]
}
```

```json
{
  "query_id": "HV2-01",
  "query": "Que contient FINACEM CACHET BLEU et combien de mois peut-on le conserver ?",
  "expected": [
    {
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "chunk_ids": [
        "00c8d2bdbddae924"
      ],
      "substring": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec."
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "99cc92ba87a42ea0",
      "score": 0.7074547022937835,
      "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "99cc92ba87a42ea0",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs."
      },
      "dense_score": 0.70925367,
      "dense_rank": 1,
      "lexical_score": 0.7074547022937835,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.4217404165794978,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "67f066024d5bc422",
      "score": 0.7074547022937835,
      "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être nivelé, stable, propre, sans la présence de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer  FINACEM  CACHET  BLEU  dans  environ   2.3L d’eau pour 5 kg  de  poudre,  puis  mélanger  à  la  main ou à l’aide  d’un  malaxeur  jusqu’à l’obtention d’une pâte homo- -gène à la consistance souhaitée.\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\n• Il  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Répandre le produit sur la surface avec une spatule lisse pour assurer  une répartition et une couverture complète de la surface.\n• Le  produit  est  appliqué  d’un  à  deux  couches  pour une épaisseur  jusqu’à 2 à 3 mm.\n• Appliquer  une deuxième couche après le durcissement de la  première  ( après  2  à  24  heures )  en croisant le sens de l’application.\n• Lorsque  l’enduit  de  ﬁnition  commence  à  durcir,  lisser à l’aide d’une taloche lisseuse.\n• La  peinture  sera  appliquée lorsque le  taux d’humidité de support est inférieur à 5%.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "67f066024d5bc422",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être nivelé, stable, propre, sans la présence de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer  FINACEM  CACHET  BLEU  dans  environ   2.3L d’eau pour 5 kg  de  poudre,  puis  mélanger  à  la  main ou à l’aide  d’un  malaxeur  jusqu’à l’obtention d’une pâte homo- -gène à la consistance souhaitée.\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\n• Il  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Répandre le produit sur la surface avec une spatule lisse pour assurer  une répartition et une couverture complète de la surface.\n• Le  produit  est  appliqué  d’un  à  deux  couches  pour une épaisseur  jusqu’à 2 à 3 mm.\n• Appliquer  une deuxième couche après le durcissement de la  première  ( après  2  à  24  heures )  en croisant le sens de l’application.\n• Lorsque  l’enduit  de  ﬁnition  commence  à  durcir,  lisser à l’aide d’une taloche lisseuse.\n• La  peinture  sera  appliquée lorsque le  taux d’humidité de support est inférieur à 5%."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7074547022937835,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.4217404165794978,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "00c8d2bdbddae924",
      "score": 0.6703633622654468,
      "text": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "00c8d2bdbddae924",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Très ﬁn.\n• Glisse renforcée.\n• Application facile.\n• Excellente adhérence.\n• Maniabilité facile.\n• Faible absorption des peintures.\n• Blancheur élevée. Composition :\n• Ciment blanc.\n• Charges minérales.\n• Additifs spéciﬁques. Conservation :\n• 10 mois dans l’emballage d’origine en endroit sec."
      },
      "dense_score": 0.65017045,
      "dense_rank": 45,
      "lexical_score": 0.6703633622654468,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.38464907655116104,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4d21807911762050",
      "score": 0.5478192804462161,
      "text": "Conseil :",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d21807911762050",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conseil :"
      },
      "dense_score": 0.6545391,
      "dense_rank": 10,
      "lexical_score": 0.5478192804462161,
      "lexical_rank": 10,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.2621049947319304,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "37fc65c352e3bf03",
      "score": 0.5478192804462161,
      "text": "Bleu",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "37fc65c352e3bf03",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Bleu"
      },
      "dense_score": 0.6449028,
      "dense_rank": 52,
      "lexical_score": 0.5478192804462161,
      "lexical_rank": 8,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.2621049947319304,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "bleu",
      "cachet",
      "combien",
      "conserver",
      "contient",
      "de",
      "et",
      "finacem",
      "le",
      "mois",
      "on",
      "peut",
      "que"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "0ea9ff06e37f196f"
  ]
}
```

```json
{
  "query_id": "HV2-02",
  "query": "Quel volume d’eau utiliser pour un sac de 25 kg de SOFAPCOL PRO 2000 ?",
  "expected": [
    {
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "chunk_ids": [
        "02f208fac8dbb8fd"
      ],
      "substring": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "85aa3643e2d06a94",
      "score": 0.78473735,
      "text": "• Verser la quanƟté d’eau env. 6.25 litres d’eau par sac de 25 kg d’enduit dans un récipient adapté (auge de maçon par exemple),",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "file_name": "LIKA%20FINA1.pdf",
      "source_path": "ai_data\\raw\\sofap\\LIKA%20FINA1.pdf",
      "parent_id": "0c04269a2bbdf29e",
      "section_path": [
        "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "85aa3643e2d06a94",
        "document_id": "full-LIKA%20FINA1-890840ee",
        "source_path": "ai_data\\raw\\sofap\\LIKA%20FINA1.pdf",
        "file_name": "LIKA%20FINA1.pdf",
        "parent_id": "0c04269a2bbdf29e",
        "section_path": [
          "•  EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Verser la quanƟté d’eau env. 6.25 litres d’eau par sac de 25 kg d’enduit dans un récipient adapté (auge de maçon par exemple),"
      }
    },
    {
      "chunk_id": "c08f4c92cc8e8a8a",
      "score": 0.7841444,
      "text": "Sac de 25 kg.\nPaleƩe houssée contre l’humidité de 1.6 tonnes soit 64 sacs de 25 kg.\nEmballage :",
      "document_id": "full-Rustika assila_Compressed-a2177721",
      "file_name": "Rustika assila_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Rustika assila_Compressed.pdf",
      "parent_id": "c697c854d1a351f8",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "c08f4c92cc8e8a8a",
        "document_id": "full-Rustika assila_Compressed-a2177721",
        "source_path": "ai_data\\raw\\sofap\\Rustika assila_Compressed.pdf",
        "file_name": "Rustika assila_Compressed.pdf",
        "parent_id": "c697c854d1a351f8",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Sac de 25 kg.\nPaleƩe houssée contre l’humidité de 1.6 tonnes soit 64 sacs de 25 kg.\nEmballage :"
      }
    },
    {
      "chunk_id": "5f5e5f914d8ac87e",
      "score": 0.7819142,
      "text": "Sac de 25 kg.\nPaleƩe houssée contre l’humidité de 1.6 tonnes soit 64 sacs de 25 kg.",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
      "parent_id": "81853e114b8e13ee",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "5f5e5f914d8ac87e",
        "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
        "file_name": "RUSTIKA%20GRAVITA1.pdf",
        "parent_id": "81853e114b8e13ee",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Sac de 25 kg.\nPaleƩe houssée contre l’humidité de 1.6 tonnes soit 64 sacs de 25 kg."
      }
    },
    {
      "chunk_id": "77736c0745034455",
      "score": 0.77874243,
      "text": "• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 3000 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "file_name": "Pro 3000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 3000_Compressed.pdf",
      "parent_id": "ea99f879c4ed09cd_1",
      "section_path": [
        "PRO 3000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "77736c0745034455",
        "document_id": "full-Pro 3000_Compressed-94812339",
        "source_path": "ai_data\\raw\\sofap\\Pro 3000_Compressed.pdf",
        "file_name": "Pro 3000_Compressed.pdf",
        "parent_id": "ea99f879c4ed09cd_1",
        "section_path": [
          "PRO 3000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 3000 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
      }
    },
    {
      "chunk_id": "a91a20d4d58b4977",
      "score": 0.77861,
      "text": "• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 200 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon.",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "file_name": "PRO%20200%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
      "parent_id": "fd83189584fcb7fb",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "a91a20d4d58b4977",
        "document_id": "full-PRO%20200%20V4-8f310261",
        "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
        "file_name": "PRO%20200%20V4.pdf",
        "parent_id": "fd83189584fcb7fb",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 200 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-02",
  "query": "Quel volume d’eau utiliser pour un sac de 25 kg de SOFAPCOL PRO 2000 ?",
  "expected": [
    {
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "chunk_ids": [
        "02f208fac8dbb8fd"
      ],
      "substring": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "02f208fac8dbb8fd",
      "score": 1.7566114661319565,
      "text": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "ccda60f1c450e8f5_1",
      "section_path": [
        "PRO 2000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "02f208fac8dbb8fd",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "ccda60f1c450e8f5_1",
        "section_path": [
          "PRO 2000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.7566114661319565,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "705d59bcdca1881d",
      "score": 1.4932434501719074,
      "text": "de gâchage : E | nviron 25 %\ne de malaxage : E | nviron 3 min\nps de maturaƟon : E | nviron 5 min\nps ouvert : E | nviron 30 min\ne praƟque d’uƟlisaƟon : E | nviron 3 heures\n\nis avant jointoiement : | Minimum 24 heures\n\nssibilité : 2 | 4à 48 h après réalisaƟon des joints\n\nmballage : | Sac de 25 kg.",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "0f515b202953b67b",
      "section_path": [
        "PRO 2000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "table",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "705d59bcdca1881d",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "0f515b202953b67b",
        "section_path": [
          "PRO 2000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "table",
        "text": "de gâchage : E | nviron 25 %\ne de malaxage : E | nviron 3 min\nps de maturaƟon : E | nviron 5 min\nps ouvert : E | nviron 30 min\ne praƟque d’uƟlisaƟon : E | nviron 3 heures\n\nis avant jointoiement : | Minimum 24 heures\n\nssibilité : 2 | 4à 48 h après réalisaƟon des joints\n\nmballage : | Sac de 25 kg."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4932434501719074,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.3682434501719074,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d87abf8b0dbf4989",
      "score": 1.4274146571512643,
      "text": "Emballage :\nSac de  25 kg.",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "45b75f7c82f4c9c9",
      "section_path": [
        "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d87abf8b0dbf4989",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "45b75f7c82f4c9c9",
        "section_path": [
          "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Emballage :\nSac de  25 kg."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4274146571512643,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.30241465715126425,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "60fc2c8ee52b2b95",
      "score": 1.2566114661319565,
      "text": "• Les supports doivent être propres , sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n• Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours, les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO1000 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon.",
      "document_id": "full-PRO%201000%20V2-467bc232",
      "file_name": "PRO%201000%20V2.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%201000%20V2.pdf",
      "parent_id": "bd1c9854cbb486b3",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "60fc2c8ee52b2b95",
        "document_id": "full-PRO%201000%20V2-467bc232",
        "source_path": "ai_data\\raw\\sofap\\PRO%201000%20V2.pdf",
        "file_name": "PRO%201000%20V2.pdf",
        "parent_id": "bd1c9854cbb486b3",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être propres , sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n• Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours, les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO1000 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2566114661319565,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.5,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "a91a20d4d58b4977",
      "score": 1.2566114661319565,
      "text": "• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 200 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon.",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "file_name": "PRO%20200%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
      "parent_id": "fd83189584fcb7fb",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "a91a20d4d58b4977",
        "document_id": "full-PRO%20200%20V4-8f310261",
        "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
        "file_name": "PRO%20200%20V4.pdf",
        "parent_id": "fd83189584fcb7fb",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 200 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2566114661319565,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.5,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "2000",
      "25",
      "d",
      "de",
      "eau",
      "kg",
      "pour",
      "pro",
      "quel",
      "sac",
      "sofapcol",
      "un",
      "utiliser",
      "volume"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "ccda60f1c450e8f5_1",
    "0f515b202953b67b",
    "45b75f7c82f4c9c9",
    "bd1c9854cbb486b3",
    "fd83189584fcb7fb"
  ]
}
```

```json
{
  "query_id": "HV2-02",
  "query": "Quel volume d’eau utiliser pour un sac de 25 kg de SOFAPCOL PRO 2000 ?",
  "expected": [
    {
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "chunk_ids": [
        "02f208fac8dbb8fd"
      ],
      "substring": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "02f208fac8dbb8fd",
      "score": 1.7566114661319565,
      "text": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "ccda60f1c450e8f5_1",
      "section_path": [
        "PRO 2000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "02f208fac8dbb8fd",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "ccda60f1c450e8f5_1",
        "section_path": [
          "PRO 2000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.7566114661319565,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "705d59bcdca1881d",
      "score": 1.4932434501719074,
      "text": "de gâchage : E | nviron 25 %\ne de malaxage : E | nviron 3 min\nps de maturaƟon : E | nviron 5 min\nps ouvert : E | nviron 30 min\ne praƟque d’uƟlisaƟon : E | nviron 3 heures\n\nis avant jointoiement : | Minimum 24 heures\n\nssibilité : 2 | 4à 48 h après réalisaƟon des joints\n\nmballage : | Sac de 25 kg.",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "0f515b202953b67b",
      "section_path": [
        "PRO 2000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "table",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "705d59bcdca1881d",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "0f515b202953b67b",
        "section_path": [
          "PRO 2000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "table",
        "text": "de gâchage : E | nviron 25 %\ne de malaxage : E | nviron 3 min\nps de maturaƟon : E | nviron 5 min\nps ouvert : E | nviron 30 min\ne praƟque d’uƟlisaƟon : E | nviron 3 heures\n\nis avant jointoiement : | Minimum 24 heures\n\nssibilité : 2 | 4à 48 h après réalisaƟon des joints\n\nmballage : | Sac de 25 kg."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4932434501719074,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.3682434501719074,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d87abf8b0dbf4989",
      "score": 1.4274146571512643,
      "text": "Emballage :\nSac de  25 kg.",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "45b75f7c82f4c9c9",
      "section_path": [
        "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d87abf8b0dbf4989",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "45b75f7c82f4c9c9",
        "section_path": [
          "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Emballage :\nSac de  25 kg."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4274146571512643,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.30241465715126425,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "60fc2c8ee52b2b95",
      "score": 1.2566114661319565,
      "text": "• Les supports doivent être propres , sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n• Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours, les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO1000 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon.",
      "document_id": "full-PRO%201000%20V2-467bc232",
      "file_name": "PRO%201000%20V2.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%201000%20V2.pdf",
      "parent_id": "bd1c9854cbb486b3",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "60fc2c8ee52b2b95",
        "document_id": "full-PRO%201000%20V2-467bc232",
        "source_path": "ai_data\\raw\\sofap\\PRO%201000%20V2.pdf",
        "file_name": "PRO%201000%20V2.pdf",
        "parent_id": "bd1c9854cbb486b3",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être propres , sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n• Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours, les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO1000 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2566114661319565,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.5,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "a91a20d4d58b4977",
      "score": 1.2566114661319565,
      "text": "• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 200 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon.",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "file_name": "PRO%20200%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
      "parent_id": "fd83189584fcb7fb",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "a91a20d4d58b4977",
        "document_id": "full-PRO%20200%20V4-8f310261",
        "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
        "file_name": "PRO%20200%20V4.pdf",
        "parent_id": "fd83189584fcb7fb",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 200 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2566114661319565,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.5,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "2000",
      "25",
      "d",
      "de",
      "eau",
      "kg",
      "pour",
      "pro",
      "quel",
      "sac",
      "sofapcol",
      "un",
      "utiliser",
      "volume"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "ccda60f1c450e8f5_1",
    "0f515b202953b67b",
    "45b75f7c82f4c9c9",
    "bd1c9854cbb486b3",
    "fd83189584fcb7fb"
  ]
}
```

```json
{
  "query_id": "HV2-02",
  "query": "Quel volume d’eau utiliser pour un sac de 25 kg de SOFAPCOL PRO 2000 ?",
  "expected": [
    {
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "chunk_ids": [
        "02f208fac8dbb8fd"
      ],
      "substring": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "02f208fac8dbb8fd",
      "score": 1.7566114661319565,
      "text": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "ccda60f1c450e8f5_1",
      "section_path": [
        "PRO 2000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "02f208fac8dbb8fd",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "ccda60f1c450e8f5_1",
        "section_path": [
          "PRO 2000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "•  Les supports doivent être propres, sains et solides (les supports à base de ciment ne doivent pas ressuer l’humidité).\n•  Les dallages doivent être réalisés depuis plus d’un mois, les chapes ciment depuis plus de 15 jours et les enduits de ciment depuis plus de 48 heures.\n• Par temps chaud et/ou vent fort, ces supports seront humidiﬁés quelques heures avant la pose.\n• L’humidiﬁcaƟon des supports en béton cellulaire est impéraƟve avant de commencer la pose du morƟer. PréparaƟon du produit :\n• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 2000 en malaxant jusqu’à l’obtenƟon  d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
      },
      "dense_score": 0.67313683,
      "dense_rank": 53,
      "lexical_score": 1.7566114661319565,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "705d59bcdca1881d",
      "score": 1.4932434501719074,
      "text": "de gâchage : E | nviron 25 %\ne de malaxage : E | nviron 3 min\nps de maturaƟon : E | nviron 5 min\nps ouvert : E | nviron 30 min\ne praƟque d’uƟlisaƟon : E | nviron 3 heures\n\nis avant jointoiement : | Minimum 24 heures\n\nssibilité : 2 | 4à 48 h après réalisaƟon des joints\n\nmballage : | Sac de 25 kg.",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "0f515b202953b67b",
      "section_path": [
        "PRO 2000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "table",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "705d59bcdca1881d",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "0f515b202953b67b",
        "section_path": [
          "PRO 2000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "table",
        "text": "de gâchage : E | nviron 25 %\ne de malaxage : E | nviron 3 min\nps de maturaƟon : E | nviron 5 min\nps ouvert : E | nviron 30 min\ne praƟque d’uƟlisaƟon : E | nviron 3 heures\n\nis avant jointoiement : | Minimum 24 heures\n\nssibilité : 2 | 4à 48 h après réalisaƟon des joints\n\nmballage : | Sac de 25 kg."
      },
      "dense_score": 0.650262,
      "dense_rank": 90,
      "lexical_score": 1.4932434501719074,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.3682434501719074,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d87abf8b0dbf4989",
      "score": 1.4274146571512643,
      "text": "Emballage :\nSac de  25 kg.",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "45b75f7c82f4c9c9",
      "section_path": [
        "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d87abf8b0dbf4989",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "45b75f7c82f4c9c9",
        "section_path": [
          "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Emballage :\nSac de  25 kg."
      },
      "dense_score": 0.7058703,
      "dense_rank": 26,
      "lexical_score": 1.4274146571512643,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 1.0,
      "word_match": 0.30241465715126425,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "77736c0745034455",
      "score": 1.2566114661319565,
      "text": "• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 3000 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :",
      "document_id": "full-Pro 3000_Compressed-94812339",
      "file_name": "Pro 3000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 3000_Compressed.pdf",
      "parent_id": "ea99f879c4ed09cd_1",
      "section_path": [
        "PRO 3000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "77736c0745034455",
        "document_id": "full-Pro 3000_Compressed-94812339",
        "source_path": "ai_data\\raw\\sofap\\Pro 3000_Compressed.pdf",
        "file_name": "Pro 3000_Compressed.pdf",
        "parent_id": "ea99f879c4ed09cd_1",
        "section_path": [
          "PRO 3000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Dans un récipient contenant environ 6.25 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 3000 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon. ApplicaƟon :"
      },
      "dense_score": 0.77874243,
      "dense_rank": 4,
      "lexical_score": 1.2566114661319565,
      "lexical_rank": 6,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.5,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "a91a20d4d58b4977",
      "score": 1.2566114661319565,
      "text": "• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 200 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon.",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "file_name": "PRO%20200%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
      "parent_id": "fd83189584fcb7fb",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "a91a20d4d58b4977",
        "document_id": "full-PRO%20200%20V4-8f310261",
        "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
        "file_name": "PRO%20200%20V4.pdf",
        "parent_id": "fd83189584fcb7fb",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Dans un récipient contenant environ 4.75 Litres d’eau propre, verser un sac de 25 kg de SOFAPCOL PRO 200 en malaxant jusqu’à l’obtenƟon d’un mélange homogène (uƟliser de préférence un malaxeur électrique).\n• Laisser reposer quelques minutes puis malaxer de nouveau avant l’applicaƟon."
      },
      "dense_score": 0.77861,
      "dense_rank": 5,
      "lexical_score": 1.2566114661319565,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.5,
      "word_match": 0.6316114661319565,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "2000",
      "25",
      "d",
      "de",
      "eau",
      "kg",
      "pour",
      "pro",
      "quel",
      "sac",
      "sofapcol",
      "un",
      "utiliser",
      "volume"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "ccda60f1c450e8f5_1",
    "0f515b202953b67b",
    "45b75f7c82f4c9c9",
    "ea99f879c4ed09cd_1",
    "fd83189584fcb7fb"
  ]
}
```

```json
{
  "query_id": "HV2-03",
  "query": "Comment mélanger les composants de CEM PRO FLEX 100 W PROTECTION et appliquer les couches ?",
  "expected": [
    {
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "chunk_ids": [
        "060897ea2a172b7a"
      ],
      "substring": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.5,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.5,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1721fac74c537e14",
      "score": 0.83049893,
      "text": "• CEM  PRO-FLEX  100  W   PROTECTION   est   un  mortier d’étanchéité ﬂexible présenté en kit prédosé à deux compo- -sants.  Il  se  compose  d’un  mortier  de  poudre  à   base de ciment (composant A) et émulsion de résine (composant B). Après mélange, on obtient un mortier applicable au rouleau, à la brosse, à la taloche, ou par pulvérisation.\n• CEM PRO-FLEX 100 W PROTECTION    est   classé  comme revêtement  pour  la  protection  de surface  de  béton  selon la norme EN1504-2 et comme produit cimentaire impermé- -able à l’eau appliqué sous forme liquide selon EN 14891.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "63aed7d95beb0645",
      "section_path": [
        "CEM PRO-FLEX 100 W\nPROTECTION"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "1721fac74c537e14",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "63aed7d95beb0645",
        "section_path": [
          "CEM PRO-FLEX 100 W\nPROTECTION"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• CEM  PRO-FLEX  100  W   PROTECTION   est   un  mortier d’étanchéité ﬂexible présenté en kit prédosé à deux compo- -sants.  Il  se  compose  d’un  mortier  de  poudre  à   base de ciment (composant A) et émulsion de résine (composant B). Après mélange, on obtient un mortier applicable au rouleau, à la brosse, à la taloche, ou par pulvérisation.\n• CEM PRO-FLEX 100 W PROTECTION    est   classé  comme revêtement  pour  la  protection  de surface  de  béton  selon la norme EN1504-2 et comme produit cimentaire impermé- -able à l’eau appliqué sous forme liquide selon EN 14891."
      }
    },
    {
      "chunk_id": "060897ea2a172b7a",
      "score": 0.78376573,
      "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 2,
      "page_end": 2,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "060897ea2a172b7a",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 2,
        "page_end": 2,
        "block_type": "list_item",
        "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
      }
    },
    {
      "chunk_id": "f9886662c444b018",
      "score": 0.7369099,
      "text": "•  Ne pas appliquer sur supports gelés ou en cours de dégel, chauds ou en plein soleil, trempés ou sous pluie baƩante et par vent fort.\n• Le port du masque et des gants est recommandé.",
      "document_id": "full-FULL%201-eb0d29c6",
      "file_name": "FULL%201.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
      "parent_id": "f0508f6ae65feaea",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "f9886662c444b018",
        "document_id": "full-FULL%201-eb0d29c6",
        "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
        "file_name": "FULL%201.pdf",
        "parent_id": "f0508f6ae65feaea",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "•  Ne pas appliquer sur supports gelés ou en cours de dégel, chauds ou en plein soleil, trempés ou sous pluie baƩante et par vent fort.\n• Le port du masque et des gants est recommandé."
      }
    },
    {
      "chunk_id": "d5deaa1b96cb2a2f",
      "score": 0.7369099,
      "text": "•  Ne pas appliquer sur supports gelés ou en cours de dégel, chauds ou en plein soleil, trempés ou sous pluie baƩante et par vent fort.\n• Le port du masque et des gants est recommandé.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": "2b204617d54cb943",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "d5deaa1b96cb2a2f",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": "2b204617d54cb943",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "•  Ne pas appliquer sur supports gelés ou en cours de dégel, chauds ou en plein soleil, trempés ou sous pluie baƩante et par vent fort.\n• Le port du masque et des gants est recommandé."
      }
    },
    {
      "chunk_id": "773d8cea09acd46b",
      "score": 0.73311245,
      "text": "“Consommation : Varie selon le support (type,planeité, rugosité)\n\nç * | Un sac peut couvrir environ 5m?.\n\nTempérature d’application: comprise entre 8°C et 35°C.",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "d8521720d7390e19",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "773d8cea09acd46b",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "d8521720d7390e19",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "“Consommation : Varie selon le support (type,planeité, rugosité)\n\nç * | Un sac peut couvrir environ 5m?.\n\nTempérature d’application: comprise entre 8°C et 35°C."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-03",
  "query": "Comment mélanger les composants de CEM PRO FLEX 100 W PROTECTION et appliquer les couches ?",
  "expected": [
    {
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "chunk_ids": [
        "060897ea2a172b7a"
      ],
      "substring": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "060897ea2a172b7a",
      "score": 2.2477744350320195,
      "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 2,
      "page_end": 2,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "060897ea2a172b7a",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 2,
        "page_end": 2,
        "block_type": "list_item",
        "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.2477744350320195,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.6922188794764638,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1bca5b1704c94391",
      "score": 2.1517626946712185,
      "text": "• Bien mélanger le contenu du seau avant usage.\n• Le produit étant prêt à l’emploi, ne pas ajouter d’eau.\n• Le port  des  protections individuelles ( gants,  lunettes ) est recommandé.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 2,
      "page_end": 2,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1bca5b1704c94391",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 2,
        "page_end": 2,
        "block_type": "list_item",
        "text": "• Bien mélanger le contenu du seau avant usage.\n• Le produit étant prêt à l’emploi, ne pas ajouter d’eau.\n• Le port  des  protections individuelles ( gants,  lunettes ) est recommandé."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.1517626946712185,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.596207139115663,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "7f456847ea806a42",
      "score": 2.1487162133254003,
      "text": "Conditoi nnement | Composant B | Bidon de 5 kg\n| Composant A | Sac de 15 kg\n| Composant A + B | 20 kg mélange prêt à l'emploi\nCompositoi n | Composant B | Émulsion de résine acrylique\n| Composant A | Ciment ; charges minérales et add\nAspect/Couleur | Gris clair |\nConservatoi n | 12 mois en emballage d’origine intact non ouvert, stocké à des températu entre +5 °C et +30 °C |\nConsommatoi n | 2 à 4 kg en deux couches pour une épaisseur de 1.5 à 2.5mm |\nTemps d’atet nte entre les couches | 2 à 4 heures selon la température |\nAccessibilité | Après 24 heures |\nTempérature d’applicatoi n | Applicatoi n entre 8°C et 35°C |",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "71de6a967af25a09",
      "section_path": [
        "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "table",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "7f456847ea806a42",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "71de6a967af25a09",
        "section_path": [
          "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "table",
        "text": "Conditoi nnement | Composant B | Bidon de 5 kg\n| Composant A | Sac de 15 kg\n| Composant A + B | 20 kg mélange prêt à l'emploi\nCompositoi n | Composant B | Émulsion de résine acrylique\n| Composant A | Ciment ; charges minérales et add\nAspect/Couleur | Gris clair |\nConservatoi n | 12 mois en emballage d’origine intact non ouvert, stocké à des températu entre +5 °C et +30 °C |\nConsommatoi n | 2 à 4 kg en deux couches pour une épaisseur de 1.5 à 2.5mm |\nTemps d’atet nte entre les couches | 2 à 4 heures selon la température |\nAccessibilité | Après 24 heures |\nTempérature d’applicatoi n | Applicatoi n entre 8°C et 35°C |"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.1487162133254003,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.5931606577698448,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "098305870fda058b",
      "score": 2.0284654695039177,
      "text": "Conservation",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "379c69d719a5fb60",
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "098305870fda058b",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "379c69d719a5fb60",
        "section_path": [
          "INFORMATION SUR LE PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conservation"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.0284654695039177,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.47290991394836196,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1415cb037decd94c",
      "score": 2.0284654695039177,
      "text": "• Application facile et souple.\n• Bonne protection du béton contre la carbonatation.\n• Excellente adhérence sur les supports sains.\n• Perméabilité à la vapeur.\n• Etanchéité contre la pression d’eau.\n• Imperméabilisation sous carrelage.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "379c69d719a5fb60",
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1415cb037decd94c",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "379c69d719a5fb60",
        "section_path": [
          "INFORMATION SUR LE PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Application facile et souple.\n• Bonne protection du béton contre la carbonatation.\n• Excellente adhérence sur les supports sains.\n• Perméabilité à la vapeur.\n• Etanchéité contre la pression d’eau.\n• Imperméabilisation sous carrelage."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.0284654695039177,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.47290991394836196,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "100",
      "appliquer",
      "cem",
      "comment",
      "composants",
      "couches",
      "de",
      "et",
      "flex",
      "les",
      "melanger",
      "pro",
      "protection",
      "w"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "71de6a967af25a09",
    "379c69d719a5fb60"
  ]
}
```

```json
{
  "query_id": "HV2-03",
  "query": "Comment mélanger les composants de CEM PRO FLEX 100 W PROTECTION et appliquer les couches ?",
  "expected": [
    {
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "chunk_ids": [
        "060897ea2a172b7a"
      ],
      "substring": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "060897ea2a172b7a",
      "score": 2.2477744350320195,
      "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 2,
      "page_end": 2,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "060897ea2a172b7a",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 2,
        "page_end": 2,
        "block_type": "list_item",
        "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.2477744350320195,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.6922188794764638,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1bca5b1704c94391",
      "score": 2.1517626946712185,
      "text": "• Bien mélanger le contenu du seau avant usage.\n• Le produit étant prêt à l’emploi, ne pas ajouter d’eau.\n• Le port  des  protections individuelles ( gants,  lunettes ) est recommandé.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 2,
      "page_end": 2,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1bca5b1704c94391",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 2,
        "page_end": 2,
        "block_type": "list_item",
        "text": "• Bien mélanger le contenu du seau avant usage.\n• Le produit étant prêt à l’emploi, ne pas ajouter d’eau.\n• Le port  des  protections individuelles ( gants,  lunettes ) est recommandé."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.1517626946712185,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.596207139115663,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "7f456847ea806a42",
      "score": 2.1487162133254003,
      "text": "Conditoi nnement | Composant B | Bidon de 5 kg\n| Composant A | Sac de 15 kg\n| Composant A + B | 20 kg mélange prêt à l'emploi\nCompositoi n | Composant B | Émulsion de résine acrylique\n| Composant A | Ciment ; charges minérales et add\nAspect/Couleur | Gris clair |\nConservatoi n | 12 mois en emballage d’origine intact non ouvert, stocké à des températu entre +5 °C et +30 °C |\nConsommatoi n | 2 à 4 kg en deux couches pour une épaisseur de 1.5 à 2.5mm |\nTemps d’atet nte entre les couches | 2 à 4 heures selon la température |\nAccessibilité | Après 24 heures |\nTempérature d’applicatoi n | Applicatoi n entre 8°C et 35°C |",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "71de6a967af25a09",
      "section_path": [
        "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "table",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "7f456847ea806a42",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "71de6a967af25a09",
        "section_path": [
          "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "table",
        "text": "Conditoi nnement | Composant B | Bidon de 5 kg\n| Composant A | Sac de 15 kg\n| Composant A + B | 20 kg mélange prêt à l'emploi\nCompositoi n | Composant B | Émulsion de résine acrylique\n| Composant A | Ciment ; charges minérales et add\nAspect/Couleur | Gris clair |\nConservatoi n | 12 mois en emballage d’origine intact non ouvert, stocké à des températu entre +5 °C et +30 °C |\nConsommatoi n | 2 à 4 kg en deux couches pour une épaisseur de 1.5 à 2.5mm |\nTemps d’atet nte entre les couches | 2 à 4 heures selon la température |\nAccessibilité | Après 24 heures |\nTempérature d’applicatoi n | Applicatoi n entre 8°C et 35°C |"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.1487162133254003,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.5931606577698448,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "098305870fda058b",
      "score": 2.0284654695039177,
      "text": "Conservation",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "379c69d719a5fb60",
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "098305870fda058b",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "379c69d719a5fb60",
        "section_path": [
          "INFORMATION SUR LE PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conservation"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.0284654695039177,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.47290991394836196,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1415cb037decd94c",
      "score": 2.0284654695039177,
      "text": "• Application facile et souple.\n• Bonne protection du béton contre la carbonatation.\n• Excellente adhérence sur les supports sains.\n• Perméabilité à la vapeur.\n• Etanchéité contre la pression d’eau.\n• Imperméabilisation sous carrelage.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "379c69d719a5fb60",
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1415cb037decd94c",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "379c69d719a5fb60",
        "section_path": [
          "INFORMATION SUR LE PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Application facile et souple.\n• Bonne protection du béton contre la carbonatation.\n• Excellente adhérence sur les supports sains.\n• Perméabilité à la vapeur.\n• Etanchéité contre la pression d’eau.\n• Imperméabilisation sous carrelage."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.0284654695039177,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.47290991394836196,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "100",
      "appliquer",
      "cem",
      "comment",
      "composants",
      "couches",
      "de",
      "et",
      "flex",
      "les",
      "melanger",
      "pro",
      "protection",
      "w"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "71de6a967af25a09",
    "379c69d719a5fb60"
  ]
}
```

```json
{
  "query_id": "HV2-03",
  "query": "Comment mélanger les composants de CEM PRO FLEX 100 W PROTECTION et appliquer les couches ?",
  "expected": [
    {
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "chunk_ids": [
        "060897ea2a172b7a"
      ],
      "substring": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "060897ea2a172b7a",
      "score": 2.2477744350320195,
      "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 2,
      "page_end": 2,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "060897ea2a172b7a",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 2,
        "page_end": 2,
        "block_type": "list_item",
        "text": "• Le  support  doit  être  sec,  propre  et  exempte d’huile, de poussière et de graisse.\n• Enlever  toute  couche  ancienne  de  peinture ou ciment et autres agents de traitement de surface.\n• Le support doit être ragrée autant que possible.\n• En cas de doute, veuillez nous consulter. Application :\n• Verser  le composant  B (liquide) dans un récipient et ajouter le composant A (Poudre) progressivement et  malaxer  avec  un   malaxeur  électrique  à   basse vitesse jusqu’a l’obtention d’un mélange homogène.\n• CEM   PRO-FLEX  100  W  PROTECTION   est  appliqué   en deux   couches  manuellement avec la brosse,  au rouleau ou par air less.\n• L’application  de   CEM  PRO-FLEX   100  W  PROTECTION doit  être  en  épaisseur  de  couche  uniforme.  Un  excès  de matière peut mener à des ﬁssurations.\n• Appliquer une deuxième  couche après le durcissement de la première couche. Nettoyage des outils et des équipements :\n• Nettoyer les outils de travail avec de l’eau immédiatement après utilisation."
      },
      "dense_score": 0.78376573,
      "dense_rank": 2,
      "lexical_score": 2.2477744350320195,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.6922188794764638,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1bca5b1704c94391",
      "score": 2.1517626946712185,
      "text": "• Bien mélanger le contenu du seau avant usage.\n• Le produit étant prêt à l’emploi, ne pas ajouter d’eau.\n• Le port  des  protections individuelles ( gants,  lunettes ) est recommandé.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 2,
      "page_end": 2,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1bca5b1704c94391",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 2,
        "page_end": 2,
        "block_type": "list_item",
        "text": "• Bien mélanger le contenu du seau avant usage.\n• Le produit étant prêt à l’emploi, ne pas ajouter d’eau.\n• Le port  des  protections individuelles ( gants,  lunettes ) est recommandé."
      },
      "dense_score": 0.7246643,
      "dense_rank": 11,
      "lexical_score": 2.1517626946712185,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.596207139115663,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "7f456847ea806a42",
      "score": 2.1487162133254003,
      "text": "Conditoi nnement | Composant B | Bidon de 5 kg\n| Composant A | Sac de 15 kg\n| Composant A + B | 20 kg mélange prêt à l'emploi\nCompositoi n | Composant B | Émulsion de résine acrylique\n| Composant A | Ciment ; charges minérales et add\nAspect/Couleur | Gris clair |\nConservatoi n | 12 mois en emballage d’origine intact non ouvert, stocké à des températu entre +5 °C et +30 °C |\nConsommatoi n | 2 à 4 kg en deux couches pour une épaisseur de 1.5 à 2.5mm |\nTemps d’atet nte entre les couches | 2 à 4 heures selon la température |\nAccessibilité | Après 24 heures |\nTempérature d’applicatoi n | Applicatoi n entre 8°C et 35°C |",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "71de6a967af25a09",
      "section_path": [
        "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "table",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "7f456847ea806a42",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "71de6a967af25a09",
        "section_path": [
          "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "table",
        "text": "Conditoi nnement | Composant B | Bidon de 5 kg\n| Composant A | Sac de 15 kg\n| Composant A + B | 20 kg mélange prêt à l'emploi\nCompositoi n | Composant B | Émulsion de résine acrylique\n| Composant A | Ciment ; charges minérales et add\nAspect/Couleur | Gris clair |\nConservatoi n | 12 mois en emballage d’origine intact non ouvert, stocké à des températu entre +5 °C et +30 °C |\nConsommatoi n | 2 à 4 kg en deux couches pour une épaisseur de 1.5 à 2.5mm |\nTemps d’atet nte entre les couches | 2 à 4 heures selon la température |\nAccessibilité | Après 24 heures |\nTempérature d’applicatoi n | Applicatoi n entre 8°C et 35°C |"
      },
      "dense_score": 0.71551,
      "dense_rank": 19,
      "lexical_score": 2.1487162133254003,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.5931606577698448,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1721fac74c537e14",
      "score": 2.0284654695039177,
      "text": "• CEM  PRO-FLEX  100  W   PROTECTION   est   un  mortier d’étanchéité ﬂexible présenté en kit prédosé à deux compo- -sants.  Il  se  compose  d’un  mortier  de  poudre  à   base de ciment (composant A) et émulsion de résine (composant B). Après mélange, on obtient un mortier applicable au rouleau, à la brosse, à la taloche, ou par pulvérisation.\n• CEM PRO-FLEX 100 W PROTECTION    est   classé  comme revêtement  pour  la  protection  de surface  de  béton  selon la norme EN1504-2 et comme produit cimentaire impermé- -able à l’eau appliqué sous forme liquide selon EN 14891.",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "63aed7d95beb0645",
      "section_path": [
        "CEM PRO-FLEX 100 W\nPROTECTION"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1721fac74c537e14",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "63aed7d95beb0645",
        "section_path": [
          "CEM PRO-FLEX 100 W\nPROTECTION"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• CEM  PRO-FLEX  100  W   PROTECTION   est   un  mortier d’étanchéité ﬂexible présenté en kit prédosé à deux compo- -sants.  Il  se  compose  d’un  mortier  de  poudre  à   base de ciment (composant A) et émulsion de résine (composant B). Après mélange, on obtient un mortier applicable au rouleau, à la brosse, à la taloche, ou par pulvérisation.\n• CEM PRO-FLEX 100 W PROTECTION    est   classé  comme revêtement  pour  la  protection  de surface  de  béton  selon la norme EN1504-2 et comme produit cimentaire impermé- -able à l’eau appliqué sous forme liquide selon EN 14891."
      },
      "dense_score": 0.83049893,
      "dense_rank": 1,
      "lexical_score": 2.0284654695039177,
      "lexical_rank": 6,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.47290991394836196,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "905f7773c9625d7e",
      "score": 2.0284654695039177,
      "text": "1-Protection d’ouvrage en béton :",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "379c69d719a5fb60",
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "905f7773c9625d7e",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "379c69d719a5fb60",
        "section_path": [
          "INFORMATION SUR LE PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "1-Protection d’ouvrage en béton :"
      },
      "dense_score": 0.70236516,
      "dense_rank": 35,
      "lexical_score": 2.0284654695039177,
      "lexical_rank": 16,
      "identifier_match": false,
      "filename_match": 0.5555555555555556,
      "numeric_match": 1.0,
      "word_match": 0.47290991394836196,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "100",
      "appliquer",
      "cem",
      "comment",
      "composants",
      "couches",
      "de",
      "et",
      "flex",
      "les",
      "melanger",
      "pro",
      "protection",
      "w"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "71de6a967af25a09",
    "63aed7d95beb0645",
    "379c69d719a5fb60"
  ]
}
```

```json
{
  "query_id": "HV2-04",
  "query": "Quel couple maximal et quel diamètre de mandrin a la perceuse ECIDL208689 ?",
  "expected": [
    {
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "chunk_ids": [
        "076ff7276b9dc660"
      ],
      "substring": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "8852467a2b9cee0c",
      "score": 0.7742204,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "ca8f3846c8154b91",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "8852467a2b9cee0c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "ca8f3846c8154b91",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "78fdf841ed57d71f",
      "score": 0.7700733,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de percussion max. : 30000 cpm Couple max. : 96 Nm Mandrin métallique Jacobs\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL209686%20Technical%20Data-9f2a71e5",
      "file_name": "ECIDL209686%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL209686%20Technical%20Data.pdf",
      "parent_id": "018f520ed7c4c02d",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "78fdf841ed57d71f",
        "document_id": "full-ECIDL209686%20Technical%20Data-9f2a71e5",
        "source_path": "ai_data\\raw\\emtop\\ECIDL209686%20Technical%20Data.pdf",
        "file_name": "ECIDL209686%20Technical%20Data.pdf",
        "parent_id": "018f520ed7c4c02d",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de percussion max. : 30000 cpm Couple max. : 96 Nm Mandrin métallique Jacobs\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "33528846f6661792",
      "score": 0.7687491,
      "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "fa3406435016e038",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "33528846f6661792",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "fa3406435016e038",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "23b329e12ef306c3",
      "score": 0.76563174,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "ba45fa3da2f2ba46",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "23b329e12ef306c3",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "ba45fa3da2f2ba46",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
      }
    },
    {
      "chunk_id": "b0127b4f2a903aa4",
      "score": 0.72016984,
      "text": "Capacité du mandrin : 3-16 mm\nTaille de la connexion : 1/2\"-20UNF Avec 1 clé de mandrin Emballé en double blister",
      "document_id": "full-EKCY1601%20Technical%20Data-3aa4bc85",
      "file_name": "EKCY1601%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EKCY1601%20Technical%20Data.pdf",
      "parent_id": "a58e16c916c77560",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "b0127b4f2a903aa4",
        "document_id": "full-EKCY1601%20Technical%20Data-3aa4bc85",
        "source_path": "ai_data\\raw\\emtop\\EKCY1601%20Technical%20Data.pdf",
        "file_name": "EKCY1601%20Technical%20Data.pdf",
        "parent_id": "a58e16c916c77560",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Capacité du mandrin : 3-16 mm\nTaille de la connexion : 1/2\"-20UNF Avec 1 clé de mandrin Emballé en double blister"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-04",
  "query": "Quel couple maximal et quel diamètre de mandrin a la perceuse ECIDL208689 ?",
  "expected": [
    {
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "chunk_ids": [
        "076ff7276b9dc660"
      ],
      "substring": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "076ff7276b9dc660",
      "score": 1.8234402972591521,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "076ff7276b9dc660",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.8234402972591521,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6567736305924853,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "33528846f6661792",
      "score": 1.648801446024918,
      "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "fa3406435016e038",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "33528846f6661792",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "fa3406435016e038",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.648801446024918,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.4821347793582513,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1e813cb64fb35053",
      "score": 1.348695631538105,
      "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Lampe de travail LED intégrée\nIndicateur LED du niveau de batterie Comprend :",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1e813cb64fb35053",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Lampe de travail LED intégrée\nIndicateur LED du niveau de batterie Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "bbbdef1e09e53fb5",
      "score": 1.348695631538105,
      "text": "2 batteries de 4,0Ah (EBPK20021)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "bbbdef1e09e53fb5",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 batteries de 4,0Ah (EBPK20021)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "cbecafccf99e52d3",
      "score": 1.348695631538105,
      "text": "percer des trous, visser des vis, percer des trous dans le béton",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "cbecafccf99e52d3",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "percer des trous, visser des vis, percer des trous dans le béton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL208689"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "ECIDL208689%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "couple",
      "de",
      "diametre",
      "ecidl208689",
      "et",
      "la",
      "mandrin",
      "maximal",
      "perceuse",
      "quel"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "627a272f376d1bd8",
    "fa3406435016e038"
  ]
}
```

```json
{
  "query_id": "HV2-04",
  "query": "Quel couple maximal et quel diamètre de mandrin a la perceuse ECIDL208689 ?",
  "expected": [
    {
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "chunk_ids": [
        "076ff7276b9dc660"
      ],
      "substring": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "076ff7276b9dc660",
      "score": 1.8234402972591521,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "076ff7276b9dc660",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.8234402972591521,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6567736305924853,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "33528846f6661792",
      "score": 1.648801446024918,
      "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "fa3406435016e038",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "33528846f6661792",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "fa3406435016e038",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.648801446024918,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.4821347793582513,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "1e813cb64fb35053",
      "score": 1.348695631538105,
      "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Lampe de travail LED intégrée\nIndicateur LED du niveau de batterie Comprend :",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1e813cb64fb35053",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Lampe de travail LED intégrée\nIndicateur LED du niveau de batterie Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "bbbdef1e09e53fb5",
      "score": 1.348695631538105,
      "text": "2 batteries de 4,0Ah (EBPK20021)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "bbbdef1e09e53fb5",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 batteries de 4,0Ah (EBPK20021)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "cbecafccf99e52d3",
      "score": 1.348695631538105,
      "text": "percer des trous, visser des vis, percer des trous dans le béton",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "cbecafccf99e52d3",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "percer des trous, visser des vis, percer des trous dans le béton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL208689"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "ECIDL208689%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "couple",
      "de",
      "diametre",
      "ecidl208689",
      "et",
      "la",
      "mandrin",
      "maximal",
      "perceuse",
      "quel"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "627a272f376d1bd8",
    "fa3406435016e038"
  ]
}
```

```json
{
  "query_id": "HV2-04",
  "query": "Quel couple maximal et quel diamètre de mandrin a la perceuse ECIDL208689 ?",
  "expected": [
    {
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "chunk_ids": [
        "076ff7276b9dc660"
      ],
      "substring": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "076ff7276b9dc660",
      "score": 1.8234402972591521,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "076ff7276b9dc660",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal pouvant atteindre 86 Nm\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Carter de tête de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20V"
      },
      "dense_score": 0.6384275,
      "dense_rank": 55,
      "lexical_score": 1.8234402972591521,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6567736305924853,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "33528846f6661792",
      "score": 1.648801446024918,
      "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "fa3406435016e038",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "33528846f6661792",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "fa3406435016e038",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1"
      },
      "dense_score": 0.7687491,
      "dense_rank": 3,
      "lexical_score": 1.648801446024918,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.4821347793582513,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "1e813cb64fb35053",
      "score": 1.348695631538105,
      "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Lampe de travail LED intégrée\nIndicateur LED du niveau de batterie Comprend :",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1e813cb64fb35053",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Lampe de travail LED intégrée\nIndicateur LED du niveau de batterie Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "bbbdef1e09e53fb5",
      "score": 1.348695631538105,
      "text": "2 batteries de 4,0Ah (EBPK20021)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "bbbdef1e09e53fb5",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 batteries de 4,0Ah (EBPK20021)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "cbecafccf99e52d3",
      "score": 1.348695631538105,
      "text": "percer des trous, visser des vis, percer des trous dans le béton",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "627a272f376d1bd8",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "cbecafccf99e52d3",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "627a272f376d1bd8",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "percer des trous, visser des vis, percer des trous dans le béton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.348695631538105,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.18202896487143813,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL208689"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "ECIDL208689%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "couple",
      "de",
      "diametre",
      "ecidl208689",
      "et",
      "la",
      "mandrin",
      "maximal",
      "perceuse",
      "quel"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "627a272f376d1bd8",
    "fa3406435016e038"
  ]
}
```

```json
{
  "query_id": "HV2-05",
  "query": "La meuleuse ELAG4108112 a-t-elle une protection contre le redémarrage ?",
  "expected": [
    {
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "chunk_ids": [
        "07b34086a7c41e34"
      ],
      "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "905f7773c9625d7e",
      "score": 0.7188885,
      "text": "1-Protection d’ouvrage en béton :",
      "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
      "file_name": "CEM PRO FLEX 100 W Protection.pdf",
      "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
      "parent_id": "379c69d719a5fb60",
      "section_path": [
        "INFORMATION SUR LE PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "905f7773c9625d7e",
        "document_id": "full-CEM PRO FLEX 100 W Protection-2de0b296",
        "source_path": "ai_data\\raw\\sofap\\CEM PRO FLEX 100 W Protection.pdf",
        "file_name": "CEM PRO FLEX 100 W Protection.pdf",
        "parent_id": "379c69d719a5fb60",
        "section_path": [
          "INFORMATION SUR LE PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "1-Protection d’ouvrage en béton :"
      }
    },
    {
      "chunk_id": "dc131b94eec0699a",
      "score": 0.68344176,
      "text": "© Support ayant une faible résistance à l’arrachement (RT1).",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "file_name": "ISBAROC-R.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
      "parent_id": "ca4e602fe65f328d",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "dc131b94eec0699a",
        "document_id": "full-ISBAROC-R-3a4b4eb9",
        "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
        "file_name": "ISBAROC-R.pdf",
        "parent_id": "ca4e602fe65f328d",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "© Support ayant une faible résistance à l’arrachement (RT1)."
      }
    },
    {
      "chunk_id": "7571ea2ecbdbcab7",
      "score": 0.68305314,
      "text": "o Support ayant une faible résistance à l’arrachement (RT1).",
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "parent_id": "c3e2db2878fa1f2e",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "7571ea2ecbdbcab7",
        "document_id": "full-FULL-88a1b942",
        "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
        "file_name": "FULL.pdf",
        "parent_id": "c3e2db2878fa1f2e",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "o Support ayant une faible résistance à l’arrachement (RT1)."
      }
    },
    {
      "chunk_id": "46c64b7934d42b2b",
      "score": 0.68305314,
      "text": "o Support ayant une faible résistance à l’arrachement (RT1).",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "d69c0c75186133c2",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "46c64b7934d42b2b",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "d69c0c75186133c2",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "o Support ayant une faible résistance à l’arrachement (RT1)."
      }
    },
    {
      "chunk_id": "fced69f8a9f85c31",
      "score": 0.67636895,
      "text": "Taille de la roue : 150 mm Repose-pièce réglable Socle en aluminium robuste Comprend 1 jeu de protections oculaires\nComprend 1 boîte de rangement pour outils Emballé dans un carton",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "fced69f8a9f85c31",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Taille de la roue : 150 mm Repose-pièce réglable Socle en aluminium robuste Comprend 1 jeu de protections oculaires\nComprend 1 boîte de rangement pour outils Emballé dans un carton"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-05",
  "query": "La meuleuse ELAG4108112 a-t-elle une protection contre le redémarrage ?",
  "expected": [
    {
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "chunk_ids": [
        "07b34086a7c41e34"
      ],
      "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "07b34086a7c41e34",
      "score": 2.032333578872638,
      "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "d3af1d79e50b405b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "07b34086a7c41e34",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "d3af1d79e50b405b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.032333578872638,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.8656669122059716,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "10061c6c48d3fcb4",
      "score": 1.3598829914036252,
      "text": "Conditionné dans une mallette de transport",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "f1b193fd65c83390",
      "section_path": [
        "(P40/P60/P80)"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "10061c6c48d3fcb4",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "f1b193fd65c83390",
        "section_path": [
          "(P40/P60/P80)"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conditionné dans une mallette de transport"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "42c1b4702cc4f77e",
      "score": 1.3598829914036252,
      "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Inclus :",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "6adb1c8bb2e0463c",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "42c1b4702cc4f77e",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "6adb1c8bb2e0463c",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Inclus :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "80aef6020ca418c8",
      "score": 1.3598829914036252,
      "text": "1 jeu de disques abrasifs pour coupe de métal (10 pcs)\n3 pcs de disques à lamelles",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "d3af1d79e50b405b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "80aef6020ca418c8",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "d3af1d79e50b405b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1 jeu de disques abrasifs pour coupe de métal (10 pcs)\n3 pcs de disques à lamelles"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "fc78303af963ba12",
      "score": 1.3598829914036252,
      "text": "2 pcs de batteries 2.0Ah (EBPK42201)\n1 chargeur (EFCR42021) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "f1b193fd65c83390",
      "section_path": [
        "(P40/P60/P80)"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fc78303af963ba12",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "f1b193fd65c83390",
        "section_path": [
          "(P40/P60/P80)"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 pcs de batteries 2.0Ah (EBPK42201)\n1 chargeur (EFCR42021) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ELAG4108112"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "ELAG4108112%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "contre",
      "elag4108112",
      "elle",
      "la",
      "le",
      "meuleuse",
      "protection",
      "redemarrage",
      "t",
      "une"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "d3af1d79e50b405b",
    "f1b193fd65c83390",
    "6adb1c8bb2e0463c"
  ]
}
```

```json
{
  "query_id": "HV2-05",
  "query": "La meuleuse ELAG4108112 a-t-elle une protection contre le redémarrage ?",
  "expected": [
    {
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "chunk_ids": [
        "07b34086a7c41e34"
      ],
      "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "07b34086a7c41e34",
      "score": 2.032333578872638,
      "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "d3af1d79e50b405b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "07b34086a7c41e34",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "d3af1d79e50b405b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.032333578872638,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.8656669122059716,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "10061c6c48d3fcb4",
      "score": 1.3598829914036252,
      "text": "Conditionné dans une mallette de transport",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "f1b193fd65c83390",
      "section_path": [
        "(P40/P60/P80)"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "10061c6c48d3fcb4",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "f1b193fd65c83390",
        "section_path": [
          "(P40/P60/P80)"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conditionné dans une mallette de transport"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "42c1b4702cc4f77e",
      "score": 1.3598829914036252,
      "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Inclus :",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "6adb1c8bb2e0463c",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "42c1b4702cc4f77e",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "6adb1c8bb2e0463c",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Inclus :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "80aef6020ca418c8",
      "score": 1.3598829914036252,
      "text": "1 jeu de disques abrasifs pour coupe de métal (10 pcs)\n3 pcs de disques à lamelles",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "d3af1d79e50b405b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "80aef6020ca418c8",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "d3af1d79e50b405b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1 jeu de disques abrasifs pour coupe de métal (10 pcs)\n3 pcs de disques à lamelles"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "fc78303af963ba12",
      "score": 1.3598829914036252,
      "text": "2 pcs de batteries 2.0Ah (EBPK42201)\n1 chargeur (EFCR42021) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "f1b193fd65c83390",
      "section_path": [
        "(P40/P60/P80)"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fc78303af963ba12",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "f1b193fd65c83390",
        "section_path": [
          "(P40/P60/P80)"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 pcs de batteries 2.0Ah (EBPK42201)\n1 chargeur (EFCR42021) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ELAG4108112"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "ELAG4108112%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "contre",
      "elag4108112",
      "elle",
      "la",
      "le",
      "meuleuse",
      "protection",
      "redemarrage",
      "t",
      "une"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "d3af1d79e50b405b",
    "f1b193fd65c83390",
    "6adb1c8bb2e0463c"
  ]
}
```

```json
{
  "query_id": "HV2-05",
  "query": "La meuleuse ELAG4108112 a-t-elle une protection contre le redémarrage ?",
  "expected": [
    {
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "chunk_ids": [
        "07b34086a7c41e34"
      ],
      "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "07b34086a7c41e34",
      "score": 2.032333578872638,
      "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "d3af1d79e50b405b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "07b34086a7c41e34",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "d3af1d79e50b405b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être montée de manière flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entrée max : 1080W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.032333578872638,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.8656669122059716,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "10061c6c48d3fcb4",
      "score": 1.3598829914036252,
      "text": "Conditionné dans une mallette de transport",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "f1b193fd65c83390",
      "section_path": [
        "(P40/P60/P80)"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "10061c6c48d3fcb4",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "f1b193fd65c83390",
        "section_path": [
          "(P40/P60/P80)"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conditionné dans une mallette de transport"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "42c1b4702cc4f77e",
      "score": 1.3598829914036252,
      "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Inclus :",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "6adb1c8bb2e0463c",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "42c1b4702cc4f77e",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "6adb1c8bb2e0463c",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Inclus :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "80aef6020ca418c8",
      "score": 1.3598829914036252,
      "text": "1 jeu de disques abrasifs pour coupe de métal (10 pcs)\n3 pcs de disques à lamelles",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "d3af1d79e50b405b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "80aef6020ca418c8",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "d3af1d79e50b405b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1 jeu de disques abrasifs pour coupe de métal (10 pcs)\n3 pcs de disques à lamelles"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "fc78303af963ba12",
      "score": 1.3598829914036252,
      "text": "2 pcs de batteries 2.0Ah (EBPK42201)\n1 chargeur (EFCR42021) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "file_name": "ELAG4108112%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
      "parent_id": "f1b193fd65c83390",
      "section_path": [
        "(P40/P60/P80)"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fc78303af963ba12",
        "document_id": "full-ELAG4108112%20Technical%20Data-c5f87c6e",
        "source_path": "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf",
        "file_name": "ELAG4108112%20Technical%20Data.pdf",
        "parent_id": "f1b193fd65c83390",
        "section_path": [
          "(P40/P60/P80)"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 pcs de batteries 2.0Ah (EBPK42201)\n1 chargeur (EFCR42021) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3598829914036252,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.19321632473695857,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ELAG4108112"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ELAG4108112%20Technical%20Data-c5f87c6e",
      "ELAG4108112%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ELAG4108112%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "contre",
      "elag4108112",
      "elle",
      "la",
      "le",
      "meuleuse",
      "protection",
      "redemarrage",
      "t",
      "une"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "d3af1d79e50b405b",
    "f1b193fd65c83390",
    "6adb1c8bb2e0463c"
  ]
}
```

```json
{
  "query_id": "HV2-06",
  "query": "En quel acier sont fabriquées les douilles EMSS12102L ?",
  "expected": [
    {
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "chunk_ids": [
        "0a001bc9ecfb185c"
      ],
      "substring": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "88ab9473c30b61f5",
      "score": 0.68881994,
      "text": "CaractérisƟques NormaƟves selon EN 12004:\nCaractérisƟques d’emploi :",
      "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
      "file_name": "FLEX%20PLUS%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\FLEX%20PLUS%20V4.pdf",
      "parent_id": "16d4868d2c1bc68b",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "88ab9473c30b61f5",
        "document_id": "full-FLEX%20PLUS%20V4-98e08a07",
        "source_path": "ai_data\\raw\\sofap\\FLEX%20PLUS%20V4.pdf",
        "file_name": "FLEX%20PLUS%20V4.pdf",
        "parent_id": "16d4868d2c1bc68b",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "CaractérisƟques NormaƟves selon EN 12004:\nCaractérisƟques d’emploi :"
      }
    },
    {
      "chunk_id": "263a5cf2cf716c53",
      "score": 0.68881994,
      "text": "CaractérisƟques NormaƟves selon EN 12004 :\nCaractérisƟques d’emploi :",
      "document_id": "full-PRO%201000%20V2-467bc232",
      "file_name": "PRO%201000%20V2.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%201000%20V2.pdf",
      "parent_id": "590fe9090ae1ecf9",
      "section_path": [
        "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "263a5cf2cf716c53",
        "document_id": "full-PRO%201000%20V2-467bc232",
        "source_path": "ai_data\\raw\\sofap\\PRO%201000%20V2.pdf",
        "file_name": "PRO%201000%20V2.pdf",
        "parent_id": "590fe9090ae1ecf9",
        "section_path": [
          "CARACTÉRISTIQUES PRODUIT & PERFORMANCES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "CaractérisƟques NormaƟves selon EN 12004 :\nCaractérisƟques d’emploi :"
      }
    },
    {
      "chunk_id": "dfe6d8c968fe219e",
      "score": 0.68881994,
      "text": "CaractérisƟques NormaƟves selon EN 12004 :\nCaractérisƟques d’emploi :",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "file_name": "PRO%20200%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
      "parent_id": "fd83189584fcb7fb",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "dfe6d8c968fe219e",
        "document_id": "full-PRO%20200%20V4-8f310261",
        "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
        "file_name": "PRO%20200%20V4.pdf",
        "parent_id": "fd83189584fcb7fb",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "CaractérisƟques NormaƟves selon EN 12004 :\nCaractérisƟques d’emploi :"
      }
    },
    {
      "chunk_id": "598865490cb98295",
      "score": 0.68881994,
      "text": "CaractérisƟques NormaƟves selon EN 12004:\nCaractérisƟques d’emploi :",
      "document_id": "full-Pro 2000_Compressed-f979ade1",
      "file_name": "Pro 2000_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
      "parent_id": "ccda60f1c450e8f5_1",
      "section_path": [
        "PRO 2000"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "598865490cb98295",
        "document_id": "full-Pro 2000_Compressed-f979ade1",
        "source_path": "ai_data\\raw\\sofap\\Pro 2000_Compressed.pdf",
        "file_name": "Pro 2000_Compressed.pdf",
        "parent_id": "ccda60f1c450e8f5_1",
        "section_path": [
          "PRO 2000"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "CaractérisƟques NormaƟves selon EN 12004:\nCaractérisƟques d’emploi :"
      }
    },
    {
      "chunk_id": "ad403a5357e594b6",
      "score": 0.6838529,
      "text": "• 12 mois en emballage fermé à l’abri du gel.",
      "document_id": "full-SUPROTEC1-ed82cb2d",
      "file_name": "SUPROTEC1.pdf",
      "source_path": "ai_data\\raw\\sofap\\SUPROTEC1.pdf",
      "parent_id": "cb11e582566fe830",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "ad403a5357e594b6",
        "document_id": "full-SUPROTEC1-ed82cb2d",
        "source_path": "ai_data\\raw\\sofap\\SUPROTEC1.pdf",
        "file_name": "SUPROTEC1.pdf",
        "parent_id": "cb11e582566fe830",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• 12 mois en emballage fermé à l’abri du gel."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-06",
  "query": "En quel acier sont fabriquées les douilles EMSS12102L ?",
  "expected": [
    {
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "chunk_ids": [
        "0a001bc9ecfb185c"
      ],
      "substring": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail."
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "0a001bc9ecfb185c",
      "score": 1.9473958493620498,
      "text": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail.",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "0a001bc9ecfb185c",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.9473958493620498,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6973958493620499,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "e1812f6b0d73ffe6",
      "score": 1.7807128041956686,
      "text": "3. La douille est équipée d’un trou anti-décrochage et d’une rainure de fixation pour bague\n10 pièces, jeu de douilles à choc profond 1/2\" DR. Tailles : 10, 12, 13, 14, 15, 17, 19, 21, 22, 24 mm Longueur : 78 mm Matériau : CrMo Traitement thermique Conditionné en BMC",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e1812f6b0d73ffe6",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "3. La douille est équipée d’un trou anti-décrochage et d’une rainure de fixation pour bague\n10 pièces, jeu de douilles à choc profond 1/2\" DR. Tailles : 10, 12, 13, 14, 15, 17, 19, 21, 22, 24 mm Longueur : 78 mm Matériau : CrMo Traitement thermique Conditionné en BMC"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.7807128041956686,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.5307128041956685,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "634fcfdb234afb91",
      "score": 1.5187268211362037,
      "text": "mines, métallurgie, construction navale, réparation automobile et autres industries,\nmaintenance de machines lourdes et démontage/montage de grosses vis, peut être utilisé\navec des outils pneumatiques de type clé à chocs",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "634fcfdb234afb91",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "mines, métallurgie, construction navale, réparation automobile et autres industries,\nmaintenance de machines lourdes et démontage/montage de grosses vis, peut être utilisé\navec des outils pneumatiques de type clé à chocs"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5187268211362037,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.26872682113620366,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "75ee813780fa6e6e",
      "score": 1.5187268211362037,
      "text": "Convient aux clés à chocs pneumatiques et électriques, etc. Excellente résistance aux impacts, couple plus élevé ;",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "75ee813780fa6e6e",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Convient aux clés à chocs pneumatiques et électriques, etc. Excellente résistance aux impacts, couple plus élevé ;"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5187268211362037,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.26872682113620366,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "56635349b150c7d8",
      "score": 0.3026041506379501,
      "text": "1. Lunettes de protection scientifiques et sécuritaires : nos lunettes de protection sont étanches, résistantes aux chocs, et peuvent non seulement bloquer les éclaboussures de salive, les projections et la poussière.\n2. Lunettes de protection anti-buée réutilisables : les lunettes de sécurité anti-buée possèdent un revêtement anti-buée, les verres ne s'embuent pas facilement lorsqu'ils sont exposés à la vapeur d'eau.\n3. Lunettes de haute qualité : fabriquées en matériau PC anti-explosion, elles sont légères, résistantes, anti-choc, capables de supporter une forte pression, durables et esthétiques.\n4. Design léger et confortable : le corps principal de ces larges lunettes de sécurité est",
      "document_id": "full-ESGG0101%20Technical%20Data-513ddd55",
      "file_name": "ESGG0101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ESGG0101%20Technical%20Data.pdf",
      "parent_id": "4402b6c3eca2fbc3",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "56635349b150c7d8",
        "document_id": "full-ESGG0101%20Technical%20Data-513ddd55",
        "source_path": "ai_data\\raw\\emtop\\ESGG0101%20Technical%20Data.pdf",
        "file_name": "ESGG0101%20Technical%20Data.pdf",
        "parent_id": "4402b6c3eca2fbc3",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Lunettes de protection scientifiques et sécuritaires : nos lunettes de protection sont étanches, résistantes aux chocs, et peuvent non seulement bloquer les éclaboussures de salive, les projections et la poussière.\n2. Lunettes de protection anti-buée réutilisables : les lunettes de sécurité anti-buée possèdent un revêtement anti-buée, les verres ne s'embuent pas facilement lorsqu'ils sont exposés à la vapeur d'eau.\n3. Lunettes de haute qualité : fabriquées en matériau PC anti-explosion, elles sont légères, résistantes, anti-choc, capables de supporter une forte pression, durables et esthétiques.\n4. Design léger et confortable : le corps principal de ces larges lunettes de sécurité est"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.3026041506379501,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.3026041506379501,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EMSS12102L"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "EMSS12102L%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "acier",
      "douilles",
      "emss12102l",
      "en",
      "fabriquees",
      "les",
      "quel",
      "sont"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "82e47b1b4720ef73",
    "4402b6c3eca2fbc3"
  ]
}
```

```json
{
  "query_id": "HV2-06",
  "query": "En quel acier sont fabriquées les douilles EMSS12102L ?",
  "expected": [
    {
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "chunk_ids": [
        "0a001bc9ecfb185c"
      ],
      "substring": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "0a001bc9ecfb185c",
      "score": 1.9473958493620498,
      "text": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail.",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "0a001bc9ecfb185c",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.9473958493620498,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6973958493620499,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "e1812f6b0d73ffe6",
      "score": 1.7807128041956686,
      "text": "3. La douille est équipée d’un trou anti-décrochage et d’une rainure de fixation pour bague\n10 pièces, jeu de douilles à choc profond 1/2\" DR. Tailles : 10, 12, 13, 14, 15, 17, 19, 21, 22, 24 mm Longueur : 78 mm Matériau : CrMo Traitement thermique Conditionné en BMC",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e1812f6b0d73ffe6",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "3. La douille est équipée d’un trou anti-décrochage et d’une rainure de fixation pour bague\n10 pièces, jeu de douilles à choc profond 1/2\" DR. Tailles : 10, 12, 13, 14, 15, 17, 19, 21, 22, 24 mm Longueur : 78 mm Matériau : CrMo Traitement thermique Conditionné en BMC"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.7807128041956686,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.5307128041956685,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "634fcfdb234afb91",
      "score": 1.5187268211362037,
      "text": "mines, métallurgie, construction navale, réparation automobile et autres industries,\nmaintenance de machines lourdes et démontage/montage de grosses vis, peut être utilisé\navec des outils pneumatiques de type clé à chocs",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "634fcfdb234afb91",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "mines, métallurgie, construction navale, réparation automobile et autres industries,\nmaintenance de machines lourdes et démontage/montage de grosses vis, peut être utilisé\navec des outils pneumatiques de type clé à chocs"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5187268211362037,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.26872682113620366,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "75ee813780fa6e6e",
      "score": 1.5187268211362037,
      "text": "Convient aux clés à chocs pneumatiques et électriques, etc. Excellente résistance aux impacts, couple plus élevé ;",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "75ee813780fa6e6e",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Convient aux clés à chocs pneumatiques et électriques, etc. Excellente résistance aux impacts, couple plus élevé ;"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5187268211362037,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.26872682113620366,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "56635349b150c7d8",
      "score": 0.3026041506379501,
      "text": "1. Lunettes de protection scientifiques et sécuritaires : nos lunettes de protection sont étanches, résistantes aux chocs, et peuvent non seulement bloquer les éclaboussures de salive, les projections et la poussière.\n2. Lunettes de protection anti-buée réutilisables : les lunettes de sécurité anti-buée possèdent un revêtement anti-buée, les verres ne s'embuent pas facilement lorsqu'ils sont exposés à la vapeur d'eau.\n3. Lunettes de haute qualité : fabriquées en matériau PC anti-explosion, elles sont légères, résistantes, anti-choc, capables de supporter une forte pression, durables et esthétiques.\n4. Design léger et confortable : le corps principal de ces larges lunettes de sécurité est",
      "document_id": "full-ESGG0101%20Technical%20Data-513ddd55",
      "file_name": "ESGG0101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ESGG0101%20Technical%20Data.pdf",
      "parent_id": "4402b6c3eca2fbc3",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "56635349b150c7d8",
        "document_id": "full-ESGG0101%20Technical%20Data-513ddd55",
        "source_path": "ai_data\\raw\\emtop\\ESGG0101%20Technical%20Data.pdf",
        "file_name": "ESGG0101%20Technical%20Data.pdf",
        "parent_id": "4402b6c3eca2fbc3",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Lunettes de protection scientifiques et sécuritaires : nos lunettes de protection sont étanches, résistantes aux chocs, et peuvent non seulement bloquer les éclaboussures de salive, les projections et la poussière.\n2. Lunettes de protection anti-buée réutilisables : les lunettes de sécurité anti-buée possèdent un revêtement anti-buée, les verres ne s'embuent pas facilement lorsqu'ils sont exposés à la vapeur d'eau.\n3. Lunettes de haute qualité : fabriquées en matériau PC anti-explosion, elles sont légères, résistantes, anti-choc, capables de supporter une forte pression, durables et esthétiques.\n4. Design léger et confortable : le corps principal de ces larges lunettes de sécurité est"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.3026041506379501,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.3026041506379501,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EMSS12102L"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "EMSS12102L%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "acier",
      "douilles",
      "emss12102l",
      "en",
      "fabriquees",
      "les",
      "quel",
      "sont"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "82e47b1b4720ef73",
    "4402b6c3eca2fbc3"
  ]
}
```

```json
{
  "query_id": "HV2-06",
  "query": "En quel acier sont fabriquées les douilles EMSS12102L ?",
  "expected": [
    {
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "chunk_ids": [
        "0a001bc9ecfb185c"
      ],
      "substring": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail."
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "0a001bc9ecfb185c",
      "score": 1.9473958493620498,
      "text": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail.",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "0a001bc9ecfb185c",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. La douille est forgée d’une seule pièce en acier au chrome-molybdène, avec traitement antirouille par phosphatation noire et trempe à haute température ; elle offre une grande dureté, une forte résistance aux chocs, et une durabilité accrue ;\n2. La gamme de douilles est complète, avec une longueur rallongée et une profondeur plus importante. L’interface hexagonale interne épaissie permet un couple élevé et se casse difficilement. Le couple requis peut être ajusté selon les différents besoins de travail."
      },
      "dense_score": 0.6684261,
      "dense_rank": 30,
      "lexical_score": 1.9473958493620498,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6973958493620499,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "e1812f6b0d73ffe6",
      "score": 1.7807128041956686,
      "text": "3. La douille est équipée d’un trou anti-décrochage et d’une rainure de fixation pour bague\n10 pièces, jeu de douilles à choc profond 1/2\" DR. Tailles : 10, 12, 13, 14, 15, 17, 19, 21, 22, 24 mm Longueur : 78 mm Matériau : CrMo Traitement thermique Conditionné en BMC",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e1812f6b0d73ffe6",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "3. La douille est équipée d’un trou anti-décrochage et d’une rainure de fixation pour bague\n10 pièces, jeu de douilles à choc profond 1/2\" DR. Tailles : 10, 12, 13, 14, 15, 17, 19, 21, 22, 24 mm Longueur : 78 mm Matériau : CrMo Traitement thermique Conditionné en BMC"
      },
      "dense_score": 0.64065963,
      "dense_rank": 74,
      "lexical_score": 1.7807128041956686,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.5307128041956685,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "634fcfdb234afb91",
      "score": 1.5187268211362037,
      "text": "mines, métallurgie, construction navale, réparation automobile et autres industries,\nmaintenance de machines lourdes et démontage/montage de grosses vis, peut être utilisé\navec des outils pneumatiques de type clé à chocs",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "634fcfdb234afb91",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "mines, métallurgie, construction navale, réparation automobile et autres industries,\nmaintenance de machines lourdes et démontage/montage de grosses vis, peut être utilisé\navec des outils pneumatiques de type clé à chocs"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5187268211362037,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.26872682113620366,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "75ee813780fa6e6e",
      "score": 1.5187268211362037,
      "text": "Convient aux clés à chocs pneumatiques et électriques, etc. Excellente résistance aux impacts, couple plus élevé ;",
      "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "file_name": "EMSS12102L%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
      "parent_id": "82e47b1b4720ef73",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "75ee813780fa6e6e",
        "document_id": "full-EMSS12102L%20Technical%20Data-a8fa8e71",
        "source_path": "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf",
        "file_name": "EMSS12102L%20Technical%20Data.pdf",
        "parent_id": "82e47b1b4720ef73",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Convient aux clés à chocs pneumatiques et électriques, etc. Excellente résistance aux impacts, couple plus élevé ;"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5187268211362037,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.26872682113620366,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "56635349b150c7d8",
      "score": 0.3026041506379501,
      "text": "1. Lunettes de protection scientifiques et sécuritaires : nos lunettes de protection sont étanches, résistantes aux chocs, et peuvent non seulement bloquer les éclaboussures de salive, les projections et la poussière.\n2. Lunettes de protection anti-buée réutilisables : les lunettes de sécurité anti-buée possèdent un revêtement anti-buée, les verres ne s'embuent pas facilement lorsqu'ils sont exposés à la vapeur d'eau.\n3. Lunettes de haute qualité : fabriquées en matériau PC anti-explosion, elles sont légères, résistantes, anti-choc, capables de supporter une forte pression, durables et esthétiques.\n4. Design léger et confortable : le corps principal de ces larges lunettes de sécurité est",
      "document_id": "full-ESGG0101%20Technical%20Data-513ddd55",
      "file_name": "ESGG0101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ESGG0101%20Technical%20Data.pdf",
      "parent_id": "4402b6c3eca2fbc3",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "56635349b150c7d8",
        "document_id": "full-ESGG0101%20Technical%20Data-513ddd55",
        "source_path": "ai_data\\raw\\emtop\\ESGG0101%20Technical%20Data.pdf",
        "file_name": "ESGG0101%20Technical%20Data.pdf",
        "parent_id": "4402b6c3eca2fbc3",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Lunettes de protection scientifiques et sécuritaires : nos lunettes de protection sont étanches, résistantes aux chocs, et peuvent non seulement bloquer les éclaboussures de salive, les projections et la poussière.\n2. Lunettes de protection anti-buée réutilisables : les lunettes de sécurité anti-buée possèdent un revêtement anti-buée, les verres ne s'embuent pas facilement lorsqu'ils sont exposés à la vapeur d'eau.\n3. Lunettes de haute qualité : fabriquées en matériau PC anti-explosion, elles sont légères, résistantes, anti-choc, capables de supporter une forte pression, durables et esthétiques.\n4. Design léger et confortable : le corps principal de ces larges lunettes de sécurité est"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.3026041506379501,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.3026041506379501,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EMSS12102L"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EMSS12102L%20Technical%20Data-a8fa8e71",
      "EMSS12102L%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EMSS12102L%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "acier",
      "douilles",
      "emss12102l",
      "en",
      "fabriquees",
      "les",
      "quel",
      "sont"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "82e47b1b4720ef73",
    "4402b6c3eca2fbc3"
  ]
}
```

```json
{
  "query_id": "HV2-07",
  "query": "À quel DTU se référer pour préparer les supports de RUSTIKA TYROLIEN ?",
  "expected": [
    {
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "chunk_ids": [
        "141e0f1f0585631f"
      ],
      "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "f153903bddd627af",
      "score": 0.8066102,
      "text": "Préparation du Support (DTU 59.1):",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "f153903bddd627af",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Préparation du Support (DTU 59.1):"
      }
    },
    {
      "chunk_id": "100f6af3e5bd24df",
      "score": 0.8066102,
      "text": "Préparation du Support (DTU 59.1):",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": "4c6a6737fb23f8b0",
      "section_path": [
        "FINACEM CACHET ROUGE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "100f6af3e5bd24df",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": "4c6a6737fb23f8b0",
        "section_path": [
          "FINACEM CACHET ROUGE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Préparation du Support (DTU 59.1):"
      }
    },
    {
      "chunk_id": "141e0f1f0585631f",
      "score": 0.79688716,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "774ce52d9a7008e7",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "141e0f1f0585631f",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "774ce52d9a7008e7",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
      }
    },
    {
      "chunk_id": "a72214f0a36995eb",
      "score": 0.7903493,
      "text": "Préparation du Support (DTU 26-1)",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "file_name": "ISBAROC-R.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
      "parent_id": "b4c2af1d54d3c42d",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "a72214f0a36995eb",
        "document_id": "full-ISBAROC-R-3a4b4eb9",
        "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
        "file_name": "ISBAROC-R.pdf",
        "parent_id": "b4c2af1d54d3c42d",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Préparation du Support (DTU 26-1)"
      }
    },
    {
      "chunk_id": "799d9b539159cf24",
      "score": 0.7903493,
      "text": "Préparation du Support (DTU 26-1)",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "5657a88c2b7bae8a",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "799d9b539159cf24",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "5657a88c2b7bae8a",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Préparation du Support (DTU 26-1)"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-07",
  "query": "À quel DTU se référer pour préparer les supports de RUSTIKA TYROLIEN ?",
  "expected": [
    {
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "chunk_ids": [
        "141e0f1f0585631f"
      ],
      "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.5,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.5,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "8e28b04914f62ba0",
      "score": 0.5413241991351707,
      "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter.",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
      "parent_id": "0debe0ca3f77bd9c",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8e28b04914f62ba0",
        "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
        "file_name": "RUSTIKA%20GRAVITA1.pdf",
        "parent_id": "0debe0ca3f77bd9c",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "141e0f1f0585631f",
      "score": 0.5413241991351707,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "774ce52d9a7008e7",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "141e0f1f0585631f",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "774ce52d9a7008e7",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "bcf7f1df2a8282af",
      "score": 0.5413241991351707,
      "text": "Supports Admissibles : support conforme au DTU 26.1.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "68ca8b54f2fbfd97",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "bcf7f1df2a8282af",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "68ca8b54f2fbfd97",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Supports Admissibles : support conforme au DTU 26.1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "031906020217a37a",
      "score": 0.5199119099404449,
      "text": "• Après l’humidiﬁcaƟon et la dispariƟon du ﬁlm d’eau, appliquer à la tyrolienne l’enduit RUSTIKA TYROLIEN. L’opéraƟon se fait en 3 passes :\n• Projeter la 1ère passe perpendiculairement au mur pour couvrir le support et l’appariƟon de spectres de joints de maçonnerie.\n• Laisser « Ɵrer » ceƩe 1ère passe.\n•  Projeter la 2ème passe en biais par rapport au mur.\n• Laisser « Ɵrer » ceƩe deuxième passe.\n• Projeter la 3ème passe en biais de l’autre côté.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "2e17fa0b9311a335",
      "section_path": [
        "RUSTIKA TYROLIEN"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "031906020217a37a",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "2e17fa0b9311a335",
        "section_path": [
          "RUSTIKA TYROLIEN"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Après l’humidiﬁcaƟon et la dispariƟon du ﬁlm d’eau, appliquer à la tyrolienne l’enduit RUSTIKA TYROLIEN. L’opéraƟon se fait en 3 passes :\n• Projeter la 1ère passe perpendiculairement au mur pour couvrir le support et l’appariƟon de spectres de joints de maçonnerie.\n• Laisser « Ɵrer » ceƩe 1ère passe.\n•  Projeter la 2ème passe en biais par rapport au mur.\n• Laisser « Ɵrer » ceƩe deuxième passe.\n• Projeter la 3ème passe en biais de l’autre côté."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5199119099404449,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.35324524327377826,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "fa9c97f5d5eb3ce6",
      "score": 0.5199119099404449,
      "text": "RUSTIKA TYROLIEN est un enduit de parement décoraƟf en poudre, hautement hydrofugé qui s’applique à la tyrolienne. Il permet des ﬁniƟons « moucheƟs » brut ou écrasé, en intérieur et extérieur.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fa9c97f5d5eb3ce6",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "RUSTIKA TYROLIEN est un enduit de parement décoraƟf en poudre, hautement hydrofugé qui s’applique à la tyrolienne. Il permet des ﬁniƟons « moucheƟs » brut ou écrasé, en intérieur et extérieur."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5199119099404449,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.35324524327377826,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "de",
      "dtu",
      "les",
      "pour",
      "preparer",
      "quel",
      "referer",
      "rustika",
      "se",
      "supports",
      "tyrolien"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "0debe0ca3f77bd9c",
    "774ce52d9a7008e7",
    "68ca8b54f2fbfd97",
    "2e17fa0b9311a335"
  ]
}
```

```json
{
  "query_id": "HV2-07",
  "query": "À quel DTU se référer pour préparer les supports de RUSTIKA TYROLIEN ?",
  "expected": [
    {
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "chunk_ids": [
        "141e0f1f0585631f"
      ],
      "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.5,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.5,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "8e28b04914f62ba0",
      "score": 0.5413241991351707,
      "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter.",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
      "parent_id": "0debe0ca3f77bd9c",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8e28b04914f62ba0",
        "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
        "file_name": "RUSTIKA%20GRAVITA1.pdf",
        "parent_id": "0debe0ca3f77bd9c",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "141e0f1f0585631f",
      "score": 0.5413241991351707,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "774ce52d9a7008e7",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "141e0f1f0585631f",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "774ce52d9a7008e7",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "bcf7f1df2a8282af",
      "score": 0.5413241991351707,
      "text": "Supports Admissibles : support conforme au DTU 26.1.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "68ca8b54f2fbfd97",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "bcf7f1df2a8282af",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "68ca8b54f2fbfd97",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Supports Admissibles : support conforme au DTU 26.1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "031906020217a37a",
      "score": 0.5199119099404449,
      "text": "• Après l’humidiﬁcaƟon et la dispariƟon du ﬁlm d’eau, appliquer à la tyrolienne l’enduit RUSTIKA TYROLIEN. L’opéraƟon se fait en 3 passes :\n• Projeter la 1ère passe perpendiculairement au mur pour couvrir le support et l’appariƟon de spectres de joints de maçonnerie.\n• Laisser « Ɵrer » ceƩe 1ère passe.\n•  Projeter la 2ème passe en biais par rapport au mur.\n• Laisser « Ɵrer » ceƩe deuxième passe.\n• Projeter la 3ème passe en biais de l’autre côté.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "2e17fa0b9311a335",
      "section_path": [
        "RUSTIKA TYROLIEN"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "031906020217a37a",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "2e17fa0b9311a335",
        "section_path": [
          "RUSTIKA TYROLIEN"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Après l’humidiﬁcaƟon et la dispariƟon du ﬁlm d’eau, appliquer à la tyrolienne l’enduit RUSTIKA TYROLIEN. L’opéraƟon se fait en 3 passes :\n• Projeter la 1ère passe perpendiculairement au mur pour couvrir le support et l’appariƟon de spectres de joints de maçonnerie.\n• Laisser « Ɵrer » ceƩe 1ère passe.\n•  Projeter la 2ème passe en biais par rapport au mur.\n• Laisser « Ɵrer » ceƩe deuxième passe.\n• Projeter la 3ème passe en biais de l’autre côté."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5199119099404449,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.35324524327377826,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "fa9c97f5d5eb3ce6",
      "score": 0.5199119099404449,
      "text": "RUSTIKA TYROLIEN est un enduit de parement décoraƟf en poudre, hautement hydrofugé qui s’applique à la tyrolienne. Il permet des ﬁniƟons « moucheƟs » brut ou écrasé, en intérieur et extérieur.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fa9c97f5d5eb3ce6",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "RUSTIKA TYROLIEN est un enduit de parement décoraƟf en poudre, hautement hydrofugé qui s’applique à la tyrolienne. Il permet des ﬁniƟons « moucheƟs » brut ou écrasé, en intérieur et extérieur."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5199119099404449,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.35324524327377826,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "de",
      "dtu",
      "les",
      "pour",
      "preparer",
      "quel",
      "referer",
      "rustika",
      "se",
      "supports",
      "tyrolien"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "0debe0ca3f77bd9c",
    "774ce52d9a7008e7",
    "68ca8b54f2fbfd97",
    "2e17fa0b9311a335"
  ]
}
```

```json
{
  "query_id": "HV2-07",
  "query": "À quel DTU se référer pour préparer les supports de RUSTIKA TYROLIEN ?",
  "expected": [
    {
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "chunk_ids": [
        "141e0f1f0585631f"
      ],
      "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "141e0f1f0585631f",
      "score": 0.5413241991351707,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "774ce52d9a7008e7",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "141e0f1f0585631f",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "774ce52d9a7008e7",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 26.1\n• Les supports seront sains,propres, dépoussiérés, stables et résistants."
      },
      "dense_score": 0.79688716,
      "dense_rank": 3,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "bcf7f1df2a8282af",
      "score": 0.5413241991351707,
      "text": "Supports Admissibles : support conforme au DTU 26.1.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "68ca8b54f2fbfd97",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "bcf7f1df2a8282af",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "68ca8b54f2fbfd97",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Supports Admissibles : support conforme au DTU 26.1."
      },
      "dense_score": 0.74694353,
      "dense_rank": 29,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "8e28b04914f62ba0",
      "score": 0.5413241991351707,
      "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter.",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
      "parent_id": "0debe0ca3f77bd9c",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8e28b04914f62ba0",
        "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
        "file_name": "RUSTIKA%20GRAVITA1.pdf",
        "parent_id": "0debe0ca3f77bd9c",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter."
      },
      "dense_score": 0.7414123,
      "dense_rank": 33,
      "lexical_score": 0.5413241991351707,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3746575324685041,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "fa9c97f5d5eb3ce6",
      "score": 0.5199119099404449,
      "text": "RUSTIKA TYROLIEN est un enduit de parement décoraƟf en poudre, hautement hydrofugé qui s’applique à la tyrolienne. Il permet des ﬁniƟons « moucheƟs » brut ou écrasé, en intérieur et extérieur.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fa9c97f5d5eb3ce6",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "RUSTIKA TYROLIEN est un enduit de parement décoraƟf en poudre, hautement hydrofugé qui s’applique à la tyrolienne. Il permet des ﬁniƟons « moucheƟs » brut ou écrasé, en intérieur et extérieur."
      },
      "dense_score": 0.7217318,
      "dense_rank": 46,
      "lexical_score": 0.5199119099404449,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.35324524327377826,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "031906020217a37a",
      "score": 0.5199119099404449,
      "text": "• Après l’humidiﬁcaƟon et la dispariƟon du ﬁlm d’eau, appliquer à la tyrolienne l’enduit RUSTIKA TYROLIEN. L’opéraƟon se fait en 3 passes :\n• Projeter la 1ère passe perpendiculairement au mur pour couvrir le support et l’appariƟon de spectres de joints de maçonnerie.\n• Laisser « Ɵrer » ceƩe 1ère passe.\n•  Projeter la 2ème passe en biais par rapport au mur.\n• Laisser « Ɵrer » ceƩe deuxième passe.\n• Projeter la 3ème passe en biais de l’autre côté.",
      "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
      "file_name": "RUSTIKA%20TYROLIEN1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
      "parent_id": "2e17fa0b9311a335",
      "section_path": [
        "RUSTIKA TYROLIEN"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "031906020217a37a",
        "document_id": "full-RUSTIKA%20TYROLIEN1-b9628ec3",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20TYROLIEN1.pdf",
        "file_name": "RUSTIKA%20TYROLIEN1.pdf",
        "parent_id": "2e17fa0b9311a335",
        "section_path": [
          "RUSTIKA TYROLIEN"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Après l’humidiﬁcaƟon et la dispariƟon du ﬁlm d’eau, appliquer à la tyrolienne l’enduit RUSTIKA TYROLIEN. L’opéraƟon se fait en 3 passes :\n• Projeter la 1ère passe perpendiculairement au mur pour couvrir le support et l’appariƟon de spectres de joints de maçonnerie.\n• Laisser « Ɵrer » ceƩe 1ère passe.\n•  Projeter la 2ème passe en biais par rapport au mur.\n• Laisser « Ɵrer » ceƩe deuxième passe.\n• Projeter la 3ème passe en biais de l’autre côté."
      },
      "dense_score": 0.69878733,
      "dense_rank": 68,
      "lexical_score": 0.5199119099404449,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.35324524327377826,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "de",
      "dtu",
      "les",
      "pour",
      "preparer",
      "quel",
      "referer",
      "rustika",
      "se",
      "supports",
      "tyrolien"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "774ce52d9a7008e7",
    "68ca8b54f2fbfd97",
    "0debe0ca3f77bd9c",
    "2e17fa0b9311a335"
  ]
}
```

```json
{
  "query_id": "HV2-08",
  "query": "Combien de types de mandrins sont fournis avec EMAT5541 ?",
  "expected": [
    {
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "chunk_ids": [
        "16c3b9f4450fb430"
      ],
      "substring": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1cd6a809254993db",
      "score": 0.6996254,
      "text": "42 mm Système de mandrin SDS plus",
      "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
      "file_name": "ERHRP1801%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
      "parent_id": "da7b16f47e71f086",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "1cd6a809254993db",
        "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
        "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
        "file_name": "ERHRP1801%20Technical%20Data.pdf",
        "parent_id": "da7b16f47e71f086",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "42 mm Système de mandrin SDS plus"
      }
    },
    {
      "chunk_id": "54de190bfdd69ad6",
      "score": 0.69451886,
      "text": "ConsommaƟon: | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": "c411d14abbdf8885",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1."
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "54de190bfdd69ad6",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": "c411d14abbdf8885",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1."
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ConsommaƟon: | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi."
      }
    },
    {
      "chunk_id": "f92831801a1cf601",
      "score": 0.69433045,
      "text": "•  Les valeurs des caractérisƟques techniques sont des valeurs staƟsƟques moyennes et qui peuvent être mises à jour sans préavis.",
      "document_id": "full-PRO%20200%20V4-8f310261",
      "file_name": "PRO%20200%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
      "parent_id": "6ca19defdb73ac8a",
      "section_path": [
        "MENTION LÉGALE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "f92831801a1cf601",
        "document_id": "full-PRO%20200%20V4-8f310261",
        "source_path": "ai_data\\raw\\sofap\\PRO%20200%20V4.pdf",
        "file_name": "PRO%20200%20V4.pdf",
        "parent_id": "6ca19defdb73ac8a",
        "section_path": [
          "MENTION LÉGALE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "•  Les valeurs des caractérisƟques techniques sont des valeurs staƟsƟques moyennes et qui peuvent être mises à jour sans préavis."
      }
    },
    {
      "chunk_id": "aab1b89d43a0f3d1",
      "score": 0.69433045,
      "text": "• Les valeurs des caractérisƟques techniques sont des valeurs staƟsƟques moyennes et qui peuvent être mises à jour sans préavis.",
      "document_id": "full-SUPERDUR1-8aaac074",
      "file_name": "SUPERDUR1.pdf",
      "source_path": "ai_data\\raw\\sofap\\SUPERDUR1.pdf",
      "parent_id": "22b42d55d47356fe",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "aab1b89d43a0f3d1",
        "document_id": "full-SUPERDUR1-8aaac074",
        "source_path": "ai_data\\raw\\sofap\\SUPERDUR1.pdf",
        "file_name": "SUPERDUR1.pdf",
        "parent_id": "22b42d55d47356fe",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les valeurs des caractérisƟques techniques sont des valeurs staƟsƟques moyennes et qui peuvent être mises à jour sans préavis."
      }
    },
    {
      "chunk_id": "b720169fe44cd03a",
      "score": 0.6909044,
      "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "50742f9117acc4d4",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "b720169fe44cd03a",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "50742f9117acc4d4",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-08",
  "query": "Combien de types de mandrins sont fournis avec EMAT5541 ?",
  "expected": [
    {
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "chunk_ids": [
        "16c3b9f4450fb430"
      ],
      "substring": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "16c3b9f4450fb430",
      "score": 1.9949493717749625,
      "text": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "16c3b9f4450fb430",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.9949493717749625,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.7449493717749623,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "9cad0eefa5ab0ef1",
      "score": 1.4883025052252086,
      "text": "Convient pour l'usinage de précision de divers métaux, le meulage de surfaces planes, le meulage des chanfreins, l'ébavurage, le polissage, la gravure, etc.",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "9cad0eefa5ab0ef1",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Convient pour l'usinage de précision de divers métaux, le meulage de surfaces planes, le meulage des chanfreins, l'ébavurage, le polissage, la gravure, etc."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d867d5ac24847cda",
      "score": 1.4883025052252086,
      "text": "22 000/min Entrée d'air : 1/4\" Tuyau d'air (ID) : 3/8\" Consommation d'air moyenne : 4,5 cfm (128,3 l/min) Pression d'air de fonctionnement : 6,3 bar (90 PSI) ) Emballé par boîte de couleur",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d867d5ac24847cda",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "22 000/min Entrée d'air : 1/4\" Tuyau d'air (ID) : 3/8\" Consommation d'air moyenne : 4,5 cfm (128,3 l/min) Pression d'air de fonctionnement : 6,3 bar (90 PSI) ) Emballé par boîte de couleur"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "eb2ab4d327732acf",
      "score": 1.4883025052252086,
      "text": "Sans bouchon rapide Capuchon de broyeur : 6 mm et 3 mm Vitesse libre :",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "e1c8828ae3017776",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "eb2ab4d327732acf",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "e1c8828ae3017776",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Sans bouchon rapide Capuchon de broyeur : 6 mm et 3 mm Vitesse libre :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "581670aa3d744503",
      "score": 0.2550506282250377,
      "text": "1. Le tuyau d'eau de 1/2’’ peut être rangé sur 40 m\n2. Pas d'assemblage, il suffit de connecter le tuyau pour l'utiliser\n3. Utilisation d'un enrouleur avec poignée pour un rangement plus facile\n4. Peut être suspendu au mur avec les supports supérieur et inférieur fournis\n5. Coque gauche et droite avec prise pour pistolet à eau",
      "document_id": "full-EHHR20124%20Technical%20Data-ebd32e63",
      "file_name": "EHHR20124%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EHHR20124%20Technical%20Data.pdf",
      "parent_id": "3af45d094a6fd160",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "581670aa3d744503",
        "document_id": "full-EHHR20124%20Technical%20Data-ebd32e63",
        "source_path": "ai_data\\raw\\emtop\\EHHR20124%20Technical%20Data.pdf",
        "file_name": "EHHR20124%20Technical%20Data.pdf",
        "parent_id": "3af45d094a6fd160",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Le tuyau d'eau de 1/2’’ peut être rangé sur 40 m\n2. Pas d'assemblage, il suffit de connecter le tuyau pour l'utiliser\n3. Utilisation d'un enrouleur avec poignée pour un rangement plus facile\n4. Peut être suspendu au mur avec les supports supérieur et inférieur fournis\n5. Coque gauche et droite avec prise pour pistolet à eau"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.2550506282250377,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.2550506282250377,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EMAT5541"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "EMAT5541%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "avec",
      "combien",
      "de",
      "emat5541",
      "fournis",
      "mandrins",
      "sont",
      "types"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "93f5d0efddf6b54f",
    "e1c8828ae3017776",
    "3af45d094a6fd160"
  ]
}
```

```json
{
  "query_id": "HV2-08",
  "query": "Combien de types de mandrins sont fournis avec EMAT5541 ?",
  "expected": [
    {
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "chunk_ids": [
        "16c3b9f4450fb430"
      ],
      "substring": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "16c3b9f4450fb430",
      "score": 1.9949493717749625,
      "text": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "16c3b9f4450fb430",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.9949493717749625,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.7449493717749623,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "9cad0eefa5ab0ef1",
      "score": 1.4883025052252086,
      "text": "Convient pour l'usinage de précision de divers métaux, le meulage de surfaces planes, le meulage des chanfreins, l'ébavurage, le polissage, la gravure, etc.",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "9cad0eefa5ab0ef1",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Convient pour l'usinage de précision de divers métaux, le meulage de surfaces planes, le meulage des chanfreins, l'ébavurage, le polissage, la gravure, etc."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "d867d5ac24847cda",
      "score": 1.4883025052252086,
      "text": "22 000/min Entrée d'air : 1/4\" Tuyau d'air (ID) : 3/8\" Consommation d'air moyenne : 4,5 cfm (128,3 l/min) Pression d'air de fonctionnement : 6,3 bar (90 PSI) ) Emballé par boîte de couleur",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d867d5ac24847cda",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "22 000/min Entrée d'air : 1/4\" Tuyau d'air (ID) : 3/8\" Consommation d'air moyenne : 4,5 cfm (128,3 l/min) Pression d'air de fonctionnement : 6,3 bar (90 PSI) ) Emballé par boîte de couleur"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "eb2ab4d327732acf",
      "score": 1.4883025052252086,
      "text": "Sans bouchon rapide Capuchon de broyeur : 6 mm et 3 mm Vitesse libre :",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "e1c8828ae3017776",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "eb2ab4d327732acf",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "e1c8828ae3017776",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Sans bouchon rapide Capuchon de broyeur : 6 mm et 3 mm Vitesse libre :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "581670aa3d744503",
      "score": 0.2550506282250377,
      "text": "1. Le tuyau d'eau de 1/2’’ peut être rangé sur 40 m\n2. Pas d'assemblage, il suffit de connecter le tuyau pour l'utiliser\n3. Utilisation d'un enrouleur avec poignée pour un rangement plus facile\n4. Peut être suspendu au mur avec les supports supérieur et inférieur fournis\n5. Coque gauche et droite avec prise pour pistolet à eau",
      "document_id": "full-EHHR20124%20Technical%20Data-ebd32e63",
      "file_name": "EHHR20124%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EHHR20124%20Technical%20Data.pdf",
      "parent_id": "3af45d094a6fd160",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "581670aa3d744503",
        "document_id": "full-EHHR20124%20Technical%20Data-ebd32e63",
        "source_path": "ai_data\\raw\\emtop\\EHHR20124%20Technical%20Data.pdf",
        "file_name": "EHHR20124%20Technical%20Data.pdf",
        "parent_id": "3af45d094a6fd160",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Le tuyau d'eau de 1/2’’ peut être rangé sur 40 m\n2. Pas d'assemblage, il suffit de connecter le tuyau pour l'utiliser\n3. Utilisation d'un enrouleur avec poignée pour un rangement plus facile\n4. Peut être suspendu au mur avec les supports supérieur et inférieur fournis\n5. Coque gauche et droite avec prise pour pistolet à eau"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.2550506282250377,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.2550506282250377,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EMAT5541"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "EMAT5541%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "avec",
      "combien",
      "de",
      "emat5541",
      "fournis",
      "mandrins",
      "sont",
      "types"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "93f5d0efddf6b54f",
    "e1c8828ae3017776",
    "3af45d094a6fd160"
  ]
}
```

```json
{
  "query_id": "HV2-08",
  "query": "Combien de types de mandrins sont fournis avec EMAT5541 ?",
  "expected": [
    {
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "chunk_ids": [
        "16c3b9f4450fb430"
      ],
      "substring": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "16c3b9f4450fb430",
      "score": 1.9949493717749625,
      "text": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "16c3b9f4450fb430",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Manchon en caoutchouc développé, anti-vibration, isolant thermique, conforme à la conception ergonomique\n2. Gâchette développée, utilisation plus fluide\n3. Haute vitesse, fonction de réglage de vitesse variable, adaptée à diverses conditions de travail\n4. Livré avec 2 types de mandrins différents, compatibles avec différentes tailles de meules"
      },
      "dense_score": 0.67227894,
      "dense_rank": 47,
      "lexical_score": 1.9949493717749625,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.7449493717749623,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "9cad0eefa5ab0ef1",
      "score": 1.4883025052252086,
      "text": "Convient pour l'usinage de précision de divers métaux, le meulage de surfaces planes, le meulage des chanfreins, l'ébavurage, le polissage, la gravure, etc.",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "9cad0eefa5ab0ef1",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Convient pour l'usinage de précision de divers métaux, le meulage de surfaces planes, le meulage des chanfreins, l'ébavurage, le polissage, la gravure, etc."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "d867d5ac24847cda",
      "score": 1.4883025052252086,
      "text": "22 000/min Entrée d'air : 1/4\" Tuyau d'air (ID) : 3/8\" Consommation d'air moyenne : 4,5 cfm (128,3 l/min) Pression d'air de fonctionnement : 6,3 bar (90 PSI) ) Emballé par boîte de couleur",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "93f5d0efddf6b54f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d867d5ac24847cda",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "93f5d0efddf6b54f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "22 000/min Entrée d'air : 1/4\" Tuyau d'air (ID) : 3/8\" Consommation d'air moyenne : 4,5 cfm (128,3 l/min) Pression d'air de fonctionnement : 6,3 bar (90 PSI) ) Emballé par boîte de couleur"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "eb2ab4d327732acf",
      "score": 1.4883025052252086,
      "text": "Sans bouchon rapide Capuchon de broyeur : 6 mm et 3 mm Vitesse libre :",
      "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "file_name": "EMAT5541%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
      "parent_id": "e1c8828ae3017776",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "eb2ab4d327732acf",
        "document_id": "full-EMAT5541%20Technical%20Data-2a96a8ae",
        "source_path": "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf",
        "file_name": "EMAT5541%20Technical%20Data.pdf",
        "parent_id": "e1c8828ae3017776",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Sans bouchon rapide Capuchon de broyeur : 6 mm et 3 mm Vitesse libre :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4883025052252086,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.23830250522520852,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "581670aa3d744503",
      "score": 0.2550506282250377,
      "text": "1. Le tuyau d'eau de 1/2’’ peut être rangé sur 40 m\n2. Pas d'assemblage, il suffit de connecter le tuyau pour l'utiliser\n3. Utilisation d'un enrouleur avec poignée pour un rangement plus facile\n4. Peut être suspendu au mur avec les supports supérieur et inférieur fournis\n5. Coque gauche et droite avec prise pour pistolet à eau",
      "document_id": "full-EHHR20124%20Technical%20Data-ebd32e63",
      "file_name": "EHHR20124%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EHHR20124%20Technical%20Data.pdf",
      "parent_id": "3af45d094a6fd160",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "581670aa3d744503",
        "document_id": "full-EHHR20124%20Technical%20Data-ebd32e63",
        "source_path": "ai_data\\raw\\emtop\\EHHR20124%20Technical%20Data.pdf",
        "file_name": "EHHR20124%20Technical%20Data.pdf",
        "parent_id": "3af45d094a6fd160",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Le tuyau d'eau de 1/2’’ peut être rangé sur 40 m\n2. Pas d'assemblage, il suffit de connecter le tuyau pour l'utiliser\n3. Utilisation d'un enrouleur avec poignée pour un rangement plus facile\n4. Peut être suspendu au mur avec les supports supérieur et inférieur fournis\n5. Coque gauche et droite avec prise pour pistolet à eau"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.2550506282250377,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.2550506282250377,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EMAT5541"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EMAT5541%20Technical%20Data-2a96a8ae",
      "EMAT5541%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EMAT5541%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "avec",
      "combien",
      "de",
      "emat5541",
      "fournis",
      "mandrins",
      "sont",
      "types"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "93f5d0efddf6b54f",
    "e1c8828ae3017776",
    "3af45d094a6fd160"
  ]
}
```

```json
{
  "query_id": "HV2-09",
  "query": "Quels supports sont interdits pour ISBAROC R selon sa fiche R1 ?",
  "expected": [
    {
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "chunk_ids": [
        "1977a381add0de0f"
      ],
      "substring": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "bddadaf8c1cd0a1f",
      "score": 0.7471851,
      "text": "au moins 2 jours avant et en utilisant ISBAROC R.",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "file_name": "ISBAROC-R.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
      "parent_id": "b4c2af1d54d3c42d",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "bddadaf8c1cd0a1f",
        "document_id": "full-ISBAROC-R-3a4b4eb9",
        "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
        "file_name": "ISBAROC-R.pdf",
        "parent_id": "b4c2af1d54d3c42d",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "au moins 2 jours avant et en utilisant ISBAROC R."
      }
    },
    {
      "chunk_id": "c8a1971975a3c484",
      "score": 0.7468818,
      "text": "Conseil :\nPréparaƟon du support :",
      "document_id": "full-MARBRE%20V4-5e49c875",
      "file_name": "MARBRE%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MARBRE%20V4.pdf",
      "parent_id": "11fdf9064fe2984d",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "c8a1971975a3c484",
        "document_id": "full-MARBRE%20V4-5e49c875",
        "source_path": "ai_data\\raw\\sofap\\MARBRE%20V4.pdf",
        "file_name": "MARBRE%20V4.pdf",
        "parent_id": "11fdf9064fe2984d",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conseil :\nPréparaƟon du support :"
      }
    },
    {
      "chunk_id": "71e680d35400bbf3",
      "score": 0.7465235,
      "text": "• Classe RT2 et RT3 (béton, brique et maçonnerie de parpings…) selon DTU 26.1.\n• Maçonneries anciennes et autres supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre.",
      "document_id": "full-FULL%201-eb0d29c6",
      "file_name": "FULL%201.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
      "parent_id": "429924a0c5fccf4f",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "71e680d35400bbf3",
        "document_id": "full-FULL%201-eb0d29c6",
        "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
        "file_name": "FULL%201.pdf",
        "parent_id": "429924a0c5fccf4f",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique et maçonnerie de parpings…) selon DTU 26.1.\n• Maçonneries anciennes et autres supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
      }
    },
    {
      "chunk_id": "1e22000f776ecf87",
      "score": 0.7452308,
      "text": "ISBAROC R est un enduit sous couche d’usage courant, desƟné à l’applicaƟon mécanique  sur les murs intérieurs et extérieurs.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "1e22000f776ecf87",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ISBAROC R est un enduit sous couche d’usage courant, desƟné à l’applicaƟon mécanique  sur les murs intérieurs et extérieurs."
      }
    },
    {
      "chunk_id": "8ed2bc02e7f85eb2",
      "score": 0.7441441,
      "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autres supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre.",
      "document_id": "full-LIKA%20FINA1-890840ee",
      "file_name": "LIKA%20FINA1.pdf",
      "source_path": "ai_data\\raw\\sofap\\LIKA%20FINA1.pdf",
      "parent_id": "c5129aa55c90673e",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "8ed2bc02e7f85eb2",
        "document_id": "full-LIKA%20FINA1-890840ee",
        "source_path": "ai_data\\raw\\sofap\\LIKA%20FINA1.pdf",
        "file_name": "LIKA%20FINA1.pdf",
        "parent_id": "c5129aa55c90673e",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autres supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-09",
  "query": "Quels supports sont interdits pour ISBAROC R selon sa fiche R1 ?",
  "expected": [
    {
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "chunk_ids": [
        "1977a381add0de0f"
      ],
      "substring": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1977a381add0de0f",
      "score": 0.8694266099546438,
      "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "4782ab91802b6335",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1977a381add0de0f",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "4782ab91802b6335",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.8694266099546438,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6194266099546438,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "fa51b798bf96bebb",
      "score": 0.7179940739951238,
      "text": "Supports Interdits :",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "file_name": "ISBAROC-R.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
      "parent_id": "ca4e602fe65f328d",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fa51b798bf96bebb",
        "document_id": "full-ISBAROC-R-3a4b4eb9",
        "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
        "file_name": "ISBAROC-R.pdf",
        "parent_id": "ca4e602fe65f328d",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Supports Interdits :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7179940739951238,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.4679940739951238,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "126e3e382dab64b2",
      "score": 0.6068544447040398,
      "text": "Il est classé comme morƟer de type GP CS IIΙ W0 selon NF ΕΝ 998-1.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "126e3e382dab64b2",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "Il est classé comme morƟer de type GP CS IIΙ W0 selon NF ΕΝ 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "b720169fe44cd03a",
      "score": 0.6068544447040398,
      "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "50742f9117acc4d4",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "b720169fe44cd03a",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "50742f9117acc4d4",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d01f9aff5cddcc4e",
      "score": 0.6068544447040398,
      "text": "• Pour les épaisseurs supérieures à 15 mm, l'enduit doit être appliqué en plusieurs couches successives, à espacer d'au moins 24 h.\n• AƩendre quelques minutes avant de dresser et d’égaliser la surface avec une règle en aluminium.\n• Après environ 4 heures selon les condiƟons environnementales et du type de surface, une fois le produit est durci, ﬁnir l’enduit avec une truelle en plasƟque ou en bois, pour obtenir une surface plus compacte apte à recevoir les ﬁniƟons ultérieures.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "eed7140b6cd8b0b1",
      "section_path": [
        "ISBAROC  ‘R’"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d01f9aff5cddcc4e",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "eed7140b6cd8b0b1",
        "section_path": [
          "ISBAROC  ‘R’"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Pour les épaisseurs supérieures à 15 mm, l'enduit doit être appliqué en plusieurs couches successives, à espacer d'au moins 24 h.\n• AƩendre quelques minutes avant de dresser et d’égaliser la surface avec une règle en aluminium.\n• Après environ 4 heures selon les condiƟons environnementales et du type de surface, une fois le produit est durci, ﬁnir l’enduit avec une truelle en plasƟque ou en bois, pour obtenir une surface plus compacte apte à recevoir les ﬁniƟons ultérieures."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "fiche",
      "interdits",
      "isbaroc",
      "pour",
      "quels",
      "r",
      "r1",
      "sa",
      "selon",
      "sont",
      "supports"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "4782ab91802b6335",
    "ca4e602fe65f328d",
    "50742f9117acc4d4",
    "eed7140b6cd8b0b1"
  ]
}
```

```json
{
  "query_id": "HV2-09",
  "query": "Quels supports sont interdits pour ISBAROC R selon sa fiche R1 ?",
  "expected": [
    {
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "chunk_ids": [
        "1977a381add0de0f"
      ],
      "substring": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1977a381add0de0f",
      "score": 0.8694266099546438,
      "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "4782ab91802b6335",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1977a381add0de0f",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "4782ab91802b6335",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.8694266099546438,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6194266099546438,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "fa51b798bf96bebb",
      "score": 0.7179940739951238,
      "text": "Supports Interdits :",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "file_name": "ISBAROC-R.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
      "parent_id": "ca4e602fe65f328d",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fa51b798bf96bebb",
        "document_id": "full-ISBAROC-R-3a4b4eb9",
        "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
        "file_name": "ISBAROC-R.pdf",
        "parent_id": "ca4e602fe65f328d",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Supports Interdits :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7179940739951238,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.4679940739951238,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "126e3e382dab64b2",
      "score": 0.6068544447040398,
      "text": "Il est classé comme morƟer de type GP CS IIΙ W0 selon NF ΕΝ 998-1.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "126e3e382dab64b2",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "Il est classé comme morƟer de type GP CS IIΙ W0 selon NF ΕΝ 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "b720169fe44cd03a",
      "score": 0.6068544447040398,
      "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "50742f9117acc4d4",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "b720169fe44cd03a",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "50742f9117acc4d4",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d01f9aff5cddcc4e",
      "score": 0.6068544447040398,
      "text": "• Pour les épaisseurs supérieures à 15 mm, l'enduit doit être appliqué en plusieurs couches successives, à espacer d'au moins 24 h.\n• AƩendre quelques minutes avant de dresser et d’égaliser la surface avec une règle en aluminium.\n• Après environ 4 heures selon les condiƟons environnementales et du type de surface, une fois le produit est durci, ﬁnir l’enduit avec une truelle en plasƟque ou en bois, pour obtenir une surface plus compacte apte à recevoir les ﬁniƟons ultérieures.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "eed7140b6cd8b0b1",
      "section_path": [
        "ISBAROC  ‘R’"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d01f9aff5cddcc4e",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "eed7140b6cd8b0b1",
        "section_path": [
          "ISBAROC  ‘R’"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Pour les épaisseurs supérieures à 15 mm, l'enduit doit être appliqué en plusieurs couches successives, à espacer d'au moins 24 h.\n• AƩendre quelques minutes avant de dresser et d’égaliser la surface avec une règle en aluminium.\n• Après environ 4 heures selon les condiƟons environnementales et du type de surface, une fois le produit est durci, ﬁnir l’enduit avec une truelle en plasƟque ou en bois, pour obtenir une surface plus compacte apte à recevoir les ﬁniƟons ultérieures."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "fiche",
      "interdits",
      "isbaroc",
      "pour",
      "quels",
      "r",
      "r1",
      "sa",
      "selon",
      "sont",
      "supports"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "4782ab91802b6335",
    "ca4e602fe65f328d",
    "50742f9117acc4d4",
    "eed7140b6cd8b0b1"
  ]
}
```

```json
{
  "query_id": "HV2-09",
  "query": "Quels supports sont interdits pour ISBAROC R selon sa fiche R1 ?",
  "expected": [
    {
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "chunk_ids": [
        "1977a381add0de0f"
      ],
      "substring": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1977a381add0de0f",
      "score": 0.8694266099546438,
      "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "4782ab91802b6335",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1977a381add0de0f",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "4782ab91802b6335",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter. Supports Interdits :\n• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
      },
      "dense_score": 0.7441434,
      "dense_rank": 7,
      "lexical_score": 0.8694266099546438,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6194266099546438,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "fa51b798bf96bebb",
      "score": 0.7179940739951238,
      "text": "Supports Interdits :",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "file_name": "ISBAROC-R.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
      "parent_id": "ca4e602fe65f328d",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fa51b798bf96bebb",
        "document_id": "full-ISBAROC-R-3a4b4eb9",
        "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
        "file_name": "ISBAROC-R.pdf",
        "parent_id": "ca4e602fe65f328d",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Supports Interdits :"
      },
      "dense_score": 0.7014049,
      "dense_rank": 23,
      "lexical_score": 0.7179940739951238,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.4679940739951238,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "b720169fe44cd03a",
      "score": 0.6068544447040398,
      "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "50742f9117acc4d4",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "b720169fe44cd03a",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "50742f9117acc4d4",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi"
      },
      "dense_score": 0.67648983,
      "dense_rank": 84,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "126e3e382dab64b2",
      "score": 0.6068544447040398,
      "text": "Il est classé comme morƟer de type GP CS IIΙ W0 selon NF ΕΝ 998-1.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "126e3e382dab64b2",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "Il est classé comme morƟer de type GP CS IIΙ W0 selon NF ΕΝ 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d01f9aff5cddcc4e",
      "score": 0.6068544447040398,
      "text": "• Pour les épaisseurs supérieures à 15 mm, l'enduit doit être appliqué en plusieurs couches successives, à espacer d'au moins 24 h.\n• AƩendre quelques minutes avant de dresser et d’égaliser la surface avec une règle en aluminium.\n• Après environ 4 heures selon les condiƟons environnementales et du type de surface, une fois le produit est durci, ﬁnir l’enduit avec une truelle en plasƟque ou en bois, pour obtenir une surface plus compacte apte à recevoir les ﬁniƟons ultérieures.",
      "document_id": "full-ISBAROC%20R1-1c9a7b6f",
      "file_name": "ISBAROC%20R1.pdf",
      "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
      "parent_id": "eed7140b6cd8b0b1",
      "section_path": [
        "ISBAROC  ‘R’"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d01f9aff5cddcc4e",
        "document_id": "full-ISBAROC%20R1-1c9a7b6f",
        "source_path": "ai_data\\raw\\sofap\\ISBAROC%20R1.pdf",
        "file_name": "ISBAROC%20R1.pdf",
        "parent_id": "eed7140b6cd8b0b1",
        "section_path": [
          "ISBAROC  ‘R’"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Pour les épaisseurs supérieures à 15 mm, l'enduit doit être appliqué en plusieurs couches successives, à espacer d'au moins 24 h.\n• AƩendre quelques minutes avant de dresser et d’égaliser la surface avec une règle en aluminium.\n• Après environ 4 heures selon les condiƟons environnementales et du type de surface, une fois le produit est durci, ﬁnir l’enduit avec une truelle en plasƟque ou en bois, pour obtenir une surface plus compacte apte à recevoir les ﬁniƟons ultérieures."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6068544447040398,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3568544447040399,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "fiche",
      "interdits",
      "isbaroc",
      "pour",
      "quels",
      "r",
      "r1",
      "sa",
      "selon",
      "sont",
      "supports"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "4782ab91802b6335",
    "ca4e602fe65f328d",
    "50742f9117acc4d4",
    "eed7140b6cd8b0b1"
  ]
}
```

```json
{
  "query_id": "HV2-10",
  "query": "LIKA FULL est-il prévu pour une application manuelle ou mécanique, et sur quels murs ?",
  "expected": [
    {
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "chunk_ids": [
        "1aa4f45f7ad68d38"
      ],
      "substring": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "2c44420576a14a4b",
      "score": 0.8108625,
      "text": "• LIKA FULL ECO est appliqué avec une machine à projeter en une seule couche jusqu'à une épaisseur de 20 mm .",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": "b152122a4501e702",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "2c44420576a14a4b",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": "b152122a4501e702",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• LIKA FULL ECO est appliqué avec une machine à projeter en une seule couche jusqu'à une épaisseur de 20 mm ."
      }
    },
    {
      "chunk_id": "c1e2e29c9854a922",
      "score": 0.7926512,
      "text": "NB: LIKA FULL ECO peut être gâcher mécaniquement et appliquer manuellement sous réserve de respecter le taux de gâchage et le temps de malaxage pour obtenir une pâte homogène.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": "b152122a4501e702",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "c1e2e29c9854a922",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": "b152122a4501e702",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "NB: LIKA FULL ECO peut être gâcher mécaniquement et appliquer manuellement sous réserve de respecter le taux de gâchage et le temps de malaxage pour obtenir une pâte homogène."
      }
    },
    {
      "chunk_id": "1aa4f45f7ad68d38",
      "score": 0.78694916,
      "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1.",
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "parent_id": "2701cbb89f2dfd9d",
      "section_path": [
        "DESCRIPTION PRODUIT __ _"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "1aa4f45f7ad68d38",
        "document_id": "full-FULL-88a1b942",
        "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
        "file_name": "FULL.pdf",
        "parent_id": "2701cbb89f2dfd9d",
        "section_path": [
          "DESCRIPTION PRODUIT __ _"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
      }
    },
    {
      "chunk_id": "ceaa0295d4a43ae2",
      "score": 0.770464,
      "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, desƟné à l’applicaƟon mécanique sur les murs extérieurs. Il est classé comme morƟer de type OC CS III W2 selon la norme nf EN 998-1.",
      "document_id": "full-FULL%201-eb0d29c6",
      "file_name": "FULL%201.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
      "parent_id": "429924a0c5fccf4f",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "ceaa0295d4a43ae2",
        "document_id": "full-FULL%201-eb0d29c6",
        "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
        "file_name": "FULL%201.pdf",
        "parent_id": "429924a0c5fccf4f",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, desƟné à l’applicaƟon mécanique sur les murs extérieurs. Il est classé comme morƟer de type OC CS III W2 selon la norme nf EN 998-1."
      }
    },
    {
      "chunk_id": "3f5dcce27d09ffc8",
      "score": 0.74369884,
      "text": "d’un agitateur mécanique jusqu’à l'obtention de la consistance crémeuse.\n© Laisser reposer quelques minutes puis malaxer de nouveau brièvement.\npuis appliquer LIKA FINA en deux passes successives (frais sur frais) avec",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "5657a88c2b7bae8a",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "3f5dcce27d09ffc8",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "5657a88c2b7bae8a",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "d’un agitateur mécanique jusqu’à l'obtention de la consistance crémeuse.\n© Laisser reposer quelques minutes puis malaxer de nouveau brièvement.\npuis appliquer LIKA FINA en deux passes successives (frais sur frais) avec"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-10",
  "query": "LIKA FULL est-il prévu pour une application manuelle ou mécanique, et sur quels murs ?",
  "expected": [
    {
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "chunk_ids": [
        "1aa4f45f7ad68d38"
      ],
      "substring": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1aa4f45f7ad68d38",
      "score": 0.7666167649140381,
      "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1.",
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "parent_id": "2701cbb89f2dfd9d",
      "section_path": [
        "DESCRIPTION PRODUIT __ _"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1aa4f45f7ad68d38",
        "document_id": "full-FULL-88a1b942",
        "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
        "file_name": "FULL.pdf",
        "parent_id": "2701cbb89f2dfd9d",
        "section_path": [
          "DESCRIPTION PRODUIT __ _"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7666167649140381,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.6237596220568952,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "754a782a4dcfb25e",
      "score": 0.6700786500915616,
      "text": "DESCRIPTION PRODUIT __ oôî®Œô&à=œïËî°ï=ï7’\nLIKA FINA est un enduit mince décoratif, hydrofugé, teinté dans la masse, destiné à l’application manuelle sur les murs extérieurs. il est classé comme mortier de type CR CS IIl W2 selon la norme NF EN 998-1.",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "7cc918e9864d26bc_1",
      "section_path": [
        "LIKA FINA"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "754a782a4dcfb25e",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "7cc918e9864d26bc_1",
        "section_path": [
          "LIKA FINA"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "DESCRIPTION PRODUIT __ oôî®Œô&à=œïËî°ï=ï7’\nLIKA FINA est un enduit mince décoratif, hydrofugé, teinté dans la masse, destiné à l’application manuelle sur les murs extérieurs. il est classé comme mortier de type CR CS IIl W2 selon la norme NF EN 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6700786500915616,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5272215072344187,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ceaa0295d4a43ae2",
      "score": 0.6408594060930299,
      "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, desƟné à l’applicaƟon mécanique sur les murs extérieurs. Il est classé comme morƟer de type OC CS III W2 selon la norme nf EN 998-1.",
      "document_id": "full-FULL%201-eb0d29c6",
      "file_name": "FULL%201.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
      "parent_id": "429924a0c5fccf4f",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ceaa0295d4a43ae2",
        "document_id": "full-FULL%201-eb0d29c6",
        "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
        "file_name": "FULL%201.pdf",
        "parent_id": "429924a0c5fccf4f",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, desƟné à l’applicaƟon mécanique sur les murs extérieurs. Il est classé comme morƟer de type OC CS III W2 selon la norme nf EN 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6408594060930299,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.4980022632358871,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ead4d9e0135d7215",
      "score": 0.6408594060930299,
      "text": "LIKA FULL ECO est un enduit monocouche (OC2) blanc, hydrofugé, desƟné à l’applicaƟon mécanique sur les murs extérieurs.Il est classé comme morƟer de type OC CS IΙI W1 selon la norme NF ΕΝ 998-1.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ead4d9e0135d7215",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL ECO est un enduit monocouche (OC2) blanc, hydrofugé, desƟné à l’applicaƟon mécanique sur les murs extérieurs.Il est classé comme morƟer de type OC CS IΙI W1 selon la norme NF ΕΝ 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6408594060930299,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.4980022632358871,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "7dc57d0ac05fcf22",
      "score": 0.5556392560620943,
      "text": "• ApplicaƟon mécanique / manuelle.\n• Grande variété de ﬁniƟons.\n• Enduit hydrofugé .\n• Bonne adhérence sur support.\n• Excellente maniabilité et souplesse.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": "b152122a4501e702",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "7dc57d0ac05fcf22",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": "b152122a4501e702",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• ApplicaƟon mécanique / manuelle.\n• Grande variété de ﬁniƟons.\n• Enduit hydrofugé .\n• Bonne adhérence sur support.\n• Excellente maniabilité et souplesse."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5556392560620943,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.41278211320495145,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "application",
      "est",
      "et",
      "full",
      "il",
      "lika",
      "manuelle",
      "mecanique",
      "murs",
      "ou",
      "pour",
      "prevu",
      "quels",
      "sur",
      "une"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "2701cbb89f2dfd9d",
    "7cc918e9864d26bc_1",
    "429924a0c5fccf4f",
    "b152122a4501e702"
  ]
}
```

```json
{
  "query_id": "HV2-10",
  "query": "LIKA FULL est-il prévu pour une application manuelle ou mécanique, et sur quels murs ?",
  "expected": [
    {
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "chunk_ids": [
        "1aa4f45f7ad68d38"
      ],
      "substring": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1aa4f45f7ad68d38",
      "score": 0.7666167649140381,
      "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1.",
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "parent_id": "2701cbb89f2dfd9d",
      "section_path": [
        "DESCRIPTION PRODUIT __ _"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1aa4f45f7ad68d38",
        "document_id": "full-FULL-88a1b942",
        "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
        "file_name": "FULL.pdf",
        "parent_id": "2701cbb89f2dfd9d",
        "section_path": [
          "DESCRIPTION PRODUIT __ _"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7666167649140381,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.6237596220568952,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "754a782a4dcfb25e",
      "score": 0.6700786500915616,
      "text": "DESCRIPTION PRODUIT __ oôî®Œô&à=œïËî°ï=ï7’\nLIKA FINA est un enduit mince décoratif, hydrofugé, teinté dans la masse, destiné à l’application manuelle sur les murs extérieurs. il est classé comme mortier de type CR CS IIl W2 selon la norme NF EN 998-1.",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "7cc918e9864d26bc_1",
      "section_path": [
        "LIKA FINA"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "754a782a4dcfb25e",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "7cc918e9864d26bc_1",
        "section_path": [
          "LIKA FINA"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "DESCRIPTION PRODUIT __ oôî®Œô&à=œïËî°ï=ï7’\nLIKA FINA est un enduit mince décoratif, hydrofugé, teinté dans la masse, destiné à l’application manuelle sur les murs extérieurs. il est classé comme mortier de type CR CS IIl W2 selon la norme NF EN 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6700786500915616,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5272215072344187,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ceaa0295d4a43ae2",
      "score": 0.6408594060930299,
      "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, desƟné à l’applicaƟon mécanique sur les murs extérieurs. Il est classé comme morƟer de type OC CS III W2 selon la norme nf EN 998-1.",
      "document_id": "full-FULL%201-eb0d29c6",
      "file_name": "FULL%201.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
      "parent_id": "429924a0c5fccf4f",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ceaa0295d4a43ae2",
        "document_id": "full-FULL%201-eb0d29c6",
        "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
        "file_name": "FULL%201.pdf",
        "parent_id": "429924a0c5fccf4f",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, desƟné à l’applicaƟon mécanique sur les murs extérieurs. Il est classé comme morƟer de type OC CS III W2 selon la norme nf EN 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6408594060930299,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.4980022632358871,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ead4d9e0135d7215",
      "score": 0.6408594060930299,
      "text": "LIKA FULL ECO est un enduit monocouche (OC2) blanc, hydrofugé, desƟné à l’applicaƟon mécanique sur les murs extérieurs.Il est classé comme morƟer de type OC CS IΙI W1 selon la norme NF ΕΝ 998-1.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ead4d9e0135d7215",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL ECO est un enduit monocouche (OC2) blanc, hydrofugé, desƟné à l’applicaƟon mécanique sur les murs extérieurs.Il est classé comme morƟer de type OC CS IΙI W1 selon la norme NF ΕΝ 998-1."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6408594060930299,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.4980022632358871,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "7dc57d0ac05fcf22",
      "score": 0.5556392560620943,
      "text": "• ApplicaƟon mécanique / manuelle.\n• Grande variété de ﬁniƟons.\n• Enduit hydrofugé .\n• Bonne adhérence sur support.\n• Excellente maniabilité et souplesse.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": "b152122a4501e702",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "7dc57d0ac05fcf22",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": "b152122a4501e702",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• ApplicaƟon mécanique / manuelle.\n• Grande variété de ﬁniƟons.\n• Enduit hydrofugé .\n• Bonne adhérence sur support.\n• Excellente maniabilité et souplesse."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5556392560620943,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.41278211320495145,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "application",
      "est",
      "et",
      "full",
      "il",
      "lika",
      "manuelle",
      "mecanique",
      "murs",
      "ou",
      "pour",
      "prevu",
      "quels",
      "sur",
      "une"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "2701cbb89f2dfd9d",
    "7cc918e9864d26bc_1",
    "429924a0c5fccf4f",
    "b152122a4501e702"
  ]
}
```

```json
{
  "query_id": "HV2-10",
  "query": "LIKA FULL est-il prévu pour une application manuelle ou mécanique, et sur quels murs ?",
  "expected": [
    {
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "chunk_ids": [
        "1aa4f45f7ad68d38"
      ],
      "substring": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1aa4f45f7ad68d38",
      "score": 0.7666167649140381,
      "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1.",
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "parent_id": "2701cbb89f2dfd9d",
      "section_path": [
        "DESCRIPTION PRODUIT __ _"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1aa4f45f7ad68d38",
        "document_id": "full-FULL-88a1b942",
        "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
        "file_name": "FULL.pdf",
        "parent_id": "2701cbb89f2dfd9d",
        "section_path": [
          "DESCRIPTION PRODUIT __ _"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, destiné à l’application mécanique sur les murs extérieurs. Il est classé comme mortier de type OC CS IIl W2 selon la norme nf EN 998-1."
      },
      "dense_score": 0.78694916,
      "dense_rank": 3,
      "lexical_score": 0.7666167649140381,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.6237596220568952,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "754a782a4dcfb25e",
      "score": 0.6700786500915616,
      "text": "DESCRIPTION PRODUIT __ oôî®Œô&à=œïËî°ï=ï7’\nLIKA FINA est un enduit mince décoratif, hydrofugé, teinté dans la masse, destiné à l’application manuelle sur les murs extérieurs. il est classé comme mortier de type CR CS IIl W2 selon la norme NF EN 998-1.",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "7cc918e9864d26bc_1",
      "section_path": [
        "LIKA FINA"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "754a782a4dcfb25e",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "7cc918e9864d26bc_1",
        "section_path": [
          "LIKA FINA"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "DESCRIPTION PRODUIT __ oôî®Œô&à=œïËî°ï=ï7’\nLIKA FINA est un enduit mince décoratif, hydrofugé, teinté dans la masse, destiné à l’application manuelle sur les murs extérieurs. il est classé comme mortier de type CR CS IIl W2 selon la norme NF EN 998-1."
      },
      "dense_score": 0.7094101,
      "dense_rank": 19,
      "lexical_score": 0.6700786500915616,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5272215072344187,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ceaa0295d4a43ae2",
      "score": 0.6408594060930299,
      "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, desƟné à l’applicaƟon mécanique sur les murs extérieurs. Il est classé comme morƟer de type OC CS III W2 selon la norme nf EN 998-1.",
      "document_id": "full-FULL%201-eb0d29c6",
      "file_name": "FULL%201.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
      "parent_id": "429924a0c5fccf4f",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ceaa0295d4a43ae2",
        "document_id": "full-FULL%201-eb0d29c6",
        "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
        "file_name": "FULL%201.pdf",
        "parent_id": "429924a0c5fccf4f",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL est un enduit monocouche (OC2), hydrofugé, teinté dans la masse, desƟné à l’applicaƟon mécanique sur les murs extérieurs. Il est classé comme morƟer de type OC CS III W2 selon la norme nf EN 998-1."
      },
      "dense_score": 0.770464,
      "dense_rank": 4,
      "lexical_score": 0.6408594060930299,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.4980022632358871,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ead4d9e0135d7215",
      "score": 0.6408594060930299,
      "text": "LIKA FULL ECO est un enduit monocouche (OC2) blanc, hydrofugé, desƟné à l’applicaƟon mécanique sur les murs extérieurs.Il est classé comme morƟer de type OC CS IΙI W1 selon la norme NF ΕΝ 998-1.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ead4d9e0135d7215",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "LIKA FULL ECO est un enduit monocouche (OC2) blanc, hydrofugé, desƟné à l’applicaƟon mécanique sur les murs extérieurs.Il est classé comme morƟer de type OC CS IΙI W1 selon la norme NF ΕΝ 998-1."
      },
      "dense_score": 0.73141176,
      "dense_rank": 9,
      "lexical_score": 0.6408594060930299,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.4980022632358871,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "7dc57d0ac05fcf22",
      "score": 0.5556392560620943,
      "text": "• ApplicaƟon mécanique / manuelle.\n• Grande variété de ﬁniƟons.\n• Enduit hydrofugé .\n• Bonne adhérence sur support.\n• Excellente maniabilité et souplesse.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": "b152122a4501e702",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "7dc57d0ac05fcf22",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": "b152122a4501e702",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• ApplicaƟon mécanique / manuelle.\n• Grande variété de ﬁniƟons.\n• Enduit hydrofugé .\n• Bonne adhérence sur support.\n• Excellente maniabilité et souplesse."
      },
      "dense_score": 0.6752937,
      "dense_rank": 79,
      "lexical_score": 0.5556392560620943,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.41278211320495145,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "application",
      "est",
      "et",
      "full",
      "il",
      "lika",
      "manuelle",
      "mecanique",
      "murs",
      "ou",
      "pour",
      "prevu",
      "quels",
      "sur",
      "une"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "2701cbb89f2dfd9d",
    "7cc918e9864d26bc_1",
    "429924a0c5fccf4f",
    "b152122a4501e702"
  ]
}
```

```json
{
  "query_id": "HV2-11",
  "query": "HYDRO FAÇADE laisse-t-il des taches blanches et modifie-t-il la perméabilité à la vapeur ?",
  "expected": [
    {
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "chunk_ids": [
        "1cdfe98fdc496aa3"
      ],
      "substring": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "e902281385b8b3b8",
      "score": 0.84100413,
      "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux.",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "e902281385b8b3b8",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux."
      }
    },
    {
      "chunk_id": "d549a5580da8c35f",
      "score": 0.8164073,
      "text": "• HYDRO-FAçADE oﬀre une protecƟon longue durée et montre une très bonne pénétraƟon dans les diﬀérents matériaux de construcƟon tels que les enduits monocouche, enduits de ﬁniƟon extérieure, bétons, peintures, briques et pierres naturelles ou reconsƟtuées….",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "1c8222059c1aecbf",
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "d549a5580da8c35f",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "1c8222059c1aecbf",
        "section_path": [
          "HYDRO-FAÇADE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• HYDRO-FAçADE oﬀre une protecƟon longue durée et montre une très bonne pénétraƟon dans les diﬀérents matériaux de construcƟon tels que les enduits monocouche, enduits de ﬁniƟon extérieure, bétons, peintures, briques et pierres naturelles ou reconsƟtuées…."
      }
    },
    {
      "chunk_id": "29c5dc7d7a051871",
      "score": 0.78078514,
      "text": "2- Appliquer HYDRO-FAÇADE à la brosse, au rouleau, au pulvérisateur à basse pression, ou par projecƟon au pistolet « airless », en travaillant du bas vers le haut, jusqu’à saturaƟon du support en évitant les coulures .\nNB: Pour les supports très absorbants il est nécessaire d’appliquer une deuxième couche pour obtenir un résultat performant, en travaillant « frais sur frais » ou quand la surface est totalement sèche jusqu’à ce que la consommaƟon prévue soit aƩeinte (éviter les excès en surface).",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "1c8222059c1aecbf",
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "29c5dc7d7a051871",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "1c8222059c1aecbf",
        "section_path": [
          "HYDRO-FAÇADE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "2- Appliquer HYDRO-FAÇADE à la brosse, au rouleau, au pulvérisateur à basse pression, ou par projecƟon au pistolet « airless », en travaillant du bas vers le haut, jusqu’à saturaƟon du support en évitant les coulures .\nNB: Pour les supports très absorbants il est nécessaire d’appliquer une deuxième couche pour obtenir un résultat performant, en travaillant « frais sur frais » ou quand la surface est totalement sèche jusqu’à ce que la consommaƟon prévue soit aƩeinte (éviter les excès en surface)."
      }
    },
    {
      "chunk_id": "d84c18a2bbfb26d5",
      "score": 0.74992406,
      "text": "Recouvrement :\nHYDRO REP surfaçage est recouvrable après séchage complet par toutes peinture ou système (enduit+ peinture) permettant de conserver son effet respirant et maintenir les échanges gazeux.",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
      "parent_id": "e6f68dfdf81aa764",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "d84c18a2bbfb26d5",
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "parent_id": "e6f68dfdf81aa764",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Recouvrement :\nHYDRO REP surfaçage est recouvrable après séchage complet par toutes peinture ou système (enduit+ peinture) permettant de conserver son effet respirant et maintenir les échanges gazeux."
      }
    },
    {
      "chunk_id": "12d9cd77636e1105",
      "score": 0.7421713,
      "text": "© Imperméabilisation de façade.",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "306b96530fa94f9a",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "12d9cd77636e1105",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "306b96530fa94f9a",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "© Imperméabilisation de façade."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-11",
  "query": "HYDRO FAÇADE laisse-t-il des taches blanches et modifie-t-il la perméabilité à la vapeur ?",
  "expected": [
    {
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "chunk_ids": [
        "1cdfe98fdc496aa3"
      ],
      "substring": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:"
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1cdfe98fdc496aa3",
      "score": 0.9234877426947434,
      "text": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "e73f5ddbcf759c72",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1cdfe98fdc496aa3",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "e73f5ddbcf759c72",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.9234877426947434,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.8123766315836323,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4874bb4a97896530",
      "score": 0.41069216502924405,
      "text": "Indice de blancheur : > 95.\nRésistance à la compression : > 6 MPa.\nPerméabilité à l’eau liquide EN 1062-3 : | PND.\n\nPerméabilité à la vapeur d’eau : PND.\n\nAdhérence enduit/support en ISO 4624 : z> 0.8 MPa.",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
      "parent_id": "9a1513836318291a",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4874bb4a97896530",
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "parent_id": "9a1513836318291a",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Indice de blancheur : > 95.\nRésistance à la compression : > 6 MPa.\nPerméabilité à l’eau liquide EN 1062-3 : | PND.\n\nPerméabilité à la vapeur d’eau : PND.\n\nAdhérence enduit/support en ISO 4624 : z> 0.8 MPa."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.41069216502924405,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.29958105391813294,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "29c5dc7d7a051871",
      "score": 0.28977941031321486,
      "text": "2- Appliquer HYDRO-FAÇADE à la brosse, au rouleau, au pulvérisateur à basse pression, ou par projecƟon au pistolet « airless », en travaillant du bas vers le haut, jusqu’à saturaƟon du support en évitant les coulures .\nNB: Pour les supports très absorbants il est nécessaire d’appliquer une deuxième couche pour obtenir un résultat performant, en travaillant « frais sur frais » ou quand la surface est totalement sèche jusqu’à ce que la consommaƟon prévue soit aƩeinte (éviter les excès en surface).",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "1c8222059c1aecbf",
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "29c5dc7d7a051871",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "1c8222059c1aecbf",
        "section_path": [
          "HYDRO-FAÇADE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "2- Appliquer HYDRO-FAÇADE à la brosse, au rouleau, au pulvérisateur à basse pression, ou par projecƟon au pistolet « airless », en travaillant du bas vers le haut, jusqu’à saturaƟon du support en évitant les coulures .\nNB: Pour les supports très absorbants il est nécessaire d’appliquer une deuxième couche pour obtenir un résultat performant, en travaillant « frais sur frais » ou quand la surface est totalement sèche jusqu’à ce que la consommaƟon prévue soit aƩeinte (éviter les excès en surface)."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d549a5580da8c35f",
      "score": 0.28977941031321486,
      "text": "• HYDRO-FAçADE oﬀre une protecƟon longue durée et montre une très bonne pénétraƟon dans les diﬀérents matériaux de construcƟon tels que les enduits monocouche, enduits de ﬁniƟon extérieure, bétons, peintures, briques et pierres naturelles ou reconsƟtuées….",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "1c8222059c1aecbf",
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d549a5580da8c35f",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "1c8222059c1aecbf",
        "section_path": [
          "HYDRO-FAÇADE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• HYDRO-FAçADE oﬀre une protecƟon longue durée et montre une très bonne pénétraƟon dans les diﬀérents matériaux de construcƟon tels que les enduits monocouche, enduits de ﬁniƟon extérieure, bétons, peintures, briques et pierres naturelles ou reconsƟtuées…."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "e902281385b8b3b8",
      "score": 0.28977941031321486,
      "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux.",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e902281385b8b3b8",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "blanches",
      "des",
      "et",
      "facade",
      "hydro",
      "il",
      "la",
      "laisse",
      "modifie",
      "permeabilite",
      "t",
      "taches",
      "vapeur"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "e73f5ddbcf759c72",
    "9a1513836318291a",
    "1c8222059c1aecbf"
  ]
}
```

```json
{
  "query_id": "HV2-11",
  "query": "HYDRO FAÇADE laisse-t-il des taches blanches et modifie-t-il la perméabilité à la vapeur ?",
  "expected": [
    {
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "chunk_ids": [
        "1cdfe98fdc496aa3"
      ],
      "substring": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1cdfe98fdc496aa3",
      "score": 0.9234877426947434,
      "text": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "e73f5ddbcf759c72",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1cdfe98fdc496aa3",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "e73f5ddbcf759c72",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.9234877426947434,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.8123766315836323,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4874bb4a97896530",
      "score": 0.41069216502924405,
      "text": "Indice de blancheur : > 95.\nRésistance à la compression : > 6 MPa.\nPerméabilité à l’eau liquide EN 1062-3 : | PND.\n\nPerméabilité à la vapeur d’eau : PND.\n\nAdhérence enduit/support en ISO 4624 : z> 0.8 MPa.",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
      "parent_id": "9a1513836318291a",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4874bb4a97896530",
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "parent_id": "9a1513836318291a",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Indice de blancheur : > 95.\nRésistance à la compression : > 6 MPa.\nPerméabilité à l’eau liquide EN 1062-3 : | PND.\n\nPerméabilité à la vapeur d’eau : PND.\n\nAdhérence enduit/support en ISO 4624 : z> 0.8 MPa."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.41069216502924405,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.29958105391813294,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "29c5dc7d7a051871",
      "score": 0.28977941031321486,
      "text": "2- Appliquer HYDRO-FAÇADE à la brosse, au rouleau, au pulvérisateur à basse pression, ou par projecƟon au pistolet « airless », en travaillant du bas vers le haut, jusqu’à saturaƟon du support en évitant les coulures .\nNB: Pour les supports très absorbants il est nécessaire d’appliquer une deuxième couche pour obtenir un résultat performant, en travaillant « frais sur frais » ou quand la surface est totalement sèche jusqu’à ce que la consommaƟon prévue soit aƩeinte (éviter les excès en surface).",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "1c8222059c1aecbf",
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "29c5dc7d7a051871",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "1c8222059c1aecbf",
        "section_path": [
          "HYDRO-FAÇADE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "2- Appliquer HYDRO-FAÇADE à la brosse, au rouleau, au pulvérisateur à basse pression, ou par projecƟon au pistolet « airless », en travaillant du bas vers le haut, jusqu’à saturaƟon du support en évitant les coulures .\nNB: Pour les supports très absorbants il est nécessaire d’appliquer une deuxième couche pour obtenir un résultat performant, en travaillant « frais sur frais » ou quand la surface est totalement sèche jusqu’à ce que la consommaƟon prévue soit aƩeinte (éviter les excès en surface)."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d549a5580da8c35f",
      "score": 0.28977941031321486,
      "text": "• HYDRO-FAçADE oﬀre une protecƟon longue durée et montre une très bonne pénétraƟon dans les diﬀérents matériaux de construcƟon tels que les enduits monocouche, enduits de ﬁniƟon extérieure, bétons, peintures, briques et pierres naturelles ou reconsƟtuées….",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "1c8222059c1aecbf",
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d549a5580da8c35f",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "1c8222059c1aecbf",
        "section_path": [
          "HYDRO-FAÇADE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• HYDRO-FAçADE oﬀre une protecƟon longue durée et montre une très bonne pénétraƟon dans les diﬀérents matériaux de construcƟon tels que les enduits monocouche, enduits de ﬁniƟon extérieure, bétons, peintures, briques et pierres naturelles ou reconsƟtuées…."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "e902281385b8b3b8",
      "score": 0.28977941031321486,
      "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux.",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e902281385b8b3b8",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "blanches",
      "des",
      "et",
      "facade",
      "hydro",
      "il",
      "la",
      "laisse",
      "modifie",
      "permeabilite",
      "t",
      "taches",
      "vapeur"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "e73f5ddbcf759c72",
    "9a1513836318291a",
    "1c8222059c1aecbf"
  ]
}
```

```json
{
  "query_id": "HV2-11",
  "query": "HYDRO FAÇADE laisse-t-il des taches blanches et modifie-t-il la perméabilité à la vapeur ?",
  "expected": [
    {
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "chunk_ids": [
        "1cdfe98fdc496aa3"
      ],
      "substring": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:"
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "1cdfe98fdc496aa3",
      "score": 0.9234877426947434,
      "text": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "e73f5ddbcf759c72",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1cdfe98fdc496aa3",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "e73f5ddbcf759c72",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Facile à uƟliser.\n• Très forte pénétraƟon dans le support.\n• Eﬃcacité durable.\n• Ne modiﬁe pas la perméabilité à la vapeur d’eau.\n• Ne laisse pas des tâches blanches après séchage.\n• Diminue la salissure des supports.\n• Limite le risque de développement des moisissures. ComposiƟon:"
      },
      "dense_score": 0.7271886,
      "dense_rank": 7,
      "lexical_score": 0.9234877426947434,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.8123766315836323,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4874bb4a97896530",
      "score": 0.41069216502924405,
      "text": "Indice de blancheur : > 95.\nRésistance à la compression : > 6 MPa.\nPerméabilité à l’eau liquide EN 1062-3 : | PND.\n\nPerméabilité à la vapeur d’eau : PND.\n\nAdhérence enduit/support en ISO 4624 : z> 0.8 MPa.",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
      "parent_id": "9a1513836318291a",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4874bb4a97896530",
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "parent_id": "9a1513836318291a",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Indice de blancheur : > 95.\nRésistance à la compression : > 6 MPa.\nPerméabilité à l’eau liquide EN 1062-3 : | PND.\n\nPerméabilité à la vapeur d’eau : PND.\n\nAdhérence enduit/support en ISO 4624 : z> 0.8 MPa."
      },
      "dense_score": 0.70472825,
      "dense_rank": 17,
      "lexical_score": 0.41069216502924405,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.29958105391813294,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "e902281385b8b3b8",
      "score": 0.28977941031321486,
      "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux.",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e902281385b8b3b8",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "HYDRO-FAçADE est une imprégnaƟon en phase aqueuse, prête à l’emploi, desƟnée à l’hydrofugaƟon des façades et des toitures en extérieur.\nHYDRO-FAçADE forme une barrière eﬃcace contre la pénétraƟon de l’eau (pluies) et les agressions atmosphériques sans empêcher les échanges gazeux."
      },
      "dense_score": 0.84100413,
      "dense_rank": 1,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d549a5580da8c35f",
      "score": 0.28977941031321486,
      "text": "• HYDRO-FAçADE oﬀre une protecƟon longue durée et montre une très bonne pénétraƟon dans les diﬀérents matériaux de construcƟon tels que les enduits monocouche, enduits de ﬁniƟon extérieure, bétons, peintures, briques et pierres naturelles ou reconsƟtuées….",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "1c8222059c1aecbf",
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d549a5580da8c35f",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "1c8222059c1aecbf",
        "section_path": [
          "HYDRO-FAÇADE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• HYDRO-FAçADE oﬀre une protecƟon longue durée et montre une très bonne pénétraƟon dans les diﬀérents matériaux de construcƟon tels que les enduits monocouche, enduits de ﬁniƟon extérieure, bétons, peintures, briques et pierres naturelles ou reconsƟtuées…."
      },
      "dense_score": 0.8164073,
      "dense_rank": 2,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "29c5dc7d7a051871",
      "score": 0.28977941031321486,
      "text": "2- Appliquer HYDRO-FAÇADE à la brosse, au rouleau, au pulvérisateur à basse pression, ou par projecƟon au pistolet « airless », en travaillant du bas vers le haut, jusqu’à saturaƟon du support en évitant les coulures .\nNB: Pour les supports très absorbants il est nécessaire d’appliquer une deuxième couche pour obtenir un résultat performant, en travaillant « frais sur frais » ou quand la surface est totalement sèche jusqu’à ce que la consommaƟon prévue soit aƩeinte (éviter les excès en surface).",
      "document_id": "full-HYDRO%20FAçADE1-d78abedc",
      "file_name": "HYDRO%20FAçADE1.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
      "parent_id": "1c8222059c1aecbf",
      "section_path": [
        "HYDRO-FAÇADE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "29c5dc7d7a051871",
        "document_id": "full-HYDRO%20FAçADE1-d78abedc",
        "source_path": "ai_data\\raw\\sofap\\HYDRO%20FAçADE1.pdf",
        "file_name": "HYDRO%20FAçADE1.pdf",
        "parent_id": "1c8222059c1aecbf",
        "section_path": [
          "HYDRO-FAÇADE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "2- Appliquer HYDRO-FAÇADE à la brosse, au rouleau, au pulvérisateur à basse pression, ou par projecƟon au pistolet « airless », en travaillant du bas vers le haut, jusqu’à saturaƟon du support en évitant les coulures .\nNB: Pour les supports très absorbants il est nécessaire d’appliquer une deuxième couche pour obtenir un résultat performant, en travaillant « frais sur frais » ou quand la surface est totalement sèche jusqu’à ce que la consommaƟon prévue soit aƩeinte (éviter les excès en surface)."
      },
      "dense_score": 0.78078514,
      "dense_rank": 3,
      "lexical_score": 0.28977941031321486,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.17866829920210378,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "blanches",
      "des",
      "et",
      "facade",
      "hydro",
      "il",
      "la",
      "laisse",
      "modifie",
      "permeabilite",
      "t",
      "taches",
      "vapeur"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "e73f5ddbcf759c72",
    "9a1513836318291a",
    "1c8222059c1aecbf"
  ]
}
```

```json
{
  "query_id": "HV2-12",
  "query": "Quel couple maximal et combien de vitesses mécaniques offre ECIDL426981 ?",
  "expected": [
    {
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "chunk_ids": [
        "23b329e12ef306c3"
      ],
      "substring": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "23b329e12ef306c3",
      "score": 0.7874751,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "ba45fa3da2f2ba46",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "23b329e12ef306c3",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "ba45fa3da2f2ba46",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
      }
    },
    {
      "chunk_id": "78fdf841ed57d71f",
      "score": 0.7785136,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de percussion max. : 30000 cpm Couple max. : 96 Nm Mandrin métallique Jacobs\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL209686%20Technical%20Data-9f2a71e5",
      "file_name": "ECIDL209686%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL209686%20Technical%20Data.pdf",
      "parent_id": "018f520ed7c4c02d",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "78fdf841ed57d71f",
        "document_id": "full-ECIDL209686%20Technical%20Data-9f2a71e5",
        "source_path": "ai_data\\raw\\emtop\\ECIDL209686%20Technical%20Data.pdf",
        "file_name": "ECIDL209686%20Technical%20Data.pdf",
        "parent_id": "018f520ed7c4c02d",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de percussion max. : 30000 cpm Couple max. : 96 Nm Mandrin métallique Jacobs\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "33528846f6661792",
      "score": 0.77588093,
      "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "fa3406435016e038",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "33528846f6661792",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "fa3406435016e038",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "8852467a2b9cee0c",
      "score": 0.77021646,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "ca8f3846c8154b91",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "8852467a2b9cee0c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "ca8f3846c8154b91",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "417a91277e2fa7fb",
      "score": 0.76445097,
      "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "417a91277e2fa7fb",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-12",
  "query": "Quel couple maximal et combien de vitesses mécaniques offre ECIDL426981 ?",
  "expected": [
    {
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "chunk_ids": [
        "23b329e12ef306c3"
      ],
      "substring": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "23b329e12ef306c3",
      "score": 1.8063547219770644,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "ba45fa3da2f2ba46",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "23b329e12ef306c3",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "ba45fa3da2f2ba46",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.8063547219770644,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6396880553103976,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "d69ffa61d59c5921",
      "score": 1.8063547219770644,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu'à 69NM\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 vitesses, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Livré avec une boîte d'accessoires de 47 pièces + 3 forets à béton, pour divers scénarios d'utilisation\n6. Emballage en boîte moulée par injection, facile à transporter Moteur sans balais Tension : 42V",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d69ffa61d59c5921",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu'à 69NM\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 vitesses, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Livré avec une boîte d'accessoires de 47 pièces + 3 forets à béton, pour divers scénarios d'utilisation\n6. Emballage en boîte moulée par injection, facile à transporter Moteur sans balais Tension : 42V"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.8063547219770644,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6396880553103976,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "2d1d425b9fec8aa6",
      "score": 1.3423035432509514,
      "text": "Fonction de verrouillage de la broche Éclairage de travail LED intégré Comprend :",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d1d425b9fec8aa6",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Fonction de verrouillage de la broche Éclairage de travail LED intégré Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4bb4ffd63a2108c7",
      "score": 1.3423035432509514,
      "text": "Perçage, vissage, perçage de béton",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4bb4ffd63a2108c7",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Perçage, vissage, perçage de béton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "62618a9c6b877cb4",
      "score": 1.3423035432509514,
      "text": "47 accessoires\n3 forets pour maçonnerie (4 mm, 5 mm, 6 mm)\n2 embouts de tournevis à percussion de 150 mm (PH2)\n1 pack batterie 2,0 Ah (EBPK42201)",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "62618a9c6b877cb4",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "47 accessoires\n3 forets pour maçonnerie (4 mm, 5 mm, 6 mm)\n2 embouts de tournevis à percussion de 150 mm (PH2)\n1 pack batterie 2,0 Ah (EBPK42201)"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL426981"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "ECIDL426981%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "combien",
      "couple",
      "de",
      "ecidl426981",
      "et",
      "maximal",
      "mecaniques",
      "offre",
      "quel",
      "vitesses"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "ba45fa3da2f2ba46",
    "52665d8774fd0132"
  ]
}
```

```json
{
  "query_id": "HV2-12",
  "query": "Quel couple maximal et combien de vitesses mécaniques offre ECIDL426981 ?",
  "expected": [
    {
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "chunk_ids": [
        "23b329e12ef306c3"
      ],
      "substring": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "23b329e12ef306c3",
      "score": 1.8063547219770644,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "ba45fa3da2f2ba46",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "23b329e12ef306c3",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "ba45fa3da2f2ba46",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.8063547219770644,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6396880553103976,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "d69ffa61d59c5921",
      "score": 1.8063547219770644,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu'à 69NM\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 vitesses, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Livré avec une boîte d'accessoires de 47 pièces + 3 forets à béton, pour divers scénarios d'utilisation\n6. Emballage en boîte moulée par injection, facile à transporter Moteur sans balais Tension : 42V",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d69ffa61d59c5921",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu'à 69NM\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 vitesses, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Livré avec une boîte d'accessoires de 47 pièces + 3 forets à béton, pour divers scénarios d'utilisation\n6. Emballage en boîte moulée par injection, facile à transporter Moteur sans balais Tension : 42V"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.8063547219770644,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6396880553103976,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "2d1d425b9fec8aa6",
      "score": 1.3423035432509514,
      "text": "Fonction de verrouillage de la broche Éclairage de travail LED intégré Comprend :",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d1d425b9fec8aa6",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Fonction de verrouillage de la broche Éclairage de travail LED intégré Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "4bb4ffd63a2108c7",
      "score": 1.3423035432509514,
      "text": "Perçage, vissage, perçage de béton",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4bb4ffd63a2108c7",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Perçage, vissage, perçage de béton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "62618a9c6b877cb4",
      "score": 1.3423035432509514,
      "text": "47 accessoires\n3 forets pour maçonnerie (4 mm, 5 mm, 6 mm)\n2 embouts de tournevis à percussion de 150 mm (PH2)\n1 pack batterie 2,0 Ah (EBPK42201)",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "62618a9c6b877cb4",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "47 accessoires\n3 forets pour maçonnerie (4 mm, 5 mm, 6 mm)\n2 embouts de tournevis à percussion de 150 mm (PH2)\n1 pack batterie 2,0 Ah (EBPK42201)"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL426981"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "ECIDL426981%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "combien",
      "couple",
      "de",
      "ecidl426981",
      "et",
      "maximal",
      "mecaniques",
      "offre",
      "quel",
      "vitesses"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "ba45fa3da2f2ba46",
    "52665d8774fd0132"
  ]
}
```

```json
{
  "query_id": "HV2-12",
  "query": "Quel couple maximal et combien de vitesses mécaniques offre ECIDL426981 ?",
  "expected": [
    {
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "chunk_ids": [
        "23b329e12ef306c3"
      ],
      "substring": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "23b329e12ef306c3",
      "score": 1.8063547219770644,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "ba45fa3da2f2ba46",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "23b329e12ef306c3",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "ba45fa3da2f2ba46",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
      },
      "dense_score": 0.7874751,
      "dense_rank": 1,
      "lexical_score": 1.8063547219770644,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6396880553103976,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "d69ffa61d59c5921",
      "score": 1.8063547219770644,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu'à 69NM\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 vitesses, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Livré avec une boîte d'accessoires de 47 pièces + 3 forets à béton, pour divers scénarios d'utilisation\n6. Emballage en boîte moulée par injection, facile à transporter Moteur sans balais Tension : 42V",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "d69ffa61d59c5921",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu'à 69NM\n2. Mandrin tout métal de 13 mm, avec verrouillage, maintien plus stable\n3. Réglage à 22+1+1 vitesses, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Livré avec une boîte d'accessoires de 47 pièces + 3 forets à béton, pour divers scénarios d'utilisation\n6. Emballage en boîte moulée par injection, facile à transporter Moteur sans balais Tension : 42V"
      },
      "dense_score": 0.6795528,
      "dense_rank": 11,
      "lexical_score": 1.8063547219770644,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.6396880553103976,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "62618a9c6b877cb4",
      "score": 1.3423035432509514,
      "text": "47 accessoires\n3 forets pour maçonnerie (4 mm, 5 mm, 6 mm)\n2 embouts de tournevis à percussion de 150 mm (PH2)\n1 pack batterie 2,0 Ah (EBPK42201)",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "62618a9c6b877cb4",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "47 accessoires\n3 forets pour maçonnerie (4 mm, 5 mm, 6 mm)\n2 embouts de tournevis à percussion de 150 mm (PH2)\n1 pack batterie 2,0 Ah (EBPK42201)"
      },
      "dense_score": 0.62829906,
      "dense_rank": 94,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "2d1d425b9fec8aa6",
      "score": 1.3423035432509514,
      "text": "Fonction de verrouillage de la broche Éclairage de travail LED intégré Comprend :",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d1d425b9fec8aa6",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Fonction de verrouillage de la broche Éclairage de travail LED intégré Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "4bb4ffd63a2108c7",
      "score": 1.3423035432509514,
      "text": "Perçage, vissage, perçage de béton",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "52665d8774fd0132",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4bb4ffd63a2108c7",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "52665d8774fd0132",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Perçage, vissage, perçage de béton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3423035432509514,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17563687658428456,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL426981"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "ECIDL426981%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "combien",
      "couple",
      "de",
      "ecidl426981",
      "et",
      "maximal",
      "mecaniques",
      "offre",
      "quel",
      "vitesses"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "ba45fa3da2f2ba46",
    "52665d8774fd0132"
  ]
}
```

```json
{
  "query_id": "HV2-13",
  "query": "Quels dispositifs du touret EBGR61501 protègent les yeux et empêchent la poussière d’entrer ?",
  "expected": [
    {
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "chunk_ids": [
        "2d13aad6e3293d4f"
      ],
      "substring": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "224983fcd9991c9b",
      "score": 0.67805386,
      "text": "Traﬁc d’engins légers :",
      "document_id": "full-SUPERDUR1-8aaac074",
      "file_name": "SUPERDUR1.pdf",
      "source_path": "ai_data\\raw\\sofap\\SUPERDUR1.pdf",
      "parent_id": "394c8227cec43296",
      "section_path": [
        "• EN 13813  _   DTU 26-2  _  DTU 13.3 ."
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "224983fcd9991c9b",
        "document_id": "full-SUPERDUR1-8aaac074",
        "source_path": "ai_data\\raw\\sofap\\SUPERDUR1.pdf",
        "file_name": "SUPERDUR1.pdf",
        "parent_id": "394c8227cec43296",
        "section_path": [
          "• EN 13813  _   DTU 26-2  _  DTU 13.3 ."
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Traﬁc d’engins légers :"
      }
    },
    {
      "chunk_id": "8e28b04914f62ba0",
      "score": 0.6768389,
      "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter.",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
      "parent_id": "0debe0ca3f77bd9c",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "8e28b04914f62ba0",
        "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
        "file_name": "RUSTIKA%20GRAVITA1.pdf",
        "parent_id": "0debe0ca3f77bd9c",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing...) selon DTU 26.1.\n• Maçonneries anciennes et autre supports : nous consulter."
      }
    },
    {
      "chunk_id": "f1837ea6d89afe65",
      "score": 0.6752963,
      "text": "1 paire de gants enduits de PU\n1 bouteille d’huile\n1 pierre à affûter\n1 batterie 2,0 Ah (EBPK20011)\n1 chargeur (EFCR20200)",
      "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
      "file_name": "ELSL203051%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELSL203051%20Technical%20Data.pdf",
      "parent_id": "a21376e6ffcb92b2",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "f1837ea6d89afe65",
        "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
        "source_path": "ai_data\\raw\\emtop\\ELSL203051%20Technical%20Data.pdf",
        "file_name": "ELSL203051%20Technical%20Data.pdf",
        "parent_id": "a21376e6ffcb92b2",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1 paire de gants enduits de PU\n1 bouteille d’huile\n1 pierre à affûter\n1 batterie 2,0 Ah (EBPK20011)\n1 chargeur (EFCR20200)"
      }
    },
    {
      "chunk_id": "b48abcc218bcbcea",
      "score": 0.6739015,
      "text": "Performances de l’enduit à l’état durci selon EN 998-1:\nDensité :",
      "document_id": "full-FULL-88a1b942",
      "file_name": "FULL.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
      "parent_id": "2c08a6759ef7b78b",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "b48abcc218bcbcea",
        "document_id": "full-FULL-88a1b942",
        "source_path": "ai_data\\raw\\gypsobat\\FULL.pdf",
        "file_name": "FULL.pdf",
        "parent_id": "2c08a6759ef7b78b",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Performances de l’enduit à l’état durci selon EN 998-1:\nDensité :"
      }
    },
    {
      "chunk_id": "2d50db6317b6327f",
      "score": 0.67351335,
      "text": "o Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing…) selon DTU 26.1.",
      "document_id": "full-ISBAROC-R-3a4b4eb9",
      "file_name": "ISBAROC-R.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
      "parent_id": "ca4e602fe65f328d",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "2d50db6317b6327f",
        "document_id": "full-ISBAROC-R-3a4b4eb9",
        "source_path": "ai_data\\raw\\gypsobat\\ISBAROC-R.pdf",
        "file_name": "ISBAROC-R.pdf",
        "parent_id": "ca4e602fe65f328d",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "o Classe RT2 et RT3 (béton, brique & maçonnerie de parpaing…) selon DTU 26.1."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-13",
  "query": "Quels dispositifs du touret EBGR61501 protègent les yeux et empêchent la poussière d’entrer ?",
  "expected": [
    {
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "chunk_ids": [
        "2d13aad6e3293d4f"
      ],
      "substring": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "2d13aad6e3293d4f",
      "score": 1.4622385034818306,
      "text": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d13aad6e3293d4f",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4622385034818306,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.3511273923707195,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "1fa0b150a6b65ef1",
      "score": 1.219044431371339,
      "text": "La meuleuse convient au meulage périphérique à sec des métaux - uniquement dans des locaux secs et pour un meulage occasionnel. La pièce est guidée à la main.",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1fa0b150a6b65ef1",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse convient au meulage périphérique à sec des métaux - uniquement dans des locaux secs et pour un meulage occasionnel. La pièce est guidée à la main."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "2682069955a47b80",
      "score": 1.219044431371339,
      "text": "Vitesse à vide : 2950 tr/min",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "8d263804648fe449",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2682069955a47b80",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "8d263804648fe449",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 2950 tr/min"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "fced69f8a9f85c31",
      "score": 1.219044431371339,
      "text": "Taille de la roue : 150 mm Repose-pièce réglable Socle en aluminium robuste Comprend 1 jeu de protections oculaires\nComprend 1 boîte de rangement pour outils Emballé dans un carton",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fced69f8a9f85c31",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Taille de la roue : 150 mm Repose-pièce réglable Socle en aluminium robuste Comprend 1 jeu de protections oculaires\nComprend 1 boîte de rangement pour outils Emballé dans un carton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4d20acf2ffaa3626",
      "score": 0.15855437336738676,
      "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d20acf2ffaa3626",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.15855437336738676,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.15855437336738676,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EBGR61501"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "EBGR61501%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "d",
      "dispositifs",
      "du",
      "ebgr61501",
      "empechent",
      "entrer",
      "et",
      "la",
      "les",
      "poussiere",
      "protegent",
      "quels",
      "touret",
      "yeux"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "66f7e98da274f736",
    "8d263804648fe449",
    "82c3af845f7562f6"
  ]
}
```

```json
{
  "query_id": "HV2-13",
  "query": "Quels dispositifs du touret EBGR61501 protègent les yeux et empêchent la poussière d’entrer ?",
  "expected": [
    {
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "chunk_ids": [
        "2d13aad6e3293d4f"
      ],
      "substring": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "2d13aad6e3293d4f",
      "score": 1.4622385034818306,
      "text": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d13aad6e3293d4f",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4622385034818306,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.3511273923707195,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "1fa0b150a6b65ef1",
      "score": 1.219044431371339,
      "text": "La meuleuse convient au meulage périphérique à sec des métaux - uniquement dans des locaux secs et pour un meulage occasionnel. La pièce est guidée à la main.",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1fa0b150a6b65ef1",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse convient au meulage périphérique à sec des métaux - uniquement dans des locaux secs et pour un meulage occasionnel. La pièce est guidée à la main."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "2682069955a47b80",
      "score": 1.219044431371339,
      "text": "Vitesse à vide : 2950 tr/min",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "8d263804648fe449",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2682069955a47b80",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "8d263804648fe449",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 2950 tr/min"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "fced69f8a9f85c31",
      "score": 1.219044431371339,
      "text": "Taille de la roue : 150 mm Repose-pièce réglable Socle en aluminium robuste Comprend 1 jeu de protections oculaires\nComprend 1 boîte de rangement pour outils Emballé dans un carton",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fced69f8a9f85c31",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Taille de la roue : 150 mm Repose-pièce réglable Socle en aluminium robuste Comprend 1 jeu de protections oculaires\nComprend 1 boîte de rangement pour outils Emballé dans un carton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "4d20acf2ffaa3626",
      "score": 0.15855437336738676,
      "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d20acf2ffaa3626",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.15855437336738676,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.15855437336738676,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EBGR61501"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "EBGR61501%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "d",
      "dispositifs",
      "du",
      "ebgr61501",
      "empechent",
      "entrer",
      "et",
      "la",
      "les",
      "poussiere",
      "protegent",
      "quels",
      "touret",
      "yeux"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "66f7e98da274f736",
    "8d263804648fe449",
    "82c3af845f7562f6"
  ]
}
```

```json
{
  "query_id": "HV2-13",
  "query": "Quels dispositifs du touret EBGR61501 protègent les yeux et empêchent la poussière d’entrer ?",
  "expected": [
    {
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "chunk_ids": [
        "2d13aad6e3293d4f"
      ],
      "substring": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "2d13aad6e3293d4f",
      "score": 1.4622385034818306,
      "text": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d13aad6e3293d4f",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Double lunettes de protection, pour empêcher les étincelles de jaillir dans les yeux\n2. Interrupteur anti-poussière, pour empêcher la poussière de pénétrer\n3. Support de lame coulissante, pour un meulage plus facile et moins fatigant\n4. Base épaissie, plus stable, moins sujette aux vibrations Tension : 220-240V~50Hz Puissance d’entrée : 150W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4622385034818306,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.3511273923707195,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "1fa0b150a6b65ef1",
      "score": 1.219044431371339,
      "text": "La meuleuse convient au meulage périphérique à sec des métaux - uniquement dans des locaux secs et pour un meulage occasionnel. La pièce est guidée à la main.",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "1fa0b150a6b65ef1",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse convient au meulage périphérique à sec des métaux - uniquement dans des locaux secs et pour un meulage occasionnel. La pièce est guidée à la main."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "2682069955a47b80",
      "score": 1.219044431371339,
      "text": "Vitesse à vide : 2950 tr/min",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "8d263804648fe449",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2682069955a47b80",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "8d263804648fe449",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 2950 tr/min"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "fced69f8a9f85c31",
      "score": 1.219044431371339,
      "text": "Taille de la roue : 150 mm Repose-pièce réglable Socle en aluminium robuste Comprend 1 jeu de protections oculaires\nComprend 1 boîte de rangement pour outils Emballé dans un carton",
      "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "file_name": "EBGR61501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
      "parent_id": "66f7e98da274f736",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "fced69f8a9f85c31",
        "document_id": "full-EBGR61501%20Technical%20Data-91d5fdfa",
        "source_path": "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf",
        "file_name": "EBGR61501%20Technical%20Data.pdf",
        "parent_id": "66f7e98da274f736",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Taille de la roue : 150 mm Repose-pièce réglable Socle en aluminium robuste Comprend 1 jeu de protections oculaires\nComprend 1 boîte de rangement pour outils Emballé dans un carton"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.219044431371339,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.1111111111111111,
      "numeric_match": 0.0,
      "word_match": 0.10793332026022805,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "4d20acf2ffaa3626",
      "score": 0.15855437336738676,
      "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d20acf2ffaa3626",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.15855437336738676,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.15855437336738676,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EBGR61501"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EBGR61501%20Technical%20Data-91d5fdfa",
      "EBGR61501%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EBGR61501%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "d",
      "dispositifs",
      "du",
      "ebgr61501",
      "empechent",
      "entrer",
      "et",
      "la",
      "les",
      "poussiere",
      "protegent",
      "quels",
      "touret",
      "yeux"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "66f7e98da274f736",
    "8d263804648fe449",
    "82c3af845f7562f6"
  ]
}
```

```json
{
  "query_id": "HV2-14",
  "query": "Pour quel type de structures les consommables EEWSFC08101 sont-ils destinés ?",
  "expected": [
    {
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "chunk_ids": [
        "2d2de2c8733e630e"
      ],
      "substring": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.5,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.5,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "773d8cea09acd46b",
      "score": 0.71170545,
      "text": "“Consommation : Varie selon le support (type,planeité, rugosité)\n\nç * | Un sac peut couvrir environ 5m?.\n\nTempérature d’application: comprise entre 8°C et 35°C.",
      "document_id": "full-LIKA-FINA-1-d813e596",
      "file_name": "LIKA-FINA-1.pdf",
      "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
      "parent_id": "d8521720d7390e19",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "773d8cea09acd46b",
        "document_id": "full-LIKA-FINA-1-d813e596",
        "source_path": "ai_data\\raw\\gypsobat\\LIKA-FINA-1.pdf",
        "file_name": "LIKA-FINA-1.pdf",
        "parent_id": "d8521720d7390e19",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "“Consommation : Varie selon le support (type,planeité, rugosité)\n\nç * | Un sac peut couvrir environ 5m?.\n\nTempérature d’application: comprise entre 8°C et 35°C."
      }
    },
    {
      "chunk_id": "2d2de2c8733e630e",
      "score": 0.6930989,
      "text": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "8410aed771a1103e",
      "section_path": [
        "ULMGT1652, EMGT2052, ULMGT2052,"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "2d2de2c8733e630e",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "8410aed771a1103e",
        "section_path": [
          "ULMGT1652, EMGT2052, ULMGT2052,"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
      }
    },
    {
      "chunk_id": "5a34448dc9e908e6",
      "score": 0.6914786,
      "text": "• ApplicaƟon mécanique.\n• Grande variété de ﬁniƟon.\n• Coloré dans la masse.\n• imperméabilisaƟon de façade.",
      "document_id": "full-FULL%201-eb0d29c6",
      "file_name": "FULL%201.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
      "parent_id": "429924a0c5fccf4f",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "5a34448dc9e908e6",
        "document_id": "full-FULL%201-eb0d29c6",
        "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
        "file_name": "FULL%201.pdf",
        "parent_id": "429924a0c5fccf4f",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• ApplicaƟon mécanique.\n• Grande variété de ﬁniƟon.\n• Coloré dans la masse.\n• imperméabilisaƟon de façade."
      }
    },
    {
      "chunk_id": "54de190bfdd69ad6",
      "score": 0.68842304,
      "text": "ConsommaƟon: | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi.",
      "document_id": "full-FULL%20ECO1-bfeacce9",
      "file_name": "FULL%20ECO1.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
      "parent_id": "c411d14abbdf8885",
      "section_path": [
        "• EN 998-1   -  DTU 26.1 -  DTU 20.1."
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "54de190bfdd69ad6",
        "document_id": "full-FULL%20ECO1-bfeacce9",
        "source_path": "ai_data\\raw\\sofap\\FULL%20ECO1.pdf",
        "file_name": "FULL%20ECO1.pdf",
        "parent_id": "c411d14abbdf8885",
        "section_path": [
          "• EN 998-1   -  DTU 26.1 -  DTU 20.1."
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ConsommaƟon: | Varie selon le support (type, planeité, rugosité). 1 m² nécessite environ 37.5 kg càd un sac et demi."
      }
    },
    {
      "chunk_id": "73ce9be871aa1ca6",
      "score": 0.686792,
      "text": "ConsommaƟon : | Varie selon le support (type, planeité,rugosité) Un sac peut couvrir environ 1m².",
      "document_id": "full-FULL%201-eb0d29c6",
      "file_name": "FULL%201.pdf",
      "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
      "parent_id": "9732978180b5499d",
      "section_path": [
        "LIKA FULL"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "73ce9be871aa1ca6",
        "document_id": "full-FULL%201-eb0d29c6",
        "source_path": "ai_data\\raw\\sofap\\FULL%201.pdf",
        "file_name": "FULL%201.pdf",
        "parent_id": "9732978180b5499d",
        "section_path": [
          "LIKA FULL"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ConsommaƟon : | Varie selon le support (type, planeité,rugosité) Un sac peut couvrir environ 1m²."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-14",
  "query": "Pour quel type de structures les consommables EEWSFC08101 sont-ils destinés ?",
  "expected": [
    {
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "chunk_ids": [
        "2d2de2c8733e630e"
      ],
      "substring": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "2d2de2c8733e630e",
      "score": 1.506423997889652,
      "text": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "8410aed771a1103e",
      "section_path": [
        "ULMGT1652, EMGT2052, ULMGT2052,"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d2de2c8733e630e",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "8410aed771a1103e",
        "section_path": [
          "ULMGT1652, EMGT2052, ULMGT2052,"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.506423997889652,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3397573312229854,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "303731f3b5fd1ce2",
      "score": 1.3224668242197846,
      "text": "Utilisé avec une machine à souder MIG",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "303731f3b5fd1ce2",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Utilisé avec une machine à souder MIG"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "5cadd1d9038b030c",
      "score": 1.3224668242197846,
      "text": "Numéro de modèle : E71T-GS Diamètre : 0,8 mm\nPoids : 1 kg/bobine, 20 kg/boîte carton Matériau : Acier au carbone",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "1d65255d95e05f67",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "5cadd1d9038b030c",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "1d65255d95e05f67",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Numéro de modèle : E71T-GS Diamètre : 0,8 mm\nPoids : 1 kg/bobine, 20 kg/boîte carton Matériau : Acier au carbone"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "cc86e71ab03c85da",
      "score": 1.3224668242197846,
      "text": "3. Soudage stable Fil à souder tubé",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "caption",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "cc86e71ab03c85da",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "caption",
        "text": "3. Soudage stable Fil à souder tubé"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "eb370fcc19013a8a",
      "score": 1.3224668242197846,
      "text": "1. Peu d'éclaboussures, peu de fumée\n2. Facile à enlever les scories, soudure esthétique",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "eb370fcc19013a8a",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Peu d'éclaboussures, peu de fumée\n2. Facile à enlever les scories, soudure esthétique"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EEWSFC08101"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EEWSFC08101%20Technical%20Data-56178add",
      "EEWSFC08101%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "consommables",
      "de",
      "destines",
      "eewsfc08101",
      "ils",
      "les",
      "pour",
      "quel",
      "sont",
      "structures",
      "type"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "8410aed771a1103e",
    "f0945a9734376990",
    "1d65255d95e05f67"
  ]
}
```

```json
{
  "query_id": "HV2-14",
  "query": "Pour quel type de structures les consommables EEWSFC08101 sont-ils destinés ?",
  "expected": [
    {
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "chunk_ids": [
        "2d2de2c8733e630e"
      ],
      "substring": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "2d2de2c8733e630e",
      "score": 1.506423997889652,
      "text": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "8410aed771a1103e",
      "section_path": [
        "ULMGT1652, EMGT2052, ULMGT2052,"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d2de2c8733e630e",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "8410aed771a1103e",
        "section_path": [
          "ULMGT1652, EMGT2052, ULMGT2052,"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.506423997889652,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3397573312229854,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "303731f3b5fd1ce2",
      "score": 1.3224668242197846,
      "text": "Utilisé avec une machine à souder MIG",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "303731f3b5fd1ce2",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Utilisé avec une machine à souder MIG"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "5cadd1d9038b030c",
      "score": 1.3224668242197846,
      "text": "Numéro de modèle : E71T-GS Diamètre : 0,8 mm\nPoids : 1 kg/bobine, 20 kg/boîte carton Matériau : Acier au carbone",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "1d65255d95e05f67",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "5cadd1d9038b030c",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "1d65255d95e05f67",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Numéro de modèle : E71T-GS Diamètre : 0,8 mm\nPoids : 1 kg/bobine, 20 kg/boîte carton Matériau : Acier au carbone"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "cc86e71ab03c85da",
      "score": 1.3224668242197846,
      "text": "3. Soudage stable Fil à souder tubé",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "caption",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "cc86e71ab03c85da",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "caption",
        "text": "3. Soudage stable Fil à souder tubé"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "eb370fcc19013a8a",
      "score": 1.3224668242197846,
      "text": "1. Peu d'éclaboussures, peu de fumée\n2. Facile à enlever les scories, soudure esthétique",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "eb370fcc19013a8a",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Peu d'éclaboussures, peu de fumée\n2. Facile à enlever les scories, soudure esthétique"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EEWSFC08101"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EEWSFC08101%20Technical%20Data-56178add",
      "EEWSFC08101%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "consommables",
      "de",
      "destines",
      "eewsfc08101",
      "ils",
      "les",
      "pour",
      "quel",
      "sont",
      "structures",
      "type"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "8410aed771a1103e",
    "f0945a9734376990",
    "1d65255d95e05f67"
  ]
}
```

```json
{
  "query_id": "HV2-14",
  "query": "Pour quel type de structures les consommables EEWSFC08101 sont-ils destinés ?",
  "expected": [
    {
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "chunk_ids": [
        "2d2de2c8733e630e"
      ],
      "substring": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "2d2de2c8733e630e",
      "score": 1.506423997889652,
      "text": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "8410aed771a1103e",
      "section_path": [
        "ULMGT1652, EMGT2052, ULMGT2052,"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2d2de2c8733e630e",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "8410aed771a1103e",
        "section_path": [
          "ULMGT1652, EMGT2052, ULMGT2052,"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ULFC1352 et EFC1352.\nAvantage : Moins de projections, arc stable, facile à décaper, bonne apparence du cordon.\nApplication : Soudage de structures en acier au carbone Emballé sous vide Emballé dans une boîte colorée"
      },
      "dense_score": 0.6930989,
      "dense_rank": 2,
      "lexical_score": 1.506423997889652,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.3397573312229854,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "303731f3b5fd1ce2",
      "score": 1.3224668242197846,
      "text": "Utilisé avec une machine à souder MIG",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "303731f3b5fd1ce2",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Utilisé avec une machine à souder MIG"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "5cadd1d9038b030c",
      "score": 1.3224668242197846,
      "text": "Numéro de modèle : E71T-GS Diamètre : 0,8 mm\nPoids : 1 kg/bobine, 20 kg/boîte carton Matériau : Acier au carbone",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "1d65255d95e05f67",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "5cadd1d9038b030c",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "1d65255d95e05f67",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Numéro de modèle : E71T-GS Diamètre : 0,8 mm\nPoids : 1 kg/bobine, 20 kg/boîte carton Matériau : Acier au carbone"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "cc86e71ab03c85da",
      "score": 1.3224668242197846,
      "text": "3. Soudage stable Fil à souder tubé",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "caption",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "cc86e71ab03c85da",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "caption",
        "text": "3. Soudage stable Fil à souder tubé"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "eb370fcc19013a8a",
      "score": 1.3224668242197846,
      "text": "1. Peu d'éclaboussures, peu de fumée\n2. Facile à enlever les scories, soudure esthétique",
      "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
      "file_name": "EEWSFC08101%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
      "parent_id": "f0945a9734376990",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "eb370fcc19013a8a",
        "document_id": "full-EEWSFC08101%20Technical%20Data-56178add",
        "source_path": "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf",
        "file_name": "EEWSFC08101%20Technical%20Data.pdf",
        "parent_id": "f0945a9734376990",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Peu d'éclaboussures, peu de fumée\n2. Facile à enlever les scories, soudure esthétique"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3224668242197846,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.15580015755311785,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EEWSFC08101"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EEWSFC08101%20Technical%20Data-56178add",
      "EEWSFC08101%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EEWSFC08101%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "consommables",
      "de",
      "destines",
      "eewsfc08101",
      "ils",
      "les",
      "pour",
      "quel",
      "sont",
      "structures",
      "type"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "8410aed771a1103e",
    "f0945a9734376990",
    "1d65255d95e05f67"
  ]
}
```

```json
{
  "query_id": "HV2-15",
  "query": "Dans quel état doivent être les fonds avant MURENDUIT V et quel DTU appliquer ?",
  "expected": [
    {
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "chunk_ids": [
        "38c9503e6e3dc893"
      ],
      "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 0.3333333333333333,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "a9840de53ad1d35e",
      "score": 0.781613,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20B%20V4.pdf",
      "parent_id": "b7b233a60f08174f",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "a9840de53ad1d35e",
        "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
        "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20B%20V4.pdf",
        "file_name": "HYDROMUR%20B%20V4.pdf",
        "parent_id": "b7b233a60f08174f",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      }
    },
    {
      "chunk_id": "4653fb63770174cf",
      "score": 0.781613,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20B%20V4.pdf",
      "parent_id": "72a8c2be9927eee3",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "4653fb63770174cf",
        "document_id": "full-MURENDUIT%20B%20V4-a9608640",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20B%20V4.pdf",
        "file_name": "MURENDUIT%20B%20V4.pdf",
        "parent_id": "72a8c2be9927eee3",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      }
    },
    {
      "chunk_id": "38c9503e6e3dc893",
      "score": 0.781613,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "05467506c165bee4",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "38c9503e6e3dc893",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "05467506c165bee4",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      }
    },
    {
      "chunk_id": "a01b6254f0c39417",
      "score": 0.771935,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, dépoussiérés , sains et secs.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées.",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
      "parent_id": "b1bc75eeaf0ce72e",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "a01b6254f0c39417",
        "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
        "file_name": "MURENDUIT%20R%20V4.pdf",
        "parent_id": "b1bc75eeaf0ce72e",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, dépoussiérés , sains et secs.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées."
      }
    },
    {
      "chunk_id": "f5d262f2e188978c",
      "score": 0.77165496,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées.",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20PRO%20V2.pdf",
      "parent_id": "7c549a1d8d286fbc",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "f5d262f2e188978c",
        "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
        "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20PRO%20V2.pdf",
        "file_name": "HYDROMUR%20PRO%20V2.pdf",
        "parent_id": "7c549a1d8d286fbc",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-15",
  "query": "Dans quel état doivent être les fonds avant MURENDUIT V et quel DTU appliquer ?",
  "expected": [
    {
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "chunk_ids": [
        "38c9503e6e3dc893"
      ],
      "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "38c9503e6e3dc893",
      "score": 0.9891555270389638,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "05467506c165bee4",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "38c9503e6e3dc893",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "05467506c165bee4",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.9891555270389638,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.7034412413246781,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4653fb63770174cf",
      "score": 0.7284527318970699,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20B%20V4.pdf",
      "parent_id": "72a8c2be9927eee3",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4653fb63770174cf",
        "document_id": "full-MURENDUIT%20B%20V4-a9608640",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20B%20V4.pdf",
        "file_name": "MURENDUIT%20B%20V4.pdf",
        "parent_id": "72a8c2be9927eee3",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7284527318970699,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5855955890399271,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "a01b6254f0c39417",
      "score": 0.7284527318970699,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, dépoussiérés , sains et secs.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées.",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
      "parent_id": "b1bc75eeaf0ce72e",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "a01b6254f0c39417",
        "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
        "file_name": "MURENDUIT%20R%20V4.pdf",
        "parent_id": "b1bc75eeaf0ce72e",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, dépoussiérés , sains et secs.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7284527318970699,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5855955890399271,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "24e981c191415fd0",
      "score": 0.6999044621829508,
      "text": "• Enduit ciment, Plâtre,  plaques de plâtre...\n• Anciens fonds peints  cohésifs.",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "afba9fca5b456572",
      "section_path": [
        "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "24e981c191415fd0",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "afba9fca5b456572",
        "section_path": [
          "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Enduit ciment, Plâtre,  plaques de plâtre...\n• Anciens fonds peints  cohésifs."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6999044621829508,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.41419017646866507,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "26f36b4896013062",
      "score": 0.6788203882457763,
      "text": "Performances de l’enduit à l’état durci :",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "05467506c165bee4",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "26f36b4896013062",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "05467506c165bee4",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Performances de l’enduit à l’état durci :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6788203882457763,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.3931061025314906,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "appliquer",
      "avant",
      "dans",
      "doivent",
      "dtu",
      "et",
      "etat",
      "etre",
      "fonds",
      "les",
      "murenduit",
      "quel",
      "v"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "05467506c165bee4",
    "72a8c2be9927eee3",
    "b1bc75eeaf0ce72e",
    "afba9fca5b456572"
  ]
}
```

```json
{
  "query_id": "HV2-15",
  "query": "Dans quel état doivent être les fonds avant MURENDUIT V et quel DTU appliquer ?",
  "expected": [
    {
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "chunk_ids": [
        "38c9503e6e3dc893"
      ],
      "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "38c9503e6e3dc893",
      "score": 0.9891555270389638,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "05467506c165bee4",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "38c9503e6e3dc893",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "05467506c165bee4",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.9891555270389638,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.7034412413246781,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4653fb63770174cf",
      "score": 0.7284527318970699,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20B%20V4.pdf",
      "parent_id": "72a8c2be9927eee3",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4653fb63770174cf",
        "document_id": "full-MURENDUIT%20B%20V4-a9608640",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20B%20V4.pdf",
        "file_name": "MURENDUIT%20B%20V4.pdf",
        "parent_id": "72a8c2be9927eee3",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7284527318970699,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5855955890399271,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "a01b6254f0c39417",
      "score": 0.7284527318970699,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, dépoussiérés , sains et secs.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées.",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
      "parent_id": "b1bc75eeaf0ce72e",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "a01b6254f0c39417",
        "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
        "file_name": "MURENDUIT%20R%20V4.pdf",
        "parent_id": "b1bc75eeaf0ce72e",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, dépoussiérés , sains et secs.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.7284527318970699,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5855955890399271,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "24e981c191415fd0",
      "score": 0.6999044621829508,
      "text": "• Enduit ciment, Plâtre,  plaques de plâtre...\n• Anciens fonds peints  cohésifs.",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "afba9fca5b456572",
      "section_path": [
        "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "24e981c191415fd0",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "afba9fca5b456572",
        "section_path": [
          "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Enduit ciment, Plâtre,  plaques de plâtre...\n• Anciens fonds peints  cohésifs."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6999044621829508,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.41419017646866507,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "26f36b4896013062",
      "score": 0.6788203882457763,
      "text": "Performances de l’enduit à l’état durci :",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "05467506c165bee4",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "26f36b4896013062",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "05467506c165bee4",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Performances de l’enduit à l’état durci :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6788203882457763,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.3931061025314906,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "appliquer",
      "avant",
      "dans",
      "doivent",
      "dtu",
      "et",
      "etat",
      "etre",
      "fonds",
      "les",
      "murenduit",
      "quel",
      "v"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "05467506c165bee4",
    "72a8c2be9927eee3",
    "b1bc75eeaf0ce72e",
    "afba9fca5b456572"
  ]
}
```

```json
{
  "query_id": "HV2-15",
  "query": "Dans quel état doivent être les fonds avant MURENDUIT V et quel DTU appliquer ?",
  "expected": [
    {
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "chunk_ids": [
        "38c9503e6e3dc893"
      ],
      "substring": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "38c9503e6e3dc893",
      "score": 0.9891555270389638,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "05467506c165bee4",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "38c9503e6e3dc893",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "05467506c165bee4",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      },
      "dense_score": 0.781613,
      "dense_rank": 3,
      "lexical_score": 0.9891555270389638,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.7034412413246781,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4653fb63770174cf",
      "score": 0.7284527318970699,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés.",
      "document_id": "full-MURENDUIT%20B%20V4-a9608640",
      "file_name": "MURENDUIT%20B%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20B%20V4.pdf",
      "parent_id": "72a8c2be9927eee3",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4653fb63770174cf",
        "document_id": "full-MURENDUIT%20B%20V4-a9608640",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20B%20V4.pdf",
        "file_name": "MURENDUIT%20B%20V4.pdf",
        "parent_id": "72a8c2be9927eee3",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, sains et secs, dépoussiérés."
      },
      "dense_score": 0.781613,
      "dense_rank": 2,
      "lexical_score": 0.7284527318970699,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5855955890399271,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "a01b6254f0c39417",
      "score": 0.7284527318970699,
      "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, dépoussiérés , sains et secs.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées.",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
      "parent_id": "b1bc75eeaf0ce72e",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "a01b6254f0c39417",
        "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
        "file_name": "MURENDUIT%20R%20V4.pdf",
        "parent_id": "b1bc75eeaf0ce72e",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Les supports doivent être préparés conformément aux spéciﬁcaƟons du DTU 59.1.\n• Les fonds doivent être durs, cohésifs, propres, dépoussiérés , sains et secs.\n• Les trous doivent être purgés des parƟes non adhérentes et les ﬁssures ouvertes et brossées."
      },
      "dense_score": 0.771935,
      "dense_rank": 4,
      "lexical_score": 0.7284527318970699,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5855955890399271,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "24e981c191415fd0",
      "score": 0.6999044621829508,
      "text": "• Enduit ciment, Plâtre,  plaques de plâtre...\n• Anciens fonds peints  cohésifs.",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "afba9fca5b456572",
      "section_path": [
        "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "24e981c191415fd0",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "afba9fca5b456572",
        "section_path": [
          "• EN 16-566  - NFT 36-005  - DTU 59.1 - DTU 59.4"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Enduit ciment, Plâtre,  plaques de plâtre...\n• Anciens fonds peints  cohésifs."
      },
      "dense_score": 0.71626246,
      "dense_rank": 14,
      "lexical_score": 0.6999044621829508,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.41419017646866507,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "26f36b4896013062",
      "score": 0.6788203882457763,
      "text": "Performances de l’enduit à l’état durci :",
      "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
      "file_name": "MURENDUIT%20V%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
      "parent_id": "05467506c165bee4",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "26f36b4896013062",
        "document_id": "full-MURENDUIT%20V%20V4-93ec077e",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20V%20V4.pdf",
        "file_name": "MURENDUIT%20V%20V4.pdf",
        "parent_id": "05467506c165bee4",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Performances de l’enduit à l’état durci :"
      },
      "dense_score": 0.6663517,
      "dense_rank": 100,
      "lexical_score": 0.6788203882457763,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.2857142857142857,
      "numeric_match": 0.0,
      "word_match": 0.3931061025314906,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "appliquer",
      "avant",
      "dans",
      "doivent",
      "dtu",
      "et",
      "etat",
      "etre",
      "fonds",
      "les",
      "murenduit",
      "quel",
      "v"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "05467506c165bee4",
    "72a8c2be9927eee3",
    "b1bc75eeaf0ce72e",
    "afba9fca5b456572"
  ]
}
```

```json
{
  "query_id": "HV2-16",
  "query": "FINACEM CACHET ROUGE convient-il au rebouchage intérieur et à la pose manuelle ?",
  "expected": [
    {
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "chunk_ids": [
        "3bc67ce5710b3476"
      ],
      "substring": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "3bc67ce5710b3476",
      "score": 0.7847371,
      "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs.",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "3bc67ce5710b3476",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
      }
    },
    {
      "chunk_id": "4d723f7a15ac728e",
      "score": 0.72930396,
      "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur.",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "4d723f7a15ac728e",
        "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
        "file_name": "MURENDUIT%20R%20V4.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur."
      }
    },
    {
      "chunk_id": "2b27f231945ce42e",
      "score": 0.71994364,
      "text": "AcƟon de Rebouchage :",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "aa507d42c47b8ed2",
      "section_path": [
        "HYDROMUR R"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "2b27f231945ce42e",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "aa507d42c47b8ed2",
        "section_path": [
          "HYDROMUR R"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "AcƟon de Rebouchage :"
      }
    },
    {
      "chunk_id": "5d0346d21219c877",
      "score": 0.7180886,
      "text": "• Reboucher abondamment le trou ou la ﬁssure à l’aide du",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "aa507d42c47b8ed2",
      "section_path": [
        "HYDROMUR R"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "5d0346d21219c877",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "aa507d42c47b8ed2",
        "section_path": [
          "HYDROMUR R"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Reboucher abondamment le trou ou la ﬁssure à l’aide du"
      }
    },
    {
      "chunk_id": "99cc92ba87a42ea0",
      "score": 0.71048164,
      "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "99cc92ba87a42ea0",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs."
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-16",
  "query": "FINACEM CACHET ROUGE convient-il au rebouchage intérieur et à la pose manuelle ?",
  "expected": [
    {
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "chunk_ids": [
        "3bc67ce5710b3476"
      ],
      "substring": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "3bc67ce5710b3476",
      "score": 0.892126030430718,
      "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs.",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3bc67ce5710b3476",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.892126030430718,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.642126030430718,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4d723f7a15ac728e",
      "score": 0.6684027875238562,
      "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur.",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d723f7a15ac728e",
        "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
        "file_name": "MURENDUIT%20R%20V4.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6684027875238562,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.6684027875238562,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ccebd0383f5c6de9",
      "score": 0.6249006654140581,
      "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être  nivelé, stable, propre, sans la présen- -ce de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer FINACEM CACHET ROUGE  dans environ  2.4 L d’eau pour  5  kg  de poudre,  puis  mélanger  à  la main ou à l’aide d’un malaxeur jusqu’à l’obtention  d’une  pâte  homo- -gène à la consistance souhaitée:\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\nIl  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Reboucher  abondamment  le  trou  ou  la ﬁssure à l’aide d’un couteau à enduire en croisant les passes.\n• Lorsque  l’enduit  commence  à  durcir,  couper  en croisant les passes.",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": "4c6a6737fb23f8b0",
      "section_path": [
        "FINACEM CACHET ROUGE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ccebd0383f5c6de9",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": "4c6a6737fb23f8b0",
        "section_path": [
          "FINACEM CACHET ROUGE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être  nivelé, stable, propre, sans la présen- -ce de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer FINACEM CACHET ROUGE  dans environ  2.4 L d’eau pour  5  kg  de poudre,  puis  mélanger  à  la main ou à l’aide d’un malaxeur jusqu’à l’obtention  d’une  pâte  homo- -gène à la consistance souhaitée:\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\nIl  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Reboucher  abondamment  le  trou  ou  la ﬁssure à l’aide d’un couteau à enduire en croisant les passes.\n• Lorsque  l’enduit  commence  à  durcir,  couper  en croisant les passes."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6249006654140581,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3749006654140581,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ec887325f82c4c1a",
      "score": 0.6185148376617187,
      "text": "Enduit de rebouchage / Famille III - Catégorie 3",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": "05c90ba8bc6d0d65",
      "section_path": [
        "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ec887325f82c4c1a",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": "05c90ba8bc6d0d65",
        "section_path": [
          "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Enduit de rebouchage / Famille III - Catégorie 3"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6185148376617187,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3685148376617186,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "99cc92ba87a42ea0",
      "score": 0.5092870376346841,
      "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "99cc92ba87a42ea0",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5092870376346841,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.384287037634684,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "au",
      "cachet",
      "convient",
      "et",
      "finacem",
      "il",
      "interieur",
      "la",
      "manuelle",
      "pose",
      "rebouchage",
      "rouge"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "4c6a6737fb23f8b0",
    "05c90ba8bc6d0d65",
    "0ea9ff06e37f196f"
  ]
}
```

```json
{
  "query_id": "HV2-16",
  "query": "FINACEM CACHET ROUGE convient-il au rebouchage intérieur et à la pose manuelle ?",
  "expected": [
    {
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "chunk_ids": [
        "3bc67ce5710b3476"
      ],
      "substring": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "3bc67ce5710b3476",
      "score": 0.892126030430718,
      "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs.",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3bc67ce5710b3476",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.892126030430718,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.642126030430718,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4d723f7a15ac728e",
      "score": 0.6684027875238562,
      "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur.",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d723f7a15ac728e",
        "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
        "file_name": "MURENDUIT%20R%20V4.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6684027875238562,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.6684027875238562,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ccebd0383f5c6de9",
      "score": 0.6249006654140581,
      "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être  nivelé, stable, propre, sans la présen- -ce de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer FINACEM CACHET ROUGE  dans environ  2.4 L d’eau pour  5  kg  de poudre,  puis  mélanger  à  la main ou à l’aide d’un malaxeur jusqu’à l’obtention  d’une  pâte  homo- -gène à la consistance souhaitée:\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\nIl  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Reboucher  abondamment  le  trou  ou  la ﬁssure à l’aide d’un couteau à enduire en croisant les passes.\n• Lorsque  l’enduit  commence  à  durcir,  couper  en croisant les passes.",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": "4c6a6737fb23f8b0",
      "section_path": [
        "FINACEM CACHET ROUGE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ccebd0383f5c6de9",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": "4c6a6737fb23f8b0",
        "section_path": [
          "FINACEM CACHET ROUGE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être  nivelé, stable, propre, sans la présen- -ce de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer FINACEM CACHET ROUGE  dans environ  2.4 L d’eau pour  5  kg  de poudre,  puis  mélanger  à  la main ou à l’aide d’un malaxeur jusqu’à l’obtention  d’une  pâte  homo- -gène à la consistance souhaitée:\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\nIl  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Reboucher  abondamment  le  trou  ou  la ﬁssure à l’aide d’un couteau à enduire en croisant les passes.\n• Lorsque  l’enduit  commence  à  durcir,  couper  en croisant les passes."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6249006654140581,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3749006654140581,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ec887325f82c4c1a",
      "score": 0.6185148376617187,
      "text": "Enduit de rebouchage / Famille III - Catégorie 3",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": "05c90ba8bc6d0d65",
      "section_path": [
        "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ec887325f82c4c1a",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": "05c90ba8bc6d0d65",
        "section_path": [
          "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Enduit de rebouchage / Famille III - Catégorie 3"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6185148376617187,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3685148376617186,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "99cc92ba87a42ea0",
      "score": 0.5092870376346841,
      "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "99cc92ba87a42ea0",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5092870376346841,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.384287037634684,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "au",
      "cachet",
      "convient",
      "et",
      "finacem",
      "il",
      "interieur",
      "la",
      "manuelle",
      "pose",
      "rebouchage",
      "rouge"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "4c6a6737fb23f8b0",
    "05c90ba8bc6d0d65",
    "0ea9ff06e37f196f"
  ]
}
```

```json
{
  "query_id": "HV2-16",
  "query": "FINACEM CACHET ROUGE convient-il au rebouchage intérieur et à la pose manuelle ?",
  "expected": [
    {
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "chunk_ids": [
        "3bc67ce5710b3476"
      ],
      "substring": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "3bc67ce5710b3476",
      "score": 0.892126030430718,
      "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs.",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3bc67ce5710b3476",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM  CACHET  ROUGE  est  un enduit de rebouchage et ragréage en  poudre,  en   application    manuelle   pour   des environnements intérieurs."
      },
      "dense_score": 0.7847371,
      "dense_rank": 1,
      "lexical_score": 0.892126030430718,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.642126030430718,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4d723f7a15ac728e",
      "score": 0.6684027875238562,
      "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur.",
      "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
      "file_name": "MURENDUIT%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
      "parent_id": null,
      "section_path": [],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d723f7a15ac728e",
        "document_id": "full-MURENDUIT%20R%20V4-72cd5c90",
        "source_path": "ai_data\\raw\\sofap\\MURENDUIT%20R%20V4.pdf",
        "file_name": "MURENDUIT%20R%20V4.pdf",
        "parent_id": null,
        "section_path": [],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "MURENDUIT CACHET ROUGE  est un enduit en poudre, de haute qualité, desƟné au rebouchage en applicaƟon manuelle sur les murs et plafonds  en intérieur."
      },
      "dense_score": 0.72930396,
      "dense_rank": 2,
      "lexical_score": 0.6684027875238562,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.6684027875238562,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ccebd0383f5c6de9",
      "score": 0.6249006654140581,
      "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être  nivelé, stable, propre, sans la présen- -ce de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer FINACEM CACHET ROUGE  dans environ  2.4 L d’eau pour  5  kg  de poudre,  puis  mélanger  à  la main ou à l’aide d’un malaxeur jusqu’à l’obtention  d’une  pâte  homo- -gène à la consistance souhaitée:\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\nIl  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Reboucher  abondamment  le  trou  ou  la ﬁssure à l’aide d’un couteau à enduire en croisant les passes.\n• Lorsque  l’enduit  commence  à  durcir,  couper  en croisant les passes.",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": "4c6a6737fb23f8b0",
      "section_path": [
        "FINACEM CACHET ROUGE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ccebd0383f5c6de9",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": "4c6a6737fb23f8b0",
        "section_path": [
          "FINACEM CACHET ROUGE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Niveler le support s’il y a un déséquilibre des stands.\n• Le support doit être  nivelé, stable, propre, sans la présen- -ce de peintures, vernis, graisses, etc. Préparation de l’enduit :\n• Saupoudrer FINACEM CACHET ROUGE  dans environ  2.4 L d’eau pour  5  kg  de poudre,  puis  mélanger  à  la main ou à l’aide d’un malaxeur jusqu’à l’obtention  d’une  pâte  homo- -gène à la consistance souhaitée:\n• Ajuster la consistance en fonction des travaux à réaliser.\n• Pâte fermé pour angles et rattrapages en forte épaisseur.\n• Pâte souple pour angles et les rattrapages pélliculaires.\nIl  est  recommandé  que  le  mélange  soit  laissé  au repos environ 5 minutes et mélangé à nouveau avant l’utilisation. Application :\n• Reboucher  abondamment  le  trou  ou  la ﬁssure à l’aide d’un couteau à enduire en croisant les passes.\n• Lorsque  l’enduit  commence  à  durcir,  couper  en croisant les passes."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6249006654140581,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3749006654140581,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "ec887325f82c4c1a",
      "score": 0.6185148376617187,
      "text": "Enduit de rebouchage / Famille III - Catégorie 3",
      "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
      "file_name": "FINACEM ROUGE_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
      "parent_id": "05c90ba8bc6d0d65",
      "section_path": [
        "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "ec887325f82c4c1a",
        "document_id": "full-FINACEM ROUGE_compressed-b55c6bdb",
        "source_path": "ai_data\\raw\\sofap\\FINACEM ROUGE_compressed.pdf",
        "file_name": "FINACEM ROUGE_compressed.pdf",
        "parent_id": "05c90ba8bc6d0d65",
        "section_path": [
          "LES PLUS PRODUIT\nDESCRIPTION PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Enduit de rebouchage / Famille III - Catégorie 3"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6185148376617187,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.3685148376617186,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "99cc92ba87a42ea0",
      "score": 0.5092870376346841,
      "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs.",
      "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
      "file_name": "FINACEM BLEU_compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
      "parent_id": "0ea9ff06e37f196f",
      "section_path": [
        "FINACEM CACHET BLEU"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "99cc92ba87a42ea0",
        "document_id": "full-FINACEM BLEU_compressed-9ca633ef",
        "source_path": "ai_data\\raw\\sofap\\FINACEM BLEU_compressed.pdf",
        "file_name": "FINACEM BLEU_compressed.pdf",
        "parent_id": "0ea9ff06e37f196f",
        "section_path": [
          "FINACEM CACHET BLEU"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "FINACEM CACHET BLEU  est un enduit de ﬁnition en poudre, de blancheur  élevée,  destiné  à  la  ﬁnition lisse, en applica- tion manuelle pour des environnements intérieurs."
      },
      "dense_score": 0.71048164,
      "dense_rank": 5,
      "lexical_score": 0.5092870376346841,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.384287037634684,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "a",
      "au",
      "cachet",
      "convient",
      "et",
      "finacem",
      "il",
      "interieur",
      "la",
      "manuelle",
      "pose",
      "rebouchage",
      "rouge"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "4c6a6737fb23f8b0",
    "05c90ba8bc6d0d65",
    "0ea9ff06e37f196f"
  ]
}
```

```json
{
  "query_id": "HV2-17",
  "query": "HYDROMUR R peut-il être utilisé sur une surface déjà peinte ou un support horizontal ?",
  "expected": [
    {
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "chunk_ids": [
        "3d78bc891b779755"
      ],
      "substring": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
    }
  ],
  "mode": "V1 dense-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "0edc15932b396769",
      "score": 0.77351755,
      "text": "La consommation de l’HYDRO REP surfaçage varie selon le support (type, planéité, rugosité) env.1.15 kg / m?/mm.",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
      "parent_id": "e6f68dfdf81aa764",
      "section_path": [
        "LES PLUS PRODUIT"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "0edc15932b396769",
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "parent_id": "e6f68dfdf81aa764",
        "section_path": [
          "LES PLUS PRODUIT"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La consommation de l’HYDRO REP surfaçage varie selon le support (type, planéité, rugosité) env.1.15 kg / m?/mm."
      }
    },
    {
      "chunk_id": "04e9994c5b53d24b",
      "score": 0.7688304,
      "text": "Tout arrachement de la surface ou toute remontée de laitance signiﬁe que le béton est encore trop frais et qu’il faut aƩendre.",
      "document_id": "full-SUPERDUR1-8aaac074",
      "file_name": "SUPERDUR1.pdf",
      "source_path": "ai_data\\raw\\sofap\\SUPERDUR1.pdf",
      "parent_id": "3b24d11173156a05",
      "section_path": [
        "NB :"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "04e9994c5b53d24b",
        "document_id": "full-SUPERDUR1-8aaac074",
        "source_path": "ai_data\\raw\\sofap\\SUPERDUR1.pdf",
        "file_name": "SUPERDUR1.pdf",
        "parent_id": "3b24d11173156a05",
        "section_path": [
          "NB :"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Tout arrachement de la surface ou toute remontée de laitance signiﬁe que le béton est encore trop frais et qu’il faut aƩendre."
      }
    },
    {
      "chunk_id": "32f126178b774b0b",
      "score": 0.76143074,
      "text": "• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre.",
      "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
      "file_name": "RUSTIKA%20GRAVITA1.pdf",
      "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
      "parent_id": "0debe0ca3f77bd9c",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "32f126178b774b0b",
        "document_id": "full-RUSTIKA%20GRAVITA1-2cf866dc",
        "source_path": "ai_data\\raw\\sofap\\RUSTIKA%20GRAVITA1.pdf",
        "file_name": "RUSTIKA%20GRAVITA1.pdf",
        "parent_id": "0debe0ca3f77bd9c",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Support non conforme au DTU 26.1.\n• Support horizontal.\n• Support ayant une faible résistance à l’arrachement (RT1).\n• Support métallique, peint, en plâtre."
      }
    },
    {
      "chunk_id": "2568dbcc81a0785f",
      "score": 0.75946283,
      "text": "o Appliquer l’'enduit HYDRO REP surfaçage, avec une taloche lisse, sur l’ensemble de la surface.",
      "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
      "file_name": "HYDRO REP surfaçage_Compressed.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
      "parent_id": "a92b0b977714c830",
      "section_path": [
        "MISE EN OEUVRE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "2568dbcc81a0785f",
        "document_id": "full-HYDRO REP surfaçage_Compressed-8fb9c724",
        "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfaçage_Compressed.pdf",
        "file_name": "HYDRO REP surfaçage_Compressed.pdf",
        "parent_id": "a92b0b977714c830",
        "section_path": [
          "MISE EN OEUVRE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "o Appliquer l’'enduit HYDRO REP surfaçage, avec une taloche lisse, sur l’ensemble de la surface."
      }
    },
    {
      "chunk_id": "bb36852b0f00f047",
      "score": 0.7501599,
      "text": "Durcisseur de surface",
      "document_id": "full-SUPERDUR1-8aaac074",
      "file_name": "SUPERDUR1.pdf",
      "source_path": "ai_data\\raw\\sofap\\SUPERDUR1.pdf",
      "parent_id": "354c6058134b0a1e",
      "section_path": [
        "SUPERDUR"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "bb36852b0f00f047",
        "document_id": "full-SUPERDUR1-8aaac074",
        "source_path": "ai_data\\raw\\sofap\\SUPERDUR1.pdf",
        "file_name": "SUPERDUR1.pdf",
        "parent_id": "354c6058134b0a1e",
        "section_path": [
          "SUPERDUR"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Durcisseur de surface"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-17",
  "query": "HYDROMUR R peut-il être utilisé sur une surface déjà peinte ou un support horizontal ?",
  "expected": [
    {
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "chunk_ids": [
        "3d78bc891b779755"
      ],
      "substring": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
    }
  ],
  "mode": "lexical-only",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "3d78bc891b779755",
      "score": 0.8869460946339854,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "c9da5f564f9a8786",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3d78bc891b779755",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "c9da5f564f9a8786",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.8869460946339854,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6369460946339854,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "f62dff6a25640c19",
      "score": 0.6785518643442398,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20B%20V4.pdf",
      "parent_id": "1a2fe21db07a7435",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "f62dff6a25640c19",
        "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
        "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20B%20V4.pdf",
        "file_name": "HYDROMUR%20B%20V4.pdf",
        "parent_id": "1a2fe21db07a7435",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6785518643442398,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.5535518643442398,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "3ed583a0075f3b76",
      "score": 0.6785518643442398,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20PRO%20V2.pdf",
      "parent_id": "9ac403e517ff652f",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3ed583a0075f3b76",
        "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
        "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20PRO%20V2.pdf",
        "file_name": "HYDROMUR%20PRO%20V2.pdf",
        "parent_id": "9ac403e517ff652f",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6785518643442398,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.5535518643442398,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "e1762bb703d103a7",
      "score": 0.533526998278348,
      "text": "• Appliquer l’enduit HYDROMUR R avec une taloche lisse, sur l’ensemble de la surface.\n• Travailler par zone d’environ1 m², en appliquant uniformément et en croisant les passes.",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "aa507d42c47b8ed2",
      "section_path": [
        "HYDROMUR R"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e1762bb703d103a7",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "aa507d42c47b8ed2",
        "section_path": [
          "HYDROMUR R"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Appliquer l’enduit HYDROMUR R avec une taloche lisse, sur l’ensemble de la surface.\n• Travailler par zone d’environ1 m², en appliquant uniformément et en croisant les passes."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.533526998278348,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.28352699827834804,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "02e44311c43e86b9",
      "score": 0.5156929836926543,
      "text": "PréparaƟon du Support :",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "1a1ea8248bc8cb02",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "02e44311c43e86b9",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "1a1ea8248bc8cb02",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "PréparaƟon du Support :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5156929836926543,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.2656929836926542,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "deja",
      "etre",
      "horizontal",
      "hydromur",
      "il",
      "ou",
      "peinte",
      "peut",
      "r",
      "support",
      "sur",
      "surface",
      "un",
      "une",
      "utilise"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "c9da5f564f9a8786",
    "1a2fe21db07a7435",
    "9ac403e517ff652f",
    "aa507d42c47b8ed2",
    "1a1ea8248bc8cb02"
  ]
}
```

```json
{
  "query_id": "HV2-17",
  "query": "HYDROMUR R peut-il être utilisé sur une surface déjà peinte ou un support horizontal ?",
  "expected": [
    {
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "chunk_ids": [
        "3d78bc891b779755"
      ],
      "substring": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
    }
  ],
  "mode": "identifier + lexical",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "3d78bc891b779755",
      "score": 0.8869460946339854,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "c9da5f564f9a8786",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3d78bc891b779755",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "c9da5f564f9a8786",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.8869460946339854,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6369460946339854,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "f62dff6a25640c19",
      "score": 0.6785518643442398,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20B%20V4.pdf",
      "parent_id": "1a2fe21db07a7435",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "f62dff6a25640c19",
        "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
        "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20B%20V4.pdf",
        "file_name": "HYDROMUR%20B%20V4.pdf",
        "parent_id": "1a2fe21db07a7435",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6785518643442398,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.5535518643442398,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "3ed583a0075f3b76",
      "score": 0.6785518643442398,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20PRO%20V2.pdf",
      "parent_id": "9ac403e517ff652f",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3ed583a0075f3b76",
        "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
        "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20PRO%20V2.pdf",
        "file_name": "HYDROMUR%20PRO%20V2.pdf",
        "parent_id": "9ac403e517ff652f",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.6785518643442398,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.5535518643442398,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "e1762bb703d103a7",
      "score": 0.533526998278348,
      "text": "• Appliquer l’enduit HYDROMUR R avec une taloche lisse, sur l’ensemble de la surface.\n• Travailler par zone d’environ1 m², en appliquant uniformément et en croisant les passes.",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "aa507d42c47b8ed2",
      "section_path": [
        "HYDROMUR R"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e1762bb703d103a7",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "aa507d42c47b8ed2",
        "section_path": [
          "HYDROMUR R"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Appliquer l’enduit HYDROMUR R avec une taloche lisse, sur l’ensemble de la surface.\n• Travailler par zone d’environ1 m², en appliquant uniformément et en croisant les passes."
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.533526998278348,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.28352699827834804,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "02e44311c43e86b9",
      "score": 0.5156929836926543,
      "text": "PréparaƟon du Support :",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "1a1ea8248bc8cb02",
      "section_path": [
        "DOCUMENT DE RÉFÉRENCE"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "02e44311c43e86b9",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "1a1ea8248bc8cb02",
        "section_path": [
          "DOCUMENT DE RÉFÉRENCE"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "PréparaƟon du Support :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5156929836926543,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.2656929836926542,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "deja",
      "etre",
      "horizontal",
      "hydromur",
      "il",
      "ou",
      "peinte",
      "peut",
      "r",
      "support",
      "sur",
      "surface",
      "un",
      "une",
      "utilise"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "c9da5f564f9a8786",
    "1a2fe21db07a7435",
    "9ac403e517ff652f",
    "aa507d42c47b8ed2",
    "1a1ea8248bc8cb02"
  ]
}
```

```json
{
  "query_id": "HV2-17",
  "query": "HYDROMUR R peut-il être utilisé sur une surface déjà peinte ou un support horizontal ?",
  "expected": [
    {
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "chunk_ids": [
        "3d78bc891b779755"
      ],
      "substring": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
    }
  ],
  "mode": "full V2",
  "identifier": false,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "3d78bc891b779755",
      "score": 0.8869460946339854,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "c9da5f564f9a8786",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3d78bc891b779755",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "c9da5f564f9a8786",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": 0.7373291,
      "dense_rank": 14,
      "lexical_score": 0.8869460946339854,
      "lexical_rank": 1,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.6369460946339854,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "f62dff6a25640c19",
      "score": 0.6785518643442398,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
      "file_name": "HYDROMUR%20B%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20B%20V4.pdf",
      "parent_id": "1a2fe21db07a7435",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "f62dff6a25640c19",
        "document_id": "full-HYDROMUR%20B%20V4-ebcd1c8c",
        "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20B%20V4.pdf",
        "file_name": "HYDROMUR%20B%20V4.pdf",
        "parent_id": "1a2fe21db07a7435",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": 0.7373291,
      "dense_rank": 12,
      "lexical_score": 0.6785518643442398,
      "lexical_rank": 2,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.5535518643442398,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "3ed583a0075f3b76",
      "score": 0.6785518643442398,
      "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte.",
      "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
      "file_name": "HYDROMUR%20PRO%20V2.pdf",
      "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20PRO%20V2.pdf",
      "parent_id": "9ac403e517ff652f",
      "section_path": [
        "DOMAINE D’EMPLOI"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "3ed583a0075f3b76",
        "document_id": "full-HYDROMUR%20PRO%20V2-3acb08a0",
        "source_path": "ai_data\\raw\\sofap\\HYDROMUR%20PRO%20V2.pdf",
        "file_name": "HYDROMUR%20PRO%20V2.pdf",
        "parent_id": "9ac403e517ff652f",
        "section_path": [
          "DOMAINE D’EMPLOI"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Supports non conformes au DTU 26.1.\n• Supports horizontaux .\n• Supports en plâtre.\n• Revêtements en plasƟque.\n• Surface déja peinte."
      },
      "dense_score": 0.7373291,
      "dense_rank": 13,
      "lexical_score": 0.6785518643442398,
      "lexical_rank": 3,
      "identifier_match": false,
      "filename_match": 0.125,
      "numeric_match": 0.0,
      "word_match": 0.5535518643442398,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "e1762bb703d103a7",
      "score": 0.533526998278348,
      "text": "• Appliquer l’enduit HYDROMUR R avec une taloche lisse, sur l’ensemble de la surface.\n• Travailler par zone d’environ1 m², en appliquant uniformément et en croisant les passes.",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "aa507d42c47b8ed2",
      "section_path": [
        "HYDROMUR R"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "e1762bb703d103a7",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "aa507d42c47b8ed2",
        "section_path": [
          "HYDROMUR R"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "• Appliquer l’enduit HYDROMUR R avec une taloche lisse, sur l’ensemble de la surface.\n• Travailler par zone d’environ1 m², en appliquant uniformément et en croisant les passes."
      },
      "dense_score": 0.7450738,
      "dense_rank": 9,
      "lexical_score": 0.533526998278348,
      "lexical_rank": 4,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.28352699827834804,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "f451b42f0ccbd5eb",
      "score": 0.5156929836926543,
      "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). Un sac peut couvrir environ 25 m².",
      "document_id": "full-hydromur%20R%20V4-240171e4",
      "file_name": "hydromur%20R%20V4.pdf",
      "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
      "parent_id": "aa507d42c47b8ed2",
      "section_path": [
        "HYDROMUR R"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "f451b42f0ccbd5eb",
        "document_id": "full-hydromur%20R%20V4-240171e4",
        "source_path": "ai_data\\raw\\sofap\\hydromur%20R%20V4.pdf",
        "file_name": "hydromur%20R%20V4.pdf",
        "parent_id": "aa507d42c47b8ed2",
        "section_path": [
          "HYDROMUR R"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "ConsommaƟon : | Varie selon le support (type, planeité, rugosité). Un sac peut couvrir environ 25 m²."
      },
      "dense_score": 0.69829416,
      "dense_rank": 97,
      "lexical_score": 0.5156929836926543,
      "lexical_rank": 10,
      "identifier_match": false,
      "filename_match": 0.25,
      "numeric_match": 0.0,
      "word_match": 0.2656929836926542,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [],
    "unknown_identifiers": [],
    "route_source": null,
    "route_status": "unrouted",
    "tokens": [
      "deja",
      "etre",
      "horizontal",
      "hydromur",
      "il",
      "ou",
      "peinte",
      "peut",
      "r",
      "support",
      "sur",
      "surface",
      "un",
      "une",
      "utilise"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "c9da5f564f9a8786",
    "1a2fe21db07a7435",
    "9ac403e517ff652f",
    "aa507d42c47b8ed2"
  ]
}
```

```json
{
  "query_id": "HV2-18",
  "query": "Quelle tension et quelle puissance maximale sont indiquées pour ELAG2120252 ?",
  "expected": [
    {
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "chunk_ids": [
        "4035aaf42a8f2aec"
      ],
      "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "7bd6cf9f6febf5fd",
      "score": 0.6985873,
      "text": "Tension : 220-240V~50/60Hz Puissance d'entrée : 1400W\nVitesse à vide : 13000 tr/min\nDiamètre de la lame : 110x20mm",
      "document_id": "full-EMCT14006%20Technical%20Data-488d023a",
      "file_name": "EMCT14006%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EMCT14006%20Technical%20Data.pdf",
      "parent_id": "8400763917a9ce59",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "7bd6cf9f6febf5fd",
        "document_id": "full-EMCT14006%20Technical%20Data-488d023a",
        "source_path": "ai_data\\raw\\emtop\\EMCT14006%20Technical%20Data.pdf",
        "file_name": "EMCT14006%20Technical%20Data.pdf",
        "parent_id": "8400763917a9ce59",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension : 220-240V~50/60Hz Puissance d'entrée : 1400W\nVitesse à vide : 13000 tr/min\nDiamètre de la lame : 110x20mm"
      }
    },
    {
      "chunk_id": "02dd0774ee118fee",
      "score": 0.6942364,
      "text": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :",
      "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
      "file_name": "ERHRP1801%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
      "parent_id": "4771ef5b1bc51aef",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "02dd0774ee118fee",
        "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
        "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
        "file_name": "ERHRP1801%20Technical%20Data.pdf",
        "parent_id": "4771ef5b1bc51aef",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :"
      }
    },
    {
      "chunk_id": "c767e3e9922ae9e7",
      "score": 0.68936694,
      "text": "Pistolet de gonflage de pneus pneumatiques Pression maximale :\n8,5 bars (120 psi) Avec connecteur de type Europe, connecteur de type\nUSA, connecteur de type Nitto et connecteur de type Italie. Emballé par carte coulissante",
      "document_id": "full-EASGT8501%20Technical%20Data-b3c1195b",
      "file_name": "EASGT8501%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EASGT8501%20Technical%20Data.pdf",
      "parent_id": "17d883d64a42755f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "c767e3e9922ae9e7",
        "document_id": "full-EASGT8501%20Technical%20Data-b3c1195b",
        "source_path": "ai_data\\raw\\emtop\\EASGT8501%20Technical%20Data.pdf",
        "file_name": "EASGT8501%20Technical%20Data.pdf",
        "parent_id": "17d883d64a42755f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Pistolet de gonflage de pneus pneumatiques Pression maximale :\n8,5 bars (120 psi) Avec connecteur de type Europe, connecteur de type\nUSA, connecteur de type Nitto et connecteur de type Italie. Emballé par carte coulissante"
      }
    },
    {
      "chunk_id": "0bca250d1cabc854",
      "score": 0.6888997,
      "text": "Facile à installer et à démarrer Tension : 20 V\nVitesse à vide : 18 000 tr/min",
      "document_id": "full-ELAB2078%20Technical%20Data-f807d4c7",
      "file_name": "ELAB2078%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAB2078%20Technical%20Data.pdf",
      "parent_id": "c2355a1218b1849f",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "0bca250d1cabc854",
        "document_id": "full-ELAB2078%20Technical%20Data-f807d4c7",
        "source_path": "ai_data\\raw\\emtop\\ELAB2078%20Technical%20Data.pdf",
        "file_name": "ELAB2078%20Technical%20Data.pdf",
        "parent_id": "c2355a1218b1849f",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Facile à installer et à démarrer Tension : 20 V\nVitesse à vide : 18 000 tr/min"
      }
    },
    {
      "chunk_id": "bcdeb2a5098c19e0",
      "score": 0.6854989,
      "text": "Tension d'entrée (V) : 1~220-240 Fréquence (Hz) : 50/60\nCourant de sortie (A) : 15-40A Épaisseur de coupe : ≤12mm\nCycle de service (%) : 40%\nTension à vide (V) : 400",
      "document_id": "full-ECUT451%20Technical%20Data-d6d7ef3d",
      "file_name": "ECUT451%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECUT451%20Technical%20Data.pdf",
      "parent_id": "cd3ca726faea4336",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "bcdeb2a5098c19e0",
        "document_id": "full-ECUT451%20Technical%20Data-d6d7ef3d",
        "source_path": "ai_data\\raw\\emtop\\ECUT451%20Technical%20Data.pdf",
        "file_name": "ECUT451%20Technical%20Data.pdf",
        "parent_id": "cd3ca726faea4336",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension d'entrée (V) : 1~220-240 Fréquence (Hz) : 50/60\nCourant de sortie (A) : 15-40A Épaisseur de coupe : ≤12mm\nCycle de service (%) : 40%\nTension à vide (V) : 400"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-18",
  "query": "Quelle tension et quelle puissance maximale sont indiquées pour ELAG2120252 ?",
  "expected": [
    {
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "chunk_ids": [
        "4035aaf42a8f2aec"
      ],
      "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "4035aaf42a8f2aec",
      "score": 2.014822869262222,
      "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4035aaf42a8f2aec",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.014822869262222,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.8148228692622217,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "9e1c3c2d68230178",
      "score": 1.6176136929549785,
      "text": "1 jeu de disques abrasifs pour coupe de métal (10 pièces)\n2 batteries 5,0Ah (EBPK20031)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "9e1c3c2d68230178",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1 jeu de disques abrasifs pour coupe de métal (10 pièces)\n2 batteries 5,0Ah (EBPK20031)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.6176136929549785,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.4176136929549786,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "6e233cdb52982292",
      "score": 1.4515091523675934,
      "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Poignée anti-vibration Comprend :",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "3add8cd9cbca9965",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "6e233cdb52982292",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "3add8cd9cbca9965",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Poignée anti-vibration Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4515091523675934,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.25150915236759336,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "c1298483d5044e4d",
      "score": 1.4515091523675934,
      "text": "Conditionné dans une mallette de transport",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "c1298483d5044e4d",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conditionné dans une mallette de transport"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4515091523675934,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.25150915236759336,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "02dd0774ee118fee",
      "score": 0.5633137168946283,
      "text": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :",
      "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
      "file_name": "ERHRP1801%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
      "parent_id": "4771ef5b1bc51aef",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "02dd0774ee118fee",
        "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
        "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
        "file_name": "ERHRP1801%20Technical%20Data.pdf",
        "parent_id": "4771ef5b1bc51aef",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5633137168946283,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.5633137168946283,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ELAG2120252"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "ELAG2120252%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "elag2120252",
      "et",
      "indiquees",
      "maximale",
      "pour",
      "puissance",
      "quelle",
      "sont",
      "tension"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "b1015182ec12b2b6",
    "3add8cd9cbca9965",
    "4771ef5b1bc51aef"
  ]
}
```

```json
{
  "query_id": "HV2-18",
  "query": "Quelle tension et quelle puissance maximale sont indiquées pour ELAG2120252 ?",
  "expected": [
    {
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "chunk_ids": [
        "4035aaf42a8f2aec"
      ],
      "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "4035aaf42a8f2aec",
      "score": 2.014822869262222,
      "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4035aaf42a8f2aec",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.014822869262222,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.8148228692622217,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "9e1c3c2d68230178",
      "score": 1.6176136929549785,
      "text": "1 jeu de disques abrasifs pour coupe de métal (10 pièces)\n2 batteries 5,0Ah (EBPK20031)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "9e1c3c2d68230178",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1 jeu de disques abrasifs pour coupe de métal (10 pièces)\n2 batteries 5,0Ah (EBPK20031)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.6176136929549785,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.4176136929549786,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "6e233cdb52982292",
      "score": 1.4515091523675934,
      "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Poignée anti-vibration Comprend :",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "3add8cd9cbca9965",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "6e233cdb52982292",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "3add8cd9cbca9965",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Poignée anti-vibration Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4515091523675934,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.25150915236759336,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "c1298483d5044e4d",
      "score": 1.4515091523675934,
      "text": "Conditionné dans une mallette de transport",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "c1298483d5044e4d",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conditionné dans une mallette de transport"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4515091523675934,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.25150915236759336,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "02dd0774ee118fee",
      "score": 0.5633137168946283,
      "text": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :",
      "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
      "file_name": "ERHRP1801%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
      "parent_id": "4771ef5b1bc51aef",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "02dd0774ee118fee",
        "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
        "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
        "file_name": "ERHRP1801%20Technical%20Data.pdf",
        "parent_id": "4771ef5b1bc51aef",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 0.5633137168946283,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.5633137168946283,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ELAG2120252"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "ELAG2120252%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "elag2120252",
      "et",
      "indiquees",
      "maximale",
      "pour",
      "puissance",
      "quelle",
      "sont",
      "tension"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "b1015182ec12b2b6",
    "3add8cd9cbca9965",
    "4771ef5b1bc51aef"
  ]
}
```

```json
{
  "query_id": "HV2-18",
  "query": "Quelle tension et quelle puissance maximale sont indiquées pour ELAG2120252 ?",
  "expected": [
    {
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "chunk_ids": [
        "4035aaf42a8f2aec"
      ],
      "substring": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "4035aaf42a8f2aec",
      "score": 2.014822869262222,
      "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4035aaf42a8f2aec",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "La meuleuse d'angle adaptée au meulage, au ponçage, aux opérations de découpe abrasive et au brossage métallique, béton, pierre et matériaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une durée de fonctionnement plus longue\nFonction de démarrage progressif et protection contre le redémarrage pour une utilisation plus sûre\nDisjoncteur de surcharge pour une longue durée de vie\nFonctionnement très fluide grâce à la séparation du moteur et de la transmission\nBoîtier de transmission robuste en aluminium\nDesign élancé avec surfaces de préhension ergonomiques et souples\nPoignée supplémentaire pouvant être fixée de manière flexible en 2 positions Moteur sans balais Tension : 20V Puissance d'entrée maximale : 1200W"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 2.014822869262222,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.8148228692622217,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "9e1c3c2d68230178",
      "score": 1.6176136929549785,
      "text": "1 jeu de disques abrasifs pour coupe de métal (10 pièces)\n2 batteries 5,0Ah (EBPK20031)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "9e1c3c2d68230178",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1 jeu de disques abrasifs pour coupe de métal (10 pièces)\n2 batteries 5,0Ah (EBPK20031)\n1 chargeur (EFCR20411) Tension de charge : 220-240V~50/60Hz"
      },
      "dense_score": 0.6545938,
      "dense_rank": 43,
      "lexical_score": 1.6176136929549785,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.4176136929549786,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "6e233cdb52982292",
      "score": 1.4515091523675934,
      "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Poignée anti-vibration Comprend :",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "3add8cd9cbca9965",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "6e233cdb52982292",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "3add8cd9cbca9965",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 3000/6000/9000 tr/min Diamètre du disque : 115mm\nFiletage de la broche : M14 Poignée anti-vibration Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4515091523675934,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.25150915236759336,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "c1298483d5044e4d",
      "score": 1.4515091523675934,
      "text": "Conditionné dans une mallette de transport",
      "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "file_name": "ELAG2120252%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
      "parent_id": "b1015182ec12b2b6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "c1298483d5044e4d",
        "document_id": "full-ELAG2120252%20Technical%20Data-8174b6c1",
        "source_path": "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf",
        "file_name": "ELAG2120252%20Technical%20Data.pdf",
        "parent_id": "b1015182ec12b2b6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Conditionné dans une mallette de transport"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4515091523675934,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.2,
      "numeric_match": 0.0,
      "word_match": 0.25150915236759336,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "02dd0774ee118fee",
      "score": 0.5633137168946283,
      "text": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :",
      "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
      "file_name": "ERHRP1801%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
      "parent_id": "4771ef5b1bc51aef",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "02dd0774ee118fee",
        "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
        "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
        "file_name": "ERHRP1801%20Technical%20Data.pdf",
        "parent_id": "4771ef5b1bc51aef",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entrée : 1 800 W Vitesse à vide : 850 tr/min Taux d'impact : 4 200 bpm Énergie d'impact : 7,0 J Capacité de perçage maximale :\nBéton : 36 mm Acier : 13 mm Bois :"
      },
      "dense_score": 0.6942364,
      "dense_rank": 2,
      "lexical_score": 0.5633137168946283,
      "lexical_rank": 5,
      "identifier_match": false,
      "filename_match": 0.0,
      "numeric_match": 0.0,
      "word_match": 0.5633137168946283,
      "candidate_sources": [
        "dense",
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ELAG2120252"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ELAG2120252%20Technical%20Data-8174b6c1",
      "ELAG2120252%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ELAG2120252%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "elag2120252",
      "et",
      "indiquees",
      "maximale",
      "pour",
      "puissance",
      "quelle",
      "sont",
      "tension"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "b1015182ec12b2b6",
    "3add8cd9cbca9965",
    "4771ef5b1bc51aef"
  ]
}
```

```json
{
  "query_id": "HV2-19",
  "query": "Quel couple maximal et quelle vitesse à vide donne la clé EATL12001 ?",
  "expected": [
    {
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "chunk_ids": [
        "417a91277e2fa7fb"
      ],
      "substring": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "417a91277e2fa7fb",
      "score": 0.79414743,
      "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "417a91277e2fa7fb",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
      }
    },
    {
      "chunk_id": "33528846f6661792",
      "score": 0.7747224,
      "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "fa3406435016e038",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "33528846f6661792",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "fa3406435016e038",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "8852467a2b9cee0c",
      "score": 0.77110016,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "ca8f3846c8154b91",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "8852467a2b9cee0c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "ca8f3846c8154b91",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "78fdf841ed57d71f",
      "score": 0.7611366,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de percussion max. : 30000 cpm Couple max. : 96 Nm Mandrin métallique Jacobs\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL209686%20Technical%20Data-9f2a71e5",
      "file_name": "ECIDL209686%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL209686%20Technical%20Data.pdf",
      "parent_id": "018f520ed7c4c02d",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "78fdf841ed57d71f",
        "document_id": "full-ECIDL209686%20Technical%20Data-9f2a71e5",
        "source_path": "ai_data\\raw\\emtop\\ECIDL209686%20Technical%20Data.pdf",
        "file_name": "ECIDL209686%20Technical%20Data.pdf",
        "parent_id": "018f520ed7c4c02d",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de percussion max. : 30000 cpm Couple max. : 96 Nm Mandrin métallique Jacobs\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "23b329e12ef306c3",
      "score": 0.7482308,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses",
      "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
      "file_name": "ECIDL426981%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
      "parent_id": "ba45fa3da2f2ba46",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "23b329e12ef306c3",
        "document_id": "full-ECIDL426981%20Technical%20Data-bcb0a8d4",
        "source_path": "ai_data\\raw\\emtop\\ECIDL426981%20Technical%20Data.pdf",
        "file_name": "ECIDL426981%20Technical%20Data.pdf",
        "parent_id": "ba45fa3da2f2ba46",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min Fréquence d'impact maximale : 30000 bpm Couple maximal : 69 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1 Engrenage mécanique à 2 vitesses"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-19",
  "query": "Quel couple maximal et quelle vitesse à vide donne la clé EATL12001 ?",
  "expected": [
    {
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "chunk_ids": [
        "417a91277e2fa7fb"
      ],
      "substring": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "417a91277e2fa7fb",
      "score": 1.6510989277201444,
      "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "417a91277e2fa7fb",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.6510989277201444,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5082417848630016,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "4d20acf2ffaa3626",
      "score": 1.5590812128722422,
      "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d20acf2ffaa3626",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5590812128722422,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.41622407001509937,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "07d625adcf5c7a36",
      "score": 1.2923936367803237,
      "text": "Taille du boulon : Entrée d'air 1/2\" (13",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "e485d4a8a18d8403",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "07d625adcf5c7a36",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "e485d4a8a18d8403",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Taille du boulon : Entrée d'air 1/2\" (13"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "211c357f45318467",
      "score": 1.2923936367803237,
      "text": "mm) (NPT) : Tuyau d'air 1/4\" (ID) : 3/8\"",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "211c357f45318467",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "mm) (NPT) : Tuyau d'air 1/4\" (ID) : 3/8\""
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "838a07b066ef066e",
      "score": 1.2923936367803237,
      "text": "Entraînement carré : 12 mm (1/2\")",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "8a7d254a4071a520",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "838a07b066ef066e",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "8a7d254a4071a520",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Entraînement carré : 12 mm (1/2\")"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EATL12001"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EATL12001%20Technical%20Data-ec00f05d",
      "EATL12001%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "cle",
      "couple",
      "donne",
      "eatl12001",
      "et",
      "la",
      "maximal",
      "quel",
      "quelle",
      "vide",
      "vitesse"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "82c3af845f7562f6",
    "e485d4a8a18d8403",
    "8a7d254a4071a520"
  ]
}
```

```json
{
  "query_id": "HV2-19",
  "query": "Quel couple maximal et quelle vitesse à vide donne la clé EATL12001 ?",
  "expected": [
    {
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "chunk_ids": [
        "417a91277e2fa7fb"
      ],
      "substring": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "417a91277e2fa7fb",
      "score": 1.6510989277201444,
      "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "417a91277e2fa7fb",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.6510989277201444,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5082417848630016,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "4d20acf2ffaa3626",
      "score": 1.5590812128722422,
      "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d20acf2ffaa3626",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5590812128722422,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.41622407001509937,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "07d625adcf5c7a36",
      "score": 1.2923936367803237,
      "text": "Taille du boulon : Entrée d'air 1/2\" (13",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "e485d4a8a18d8403",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "07d625adcf5c7a36",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "e485d4a8a18d8403",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Taille du boulon : Entrée d'air 1/2\" (13"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "211c357f45318467",
      "score": 1.2923936367803237,
      "text": "mm) (NPT) : Tuyau d'air 1/4\" (ID) : 3/8\"",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "211c357f45318467",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "mm) (NPT) : Tuyau d'air 1/4\" (ID) : 3/8\""
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "838a07b066ef066e",
      "score": 1.2923936367803237,
      "text": "Entraînement carré : 12 mm (1/2\")",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "8a7d254a4071a520",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "838a07b066ef066e",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "8a7d254a4071a520",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Entraînement carré : 12 mm (1/2\")"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EATL12001"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EATL12001%20Technical%20Data-ec00f05d",
      "EATL12001%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "cle",
      "couple",
      "donne",
      "eatl12001",
      "et",
      "la",
      "maximal",
      "quel",
      "quelle",
      "vide",
      "vitesse"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "82c3af845f7562f6",
    "e485d4a8a18d8403",
    "8a7d254a4071a520"
  ]
}
```

```json
{
  "query_id": "HV2-19",
  "query": "Quel couple maximal et quelle vitesse à vide donne la clé EATL12001 ?",
  "expected": [
    {
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "chunk_ids": [
        "417a91277e2fa7fb"
      ],
      "substring": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "417a91277e2fa7fb",
      "score": 1.6510989277201444,
      "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "417a91277e2fa7fb",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
      },
      "dense_score": 0.79414743,
      "dense_rank": 1,
      "lexical_score": 1.6510989277201444,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.5082417848630016,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "4d20acf2ffaa3626",
      "score": 1.5590812128722422,
      "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4d20acf2ffaa3626",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Couple industriel élevé, démontage et montage des boulons en toute simplicité\n2. Léger et durable, adapté aux travaux de montage et démontage dans des espaces étroits\n3. Structure professionnelle, couple plus important, durée de vie plus longue\n4. Supporte la rotation avant et arrière, réglable selon les besoins, travail plus facile\n5. Échappement direct, garantit la puissance de la clé\n6. Interrupteur à plaque de pression, facile à presser\n7. Filtre en acier, empêche les débris métalliques et les particules d'entrer dans le corps de l'outil, protège le cylindre des rayures"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.5590812128722422,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.41622407001509937,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "07d625adcf5c7a36",
      "score": 1.2923936367803237,
      "text": "Taille du boulon : Entrée d'air 1/2\" (13",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "e485d4a8a18d8403",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "07d625adcf5c7a36",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "e485d4a8a18d8403",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Taille du boulon : Entrée d'air 1/2\" (13"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "211c357f45318467",
      "score": 1.2923936367803237,
      "text": "mm) (NPT) : Tuyau d'air 1/4\" (ID) : 3/8\"",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "211c357f45318467",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "mm) (NPT) : Tuyau d'air 1/4\" (ID) : 3/8\""
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "838a07b066ef066e",
      "score": 1.2923936367803237,
      "text": "Entraînement carré : 12 mm (1/2\")",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "8a7d254a4071a520",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "838a07b066ef066e",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "8a7d254a4071a520",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Entraînement carré : 12 mm (1/2\")"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.2923936367803237,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.14285714285714285,
      "numeric_match": 0.0,
      "word_match": 0.14953649392318097,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "EATL12001"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-EATL12001%20Technical%20Data-ec00f05d",
      "EATL12001%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "a",
      "cle",
      "couple",
      "donne",
      "eatl12001",
      "et",
      "la",
      "maximal",
      "quel",
      "quelle",
      "vide",
      "vitesse"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "82c3af845f7562f6",
    "e485d4a8a18d8403",
    "8a7d254a4071a520"
  ]
}
```

```json
{
  "query_id": "HV2-20",
  "query": "Quel couple maximal et quel réglage de positions offre ECIDL208682 ?",
  "expected": [
    {
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "chunk_ids": [
        "4443ce1dbfc8797c"
      ],
      "substring": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V"
    }
  ],
  "mode": "V1 dense-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 0.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "3": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    },
    "5": {
      "hit": 0,
      "reciprocal_rank": 0,
      "document_recall": 1.0,
      "exact_evidence_recall": 0.0,
      "substring_evidence_recall": 0.0,
      "evidence_recall": 0.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "33528846f6661792",
      "score": 0.7211351,
      "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
      "file_name": "ECIDL208689%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
      "parent_id": "fa3406435016e038",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "33528846f6661792",
        "document_id": "full-ECIDL208689%20Technical%20Data-e7a6f8d9",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208689%20Technical%20Data.pdf",
        "file_name": "ECIDL208689%20Technical%20Data.pdf",
        "parent_id": "fa3406435016e038",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-550/0-2100 tr/min\nCadence de frappe max. : 31500 coups/min Couple max. : 86Nm Mandrin métallique Jacobs Capacité du mandrin : 13mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "8852467a2b9cee0c",
      "score": 0.7155632,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "ca8f3846c8154b91",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "8852467a2b9cee0c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "ca8f3846c8154b91",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      }
    },
    {
      "chunk_id": "6818d05d93fe2162",
      "score": 0.71197146,
      "text": "Couple de serrage : 460Nm Couple de desserrage : 600Nm Comprend :",
      "document_id": "full-ECIWL42461%20Technical%20Data-a7e3fb17",
      "file_name": "ECIWL42461%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIWL42461%20Technical%20Data.pdf",
      "parent_id": "9458390475cd0573",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "6818d05d93fe2162",
        "document_id": "full-ECIWL42461%20Technical%20Data-a7e3fb17",
        "source_path": "ai_data\\raw\\emtop\\ECIWL42461%20Technical%20Data.pdf",
        "file_name": "ECIWL42461%20Technical%20Data.pdf",
        "parent_id": "9458390475cd0573",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Couple de serrage : 460Nm Couple de desserrage : 600Nm Comprend :"
      }
    },
    {
      "chunk_id": "417a91277e2fa7fb",
      "score": 0.71183705,
      "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant",
      "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
      "file_name": "EATL12001%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
      "parent_id": "82c3af845f7562f6",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "417a91277e2fa7fb",
        "document_id": "full-EATL12001%20Technical%20Data-ec00f05d",
        "source_path": "ai_data\\raw\\emtop\\EATL12001%20Technical%20Data.pdf",
        "file_name": "EATL12001%20Technical%20Data.pdf",
        "parent_id": "82c3af845f7562f6",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Vitesse à vide : 160 tr/min Couple maximum : 68 N.m (50 Ft-Lb) Avec connecteur de type européen, connecteur de type USA, connecteur de type Nitto et connecteur de type Italie. Capacité d'échappement avant"
      }
    },
    {
      "chunk_id": "78fdf841ed57d71f",
      "score": 0.7117226,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de percussion max. : 30000 cpm Couple max. : 96 Nm Mandrin métallique Jacobs\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL209686%20Technical%20Data-9f2a71e5",
      "file_name": "ECIDL209686%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL209686%20Technical%20Data.pdf",
      "parent_id": "018f520ed7c4c02d",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": null,
      "parent_id_path_source": "unavailable",
      "payload_metadata": {
        "chunk_id": "78fdf841ed57d71f",
        "document_id": "full-ECIDL209686%20Technical%20Data-9f2a71e5",
        "source_path": "ai_data\\raw\\emtop\\ECIDL209686%20Technical%20Data.pdf",
        "file_name": "ECIDL209686%20Technical%20Data.pdf",
        "parent_id": "018f520ed7c4c02d",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de percussion max. : 30000 cpm Couple max. : 96 Nm Mandrin métallique Jacobs\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      }
    }
  ],
  "warnings": [],
  "query_analysis": null,
  "parent_ids": []
}
```

```json
{
  "query_id": "HV2-20",
  "query": "Quel couple maximal et quel réglage de positions offre ECIDL208682 ?",
  "expected": [
    {
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "chunk_ids": [
        "4443ce1dbfc8797c"
      ],
      "substring": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V"
    }
  ],
  "mode": "lexical-only",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "4443ce1dbfc8797c",
      "score": 1.9811268112443026,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4443ce1dbfc8797c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.9811268112443026,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.8144601445776358,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "8852467a2b9cee0c",
      "score": 1.4825816894109263,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "ca8f3846c8154b91",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8852467a2b9cee0c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "ca8f3846c8154b91",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4825816894109263,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.31591502274425953,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "2851a3187a70796d",
      "score": 1.3436173499121666,
      "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Éclairage de travail LED intégré\nIndicateur LED du niveau de batterie Comprend :",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2851a3187a70796d",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Éclairage de travail LED intégré\nIndicateur LED du niveau de batterie Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "8d8800e7f362d585",
      "score": 1.3436173499121666,
      "text": "Tension de charge : 220-240 V~50/60",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "385f6166148afb90",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8d8800e7f362d585",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "385f6166148afb90",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension de charge : 220-240 V~50/60"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    },
    {
      "chunk_id": "c07cac87dfdccd90",
      "score": 1.3436173499121666,
      "text": "2 batteries 4,0 Ah (EBPK20021)\n1 chargeur (EFCR20411)",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "c07cac87dfdccd90",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 batteries 4,0 Ah (EBPK20021)\n1 chargeur (EFCR20411)"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "lexical"
      ],
      "identifier_route": false
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL208682"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL208682%20Technical%20Data-71b4059d",
      "ECIDL208682%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "couple",
      "de",
      "ecidl208682",
      "et",
      "maximal",
      "offre",
      "positions",
      "quel",
      "reglage"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "2b0799ef8230ad5b",
    "ca8f3846c8154b91",
    "385f6166148afb90"
  ]
}
```

```json
{
  "query_id": "HV2-20",
  "query": "Quel couple maximal et quel réglage de positions offre ECIDL208682 ?",
  "expected": [
    {
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "chunk_ids": [
        "4443ce1dbfc8797c"
      ],
      "substring": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V"
    }
  ],
  "mode": "identifier + lexical",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "4443ce1dbfc8797c",
      "score": 1.9811268112443026,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4443ce1dbfc8797c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.9811268112443026,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.8144601445776358,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "8852467a2b9cee0c",
      "score": 1.4825816894109263,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "ca8f3846c8154b91",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8852467a2b9cee0c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "ca8f3846c8154b91",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.4825816894109263,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.31591502274425953,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "2851a3187a70796d",
      "score": 1.3436173499121666,
      "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Éclairage de travail LED intégré\nIndicateur LED du niveau de batterie Comprend :",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2851a3187a70796d",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Éclairage de travail LED intégré\nIndicateur LED du niveau de batterie Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "8d8800e7f362d585",
      "score": 1.3436173499121666,
      "text": "Tension de charge : 220-240 V~50/60",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "385f6166148afb90",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8d8800e7f362d585",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "385f6166148afb90",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension de charge : 220-240 V~50/60"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "c07cac87dfdccd90",
      "score": 1.3436173499121666,
      "text": "2 batteries 4,0 Ah (EBPK20021)\n1 chargeur (EFCR20411)",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "c07cac87dfdccd90",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 batteries 4,0 Ah (EBPK20021)\n1 chargeur (EFCR20411)"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL208682"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL208682%20Technical%20Data-71b4059d",
      "ECIDL208682%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "couple",
      "de",
      "ecidl208682",
      "et",
      "maximal",
      "offre",
      "positions",
      "quel",
      "reglage"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "2b0799ef8230ad5b",
    "ca8f3846c8154b91",
    "385f6166148afb90"
  ]
}
```

```json
{
  "query_id": "HV2-20",
  "query": "Quel couple maximal et quel réglage de positions offre ECIDL208682 ?",
  "expected": [
    {
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "chunk_ids": [
        "4443ce1dbfc8797c"
      ],
      "substring": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V"
    }
  ],
  "mode": "full V2",
  "identifier": true,
  "metrics": {
    "1": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "3": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    },
    "5": {
      "hit": 1,
      "reciprocal_rank": 1.0,
      "document_recall": 1.0,
      "exact_evidence_recall": 1.0,
      "substring_evidence_recall": 1.0,
      "evidence_recall": 1.0,
      "empty": 0
    }
  },
  "hits": [
    {
      "chunk_id": "4443ce1dbfc8797c",
      "score": 1.9811268112443026,
      "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "4443ce1dbfc8797c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "1. Moteur sans balais, puissance élevée, couple maximal jusqu’à 86 Nm\n2. Mandrin entièrement métallique de 13 mm, avec verrouillage, pour un serrage plus stable\n3. Réglage à 22+1+1 positions, avec percussion, adapté à différents environnements de travail\n4. Machine plus courte, plus compacte\n5. Tête de carter de boîte de vitesses entièrement en aluminium Moteur sans balais Tension : 20 V"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.9811268112443026,
      "lexical_rank": 1,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.8144601445776358,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "8852467a2b9cee0c",
      "score": 1.4825816894109263,
      "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "ca8f3846c8154b91",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8852467a2b9cee0c",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "ca8f3846c8154b91",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Vitesse à vide : 0-500/0-2000 tr/min\nCadence de frappe max. : 30000 coups/min Couple max. : 86 Nm Mandrin métallique\nCapacité du mandrin : 13 mm Réglages de couple : 22+1+1"
      },
      "dense_score": 0.7155632,
      "dense_rank": 2,
      "lexical_score": 1.4825816894109263,
      "lexical_rank": 2,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.31591502274425953,
      "candidate_sources": [
        "dense",
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "2851a3187a70796d",
      "score": 1.3436173499121666,
      "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Éclairage de travail LED intégré\nIndicateur LED du niveau de batterie Comprend :",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "paragraph",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "2851a3187a70796d",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "paragraph",
        "text": "Boîte de vitesses mécanique à 2 vitesses\nFonction de verrouillage de la broche Éclairage de travail LED intégré\nIndicateur LED du niveau de batterie Comprend :"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 3,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "8d8800e7f362d585",
      "score": 1.3436173499121666,
      "text": "Tension de charge : 220-240 V~50/60",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "385f6166148afb90",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "key_value",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "8d8800e7f362d585",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "385f6166148afb90",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "key_value",
        "text": "Tension de charge : 220-240 V~50/60"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 4,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    },
    {
      "chunk_id": "c07cac87dfdccd90",
      "score": 1.3436173499121666,
      "text": "2 batteries 4,0 Ah (EBPK20021)\n1 chargeur (EFCR20411)",
      "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
      "file_name": "ECIDL208682%20Technical%20Data.pdf",
      "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
      "parent_id": "2b0799ef8230ad5b",
      "section_path": [
        "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
      ],
      "page_start": 1,
      "page_end": 1,
      "block_type": "list_item",
      "parent_id_path": [],
      "parent_id_path_source": "verified_source_child",
      "payload_metadata": {
        "chunk_id": "c07cac87dfdccd90",
        "document_id": "full-ECIDL208682%20Technical%20Data-71b4059d",
        "source_path": "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf",
        "file_name": "ECIDL208682%20Technical%20Data.pdf",
        "parent_id": "2b0799ef8230ad5b",
        "section_path": [
          "POINTS DE VENTE\nUTILISATION\nDESCRIPTION ET\nCARACTÉRISTIQUES"
        ],
        "page_start": 1,
        "page_end": 1,
        "block_type": "list_item",
        "text": "2 batteries 4,0 Ah (EBPK20021)\n1 chargeur (EFCR20411)"
      },
      "dense_score": null,
      "dense_rank": null,
      "lexical_score": 1.3436173499121666,
      "lexical_rank": 5,
      "identifier_match": true,
      "filename_match": 0.16666666666666666,
      "numeric_match": 0.0,
      "word_match": 0.17695068324549995,
      "candidate_sources": [
        "identifier_route",
        "lexical"
      ],
      "identifier_route": true
    }
  ],
  "warnings": [],
  "query_analysis": {
    "identifiers": [
      "ECIDL208682"
    ],
    "unknown_identifiers": [],
    "route_source": [
      "full-ECIDL208682%20Technical%20Data-71b4059d",
      "ECIDL208682%20Technical%20Data.pdf",
      "ai_data\\raw\\emtop\\ECIDL208682%20Technical%20Data.pdf"
    ],
    "route_status": "unique",
    "tokens": [
      "couple",
      "de",
      "ecidl208682",
      "et",
      "maximal",
      "offre",
      "positions",
      "quel",
      "reglage"
    ],
    "snapshot_sha256": "64b1fbf8886cd2b4620b88206eeb69ca48cf41ecd7edc87cabc03dca4abed979"
  },
  "parent_ids": [
    "2b0799ef8230ad5b",
    "ca8f3846c8154b91",
    "385f6166148afb90"
  ]
}
```

## Reproduction

Run from backend: `venv\Scripts\python.exe -B scripts/evaluate_retrieval_v2.py`. No collection writes, extraction/chunking/indexing changes, RAG calls, Qwen calls or student-chat integration occur.
