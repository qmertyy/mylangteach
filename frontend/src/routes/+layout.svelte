<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import { 
    chats, categories, documents, llmConfig, 
    sidebarOpen, error, settingsOpen
  } from '$lib/stores';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Settings from '$lib/components/Settings.svelte';
  import Toast from '$lib/components/Toast.svelte';
  
  onMount(async () => {
    try {
      const [configData, chatsData, categoriesData, docsData] = await Promise.all([
        api.getConfig(),
        api.getChats(),
        api.getCategories(),
        api.getDocuments()
      ]);
      
      llmConfig.set(configData);
      chats.set(chatsData);
      categories.set(categoriesData);
      documents.set(docsData);
    } catch (e) {
      error.set('Failed to connect to backend. Is the server running?');
    }
  });
</script>

<div class="min-h-screen bg-ink-50 flex">
  <!-- Noise texture overlay -->
  <div class="fixed inset-0 noise pointer-events-none"></div>
  
  <!-- Sidebar -->
  <Sidebar />
  
  <!-- Main content -->
  <main class="flex-1 flex flex-col min-h-screen relative transition-all duration-300" class:ml-72={$sidebarOpen} class:ml-0={!$sidebarOpen}>
    <slot />
  </main>
  
  <!-- Settings modal -->
  {#if $settingsOpen}
    <Settings />
  {/if}
  
  <!-- Toast notifications -->
  <Toast />
</div>
