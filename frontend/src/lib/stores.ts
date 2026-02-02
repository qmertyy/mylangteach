import { writable, derived } from 'svelte/store';
import type { Chat, Message, Category, Document, LLMConfig, GrammarDetected } from './api';

// App state
export const currentMode = writable<'free_talk' | 'grammar' | 'document' | null>(null);
export const currentChatId = writable<string | null>(null);
export const sidebarOpen = writable(true);
export const isLoading = writable(false);
export const error = writable<string | null>(null);

// Data stores
export const chats = writable<Chat[]>([]);
export const messages = writable<Message[]>([]);
export const categories = writable<Category[]>([]);
export const documents = writable<Document[]>([]);
export const llmConfig = writable<LLMConfig | null>(null);

// Grammar detection
export const pendingGrammar = writable<GrammarDetected | null>(null);

// Recording state (for voice input)
export const isRecording = writable(false);

// Derived stores
export const topicChats = derived(chats, ($chats) => 
  $chats.filter(c => c.mode === 'free_talk')
);

export const grammarChats = derived(chats, ($chats) => 
  $chats.filter(c => c.mode === 'grammar')
);

export const documentChats = derived(chats, ($chats) => 
  $chats.filter(c => c.mode === 'document')
);

export const topicCategories = derived(categories, ($categories) =>
  $categories.filter(c => c.type === 'topic')
);

export const grammarCategories = derived(categories, ($categories) =>
  $categories.filter(c => c.type === 'grammar')
);

export const documentCategories = derived(categories, ($categories) =>
  $categories.filter(c => c.type === 'document')
);

// Current chat derived
export const currentChat = derived([chats, currentChatId], ([$chats, $currentChatId]) =>
  $chats.find(c => c.id === $currentChatId) || null
);

// Settings
export const settingsOpen = writable(false);

// Clear error after 5 seconds
error.subscribe(value => {
  if (value) {
    setTimeout(() => error.set(null), 5000);
  }
});
