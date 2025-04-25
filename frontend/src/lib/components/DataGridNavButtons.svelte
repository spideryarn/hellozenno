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

  // Props that match DataGrid pagination state
  export let page: number = 1;
  export let totalPages: number = 1;
  export let isLoading: boolean = false;
  
  // Function to call when page changes
  export let onPageChange: (newPage: number) => void;

  // Helper function to navigate to specific page
  function goToPage(p: number) {
    const max = totalPages;
    onPageChange(Math.min(Math.max(1, p), max));
  }
</script>

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
        ({page}/{totalPages})
      {/if}
    </span>
    <button class="button" on:click={() => goToPage(page + 1)} disabled={page === totalPages || isLoading} title="Next Page">
      <CaretRight size={16} weight="bold" />
    </button>
    <button class="button" on:click={() => goToPage(totalPages)} disabled={page === totalPages || isLoading} title="Last Page">
      <CaretDoubleRight size={16} weight="bold" />
    </button>
  </div>
{/if}

<style>
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
    min-width: 3.5rem;
    justify-content: center;
  }
</style>