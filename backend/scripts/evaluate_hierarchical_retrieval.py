"""Labeled, read-only retrieval evaluation; no generation or collection writes.

Run from backend: python -B scripts/evaluate_hierarchical_retrieval.py
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from qdrant_client import QdrantClient
from app.ai.embeddings.service import EmbeddingService
from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider
from app.ai.retrieval.hierarchical_retriever import (
    COLLECTION, HierarchicalRetriever, HierarchicalRetrievalConfig,
)

TOP_K = (1, 3, 5, 10)
THRESHOLDS = (0.0, 0.2, 0.3, 0.4, 0.5, 0.6)
MODES = ("child_only", "verified_parent")
# Frozen labels copied from actual indexed payloads, before running searches.
LABELS = [
    {
        "id": "BL01",
        "query": "Quel mortier colle convient aux grands formats sur des supports neufs et anciens ?",
        "categories": [
            "product identification",
            "vague/general"
        ],
        "evidence": [
            {
                "document_id": "full-FLEX%20V4-afe87429",
                "file_name": "FLEX%20V4.pdf",
                "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
                "chunk_ids": [
                    "6c394de6b51732a5"
                ],
                "substring": "Mor\u019fer colle am\u00e9lior\u00e9, d\u00e9formable, r\u00e9sistant au glissement, \u00e0 base de ciment avec un temps ouvert allong\u00e9 des\u019fn\u00e9 \u00e0 la pose de carreaux c\u00e9ramiques de grands formats en sols et murs int\u00e9rieurs et ext\u00e9rieurs sur supports neufs et anciens."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL02",
        "query": "Quelle est la tension de la batterie EBPK20021 et sa capacit\u00e9 ?",
        "categories": [
            "technical specifications"
        ],
        "evidence": [
            {
                "document_id": "full-EBPK20021%20Technical%20Data-e774e072",
                "file_name": "EBPK20021%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EBPK20021%20Technical%20Data.pdf",
                "chunk_ids": [
                    "438169fa5ddf1d66"
                ],
                "substring": "Des cellules Li-Ion de haute qualit\u00e9 signifient aucun effet m\u00e9moire, une faible autod\u00e9charge et une puissance \u00e9lev\u00e9e et constante\nLe niveau de charge actuel est indiqu\u00e9 par un affichage LED \u00e0 3 niveaux\nBo\u00eetier prot\u00e9g\u00e9 contre la poussi\u00e8re, la corrosion et les dommages m\u00e9caniques Tension : 20 V Batterie lithium-ion 4,0 Ah\nVoyant LED de niveau de charge de la batterie Une seule batterie compatible avec tous les outils multiples P20S\nEmball\u00e9 dans une bo\u00eete de couleur"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL03",
        "query": "\u00c0 quoi sert le multim\u00e8tre EDMR5110004 ?",
        "categories": [
            "application/use"
        ],
        "evidence": [
            {
                "document_id": "full-EDMR5110004%20Technical%20Data-0ce60f56",
                "file_name": "EDMR5110004%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EDMR5110004%20Technical%20Data.pdf",
                "chunk_ids": [
                    "7446289f7f148334"
                ],
                "substring": "Utilis\u00e9 pour les tests de circuits, le diagnostic des pannes, la mesure du courant, la d\u00e9tection de tension"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL04",
        "query": "Quelle est la consommation de HYDRO REP surfa\u00e7age par millim\u00e8tre ?",
        "categories": [
            "consumption"
        ],
        "evidence": [
            {
                "document_id": "full-HYDRO REP surfa\u00e7age_Compressed-8fb9c724",
                "file_name": "HYDRO REP surfa\u00e7age_Compressed.pdf",
                "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfa\u00e7age_Compressed.pdf",
                "chunk_ids": [
                    "0edc15932b396769"
                ],
                "substring": "La consommation de l\u2019HYDRO REP surfa\u00e7age varie selon le support (type, plan\u00e9it\u00e9, rugosit\u00e9) env.1.15 kg / m?/mm."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL05",
        "query": "Quelles sont les dimensions de la bo\u00eete \u00e0 outils EMTB1322 ?",
        "categories": [
            "dimensions",
            "highly specific"
        ],
        "evidence": [
            {
                "document_id": "full-EMTB1322%20Technical%20Data-c1a8f553",
                "file_name": "EMTB1322%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EMTB1322%20Technical%20Data.pdf",
                "chunk_ids": [
                    "05647b178a6474f2"
                ],
                "substring": "Dimensions : 345 mm * 280 mm * 110 mm Poign\u00e9e large int\u00e9gr\u00e9e pour un transport facile et stable Compartiments \u00e0 gobelets amovibles en 3 tailles diff\u00e9rentes Avec 12 gobelets amovibles"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL06",
        "query": "Quelle norme et quelle classification sont indiqu\u00e9es pour Adh\u00e9rcol P-3000 ?",
        "categories": [
            "standards/norms"
        ],
        "evidence": [
            {
                "document_id": "full-Adh\u00e9rcol P-3000_Compressed-ae52c6b9",
                "file_name": "Adh\u00e9rcol P-3000_Compressed.pdf",
                "source_path": "ai_data\\raw\\sofap\\Adh\u00e9rcol P-3000_Compressed.pdf",
                "chunk_ids": [
                    "9bd12e595fbda7a8"
                ],
                "substring": "Colle adh\u00e9sive en p\u00e2te \u00e0 base de r\u00e9sine synth\u00e9\u019fque en dispersion aqueuse et d\u2019addi\u019ffs sp\u00e9ciaux, pr\u00eat \u00e0 l\u2019emploi, \u00e0 temps ouvert allong\u00e9 et r\u00e9sistant au glissement, class\u00e9 D1TE selon EN 12004."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL07",
        "query": "SOFAPCOL FLEX convient-il aux pierres naturelles et au gr\u00e8s c\u00e9rame ?",
        "categories": [
            "substrate/support compatibility"
        ],
        "evidence": [
            {
                "document_id": "full-FLEX%20V4-afe87429",
                "file_name": "FLEX%20V4.pdf",
                "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
                "chunk_ids": [
                    "999bccf06fa6fd31"
                ],
                "substring": "\u2022 Pose de carrelages (gr\u00e9s cerame) et pierres naturelles (marbre, pierre, calcaire, granit) de toute porosit\u00e9 et de grands formats."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL08",
        "query": "Comment pr\u00e9parer un sac de 25 kg de SOFAPCOL FLEX et combien d\u2019eau ajouter ?",
        "categories": [
            "preparation/application instructions"
        ],
        "evidence": [
            {
                "document_id": "full-FLEX%20V4-afe87429",
                "file_name": "FLEX%20V4.pdf",
                "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
                "chunk_ids": [
                    "073b9b2da7ef170a"
                ],
                "substring": "\u2022 Dans un r\u00e9cipient contenant environ 7 Litres d\u2019eau propre, verser un sac de 25 kg de SOFAPCOL FLEX en malaxant jusqu\u2019\u00e0 l\u2019obten\u019fon d\u2019un m\u00e9lange homog\u00e8ne (u\u019fliser de pr\u00e9f\u00e9rence un malaxeur \u00e9lectrique).\n\u2022 Laisser reposer quelques minutes puis malaxer de nouveau avant l\u2019applica\u019fon."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL09",
        "query": "Peut-on ajouter de l\u2019eau \u00e0 PRIMER CONTACT et quelles protections porter ?",
        "categories": [
            "safety/limitations"
        ],
        "evidence": [
            {
                "document_id": "full-primer%20contact1-411ec87f",
                "file_name": "primer%20contact1.pdf",
                "source_path": "ai_data\\raw\\sofap\\primer%20contact1.pdf",
                "chunk_ids": [
                    "013da106acce8f93"
                ],
                "substring": "\u2022 Bien m\u00e9langer le contenu du seau avant usage.\n\u2022 Le produit \u00e9tant pr\u00eat \u00e0 l\u2019emploi, ne pas ajouter d\u2019eau.\n\u2022 Ne\u01a9oyer les ou\u019fls imm\u00e9diatement apr\u00e8s applica\u019fon avec de l\u2019eau.\n\u2022 Le port des protec\u019fons individuelles (gants, lune\u01a9es) est recommand\u00e9."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL10",
        "query": "Comparer la consommation de SUPLATEX en primaire \u00e0 celle de HYDRO REP surfa\u00e7age.",
        "categories": [
            "cross-document ambiguity",
            "consumption"
        ],
        "evidence": [
            {
                "document_id": "full-SUPLATEX1-c1a35954",
                "file_name": "SUPLATEX1.pdf",
                "source_path": "ai_data\\raw\\sofap\\SUPLATEX1.pdf",
                "chunk_ids": [
                    "3ffbfb4c1ebb40d8"
                ],
                "substring": "\u2022 En couche d'accrochage (gobe\u019fs, barbo\u019fne) : environ 0,120 L / m\u00b2.\n\u2022 En mor\u019fer : environ 0,600 L / m\u00b2.\n\u2022 En primaire : de 80 g \u00e0 150 g/m\u00b2 environ selon la nature du support.\n\u2022 En produit de cure : 150 g/m\u00b2 environ."
            },
            {
                "document_id": "full-HYDRO REP surfa\u00e7age_Compressed-8fb9c724",
                "file_name": "HYDRO REP surfa\u00e7age_Compressed.pdf",
                "source_path": "ai_data\\raw\\sofap\\HYDRO REP surfa\u00e7age_Compressed.pdf",
                "chunk_ids": [
                    "0edc15932b396769"
                ],
                "substring": "La consommation de l\u2019HYDRO REP surfa\u00e7age varie selon le support (type, plan\u00e9it\u00e9, rugosit\u00e9) env.1.15 kg / m?/mm."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL11",
        "query": "Je cherche un outil pour couper des branches : que peut-il couper et quelles sont ses limites ?",
        "categories": [
            "vague/general",
            "safety/limitations"
        ],
        "evidence": [
            {
                "document_id": "full-ELSL203051%20Technical%20Data-e04c020d",
                "file_name": "ELSL203051%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ELSL203051%20Technical%20Data.pdf",
                "chunk_ids": [
                    "ae22722a9aeab3e8"
                ],
                "substring": "Cet \u00e9quipement est con\u00e7u pour couper des branches et des plantes d\u2019un diam\u00e8tre maximal de 30 mm (bois tendre). Le diam\u00e8tre est plus petit pour le bois dur. Cet \u00e9quipement ne convient pas \u00e0 la coupe du m\u00e9tal. L\u2019\u00e9quipement doit \u00eatre utilis\u00e9 uniquement pour l\u2019usage pr\u00e9vu.\nMoteur sans balais haute efficacit\u00e9 offrant plus de puissance et maximisant l\u2019autonomie"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL12",
        "query": "Quelle pression et quelle consommation d\u2019air demande la cl\u00e9 EATL341601 ?",
        "categories": [
            "highly specific",
            "technical specifications"
        ],
        "evidence": [
            {
                "document_id": "full-EATL341601%20Technical%20Data-7d7a619c",
                "file_name": "EATL341601%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EATL341601%20Technical%20Data.pdf",
                "chunk_ids": [
                    "ac2941f29e389f39"
                ],
                "substring": "Entra\u00eenement carr\u00e9 : 19 mm (3/4\")\nVitesse \u00e0 vide : 4 000 tr/min Couple maximum : 1 600 Nm (1 180 pieds)\nPoids : 6,0 kg M\u00e9canisme \u00e0 double marteau Avec connecteur universel.\nConsommation d'air : 256 l/min (9 cfm) Pression d'air : 6,2 bar (90 psi)\nLongueur : 234 mm (9,2\") Poids : 5,9 kg (13 lb) Entr\u00e9e d'air : 3/8\" Tuyau d'air : 1/2\" Emball\u00e9 par bo\u00eete de couleur"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL13",
        "query": "Quelle est la puissance et la vitesse \u00e0 vide de la scie ECSW1852 ?",
        "categories": [
            "technical specifications"
        ],
        "evidence": [
            {
                "document_id": "full-ECSW1852%20Technical%20Data-c3aa9e19",
                "file_name": "ECSW1852%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ECSW1852%20Technical%20Data.pdf",
                "chunk_ids": [
                    "9c77702218b75b91"
                ],
                "substring": "Puissance d'entr\u00e9e : 1400 W Vitesse \u00e0 vide : 4800 tr/min Diam\u00e8tre de la lame : 185 x 20 mm Capacit\u00e9 de coupe : 45 degr\u00e9s : 45 mm 90 degr\u00e9s : 65 mm Profondeur de coupe r\u00e9glable Coupe en biseau r\u00e9glable Avec 1 lame de 185 mm Avec 1 jeu de balais de charbon suppl\u00e9mentaires Emball\u00e9 par bo\u00eete de couleur"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL14",
        "query": "Comment appliquer PRIMER CONTACT sur un support tr\u00e8s lisse ?",
        "categories": [
            "preparation/application instructions"
        ],
        "evidence": [
            {
                "document_id": "full-primer%20contact1-411ec87f",
                "file_name": "primer%20contact1.pdf",
                "source_path": "ai_data\\raw\\sofap\\primer%20contact1.pdf",
                "chunk_ids": [
                    "90d0baaf325706fc"
                ],
                "substring": "\u2022  Appliquer PRIMER CONTACT au rouleau (laine de pr\u00e9f\u00e9rence) ou \u00e0 l\u2019aide d\u2019une brosse, en une couche r\u00e9guli\u00e8re r\u00e9alis\u00e9e en passes crois\u00e9es.\n\u2022  En cas de support tr\u00e8s lisse ou textur\u00e9, il est recommand\u00e9 d\u2019appliquer PRIMER CONTACT en couche crois\u00e9e."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL15",
        "query": "Combien de temps peut-on conserver PRIMER CONTACT et dans quelles conditions ?",
        "categories": [
            "safety/limitations"
        ],
        "evidence": [
            {
                "document_id": "full-primer%20contact1-411ec87f",
                "file_name": "primer%20contact1.pdf",
                "source_path": "ai_data\\raw\\sofap\\primer%20contact1.pdf",
                "chunk_ids": [
                    "acc4b208ab89c4fe"
                ],
                "substring": "\u2022 PRIMER CONTACT  se compose d\u2019un liant synth\u00e9\u019fque avec une stabilit\u00e9 alcaline, charges siliceuses, colorant. .Conserva\u019fon :\n\u2022 12 mois en emballage d\u2019origine, ferm\u00e9 \u00e0 l\u2019abri de l\u2019humidit\u00e9, prot\u00e9g\u00e9 du gel et des exc\u00e8s de chaleur (soleil direct)."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL16",
        "query": "Quel d\u00e9lai minimum avant jointoiement avec SOFAPCOL FLEX ?",
        "categories": [
            "application/use",
            "highly specific"
        ],
        "evidence": [
            {
                "document_id": "full-FLEX%20V4-afe87429",
                "file_name": "FLEX%20V4.pdf",
                "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
                "chunk_ids": [
                    "ce25465f13a094bd"
                ],
                "substring": "ux de g\u00e2chage : | Environ 28%\nur\u00e9e de malaxage : | Environ 3 min\nmps de matura\u019fon : | Environ 5 min\nmps ouvert : | Environ 30 min\n\nur\u00e9e pra\u019fque d\u2019u\u019flisa\u019f | on : Environ 3 heures\n\u00e9lais avant jointoieme | nt : Minimum 24 heures\n\nccessibilit\u00e9 : | 24\u00e0 48 h apr\u00e8s r\u00e9alisa\u019fon des joints"
            }
        ],
        "parser_signal": True
    },
    {
        "id": "BL17",
        "query": "Comment pr\u00e9parer les supports ciment avant la pose avec FLEX ?",
        "categories": [
            "substrate/support compatibility",
            "preparation/application instructions"
        ],
        "evidence": [
            {
                "document_id": "full-FLEX%20V4-afe87429",
                "file_name": "FLEX%20V4.pdf",
                "source_path": "ai_data\\raw\\sofap\\FLEX%20V4.pdf",
                "chunk_ids": [
                    "ac36b959e19a154b"
                ],
                "substring": "\u2022 Les supports doivent \u00eatre propres, sains et solides (les supports \u00e0 base de ciment ne doivent pas ressuer l\u2019humidit\u00e9).\n\u2022 Les dallages doivent \u00eatre r\u00e9alis\u00e9s depuis plus d\u2019un mois, les chapes ciment depuis plus de 15 jours, les enduits de ciment depuis plus de 48 heures.\n\u2022 Par temps chaud et/ou vent fort, ces supports seront humidi\ufb01\u00e9s quelques heures avant la pose.\n\u2022 L\u2019humidi\ufb01ca\u019fon des supports en b\u00e9ton cellulaire est imp\u00e9ra\u019fve avant de commencer la pose du mor\u019fer."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL18",
        "query": "\u00c0 quelle norme est conforme Mura-colle-platre et quelle est sa consommation ?",
        "categories": [
            "standards/norms",
            "consumption"
        ],
        "evidence": [
            {
                "document_id": "full-fiche_technique_Mura-colle-platre-24ed7a37",
                "file_name": "fiche_technique_Mura-colle-platre.pdf",
                "source_path": "ai_data\\raw\\gypsobat\\documents\\fiche_technique_Mura-colle-platre.pdf",
                "chunk_ids": [
                    "39a3d4120d0078db"
                ],
                "substring": "Consommation | 3 \u00e0 4 kg /m\u00b2\nTaux de g\u00e2chage | \u00e0 consistance 25%\u00b11\nConformit\u00e9 \u00e0 la norme | EN12004\nAdh\u00e9rance par traction | \u2265 0,5 N/mm\u00b2\nPropri\u00e9t\u00e9s | -Haute r\u00e9tention d\u2019eau. -Pouvoir liant tr\u00e9s efficace -Haute r\u00e9sistance en ambiance humide satur\u00e9e.\n\nType de produit | mortiers de colle des carreaux fa\u00efence\nClassification | C1\nTemps ouvert | \u2265 30 mn\nTemps d\u2019emploi 2 | h-3h\nTemp\u00e9rature d\u2019application 5 | \u00b0 \u00e0 35\u00b0 C"
            }
        ],
        "parser_signal": True
    },
    {
        "id": "BL19",
        "query": "Quelles sont les dimensions du chariot \u00e0 sept tiroirs ETCS0701 avec ses roulettes ?",
        "categories": [
            "dimensions",
            "highly specific"
        ],
        "evidence": [
            {
                "document_id": "full-ETCS0701%20Technical%20Data-2f79a4f6",
                "file_name": "ETCS0701%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ETCS0701%20Technical%20Data.pdf",
                "chunk_ids": [
                    "4cde6050e2f553a5"
                ],
                "substring": "1. Grand espace de stockage, poussoir confortable.\n2. Chaque tiroir est \u00e9quip\u00e9 d'une fonction d'auto-verrouillage pour \u00e9viter qu'il ne glisse automatiquement.\n3. Dispositif de frein pour roulettes multidirectionnelles.\n4. Conception de glissi\u00e8res \u00e0 billes enti\u00e8rement extensibles.\n5. Le corps du chariot est fabriqu\u00e9 en t\u00f4le d'acier lamin\u00e9e \u00e0 froid de haute qualit\u00e9, solide et robuste. Armoire \u00e0 roulettes Avec 7 tiroirs Dimensions totales : 680*458*802mm Dimensions totales avec roulettes : 680*458*945mm"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL20",
        "query": "Quelle est la capacit\u00e9 de charge du chariot ETDR7A30 ?",
        "categories": [
            "technical specifications"
        ],
        "evidence": [
            {
                "document_id": "full-ETDR7A30%20Technical%20Data-fd99ae9f",
                "file_name": "ETDR7A30%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ETDR7A30%20Technical%20Data.pdf",
                "chunk_ids": [
                    "83bbcde9f1cf5952"
                ],
                "substring": "1. Mat\u00e9riau de haute qualit\u00e9, solide et durable\n2. Avec frein \u00e0 pied, facile \u00e0 utiliser Charge : \u2264300kg Dimensions du chariot : 1280*870*360mm"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL21",
        "query": "La meuleuse ELAG4128112 est-elle utilisable avec de l\u2019eau ?",
        "categories": [
            "safety/limitations"
        ],
        "evidence": [
            {
                "document_id": "full-ELAG4128112%20Technical%20Data-52718f1b",
                "file_name": "ELAG4128112%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ELAG4128112%20Technical%20Data.pdf",
                "chunk_ids": [
                    "138f1d84eedd52dc"
                ],
                "substring": "La meuleuse d'angle adapt\u00e9e au meulage, au pon\u00e7age, aux op\u00e9rations de d\u00e9coupe abrasive et au brossage m\u00e9tallique, b\u00e9ton, pierre et mat\u00e9riaux similaires sans utilisation d'eau.\nMoteur sans balais - plus de puissance et une dur\u00e9e de fonctionnement plus longue\nFonction de d\u00e9marrage progressif et protection contre le red\u00e9marrage pour une utilisation plus s\u00fbre\nDisjoncteur de surcharge pour une longue dur\u00e9e de vie\nFonctionnement tr\u00e8s fluide gr\u00e2ce \u00e0 la s\u00e9paration du moteur et de la transmission\nBo\u00eetier de transmission robuste en aluminium\nDesign \u00e9lanc\u00e9 avec surfaces de pr\u00e9hension ergonomiques et souples\nPoign\u00e9e suppl\u00e9mentaire pouvant \u00eatre fix\u00e9e de mani\u00e8re flexible en 2 positions Moteur sans balais Tension : 42V Puissance d'entr\u00e9e max : 1280W Vitesse \u00e0 vide : 3000/6500/10000 tr/min Diam\u00e8tre du disque : 115mm"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL22",
        "query": "Quelle batterie est compatible avec les outils P20S ?",
        "categories": [
            "product identification",
            "vague/general"
        ],
        "evidence": [
            {
                "document_id": "full-EBPK20011%20Technical%20Data-ac08f0ef",
                "file_name": "EBPK20011%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EBPK20011%20Technical%20Data.pdf",
                "chunk_ids": [
                    "8f6935deb4a8474e"
                ],
                "substring": "Des cellules Li-Ion de haute qualit\u00e9 signifient pas d'effet m\u00e9moire, faible autod\u00e9charge et puissance \u00e9lev\u00e9e et constante\nNiveau de charge actuel indiqu\u00e9 par un affichage LED \u00e0 3 niveaux\nBo\u00eetier prot\u00e9g\u00e9 contre la poussi\u00e8re, la corrosion et les dommages m\u00e9caniques\nTension : batterie Lithium-ion 20 V 2,0 Ah Indicateur d'alimentation de la batterie LED Une batterie convient \u00e0 tous les outils multiples P20S\nEmball\u00e9 dans une bo\u00eete de couleur"
            },
            {
                "document_id": "full-EBPK20021%20Technical%20Data-e774e072",
                "file_name": "EBPK20021%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EBPK20021%20Technical%20Data.pdf",
                "chunk_ids": [
                    "438169fa5ddf1d66"
                ],
                "substring": "Des cellules Li-Ion de haute qualit\u00e9 signifient aucun effet m\u00e9moire, une faible autod\u00e9charge et une puissance \u00e9lev\u00e9e et constante\nLe niveau de charge actuel est indiqu\u00e9 par un affichage LED \u00e0 3 niveaux\nBo\u00eetier prot\u00e9g\u00e9 contre la poussi\u00e8re, la corrosion et les dommages m\u00e9caniques Tension : 20 V Batterie lithium-ion 4,0 Ah\nVoyant LED de niveau de charge de la batterie Une seule batterie compatible avec tous les outils multiples P20S\nEmball\u00e9 dans une bo\u00eete de couleur"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL23",
        "query": "Quels mat\u00e9riaux la polisseuse ELAP20151 peut-elle polir ?",
        "categories": [
            "application/use"
        ],
        "evidence": [
            {
                "document_id": "full-ELAP20151%20Technical%20Data-640eea36",
                "file_name": "ELAP20151%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ELAP20151%20Technical%20Data.pdf",
                "chunk_ids": [
                    "cc268fb57f689936"
                ],
                "substring": "L'outil \u00e9lectrique est destin\u00e9 au polissage et au brossage des surfaces m\u00e9talliques et rev\u00eatues ainsi qu'au polissage de la pierre.\nSolution sans fil pour une vari\u00e9t\u00e9 d'applications de polissage o\u00f9 la mobilit\u00e9 est importante\nPolisseuse \u00e0 double action aliment\u00e9e par batterie offrant une orbite al\u00e9atoire s\u00e9lectionnable avec rotation forc\u00e9e ou rotation libre\nLe design sans fil \u00e9limine les tracas de la gestion des c\u00e2bles et les rayures accidentelles des surfaces d\u00e9licates\nMolette de contr\u00f4le de vitesse variable situ\u00e9e de mani\u00e8re pratique avec 6 r\u00e9glages de vitesse (2000-4500 tr/min) OPM\n\u00c9quip\u00e9e de plaques de support pour tampons \u00e0 boucle de 6\" Moteur sans balais Tension : 20V"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL24",
        "query": "Quel est le couple de serrage et de desserrage de ECIWL42602 ?",
        "categories": [
            "technical specifications"
        ],
        "evidence": [
            {
                "document_id": "full-ECIWL42602%20Technical%20Data-292a3638",
                "file_name": "ECIWL42602%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ECIWL42602%20Technical%20Data.pdf",
                "chunk_ids": [
                    "28018b71f6582b5c"
                ],
                "substring": "La machine est destin\u00e9e au vissage et au desserrage des vis et des boulons, ainsi qu\u2019au serrage et au desserrage des \u00e9crous dans la plage de dimensions correspondante.\nLe moteur sans balais d\u00e9livre un couple de serrage de 600 Nm et un couple de desserrage de 750 Nm\nInterrupteur de s\u00e9lection de puissance \u00e0 3 vitesses (0-1700/0-2100 tr/min/0-2300 tr/min et 0-2400/0-2800/0-3300 coups/min) pour un contr\u00f4le pr\u00e9cis du serrage dans une large gamme d\u2019applications"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL25",
        "query": "Quelles fonctions de protection poss\u00e8de le multim\u00e8tre EDMR5110004 ?",
        "categories": [
            "safety/limitations"
        ],
        "evidence": [
            {
                "document_id": "full-EDMR5110004%20Technical%20Data-0ce60f56",
                "file_name": "EDMR5110004%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EDMR5110004%20Technical%20Data.pdf",
                "chunk_ids": [
                    "ac5da251ccc4f1ba"
                ],
                "substring": "1. Mod\u00e9lisation sp\u00e9cialis\u00e9e ;\n2. Affichage de la valeur efficace r\u00e9elle ;\n3. Fonction Smart, reconnaissance automatique des tests de tension, r\u00e9sistance et continuit\u00e9 ;\n4. Protection intelligente contre la surchauffe, avec fonction de protection contre les surcharges, emp\u00eachant les op\u00e9rations hors plage qui pourraient endommager le voltm\u00e8tre et l'amp\u00e8rem\u00e8tre, protection compl\u00e8te contre les surcharges, utilisation s\u00fbre et fiable ;\n5. Coque en caoutchouc, sensation agr\u00e9able au toucher \u00c9cran d'affichage couleur VA"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL26",
        "query": "Quel chargeur fournit une sortie 20 V et 2 A ?",
        "categories": [
            "product identification",
            "cross-document ambiguity"
        ],
        "evidence": [
            {
                "document_id": "full-EFCR20200%20Technical%20Data-ba45c83b",
                "file_name": "EFCR20200%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EFCR20200%20Technical%20Data.pdf",
                "chunk_ids": [
                    "c7e705cf2296d928"
                ],
                "substring": "Tension d'entr\u00e9e : 220-240 V ~ 50/60\nHz Tension de sortie : 20 V Courant de sortie : 2 A Emball\u00e9 dans une bo\u00eete de couleur."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL27",
        "query": "Quelles sont les dimensions et la mati\u00e8re de l\u2019arroseur ESNE13602 ?",
        "categories": [
            "dimensions"
        ],
        "evidence": [
            {
                "document_id": "full-ESNE13602%20Technical%20Data-608a536b",
                "file_name": "ESNE13602%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ESNE13602%20Technical%20Data.pdf",
                "chunk_ids": [
                    "026697171fe34411"
                ],
                "substring": "T\u00eate d'arroseur plastique Auto Gear Adaptateur d'outil 3/4\"\nPique en plastique \u00e0 3 broches Avec fonction rotative \u00e0 360\u00b0 R\u00e9glez librement les port\u00e9es/distance \u00e0 ajuster Dimensions : 38*17,4*6,4 cm Composition mat\u00e9rielle : ABS+PP\nEmball\u00e9 avec un cintre en papier"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL28",
        "query": "Quelle \u00e9nergie d\u2019impact offre le perforateur ERHRP1801 ?",
        "categories": [
            "technical specifications",
            "highly specific"
        ],
        "evidence": [
            {
                "document_id": "full-ERHRP1801%20Technical%20Data-111b1cac",
                "file_name": "ERHRP1801%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ERHRP1801%20Technical%20Data.pdf",
                "chunk_ids": [
                    "02dd0774ee118fee"
                ],
                "substring": "Tension : 220-240 V ~ 50/60 Hz\nPuissance d'entr\u00e9e : 1 800 W Vitesse \u00e0 vide : 850 tr/min Taux d'impact : 4 200 bpm \u00c9nergie d'impact : 7,0 J Capacit\u00e9 de per\u00e7age maximale :\nB\u00e9ton : 36 mm Acier : 13 mm Bois :"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL29",
        "query": "Quelle est l\u2019\u00e9paisseur maximale de coupe du d\u00e9coupeur ECUT451 ?",
        "categories": [
            "technical specifications"
        ],
        "evidence": [
            {
                "document_id": "full-ECUT451%20Technical%20Data-d6d7ef3d",
                "file_name": "ECUT451%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\ECUT451%20Technical%20Data.pdf",
                "chunk_ids": [
                    "bcdeb2a5098c19e0"
                ],
                "substring": "Tension d'entr\u00e9e (V) : 1~220-240 Fr\u00e9quence (Hz) : 50/60\nCourant de sortie (A) : 15-40A \u00c9paisseur de coupe : \u226412mm\nCycle de service (%) : 40%\nTension \u00e0 vide (V) : 400"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL30",
        "query": "\u00c0 quoi sert la plaque vibrante EPCT091611 ?",
        "categories": [
            "application/use"
        ],
        "evidence": [
            {
                "document_id": "full-EPCT091611%20Technical%20Data-04f35074",
                "file_name": "EPCT091611%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EPCT091611%20Technical%20Data.pdf",
                "chunk_ids": [
                    "bc8f9e9b6d4111f6"
                ],
                "substring": "Convient pour la r\u00e9paration des chauss\u00e9es en sable, gravier et sols m\u00e9lang\u00e9s dans les travaux municipaux.\nAvancement bidirectionnel r\u00e9versible.\nPosition d'op\u00e9ration mod\u00e9r\u00e9e.\nLes grands supports d'amortissement r\u00e9duisent les vibrations de la poign\u00e9e.\nLes supports d'amortissement lourds r\u00e9duisent les vibrations du pont sup\u00e9rieur.\nLa plaque inf\u00e9rieure r\u00e9sistante \u00e0 l'usure prolonge la dur\u00e9e de vie, conception ouverte, r\u00e9duit la salet\u00e9 de construction.\nLa tige de levage en position centrale facilite l'entr\u00e9e et la sortie des tranch\u00e9es.\nUtilisation de la puissance Honda, pour une dur\u00e9e de vie plus longue du produit et une qualit\u00e9 plus garantie."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL31",
        "query": "Quel diam\u00e8tre de lame utilise la scie EMCT14006 ?",
        "categories": [
            "dimensions",
            "highly specific"
        ],
        "evidence": [
            {
                "document_id": "full-EMCT14006%20Technical%20Data-488d023a",
                "file_name": "EMCT14006%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EMCT14006%20Technical%20Data.pdf",
                "chunk_ids": [
                    "7bd6cf9f6febf5fd"
                ],
                "substring": "Tension : 220-240V~50/60Hz Puissance d'entr\u00e9e : 1400W\nVitesse \u00e0 vide : 13000 tr/min\nDiam\u00e8tre de la lame : 110x20mm"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL32",
        "query": "Quelle est la temp\u00e9rature maximale du d\u00e9capeur thermique EHGN200318 ?",
        "categories": [
            "technical specifications"
        ],
        "evidence": [
            {
                "document_id": "full-EHGN200318%20Technical%20Data-944a00c8",
                "file_name": "EHGN200318%20Technical%20Data.pdf",
                "source_path": "ai_data\\raw\\emtop\\EHGN200318%20Technical%20Data.pdf",
                "chunk_ids": [
                    "3aa2c41cf26d5229"
                ],
                "substring": "1. \u00c9l\u00e9ment chauffant \u00e0 longue dur\u00e9e de vie\n2. Peut \u00eatre utilis\u00e9 en position invers\u00e9e\n3. Divers accessoires adapt\u00e9s \u00e0 diff\u00e9rents sc\u00e9narios de travail\n4. R\u00e9glage en 2 niveaux du d\u00e9bit d'air, vitesse du vent, temp\u00e9rature maximale jusqu'\u00e0 550\u2103, vitesse maximale jusqu'\u00e0 200L/min\n5. Coque et poign\u00e9e de conception d\u00e9velopp\u00e9e, prise en main confortable\n6. \u00c9quip\u00e9 de 2 batteries 5.0Ah, chargeur 4A, grande autonomie\n7. Affichage num\u00e9rique LCD, surveillance en temps r\u00e9el de la temp\u00e9rature de travail\n8. Corps principal et gaine du tuyau d'air s\u00e9parables, protection contre les br\u00fblures lors du Tension : 20V Temp\u00e9rature : 30-300\u2103/30-550\u00b0C"
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL33",
        "query": "Quelle consommation pr\u00e9voir pour SUPLATEX en mortier et en produit de cure ?",
        "categories": [
            "consumption"
        ],
        "evidence": [
            {
                "document_id": "full-SUPLATEX1-c1a35954",
                "file_name": "SUPLATEX1.pdf",
                "source_path": "ai_data\\raw\\sofap\\SUPLATEX1.pdf",
                "chunk_ids": [
                    "3ffbfb4c1ebb40d8"
                ],
                "substring": "\u2022 En couche d'accrochage (gobe\u019fs, barbo\u019fne) : environ 0,120 L / m\u00b2.\n\u2022 En mor\u019fer : environ 0,600 L / m\u00b2.\n\u2022 En primaire : de 80 g \u00e0 150 g/m\u00b2 environ selon la nature du support.\n\u2022 En produit de cure : 150 g/m\u00b2 environ."
            }
        ],
        "parser_signal": False
    },
    {
        "id": "BL34",
        "query": "Comment r\u00e9aliser l\u2019encollage du carrelage avec SOFAPCOL CONFORT ?",
        "categories": [
            "preparation/application instructions",
            "standards/norms"
        ],
        "evidence": [
            {
                "document_id": "full-CONFORT%20V4-577b657d",
                "file_name": "CONFORT%20V4.pdf",
                "source_path": "ai_data\\raw\\sofap\\CONFORT%20V4.pdf",
                "chunk_ids": [
                    "3b667fd34f972c32"
                ],
                "substring": "\u2022  Appliquer le mor\u019fer colle sur le support avec une taloche, puis l\u2019\u00e9paisseur du mor\u019fer colle sera r\u00e9gl\u00e9e avec la spatule crant\u00e9e adapt\u00e9e \u00e0 la dimension et au relief des carreaux.\n\u2022 Dans certains cas, la pose doit \u00eatre e\ufb00ectu\u00e9e par double encollage (se r\u00e9f\u00e9rer au DTU 52.2)."
            }
        ],
        "parser_signal": False
    }
]


def source_key(row):
    return (row["document_id"], row["file_name"], row["source_path"])


def read_collection(client):
    """Only the hierarchical collection; include vectors for integrity comparison."""
    rows, hashes, offset = [], [], None
    while True:
        points, offset = client.scroll(COLLECTION, limit=256, offset=offset,
                                      with_payload=True, with_vectors=True)
        for point in points:
            rows.append(point.payload)
            hashes.append(hashlib.sha256(point.model_dump_json().encode()).hexdigest())
        if offset is None:
            break
    return rows, hashlib.sha256(json.dumps(sorted(hashes)).encode()).hexdigest()


def validate_labels(labels, rows):
    if len(labels) < 30 or len({q["id"] for q in labels}) != len(labels):
        raise ValueError("Need at least 30 uniquely identified queries")
    for label in labels:
        if not label["query"].strip() or not label["evidence"]:
            raise ValueError("Empty query/evidence")
        for evidence in label["evidence"]:
            candidates = [r for r in rows if source_key(r) == source_key(evidence)
                          and r["chunk_id"] in evidence["chunk_ids"]]
            if {r["chunk_id"] for r in candidates} != set(evidence["chunk_ids"]):
                raise ValueError(f"Missing labeled chunks: {label['id']}")
            if not evidence["substring"] or not all(evidence["substring"] in r["text"] for r in candidates):
                raise ValueError(f"Labeled evidence changed: {label['id']}")


class CachedQueries:
    """Run-local exact-query cache of the existing embedding service."""
    def __init__(self, service):
        self.service = service
        self.dimension = service.dimension
        self.cache = {}

    def embed_single(self, query):
        if query not in self.cache:
            self.cache[query] = self.service.embed_single(query)
        return list(self.cache[query])


def measure(label, response, include_parents):
    """Evidence units are required facts; each unit's chunk IDs are alternatives."""
    exact, substring, ranks = set(), set(), []
    docs = {source_key(h) for h in response["hits"]}
    expected_docs = {source_key(e) for e in label["evidence"]}
    for rank, hit in enumerate(response["hits"], 1):
        texts = [hit["text"]]
        if include_parents:
            for context in response["contexts"]:
                if source_key(context) == source_key(hit) and hit["chunk_id"] in context["chunk_ids"]:
                    texts.extend(p["text"] for p in context["parents"] if source_key(p) == source_key(hit))
        relevant = False
        for i, evidence in enumerate(label["evidence"]):
            if source_key(evidence) != source_key(hit):
                continue
            is_exact = hit["chunk_id"] in evidence["chunk_ids"]
            is_substring = any(evidence["substring"] in text for text in texts)
            if is_exact:
                exact.add(i)
            if is_substring:
                substring.add(i)
            relevant |= is_exact or is_substring
        if relevant:
            ranks.append(rank)
    count = len(label["evidence"])
    return dict(hit=int(bool(ranks)), reciprocal_rank=1/min(ranks) if ranks else 0,
                document_recall=len(docs & expected_docs)/len(expected_docs),
                exact_evidence_recall=len(exact)/count, substring_evidence_recall=len(substring)/count,
                evidence_recall=len(exact | substring)/count, empty=int(not response["hits"]))


def aggregate(records):
    metrics = {name: statistics.mean(r["metrics"][name] for r in records)
               for name in ("hit", "reciprocal_rank", "document_recall", "exact_evidence_recall",
                            "substring_evidence_recall", "evidence_recall")}
    scores = [h["score"] for r in records for h in r["response"]["hits"]]
    metrics["average_returned_score"] = statistics.mean(scores) if scores else None
    metrics["empty_queries"] = sum(r["metrics"]["empty"] for r in records)
    metrics["queries"] = len(records)
    return metrics


def categorize(record, baseline, rows):
    """Conservative triage signals, not definitive attribution of causality."""
    reasons = []
    label = record["label"]
    if baseline["metrics"]["evidence_recall"] > record["metrics"]["evidence_recall"]:
        reasons.append("threshold issue")
    if "vague/general" in label["categories"] or "cross-document ambiguity" in label["categories"]:
        reasons.append("label ambiguity")
    for evidence in label["evidence"]:
        duplicates = {source_key(r) for r in rows if evidence["substring"] in r["text"]}
        if len(duplicates) > 1:
            reasons.append("duplicate/near-duplicate source issue")
    if label.get("parser_signal"):
        reasons.append("parser/chunking issue")
    if not reasons or (not baseline["metrics"]["hit"] and not label.get("parser_signal")):
        reasons.append("embedding/retrieval issue")
    return sorted(set(reasons))


def recommend(summaries):
    """Predeclared objective: smallest K within 95% of best parent evidence recall.

    Then largest tested threshold preserving that K's recall/MRR/empty count.
    This is calibration-set selection, not a held-out accuracy claim.
    """
    candidates = [s for s in summaries if s["mode"] == "verified_parent"]
    best = max(s["metrics"]["evidence_recall"] for s in candidates)
    k = min(s["top_k"] for s in candidates if s["threshold"] == 0.0
            and s["metrics"]["evidence_recall"] + 1e-12 >= .95*best)
    baseline = next(s["metrics"] for s in candidates if s["top_k"] == k and s["threshold"] == 0.0)
    eligible = [s for s in candidates if s["top_k"] == k
                and s["metrics"]["evidence_recall"] + 1e-12 >= baseline["evidence_recall"]
                and s["metrics"]["reciprocal_rank"] + 1e-12 >= baseline["reciprocal_rank"]
                and s["metrics"]["empty_queries"] <= baseline["empty_queries"]]
    return dict(top_k=k, similarity_threshold=max(s["threshold"] for s in eligible),
                mode="verified_parent", best_observed_evidence_recall=best,
                selection_rule="Smallest K reaching 95% of maximum evidence recall; highest threshold preserving recall, MRR and empty count at that K.")


def protected_snapshot():
    paths = []
    for folder in ("extraction", "chunking", "embeddings", "indexing", "vectorstore", "rag"):
        paths.extend((BACKEND/"app/ai"/folder).rglob("*.py"))
    paths.extend((BACKEND/"ai_data/reports/full_extraction").glob("*.json"))
    paths.extend((BACKEND/"ai_data/indexing").glob("*checkpoint*.json"))
    paths.extend([BACKEND/"app/routers/student.py", BACKEND/"app/ai/config.py"])
    return {str(p.relative_to(BACKEND)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def run_evaluation(retrievers, labels, rows, progress=None):
    records, summaries = [], []
    for mode in MODES:
        for k in TOP_K:
            for threshold in THRESHOLDS:
                batch = []
                for label in labels:
                    response = retrievers[mode].retrieve(label["query"], top_k=k,
                        similarity_threshold=threshold).to_dict()
                    record = dict(mode=mode, top_k=k, threshold=threshold, label=label,
                                  response=response, metrics=measure(label, response, mode == "verified_parent"))
                    records.append(record)
                    batch.append(record)
                summary = dict(mode=mode, top_k=k, threshold=threshold, metrics=aggregate(batch))
                summaries.append(summary)
                if progress:
                    progress(summary)
    baselines = {(r["mode"], r["top_k"], r["label"]["id"]): r for r in records if r["threshold"] == 0.0}
    for r in records:
        if r["metrics"]["evidence_recall"] < 1:
            r["failure_categories"] = categorize(r, baselines[r["mode"], r["top_k"], r["label"]["id"]], rows)
    return records, summaries


def write_report(path, records, summaries, metadata):
    rec = recommend(summaries)
    selected = [r for r in records if r["mode"] == rec["mode"] and r["top_k"] == rec["top_k"]
                and r["threshold"] == rec["similarity_threshold"]]
    from collections import Counter
    failures = Counter(c for r in selected for c in r.get("failure_categories", []))
    lines = ["# Hierarchical retrieval evaluation", "", f"Run: {metadata['run_utc']}", "",
        f"Recommended calibration default: **top_k={rec['top_k']}, similarity_threshold={rec['similarity_threshold']}**, verified parent context. Existing defaults were not changed.", "",
        rec["selection_rule"], "", "## Dataset and integrity", "", "```json", json.dumps(metadata, indent=2), "```", "",
        "## Method and practical limits", "",
        f"{len(LABELS)} frozen French BuildLearn questions were labeled from the actual indexed children before searching. Labels include full source identity, alternative chunk IDs and exact source substrings. All labels are validated against the live payloads at startup. Multiple evidence units are required facts; IDs within a unit are alternatives. Exact matching is case-sensitive and preserves source OCR. No answer or source text is generated.", "",
        "Every query is passed through the existing HierarchicalRetriever at each of the 48 configurations (two modes, four K values, six thresholds). Only query embeddings are cached in memory across configurations; Qdrant searches and verified source resolution are executed for each retrieval. No sibling fetches or LLM calls occur. Parent expansion uses the existing 6,000-character budget.", "",
        "Hit@K means at least one labeled evidence unit is found in the first K ranked hits, or its verified parent context in parent mode. MRR uses the first such rank and is truncated at the evaluated K. Document recall is the fraction of distinct labeled source identities retrieved. Exact evidence recall uses child IDs only; substring recall uses child text plus verified parents in parent mode, scoped to the labeled source. Combined evidence recall is their union. Metrics are macro-averaged over questions; average score is micro-averaged over returned hits. Empty count includes all questions with no returned hits. Parent expansion does not alter child scores or document rankings.", "",
        "This is a small, manually curated calibration set, not an exhaustive relevance judgment or held-out benchmark. General questions have incomplete positive labels, so an unlabelled result may be valid. It contains no unanswerable negative queries: threshold precision/abstention cannot be established. The selected threshold is the highest tested value that loses no measured recall/MRR or nonempty coverage at the selected K; it is not a calibrated relevance probability. Exact/near-duplicate sources are deliberately retained as distinct source identities. Failure categories are overlapping triage signals, not proven causal diagnoses. Parser signals identify visibly damaged indexed evidence without modifying parsing or chunking.", "",
        "## All configuration metrics", "",
        "| Mode | K / Hit@K | Threshold | Hit@K | MRR@K | Document recall | Exact recall | Substring recall | Combined recall | Mean score | Empty |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in summaries:
        m=s["metrics"]
        score = f"{m['average_returned_score']:.4f}" if m['average_returned_score'] is not None else "n/a"
        lines.append(f"| {s['mode']} | {s['top_k']} | {s['threshold']:.1f} | {m['hit']:.4f} | {m['reciprocal_rank']:.4f} | {m['document_recall']:.4f} | {m['exact_evidence_recall']:.4f} | {m['substring_evidence_recall']:.4f} | {m['evidence_recall']:.4f} | {score} | {m['empty_queries']} |")
    chosen=aggregate(selected)
    child=next(s["metrics"] for s in summaries if s["mode"] == "child_only"
               and s["top_k"] == rec["top_k"] and s["threshold"] == rec["similarity_threshold"])
    lines.extend(["", "## Measured findings", "",
        f"At the selected configuration, {sum(r['metrics']['hit'] for r in selected)}/{len(selected)} questions have at least one labeled evidence hit. Combined evidence recall is {chosen['evidence_recall']:.2%}; document recall is {chosen['document_recall']:.2%}; MRR is {chosen['reciprocal_rank']:.4f}. This measured evidence coverage is insufficient to claim strong retrieval quality.", "",
        f"Verified parent expansion changes combined evidence recall by {chosen['evidence_recall']-child['evidence_recall']:+.2%} compared with child-only at the same settings. Expansion can provide useful surrounding text without supplying the particular labeled facts; a zero metric gain must not be described as an evidence-recall improvement.", "",
        "| Question category (overlapping) | Questions | Hits | Combined evidence recall |",
        "|---|---:|---:|---:|"])
    for category in sorted({c for r in selected for c in r["label"]["categories"]}):
        subset=[r for r in selected if category in r["label"]["categories"]]
        lines.append(f"| {category} | {len(subset)} | {sum(r['metrics']['hit'] for r in subset)} | {aggregate(subset)['evidence_recall']:.4f} |")
    identical=all(s["metrics"] == next(b["metrics"] for b in summaries if b["mode"] == s["mode"]
        and b["top_k"] == s["top_k"] and b["threshold"] == 0.0) for s in summaries)
    if identical:
        lines.extend(["", "All six tested thresholds produce identical metrics and returned-score averages at every K/mode. Threshold calibration has no observed discriminatory value on this positive-only set. The 0.6 recommendation is the predeclared lossless tie-break among tested thresholds; there is no measured superiority over 0.0–0.5. Add independently judged ambiguous and unanswerable queries before relying on threshold-based abstention."])
    lines.extend(["", "## Failure triage at recommended configuration", "", "```json", json.dumps(dict(failures),indent=2), "```", "",
        "Embedding/retrieval signals require broader query/model analysis; parser signals require a corpus-wide audit before any changes. Ambiguous labels need additional human judgments. Duplicate signals require source/version review. Threshold losses are measured against the same mode/K at threshold 0.0. No pipeline tuning was performed.", "",
        "## Frozen labels and indexed evidence", "", "```json", json.dumps(LABELS, ensure_ascii=False, indent=2), "```", "",
        "## Complete per-query results", "", "Each row includes returned source/chunk IDs, scores, sections and block types; failed rows include expected evidence and all triage categories. Text is not repeated for every configuration; labels above retain exact evidence and the source snapshot digest identifies the evaluated dataset.", ""])
    for r in records:
        detail = {k:r[k] for k in ("mode", "top_k", "threshold", "metrics")}
        detail.update(query_id=r["label"]["id"], query=r["label"]["query"], warnings=r["response"]["warnings"],
                      returned=[{k:h[k] for k in ("document_id","file_name","source_path","chunk_id","score","section_path","block_type")} for h in r["response"]["hits"]],
                      parent_ids=[p["parent_id"] for c in r["response"]["contexts"] for p in c["parents"]])
        if "failure_categories" in r:
            detail.update(expected=r["label"]["evidence"], failure_categories=r["failure_categories"])
        lines.extend(["```json", json.dumps(detail,ensure_ascii=False), "```", ""])
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("\n".join(lines),encoding="utf-8")
    return rec, selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qdrant-url", default="http://127.0.0.1:6333")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--report", type=Path, default=BACKEND.parent/"docs/ai/RETRIEVAL_EVALUATION_REPORT.md")
    args=parser.parse_args()
    # Restrict output to documentation, never a checkpoint/source/code path.
    report=args.report.resolve()
    if not report.is_relative_to((BACKEND.parent/"docs/ai").resolve()) or report.suffix != ".md":
        parser.error("Report must be a Markdown file under docs/ai")
    before=protected_snapshot()
    client=QdrantClient(url=args.qdrant_url)
    rows,digest=read_collection(client)
    validate_labels(LABELS,rows)
    embeddings=CachedQueries(EmbeddingService(provider=OllamaEmbeddingProvider(
        base_url=args.ollama_url,model="nomic-embed-text",normalize=True)))
    retrievers={mode:HierarchicalRetriever(config=HierarchicalRetrievalConfig(expand_parents=mode=="verified_parent"),
                 embeddings=embeddings,client=client) for mode in MODES}
    records,summaries=run_evaluation(retrievers,LABELS,rows,
        progress=lambda s:print(json.dumps(s),flush=True))
    after_rows,after_digest=read_collection(client)
    if digest != after_digest or before != protected_snapshot():
        raise RuntimeError("Protected source/checkpoint or collection changed during evaluation")
    metadata=dict(run_utc=datetime.now(timezone.utc).isoformat(),collection=COLLECTION,
                  points=len(rows),points_after=len(after_rows),payload_vector_sha256=digest,
                  collection_unchanged=True,protected_files_unchanged=True,protected_files=len(before),
                  labels_sha256=hashlib.sha256(json.dumps(LABELS,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                  query_count=len(LABELS),configurations=len(summaries),retrieval_calls=len(records),
                  embedding_calls=len(embeddings.cache),embedding_model="nomic-embed-text",distance="COSINE",
                  parent_warnings=sum(bool(r["response"]["warnings"]) for r in records),
                  verified_parent_contexts=sum(bool(c["parents"]) for r in records for c in r["response"]["contexts"]),
                  integrity_scope="All hierarchical point payloads/vectors; protected Python sources, extraction JSONs, checkpoints, student router and AI config. Qdrant access logs excluded; no production collection is queried.")
    rec,selected=write_report(report,records,summaries,metadata)
    print("RECOMMENDATION "+json.dumps(rec),flush=True)
    for r in records:
        if "failure_categories" in r:
            print("FAILURE "+json.dumps(dict(mode=r["mode"],top_k=r["top_k"],threshold=r["threshold"],query=r["label"]["query"], expected=r["label"]["evidence"],
                categories=r["failure_categories"], returned=[{k:h[k] for k in ("document_id","file_name","chunk_id","score","section_path","block_type")} for h in r["response"]["hits"]]),ensure_ascii=True),flush=True)
    print(f"Report: {report}")
    client.close()


if __name__ == "__main__":
    main()
