<script lang="ts">
  import type { SearchMatch, SearchResultCategory, SearchResults } from '$lib/types';
  import { goto } from '$app/navigation';
  
  export let results: SearchResults;
  
  /**
   * Handle click on a search result item
   */
  function handleResultClick(match: SearchMatch) {
    // Prefer the lemma if available, otherwise use the wordform
    if (match.target_language_lemma) {
      goto(`/language/${results.target_language_code}/lemma/${encodeURIComponent(match.target_language_lemma)}`);
    } else {
      goto(`/language/${results.target_language_code}/wordform/${encodeURIComponent(match.target_language_wordform)}`);
    }
  }
  
  /**
   * Helper to format a search match item
   */
  function formatMatch(match: SearchMatch): string {
    const parts = [];
    
    // Add the wordform
    parts.push(`<span class="hz-foreign-text">${match.target_language_wordform}</span>`);
    
    // Add the lemma if different from wordform
    if (match.target_language_lemma && match.target_language_lemma !== match.target_language_wordform) {
      parts.push(`(form of <span class="hz-foreign-text">${match.target_language_lemma}</span>)`);
    }
    
    // Add translations if available
    if (match.english && match.english.length > 0) {
      parts.push(`"${match.english.join(', ')}"`);
    }
    
    // Add part of speech if available
    if (match.part_of_speech) {
      parts.push(`[${match.part_of_speech}]`);
    }
    
    return parts.join(' ');
  }
</script>

<div class="search-results">
  <h2>Search Results for "{results.search_term}"</h2>
  
  {#if results.status === 'invalid'}
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title text-danger">No matches found</h5>
        <p>No matches were found for "<span class="hz-foreign-text">{results.search_term}</span>" in {results.target_language_name}.</p>
        
        {#if results.possible_misspellings && results.possible_misspellings.length > 0}
          <p>Did you mean:</p>
          <ul>
            {#each results.possible_misspellings as suggestion}
              <li>
                <a href="/language/{results.target_language_code}/wordform/{encodeURIComponent(suggestion)}" class="hz-foreign-text">
                  {suggestion}
                </a>
              </li>
            {/each}
          </ul>
        {/if}
      </div>
    </div>
  {/if}
  
  {#if results.status === 'multiple_matches' && results.target_language_results}
    <!-- Target language matches -->
    {#if results.target_language_results.matches && results.target_language_results.matches.length > 0}
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <h5 class="card-title mb-0">{results.target_language_name} Matches</h5>
        </div>
        <div class="card-body">
          <ul class="list-group list-group-flush">
            {#each results.target_language_results.matches as match}
              <li class="list-group-item">
                <button 
                  class="btn btn-link text-start w-100 text-decoration-none" 
                  on:click={() => handleResultClick(match)}
                >
                  {@html formatMatch(match)}
                </button>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
    
    <!-- Possible misspellings -->
    {#if results.target_language_results.possible_misspellings && results.target_language_results.possible_misspellings.length > 0}
      <div class="card mb-4">
        <div class="card-header bg-warning text-dark">
          <h5 class="card-title mb-0">Possible Misspellings</h5>
        </div>
        <div class="card-body">
          <ul class="list-group list-group-flush">
            {#each results.target_language_results.possible_misspellings as suggestion}
              <li class="list-group-item">
                <a 
                  href="/language/{results.target_language_code}/wordform/{encodeURIComponent(suggestion)}" 
                  class="hz-foreign-text"
                >
                  {suggestion}
                </a>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
    
    <!-- English translation matches -->
    {#if results.english_results && results.english_results.matches && results.english_results.matches.length > 0}
      <div class="card mb-4">
        <div class="card-header bg-secondary text-white">
          <h5 class="card-title mb-0">English Translation Matches</h5>
        </div>
        <div class="card-body">
          <ul class="list-group list-group-flush">
            {#each results.english_results.matches as match}
              <li class="list-group-item">
                <button 
                  class="btn btn-link text-start w-100 text-decoration-none" 
                  on:click={() => handleResultClick(match)}
                >
                  {@html formatMatch(match)}
                </button>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
  {/if}
  
  <!-- Back to search form link -->
  <div class="mb-3">
    <a href="/language/{results.target_language_code}/search" class="btn btn-outline-primary">
      <i class="bi bi-arrow-left"></i> Back to Search
    </a>
  </div>
</div>

<style>
  .search-results {
    margin-bottom: 2rem;
  }
  
  .card-header {
    border-bottom: none;
  }
  
  .btn-link {
    padding: 0.5rem 0;
  }
  
  /* Add a subtle hover effect for list items */
  .list-group-item:hover {
    background-color: rgba(var(--bs-primary-rgb), 0.05);
  }
</style>