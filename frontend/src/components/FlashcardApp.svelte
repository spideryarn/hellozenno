<script lang="ts">
  import { onMount } from 'svelte';
  import type { SentenceData, FlashcardState } from '../lib/types';
  import { advanceStage, previousStage, getButtonLabels } from '../lib/flashcard-utils';

  // Props
  export let sentence: SentenceData;
  export let targetLanguageCode: string;
  export let targetLanguageName: string;
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
    window.location.href = `/${targetLanguageCode}/flashcards2/random${queryString}`;
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

<div class="flashcard">
  {#if state.error}
    <div class="error-message">
      {state.error}
    </div>
  {/if}
  
  <div class="flashcard-content">
    <!-- Audio element (hidden) with autoplay attribute similar to v1 -->
    <audio 
      src={sentence.audioUrl} 
      bind:this={audioElement} 
      preload="auto"
      autoplay
    ></audio>
    
    <!-- Stage 2 & 3: Sentence -->
    {#if state.stage >= 2}
      <h3 class="sentence-text">{sentence.text}</h3>
    {/if}
    
    <!-- Stage 3: Translation -->
    {#if state.stage >= 3}
      <p class="translation-text">{sentence.translation}</p>
      
      {#if sentence.lemmaWords && sentence.lemmaWords.length > 0}
        <p class="lemma-words">
          Vocabulary: {sentence.lemmaWords.join(', ')}
        </p>
      {/if}
    {/if}
  </div>
  
  <div class="flashcard-controls">
    <button 
      class="flashcard-btn" 
      class:active={state.stage === 1} 
      disabled={buttonLabels.leftDisabled} 
      on:click={handleLeftClick}
    >
      <i class="fas fa-{state.stage === 1 ? 'play' : 'arrow-left'}"></i>
      {buttonLabels.left}
      <span class="shortcut-hint">(←)</span>
    </button>
    
    <button 
      class="flashcard-btn" 
      class:active={state.stage === 3} 
      disabled={buttonLabels.rightDisabled} 
      on:click={handleRightClick}
    >
      <i class="fas fa-{state.stage < 3 ? 'arrow-right' : 'eye'}"></i>
      {buttonLabels.right}
      <span class="shortcut-hint">(→)</span>
    </button>
    
    <button 
      class="flashcard-btn next-btn" 
      on:click={handleNextClick}
    >
      <i class="fas fa-forward"></i>
      New Sentence
      <span class="shortcut-hint">(Enter)</span>
    </button>
  </div>
</div>

<style>
  .flashcard {
    display: flex;
    flex-direction: column;
    min-height: 300px;
    width: 100%;
    padding: 1rem;
  }
  
  .error-message {
    background-color: #fee2e2;
    color: #b91c1c;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin-bottom: 1rem;
  }
  
  .flashcard-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-bottom: 1rem;
    min-height: 150px;
  }
  
  .sentence-text {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    text-align: center;
    line-height: 1.4;
  }
  
  .translation-text {
    font-size: 1.25rem;
    color: #64748b;
    margin-bottom: 0.5rem;
    text-align: center;
  }
  
  .lemma-words {
    font-size: 1rem;
    color: #94a3b8;
    text-align: center;
    font-style: italic;
  }
  
  .flashcard-controls {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
  }
  
  .flashcard-btn {
    font-size: 1.25rem;
    padding: 0.75rem;
    border: 2px solid #2563eb;
    border-radius: 8px;
    background-color: white;
    color: #2563eb;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
  }
  
  .flashcard-btn:hover:not(:disabled) {
    background-color: #2563eb;
    color: white;
  }
  
  .flashcard-btn.active {
    background-color: #2563eb;
    color: white;
  }
  
  .flashcard-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .next-btn {
    background-color: #10b981;
    border-color: #10b981;
    color: white;
  }
  
  .next-btn:hover {
    background-color: #059669;
    border-color: #059669;
  }
  
  .shortcut-hint {
    font-size: 0.9rem;
    opacity: 0.7;
    margin-left: 0.25rem;
  }
  
  /* Desktop layout */
  @media (min-width: 768px) {
    .flashcard-controls {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
    }
    
    .next-btn {
      grid-column: span 2;
    }
  }
</style>