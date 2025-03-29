<!-- Sentence.svelte -->
<script lang="ts">
  import type { SentenceProps } from '../lib/types';
  import '../styles/global.css';
  import '../styles/bulma-imports.css'; // Import Bulma
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

<div class="container">
  <div class="card">
    <div class="card-content">
      <!-- Metadata -->
      {#if metadata}
        <div class="is-pulled-right has-text-right p-2 has-background-dark is-size-7">
          <p class="has-family-monospace mb-1">
            Created: <span class="metadata-timestamp">{metadata.created_at ? new Date(metadata.created_at).toLocaleString() : 'N/A'}</span>
          </p>
          <p class="has-family-monospace">
            Updated: <span class="metadata-timestamp">{metadata.updated_at ? new Date(metadata.updated_at).toLocaleString() : 'N/A'}</span>
          </p>
        </div>
      {/if}

      <div class="content">
        <div class="enhanced-text mb-5">
          <!-- Render the enhanced text with fallback -->
          {@html enhanced_sentence_text || '<p>No sentence text available</p>'}
        </div>
        
        {#if sentence.translation}
          <div class="translated-text mb-5">
            {sentence.translation}
          </div>
        {/if}

        <!-- Audio Section -->
        <div class="mb-5">
          {#if sentence.has_audio}
            <div class="box has-background-dark">
              <audio
                bind:this={audioPlayer}
                controls
                src={audioUrl}
                class="is-fullwidth"
                style="width: 100%;"
              >
                Your browser does not support the audio element.
              </audio>
              
              <div class="field has-addons is-centered mt-3">
                <p class="control">
                  <button class="button is-small has-family-monospace" on:click={() => setPlaybackRate(0.8)}>0.8x</button>
                </p>
                <p class="control">
                  <button class="button is-small has-family-monospace" on:click={() => setPlaybackRate(0.9)}>0.9x</button>
                </p>
                <p class="control">
                  <button class="button is-small has-family-monospace" on:click={() => setPlaybackRate(1.0)}>1.0x</button>
                </p>
                <p class="control">
                  <button class="button is-small has-family-monospace" on:click={() => setPlaybackRate(1.5)}>1.5x</button>
                </p>
              </div>
            </div>
          {:else}
            <button
              class="button is-primary"
              on:click={generateAudio}
              disabled={isGeneratingAudio}
            >
              <span class="icon">
                <i class="fas fa-volume-up"></i>
              </span>
              <span>{isGeneratingAudio ? 'Generating...' : 'Generate audio'}</span>
            </button>
          {/if}
        </div>

        {#if sentence.lemma_words}
          <div class="mt-6 pt-4" style="border-top: 1px solid var(--dark-border);">
            <h3 class="title is-5">Words</h3>
            <div class="content">
              {#each sentence.lemma_words as lemma}
                <div class="mb-3">
                  <MiniLemma 
                    lemma={lemma}
                    partOfSpeech={lemmasData[lemma]?.part_of_speech || ''}
                    translations={lemmasData[lemma]?.translations || []}
                    href="/lang/{sentence.language_code}/lemma/{lemma}"
                  />
                  {#if lemmasData[lemma]?.isLoading}
                    <div class="has-text-grey-light is-size-7 is-italic ml-3 has-family-monospace">Loading lemma data...</div>
                  {/if}
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  /* Only keep styles that aren't covered by Bulma classes */
  :global(p) {
    margin: 0;
    padding: 0;
  }

  :global(.word-link) {
    text-decoration: underline;
    text-decoration-color: rgba(50, 115, 220, 0.3);
    text-underline-offset: 3px;
  }
  
  :global(.word-link:hover) {
    text-decoration-color: var(--dark-primary);
  }
  
  /* Ensure consistent styling for any nested elements */
  :global(br) {
    display: block;
    content: "";
    margin-top: 0.5rem;
  }
</style> 