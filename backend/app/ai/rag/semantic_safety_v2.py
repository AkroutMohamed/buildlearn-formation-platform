"""Selected-context-only safety checks, beside the unchanged extractive validator."""
from collections import defaultdict
import re
from urllib.parse import unquote

from app.ai.rag.answer_validation_v2 import canonical, support_id

CODE = re.compile(r'\b[a-z]{2,8}\d[a-z0-9]{2,11}\b')
STANDARD = re.compile(r'^(?:en|iso|iec|din|nf|dtu)\d')
DECLARATION = re.compile(r'\b([A-Z][A-Z0-9À-ÖØ-Ý _-]{2,60})\s+(?:est|is)\b')


class SemanticSafetyError(ValueError):
    pass


def codes(text):
    return {m for m in CODE.findall(canonical(text)) if not STANDARD.match(m)}


def document_key(source):
    return source.document_id, source.source_path


def phrase_in(phrase, text):
    return bool(re.search(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', canonical(text)))


def declared_names(text):
    # Only explicit entity declarations, never arbitrary uppercase headings.
    return {canonical(m.group(1)).replace('_', ' ').replace('-', ' ') for m in DECLARATION.finditer(text)}


def identities(sources):
    groups = defaultdict(list)
    for source in sources: groups[document_key(source)].append(source)
    result = {}
    for key, selected in groups.items():
        filenames = {unquote(s.file_name).replace('\\', '/').rsplit('/', 1)[-1] for s in selected}
        filename_codes = set().union(*(codes(f) for f in filenames))
        names = set().union(*(declared_names(s.text) for s in selected))
        # A standalone reference heading identifies the owner, unlike a body
        # reference such as "compatible with AX123", which names another product.
        heading_codes = set()
        for source in selected:
            headings = list(source.section_path)
            if source.block_type == 'heading' or source.evidence_kind == 'verified_parent':
                headings += [source.text]
            for heading in headings:
                value = canonical(heading).strip()
                if CODE.fullmatch(value) and not STANDARD.match(value): heading_codes.add(value)
        declared_codes = {name for name in names if CODE.fullmatch(name)}
        owners = filename_codes | heading_codes | declared_codes
        result[key] = owners | names
        if len(filenames) != 1 or len(owners) > 1 or len(names - declared_codes) > 1:
            result[key].add('!mixed_product_identity')
    return result


def resolve_targets(question, sources, resolver=None):
    if resolver is not None:
        resolution=resolver.resolve(question)
        if not resolution.safe: raise SemanticSafetyError('product_identity_unresolved')
        catalog={document_key(s): resolver.ownership(s) for s in sources}
        return set(resolution.resolved_product_ids),catalog
    catalog = identities(sources)
    query_codes = codes(question)
    all_names = set().union(*catalog.values()) if catalog else set()
    targets = {name for name in all_names if phrase_in(name, question)}
    if query_codes - targets: raise SemanticSafetyError('product_identity_unresolved')
    # A recognized code must not hide an additional unresolved named target.
    for phrase in re.findall(r'\b[A-ZÀ-ÖØ-Ý]{2,}(?:[ _-]+[A-ZÀ-ÖØ-Ý]{1,}){1,3}\b', question):
        name = canonical(phrase).replace('_', ' ').replace('-', ' ')
        if set(name.split()) <= {'nf','en','iso','iec','din','dtu'}: continue
        if name not in all_names: raise SemanticSafetyError('product_identity_unresolved')
    # Named products need an explicit selected declaration. A filename alone
    # cannot license inferring a family/name/revision alias.
    if not targets: raise SemanticSafetyError('product_identity_unresolved')
    # Prefer the most specific declared name over a nested short alias.
    targets = {t for t in targets if not any(t != other and phrase_in(t, other) for other in targets)}
    return targets, catalog


def check_context(question, sources, resolver=None):
    targets, catalog = resolve_targets(question, sources, resolver)
    if resolver is not None:
        if not targets <= set().union(*catalog.values()):
            raise SemanticSafetyError('unverified_or_incomplete_product_ownership')
    relevant = [s for s in sources if catalog[document_key(s)] & targets]
    if any('!mixed_product_identity' in catalog[document_key(s)] for s in relevant):
        raise SemanticSafetyError('mixed_product_identity')
    # Detect explicit opposing permissions for the same surface/object. No
    # inference from an unrelated heading or hidden source is permitted.
    statements = defaultdict(set)
    measurements = defaultdict(set)
    descriptions = defaultdict(set)
    for source in relevant:
        identity = tuple(sorted(catalog[document_key(source)] & targets))
        body = canonical(source.text)
        for category, pattern in (
            ('welder', r'\b(?:est|is) (?:un |une |a |an )?(?:poste de soudage|soudeuse|welding machine|welder)\b'),
            ('saw_blade', r'\b(?:est|is) (?:un |une |a |an )?(?:lame de scie|saw blade)\b')):
            if re.search(pattern, body): descriptions[identity].add(category)
        for match in re.finditer(r'\b([a-z]+(?: [a-z]+){0,2})\s*:\s*(\d+(?:[.,]\d+)?)\s*(kg|mm|bar|nm|v|w)\b', body):
            measurements[(identity, match[1], match[3])].add(float(match[2].replace(',', '.')))
        for line in canonical(source.text).split('.'):
            match = re.search(r'(ne pas appliquer sur|interdit sur|allowed on|prohibited on|convient pour|ne convient pas pour)\s+(.+)', line)
            if match:
                negative = match[1].startswith(('ne ', 'interdit', 'prohibited'))
                statements[(identity, match[2].strip())].add(negative)
    if any(len(v) > 1 for v in statements.values()): raise SemanticSafetyError('contradictory_permission')
    if any(len(v) > 1 for v in descriptions.values()) or any(len(v) > 1 for v in measurements.values()):
        raise SemanticSafetyError('contradictory_description_or_measurement')
    return targets, catalog


def validate_semantics(claims, sources, question, resolver=None):
    targets, catalog = check_context(question, sources, resolver)
    lookup = {support_id(s): s for s in sources}
    used_targets = set()
    permission = bool(re.search(r'\b(peut|can|may|compatible|convient|allowed|autorise)\b', canonical(question)))
    for claim in claims:
        source = lookup[claim['support_chunk_ids'][0]]
        owned = catalog[document_key(source)] & targets
        if not owned: raise SemanticSafetyError('wrong_target_product')
        used_targets |= owned
        if permission and not re.search(r'ne pas|interdit|non admis|admissible|autorise|convient|destine|uniquement|only|allowed|prohibit|suitable|not suitable', canonical(claim['text'])):
            raise SemanticSafetyError('unqualified_permission')
        if permission:
            question_tail = re.search(r'\b(?:sur|on|avec|with)\s+(.+?)[?.]*$', canonical(question))
            if question_tail:
                objects = set(re.findall(r'[a-z]{3,}', question_tail[1])) - {'les','des','une','the','that','this','for','sans','sur'}
                if objects and not objects & set(re.findall(r'[a-z]{3,}', canonical(claim['text']))):
                    raise SemanticSafetyError('permission_object_not_supported')
    if used_targets != targets: raise SemanticSafetyError('incomplete_target_coverage')
    return claims
