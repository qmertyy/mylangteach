<script lang="ts">
  import { 
    sidebarOpen, currentMode, currentChatId, settingsOpen,
    topicChats, grammarChats, documentChats, documents
  } from '$lib/stores';
  import { goto } from '$app/navigation';
  
  function selectMode(mode: 'free_talk' | 'grammar' | 'document' | null) {
    currentMode.set(mode);
    currentChatId.set(null);
    goto('/');
  }
  
  function selectChat(chatId: string) {
    currentChatId.set(chatId);
    goto(`/chat/${chatId}`);
  }
  
  function toggleSidebar() {
    sidebarOpen.update(v => !v);
  }
</script>

<!-- Sidebar toggle button (always visible) -->
<button 
  on:click={toggleSidebar}
  class="fixed top-4 left-4 z-50 btn-icon bg-white shadow-md"
  class:opacity-0={$sidebarOpen}
  class:opacity-100={!$sidebarOpen}
  aria-label="Toggle sidebar"
>
  <svg class="w-5 h-5 text-ink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
  </svg>
</button>

<!-- Sidebar panel -->
<aside 
  class="fixed left-0 top-0 h-full w-72 bg-white border-r border-ink-200 z-40 transform transition-transform duration-300 flex flex-col"
  class:translate-x-0={$sidebarOpen}
  class:-translate-x-full={!$sidebarOpen}
>
  <!-- Header -->
  <div class="p-4 border-b border-ink-100 flex items-center justify-between">
    <button on:click={() => selectMode(null)} class="flex items-center gap-3 hover:opacity-80 transition-opacity">
      <span class="text-2xl">📚</span>
      <span class="font-display text-xl font-semibold text-ink-800">Language Teacher</span>
    </button>
    <button on:click={toggleSidebar} class="btn-icon">
      <svg class="w-5 h-5 text-ink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
      </svg>
    </button>
  </div>
  
  <!-- Navigation -->
  <nav class="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-6">
    <!-- Mode Selection -->
    <div>
      <h3 class="px-3 text-xs font-semibold text-ink-500 uppercase tracking-wider mb-2">Modes</h3>
      <div class="space-y-1">
        <button 
          on:click={() => selectMode('free_talk')} 
          class="sidebar-item w-full text-left"
          class:active={$currentMode === 'free_talk'}
        >
          <span class="text-lg">💬</span>
          <span>Free Talk</span>
        </button>
        <button 
          on:click={() => selectMode('grammar')} 
          class="sidebar-item w-full text-left"
          class:active={$currentMode === 'grammar'}
        >
          <span class="text-lg">📖</span>
          <span>Grammar</span>
        </button>
        <button 
          on:click={() => selectMode('document')} 
          class="sidebar-item w-full text-left"
          class:active={$currentMode === 'document'}
        >
          <span class="text-lg">📄</span>
          <span>Document Mode</span>
        </button>
      </div>
    </div>
    
    <!-- Recent Chats -->
    {#if $topicChats.length > 0}
      <div>
        <h3 class="px-3 text-xs font-semibold text-ink-500 uppercase tracking-wider mb-2">Topic Chats</h3>
        <div class="space-y-1">
          {#each $topicChats.slice(0, 5) as chat}
            <button 
              on:click={() => selectChat(chat.id)}
              class="sidebar-item w-full text-left text-sm"
              class:active={$currentChatId === chat.id}
            >
              <span class="truncate">{chat.title}</span>
            </button>
          {/each}
        </div>
      </div>
    {/if}
    
    {#if $grammarChats.length > 0}
      <div>
        <h3 class="px-3 text-xs font-semibold text-ink-500 uppercase tracking-wider mb-2">Grammar Lessons</h3>
        <div class="space-y-1">
          {#each $grammarChats.slice(0, 5) as chat}
            <button 
              on:click={() => selectChat(chat.id)}
              class="sidebar-item w-full text-left text-sm"
              class:active={$currentChatId === chat.id}
            >
              <span class="truncate">{chat.title}</span>
            </button>
          {/each}
        </div>
      </div>
    {/if}
    
    {#if $documentChats.length > 0}
      <div>
        <h3 class="px-3 text-xs font-semibold text-ink-500 uppercase tracking-wider mb-2">Document Chats</h3>
        <div class="space-y-1">
          {#each $documentChats.slice(0, 5) as chat}
            <button 
              on:click={() => selectChat(chat.id)}
              class="sidebar-item w-full text-left text-sm"
              class:active={$currentChatId === chat.id}
            >
              <span class="truncate">{chat.title}</span>
            </button>
          {/each}
        </div>
      </div>
    {/if}
    
    {#if $documents.length > 0}
      <div>
        <h3 class="px-3 text-xs font-semibold text-ink-500 uppercase tracking-wider mb-2">Documents</h3>
        <div class="space-y-1">
          {#each $documents.slice(0, 5) as doc}
            <div class="sidebar-item text-sm opacity-70">
              <span class="text-lg">📎</span>
              <span class="truncate">{doc.filename}</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </nav>
  
  <!-- Footer -->
  <div class="p-3 border-t border-ink-100">
    <button 
      on:click={() => settingsOpen.set(true)}
      class="sidebar-item w-full text-left"
    >
      <svg class="w-5 h-5 text-ink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <span>Settings</span>
    </button>
  </div>
</aside>
