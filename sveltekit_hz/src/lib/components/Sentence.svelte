<script lang="ts">
  import type { Sentence, SentenceMetadata } from '$lib/api';
  
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
  const audioUrl = `/api/language/${sentence.language_code}/sentence/${sentence.id}/audio`;
</script>

<div class="sentence-page">
  <div class="sentence-container">
    <!-- Metadata -->
    {#if metadata && (metadata.created_at || metadata.updated_at)}
      <div class="metadata-section">
        {#if metadata.created_at}
          <p>Created: <span class="metadata">{new Date(metadata.created_at).toLocaleString()}</span></p>
        {/if}
        {#if metadata.updated_at}
          <p>Updated: <span class="metadata">{new Date(metadata.updated_at).toLocaleString()}</span></p>
        {/if}
      </div>
    {/if}

    <div class="main-content">
      <div class="target-lang-text">
        <!-- Render the enhanced text with fallback -->
        {@html enhanced_sentence_text || `<p>${sentence.text}</p>`}
      </div>
      
      {#if sentence.translation}
        <div class="english-translation">
          {sentence.translation}
        </div>
      {/if}

      <!-- Audio Section -->
      {#if sentence.has_audio}
        <div class="audio-section">
          <audio
            bind:this={audioPlayer}
            controls
            src={audioUrl}
            class="audio-player"
          >
            Your browser does not support the audio element.
          </audio>
          
          <div class="playback-controls">
            <button class="speed-button" on:click={() => setPlaybackRate(0.8)}>0.8x</button>
            <button class="speed-button" on:click={() => setPlaybackRate(1.0)}>1.0x</button>
            <button class="speed-button" on:click={() => setPlaybackRate(1.5)}>1.5x</button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .sentence-page {
    padding: 1rem;
    max-width: 800px;
    margin: 0 auto;
  }

  .sentence-container {
    position: relative;
    background-color: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .metadata-section {
    position: absolute;
    top: 1rem;
    right: 1rem;
    text-align: right;
    font-size: 0.8rem;
    color: #666;
  }

  .metadata-section p {
    margin: 0.25rem 0;
  }

  .main-content {
    margin-top: 1rem;
  }

  .target-lang-text {
    font-size: 1.5rem;
    line-height: 1.6;
    margin-bottom: 1rem;
  }
  
  .english-translation {
    font-size: 1.125rem;
    color: #666;
    font-style: italic;
    margin-bottom: 1.5rem;
  }

  .audio-section {
    margin: 1rem 0;
  }

  .audio-player {
    width: 100%;
    margin-bottom: 0.5rem;
  }

  .playback-controls {
    display: flex;
    gap: 0.5rem;
  }

  .speed-button {
    padding: 0.25rem 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #f9f9f9;
    cursor: pointer;
    font-size: 0.875rem;
  }

  .speed-button:hover {
    background: #f0f0f0;
  }
</style> 