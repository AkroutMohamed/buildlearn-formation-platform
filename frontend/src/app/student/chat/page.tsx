"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { chat } from "@/services/chat.service";
import type { ChatMessage, ChatSource, Conversation } from "@/types/chat";
import { sanitizeUrl } from "@/lib/sanitizeUrl.mjs";
import { Button } from "@/components/ui/Button";
import EmptyState from "@/components/ui/EmptyState";

function SourceCard({ source }: { source: ChatSource }) {
  const documentHref = sanitizeUrl(source.document_url);
  const sourceHref = sanitizeUrl(source.source_url);
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700">
      {source.product_name && (
        <p className="font-semibold text-slate-900">{source.product_name}</p>
      )}
      {source.supplier && <p>Supplier: {source.supplier}</p>}
      {documentHref && (
        <a
          href={documentHref}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[#b91c27] hover:underline"
        >
          Document
        </a>
      )}
      {sourceHref && sourceHref !== documentHref && (
        <a
          href={sourceHref}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-2 text-[#b91c27] hover:underline"
        >
          Source
        </a>
      )}
      <div className="mt-1 flex flex-wrap gap-2 text-slate-500">
        {source.confidence && <span>Confidence: {source.confidence}</span>}
        {typeof source.score === "number" && (
          <span>Relevance: {(source.score * 100).toFixed(0)}%</span>
        )}
        {source.domain && <span>Domain: {source.domain}</span>}
      </div>
    </div>
  );
}

export default function StudentChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    chat.conversations().then(setConversations).catch(() => undefined);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const loadConversation = async (conversationId: string) => {
    setError(null);
    setActiveConversationId(conversationId);
    try {
      const msgs = await chat.messages(conversationId);
      setMessages(msgs);
    } catch {
      setError("Unable to load messages.");
    }
  };

  const startNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
    setError(null);
    inputRef.current?.focus();
  };

  const send = async () => {
    const trimmed = question.trim();
    if (!trimmed || sending) return;

    setSending(true);
    setError(null);

    const optimisticUserMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      conversation_id: activeConversationId || "",
      role: "user",
      content: trimmed,
      sources: [],
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, optimisticUserMessage]);
    setQuestion("");

    const history = messages
      .filter((m) => m.role === "user" || m.role === "assistant")
      .map((m) => ({ role: m.role, content: m.content }));

    try {
      const response = await chat.send({
        question: trimmed,
        conversation_id: activeConversationId || undefined,
        messages: history,
      });

      const assistantMessage: ChatMessage = {
        id: `temp-${Date.now()}-assistant`,
        conversation_id: response.conversation_id,
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        created_at: response.created_at,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setActiveConversationId(response.conversation_id);

      setConversations((prev) => {
        const exists = prev.find((c) => c.id === response.conversation_id);
        if (exists) {
          return prev.map((c) =>
            c.id === response.conversation_id
              ? { ...c, updated_at: new Date().toISOString() }
              : c,
          );
        }
        return [
          {
            id: response.conversation_id,
            user_id: "",
            title: trimmed.length > 60 ? trimmed.slice(0, 57) + "..." : trimmed,
            created_at: response.created_at,
            updated_at: response.created_at,
          },
          ...prev,
        ];
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setMessages((prev) => prev.filter((m) => !m.id.startsWith("temp-")));
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  };

  const deleteConversation = async (conversationId: string) => {
    await chat.deleteConversation(conversationId);
    setConversations((prev) => prev.filter((c) => c.id !== conversationId));
    if (activeConversationId === conversationId) {
      setActiveConversationId(null);
      setMessages([]);
    }
  };

  const activeConversation = useMemo(
    () => conversations.find((c) => c.id === activeConversationId) || null,
    [conversations, activeConversationId],
  );

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-7xl gap-4">
      <aside className="hidden w-72 shrink-0 overflow-y-auto rounded-xl border border-slate-200 bg-white p-4 md:block">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500">
            Conversations
          </h2>
          <Button variant="secondary" size="sm" onClick={startNewConversation}>
            New
          </Button>
        </div>
        <div className="mt-3 space-y-1">
          {conversations.length === 0 && (
            <p className="px-2 text-xs text-slate-500">No conversations yet.</p>
          )}
          {conversations.map((c) => (
            <div
              key={c.id}
              role="button"
              tabIndex={0}
              aria-current={activeConversationId === c.id ? "true" : undefined}
              onClick={() => loadConversation(c.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  loadConversation(c.id);
                }
              }}
              className={`flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-sm transition ${
                activeConversationId === c.id
                  ? "bg-red-50 text-[#b91c27]"
                  : "text-slate-700 hover:bg-slate-50"
              }`}
            >
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  loadConversation(c.id);
                }}
                className="min-w-0 flex-1 truncate text-left"
              >
                {c.title || "New conversation"}
              </button>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  deleteConversation(c.id);
                }}
                className="ml-2 shrink-0 text-slate-400 hover:text-red-600"
                aria-label="Delete conversation"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </aside>

      <section className="flex flex-1 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white">
        <header className="flex items-center justify-between border-b border-slate-200 px-5 py-3">
          <div>
            <h1 className="text-base font-semibold text-slate-900">
              {activeConversation ? activeConversation.title : "AI Assistant"}
            </h1>
            <p className="text-xs text-slate-500">
              Ask questions about indexed BuildLearn documentation.
            </p>
          </div>
          {activeConversationId && (
            <Button variant="ghost" size="sm" onClick={startNewConversation}>
              New chat
            </Button>
          )}
        </header>

        <div className="flex-1 overflow-y-auto px-5 py-4">
          {messages.length === 0 && !activeConversationId && (
            <EmptyState
              title="Start a conversation"
              message="Ask a question about a product or technical document to get a grounded answer with sources."
              icon={<span>💬</span>}
              action={
                <Link
                  href="/formations"
                  className="inline-flex items-center justify-center rounded-lg bg-[#d81f2a] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#b91c27]"
                >
                  Browse courses
                </Link>
              }
            />
          )}

          {messages.length === 0 && activeConversationId && (
            <EmptyState
              title="Ask a question"
              message="Type your question below to get started with this conversation."
              icon={<span>💬</span>}
            />
          )}

          <div className="space-y-4">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-2xl rounded-2xl px-4 py-3 ${
                    m.role === "user"
                      ? "bg-[#d81f2a] text-white"
                      : "border border-slate-200 bg-slate-50 text-slate-800"
                  }`}
                >
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
                  {m.role === "assistant" && m.sources.length > 0 && (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-xs font-semibold text-slate-600 hover:text-[#b91c27]">
                        Show sources
                      </summary>
                      <div className="mt-2 grid gap-2">
                        {m.sources.map((source, idx) => (
                          <SourceCard key={idx} source={source} />
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {sending && (
            <div className="mt-4 flex justify-start">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
                Thinking...
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4">
              <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
                {error}
              </p>
            </div>
          )}
        </div>

        <form
          className="flex items-center gap-3 border-t border-slate-200 px-5 py-3"
          onSubmit={(e) => {
            e.preventDefault();
            send();
          }}
        >
          <input
            ref={inputRef}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about a product or technical document..."
            disabled={sending}
            className="flex-1 rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm shadow-sm focus:border-[#d81f2a] focus:outline-none disabled:cursor-not-allowed disabled:opacity-60"
          />
          <Button type="submit" loading={sending} disabled={!question.trim()}>
            Send
          </Button>
        </form>
      </section>
    </div>
  );
}
