<script lang="ts">
  import { goto } from '$app/navigation';
  import { X, ClipboardText } from 'phosphor-svelte';
  
  export let languageName: string;
  export let targetLanguageCode: string;
  
  let searchQuery = '';
  let searchInput: HTMLInputElement;
  
  function handleSearch(event: MouseEvent | KeyboardEvent) {
    if (!searchQuery.trim()) return;
    
    if (!targetLanguageCode) {
      console.error('Target language code not provided to SearchBarMini component');
      return;
    }
    
    const url = `/language/${targetLanguageCode}/search?q=${encodeURIComponent(searchQuery)}`;
    
    // Check if Ctrl/Command key is pressed for "open in new tab" behavior
    if ('metaKey' in event && (event.metaKey || event.ctrlKey)) {
      window.open(url, '_blank');
    } else {
      goto(url);
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

<div class="search-box">
  <div class="d-flex" id="top-search-form">
    <input 
      type="text" 
      placeholder={`Search ${languageName} words...`} 
      required
      class="form-control me-2"
      id="top-search-input"
      bind:value={searchQuery}
      bind:this={searchInput}
      on:keydown={(e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          handleSearch(e);
        }
      }}
    >
    {#if searchQuery}
      <button 
        type="button" 
        class="btn btn-outline-secondary me-1" 
        aria-label="Clear search" 
        title="Clear search"
        on:click={clearSearch}
      >
        <X size={16} />
      </button>
    {/if}
    <button 
      type="button" 
      class="btn btn-outline-secondary me-1" 
      aria-label="Paste from clipboard" 
      title="Paste from clipboard"
      on:click={pasteFromClipboard}
    >
      <ClipboardText size={16} />
    </button>
    <button 
      class="btn btn-primary"
      on:click={(event) => handleSearch(event)}
    >Search</button>
  </div>
</div>