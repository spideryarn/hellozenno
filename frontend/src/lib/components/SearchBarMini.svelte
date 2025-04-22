<script lang="ts">
  import { goto } from '$app/navigation';
  import MagnifyingGlass from 'phosphor-svelte/lib/MagnifyingGlass';
  import X from 'phosphor-svelte/lib/X';
  import ClipboardText from 'phosphor-svelte/lib/ClipboardText';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { onMount } from 'svelte';
  
  export let languageName: string;
  export let targetLanguageCode: string;
  export let autofocus: boolean = false;
  
  let searchQuery = '';
  let searchInput: HTMLInputElement;
  let isSearching = false;
  
  onMount(() => {
    if (autofocus && searchInput) {
      searchInput.focus();
    }
  });
  
  async function handleSearch(event: MouseEvent | KeyboardEvent) {
    if (!searchQuery.trim()) return;
    
    if (!targetLanguageCode) {
      console.error('Target language code not provided to SearchBarMini component');
      return;
    }
    
    const url = `/language/${targetLanguageCode}/search?q=${encodeURIComponent(searchQuery)}`;
    
    // Set loading state
    isSearching = true;
    
    try {
      // Check if Ctrl/Command key is pressed for "open in new tab" behavior
      if ('metaKey' in event && (event.metaKey || event.ctrlKey)) {
        window.open(url, '_blank');
      } else {
        await goto(url);
      }
    } finally {
      // Reset loading state after navigation completes
      isSearching = false;
    }
  }
  
  function clearSearch() {
    searchQuery = '';
    if (searchInput) {
      searchInput.focus();
    }
  }
  
  async function pasteFromClipboard() {
    try {
      const text = await navigator.clipboard.readText();
      searchQuery = text;
      if (searchInput) {
        searchInput.focus();
      }
    } catch (error) {
      console.error('Failed to read clipboard:', error);
    }
  }
</script>

<style>
  .search-container {
    position: relative;
    display: flex;
    align-items: center;
  }

  .form-control {
    padding-right: 2.5rem;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }

  .search-button {
    margin-left: 0;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }

  .input-actions {
    position: absolute;
    right: 0.5rem;
    display: flex;
    align-items: center;
  }

  .input-action-button {
    background: none;
    border: none;
    color: var(--bs-gray-500);
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  .input-action-button:hover {
    color: var(--bs-gray-700);
  }
</style>

<div class="search-box">
  <div class="d-flex" id="top-search-form">
    <div class="search-container flex-grow-1 me-0">
      <!-- svelte-ignore a11y_autofocus -->
      <input 
        type="text" 
        placeholder={`Search ${languageName} words...`} 
        required
        class="form-control"
        id="top-search-input"
        bind:value={searchQuery}
        bind:this={searchInput}
        on:keydown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            handleSearch(e);
          } else if (e.key === 'Escape') {
            e.preventDefault();
            clearSearch();
          }
        }}
      >
      <div class="input-actions">
        {#if searchQuery}
          <button 
            type="button" 
            class="input-action-button" 
            aria-label="Clear search" 
            title="Clear search"
            on:click={clearSearch}
          >
            <X size={16} />
          </button>
        {:else if !isSearching}
          <button 
            type="button" 
            class="input-action-button" 
            aria-label="Paste from clipboard" 
            title="Paste from clipboard"
            on:click={pasteFromClipboard}
          >
            <ClipboardText size={16} />
          </button>
        {/if}
      </div>
    </div>
    <button 
      class="btn btn-primary search-button"
      disabled={isSearching}
      on:click={(event) => handleSearch(event)}
    >
      {#if isSearching}
        <LoadingSpinner style="width: 16px; height: 16px;" />
      {:else}
        <MagnifyingGlass size={16} weight="bold" />
      {/if}
    </button>
  </div>
</div>