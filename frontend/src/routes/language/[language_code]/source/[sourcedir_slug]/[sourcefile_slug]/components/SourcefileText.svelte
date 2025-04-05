<script lang="ts">
  import type { Sourcefile } from '$lib/types/sourcefile';
  import EnhancedText from '$lib/components/EnhancedText.svelte';
  
  export const sourcefile: Sourcefile = undefined as unknown as Sourcefile;
  export let enhanced_text: string | null = null;
  export let text_target: string | null = null;
  export const text_english: string | null = null;
  export let language_code: string;
</script>

<div class="text-content">
  <h2>Text</h2>
  {#if enhanced_text}
    <EnhancedText html={enhanced_text} {language_code} />
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

<style>
  .text-content {
    margin-bottom: 2rem;
    max-width: 100%;
    padding: 0;
  }
  
  .plain-text p {
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
    .plain-text p {
      padding: 0 5px; /* Minimal padding on mobile */
    }
  }
</style>