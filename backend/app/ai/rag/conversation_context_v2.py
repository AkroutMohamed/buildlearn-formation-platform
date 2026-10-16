"""Bounded, request-local topic resolution. History supplies identity, never evidence."""
from dataclasses import dataclass
import re

from app.ai.rag.product_identity import normalize


@dataclass(frozen=True)
class ConversationQuery:
    question: str
    reason: str | None = None
    product_ids: tuple[str, ...] = ()


def resolve_followup(question, history, resolver, conversation_id):
    if resolver is None:
        return ConversationQuery(question)
    explicit = resolver.resolve(question)
    if explicit.resolved_product_ids or explicit.unresolved_requested_entities or explicit.ambiguous_candidates:
        return ConversationQuery(question)
    text = normalize(question)
    elliptical = bool(re.search(r"\b(?:sa|son|ses|ce produit|cet appareil|its|this product|that product)\b", text)
                      or re.match(r"^(?:et|and)\b", text)
                      or re.fullmatch(r"(?:consommation|consumption|dimensions|pression|pressure|voltage|puissance|power|epaisseur|thickness|poids|weight)\s*[?]?", text))
    if not elliptical:
        return ConversationQuery(question)
    if not conversation_id:
        return ConversationQuery(question, "missing_conversation_product")
    turns = list(history or [])
    # ChatService persists the current user turn before building history.
    if turns and turns[-1].get("role") == "user" and turns[-1].get("content", "").strip() == question.strip():
        turns.pop()
    for turn in reversed(turns):
        if turn.get("role") != "user":
            continue
        identity = resolver.resolve(turn.get("content", ""))
        if identity.unresolved_requested_entities or identity.ambiguous_candidates:
            return ConversationQuery(question, "ambiguous_conversation_product")
        if identity.resolved_product_ids:
            if not identity.safe or len(identity.resolved_product_ids) != 1:
                return ConversationQuery(question, "ambiguous_conversation_product")
            product_id = identity.resolved_product_ids[0]
            name = resolver.product_name(product_id)
            if not name:
                return ConversationQuery(question, "ambiguous_conversation_product")
            resolved = f"{question.strip()} ({name})"
            check = resolver.resolve(resolved)
            if not check.safe or check.resolved_product_ids != (product_id,):
                return ConversationQuery(question, "ambiguous_conversation_product")
            return ConversationQuery(resolved, product_ids=(product_id,))
    return ConversationQuery(question, "missing_conversation_product")
