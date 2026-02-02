<script lang="ts">
  import { error } from '$lib/stores';
</script>

{#if $error}
  <div class="fixed bottom-4 right-4 z-50 animate-slide-up">
    <div class="flex items-center gap-3 bg-coral-600 text-white px-4 py-3 rounded-xl shadow-lg max-w-md">
      <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm">{$error}</p>
      <button onclick={() => error.set(null)} class="ml-2 hover:bg-white/20 rounded-lg p-1 transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
{/if}
