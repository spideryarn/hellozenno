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
        target_language_code: sentence.language_code,
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
        target_language_code: sentence.language_code,
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
    target_language_code: sentence.language_code,
    sentence_id: String(sentence.id)
  });
</script>

<div class="sentence-page container py-4">
  <div class="hz-sentence card">
    <!-- Metadata -->
    {#if metadata}
      <div class="metadata-section position-absolute top-0 end-0 m-3 p-2 bg-dark bg-opacity-75 rounded">
        <p class="mb-1">Created: <span class="hz-metadata">{metadata.created_at ? new Date(metadata.created_at).toLocaleString() : 'N/A'}</span></p>
        <p class="mb-1">Updated: <span class="hz-metadata">{metadata.updated_at ? new Date(metadata.updated_at).toLocaleString() : 'N/A'}</span></p>
      </div>
    {/if}

    <div class="card-body">
      <div class="hz-foreign-text mb-4">
        <!-- Render the enhanced text with fallback -->
        {@html enhanced_sentence_text || '<p>No sentence text available</p>'}
      </div>
      
      {#if sentence.translation}
        <div class="mb-4 text-muted fst-italic">
          {sentence.translation}
        </div>
      {/if}

      <!-- Audio Section -->
      {#if sentence.has_audio}
        <div class="mb-4">
          <audio
            bind:this={audioPlayer}
            controls
            src={audioUrl}
            class="hz-audio-player"
          >
            Your browser does not support the audio element.
          </audio>
          
          <div class="hz-playback-controls">
            <button class="hz-speed-button" on:click={() => setPlaybackRate(0.8)}>0.8x</button>
            <button class="hz-speed-button" on:click={() => setPlaybackRate(0.9)}>0.9x</button>
            <button class="hz-speed-button" on:click={() => setPlaybackRate(1.0)}>1.0x</button>
            <button class="hz-speed-button" on:click={() => setPlaybackRate(1.5)}>1.5x</button>
          </div>
        </div>
      {:else}
        <button
          class="hz-btn-primary mb-4"
          on:click={generateAudio}
          disabled={isGeneratingAudio}
        >
          {isGeneratingAudio ? 'Generating...' : 'Generate audio'}
        </button>
      {/if}

      {#if sentence.lemma_words}
        <div class="mt-4 pt-4 border-top">
          <h3 class="h5 mb-3">Words</h3>
          <div class="d-flex flex-column gap-2">
            {#each sentence.lemma_words as lemma}
              <MiniLemma 
                lemma={lemma}
                partOfSpeech={lemmasData[lemma]?.part_of_speech || ''}
                translations={lemmasData[lemma]?.translations || []}
                href="/lang/{sentence.language_code}/lemma/{lemma}"
              />
              {#if lemmasData[lemma]?.isLoading}
                <div class="small text-muted fst-italic mb-2">Loading lemma data...</div>
              {/if}
            {/each}
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  /* Most styling is now handled by Bootstrap classes and our custom CSS */
  /* We only need minimal component-specific styles */
  
  :global(.word-link) {
    color: var(--color-primary);
    text-decoration: none;
    margin: 0 var(--spacing-1);
  }
  
  :global(br) {
    display: block;
    content: "";
    margin-top: 0.5rem;
  }
</style> 