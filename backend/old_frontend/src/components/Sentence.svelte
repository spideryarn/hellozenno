<!-- Sentence.svelte -->
<script lang="ts">
  import type { SentenceProps } from '../lib/types';
  import '../styles/global.css';
  import MiniLemma from './MiniLemma.svelte';
  import { onMount } from 'svelte';
  import { RouteName, resolveRoute } from '../../../static/js/generated/routes';

  export let sentence: SentenceProps['sentence'];
  export let metadata: SentenceProps['metadata'];
  export let enhanced_sentence_text: SentenceProps['enhanced_sentence_text'];
  
  // Component initialized
  
  // State for audio player
  let audioPlayer: HTMLAudioElement;
  let isGeneratingAudio = false;
  
  // State for lemma data
  type LemmaData = {
    lemma: string;
    part_of_speech: string;
    translations: string[];
    isLoading: boolean;
    error: string | null;
  };
  
  let lemmasData: Record<string, LemmaData> = {};
  
  onMount(() => {
    // Component mounted successfully
  });
  
  // Initialize lemmasData with empty values
  if (sentence.lemma_words) {
    sentence.lemma_words.forEach(lemma => {
      lemmasData[lemma] = {
        lemma,
        part_of_speech: '',
        translations: [],
        isLoading: true,
        error: null
      };
    });
  }
  
  // Fetch lemma data for each lemma
  async function fetchLemmaData(lemma: string) {
    try {
      const url = resolveRoute(RouteName.LEMMA_API_GET_LEMMA_DATA_API, {
        target_language_code: sentence.target_language_code,
        lemma: lemma
      });
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch lemma data for ${lemma}`);
      }
      
      const data = await response.json();
      lemmasData[lemma] = {
        lemma,
        part_of_speech: data.part_of_speech || '',
        translations: data.translations || [],
        isLoading: false,
        error: null
      };
    } catch (error) {
      console.error('Error fetching lemma data:', error);
      lemmasData[lemma] = {
        ...lemmasData[lemma],
        isLoading: false,
        error: String(error)
      };
    }
  }
  
  // Fetch data for all lemmas when component mounts
  if (sentence.lemma_words) {
    sentence.lemma_words.forEach(fetchLemmaData);
  }

  // Function to generate audio
  async function generateAudio() {
    if (isGeneratingAudio) return;
    
    isGeneratingAudio = true;
    try {
      const url = resolveRoute(RouteName.SENTENCE_API_GENERATE_SENTENCE_AUDIO_API, {
        target_language_code: sentence.target_language_code,
        slug: sentence.slug
      });
      
      const response = await fetch(url, { method: 'POST' });
      
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
  
  // Generate the audio URL using route registry
  const audioUrl = resolveRoute(RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_API, {
    target_language_code: sentence.target_language_code,
    sentence_id: String(sentence.id)
  });
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
      <div class="target-lang-text">
        <!-- Render the enhanced text with fallback -->
        {@html enhanced_sentence_text || '<p>No sentence text available</p>'}
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
            <button class="speed-button" on:click={() => setPlaybackRate(0.9)}>0.9x</button>
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
          <div class="words-list">
            {#each sentence.lemma_words as lemma}
              <MiniLemma 
                lemma={lemma}
                partOfSpeech={lemmasData[lemma]?.part_of_speech || ''}
                translations={lemmasData[lemma]?.translations || []}
                href="/lang/{sentence.target_language_code}/lemma/{lemma}"
              />
              {#if lemmasData[lemma]?.isLoading}
                <div class="loading-indicator">Loading lemma data...</div>
              {/if}
            {/each}
          </div>
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

  .target-lang-text {
    font-size: 1.5rem;
    line-height: 1.6;
    margin-bottom: var(--spacing-4);
  }

  /* Import global styles at the top level instead of using :global scope */
  :global(p) {
    margin: 0;
    padding: 0;
  }

  :global(.word-link) {
    color: var(--color-primary);
    text-decoration: none;
    margin: 0 var(--spacing-1);
  }
  
  /* Ensure consistent styling for any nested elements */
  :global(br) {
    display: block;
    content: "";
    margin-top: 0.5rem;
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
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-2);
  }
  
  .loading-indicator {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    font-style: italic;
    margin-top: -0.5rem;
    margin-bottom: 0.5rem;
  }
</style> 