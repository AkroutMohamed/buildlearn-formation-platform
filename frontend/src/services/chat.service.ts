import type { ChatMessage, ChatRequest, ChatResponse, Conversation } from "@/types/chat";
import { apiRequest } from "@/services/api-client";

export const chat = {
  send: (data: ChatRequest) =>
    apiRequest<ChatResponse>("/ai/chat", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  conversations: () =>
    apiRequest<Conversation[]>("/ai/conversations"),

  getConversation: (id: string) =>
    apiRequest<Conversation>(`/ai/conversations/${id}`),

  messages: (conversationId: string) =>
    apiRequest<ChatMessage[]>(`/ai/conversations/${conversationId}/messages`),

  deleteConversation: (conversationId: string) =>
    apiRequest<void>(`/ai/conversations/${conversationId}`, {
      method: "DELETE",
    }),
};
