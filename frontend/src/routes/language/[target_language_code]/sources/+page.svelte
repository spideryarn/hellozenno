<script lang="ts">
  import type { PageData } from './$types';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import SourceItem from '$lib/components/SourceItem.svelte';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { SITE_NAME } from '$lib/config';
  
  export let data: PageData;
  
  // Extract data with reactive declarations
  $: ({ languageCode, languageName, sources, currentSort } = data);
  
  // Handle sorting by updating the URL with sort parameter
  function handleSort(sortBy) {
    goto(`/language/${languageCode}/sources?sort=${sortBy}`, { keepFocus: true });
  }
  
  onMount(() => {
    console.log('Component mounted, sort type:', currentSort);
  });
  
  // Function to create a new source directory
  async function createNewSourceDir() {
    try {
      // Prompt for source directory name
      const dirName = prompt('Enter new source directory name:');
      if (!dirName) return; // User cancelled
      
      // API call to create directory
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_CREATE_SOURCEDIR_API, { target_language_code: languageCode }),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ path: dirName }),
        }
      );
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create directory');
      }
      
      // Redirect to refresh the page
      window.location.reload();
      
    } catch (error) {
      alert('Error creating directory: ' + (error instanceof Error ? error.message : String(error)));
    }
  }
  
  // Function to delete an empty source directory
  async function deleteSourceDir(slug: string) {
    try {
      // Confirm deletion
      if (!confirm('Are you sure you want to delete this directory?')) {
        return;
      }
      
      // API call to delete directory
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_DELETE_SOURCEDIR_API, { 
          target_language_code: languageCode,
          sourcedir_slug: slug
        }),
        {
          method: 'DELETE',
        }
      );
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete directory');
      }
      
      // Refresh the page
      window.location.reload();
      
    } catch (error) {
      alert('Error deleting directory: ' + (error instanceof Error ? error.message : String(error)));
    }
  }
</script>

<svelte:head>
  <title>Sources | {languageName} | {SITE_NAME}</title>
</svelte:head>

<h1 class="mb-4">{languageName} Sources</h1>

<!-- Navigation links -->
<div class="mb-3">
  <nav class="nav nav-pills gap-2">
    <a class="nav-link active" href="/language/{languageCode}/sources">Sources</a>
    <a class="nav-link" href="/language/{languageCode}/wordforms">Wordforms</a>
    <a class="nav-link" href="/language/{languageCode}/lemmas">Lemmas</a>
    <a class="nav-link" href="/language/{languageCode}/sentences">Sentences</a>
    <a class="nav-link" href="/language/{languageCode}/phrases">Phrases</a>
    <a class="nav-link" href="/language/{languageCode}/flashcards">Flashcards</a>
  </nav>
</div>

<!-- Actions toolbar -->
<div class="mb-4 d-flex justify-content-between align-items-center">
  <button type="button" class="btn btn-success" on:click={createNewSourceDir}>
    New Source Directory
  </button>
  <div class="actions">
    <!-- Additional action buttons can go here -->
  </div>
</div>

<!-- Sort options -->
<div class="mb-4 text-secondary">
  Sort by:
  <button type="button" 
    on:click={() => handleSort('alpha')}
    class="btn btn-link text-decoration-none ms-2 me-2 p-0"
    class:fw-bold={currentSort === 'alpha'} 
    class:text-primary={currentSort === 'alpha'}>
    Alphabetical
  </button> |
  <button type="button" 
    on:click={() => handleSort('date')}
    class="btn btn-link text-decoration-none ms-2 p-0"
    class:fw-bold={currentSort === 'date'} 
    class:text-primary={currentSort === 'date'}>
    Recently Modified
  </button>
</div>

<!-- Debug info (hidden in production) -->
{#if typeof process !== 'undefined' && process.env && process.env.NODE_ENV !== 'production'}
  <div class="d-none">
    Current sort: {currentSort}
    Sources count: {sources.length}
  </div>
{/if}

{#if sources.length === 0}
  <div class="alert alert-info">No sources available for {languageName} yet.</div>
{:else}
  <div class="list-group">
    {#each sources as source}
      <div class="d-flex align-items-center">
        <SourceItem 
          name={source.name}
          displayName={source.display_name}
          slug={source.slug}
          {languageCode}
          description={source.description}
          statistics={source.statistics}
          className="flex-grow-1"
        />
        {#if source.is_empty}
          <button 
            type="button" 
            class="btn btn-danger btn-sm ms-2"
            on:click={() => deleteSourceDir(source.slug)}
          >
            Delete
          </button>
        {/if}
      </div>
    {/each}
  </div>
{/if} 