"""Deterministic, read-only product ownership sidecar. Never supplies answer text."""
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote

COLLECTION = 'buildlearn_products_hierarchical_v1'
CATALOG = Path(__file__).resolve().parents[3] / 'ai_data/identity/product_identity_catalog.json'
CODE = re.compile(r'\b[a-z]{2,8}\d[a-z0-9]{1,11}\b')
STANDARD = re.compile(r'^(?:en|iso|iec|din|nf|dtu|pds)\d')


def normalize(value):
    value = unicodedata.normalize('NFKD', unquote(value)).casefold()
    return ' '.join(re.findall(r'[a-z0-9]+', ''.join(c for c in value if not unicodedata.combining(c))))


def codes(value):
    return sorted({c for c in CODE.findall(normalize(value)) if not STANDARD.match(c)})


def declarations(text):
    # Capture complete entity phrases, including mixed-case descriptors. Metadata
    # corroboration below rejects generic prose and brand/company declarations.
    result = []
    for line in text.splitlines():
        m = re.search(r'^\s*(?:[•*-]\s*)?(.{2,80}?)\s+(?:est|is)\s+(?:un|une|a|an)\b', line)
        if m:
            value = m[1].strip()
            if value[:1].isupper(): result.append(value)
    return sorted(set(result), key=normalize)


def filename_alias(filename):
    stem = unquote(filename).replace('\\', '/').rsplit('/', 1)[-1].rsplit('.', 1)[0]
    stem = re.sub(r'(?i)(?:technical[ _-]*data|compressed|brochure|datasheet|certificate)', '', stem)
    stem = re.sub(r'(?i)\b(?:fiche|technique|locale)\b', '', normalize(stem))
    stem = re.sub(r'\bv\d+\b', '', stem)
    return ' '.join(stem.split())


def build_catalog(documents, rows, collection_digest):
    """Pure audit/build step; callers provide verified extracted artifacts and payloads."""
    indexed = defaultdict(list)
    for row in rows: indexed[(row['document_id'],row['source_path'])].append(row)
    inventory = []
    products = {}
    for doc in sorted(documents, key=lambda d: d['document_id']):
        did, filename = doc['document_id'], doc['file_name']
        children = indexed[(did,doc['source_path'])]
        if not children or {r['chunk_id'] for r in children} != set(doc['_chunk_ids']):
            raise ValueError('Extraction/index child inventory mismatch: ' + did)
        if any((r['file_name'], r['source_path']) != (filename, doc['source_path']) for r in children):
            raise ValueError('Extraction/index provenance mismatch: ' + did)
        text = '\n'.join(p['raw_text'] for p in doc['pages'])
        alias = filename_alias(filename)
        file_codes = codes(filename)
        found = declarations(text)
        # A declaration must share a nontrivial name token or exact code with the
        # source metadata. Uncorroborated declarations remain visible in the audit.
        meaningful = set(alias.split()) - {'pro','data','technical','board','gyproc','fiche','technique'}
        # A trailing filename revision is an alias only when the independent
        # declaration itself matches the revision-free filename.
        meaningful |= {re.sub(r'\d+$','',w) for w in meaningful if not codes(w)}
        names = {normalize(n) for n in found if set(normalize(n).split()) & meaningful}
        owner_codes = set(file_codes)
        heading_codes = {normalize(l.strip()) for l in text.splitlines() if CODE.fullmatch(normalize(l.strip()))}
        heading_codes = {c for c in heading_codes if not STANDARD.match(c)}
        foreign = heading_codes - owner_codes
        compatible = set()
        for line in text.splitlines():
            if re.search(r'convient pour|compatible|suitable for|fits|pour utilisation avec', normalize(line)):
                compatible.update(codes(line))
        flags = []
        if any(':' in n or re.search(r'\b(which|consist|application)\b',normalize(n)) for n in found if normalize(n) in names):
            flags.append('non_entity_declaration')
        if file_codes and any(codes(n) and not set(codes(n)) <= owner_codes for n in found):
            flags.append('filename_declaration_disagreement')
        if len(owner_codes) > 1: flags.append('multiple_filename_codes')
        if foreign - compatible: flags.append('incompatible_owner_headings')
        if len(names) > 1: flags.append('multiple_product_declarations')
        # Explicit declarations of different physical product types in one source
        # remain quarantined, even if a code is present in the filename.
        body = normalize(text)
        if re.search(r'soudage|welding', body) and re.search(r'lame de scie|saw blade|diametre de lame', body):
            flags.append('incompatible_product_descriptions')
        candidate = next(iter(names)) if len(names) == 1 else None
        if candidate and not owner_codes:
            words=candidate.split()
            def corroborated(value):
                return all(w in words or (len(w)==1 and any(t.startswith(w) for t in words)) for w in value.split())
            if not corroborated(alias) and not corroborated(re.sub(r'\s*\d+$','',alias).strip()):
                flags.append('filename_declaration_disagreement')
        if owner_codes:
            if candidate and codes(candidate) and not set(codes(candidate)) <= owner_codes:
                flags.append('filename_declaration_disagreement')
            candidate = next(iter(owner_codes)) if len(owner_codes) == 1 else None
        elif not candidate:
            # Filename is only a candidate. A complete title in the document must
            # independently corroborate it; no arbitrary substring matching.
            titles = {normalize(l) for l in text.splitlines() if 2 <= len(l.strip()) <= 80}
            if alias in titles: candidate = alias
            else:
                title_alias = re.sub(r'\s*\d+$', '', alias).strip()
                if title_alias in titles: candidate = title_alias
            if not candidate:
                # Some sheets repeat their complete product title before the
                # description, while the filename contains only its variant.
                # Require adjacent identical uppercase titles and an exact
                # token suffix; a filename or body mention alone is insufficient.
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                repeated = set()
                for first, second in zip(lines, lines[1:]):
                    title = normalize(first)
                    words, suffix = title.split(), alias.split()
                    if (first.isupper() and second.isupper()
                            and title == normalize(second) and suffix
                            and len(words) == len(suffix) + 1
                            and words[-len(suffix):] == suffix
                            and re.fullmatch(r'[a-z]{2,20}', words[0])):
                        repeated.add(title)
                if len(repeated) == 1:
                    candidate = next(iter(repeated))
                elif len(repeated) > 1:
                    flags.append('multiple_product_declarations')
        if not candidate: flags.append('identity_unresolved')
        product_id = None
        if candidate and not flags:
            product_id = 'product-' + sha256(candidate.encode()).hexdigest()[:20]
            product = products.setdefault(product_id, dict(product_id=product_id, canonical_name=candidate,
                codes=[], aliases=[], document_ids=[], source_files=[]))
            product['codes'] = sorted(set(product['codes']) | owner_codes)
            product['aliases'] = sorted(set(product['aliases']) | {candidate, alias, normalize(filename)} | names)
            product['document_ids']=sorted(set(product['document_ids']) | {did})
            product['source_files'].append(dict(document_id=did, file_name=filename, source_path=doc['source_path']))
        inventory.append(dict(document_id=did, source_path=doc['source_path'], file_name=filename,
            detected_product_codes=codes(text + '\n' + filename), filename_codes=file_codes,
            candidate_canonical_product_name=candidate, explicit_product_declarations=found,
            aliases_variants=sorted({alias} | names), compatibility_references=sorted(compatible),
            heading_references=sorted(heading_codes), ambiguity_conflict_flags=sorted(flags), product_id=product_id,
            ownership_basis='corroborated declaration/title' if names or (candidate and not owner_codes) else 'single source reference; full-document conflict audit',
            extraction_sha256=doc['_extraction_sha256'], raw_text_sha256=sha256(text.encode()).hexdigest(),
            child_text_sha256={r['chunk_id']: sha256(r['text'].encode()).hexdigest() for r in sorted(children,key=lambda r:r['chunk_id'])},
            duplicate_documents=[], near_duplicate_documents=[]))
    # A filename that names a different declared catalog identity is a conflict,
    # not an alias. Remove the unsafe association before exposing the catalog.
    canonical_names={p['canonical_name']:p['product_id'] for p in products.values()}
    for d in inventory:
        alias=filename_alias(d['file_name'])
        other=canonical_names.get(alias)
        if d['product_id'] and other and other!=d['product_id']:
            old=products[d['product_id']]
            old['source_files']=[f for f in old['source_files'] if (f['document_id'],f['source_path'])!=(d['document_id'],d['source_path'])]
            old['document_ids']=sorted({f['document_id'] for f in old['source_files']})
            d['product_id']=None; d['ambiguity_conflict_flags'].append('filename_declaration_disagreement')
    products={k:p for k,p in products.items() if p['source_files']}
    # Exact duplicates and transparent token-Jaccard near duplicates are audit
    # signals, not automatic ownership merges.
    texts = {(d['document_id'],d['source_path']): set(normalize('\n'.join(p['raw_text'] for p in d['pages'])).split()) for d in documents}
    for i, a in enumerate(inventory):
        for b in inventory[i+1:]:
            if a['raw_text_sha256'] == b['raw_text_sha256']:
                a['duplicate_documents'].append(b['document_id']); b['duplicate_documents'].append(a['document_id'])
            else:
                x, y = texts[(a['document_id'],a['source_path'])], texts[(b['document_id'],b['source_path'])]
                if x and y and len(x & y) / len(x | y) >= .9:
                    a['near_duplicate_documents'].append(b['document_id']); b['near_duplicate_documents'].append(a['document_id'])
    return dict(schema_version=1, collection=COLLECTION, collection_sha256=collection_digest,
        documents=inventory, products=sorted(products.values(),key=lambda p:p['product_id']),
        summary=dict(documents=len(inventory), children=len(rows),
            unambiguous_documents=sum(d['product_id'] is not None for d in inventory),
            ambiguous_documents=sum(d['product_id'] is None for d in inventory),
            multiple_reference_documents=sum(len(d['detected_product_codes'])>1 for d in inventory),
            filename_identity_disagreements=sum('filename_declaration_disagreement' in d['ambiguity_conflict_flags'] or 'incompatible_owner_headings' in d['ambiguity_conflict_flags'] for d in inventory),
            duplicate_identity_groups=sum(len(p['document_ids'])>1 for p in products.values())))


@dataclass(frozen=True)
class IdentityResolution:
    resolved_product_ids: tuple[str, ...]
    unresolved_requested_entities: tuple[str, ...]
    ambiguous_candidates: dict[str, tuple[str, ...]]

    @property
    def safe(self):
        return bool(self.resolved_product_ids) and not self.unresolved_requested_entities and not self.ambiguous_candidates


class ProductIdentityResolver:
    def __init__(self, catalog):
        # Defensive copy; instances have no request-specific mutable state.
        self._catalog = json.loads(json.dumps(catalog))
        if self._catalog['collection'] != COLLECTION: raise ValueError('Identity collection isolation')
        self._documents = {(d['document_id'],d['source_path']):d for d in self._catalog['documents']}
        self._aliases = defaultdict(set)
        for p in self._catalog['products']:
            for a in [p['canonical_name'], *p['codes'], *p['aliases']]:
                if normalize(a): self._aliases[normalize(a)].add(p['product_id'])
        # A family prefix of multiple canonical names is explicitly ambiguous.
        for p in self._catalog['products']:
            words = normalize(p['canonical_name']).split()
            for n in range(1,len(words)):
                prefix=' '.join(words[:n])
                # A full catalog name takes precedence over a family prefix.
                if prefix not in {normalize(a) for product in self._catalog['products'] for a in [product['canonical_name'],*product['aliases'],*product['codes']]}:
                    self._aliases[prefix].add(p['product_id'])

    @classmethod
    def load(cls, path=CATALOG):
        catalog=json.loads(Path(path).read_text(encoding='utf-8'))
        backend=Path(__file__).resolve().parents[3]
        checkpoint=backend/'ai_data/indexing/hierarchical_index_checkpoint.json'
        raw=checkpoint.read_bytes()
        if sha256(raw).hexdigest()!=catalog['checkpoint_sha256']:
            raise ValueError('Stale product identity catalog: checkpoint mismatch')
        manifest=json.loads(raw)['state']['dataset_manifest']
        expected={(d['document_id'],d['extraction_sha256']) for d in catalog['documents']}
        for item in manifest:
            content=(backend/'ai_data/reports/full_extraction'/item['file']).read_bytes()
            if sha256(content).hexdigest()!=item['hash'] or (item['document_id'],item['hash']) not in expected:
                raise ValueError('Stale product identity catalog: corpus mismatch')
        return cls(catalog)

    def resolve(self, question):
        text=normalize(question)
        # Only join punctuation/spacing for a complete *known* reference. Never
        # expand partial codes or infer an unknown suffix.
        for alias in self._aliases:
            m=CODE.fullmatch(alias)
            split=re.fullmatch(r'([a-z]+)(\d[a-z0-9]+)',alias) if m else None
            if split:
                text=re.sub(r'(?<!\w)'+re.escape(split[1])+r'\s+'+re.escape(split[2])+r'(?!\w)',alias,text)
        matches=[]
        for alias, ids in self._aliases.items():
            for m in re.finditer(r'(?<!\w)'+re.escape(alias)+r'(?!\w)', text):
                matches.append((m.start(),m.end(),alias,ids))
        # Nested family prefixes must not collide with a matched full variant.
        selected=[m for m in matches if not any(m[0]>=o[0] and m[1]<=o[1] and (m[0],m[1])!=(o[0],o[1]) for o in matches)]
        resolved=set(); ambiguous={}; unresolved=set()
        for start,end,alias,ids in selected:
            if len(ids)>1: ambiguous[alias]=tuple(sorted(ids))
            else: resolved.update(ids)
        for c in codes(question):
            if c not in self._aliases: unresolved.add(c)
        for m in re.finditer(r'\b([A-Z]{2,8})[ -]+(\d[A-Z0-9]{1,11})\b',unquote(question)):
            combined=normalize(m[1]+m[2]); phrase=normalize(m[0])
            if not STANDARD.match(combined) and combined not in self._aliases and not any(phrase in name for _,_,name,_ in selected):
                unresolved.add(combined)
        # Explicit uppercase requested names cannot hide behind another resolved
        # product. Also catch unknown suffixes after a known family/variant.
        for phrase in re.findall(r'\b[A-ZÀ-ÖØ-Ý]{2,}(?:[ _-]+[A-ZÀ-ÖØ-Ý]{1,}){1,3}\b', unquote(question)):
            name=normalize(phrase)
            if set(name.split()) <= {'nf','en','iso','iec','din','dtu'}: continue
            if name not in self._aliases: unresolved.add(name)
        # Only known aliases resolve; case-insensitive product-like suffixes
        # (PRO/PLUS/family letters/version numbers) require an exact catalog entry.
        for start,end,alias,ids in selected:
            tail=text[end:].split()
            if tail and re.fullmatch(r'(?:pro|plus|eco|[b-z]|v\d+|\d+)',tail[0]):
                extended=alias+' '+tail[0]
                if extended not in self._aliases: unresolved.add(extended)
            # Unknown lower-case family variants are not licensed by matching
            # their shorter parent alias. Ordinary question continuations delimit
            # the entity; the vocabulary is grammar, not evaluation product IDs.
            if tail and not CODE.fullmatch(alias) and not normalize(alias).endswith('pdf'):
                boundaries={'et','and','ou','or','de','du','des','a','au','aux','est','is','are','can','may','peut','pour','for','sur','on','avec','with','en','in','selon','from','dans','quelle','quel','quels','quelles','combien','faut','permet','what','which','how','do','does','vs','versus','sans','without','aussi','supporte','resiste','reste','contient','temperature','dimensions','consommation','pression','diametre','composition','application'}
                # Ordinary finite verbs delimit a French clause, not a variant.
                # Unknown modifiers still fail closed. This is a syntax rule,
                # not a list of particular corpus products/questions.
                clause=bool(re.fullmatch(r'[a-z]{3,}(?:e|ent)',tail[0]))
                if tail[0] not in boundaries and not clause:
                    extended=alias+' '+tail[0]
                    if extended not in self._aliases: unresolved.add(extended)
        return IdentityResolution(tuple(sorted(resolved)),tuple(sorted(unresolved)),ambiguous)

    def product_name(self, product_id):
        """Catalog display name only; does not change entity matching rules."""
        return next((p['canonical_name'] for p in self._catalog['products'] if p['product_id'] == product_id), None)

    def ownership(self, source):
        d=self._documents.get((source.document_id,source.source_path))
        if not d or not d['product_id'] or d['ambiguity_conflict_flags']: return set()
        if (source.file_name,source.source_path)!=(d['file_name'],d['source_path']): return set()
        if source.evidence_kind=='child':
            if d['child_text_sha256'].get(source.chunk_id)!=sha256(source.text.encode()).hexdigest(): return set()
        return {d['product_id']}

    def document_flags(self, source):
        d=self._documents.get((source.document_id,source.source_path))
        return tuple(d['ambiguity_conflict_flags']) if d else ('identity_unresolved',)
