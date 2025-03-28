<script lang="ts">
  import { onMount } from 'svelte';
  import type { SentenceData, FlashcardState } from '../lib/types';
  import { advanceStage, previousStage, getButtonLabels } from '../lib/flashcard-utils';
  import MiniLemma from './MiniLemma.svelte';
  import '../styles/bulma-imports.css'; // Import Bulma CSS

  // Props
  export let sentence: SentenceData;
  export let targetLanguageCode: string;
  // This value is received from the parent but not used within the component itself
  export const targetLanguageName = '';
  export let sourcefile: string | null = null;
  export let sourcedir: string | null = null;

  // State
  let state: FlashcardState = {
    stage: 1,
    sentence,
    isLoading: false,
    error: null,
    sourceFilter: {
      type: sourcefile ? 'sourcefile' : sourcedir ? 'sourcedir' : null,
      slug: sourcefile || sourcedir || null
    }
  };

  // Audio element reference
  let audioElement: HTMLAudioElement;

  // State for lemma data
  type LemmaData = {
    lemma: string;
    part_of_speech: string;
    translations: string[];
    isLoading: boolean;
    error: string | null;
  };
  
  let lemmasData: Record<string, LemmaData> = {};
  
  // Initialize lemmasData with empty values
  if (sentence.lemmaWords) {
    sentence.lemmaWords.forEach(lemma => {
      lemmasData[lemma] = {
        lemma,
        part_of_speech: '',
        translations: [],
        isLoading: true,
        error: null
      };
    });
  }
  
  import { RouteName, resolveRoute } from '../../../static/js/generated/routes';
  
  // Fetch lemma data for each lemma
  async function fetchLemmaData(lemma: string) {
    try {
      // Add debug logs to trace the API call
      console.log(`Fetching lemma data for ${lemma} with language code ${targetLanguageCode}`);
      
      const apiUrl = resolveRoute(RouteName.LEMMA_API_GET_LEMMA_DATA_API, {
        target_language_code: targetLanguageCode,
        lemma: lemma
      });
      
      console.log(`API URL: ${apiUrl}`);
      
      const response = await fetch(apiUrl);
      if (!response.ok) {
        console.error(`API error status: ${response.status}`);
        throw new Error(`Failed to fetch lemma data for ${lemma}`);
      }
      
      const data = await response.json();
      console.log(`Lemma data received:`, data);
      
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

  // Button labels based on current stage
  $: buttonLabels = getButtonLabels(state.stage);

  // Handle left button click
  function handleLeftClick() {
    if (state.stage === 1) {
      // In stage 1, left button replays audio
      playAudio();
    } else {
      // In other stages, left button goes back a stage
      state = previousStage(state);
      if (state.stage === 1) {
        // If we went back to stage 1, play the audio again
        playAudio();
      }
    }
  }

  // Handle right button click
  function handleRightClick() {
    if (!buttonLabels.rightDisabled) {
      state = advanceStage(state);
      
      // When advancing to stage 3, fetch lemma data for all words
      if (state.stage === 3 && sentence.lemmaWords && sentence.lemmaWords.length > 0) {
        sentence.lemmaWords.forEach(fetchLemmaData);
      }
    }
  }

  // Handle next button click (get new sentence)
  function handleNextClick() {
    const params = new URLSearchParams();
    
    // Add sourcefile or sourcedir to URL if present
    if (sourcefile) {
      params.append('sourcefile', sourcefile);
    } else if (sourcedir) {
      params.append('sourcedir', sourcedir);
    }
    
    const queryString = params.toString() ? `?${params.toString()}` : '';
    const url = resolveRoute(RouteName.FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW, {
      target_language_code: targetLanguageCode
    });
    window.location.href = `${url}${queryString}`;
  }

  // Play audio function
  function playAudio() {
    if (audioElement) {
      audioElement.currentTime = 0;
      audioElement.play().catch(error => {
        console.error("Error playing audio:", error);
        // More informative error message with instructions
        state = { 
          ...state, 
          error: "Audio couldn't autoplay. Please use the Play Audio button to listen." 
        };
      });
    }
  }

  // Handle keyboard shortcuts
  function handleKeydown(event: KeyboardEvent) {
    // Ignore if user is typing in an input field
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
      return;
    }
    
    switch (event.key) {
      case 'ArrowLeft':
        handleLeftClick();
        break;
      case 'ArrowRight':
        handleRightClick();
        break;
      case 'Enter':
        handleNextClick();
        break;
    }
  }

  // Initialize the component
  onMount(() => {
    // Audio element is now defined in the HTML with autoplay attribute
    // No need to create it programmatically
    
    // Add keyboard event listener
    document.addEventListener('keydown', handleKeydown);
    
    // Cleanup on destroy
    return () => {
      document.removeEventListener('keydown', handleKeydown);
    };
  });
</script>

<div class="section py-4">
  <div class="container">
    {#if state.error}
      <div class="notification is-danger is-light">
        <button class="delete" aria-label="delete"></button>
        {state.error}
      </div>
    {/if}
    
    <!-- Source filter info banner -->
    {#if state.sourceFilter.type && state.sourceFilter.slug}
      <div class="notification is-info is-light mb-4">
        <button class="delete" on:click={() => window.location.href = resolveRoute(RouteName.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW, {
          target_language_code: targetLanguageCode
        })} aria-label="delete"></button>
        <span class="icon-text">
          <span class="icon">
            <i class="ph-fill ph-filter"></i>
          </span>
          <span>Filtered by {state.sourceFilter.type === 'sourcedir' ? 'directory' : 'file'}: 
          <strong>{state.sourceFilter.slug}</strong></span>
        </span>
      </div>
    {/if}
    
    <div class="card">
      <div class="card-content has-text-centered py-5">
        <!-- Audio element (hidden) with autoplay attribute -->
        <audio 
          src={sentence.audioUrl} 
          bind:this={audioElement} 
          preload="auto"
          autoplay
        ></audio>
        
        <!-- Stage 1: Initial audio stage -->
        {#if state.stage === 1}
          <div class="block my-6 py-4">
            <span class="icon is-large">
              <i class="fas fa-volume-up fa-2x has-text-primary"></i>
            </span>
            <p class="is-size-5 mt-3 has-text-grey">Listen to the audio</p>
          </div>
        {/if}
        
        <!-- Stage 2 & 3: Sentence -->
        {#if state.stage >= 2}
          <h3 class="title is-3 mt-5 mb-5">{sentence.text}</h3>
        {/if}
        
        <!-- Stage 3: Translation -->
        {#if state.stage >= 3}
          <p class="subtitle is-4 has-text-grey mb-6">{sentence.translation}</p>
          
          {#if sentence.lemmaWords && sentence.lemmaWords.length > 0}
            <div class="mt-6 pt-4 has-background-white-ter">
              <h3 class="title is-5 mb-4">Vocabulary</h3>
              <div class="box mx-auto" style="max-width: 600px;">
                {#each sentence.lemmaWords as lemma}
                  <div class="mb-3">
                    <MiniLemma 
                      lemma={lemma}
                      partOfSpeech={lemmasData[lemma]?.part_of_speech || ''}
                      translations={lemmasData[lemma]?.translations || []}
                      href={resolveRoute(RouteName.LEMMA_VIEWS_GET_LEMMA_METADATA_VW, {
                        target_language_code: targetLanguageCode,
                        lemma: lemma
                      })}
                    />
                    {#if lemmasData[lemma]?.isLoading}
                      <div class="has-text-grey is-size-7 is-italic ml-3 has-family-monospace mt-1">Loading lemma data...</div>
                    {/if}
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        {/if}
      </div>
      
      <div class="card-footer p-4 is-justify-content-center">
        <div class="field is-grouped">
          <p class="control">
            <button 
              class="button {state.stage === 1 ? 'is-info' : 'is-light'} is-medium"
              disabled={buttonLabels.leftDisabled} 
              on:click={handleLeftClick}
            >
              <span class="icon">
                <i class="fas fa-{state.stage === 1 ? 'play' : 'arrow-left'}"></i>
              </span>
              <span>{buttonLabels.left}</span>
              <span class="tag is-small ml-1 has-family-monospace">←</span>
            </button>
          </p>
          
          <p class="control">
            <button 
              class="button {state.stage === 3 ? 'is-info' : 'is-light'} is-medium"
              disabled={buttonLabels.rightDisabled} 
              on:click={handleRightClick}
            >
              <span class="icon">
                <i class="fas fa-{state.stage < 3 ? 'arrow-right' : 'eye'}"></i>
              </span>
              <span>{buttonLabels.right}</span>
              <span class="tag is-small ml-1 has-family-monospace">→</span>
            </button>
          </p>
          
          <p class="control">
            <button 
              class="button is-primary is-medium" 
              on:click={handleNextClick}
            >
              <span class="icon">
                <i class="fas fa-forward"></i>
              </span>
              <span>New Sentence</span>
              <span class="tag is-small ml-1 has-family-monospace">Enter</span>
            </button>
          </p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  /* Some minor custom styles to enhance Bulma */
  :global(.notification .delete) {
    top: 0.85rem;
  }
  
  :global(.card) {
    box-shadow: 0 0.5em 1em -0.125em rgba(10, 10, 10, 0.1), 0 0 0 1px rgba(10, 10, 10, 0.05);
    border-radius: 8px;
  }
  
  :global(.card-footer) {
    border-top: 1px solid #f0f0f0;
  }
</style>