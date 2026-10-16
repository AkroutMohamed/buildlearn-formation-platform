"""Separate, read-only lexical-first retrieval; no generation or indexing."""
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
import re
from types import SimpleNamespace
import unicodedata
from urllib.parse import unquote

from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.ai.config import ai_settings
from app.ai.retrieval.hierarchical_models import RetrievedChild, RetrievalResponse
from app.ai.retrieval.hierarchical_retriever import COLLECTION, HierarchicalRetriever, HierarchicalRetrievalConfig

IDENTIFIER = re.compile(r"(?<![A-Z0-9])[A-Z]{2,8}[0-9][A-Z0-9]{2,11}(?![A-Z0-9])", re.I)
STOP = set("a au aux avec ce ces cette de des du en est et il la le les leur ne ou par pas pour quel quelle quelles quels que qui se ses son sur un une dans peut elle etre sont comment combien quoi avant apres".split())


def overview_priority(row):
    """Prefer explicit technical facts, then specification sections, for overviews."""
    body = normalize(row['text'])
    section = normalize(' '.join(row.get('section_path', [])))
    attribute = re.search(r'\b(?:consommation|resistance|conductivite|pression|pressure|'
        r'tension|voltage|puissance|power|couple|torque|vitesse|speed|capacite|capacity|'
        r'dimensions?|diametre|diameter|longueur|length|poids|weight|epaisseur|thickness|'
        r'reaction au feu|fire reaction|purete|purity|composition)\b', body)
    if attribute and re.search(r'\d', body):
        # Prefer clear original facts to an OCR replacement/ambiguous formula.
        # No text is corrected; lower-priority evidence remains auditable.
        return 2 if '\ufffd' in body or '(|' in body else 3
    return int(bool(re.search(r'\b(?:caracteristiques|specifications|technical specifications)\b', section)))


def is_product_overview(query):
    text = normalize(query)
    return (bool(re.search(r'\b(?:caracteristiques|specifications|fiche technique)\b', text))
        and not re.search(r'\b(?:minimum|maximum|exact|range|plage|pression|pressure|'
            r'tension|voltage|puissance|power|couple|torque|consommation|consumption|'
            r'dimensions?|diametre|diameter|poids|weight|epaisseur|thickness|'
            r'compatible|compatibility|autorise|interdit|prohibited)\b', text))


def normalize(text):
    text = unquote(text).replace("\u0153", "oe").replace("\u0152", "OE")
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)).casefold()


def tokens(text):
    return set(re.findall(r"[a-z]+[0-9]+[a-z0-9]*|[a-z]+|[0-9]+(?:[.,][0-9]+)?", normalize(text)))


def source(row):
    return row["document_id"], row["file_name"], row["source_path"]


def identity(row):
    return (*source(row), row["chunk_id"])


@dataclass(frozen=True)
class RetrievalV2Config:
    top_k: int = 5
    lexical_candidates: int = 50
    dense_candidates: int = 100
    expand_parents: bool = True
    max_parent_chars: int = 6000

    def __post_init__(self):
        for name in ("top_k", "lexical_candidates", "dense_candidates"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f"{name} must be a positive integer")
        HierarchicalRetrievalConfig(top_k=self.top_k, expand_parents=self.expand_parents,
                                    max_parent_chars=self.max_parent_chars)


@dataclass
class V2Child(RetrievedChild):
    dense_score: float | None = None
    dense_rank: int | None = None
    lexical_score: float = 0.0
    lexical_rank: int | None = None
    identifier_match: bool = False
    filename_match: float = 0.0
    numeric_match: float = 0.0
    word_match: float = 0.0
    candidate_sources: list[str] = field(default_factory=list)
    identifier_route: bool = False
    product_overview_match: bool = False
    overview_priority: int = 0


@dataclass
class V2Response(RetrievalResponse):
    candidates: list[V2Child] = field(default_factory=list)
    query_analysis: dict = field(default_factory=dict)


class LexicalIndex:
    """Process-local payload snapshot; no persistent index or new dependency."""
    def __init__(self, rows):
        unique = {}
        for row in rows:
            HierarchicalRetriever._hit(SimpleNamespace(payload=row, score=0.0))
            key = identity(row)
            if key in unique and unique[key] != row:
                raise ValueError("Conflicting corpus payload for source chunk")
            unique[key] = deepcopy(row)
        self.rows = unique
        self.catalog = {}
        for row in unique.values():
            for ref in IDENTIFIER.findall(unquote(row["file_name"])):
                if sum(c.isdigit() for c in ref) >= 3:
                    self.catalog.setdefault(ref.upper(), set()).add(source(row))
        self.row_tokens = {k: tokens(r["text"] + " " + r["file_name"]) for k, r in unique.items()}
        df = Counter(t for ts in self.row_tokens.values() for t in ts)
        self.idf = {t: math.log((len(unique)+1)/(n+1))+1 for t, n in df.items()}
        self.digest = hashlib.sha256(json.dumps(sorted(unique.values(), key=identity),
            sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def analyze(self, query):
        recognized, unknown = [], []
        for ref in sorted({m.upper() for m in IDENTIFIER.findall(query)}):
            (recognized if ref in self.catalog else unknown).append(ref)
        matches = set.intersection(*(self.catalog[r] for r in recognized)) if recognized else set()
        # Do not route a multi-reference question if any reference is unknown.
        route = next(iter(matches)) if len(matches) == 1 and not unknown else None
        return dict(identifiers=recognized, unknown_identifiers=unknown,
                    route_source=route, route_status="unique" if route else "unrouted",
                    tokens=sorted(tokens(query)))

    def rank(self, query, analysis):
        qt = tokens(query)
        numeric = {t for t in qt if re.fullmatch(r"\d+(?:[.,]\d+)?", t)}
        words = qt - numeric - STOP
        denominator = sum(self.idf.get(t, math.log(len(self.rows)+1)+1) for t in words)
        ranked = []
        for key, row in self.rows.items():
            rt = self.row_tokens[key]
            ident = any(ref.lower() in rt for ref in analysis["identifiers"])
            filename = len(words & tokens(row["file_name"]))/len(words) if words else 0.0
            number = len(numeric & rt)/len(numeric) if numeric else 0.0
            overlap = sum(self.idf[t] for t in words & rt)/denominator if denominator else 0.0
            ranked.append((key, (float(ident)+filename+number+overlap, ident, filename, number, overlap)))
        ranked.sort(key=lambda item: (-item[1][0], item[0]))
        return {key: (rank, features) for rank, (key, features) in enumerate(ranked, 1)}


class RetrievalV2:
    def __init__(self, *, config=None, client=None, embeddings=None, context_resolver=None, identity_resolver=None):
        self.config = config or RetrievalV2Config()
        self.client = client if client is not None else QdrantClient(url=ai_settings.qdrant_url)
        self._v1 = HierarchicalRetriever(client=self.client, embeddings=embeddings,
            context_resolver=context_resolver, config=HierarchicalRetrievalConfig(
                expand_parents=False, max_parent_chars=self.config.max_parent_chars))
        self._index = None
        self.identity_resolver = identity_resolver

    def refresh(self):
        params = self.client.get_collection(COLLECTION).config.params.vectors
        if not isinstance(params, models.VectorParams) or params.size != 768 or params.distance != models.Distance.COSINE:
            raise ValueError("Hierarchical collection requires 768-dimensional COSINE vectors")
        rows, offset = [], None
        while True:
            points, offset = self.client.scroll(COLLECTION, limit=256, offset=offset,
                with_payload=True, with_vectors=False)
            rows.extend(point.payload for point in points)
            if offset is None:
                break
        index = LexicalIndex(rows)
        self._index = index  # replace only after complete schema validation
        return index.digest

    def retrieve(self, query, *, top_k=None, mode="v2"):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be nonempty")
        k = self.config.top_k if top_k is None else top_k
        if type(k) is not int or k < 1:
            raise ValueError("top_k must be a positive integer")
        if mode not in ("v2", "lexical", "identifier_lexical"):
            raise ValueError("Unsupported retrieval mode")
        if self._index is None:
            self.refresh()
        index = self._index
        analysis = index.analyze(query)
        lexical = index.rank(query, analysis)
        overview_keys = set()
        # Apply only to broad specification requests with one safely resolved
        # product. Unknown identities/comparisons retain the ordinary path.
        if (mode == 'v2' and self.identity_resolver is not None
                and is_product_overview(query)):
            resolution = self.identity_resolver.resolve(query)
            if resolution.safe and len(resolution.resolved_product_ids) == 1:
                target = set(resolution.resolved_product_ids)
                for key, row in index.rows.items():
                    evidence = SimpleNamespace(**row, evidence_kind='child')
                    if self.identity_resolver.ownership(evidence) == target:
                        overview_keys.add(key)
                analysis['product_overview_ids'] = list(resolution.resolved_product_ids)
        route = analysis["route_source"] if mode != "lexical" else None
        memberships = {}
        positive = [key for key, (_, f) in lexical.items() if f[0] > 0]
        for key in positive[:self.config.lexical_candidates]:
            memberships.setdefault(key, []).append("lexical")
        if overview_keys:
            scoped = sorted(overview_keys, key=lambda key: (
                -overview_priority(index.rows[key]), -lexical[key][1][0], key))
            for key in scoped[:self.config.lexical_candidates]:
                memberships.setdefault(key, []).append('product_overview')
        if route:
            routed = [key for key in positive if source(index.rows[key]) == route]
            for key in routed[:self.config.lexical_candidates]:
                memberships.setdefault(key, []).append("identifier_route")
        dense = {}
        if mode == "v2":
            response = self._v1.retrieve(query, top_k=self.config.dense_candidates, similarity_threshold=0.0)
            for rank, hit in enumerate(response.hits, 1):
                key = identity(hit.payload_metadata)
                if key not in index.rows or hit.payload_metadata != index.rows[key]:
                    raise ValueError("Dense payload differs from lexical snapshot; refresh required")
                dense[key] = (rank, hit.score)
                memberships.setdefault(key, []).append("dense")
        candidates = []
        for key, branches in memberships.items():
            rank, features = lexical[key]
            score, ident, filename, number, word = features
            hit = self._v1._hit(SimpleNamespace(payload=index.rows[key], score=score))
            dr, ds = dense.get(key, (None, None))
            candidates.append(V2Child(**asdict(hit), dense_score=ds, dense_rank=dr,
                lexical_score=score, lexical_rank=rank, identifier_match=ident,
                filename_match=filename, numeric_match=number, word_match=word,
                candidate_sources=sorted(set(branches)), identifier_route=bool(route and source(index.rows[key]) == route),
                product_overview_match=key in overview_keys,
                overview_priority=overview_priority(index.rows[key]) if key in overview_keys else 0))
        # Lexical-first; exact routing outranks other sources. Dense is only a tie-break.
        candidates.sort(key=lambda h: (-int(h.product_overview_match), -h.overview_priority,
            -int(h.identifier_route), -h.lexical_score,
            -(h.dense_score if h.dense_score is not None else -1.0), identity(h.payload_metadata)))
        selected, seen = [], set()
        for hit in candidates:
            if overview_keys and not hit.product_overview_match:
                continue
            duplicate = (hit.text, tuple(hit.section_path), hit.page_start, hit.page_end)
            if overview_keys and duplicate in seen:
                continue
            seen.add(duplicate)
            selected.append(hit)
            if len(selected) == k:
                break
        hits = deepcopy(selected)
        warnings, resolved = [], {}
        if hits and self.config.expand_parents:
            try:
                resolved = self._v1._resolver.resolve(hits)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                warnings.append(f"Parent context unavailable: {exc}")
        for hit in hits:
            evidence = resolved.get((hit.document_id, hit.source_path, hit.chunk_id))
            if evidence is not None and hit.parent_id_path is None:
                hit.parent_id_path = list(evidence.parent_id_path)
                hit.parent_id_path_source = "verified_source_child"
        contexts = self._v1._contexts(hits, resolved, warnings)
        rendered = []
        for context in contexts:
            header = {name: getattr(context, name) for name in ("document_id", "file_name", "source_path",
                "parent_id", "parent_id_path", "section_path", "page_start", "page_end", "chunk_ids")}
            texts = list(dict.fromkeys([p.text for p in context.parents]+[f.text for f in context.fragments]))
            rendered.append(json.dumps(header, ensure_ascii=False)+"\n"+"\n\n".join(texts))
        analysis["snapshot_sha256"] = index.digest
        return V2Response(hits, contexts, "\n\n".join(rendered), list(dict.fromkeys(warnings)), candidates, analysis)
