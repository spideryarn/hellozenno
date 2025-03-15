<!--
  MiniPhrase.svelte - A compact phrase display component
  
  Used for displaying phrases in lists and references throughout the application.
  When used in lists, wrap in a container with:
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  
  Props:
    phrase: string - The canonical form of the phrase to display
    translations: string[] | null - Optional translations
    href: string - Link target for the phrase
    notes: string | null - Optional contextual notes (displayed inline in parentheses)
    part_of_speech: string | null - Optional part of speech
-->

<!-- Define the props -->
<script lang="ts">
  import { onMount } from 'svelte';

  // Declare types for Tippy
  declare global {
    interface Window {
      tippy: any; // We could make this more specific if needed
    }
    interface Element {
      _tippy?: any;
    }
  }

  export let phrase: string;
  export let translations: string[] | null = null;
  export let href: string;
  export let notes: string | null = null;
  export let part_of_speech: string | null = null;

  let phraseLink: HTMLElement;

  onMount(() => {
    console.log('MiniPhrase component mounted!', { phrase, href });
    
    // Tooltip functionality disabled as it's not needed for phrases
  });
</script>

<!-- Component template -->
<div class="mini-phrase">
  <a {href} class="phrase-link" bind:this={phraseLink}>
    <div class="phrase-content">
      <span class="phrase">{phrase}</span>
      {#if translations && translations.length > 0}
        <span class="translation">- {translations.join(', ')}</span>
      {/if}
      {#if part_of_speech}
        <span class="part-of-speech">{part_of_speech}</span>
      {/if}
      {#if notes}
        <span class="notes">({notes})</span>
      {/if}
    </div>
  </a>
</div>

<!-- Component styles -->
<style>
  .mini-phrase {
    margin: 0.25rem 0;
    display: inline-block;
    margin-right: 1rem;
  }

  .phrase-link {
    text-decoration: none;
    color: inherit;
    display: block;
  }

  .phrase-content {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    background-color: #f0f4ff; /* Light blue background to distinguish from words */
    transition: all 0.2s;
  }

  .phrase-content:hover {
    background-color: #e0e8ff;
  }

  .phrase {
    font-size: 1rem;
    line-height: 1.4;
  }

  .translation {
    font-size: 0.875rem;
    color: #64748b;
    margin-left: 0.25rem;
  }

  .part-of-speech {
    font-size: 0.75rem;
    color: #475569;
    font-style: italic;
    background-color: #f1f5f9;
    padding: 0.125rem 0.25rem;
    border-radius: 0.125rem;
    margin-left: 0.25rem;
  }

  .notes {
    font-size: 0.875rem;
    color: #64748b;
    font-style: italic;
    margin-left: 0.25rem;
  }
</style>