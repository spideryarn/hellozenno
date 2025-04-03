<script lang="ts">
  import type { PageData } from './$types';
  import { goto } from '$app/navigation';
  
  export let data: PageData;
  
  let searchQuery = data.query;
  
  function handleSubmit(event: Event) {
    event.preventDefault();
    if (searchQuery.trim()) {
      // Navigate directly to the wordform page
      goto(`/language/${data.target_language_code}/wordform/${encodeURIComponent(searchQuery.trim())}`);
    }
  }
</script>

<svelte:head>
  <title>Search - {data.target_language_name}</title>
</svelte:head>

<div class="container mt-4">
  <h1>Search {data.target_language_name} Words</h1>
  
  <div class="row mt-4">
    <div class="col-md-8 offset-md-2">
      <form on:submit={handleSubmit} class="mb-4">
        <div class="input-group">
          <input 
            type="text" 
            bind:value={searchQuery} 
            class="form-control" 
            placeholder="Enter a word to search..." 
            required
          >
          <button type="submit" class="btn btn-primary">Search</button>
        </div>
      </form>
      
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">Search Tips</h5>
          <ul class="mb-0">
            <li>Enter any {data.target_language_name} word (lemma or wordform)</li>
            <li>The search will automatically determine if it's a lemma or wordform</li>
            <li>If the word is found, you'll be redirected to its details</li>
            <li>If it's a new word, it will be analyzed and saved</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  h1 {
    margin-bottom: 1rem;
  }
  
  .card {
    background-color: var(--bs-gray-800);
    border-color: var(--bs-gray-700);
  }
  
  .card-title {
    color: var(--bs-primary);
  }
</style> 