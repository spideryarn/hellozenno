<script lang="ts">
  import type { Sentence, SentenceMetadata } from '$lib/types';
  import { MetadataCard } from '$lib';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  
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
  
  // Generate the audio URL using type-safe route resolution
  const audioUrl = getApiUrl(RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_API, {
    target_language_code: sentence.target_language_code,
    sentence_id: String(sentence.id)
  });
</script>

<div class="container py-3">
  <div class="card">
    <div class="card-body">
      <!-- Metadata -->
      {#if metadata && (metadata.created_at || metadata.updated_at)}
        <div class="text-end">
          <MetadataCard {metadata} />
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
            <button class="btn btn-sm btn-outline-secondary" on:click={() => setPlaybackRate(0.85)}>0.85x</button>
            <button class="btn btn-sm btn-outline-secondary" on:click={() => setPlaybackRate(1.0)}>1.0x</button>
            <button class="btn btn-sm btn-outline-secondary" on:click={() => setPlaybackRate(1.2)}>1.2x</button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div> 