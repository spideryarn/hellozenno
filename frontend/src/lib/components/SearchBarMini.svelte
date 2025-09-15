<script lang="ts">
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import MagnifyingGlass from 'phosphor-svelte/lib/MagnifyingGlass';
  import X from 'phosphor-svelte/lib/X';
  import ClipboardText from 'phosphor-svelte/lib/ClipboardText';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import { onMount } from 'svelte';
  
  export let languageName: string;
  export let targetLanguageCode: string;
  export let autofocus: boolean = false;
  export let initialQuery: string = '';
  
  let searchQuery = initialQuery;
  let searchInput: HTMLInputElement;
  let searchButton: HTMLAnchorElement;
  let isSearching = false;
  
  onMount(() => {
    if (autofocus && searchInput) {
      searchInput.focus();
    }
  });
  
  function getSearchUrl() {
    if (!searchQuery.trim() || !targetLanguageCode) return '';
    return `/language/${targetLanguageCode}/search?q=${encodeURIComponent(searchQuery)}`;
  }
  function buildSearchUrl(query: string) {
    if (!query.trim() || !targetLanguageCode) return '';
    return `/language/${targetLanguageCode}/search?q=${encodeURIComponent(query)}`;
  }
  
  function isOnSearchPage() {
    if (!browser) return false; // Default to false during SSR
    return window.location.pathname.includes(`/language/${targetLanguageCode}/search`);
  }
  
  async function navigateToSearch(query: string, event?: MouseEvent | KeyboardEvent) {
    if (!browser) return;
    if (!query.trim()) return;
    if (!targetLanguageCode) {
      console.error('Target language code not provided to SearchBarMini component');
      return;
    }

    // Respect user modifier keys or middle-click to let the browser handle it
    if (event instanceof MouseEvent && (event.metaKey || event.ctrlKey || event.button === 1)) {
      return;
    }

    const url = buildSearchUrl(query);
    if (!url) return;

    if (isOnSearchPage()) {
      isSearching = true;
      try {
        await goto(url);
      } finally {
        isSearching = false;
      }
    } else {
      window.open(url, '_blank', 'noopener');
    }

    if (event instanceof MouseEvent) {
      event.preventDefault();
    }
  }

  async function handleSearch(event: MouseEvent | KeyboardEvent) {
    await navigateToSearch(searchQuery, event);
  }
  
  function clearSearch() {
    searchQuery = '';
    if (searchInput) {
      searchInput.focus();
    }
  }
  
  async function pasteFromClipboard() {
    if (!browser) return; // Skip during SSR
    
    try {
      const text = await navigator.clipboard.readText();
      searchQuery = text;
      if (searchInput) {
        searchInput.focus();
      }
      // Trigger search directly using the pasted text
      if (text.trim()) {
        navigateToSearch(text);
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
    color: var(--hz-color-text-secondary);
    padding: 0.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  .input-action-button:hover {
    color: var(--hz-color-text-main);
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
          // For complete keyboard shortcuts reference, see frontend/docs/KEYBOARD_SHORTCUTS.md
          if (e.key === 'Enter') {
            e.preventDefault();
            navigateToSearch(searchQuery);
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
    <a 
      href={getSearchUrl()}
      class="btn btn-primary search-button"
      target={isOnSearchPage() ? "_self" : "_blank"}
      tabindex="0"
      role="button"
      aria-label="Search"
      on:click={(event) => handleSearch(event)}
      style="display: inline-flex; align-items: center; justify-content: center;"
      class:disabled={isSearching}
      bind:this={searchButton}
    >
      {#if isSearching}
        <LoadingSpinner style="width: 16px; height: 16px;" />
      {:else}
        <MagnifyingGlass size={16} weight="bold" />
      {/if}
    </a>
  </div>
</div>