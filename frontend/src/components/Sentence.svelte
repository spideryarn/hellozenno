<!-- Sentence.svelte -->
<script lang="ts">
  import type { SentenceProps } from '../lib/types';
  import '../styles/global.css';

  export let sentence: SentenceProps['sentence'];
  export let metadata: SentenceProps['metadata'];
  export let enhanced_sentence_text: SentenceProps['enhanced_sentence_text'];
  
  // State for audio player
  let audioPlayer: HTMLAudioElement;
  let isGeneratingAudio = false;

  // Function to generate audio
  async function generateAudio() {
    if (isGeneratingAudio) return;
    
    isGeneratingAudio = true;
    try {
      const response = await fetch(
        `/api/sentence/${sentence.language_code}/${sentence.slug}/generate_audio`,
        { method: 'POST' }
      );
      
      if (!response.ok) throw new Error('Failed to generate audio');
      
      // Reload the page to show the new audio player
      window.location.reload();
    } catch (error) {
      console.error('Error generating audio:', error);
    } finally {
      isGeneratingAudio = false;
    }
  }

  // Function to set playback rate
  function setPlaybackRate(rate: number) {
    if (audioPlayer) {
      audioPlayer.playbackRate = rate;
    }
  }
</script>

<div class="sentence-page">
  <div class="card sentence-container">
    <!-- Metadata -->
    {#if metadata}
      <div class="metadata-section">
        <p>Created: <span class="metadata">{metadata.created_at ? new Date(metadata.created_at).toLocaleString() : 'N/A'}</span></p>
        <p>Updated: <span class="metadata">{metadata.updated_at ? new Date(metadata.updated_at).toLocaleString() : 'N/A'}</span></p>
      </div>
    {/if}

    <div class="main-content">
      <div class="greek-text">
        {@html enhanced_sentence_text}
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
            src="/api/{sentence.language_code}/sentences/{sentence.id}/audio"
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
      {:else}
        <button
          class="button"
          on:click={generateAudio}
          disabled={isGeneratingAudio}
        >
          {isGeneratingAudio ? 'Generating...' : 'Generate audio'}
        </button>
      {/if}

      {#if sentence.lemma_words}
        <div class="words-section">
          <h3>Words</h3>
          <ul class="words-list">
            {#each sentence.lemma_words as lemma}
              <li>
                <a 
                  href="/{sentence.language_code}/lemma/{lemma}" 
                  class="lemma-link"
                >
                  {lemma}
                </a>
              </li>
            {/each}
          </ul>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .sentence-page {
    padding: var(--spacing-4);
    max-width: 800px;
    margin: 0 auto;
  }

  .sentence-container {
    position: relative;
  }

  .metadata-section {
    position: absolute;
    top: var(--spacing-4);
    right: var(--spacing-4);
    text-align: right;
    background: var(--color-background);
    padding: var(--spacing-2);
    border-radius: 4px;
  }

  .metadata-section p {
    margin: var(--spacing-1) 0;
  }

  .main-content {
    margin-top: var(--spacing-8);
  }

  .greek-text {
    font-size: 1.5rem;
    line-height: 1.6;
    margin-bottom: var(--spacing-4);
  }

  .greek-text :global(.word-link) {
    color: var(--color-primary);
    text-decoration: none;
    margin: 0 var(--spacing-1);
  }

  .english-translation {
    font-size: 1.125rem;
    color: var(--color-text-muted);
    font-style: italic;
    margin-bottom: var(--spacing-6);
  }

  .audio-section {
    margin: var(--spacing-4) 0;
  }

  .audio-player {
    width: 100%;
    margin-bottom: var(--spacing-2);
  }

  .playback-controls {
    display: flex;
    gap: var(--spacing-2);
  }

  .speed-button {
    padding: var(--spacing-1) var(--spacing-3);
    border: 1px solid var(--color-border);
    border-radius: 4px;
    background: var(--color-surface);
    cursor: pointer;
    font-size: 0.875rem;
    font-family: var(--font-mono);
  }

  .speed-button:hover {
    background: var(--color-background);
  }

  .words-section {
    margin-top: var(--spacing-8);
    border-top: 1px solid var(--color-border);
    padding-top: var(--spacing-4);
  }

  .words-section h3 {
    font-size: 1.125rem;
    color: var(--color-text);
    margin-bottom: var(--spacing-3);
  }

  .words-list {
    list-style: none;
    padding: 0;
  }

  .words-list li {
    margin: var(--spacing-2) 0;
  }

  .lemma-link {
    color: var(--color-primary);
    text-decoration: none;
    font-size: 1rem;
  }

  .lemma-link:hover {
    text-decoration: underline;
  }
</style> 