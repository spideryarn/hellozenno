<script lang="ts">
  import type { Sentence, SentenceMetadata } from '$lib/types';
  
  // Props for the Sentence component
  export let sentence: Sentence;
  export let metadata: SentenceMetadata = {};
  export let enhanced_sentence_text: string = '';
  
  // State for audio player
  let audioPlayer: HTMLAudioElement;
  
  // Function to set playback rate
  function setPlaybackRate(rate: number) {
    if (audioPlayer) {
      audioPlayer.playbackRate = rate;
    }
  }
  
  // Generate the audio URL
  const audioUrl = `http://localhost:3000/api/lang/sentence/${sentence.language_code}/${sentence.id}/audio`;
</script>

<div class="container py-3">
  <div class="card">
    <div class="card-body">
      <!-- Metadata -->
      {#if metadata && (metadata.created_at || metadata.updated_at)}
        <div class="text-end text-secondary small mb-3">
          {#if metadata.created_at}
            <p class="mb-1">Created: <span class="font-monospace">{new Date(metadata.created_at).toLocaleString()}</span></p>
          {/if}
          {#if metadata.updated_at}
            <p class="mb-1">Updated: <span class="font-monospace">{new Date(metadata.updated_at).toLocaleString()}</span></p>
          {/if}
        </div>
      {/if}

      <div class="mb-4">
        <div class="hz-foreign-text fs-4 mb-3">
          <!-- Render the enhanced text with fallback -->
          {@html enhanced_sentence_text || `<p>${sentence.text}</p>`}
        </div>
        
        {#if sentence.translation}
          <div class="text-secondary fst-italic">
            {sentence.translation}
          </div>
        {/if}
      </div>

      <!-- Audio Section -->
      {#if sentence.has_audio}
        <div class="mt-4">
          <audio
            bind:this={audioPlayer}
            controls
            src={audioUrl}
            class="w-100 mb-2"
          >
            Your browser does not support the audio element.
          </audio>
          
          <div class="d-flex gap-2">
            <button class="btn btn-sm btn-outline-secondary" on:click={() => setPlaybackRate(0.8)}>0.8x</button>
            <button class="btn btn-sm btn-outline-secondary" on:click={() => setPlaybackRate(1.0)}>1.0x</button>
            <button class="btn btn-sm btn-outline-secondary" on:click={() => setPlaybackRate(1.5)}>1.5x</button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div> 