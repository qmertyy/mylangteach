const API_BASE = 'http://localhost:8000';

export interface Category {
  id: string;
  name: string;
  type: 'topic' | 'grammar' | 'document';
  created_at: string;
  metadata?: string;
}

export interface Chat {
  id: string;
  category_id: string | null;
  title: string;
  mode: 'free_talk' | 'grammar' | 'document';
  created_at: string;
  updated_at: string;
  metadata?: string;
}

export interface Message {
  id: string;
  chat_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  metadata?: string;
}

export interface Document {
  id: string;
  filename: string;
  content?: string;
  extracted_words?: string[];
  extracted_sentences?: string[];
  created_at: string;
}

export interface GrammarRule {
  id: string;
  name: string;
  description?: string;
  examples?: string;
  chat_id?: string;
  created_at: string;
}

export interface LLMConfig {
  provider: 'ollama' | 'openai' | 'anthropic' | 'gemini';
  model: string;
  base_url: string;
  api_key?: string;
  has_api_key?: boolean;
}

export interface GrammarDetected {
  rule_name: string;
  explanation: string;
}

export interface ChatResponse {
  user_message: Message;
  assistant_message: Message & { grammar_detected?: GrammarDetected };
}

export interface TranscriptionResponse {
  text: string;
  original_text: string;
  language?: string;
  confidence?: number;
  was_corrected: boolean;
}

export interface TranscribeAndSendResponse {
  transcription: TranscriptionResponse;
  chat_response: ChatResponse;
}

class ApiClient {
  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error ${response.status}`);
    }
    
    return response.json();
  }

  // Config
  async getConfig(): Promise<{ llm: LLMConfig; whisper: any }> {
    return this.fetch('/api/config');
  }

  async updateConfig(config: LLMConfig): Promise<{ status: string; config: LLMConfig }> {
    return this.fetch('/api/config', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  // Categories
  async getCategories(type?: string): Promise<Category[]> {
    const query = type ? `?type=${type}` : '';
    return this.fetch(`/api/categories${query}`);
  }

  async createCategory(name: string, type: 'topic' | 'grammar' | 'document'): Promise<Category> {
    return this.fetch('/api/categories', {
      method: 'POST',
      body: JSON.stringify({ name, type }),
    });
  }

  async deleteCategory(id: string): Promise<void> {
    return this.fetch(`/api/categories/${id}`, { method: 'DELETE' });
  }

  // Chats
  async getChats(mode?: string, categoryId?: string): Promise<Chat[]> {
    const params = new URLSearchParams();
    if (mode) params.append('mode', mode);
    if (categoryId) params.append('category_id', categoryId);
    const query = params.toString() ? `?${params}` : '';
    return this.fetch(`/api/chats${query}`);
  }

  async createChat(title: string, mode: 'free_talk' | 'grammar' | 'document', categoryId?: string, documentId?: string): Promise<Chat> {
    return this.fetch('/api/chats', {
      method: 'POST',
      body: JSON.stringify({ title, mode, category_id: categoryId, document_id: documentId }),
    });
  }

  async getChat(id: string): Promise<{ chat: Chat; messages: Message[] }> {
    return this.fetch(`/api/chats/${id}`);
  }

  async deleteChat(id: string): Promise<void> {
    return this.fetch(`/api/chats/${id}`, { method: 'DELETE' });
  }

  // Messages
  async sendMessage(chatId: string, content: string, detectGrammar = true): Promise<ChatResponse> {
    return this.fetch(`/api/chats/${chatId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ chat_id: chatId, content, detect_grammar: detectGrammar }),
    });
  }

  // Audio transcription
  async transcribeAudio(audioBlob: Blob, language?: string): Promise<TranscriptionResponse> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    if (language) {
      formData.append('language', language);
    }
    
    const response = await fetch(`${API_BASE}/api/audio/transcribe`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Transcription failed' }));
      throw new Error(error.detail);
    }
    
    return response.json();
  }

  async transcribeAndSend(
    audioBlob: Blob, 
    chatId: string, 
    language?: string,
    detectGrammar = true
  ): Promise<TranscribeAndSendResponse> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('chat_id', chatId);
    formData.append('detect_grammar', String(detectGrammar));
    if (language) {
      formData.append('language', language);
    }
    
    const response = await fetch(`${API_BASE}/api/audio/transcribe-and-send`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to process audio' }));
      throw new Error(error.detail);
    }
    
    return response.json();
  }

  // Documents
  async getDocuments(): Promise<Document[]> {
    return this.fetch('/api/documents');
  }

  async uploadDocument(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail);
    }
    
    return response.json();
  }

  async getDocument(id: string): Promise<Document> {
    return this.fetch(`/api/documents/${id}`);
  }

  async deleteDocument(id: string): Promise<void> {
    return this.fetch(`/api/documents/${id}`, { method: 'DELETE' });
  }

  // Grammar Rules
  async getGrammarRules(): Promise<GrammarRule[]> {
    return this.fetch('/api/grammar-rules');
  }

  async createGrammarRule(ruleName: string, description?: string, fromChatId?: string): Promise<{ rule_id: string; chat_id: string; category_id: string }> {
    const params = new URLSearchParams({ rule_name: ruleName });
    if (description) params.append('description', description);
    if (fromChatId) params.append('from_chat_id', fromChatId);
    return this.fetch(`/api/grammar-rules?${params}`, { method: 'POST' });
  }

  // Health
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.fetch('/health');
  }
}

export const api = new ApiClient();
