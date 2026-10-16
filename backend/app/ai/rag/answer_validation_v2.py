"""Fail-closed, context-scoped extractive answer validation (no retrieval)."""
import json
import re
import unicodedata
from urllib.parse import unquote


def support_id(source):
    return source.parent_id if source.evidence_kind == "verified_parent" else source.chunk_id


def canonical(text):
    """Comparison only; original evidence and rendered quotes remain unchanged.

    Deliberately bounded OCR repair: the corpus's ti glyph, Unicode ligatures,
    accents, apostrophes and whitespace. No token deletion or fuzzy matching.
    """
    # Bullet markers are layout, not semantic tokens. Do not remove list numbers.
    text = re.sub(r"(?m)^\s*•\s*", "", text)
    text = text.replace("Ɵ", "ti").replace("’", "'").replace("‘", "'")
    text = unicodedata.normalize("NFKD", text).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip()


def evidence_lines(text, requested):
    """Recover complete original lines, preserving qualifiers and negation.

    A model excerpt is a selector, never the final answer. Partial-line matches
    expand to the complete original line. Multi-line excerpts stay contiguous.
    """
    needle = canonical(requested).strip().rstrip(".")
    if not needle or len(needle) < 3:
        raise ValueError("Evidence selector too short")
    lines = text.splitlines(keepends=True)
    for length in range(1, len(lines) + 1):
        for start in range(len(lines) - length + 1):
            end = start + length
            original = "".join(lines[start:end]).strip()
            normalized = canonical(original)
            if needle in normalized:
                return original
    raise ValueError("Claim is not an extract from its explicitly selected support")


def validate_claims(raw, sources, question=""):
    data = json.loads(raw)
    if (not isinstance(data, dict) or set(data) != {"status", "claims"}
            or data["status"] not in ("answered", "insufficient")
            or not isinstance(data["claims"], list)):
        raise ValueError("Malformed grounded response schema")
    if data["status"] == "insufficient":
        if data["claims"]:
            raise ValueError("Insufficient response cannot contain claims")
        return []
    if not 1 <= len(data["claims"]) <= 12:
        raise ValueError("Answered response requires bounded claims")
    # An unspecified drill/tool cannot acquire an identity merely because the
    # model picked one of several retrieved product references.
    refs = set()
    for source in sources:
        refs.update(re.findall(r"\b[a-z]{2,8}\d[a-z0-9]{2,11}\b", canonical(unquote(source.file_name))))
    query = canonical(question)
    if (len(refs) > 1 and not any(re.search(r"\b" + re.escape(ref) + r"\b", query) for ref in refs)
            and re.search(r"\b(couple|tension|puissance|vitesse)\b", query)):
        raise ValueError("Product identity is ambiguous for quantitative claims")
    lookup = {}
    for source in sources:
        sid = support_id(source)
        if not sid or sid in lookup:
            raise ValueError("Missing or ambiguous allowed support ID")
        lookup[sid] = source
    validated = []
    for claim in data["claims"]:
        if (not isinstance(claim, dict) or not {"text", "support_chunk_ids"} <= set(claim)
                or set(claim) - {"text", "support_chunk_ids", "quote"}
                or not isinstance(claim["text"], str) or not claim["text"].strip()
                or len(claim["text"]) > 2400):
            raise ValueError("Malformed extractive claim")
        ids = claim["support_chunk_ids"]
        if (not isinstance(ids, list) or len(ids) != 1
                or not isinstance(ids[0], str) or ids[0] not in lookup):
            raise ValueError("Claim support must be one explicitly allowed context ID")
        source = lookup[ids[0]]
        # Never try another source, even if it contains the requested text.
        original = evidence_lines(source.text, claim["text"])
        if "quote" in claim:
            if not isinstance(claim["quote"], str) or not claim["quote"].strip():
                raise ValueError("Malformed optional quote")
            evidence_lines(source.text, claim["quote"])
            if canonical(claim["text"]).rstrip(".") not in canonical(claim["quote"]).rstrip("."):
                raise ValueError("Optional quote does not contain the selected claim")
        if (source.block_type == "heading" or
                re.fullmatch(r"supports? (interdits?|admissibles?)\s*:", canonical(source.text))):
            # Source identity and text have been validated. A heading contains
            # no answer fact; never render it as an independently cited claim.
            continue
        # Unlabelled substrate lists cannot answer permission questions. In
        # particular, DOMAIN D'EMPLOI does not mean that every listed support is
        # allowed. No unseen sibling/heading or alternate product can repair it.
        permission = re.search(r"\b(peut|convient|utilise|compatible|admis|autorise|interdits?|allowed|use)\b|\bquels? supports?|\bsur quelles? surfaces?", query)
        substrate = re.search(r"\b(supports?|surfaces?|substrates?)\b", query)
        if permission and substrate:
            polarity = canonical(source.text)
            if not re.search(r"interdit|admissible|autorise|convient|destine|ne pas|non admis|prohibit|allowed|suitable", polarity):
                raise ValueError("Support compatibility polarity is absent from selected evidence")
            # Keep the prohibition/permission qualifier with its list.
            original = source.text.strip()
        if len(original) > 4000:
            raise ValueError("Original supporting passage exceeds answer budget")
        result = dict(text=original, support_chunk_ids=ids, source_id=source.source_id,
                      quote=original, validation="original_evidence_lines")
        if result not in validated:
            validated.append(result)
    if not validated:
        raise ValueError("Heading alone is not an answer fact")
    return validated
