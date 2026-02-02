<script lang="ts">
  import type { Message } from '$lib/api';
  
  
  export let message: Message;
  export let grammarDetected: { rule_name: string; explanation: string } | null = null;
  export let onLearnGrammar: ((ruleName: string, explanation: string) => void) | undefined = undefined;
  

 
  
  function handleLearnGrammar() {
    if (onLearnGrammar && grammarDetected) {
      onLearnGrammar(grammarDetected.rule_name, grammarDetected.explanation);
    }
  }
</script>

<div class="flex animate-fade-in" class:justify-end={message.role === 'user'} class:justify-start={message.role !== 'user'}>
  <div class="group relative max-w-[80%]">
    <!-- Message bubble -->
    <div class={message.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}>
      <p class="whitespace-pre-wrap">{message.content}</p>
    </div>
    
    <!-- Actions (visible on hover for assistant messages) -->
    {#if message.role === 'assistant'}
      <div class="absolute -bottom-8 left-0 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2">
        
        <span class="text-xs text-ink-400">
          {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    {/if}
    
    <!-- Grammar detection alert -->
    {#if grammarDetected && message.role === 'assistant'}
      <div class="grammar-alert mt-3">
        <div class="flex items-start gap-3">
          <span class="text-xl">💡</span>
          <div class="flex-1">
            <h4 class="font-medium text-amber-800">Grammar Tip: {grammarDetected.rule_name}</h4>
            <p class="text-sm text-amber-700 mt-1">{grammarDetected.explanation}</p>
            {#if onLearnGrammar}
              <button 
                on:click={handleLearnGrammar}
                class="mt-2 text-sm font-medium text-amber-700 hover:text-amber-800 underline underline-offset-2"
              >
                Learn more about this grammar rule →
              </button>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>
