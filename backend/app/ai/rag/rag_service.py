import logging
from datetime import datetime, timezone
from uuid import uuid4

from app.ai.llm.base import BaseLLMProvider
from app.ai.llm.ollama import OllamaProvider
from app.ai.rag.context_builder import ContextBuilder
from app.ai.rag.pipeline import BaseRAGPipeline
from app.ai.retrieval.retriever import BaseRetriever
from app.ai.rag.retriever import Retriever
from app.ai.schemas.chat import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)


class RAGService(BaseRAGPipeline):
    def __init__(
        self,
        retriever: BaseRetriever | None = None,
        llm_provider: BaseLLMProvider | None = None,
    ) -> None:
        self._retriever: BaseRetriever = retriever or Retriever()
        self._llm_provider: BaseLLMProvider = llm_provider or OllamaProvider()
        self._context_builder: ContextBuilder = ContextBuilder()

    def run(self, request: ChatRequest, history: list[dict[str, str]] | None = None) -> ChatResponse:
        if not request.question or not request.question.strip():
            raise ValueError("Question must not be empty")

        top_k = request.top_k or 5

        try:
            chunks = self._retriever.retrieve(request.question, top_k=top_k)
        except Exception as exc:
            logger.error("Retrieval failed: %s", exc)
            raise RuntimeError(f"Retrieval failed: {exc}") from exc

        built = self._context_builder.build(chunks)

        conversation_id = request.conversation_id or str(uuid4())
        now = datetime.now(timezone.utc)

        if not built.context:
            logger.info("No context available for question: %s", request.question)
            return ChatResponse(
                answer=(
                    "The information was not found in the available documentation. "
                    "Please provide a question about a specific product for which "
                    "documentation has been indexed."
                ),
                sources=[],
                conversation_id=conversation_id,
                created_at=now,
            )

        try:
            response = self._llm_provider.generate(request, built.context, history=history)
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            raise RuntimeError(f"LLM generation failed: {exc}") from exc

        response.sources = built.sources
        response.conversation_id = conversation_id
        return response
