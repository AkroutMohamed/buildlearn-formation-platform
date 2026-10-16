export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatSource {
  product_name?: string;
  supplier?: string;
  document_url?: string;
  source_url?: string;
  domain?: string;
  source_type?: string;
  discovery_provider?: string;
  confidence?: string;
  evidence?: string;
  score?: number;
  chunk_id?: string;
  document_id?: string;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  sources: ChatSource[];
  created_at: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  conversation_id: string;
  created_at: string;
}

export interface ChatRequest {
  question: string;
  conversation_id?: string;
  top_k?: number;
  messages: Array<{ role: string; content: string }>;
}
