<script lang="ts">
  import type { PageData } from './$types';
  import { page } from '$app/stores';
  import SearchResults from '$lib/components/SearchResults.svelte';
  
  export let data: PageData;
  
  // Get language name from page data if not present in result
  $: result = data.searchResults;
  $: if (result && !result.target_language_name && data.parentData) {
    result.target_language_name = data.parentData.target_language_name;
  }
</script>

<svelte:head>
  <title>Search Results - {result?.target_language_name || ''}</title>
</svelte:head>

<div class="container mt-4">
  {#if !result}
    <!-- Loading indicator -->
    <div class="d-flex justify-content-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <p class="text-center mt-3">Searching...</p>
  {:else}
    <!-- Display search results -->
    <SearchResults results={result} />
  {/if}
</div>