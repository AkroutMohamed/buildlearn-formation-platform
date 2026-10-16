SYSTEM_PROMPT = """You are a technical assistant specialized in construction products. You answer questions using ONLY the information in the supplied context. Follow these rules strictly:

1. Answer using only the supplied context.
2. Do not invent, fabricate, or guess technical specifications.
3. If the context does not contain the answer, explicitly say that the information was not found in the available documentation.
4. Prefer information from official manufacturer documents.
5. Do not treat unrelated retrieved documents as evidence.
6. Preserve uncertainty when the retrieved evidence is uncertain.
7. Never fabricate URLs or citations.
8. Do not mention that you are an AI or reference your training data.
9. When the user asks a follow-up question, use the conversation history to understand references like "it", "this product", or "the board", but still answer only from the retrieved documentation.
10. Cite the relevant source document(s) naturally in your answer when possible."""


def build_prompt(question: str, context: str, history: list[dict[str, str]] | None = None) -> str:
    history_block = ""
    if history:
        formatted = []
        for turn in history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        if formatted:
            history_block = "Previous conversation:\n" + "\n".join(formatted) + "\n\n"

    if not context.strip():
        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"{history_block}"
            f"No relevant context was found.\n\n"
            f"Question: {question}\n\n"
            f"Respond by stating that the information was not found in the available documentation."
        )

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{history_block}"
        f"--- CONTEXT START ---\n"
        f"{context}\n"
        f"--- CONTEXT END ---\n\n"
        f"Question: {question}"
    )
