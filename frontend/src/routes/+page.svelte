<script lang="ts">
  import { currentMode, documents, chats, error } from '$lib/stores';
  import { api } from '$lib/api';
  import { goto } from '$app/navigation';
  
  let newChatTitle = '';
  let selectedDocId = '';
  let creatingChat = false;
  let uploadingDoc = false;
  let fileInput: HTMLInputElement;
  
  const topicSuggestions = [
    'Travel and Vacations',
    'Food and Cooking',
    'Movies and TV Shows',
    'Technology',
    'Sports and Fitness',
    'Music and Art',
    'Daily Routines',
    'Work and Career'
  ];
  
  async function startFreeTalk(topic?: string) {
    creatingChat = true;
    try {
      const title = topic || newChatTitle || 'Free Conversation';
      const chat = await api.createChat(title, 'free_talk');
      chats.update(c => [chat, ...c]);
      goto(`/chat/${chat.id}`);
    } catch (e: any) {
      error.set(e.message);
    } finally {
      creatingChat = false;
    }
  }
  
  async function startGrammarChat() {
    creatingChat = true;
    try {
      const title = newChatTitle || 'Grammar Practice';
      const chat = await api.createChat(title, 'grammar');
      chats.update(c => [chat, ...c]);
      goto(`/chat/${chat.id}`);
    } catch (e: any) {
      error.set(e.message);
    } finally {
      creatingChat = false;
    }
  }
  
  async function startDocumentChat() {
    if (!selectedDocId) {
      error.set('Please select a document first');
      return;
    }
    
    creatingChat = true;
    try {
      const doc = $documents.find(d => d.id === selectedDocId);
      const title = `Learning from: ${doc?.filename || 'Document'}`;
      const chat = await api.createChat(title, 'document', undefined, selectedDocId);
      chats.update(c => [chat, ...c]);
      goto(`/chat/${chat.id}`);
    } catch (e: any) {
      error.set(e.message);
    } finally {
      creatingChat = false;
    }
  }
  
  async function handleFileUpload(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return;
    
    uploadingDoc = true;
    try {
      const doc = await api.uploadDocument(file);
      documents.update(d => [doc, ...d]);
      selectedDocId = doc.id;
    } catch (e: any) {
      error.set(e.message);
    } finally {
      uploadingDoc = false;
      if (fileInput) fileInput.value = '';
    }
  }
  
  function selectMode(mode: 'free_talk' | 'grammar' | 'document') {
    currentMode.set(mode);
  }
  
  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      if ($currentMode === 'free_talk') startFreeTalk();
      else if ($currentMode === 'grammar') startGrammarChat();
    }
  }
</script>

<div class="flex-1 flex items-center justify-center p-8">
  <div class="w-full max-w-4xl">
    <!-- Welcome Header -->
    {#if !$currentMode}
      <div class="text-center mb-12 animate-fade-in">
        <h1 class="font-display text-4xl md:text-5xl font-bold text-ink-800 mb-4">
          Welcome to <span class="text-gradient">Language Teacher</span>
        </h1>
        <p class="text-lg text-ink-600 max-w-2xl mx-auto">
          Your personal AI-powered language learning companion. Practice conversation, 
          master grammar, or learn vocabulary from your own documents.
        </p>
      </div>
      
      <!-- Mode Cards -->
      <div class="grid md:grid-cols-3 gap-6">
        <!-- Free Talk Mode -->
        <button 
          on:click={() => selectMode('free_talk')}
          class="mode-card bg-gradient-to-br from-sage-500 to-sage-700 text-white text-left"
        >
          <div class="text-4xl mb-4">💬</div>
          <h2 class="font-display text-xl font-semibold mb-2">Free Talk</h2>
          <p class="text-sage-100 text-sm">
            Have natural conversations on any topic. I'll help you practice and point out grammar tips along the way.
          </p>
          <div class="absolute top-4 right-4 opacity-20 text-6xl">💬</div>
        </button>
        
        <!-- Grammar Mode -->
        <button 
          on:click={() => selectMode('grammar')}
          class="mode-card bg-gradient-to-br from-amber-500 to-amber-700 text-white text-left"
        >
          <div class="text-4xl mb-4">📖</div>
          <h2 class="font-display text-xl font-semibold mb-2">Grammar</h2>
          <p class="text-amber-100 text-sm">
            Focus on specific grammar rules with explanations, examples, and practice exercises.
          </p>
          <div class="absolute top-4 right-4 opacity-20 text-6xl">📖</div>
        </button>
        
        <!-- Document Mode -->
        <button 
          on:click={() => selectMode('document')}
          class="mode-card bg-gradient-to-br from-coral-500 to-coral-700 text-white text-left"
        >
          <div class="text-4xl mb-4">📄</div>
          <h2 class="font-display text-xl font-semibold mb-2">Document</h2>
          <p class="text-coral-100 text-sm">
            Upload a PDF, image, or text file. I'll create lessons using the vocabulary and structures within.
          </p>
          <div class="absolute top-4 right-4 opacity-20 text-6xl">📄</div>
        </button>
      </div>
    {/if}
    
    <!-- Free Talk Setup -->
    {#if $currentMode === 'free_talk'}
      <div class="animate-slide-up">
        <button on:click={() => currentMode.set(null)} class="btn-ghost mb-6 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        <div class="bg-white rounded-2xl p-8 shadow-sm border border-ink-100">
          <div class="flex items-center gap-4 mb-6">
            <span class="text-4xl">💬</span>
            <div>
              <h2 class="font-display text-2xl font-semibold text-ink-800">Start a Conversation</h2>
              <p class="text-ink-600">Choose a topic or enter your own</p>
            </div>
          </div>
          
          <!-- Topic input -->
          <div class="mb-6">
            <input
              type="text"
              bind:value={newChatTitle}
              placeholder="Enter a topic (optional)"
              class="input-primary"
              on:keydown={handleKeydown}
            />
          </div>
          
          <!-- Suggested topics -->
          <div class="mb-6">
            <p class="text-sm text-ink-500 mb-3">Or choose a topic:</p>
            <div class="flex flex-wrap gap-2">
              {#each topicSuggestions as topic}
                <button 
                  on:click={() => startFreeTalk(topic)}
                  class="px-4 py-2 bg-sage-50 text-sage-700 rounded-full text-sm hover:bg-sage-100 transition-colors"
                >
                  {topic}
                </button>
              {/each}
            </div>
          </div>
          
          <button 
            on:click={() => startFreeTalk()}
            disabled={creatingChat}
            class="btn-primary w-full"
          >
            {creatingChat ? 'Starting...' : 'Start Free Conversation'}
          </button>
        </div>
      </div>
    {/if}
    
    <!-- Grammar Setup -->
    {#if $currentMode === 'grammar'}
      <div class="animate-slide-up">
        <button on:click={() => currentMode.set(null)} class="btn-ghost mb-6 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        <div class="bg-white rounded-2xl p-8 shadow-sm border border-ink-100">
          <div class="flex items-center gap-4 mb-6">
            <span class="text-4xl">📖</span>
            <div>
              <h2 class="font-display text-2xl font-semibold text-ink-800">Grammar Practice</h2>
              <p class="text-ink-600">Enter a grammar topic you'd like to learn</p>
            </div>
          </div>
          
          <div class="mb-6">
            <input
              type="text"
              bind:value={newChatTitle}
              placeholder="e.g., Past Perfect Tense, Conditionals, Articles..."
              class="input-primary"
              on:keydown={handleKeydown}
            />
          </div>
          
          <button 
            on:click={startGrammarChat}
            disabled={creatingChat}
            class="btn-primary w-full"
          >
            {creatingChat ? 'Starting...' : 'Start Grammar Lesson'}
          </button>
        </div>
      </div>
    {/if}
    
    <!-- Document Setup -->
    {#if $currentMode === 'document'}
      <div class="animate-slide-up">
        <button on:click={() => currentMode.set(null)} class="btn-ghost mb-6 flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>
        
        <div class="bg-white rounded-2xl p-8 shadow-sm border border-ink-100">
          <div class="flex items-center gap-4 mb-6">
            <span class="text-4xl">📄</span>
            <div>
              <h2 class="font-display text-2xl font-semibold text-ink-800">Document Learning</h2>
              <p class="text-ink-600">Upload or select a document to learn from</p>
            </div>
          </div>
          
          <!-- File upload -->
          <div class="mb-6">
            <label class="block">
              <div class="border-2 border-dashed border-ink-200 rounded-xl p-8 text-center hover:border-sage-400 hover:bg-sage-50/50 transition-colors cursor-pointer">
                {#if uploadingDoc}
                  <div class="flex items-center justify-center gap-2 text-ink-600">
                    <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                    Processing document...
                  </div>
                {:else}
                  <svg class="w-10 h-10 text-ink-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p class="text-ink-600 mb-1">Click to upload a file</p>
                  <p class="text-sm text-ink-400">PDF, Image (PNG, JPG), or Text file</p>
                {/if}
              </div>
              <input 
                bind:this={fileInput}
                type="file" 
                accept=".pdf,.png,.jpg,.jpeg,.gif,.webp,.txt,.md"
                on:change={handleFileUpload}
                class="hidden"
              />
            </label>
          </div>
          
          <!-- Existing documents -->
          {#if $documents.length > 0}
            <div class="mb-6">
              <p class="text-sm text-ink-500 mb-3">Or select an existing document:</p>
              <select bind:value={selectedDocId} class="input-primary">
                <option value="">Choose a document...</option>
                {#each $documents as doc}
                  <option value={doc.id}>{doc.filename}</option>
                {/each}
              </select>
            </div>
          {/if}
          
          <button 
            on:click={startDocumentChat}
            disabled={creatingChat || !selectedDocId}
            class="btn-primary w-full"
          >
            {creatingChat ? 'Starting...' : 'Start Learning from Document'}
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>
