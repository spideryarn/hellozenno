<script lang="ts">
  import type { Sourcefile } from '$lib/types/sourcefile';
  
  export let sourcefile: Sourcefile;
  export let text_english: string | null = null;
  
  // Split the translation into paragraphs if available
  $: translationParagraphs = text_english ? text_english.split('\n\n') : [];
</script>

<div class="translation-content">
  <h2>Translation</h2>
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
</div>

<style>
  .translation-content {
    margin-bottom: 2rem;
    max-width: 100%;
    padding: 0;
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
    .translation-content,
    .translated-text p {
      padding: 0 5px; /* Minimal padding on mobile */
    }
  }
</style> 