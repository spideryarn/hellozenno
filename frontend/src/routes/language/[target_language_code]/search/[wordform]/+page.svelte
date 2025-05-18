<script lang="ts">
  import type { PageData } from './$types';
  // import { page } from '$app/stores'; // No longer needed if language_name comes from data prop
  import SearchResults from '$lib/components/SearchResults.svelte';
  import { browser } from '$app/environment';

  export let data: PageData; // data will have { searchResults, language_name (from layout), ... }
  
  // Log the received searchResults to see its structure
  $: if (browser && data && data.searchResults) {
    console.log('Search Page (+page.svelte) received searchResults:', JSON.parse(JSON.stringify(data.searchResults)));
  }

  // Assuming searchResults has a 'query' property for the search term
  // and a 'data' property for the actual results, or specific category arrays.
  // Also need to handle 'status' for different display modes (e.g., invalid, multiple_matches)
  $: searchResultsData = data.searchResults;
  $: query = searchResultsData?.query ?? '';
  $: status = searchResultsData?.status;
  // Actual results might be in searchResults.data.target_language_results.matches or similar

  // Determine the language name to display
  // Prefer language_name from the searchResults if available (it's specific to the result's context)
  // Otherwise, fallback to the general language_name for the page (from layout data)
  $: display_language_name = searchResultsData?.target_language_name || data.language_name || '';
</script>

<svelte:head>
  <title>Search Results for "{query}" - {display_language_name}</title>
</svelte:head>

<div class="container mt-4">
  {#if !searchResultsData}
    <!-- Loading indicator -->
    <div class="d-flex justify-content-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <p class="text-center mt-3">Searching...</p>
  {:else}
    <!-- Display search results -->
    <SearchResults results={searchResultsData} />
  {/if}
</div>