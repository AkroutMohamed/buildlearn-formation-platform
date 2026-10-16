"""Default-on student chat adapter; preserves the RAG V2 validation pipeline."""
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import lru_cache
import json
import logging
import os
import sys
from threading import Lock
from time import perf_counter
from uuid import uuid4
from urllib.parse import unquote

from pydantic import PrivateAttr

from app.ai.schemas.chat import ChatResponse

logger = logging.getLogger(__name__)


def rag_v2_enabled():
    # Student chat defaults to V2; explicit false restores the legacy path.
    return os.environ.get("RAG_V2_ENABLED", "true").strip().lower() == "true"


class V2ChatResponse(ChatResponse):
    # PrivateAttr is neither an API field nor part of model_dump().
    _rag_v2_provenance: dict = PrivateAttr(default_factory=dict)


class _TimedCall:
    def __init__(self, target, method, stage, metrics):
        self.target, self.method, self.stage, self.metrics = target, method, stage, metrics

    def __getattr__(self, name):
        if name != self.method:
            return getattr(self.target, name)

        def call(*args, **kwargs):
            started = perf_counter()
            try:
                result = getattr(self.target, name)(*args, **kwargs)
                if self.stage == "retrieval":
                    self.metrics["retrieved_sources"] = len(result.hits)
                return result
            except Exception:
                self.metrics["technical_failure"] = self.stage + "_failed"
                raise
            finally:
                self.metrics[self.stage + "_duration_ms"] += (perf_counter() - started) * 1000
        return call


@contextmanager
def _observe_validation(metrics):
    """Thread-local call timing: no monkeypatch of the shared validator/module.

    FastAPI executes this synchronous service on one worker thread. Preserve and
    restore an existing profiler, including on exceptions and early abstention.
    """
    from app.ai.rag.answer_validation_v2 import validate_claims
    previous = sys.getprofile()
    starts = {}

    def profile(frame, event, arg):
        if frame.f_code is validate_claims.__code__:
            if event == "call":
                starts[id(frame)] = perf_counter()
            elif event == "return":
                started = starts.pop(id(frame), None)
                if started is not None:
                    metrics["validation_duration_ms"] += (perf_counter() - started) * 1000
        if previous is not None:
            previous(frame, event, arg)

    sys.setprofile(profile)
    try:
        yield
    finally:
        sys.setprofile(previous)


def _rejection_reason(warnings):
    # Only controlled enums go into logs/storage, not model output or queries.
    for warning in warnings:
        if warning.startswith('Semantic safety rejected: '):
            code=warning.removeprefix('Semantic safety rejected: ')
            if code in {'requested_fact_mismatch','incomplete_requested_fact_coverage'}:
                return code
        if not warning.startswith("Generation or grounding validation failed:"):
            continue
        if any(term in warning for term in ("JSONDecodeError", "Malformed", "requires bounded", "cannot contain claims", "must not contain claims")):
            return "malformed_model_output"
        if "ValueError:" not in warning:
            return "validator_failed"
        for term, code in (
            ("explicitly allowed", "support_not_allowed"),
            ("ambiguous allowed support", "ambiguous_support_id"),
            ("identity is ambiguous", "ambiguous_product"),
            ("polarity", "missing_compatibility_qualifier"),
            ("not an extract", "unsupported_claim"),
            ("quote", "quote_mismatch"),
            ("Heading alone", "heading_only"),
        ):
            if term in warning:
                return code
        return "validation_rejected"
    return None


def _abstention_reason(result, rejection):
    if result.retrieval_metadata.get('conversation_reason'):
        return result.retrieval_metadata['conversation_reason']
    if rejection:
        return rejection
    if any(w.startswith("Unknown or malformed product reference:") for w in result.warnings):
        return "unknown_or_malformed_reference"
    if not result.sources:
        return "no_usable_context"
    if any(w.startswith("No usable, word-relevant") for w in result.warnings):
        return "no_relevant_evidence"
    return "insufficient_or_ambiguous_evidence"


def public_sources(result):
    """Expose citations only; no paths, internal warnings, prompts, or raw text."""
    from app.ai.rag.answer_validation_v2 import support_id
    cited = {claim["source_id"] for claim in result.claims}
    mapped = []
    for source in result.sources:
        if source.source_id not in cited:
            continue
        # Defense against malformed filename metadata carrying a path.
        filename = unquote(source.file_name).replace("\\", "/").rsplit("/", 1)[-1]
        mapped.append(dict(
            source_id=source.source_id, chunk_id=source.chunk_id,
            support_chunk_id=support_id(source), document_id=source.document_id,
            file_name=filename, product_name=f"{source.source_id}: {filename}",
            page_start=source.page_start, page_end=source.page_end,
            evidence_kind=source.evidence_kind,
        ))
    return mapped


def stored_sources(response):
    audit = getattr(response, "_rag_v2_provenance", None)
    if audit is not None:
        return json.dumps(dict(format="rag_v2", sources=response.sources, provenance=audit))
    # Preserve the legacy persisted representation exactly.
    return json.dumps(response.sources) if response.sources else None


def student_sources(decoded):
    if isinstance(decoded, dict) and decoded.get("format") == "rag_v2":
        return decoded["sources"]
    return decoded


def _create_service():
    from app.ai.rag.hierarchical_rag_v2 import HierarchicalRAGV2, RAGV2Config
    from app.ai.config import ai_settings
    from app.ai.api.rag_v2_runtime import RuntimeRetrievalV2, local_transport_url
    from app.ai.embeddings.ollama_provider import OllamaEmbeddingProvider
    from app.ai.embeddings.service import EmbeddingService
    from app.ai.rag.product_identity import ProductIdentityResolver
    from qdrant_client import QdrantClient
    if (ai_settings.embedding_provider not in ('', 'ollama') or
            ai_settings.embedding_model not in ('', 'nomic-embed-text') or
            not ai_settings.embedding_normalize):
        raise ValueError('Hierarchical retrieval requires normalized Ollama/nomic-embed-text')
    # Installed model used in the validated evaluations. No fallback/download.
    config = RAGV2Config(model=os.environ.get("RAG_V2_OLLAMA_MODEL", "qwen2.5-coder:7b"),
                         base_url=local_transport_url(ai_settings.ollama_base_url))
    embeddings = EmbeddingService(provider=OllamaEmbeddingProvider(
        base_url=config.base_url, model='nomic-embed-text', normalize=True))
    identities = ProductIdentityResolver.load()
    retriever = RuntimeRetrievalV2(client=QdrantClient(url=local_transport_url(ai_settings.qdrant_url)),
                                 embeddings=embeddings, identity_resolver=identities)
    return HierarchicalRAGV2(config=config, retriever=retriever,
                             identity_resolver=identities)


class RAGV2ChatAdapter:
    def __init__(self, service_factory=None):
        self._factory = service_factory or _create_service
        self._service = None
        self._lock = Lock()

    def _get_service(self):
        with self._lock:
            if self._service is None:
                self._service = self._factory()
            return self._service

    def run(self, request, history=None):
        from app.ai.rag.hierarchical_rag_v2 import HierarchicalRAGV2, RAGV2Response
        from app.ai.rag.conversation_context_v2 import resolve_followup
        from app.ai.rag.answer_validation_v2 import support_id
        started = perf_counter()
        metrics = dict(request_id=str(uuid4()), retrieval_duration_ms=0.0,
                       generation_duration_ms=0.0, validation_duration_ms=0.0,
                       total_duration_ms=0.0, outcome="technical_failure",
                       retrieved_sources=0, supplied_sources=0, accepted_claims=0,
                       validation_rejection_reason=None, technical_failure=None)
        try:
            try:
                service = self._get_service()
            except Exception:
                metrics["technical_failure"] = "initialization_failed"
                raise RuntimeError("The AI answer service is temporarily unavailable. Please try again later.") from None
            if not request.question.strip() or len(request.question) > service.config.max_question_chars:
                metrics["outcome"] = "invalid_request"
                raise ValueError(f"V2 questions must contain 1 to {service.config.max_question_chars} characters.")
            # Per-request observers preserve the shared retriever, config and
            # generator. History/top_k remain accepted API fields but do not
            # change validated top-three evidence selection or its prompt.
            observed = HierarchicalRAGV2(config=service.config,
                retriever=_TimedCall(service.retriever, "retrieve", "retrieval", metrics),
                llm=_TimedCall(service.llm, "generate_grounded", "generation", metrics),
                identity_resolver=service.identity_resolver)
            try:
                with _observe_validation(metrics):
                    conversation_query = resolve_followup(request.question, history, service.identity_resolver, request.conversation_id)
                    if conversation_query.reason:
                        french = not any(word in request.question.lower().split() for word in ('its','this','that','and','what','how'))
                        clarification = "De quel produit parlez-vous ? Précisez son nom ou sa référence pour que je puisse vérifier les documents." if french else "Which product do you mean? Please give its name or reference so I can check the documents."
                        result = RAGV2Response(clarification, False, request.question, [], [], service.config.model,
                                               dict(conversation_reason=conversation_query.reason))
                    else:
                        if len(conversation_query.question) > service.config.max_question_chars:
                            raise ValueError("Follow-up question exceeds configured budget")
                        result = observed.run(conversation_query.question)
                    result.retrieval_metadata['conversation_product_ids'] = list(conversation_query.product_ids)
            except Exception:
                metrics["technical_failure"] = metrics["technical_failure"] or "pipeline_failed"
                raise RuntimeError("The AI answer service is temporarily unavailable. Please try again later.") from None
            metrics["supplied_sources"] = len(result.sources)
            rejection = _rejection_reason(result.warnings)
            metrics["validation_rejection_reason"] = rejection
            # RAG V2 intentionally catches provider exceptions as refusals.
            # The observer distinguishes those from factual insufficiency.
            if metrics["technical_failure"] or rejection in {"malformed_model_output", "validator_failed"}:
                metrics["technical_failure"] = metrics["technical_failure"] or "invalid_model_response"
                raise RuntimeError("The AI answer service is temporarily unavailable. Please try again later.") from None
            metrics["outcome"] = "answered" if result.grounded else "abstained"
            metrics["accepted_claims"] = len(result.claims)
            response = V2ChatResponse(answer=result.answer, sources=public_sources(result),
                conversation_id=request.conversation_id or str(uuid4()), created_at=datetime.now(timezone.utc))
            response._rag_v2_provenance = dict(request_id=metrics["request_id"], status=result.status,
                abstention_reason=None if result.grounded else _abstention_reason(result, rejection),
                requested_facts=result.retrieval_metadata.get('requested_facts',[]),
                missing_context_facts=result.retrieval_metadata.get('missing_context_facts',[]),
                conversation_product_ids=result.retrieval_metadata.get('conversation_product_ids',[]),
                conversation_reason=result.retrieval_metadata.get('conversation_reason'),
                citations=result.claims, sources=[dict(source_id=s.source_id, chunk_id=s.chunk_id,
                    support_chunk_id=support_id(s), document_id=s.document_id,
                    file_name=s.file_name, page_start=s.page_start, page_end=s.page_end,
                    score=s.score, provenance=s.provenance) for s in result.sources])
            return response
        finally:
            metrics["total_duration_ms"] = (perf_counter() - started) * 1000
            if 'response' in locals():
                response._rag_v2_provenance["telemetry"] = dict(metrics)
            logger.info("rag_v2_request %s", json.dumps(metrics, sort_keys=True))


@lru_cache(maxsize=1)
def get_rag_v2_service():
    return RAGV2ChatAdapter()
