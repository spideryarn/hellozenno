<script lang="ts">
  import type { PageData } from './$types';
  import { goto } from '$app/navigation';
  import { unifiedSearch } from '$lib/api';
  import type { SearchResult } from '$lib/types';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { SITE_NAME } from '$lib/config';
  import { truncate } from '$lib/utils';
  import SearchBarMini from '$lib/components/SearchBarMini.svelte';
  import { Breadcrumbs, type BreadcrumbItem } from '$lib';
  
  export let data: PageData;
  // Get supabase client from data prop (passed from +layout.ts)
  $: supabase = data.supabase;
  
  let query = data.query || '';
  let result: SearchResult | null = data.initialResult || null;
  // Normalize possibly undefined values for strict typing
  const targetLanguageCode = data.target_language_code ?? '';
  const langName = data.langName ?? 'Language';
  let loading = false;

  // Breadcrumb items
  $: breadcrumbItems = [
    { label: 'Home', href: '/' },
    { label: 'Languages', href: '/languages' },
    { label: langName ?? targetLanguageCode, href: `/language/${targetLanguageCode}/sources` },
    { label: 'Search' }
  ] as BreadcrumbItem[];
  
  // Ensure query is properly set from URL on mount and perform search if needed
  // Extract the query from the URL parameter
  $: urlQuery = $page.url.searchParams.get('q') || '';
  
  // Update local query when URL changes
  $: query = urlQuery;
  
  // Track query changes to trigger search
  $: {
    if (urlQuery) {
      // If we have a query parameter but no valid search result, perform the search
      if (!result || result.status === 'empty_query' || result.query !== urlQuery) {
        handleClientSearch(urlQuery);
      }
    } else if (!result) {
      // If no query and no result, show empty state
      result = {
        status: 'empty_query',
        query: '',
        target_language_code: targetLanguageCode,
        target_language_name: langName,
        data: {}
      };
    }
  }
  
  // This is a client-side search function to be used only when needed
  // (like when the user navigates directly to the page with a query parameter
  // or when the URL changes due to client-side navigation)
  async function handleClientSearch(searchQuery: string) {
    // Skip if query is empty or hasn't changed and we already have results
    if (!searchQuery.trim() || (result?.query === searchQuery && result?.status !== 'empty_query')) {
      return;
    }
    
    // If not logged in, redirect to auth page immediately
    if (!data.session) {
      const nextUrl = `${$page.url.pathname}${searchQuery ? `?q=${encodeURIComponent(searchQuery)}` : ''}`;
      goto(`/auth?next=${encodeURIComponent(nextUrl)}`);
      return;
    }
    
    loading = true;
    
    try {
      // Use the supabase client from the data prop
      result = await unifiedSearch(supabase, targetLanguageCode, searchQuery);
      
      // Handle direct navigation for single matches
      if (result.status === 'redirect') {
        goto(`/language/${targetLanguageCode}/wordform/${result.data.redirect_to}`);
      } else if (result.status === 'found') {
        const wordform = result.data.wordform_metadata.wordform;
        const lemma = result.data.wordform_metadata.lemma;
        
        if (wordform === lemma) {
          goto(`/language/${targetLanguageCode}/lemma/${encodeURIComponent(lemma)}`);
        } else {
          goto(`/language/${targetLanguageCode}/wordform/${encodeURIComponent(wordform)}`);
        }
      }
    } catch (error: any) {
      console.error('Client-side search error:', error);
      
      // Check if this is an authentication error (401)
      if (error.status === 401) {
        const nextUrl = `${$page.url.pathname}${searchQuery ? `?q=${encodeURIComponent(searchQuery)}` : ''}`;
        goto(`/auth?next=${encodeURIComponent(nextUrl)}`);
        return;
      }
      
      result = {
        status: 'error',
        query: searchQuery,
        target_language_code: targetLanguageCode,
        target_language_name: langName,
        error: error instanceof Error ? error.message : 'Unknown error',
        data: {}
      };
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>
    {query 
      ? `"${truncate(query, 20)}" | Search | ${langName} | ${SITE_NAME}`
      : `Search | ${langName} | ${SITE_NAME}`}
  </title>
</svelte:head>

<div class="container">
  <Breadcrumbs items={breadcrumbItems} />
  
  <h1>Search {langName || result?.target_language_name || 'Language'} Words</h1>
  
  <div class="mb-4">
    <SearchBarMini 
      targetLanguageCode={targetLanguageCode} 
      languageName={langName || result?.target_language_name || 'Language'} 
      autofocus={true}
      initialQuery={query}
    />
    
    {#if !data.session}
      <div class="alert alert-info mt-3">
        <strong>Authentication Required</strong>
        <p class="mb-0">You need to be logged in to use the search feature. This helps us manage AI usage costs.</p>
        <a href={`/auth?next=${encodeURIComponent($page.url.pathname)}${query ? `?q=${encodeURIComponent(query)}` : ''}`} 
           class="btn btn-primary mt-2">
          Log in to Search
        </a>
      </div>
    {/if}
    
    {#if loading}
      <div class="d-flex justify-content-center my-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="ms-3">Searching for "{query}"...</p>
      </div>
    {/if}
  </div>
  
  {#if result}
    <div class="search-results">
      <!-- Empty query state -->
      {#if result.status === 'empty_query'}
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Search {langName || 'Language'} Words</h5>
            <p>Enter a word to search. You can search for:</p>
            <ul>
              <li>Words in {langName || 'this language'}</li>
              <li>English words to find {langName || 'foreign language'} translations</li>
              <li>Word forms and dictionary forms (lemmas)</li>
            </ul>
            
            {#if !data.session}
              <div class="alert alert-info mt-3">
                <strong>Authentication Required</strong>
                <p class="mb-0">You need to be logged in to use the search feature. This helps us manage AI usage costs.</p>
              </div>
            {/if}
          </div>
        </div>
      
      <!-- Exact match found -->
      {:else if result.status === 'found'}
        <div class="card mb-4">
          <div class="card-header hz-card-header-primary">
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
            <div class="card-header hz-card-header-primary">
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
        {#if result.data.target_language_results?.possible_misspellings && result.data.target_language_results.possible_misspellings.length > 0}
          <div class="card mb-4">
            <div class="card-header hz-card-header-warning">
              <h5 class="card-title mb-0">Did you mean one of these?</h5>
            </div>
            <div class="card-body">
              <ul class="list-group list-group-flush">
                {#each result.data.target_language_results.possible_misspellings as suggestion (suggestion)}
                  <li class="list-group-item">
                    <a href="/language/{result.target_language_code}/search?q={encodeURIComponent(String(suggestion))}" class="hz-foreign-text">
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
            <div class="card-header hz-card-header-secondary">
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
          <div class="card-header hz-card-header-warning">
            <h5 class="card-title mb-0">No Results Found</h5>
          </div>
          <div class="card-body">
            <p>"{result.query}" did not match any words in {result.target_language_name} or English translations.</p>
            
            {#if result.data.possible_misspellings && result.data.possible_misspellings.length > 0}
              <p>Did you mean:</p>
              <ul>
                {#each result.data.possible_misspellings as suggestion (suggestion)}
                  <li>
                    <a href="/language/{result.target_language_code}/search?q={encodeURIComponent(String(suggestion))}" class="hz-foreign-text">
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
        {#if result.error && result.error.includes('401 UNAUTHORIZED')}
          <div class="card mb-4">
            <div class="card-header hz-card-header-info">
              <h5 class="card-title mb-0">Login Required</h5>
            </div>
            <div class="card-body">
              <p>You need to be logged in to use the search feature.</p>
              <p>This helps us manage AI usage costs and provide better service.</p>
              <a href={`/auth?next=${encodeURIComponent($page.url.pathname)}${query ? `?q=${encodeURIComponent(query)}` : ''}`} 
                 class="btn btn-primary mt-2">
                Log in to Search
              </a>
            </div>
          </div>
        {:else}
          <div class="card mb-4">
            <div class="card-header hz-card-header-warning">
              <h5 class="card-title mb-0">Search Error</h5>
            </div>
            <div class="card-body">
              <p>Sorry, we encountered an error processing your search.</p>
              <p class="text-danger">{result.error || 'Unknown error occurred'}</p>
              <p>Please try again later or with a different search term.</p>
            </div>
          </div>
        {/if}
      
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

  /* Removed unused input-action-button:hover and input-actions selectors */
</style>