<script lang="ts">
  /** 
   * Navigation buttons for DataGrid pagination
   * Extracted from DataGrid.svelte to allow reuse at top and bottom of grid
   */
  import CaretDoubleLeft from 'phosphor-svelte/lib/CaretDoubleLeft';
  import CaretLeft from 'phosphor-svelte/lib/CaretLeft';
  import CaretRight from 'phosphor-svelte/lib/CaretRight';
  import CaretDoubleRight from 'phosphor-svelte/lib/CaretDoubleRight';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { tick } from 'svelte';

  // Props that match DataGrid pagination state
  export let page: number = 1;
  export let totalPages: number = 1;
  export let isLoading: boolean = false;
  
  // Row count information props
  export let totalRows: number = 0;
  export let filteredRows: number | null = null;
  
  // Function to call when page changes
  export let onPageChange: (newPage: number) => void;

  // For the page input - separate local value for input
  let inputValue = '';
  let inputError = false;

  // Keep input value synced with page when not being edited
  $: {
    // Only update input if the input field doesn't have focus
    if (typeof document !== 'undefined' && document.activeElement !== inputElement) {
      inputValue = page.toString();
    }
  }

  let inputElement: HTMLInputElement;

  // Helper function to navigate to specific page
  function goToPage(p: number) {
    const newPage = Math.min(Math.max(1, p), totalPages);
    if (newPage !== page) {
      onPageChange(newPage);
    }
  }

  // Handle manual page input submission
  async function handleSubmit() {
    const pageNum = parseInt(inputValue);
    
    // Validate input
    if (isNaN(pageNum) || pageNum < 1 || pageNum > totalPages) {
      inputError = true;
      inputValue = page.toString(); // Reset to current page immediately
      
      // Clear error state after delay
      setTimeout(() => {
        inputError = false;
      }, 1500);
      return;
    }
    
    // Only navigate if page actually changed
    if (pageNum !== page) {
      goToPage(pageNum);
      
      // Ensure input shows the actual page we navigated to
      await tick();
      inputValue = page.toString();
    }
  }
</script>

<div class="pagination-container d-flex align-items-center justify-content-between">
  <!-- Row count display - always visible -->
  {#if totalRows > 0}
    <div class="row-count me-auto">
      <span class="badge bg-secondary text-on-light">
        {#if filteredRows !== null && filteredRows !== totalRows}
          {filteredRows} of {totalRows} rows
        {:else}
          {totalRows} rows
        {/if}
      </span>
    </div>
  {/if}

  <!-- Pagination buttons - only visible if more than one page -->
  {#if totalPages > 1}
    <div class="pagination-buttons d-flex align-items-center gap-2">
      <button class="button" on:click={() => goToPage(1)} disabled={page === 1 || isLoading} title="First Page">
        <CaretDoubleLeft size={16} weight="bold" />
      </button>
      <button class="button" on:click={() => goToPage(page - 1)} disabled={page === 1 || isLoading} title="Previous Page">
        <CaretLeft size={16} weight="bold" />
      </button>
      <span class="file-position">
        {#if isLoading}
          <LoadingSpinner size="sm" />
        {:else}
          <div class="page-input-container">
            <input
              bind:this={inputElement}
              type="text"
              class="page-input {inputError ? 'input-error' : ''}"
              bind:value={inputValue}
              on:blur={handleSubmit}
              on:keydown={(e) => e.key === 'Enter' && handleSubmit()}
              disabled={isLoading}
              title="Enter page number"
              aria-label="Go to page"
            />
            <span class="page-total">/{totalPages}</span>
          </div>
        {/if}
      </span>
      <button class="button" on:click={() => goToPage(page + 1)} disabled={page === totalPages || isLoading} title="Next Page">
        <CaretRight size={16} weight="bold" />
      </button>
      <button class="button" on:click={() => goToPage(totalPages)} disabled={page === totalPages || isLoading} title="Last Page">
        <CaretDoubleRight size={16} weight="bold" />
      </button>
    </div>
  {:else if totalRows > 0}
    <!-- If we have rows but only one page, still show the count but right-aligned -->
    <div></div>
  {/if}
</div>

<style>
  /* --- Pagination container styles --- */
  .pagination-container {
    width: 100%;
  }

  /* --- Row count styles --- */
  .row-count {
    font-size: 1rem;
    font-weight: 500;
    color: var(--hz-color-text-main);
    white-space: nowrap;
    padding: 0.5rem 0;
    margin-right: 1rem;
    display: flex;
    flex: 1;
  }
  
  .row-count .badge {
    background-color: var(--hz-color-primary-green-dark);
    color: white;
    font-weight: normal;
    padding: 0.4rem 0.8rem;
  }

  /* --- Pagination button styles --- */
  .button {
    background-color: var(--hz-color-primary-green);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    white-space: nowrap;
  }

  .button:disabled,
  .button.disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  .file-position {
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    min-width: 5rem;
    justify-content: center;
  }

  /* Page input styles */
  .page-input-container {
    display: flex;
    align-items: center;
    gap: 2px;
  }

  .page-input {
    width: 2.5rem;
    height: 1.8rem;
    border: 1px solid var(--hz-color-border);
    border-radius: 4px;
    background-color: var(--hz-color-bg-secondary);
    color: var(--hz-color-text-primary);
    text-align: center;
    padding: 0.1rem;
    font-size: 0.9rem;
  }

  .page-input:focus {
    outline: 1px solid var(--hz-color-primary-green);
    border-color: var(--hz-color-primary-green);
  }

  .page-input.input-error {
    border-color: var(--hz-color-danger, red);
    background-color: rgba(255, 0, 0, 0.05);
    animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
  }

  .page-total {
    color: var(--hz-color-text-secondary);
    font-size: 0.9rem;
  }

  @keyframes shake {
    10%, 90% { transform: translate3d(-1px, 0, 0); }
    20%, 80% { transform: translate3d(2px, 0, 0); }
    30%, 50%, 70% { transform: translate3d(-2px, 0, 0); }
    40%, 60% { transform: translate3d(1px, 0, 0); }
  }
</style>