<script lang="ts">
  import { isRecording, error } from '$lib/stores';
  import { api } from '$lib/api';
  
  export let onSend: (message: string) => void;
  export let onAudioSend: ((audioBlob: Blob) => Promise<void>) | undefined = undefined;
  export let disabled: boolean = false;
  export let placeholder: string = "Type a message...";
  
  let inputValue = '';
  let textareaRef: HTMLTextAreaElement;
  let mediaRecorder: MediaRecorder | null = null;
  let audioChunks: Blob[] = [];
  let recordingTime = 0;
  let recordingInterval: ReturnType<typeof setInterval> | null = null;
  
  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }
  
  function send() {
    const trimmed = inputValue.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      inputValue = '';
      if (textareaRef) {
        textareaRef.style.height = 'auto';
      }
    }
  }
  
  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000
        } 
      });
      
      // Use webm format which is widely supported
      const mimeType = MediaRecorder.isTypeSupported('audio/webm') 
        ? 'audio/webm' 
        : 'audio/mp4';
      
      mediaRecorder = new MediaRecorder(stream, { mimeType });
      audioChunks = [];
      recordingTime = 0;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        
        if (audioChunks.length > 0 && onAudioSend) {
          const audioBlob = new Blob(audioChunks, { type: mimeType });
          await onAudioSend(audioBlob);
        }
        
        // Clear interval
        if (recordingInterval) {
          clearInterval(recordingInterval);
          recordingInterval = null;
        }
      };
      
      mediaRecorder.start(100); // Collect data every 100ms
      isRecording.set(true);
      
      // Update recording time
      recordingInterval = setInterval(() => {
        recordingTime += 1;
      }, 1000);
      
    } catch (err: any) {
      console.error('Failed to start recording:', err);
      error.set('Could not access microphone. Please allow microphone access.');
    }
  }
  
  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      isRecording.set(false);
    }
  }
  
  function toggleRecording() {
    if ($isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }
  
  function formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }
  
  function autoResize(e: Event) {
    const target = e.target as HTMLTextAreaElement;
    target.style.height = 'auto';
    target.style.height = Math.min(target.scrollHeight, 200) + 'px';
  }
</script>

<div class="border-t border-ink-200 bg-white p-4">
  <div class="max-w-3xl mx-auto">
    <div class="flex items-end gap-3">
      <!-- Voice input button -->
      <button 
        on:click={toggleRecording}
        class="btn-icon flex-shrink-0 relative"
        class:bg-coral-100={$isRecording}
        class:text-coral-600={$isRecording}
        class:hover:bg-ink-100={!$isRecording}
        disabled={disabled && !$isRecording}
        aria-label={$isRecording ? 'Stop recording' : 'Start voice input'}
        title={$isRecording ? 'Click to stop and send' : 'Click to record voice message'}
      >
        {#if $isRecording}
          <div class="recording-indicator"></div>
        {:else}
          <svg class="w-5 h-5 text-ink-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        {/if}
      </button>
      
      <!-- Text input (hidden when recording) -->
      {#if !$isRecording}
        <div class="flex-1 relative">
          <textarea
            bind:this={textareaRef}
            bind:value={inputValue}
            on:keydown={handleKeydown}
            on:input={autoResize}
            {placeholder}
            disabled={disabled}
            rows="1"
            class="input-primary resize-none pr-12"
          ></textarea>
        </div>
        
        <!-- Send button -->
        <button 
          on:click={send}
          disabled={disabled || !inputValue.trim()}
          class="btn-primary flex-shrink-0 px-4"
          aria-label="Send message"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      {:else}
        <!-- Recording indicator -->
        <div class="flex-1 flex items-center justify-center gap-4 py-3 bg-coral-50 rounded-xl">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 bg-coral-500 rounded-full animate-pulse"></span>
            <span class="text-coral-700 font-medium">Recording...</span>
            <span class="text-coral-600 font-mono">{formatTime(recordingTime)}</span>
          </div>
        </div>
        
        <!-- Stop/Send button -->
        <button 
          on:click={stopRecording}
          class="btn-primary flex-shrink-0 px-4 bg-coral-600 hover:bg-coral-700"
          aria-label="Stop recording and send"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
        </button>
      {/if}
    </div>
    
    {#if $isRecording}
      <p class="text-center text-sm text-coral-600 mt-2">
        Speak now • Click stop when done
      </p>
    {:else if onAudioSend}
      <p class="text-center text-xs text-ink-400 mt-2">
        Press the microphone to record a voice message
      </p>
    {/if}
  </div>
</div>
