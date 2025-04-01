<!--
  MiniWordformList.svelte - A component for displaying a list of MiniWordform components
  
  This component manages the container and layout for a collection of wordforms,
  with optional empty state messaging.
  
  Props:
    wordforms: Array of wordform objects with the following properties:
      - wordform: string - The word text
      - translation: string | null - Optional translation
      - href: string - Link target for the word
      - notes: string | null - Optional contextual notes
    emptyMessage: string - Optional message to display when no wordforms are present
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import MiniWordform from './MiniWordform.svelte';
  
  // Define the type for wordform objects
  type WordformData = {
    wordform: string;
    translation: string | null;
    href: string;
    notes?: string | null;
    ordering?: number;
  };
  
  export let wordforms: WordformData[] = [];
  export let emptyMessage: string = "No words found";
  
  onMount(() => {
    console.log('MiniWordformList component mounted!', { wordformsCount: wordforms.length });
  });
  
  // Sort wordforms by ordering if available
  $: sortedWordforms = [...wordforms].sort((a, b) => {
    if (a.ordering !== undefined && b.ordering !== undefined) {
      return a.ordering - b.ordering;
    }
    return 0;
  });
</script>

<!-- Component template -->
{#if sortedWordforms.length > 0}
  <div class="wordforms-list">
    {#each sortedWordforms as wordform, i}
      <MiniWordform 
        wordform={wordform.wordform} 
        translation={wordform.translation} 
        href={wordform.href} 
        notes={wordform.notes || null} 
      />
    {/each}
  </div>
{:else}
  <p class="no-entries"><em>{emptyMessage}</em></p>
{/if}

<!-- Component styles -->
<style>
  .wordforms-list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .no-entries {
    color: #666;
    font-style: italic;
  }
</style>