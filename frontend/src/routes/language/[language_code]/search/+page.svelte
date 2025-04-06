<script lang="ts">
  import type { PageData } from './$types';
  import { goto } from '$app/navigation';
  import { unifiedSearch } from '$lib/api';
  import type { SearchResult } from '$lib/types';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  
  export let data: PageData;
  
  let query = data.query || '';
  let result: SearchResult | null = data.initialResult || null;
  let loading = false;
  
  // Ensure query is properly set from URL on mount and perform search if needed
  onMount(() => {
    // Get the current query parameter from the URL
    const urlQuery = $page.url.searchParams.get('q') || '';
    
    // Update query with the URL parameter
    query = urlQuery;
    
    // If we have a query parameter but no valid search result, perform the search
    if (urlQuery && (!result || result.status === 'empty_query')) {
      handleSearch();
    }
    
    // If no query and no result, show empty state
    if (!urlQuery && !result) {
      result = {
        status: 'empty_query',
        query: '',
        target_language_code: data.language_code,
        target_language_name: data.langName,
        data: {}
      };
    }
  });
  
  async function handleSearch() {
    if (!query.trim()) {
      result = {
        status: 'empty_query',
        query: '',
        target_language_code: data.language_code,
        target_language_name: data.langName,
        data: {}
      };
      return;
    }
    
    loading = true;
    
    // Immediately perform the search without updating the URL first
    result = await unifiedSearch(data.language_code, query);
    
    // Handle direct navigation for single matches without showing the search results first
    if (result.status === 'redirect') {
      // Go directly to the wordform page for redirect status
      goto(`/language/${data.language_code}/wordform/${result.data.redirect_to}`);
    } else if (result.status === 'found') {
      // For exact matches, go directly to the appropriate page
      const wordform = result.data.wordform_metadata.wordform;
      const lemma = result.data.wordform_metadata.lemma;
      
      if (wordform === lemma) {
        goto(`/language/${data.language_code}/lemma/${encodeURIComponent(lemma)}`);
      } else {
        goto(`/language/${data.language_code}/wordform/${encodeURIComponent(wordform)}`);
      }
    } else {
      // For other statuses (multiple_matches, invalid, etc.), update URL and show results
      goto(`/language/${data.language_code}/search?q=${encodeURIComponent(query)}`, { 
        replaceState: true,
        keepFocus: true,
        noScroll: true
      });
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>
    {query 
      ? `Search results for "${query}" - ${data.langName || 'Language'}`
      : `Search ${data.langName || 'Language'}`}
  </title>
</svelte:head>

<div class="container">
  <h1>Search {data.langName || 'Language'} Words</h1>
  
  <form on:submit|preventDefault={handleSearch}>
    <div class="input-group mb-4">
      <input 
        type="text" 
        bind:value={query} 
        placeholder={`Enter a ${data.langName || ''} word to search...`}
        aria-label="Search term"
        class="form-control"
      />
      <button type="submit" class="btn btn-primary" disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
    </div>
  </form>
  
  {#if loading}
    <div class="d-flex justify-content-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  {:else if result}
    <div class="search-results">
      <!-- Empty query state -->
      {#if result.status === 'empty_query'}
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Search {data.langName || 'Language'} Words</h5>
            <p>Enter a word to search. You can search for:</p>
            <ul>
              <li>Words in {data.langName || 'this language'}</li>
              <li>English words to find {data.langName || 'foreign language'} translations</li>
              <li>Word forms and dictionary forms (lemmas)</li>
            </ul>
          </div>
        </div>
      
      <!-- Exact match found -->
      {:else if result.status === 'found'}
        <div class="card mb-4">
          <div class="card-header bg-success text-white">
            <h5 class="card-title mb-0">Match Found</h5>
          </div>
          <div class="card-body">
            <h2 class="hz-foreign-text">{result.data.wordform_metadata.wordform}</h2>
            
            <div class="wordform-details">
              <p>
                <strong>Translation:</strong> 
                {#if result.data.wordform_metadata.translations}
                  {result.data.wordform_metadata.translations.join('; ')}
                {:else}
                  No translation available
                {/if}
              </p>
              
              <p>
                <strong>Part of Speech:</strong> 
                {result.data.wordform_metadata.part_of_speech || 'Unknown'}
              </p>
              
              <p>
                <strong>Form Type:</strong> 
                {result.data.wordform_metadata.inflection_type || 'Unknown'}
              </p>
              
              <p>
                <strong>Dictionary Form (Lemma):</strong> 
                {#if result.data.wordform_metadata.lemma}
                  <a href="/language/{result.target_language_code}/lemma/{encodeURIComponent(result.data.wordform_metadata.lemma)}" class="hz-foreign-text">
                    {result.data.wordform_metadata.lemma}
                  </a>
                {:else}
                  <em>No lemma linked</em>
                {/if}
              </p>
            </div>
            
            <a href="/language/{result.target_language_code}/wordform/{encodeURIComponent(result.data.wordform_metadata.wordform)}" class="btn btn-primary mt-3">
              View full details
            </a>
          </div>
        </div>
      
      <!-- Multiple matches -->
      {:else if result.status === 'multiple_matches'}
        <!-- Target language matches -->
        {#if result.data.target_language_results?.matches?.length > 0}
          <div class="card mb-4">
            <div class="card-header bg-primary text-white">
              <h5 class="card-title mb-0">{result.target_language_name} Matches</h5>
            </div>
            <div class="card-body">
              <ul class="list-group list-group-flush">
                {#each result.data.target_language_results.matches as match}
                  <li class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <a href="/language/{result.target_language_code}/wordform/{encodeURIComponent(match.target_language_wordform)}" class="h5 mb-1 hz-foreign-text">
                          {match.target_language_wordform}
                        </a>
                        <small class="text-muted d-block">
                          {match.part_of_speech || ''} • {match.inflection_type || ''}
                        </small>
                        <small class="d-block">
                          {#if match.target_language_lemma && match.target_language_lemma !== match.target_language_wordform}
                            <strong>Lemma:</strong> 
                            <a href="/language/{result.target_language_code}/lemma/{encodeURIComponent(match.target_language_lemma)}" class="hz-foreign-text">
                              {match.target_language_lemma}
                            </a>
                          {/if}
                        </small>
                      </div>
                      <div class="text-end">
                        <div class="translations">
                          {match.english ? match.english.join(", ") : ''}
                        </div>
                      </div>
                    </div>
                  </li>
                {/each}
              </ul>
            </div>
          </div>
        {/if}
        
        <!-- Possible misspellings for target language -->
        {#if result.data.target_language_results?.possible_misspellings?.length > 0}
          <div class="card mb-4">
            <div class="card-header bg-warning text-dark">
              <h5 class="card-title mb-0">Did you mean one of these?</h5>
            </div>
            <div class="card-body">
              <ul class="list-group list-group-flush">
                {#each result.data.target_language_results.possible_misspellings as suggestion}
                  <li class="list-group-item">
                    <a href="/language/{result.target_language_code}/search?q={encodeURIComponent(suggestion)}" class="hz-foreign-text">
                      {suggestion}
                    </a>
                  </li>
                {/each}
              </ul>
            </div>
          </div>
        {/if}
        
        <!-- English translation matches -->
        {#if result.data.english_results?.matches?.length > 0}
          <div class="card mb-4">
            <div class="card-header bg-secondary text-white">
              <h5 class="card-title mb-0">{result.target_language_name} words matching English term "{result.query}"</h5>
            </div>
            <div class="card-body">
              <ul class="list-group list-group-flush">
                {#each result.data.english_results.matches as match}
                  <li class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <a href="/language/{result.target_language_code}/wordform/{encodeURIComponent(match.target_language_wordform)}" class="h5 mb-1 hz-foreign-text">
                          {match.target_language_wordform}
                        </a>
                        <small class="text-muted d-block">
                          {match.part_of_speech || ''} • {match.inflection_type || ''}
                        </small>
                        <small class="d-block">
                          {#if match.target_language_lemma && match.target_language_lemma !== match.target_language_wordform}
                            <strong>Lemma:</strong> 
                            <a href="/language/{result.target_language_code}/lemma/{encodeURIComponent(match.target_language_lemma)}" class="hz-foreign-text">
                              {match.target_language_lemma}
                            </a>
                          {/if}
                        </small>
                      </div>
                      <div class="text-end">
                        <div class="translations">
                          {match.english ? match.english.join(", ") : ''}
                        </div>
                      </div>
                    </div>
                  </li>
                {/each}
              </ul>
            </div>
          </div>
        {/if}
      
      <!-- Invalid word -->
      {:else if result.status === 'invalid'}
        <div class="card mb-4">
          <div class="card-header bg-danger text-white">
            <h5 class="card-title mb-0">No Results Found</h5>
          </div>
          <div class="card-body">
            <p>"{result.query}" did not match any words in {result.target_language_name} or English translations.</p>
            
            {#if result.data.possible_misspellings?.length > 0}
              <p>Did you mean:</p>
              <ul>
                {#each result.data.possible_misspellings as suggestion}
                  <li>
                    <a href="/language/{result.target_language_code}/search?q={encodeURIComponent(suggestion)}" class="hz-foreign-text">
                      {suggestion}
                    </a>
                  </li>
                {/each}
              </ul>
            {/if}
            
            <p class="mt-3">Try another search term or check your spelling.</p>
          </div>
        </div>
      
      <!-- Error state -->
      {:else if result.status === 'error'}
        <div class="card mb-4">
          <div class="card-header bg-danger text-white">
            <h5 class="card-title mb-0">Search Error</h5>
          </div>
          <div class="card-body">
            <p>Sorry, we encountered an error processing your search.</p>
            <p class="text-danger">{result.error || 'Unknown error occurred'}</p>
            <p>Please try again later or with a different search term.</p>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .search-results {
    margin-bottom: 2rem;
  }
  
  .hz-foreign-text {
    font-family: var(--bs-font-sans-serif);
  }
</style>