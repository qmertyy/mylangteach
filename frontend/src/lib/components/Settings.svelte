<script lang="ts">
  import { onMount } from "svelte";
  import { settingsOpen, llmConfig, error } from "$lib/stores";
  import { api } from "$lib/api";

  let provider: string = "ollama";
  let model: string = "";
  let baseUrl: string = "http://localhost:11434";
  let apiKey: string = "";
  let saving = false;
  let initialized = false;

  onMount(() => {
    if ($llmConfig) {
      provider = $llmConfig.provider || "ollama";
      model = $llmConfig.model || "";
      baseUrl = $llmConfig.base_url || "http://localhost:11434";
    }
    initialized = true;
  });

  function handleProviderChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    provider = select.value;

    if (provider === "gemini" && !model.startsWith("gemini")) {
      model = "gemini-2.0-flash-exp";
    } else if (provider === "ollama") {
      model = "llama3.2";
    } else if (provider === "openai" && !model.startsWith("gpt")) {
      model = "gpt-4";
    } else if (provider === "anthropic" && !model.startsWith("claude")) {
      model = "claude-3-sonnet-20240229";
    }
  }

  async function saveSettings() {
    saving = true;
    try {
      const config = {
        provider: provider as "ollama" | "openai" | "anthropic" | "gemini",
        model,
        base_url: baseUrl,
        api_key: apiKey || undefined,
      };

      await api.updateConfig(config);
      llmConfig.set({
        ...config,
        has_api_key: !!apiKey || !!$llmConfig?.has_api_key,
      });
      settingsOpen.set(false);
    } catch (e: any) {
      error.set(e.message || "Failed to save settings");
    } finally {
      saving = false;
    }
  }

  function close() {
    settingsOpen.set(false);
  }
</script>

<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
  <button
    class="absolute inset-0 bg-ink-950/50 backdrop-blur-sm"
    on:click={close}
    aria-label="Close settings"
  ></button>

  <div
    class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg animate-slide-up"
  >
    <div class="flex items-center justify-between p-6 border-b border-ink-100">
      <h2 class="font-display text-xl font-semibold text-ink-800">Settings</h2>
      <button on:click={close} class="btn-icon">
        <svg
          class="w-5 h-5 text-ink-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <div class="p-6 space-y-6">
      <div>
        <label
          for="provider-select"
          class="block text-sm font-medium text-ink-700 mb-2"
          >LLM Provider</label
        >
        <select
          id="provider-select"
          value={provider}
          on:change={handleProviderChange}
          class="input-primary"
        >
          <option value="ollama">Ollama (Local)</option>
          <option value="gemini">Google Gemini </option>
          <option value="openai">OpenAI / Compatible</option>
          <option value="anthropic">Anthropic</option>
        </select>
        <p class="mt-1 text-xs text-ink-500">
          {#if provider === "ollama"}
            Run models locally with Ollama
          {:else if provider === "gemini"}
            Google Gemini API - free tier: 15 RPM, 1M tokens/day
          {:else if provider === "openai"}
            OpenAI API or compatible services
          {:else}
            Anthropic Claude API
          {/if}
        </p>
      </div>

      <div>
        <label
          for="model-input"
          class="block text-sm font-medium text-ink-700 mb-2">Model</label
        >
        <input
          id="model-input"
          type="text"
          bind:value={model}
          class="input-primary"
          placeholder={provider === "ollama"
            ? "llama3.2"
            : provider === "gemini"
              ? "gemini-2.0-flash-exp"
              : provider === "anthropic"
                ? "claude-3-sonnet-20240229"
                : "gpt-4"}
        />
        <p class="mt-1 text-xs text-ink-500">
          {#if provider === "ollama"}
            e.g., llama3.2, mistral
          {:else if provider === "gemini"}
            e.g., gemini-2.0-flash-lite
          {:else if provider === "anthropic"}
            e.g., claude-3-sonnet-20240229, claude-3-opus-20240229
          {:else}
            e.g., gpt-4, gpt-3.5-turbo
          {/if}
        </p>
      </div>

      {#if provider !== "gemini"}
        <div>
          <label
            for="baseurl-input"
            class="block text-sm font-medium text-ink-700 mb-2"
          >
            {provider === "ollama" ? "Ollama URL" : "API Base URL"}
          </label>
          <input
            id="baseurl-input"
            type="url"
            bind:value={baseUrl}
            class="input-primary"
            placeholder={provider === "ollama"
              ? "http://localhost:11434"
              : "...."}
          />
        </div>
      {/if}

      {#if provider !== "ollama"}
        <div>
          <label
            for="apikey-input"
            class="block text-sm font-medium text-ink-700 mb-2">API Key</label
          >
          <input
            id="apikey-input"
            type="password"
            bind:value={apiKey}
            class="input-primary"
            placeholder={$llmConfig?.has_api_key
              ? "••••••••••••••••"
              : "Enter your API key"}
          />
          <p class="mt-1 text-xs text-ink-500">
            {#if provider === "gemini"}
              {#if $llmConfig?.has_api_key}
                API key configured via .env file. Enter new key to override.
              {:else}
                set up the api key
              {/if}
            {:else if $llmConfig?.has_api_key}
              API key is set. Enter a new one to change.
            {:else}
              Required for this provider.
            {/if}
          </p>
        </div>
      {/if}
    </div>

    <div class="flex justify-end gap-3 p-6 border-t border-ink-100">
      <button on:click={close} class="btn-secondary"> Cancel </button>
      <button on:click={saveSettings} class="btn-primary" disabled={saving}>
        {#if saving}
          <span class="flex items-center gap-2">
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              ></path>
            </svg>
            Saving...
          </span>
        {:else}
          Save Settings
        {/if}
      </button>
    </div>
  </div>
</div>
