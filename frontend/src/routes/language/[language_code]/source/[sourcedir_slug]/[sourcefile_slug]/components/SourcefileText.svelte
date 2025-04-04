<script lang="ts">
  import type { Sourcefile } from '$lib/types/sourcefile';
  
  export let sourcefile: Sourcefile;
  export let enhanced_text: string | null = null;
  export let text_target: string | null = null;
  export let text_english: string | null = null;
  
  // State for translation collapse/expand
  let isTranslationExpanded = false;
  
  // Split the translation into paragraphs if available
  $: translationParagraphs = text_english ? text_english.split('\n\n') : [];
</script>

<div class="text-content">
  <h2>Text</h2>
  {#if enhanced_text}
    <div class="enhanced-text">
      {@html enhanced_text}
    </div>
  {:else if text_target}
    <div class="plain-text">
      {#each text_target.split('\n\n') as paragraph}
        {#if paragraph}
          <p>{paragraph}</p>
        {/if}
      {/each}
    </div>
  {:else}
    <p class="no-content">No text available</p>
  {/if}
</div>

<details bind:open={isTranslationExpanded}>
  <summary><h2 class="translation-header">Translation</h2></summary>
  <div class="translated-text">
    {#if text_english}
      {#each translationParagraphs as paragraph}
        {#if paragraph}
          <p>{paragraph}</p>
        {/if}
      {/each}
    {:else}
      <p class="no-content"><em>No translation available</em></p>
    {/if}
  </div>
</details>

<style>
  .text-content {
    margin-bottom: 2rem;
    max-width: 100%;
    padding: 0;
  }
  
  .enhanced-text {
    line-height: 1.6;
    max-width: 65ch; /* Ensure maximum of ~65 characters per line for readability */
  }
  
  .enhanced-text :global(a.word-link) {
    color: #4CAD53;
    text-decoration: none;
    border-bottom: 1px dotted #4CAD53;
  }
  
  .enhanced-text :global(a.word-link:hover) {
    background-color: rgba(76, 173, 83, 0.1);
  }
  
  /* Adjust spacing for enhanced text paragraphs */
  .enhanced-text :global(p) {
    margin-bottom: 1rem;
    padding: 0;
  }
  
  .plain-text p {
    margin-bottom: 1rem;
    line-height: 1.6;
    max-width: 65ch;
  }
  
  .translation-header {
    display: inline;
    margin: 0;
    font-size: 1.5rem;
  }
  
  summary {
    cursor: pointer;
    margin-bottom: 1rem;
  }
  
  .translated-text {
    padding: 1rem;
    background-color: rgba(0, 0, 0, 0.03);
    border-radius: 4px;
  }
  
  .translated-text p {
    margin-bottom: 1rem;
    line-height: 1.6;
    max-width: 65ch;
  }
  
  .no-content {
    color: #666;
    font-style: italic;
  }
  
  /* Responsive styling for different screen sizes */
  @media (max-width: 768px) {
    .text-content,
    .enhanced-text,
    .plain-text p,
    .translated-text p {
      padding: 0 5px; /* Minimal padding on mobile */
    }
  }
</style> 