<script lang="ts">
  import type { Sourcefile } from '$lib/types/sourcefile';
  import EnhancedText from '$lib/components/EnhancedText.svelte';
  
  export const sourcefile: Sourcefile = undefined as unknown as Sourcefile;
  export let enhanced_text: string | null = null;
  export let text_target: string | null = null;
  export let recognized_words: Array<{
    word: string;
    start: number;
    end: number;
    lemma: string;
    translations: string[];
    part_of_speech?: string;
    inflection_type?: string;
  }> = [];
  export const text_english: string | null = null;
  // VERY IMPORTANT: target_language_code is required by EnhancedText for generating API URLs
  // Previously named language_code, renamed for consistency with API
  export let language_code: string;

  // Debug flag - set to true to see what data is available
  const debug = import.meta.env.DEV && false;
</script>

<div class="text-content">
  <h2>Text</h2>
  
  {#if debug}
    <div class="debug-container">
      <h3>Debug: Available Data</h3>
      <div><strong>HTML Mode:</strong> {enhanced_text ? 'Yes' : 'No'}</div>
      <div><strong>Structured Mode:</strong> {recognized_words?.length ? 'Yes' : 'No'}</div>
      <div><strong>Language Code:</strong> {language_code}</div>
      <div><strong>Recognized Words:</strong> {recognized_words?.length || 0}</div>
      <pre>{JSON.stringify(recognized_words?.[0] || {}, null, 2)}</pre>
    </div>
  {/if}

  {#if recognized_words?.length && text_target}
    <!-- Preferred mode: Using the structured data approach for better separation of concerns -->
    <EnhancedText 
      text={text_target} 
      recognizedWords={recognized_words} 
      target_language_code={language_code} 
    />
  {:else if enhanced_text}
    <!-- DEPRECATED: Legacy HTML-based approach. This mode uses pre-generated HTML from the backend,
         which mixes content with presentation. It should eventually be removed once all
         components are updated to use the structured data approach. -->
    <EnhancedText 
      html={enhanced_text} 
      target_language_code={language_code} 
    />
  {:else if text_target}
    <!-- Fallback: Just show plain text -->
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

  .debug-container {
    margin-bottom: 2rem;
    padding: 1rem;
    border: 1px solid #ddd;
    background-color: #f8f9fa;
    border-radius: 4px;
    font-family: monospace;
  }
  
  /* Responsive styling for different screen sizes */
  @media (max-width: 768px) {
    .text-content,
    .plain-text p {
      padding: 0 5px; /* Minimal padding on mobile */
    }
  }
</style>