<script lang="ts">
  import WordformCard from '$lib/components/WordformCard.svelte';
  import SourcefileFooter from './SourcefileFooter.svelte';
  import type { Navigation } from '$lib/types/sourcefile';
  
  interface Wordform {
    wordform: string;
    lemma: string;
    frequency: number;
    translations: string[];
    pos: string; // Part of speech
    new_in_file: boolean;
  }
  
  export let wordforms: Wordform[] = [];
  export let target_language_code: string;
  // Add navigation props for bottom navigation
  export let navigation: Navigation = undefined as unknown as Navigation;
  export let sourcedir_slug: string = '';
  export let sourcefile_slug: string = '';
  
  // Reference to the container element for height measurement
  let wordsContainerElement: HTMLElement;
</script>

<div class="words-container" bind:this={wordsContainerElement}>
  <h2>Words ({wordforms.length})</h2>
  
  {#if wordforms.length === 0}
    <p class="no-content"><em>No words available for this file yet. Try processing the file first.</em></p>
  {:else}
    <div class="wordform-grid">
      {#each wordforms as wordform}
        <div class={wordform.new_in_file ? 'new-word' : ''}>
          <WordformCard
            wordform={wordform.wordform}
            translations={wordform.translations}
            part_of_speech={wordform.pos}
            lemma={wordform.lemma}
            {target_language_code}
          />
        </div>
      {/each}
    </div>
    
    <SourcefileFooter 
      {navigation}
      {target_language_code}
      {sourcedir_slug}
      view="words"
      contentRef={wordsContainerElement}
      minContentHeight={500}
    />
  {/if}
</div>

<style>
  .words-container {
    margin-top: 1rem;
  }
  
  .wordform-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .new-word {
    position: relative;
  }
  
  .new-word::before {
    content: "New";
    position: absolute;
    top: -0.5rem;
    right: -0.5rem;
    background-color: #4CAD53;
    color: white;
    font-size: 0.75rem;
    padding: 0.2rem 0.5rem;
    border-radius: 1rem;
    z-index: 1;
  }
  
  .no-content {
    color: #666;
    font-style: italic;
    margin-top: 1rem;
  }
  
  
</style> 