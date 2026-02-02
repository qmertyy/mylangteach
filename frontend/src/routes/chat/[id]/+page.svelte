<script lang="ts">
  import { page } from '$app/stores';
  import { onMount, tick } from 'svelte';
  import { api, type Message, type GrammarDetected, type TranscriptionResponse } from '$lib/api';
  import { messages, currentChatId, chats, error, isLoading } from '$lib/stores';
  import ChatInput from '$lib/components/ChatInput.svelte';
  import ChatMessage from '$lib/components/ChatMessage.svelte';
  import { goto } from '$app/navigation';
  
  let chatContainer: HTMLDivElement;
  let chatData: { title: string; mode: string } | null = null;
  let grammarAlerts: Map<string, GrammarDetected> = new Map();
  let isTranscribing = false;
  let lastTranscription: TranscriptionResponse | null = null;
  
  $: chatId = $page.params.id;
  
  // Watch for chat ID changes
  $: if (chatId) {
    loadChat();
  }
  
  onMount(async () => {
    await loadChat();
  });
  
  async function loadChat() {
    if (!chatId) return;
    
    isLoading.set(true);
    try {
      const data = await api.getChat(chatId);
      chatData = { title: data.chat.title, mode: data.chat.mode };
      messages.set(data.messages);
      currentChatId.set(chatId);
      
      // Parse grammar alerts from message metadata
      const alerts = new Map<string, GrammarDetected>();
      data.messages.forEach(msg => {
        if (msg.metadata) {
          try {
            const meta = JSON.parse(msg.metadata);
            if (meta.grammar_detected) {
              alerts.set(msg.id, meta.grammar_detected);
            }
          } catch {}
        }
      });
      grammarAlerts = alerts;
      
      // Scroll to bottom
      await tick();
      scrollToBottom();
    } catch (e: any) {
      error.set(e.message);
    } finally {
      isLoading.set(false);
    }
  }
  
  async function sendMessage(content: string) {
    if (!chatId) return;
    
    isLoading.set(true);
    try {
      const response = await api.sendMessage(chatId, content);
      
      // Add messages to store
      messages.update(m => [...m, response.user_message, response.assistant_message]);
      
      // Handle grammar detection
      if (response.assistant_message.grammar_detected) {
        grammarAlerts = new Map(grammarAlerts).set(
          response.assistant_message.id,
          response.assistant_message.grammar_detected
        );
      }
      
      // Scroll to bottom
      await tick();
      scrollToBottom();
    } catch (e: any) {
      error.set(e.message);
    } finally {
      isLoading.set(false);
    }
  }
  
  async function sendAudioMessage(audioBlob: Blob) {
    if (!chatId) return;
    
    isLoading.set(true);
    isTranscribing = true;
    lastTranscription = null;
    
    try {
      // Use the combined transcribe-and-send endpoint
      const response = await api.transcribeAndSend(audioBlob, chatId);
      
      // Store transcription info to show correction
      lastTranscription = response.transcription;
      
      // Add messages to store
      messages.update(m => [...m, response.chat_response.user_message, response.chat_response.assistant_message]);
      
      // Handle grammar detection
      if (response.chat_response.assistant_message.grammar_detected) {
        grammarAlerts = new Map(grammarAlerts).set(
          response.chat_response.assistant_message.id,
          response.chat_response.assistant_message.grammar_detected
        );
      }
      
      // Scroll to bottom
      await tick();
      scrollToBottom();
      
      // Clear transcription info after 10 seconds
      setTimeout(() => {
        lastTranscription = null;
      }, 10000);
      
    } catch (e: any) {
      error.set(e.message);
    } finally {
      isLoading.set(false);
      isTranscribing = false;
    }
  }
  
  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }
  
  async function handleLearnGrammar(ruleName: string, explanation: string) {
    try {
      const result = await api.createGrammarRule(ruleName, explanation, chatId);
      goto(`/chat/${result.chat_id}`);
    } catch (e: any) {
      error.set(e.message);
    }
  }
  
  async function deleteChat() {
    if (!chatId || !confirm('Are you sure you want to delete this chat?')) return;
    
    try {
      await api.deleteChat(chatId);
      chats.update(c => c.filter(chat => chat.id !== chatId));
      goto('/');
    } catch (e: any) {
      error.set(e.message);
    }
  }
  
  function getModeIcon(mode: string): string {
    switch (mode) {
      case 'free_talk': return '💬';
      case 'grammar': return '📖';
      case 'document': return '📄';
      default: return '💬';
    }
  }
  
  function getModeLabel(mode: string): string {
    switch (mode) {
      case 'free_talk': return 'Free Talk';
      case 'grammar': return 'Grammar';
      case 'document': return 'Document';
      default: return 'Chat';
    }
  }
  
  function getPlaceholder(): string {
    if (!chatData) return "Type your message...";
    if (chatData.mode === 'grammar') return "Ask about this grammar rule...";
    if (chatData.mode === 'document') return "Answer questions or ask about the document...";
    return "Type your message...";
  }
</script>

<div class="flex flex-col h-screen">
  <!-- Header -->
  <header class="bg-white border-b border-ink-200 px-6 py-4 flex items-center justify-between">
    <div class="flex items-center gap-4">
      <button on:click={() => goto('/')} class="btn-icon">
        <svg class="w-5 h-5 text-ink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      
      {#if chatData}
        <div class="flex items-center gap-3">
          <span class="text-2xl">{getModeIcon(chatData.mode)}</span>
          <div>
            <h1 class="font-display text-lg font-semibold text-ink-800">{chatData.title}</h1>
            <p class="text-sm text-ink-500">{getModeLabel(chatData.mode)} Mode</p>
          </div>
        </div>
      {/if}
    </div>
    
    <div class="flex items-center gap-2">
      <button on:click={deleteChat} class="btn-ghost text-coral-600 hover:bg-coral-50">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  </header>
  
  <!-- Messages -->
  <div 
    bind:this={chatContainer}
    class="flex-1 overflow-y-auto custom-scrollbar p-6"
  >
    <div class="max-w-3xl mx-auto space-y-6">
      {#if $messages.length === 0 && !$isLoading && !isTranscribing}
        <!-- Empty state -->
        <div class="text-center py-12 animate-fade-in">
          <span class="text-6xl mb-4 block">{chatData ? getModeIcon(chatData.mode) : '💬'}</span>
          <h2 class="font-display text-xl font-semibold text-ink-700 mb-2">
            {#if chatData?.mode === 'free_talk'}
              Let's start a conversation!
            {:else if chatData?.mode === 'grammar'}
              Ready to learn some grammar?
            {:else if chatData?.mode === 'document'}
              Let's explore this document together!
            {:else}
              Start the conversation
            {/if}
          </h2>
          <p class="text-ink-500 mb-4">
            {#if chatData?.mode === 'free_talk'}
              Type or use the 🎤 microphone to begin chatting about {chatData?.title || 'any topic'}
            {:else if chatData?.mode === 'grammar'}
              Ask about "{chatData?.title}" or type to get started
            {:else if chatData?.mode === 'document'}
              I'll quiz you on vocabulary and sentence structures from your document
            {:else}
              Send a message to get started
            {/if}
          </p>
          <div class="flex items-center justify-center gap-2 text-sm text-ink-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            <span>Voice messages are transcribed automatically</span>
          </div>
        </div>
      {:else}
        {#each $messages as message (message.id)}
          <ChatMessage 
            {message} 
            grammarDetected={grammarAlerts.get(message.id) || null}
            onLearnGrammar={chatData?.mode === 'free_talk' ? handleLearnGrammar : undefined}
          />
        {/each}
        
        {#if $isLoading || isTranscribing}
          <div class="flex justify-start">
            <div class="chat-bubble-assistant">
              <div class="flex items-center gap-2">
                {#if isTranscribing}
                  <span class="text-sm text-ink-500">Transcribing audio...</span>
                {/if}
                <div class="w-2 h-2 bg-sage-400 rounded-full animate-bounce-light"></div>
                <div class="w-2 h-2 bg-sage-400 rounded-full animate-bounce-light" style="animation-delay: 0.1s"></div>
                <div class="w-2 h-2 bg-sage-400 rounded-full animate-bounce-light" style="animation-delay: 0.2s"></div>
              </div>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </div>
  
  <!-- Input -->
  <ChatInput 
    onSend={sendMessage}
    onAudioSend={sendAudioMessage}
    disabled={$isLoading || isTranscribing}
    placeholder={getPlaceholder()}
  />
  
  <!-- Transcription correction info -->
  {#if lastTranscription && lastTranscription.was_corrected}
    <div class="bg-amber-50 border-t border-amber-200 px-4 py-3">
      <div class="max-w-3xl mx-auto">
        <div class="flex items-start gap-3">
          <span class="text-lg">✨</span>
          <div class="flex-1 text-sm">
            <p class="text-amber-800 font-medium">Transcription corrected by LLM</p>
            <p class="text-amber-700 mt-1">
              <span class="line-through opacity-60">{lastTranscription.original_text}</span>
              <span class="mx-2">→</span>
              <span class="font-medium">{lastTranscription.text}</span>
            </p>
          </div>
          <button 
            on:click={() => lastTranscription = null}
            class="text-amber-600 hover:text-amber-800 p-1"
            aria-label="Dismiss"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>
