<script lang="ts">
  import type { PageData } from './$types';
  import { goto } from '$app/navigation';
  import { unifiedSearch } from '$lib/api';
  import type { SearchResult } from '$lib/types';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { getContext } from 'svelte';
  import type { SupabaseClient } from '@supabase/supabase-js';
  import { X, ClipboardText } from 'phosphor-svelte';
  
  export let data: PageData;
  // Get supabase client from context if available
  const supabase = getContext<SupabaseClient>('supabase');
  
  let query = data.query || '';
  let result: SearchResult | null = data.initialResult || null;
  let loading = false;
  let searchInput: HTMLInputElement;
  
  // Ensure query is properly set from URL on mount and perform search if needed
  onMount(() => {
    // Get the current query parameter from the URL
    const urlQuery = $page.url.searchParams.get('q') || '';
    
    // Update query with the URL parameter
    query = urlQuery;
    
    // If we have a query parameter but no valid search result, perform the search
    if (urlQuery && (!result || result.status === 'empty_query')) {
      handleClientSearch(urlQuery);
    }
    
    // If no query and no result, show empty state
    if (!urlQuery && !result) {
      result = {
        status: 'empty_query',
        query: '',
        target_language_code: data.target_language_code,
        target_language_name: data.langName,
        data: {}
      };
    }
  });
  
  // This is a client-side search function to be used only when needed
  // (like when the user navigates directly to the page with a query parameter)
  async function handleClientSearch(searchQuery: string) {
    loading = true;
    
    try {
      // Use the supabase client from context if available
      result = await unifiedSearch(supabase, data.target_language_code, searchQuery);
      
      // Handle direct navigation for single matches
      if (result.status === 'redirect') {
        goto(`/language/${data.target_language_code}/wordform/${result.data.redirect_to}`);
      } else if (result.status === 'found') {
        const wordform = result.data.wordform_metadata.wordform;
        const lemma = result.data.wordform_metadata.lemma;
        
        if (wordform === lemma) {
          goto(`/language/${data.target_language_code}/lemma/${encodeURIComponent(lemma)}`);
        } else {
          goto(`/language/${data.target_language_code}/wordform/${encodeURIComponent(wordform)}`);
        }
      }
    } catch (error) {
      console.error('Client-side search error:', error);
      result = {
        status: 'error',
        query: searchQuery,
        target_language_code: data.target_language_code,
        target_language_name: data.langName,
        error: error instanceof Error ? error.message : 'Unknown error',
        data: {}
      };
    } finally {
      loading = false;
    }
  }
  
  async function handleSearch() {
    if (!query.trim()) {
      result = {
        status: 'empty_query',
        query: '',
        target_language_code: data.target_language_code,
        target_language_name: data.langName,
        data: {}
      };
      return;
    }
    
    // Update the URL to include the query parameter
    // This will trigger a server-side load with the query parameter
    // The server-side load already has access to the session via locals
    goto(`/language/${data.target_language_code}/search?q=${encodeURIComponent(query)}`);
  }
  
  function clearSearch() {
    query = '';
    if (searchInput) {
      searchInput.focus();
    }
  }
  
  async function pasteFromClipboard() {
    try {
      const text = await navigator.clipboard.readText();
      query = text;
      if (searchInput) {
        searchInput.focus();
      }
    } catch (error) {
      console.error('Failed to read clipboard:', error);
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
        bind:this={searchInput}
        placeholder={`Enter a ${data.langName || ''} word to search...`}
        aria-label="Search term"
        class="form-control"
      />
      {#if query}
        <button 
          type="button" 
          class="btn btn-outline-secondary" 
          aria-label="Clear search" 
          title="Clear search"
          on:click={clearSearch}
        >
          <X size={16} />
        </button>
      {/if}
      <button 
        type="button" 
        class="btn btn-outline-secondary" 
        aria-label="Paste from clipboard" 
        title="Paste from clipboard"
        on:click={pasteFromClipboard}
      >
        <ClipboardText size={16} />
      </button>
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