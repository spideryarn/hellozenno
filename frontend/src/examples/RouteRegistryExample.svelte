<!--
  RouteRegistryExample.svelte - Example component showing how to use the URL registry
  
  This is an example component demonstrating the use of type-safe URL resolution
  using the generated TypeScript route definitions.
-->

<script lang="ts">
  import { onMount } from 'svelte';
  import { RouteName, resolveRoute } from '../../static/js/generated/routes';

  // Component props
  export let wordform: string;
  export let target_language_code: string;

  // Component state
  let previewData: any = null;
  let loading = false;
  let error: string | null = null;

  // Function to fetch word preview data using the URL registry
  async function fetchWordPreview() {
    loading = true;
    error = null;
    
    try {
      // Type-safe route resolution with auto-completion and parameter validation
      const url = resolveRoute(RouteName.WORDFORM_API_WORD_PREVIEW, {
        target_language_code: target_language_code,
        word: wordform
      });
      
      console.log(`Fetching word preview from: ${url}`);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }
      
      previewData = await response.json();
      console.log('Preview data:', previewData);
    } catch (err) {
      console.error('Error fetching word preview:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }
  
  onMount(fetchWordPreview);
</script>

<div class="word-preview">
  <h3>Word Preview: {wordform}</h3>
  
  {#if loading}
    <div class="loading">Loading...</div>
  {:else if error}
    <div class="error">Error: {error}</div>
  {:else if previewData}
    <div class="content">
      <h4>{previewData.lemma}</h4>
      {#if previewData.translation}
        <p class="translation">Translation: {previewData.translation}</p>
      {/if}
      {#if previewData.etymology}
        <p class="etymology">Etymology: {previewData.etymology}</p>
      {/if}
    </div>
  {:else}
    <div class="empty">No data available</div>
  {/if}
  
  <div class="info">
    <h4>Route Information:</h4>
    <pre>URL: {resolveRoute(RouteName.WORDFORM_API_WORD_PREVIEW, {
      target_language_code,
      word: wordform
    })}</pre>
    <pre>Original Route Template: {RouteName.WORDFORM_API_WORD_PREVIEW}</pre>
  </div>
</div>

<style>
  .word-preview {
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    padding: 1rem;
    background-color: #f8fafc;
    max-width: 500px;
    margin: 1rem auto;
  }
  
  h3 {
    margin-top: 0;
    font-size: 1.25rem;
    color: #334155;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 0.5rem;
  }
  
  .loading {
    padding: 1rem;
    text-align: center;
    color: #64748b;
  }
  
  .error {
    padding: 1rem;
    color: #ef4444;
    background-color: #fee2e2;
    border-radius: 0.25rem;
  }
  
  .content {
    padding: 0.5rem;
  }
  
  .content h4 {
    margin-top: 0;
    color: #0f172a;
  }
  
  .translation, .etymology {
    margin: 0.5rem 0;
    font-size: 0.875rem;
  }
  
  .translation {
    color: #64748b;
  }
  
  .etymology {
    color: #475569;
    font-style: italic;
  }
  
  .empty {
    padding: 1rem;
    text-align: center;
    color: #94a3b8;
    font-style: italic;
  }
  
  .info {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px dashed #e2e8f0;
  }
  
  .info h4 {
    margin-top: 0;
    font-size: 0.875rem;
    color: #475569;
  }
  
  pre {
    background-color: #f1f5f9;
    padding: 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    overflow-x: auto;
    color: #334155;
  }
</style>