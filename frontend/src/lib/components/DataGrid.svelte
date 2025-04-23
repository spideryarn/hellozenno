<script lang="ts">
  /**
   * Very‑lightweight, reusable data grid for Hello Zenno.
   * Stage‑1 scope: static rows with Bootstrap table markup, single‑row click event.
   * More functionality (pagination, sort, filter) will be layered in future stages.
   */
  import { createEventDispatcher } from 'svelte';

  /** Column definition for DataGrid */
  // Column definition type (generic row type T)
  interface ColumnDef<T = any> {
    /** Row object key OR custom cell renderer */
    id: string;
    /** Column header label */
    header: string;
    /** Optional accessor to override default `row[id]` lookup */
    accessor?: (row: T) => unknown;
    /** Optional explicit width (e.g. 150 or '20%') */
    width?: number | string;
    /** Extra CSS classes for <td>/<th> */
    class?: string;
    /** If true, accessor result is treated as raw HTML */
    isHtml?: boolean;
  }

  /* ---------- props ---------- */
  export let columns: ColumnDef[] = [];
  export let rows: any[] = [];
  export let pageSize = 100;
  /** Whether to render the header row */
  export let showHeader: boolean = true;

  const dispatch = createEventDispatcher();

  // visibleRows will be assigned reactively further below

  function onRowClick(row: any) {
    dispatch('rowClick', row);
  }

  /** Optional async data provider. If supplied, grid becomes server-driven. */
  interface LoadParams {
    page: number;
    pageSize: number;
    sortField?: string | null;
    sortDir?: 'asc' | 'desc' | null;
    filterField?: string | null;
    filterValue?: string | null;
  }

  type LoadDataFn = (params: LoadParams) => Promise<{ rows: any[]; total: number }>;

  export let loadData: LoadDataFn | undefined = undefined;

  // --- internal state (server‑driven) ---
  let page = 1;
  let sortField: string | null = null;
  let sortDir: 'asc' | 'desc' | null = null;
  let filterField: string | null = null;
  let filterValue: string | null = null;

  let total = 0;
  let isLoading = false;
  let serverRows: any[] = [];

  /** Debounce timer for filter input */
  let filterTimer: number | undefined;

  async function fetchRows() {
    if (!loadData) return;
    isLoading = true;
    try {
      const { rows: fetchedRows, total: fetchedTotal } = await loadData({
        page,
        pageSize,
        sortField,
        sortDir,
        filterField,
        filterValue
      });
      serverRows = fetchedRows;
      total = fetchedTotal;
    } finally {
      isLoading = false;
    }
  }

  // reactively fetch when relevant state changes
  $: if (loadData) {
    fetchRows();
  }

  $: visibleRows = loadData ? serverRows : rows.slice(0, pageSize);

  const totalPages = () => Math.max(1, Math.ceil((loadData ? total : rows.length) / pageSize));

  function cycleSort(colId: string) {
    if (sortField !== colId) {
      sortField = colId;
      sortDir = 'asc';
    } else {
      sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    }
    page = 1;
  }

  function handleFilterInput(colId: string, value: string) {
    clearTimeout(filterTimer);
    filterTimer = setTimeout(() => {
      filterField = value ? colId : null;
      filterValue = value || null;
      page = 1;
    }, 300) as unknown as number;
  }

  /* Pagination helpers */
  function goToPage(p: number) {
    const max = totalPages();
    page = Math.min(Math.max(1, p), max);
  }

  import CaretDoubleLeft from 'phosphor-svelte/lib/CaretDoubleLeft';
  import CaretLeft from 'phosphor-svelte/lib/CaretLeft';
  import CaretRight from 'phosphor-svelte/lib/CaretRight';
  import CaretDoubleRight from 'phosphor-svelte/lib/CaretDoubleRight';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
</script>

<!-- Responsive wrapper so the table can scroll on small screens -->
<div class="table-responsive">
  <table class="table table-hover table-sm align-middle mb-0 hz-datagrid">
    {#if showHeader}
      <thead>
        <tr>
          {#each columns as col}
            {#if loadData}
              <th scope="col"
                  style="width: {col.width ?? 'auto'}"
                  class={`${col.class ?? ''} ${col.id === sortField ? 'sorted' : ''}`}
                  role="button"
                  on:click={() => cycleSort(col.id)}
              >
                {col.header}
                {#if col.id === sortField}
                  {#if sortDir === 'asc'}
                    ↑
                  {:else if sortDir === 'desc'}
                    ↓
                  {/if}
                {/if}
              </th>
            {:else}
              <th scope="col" style="width: {col.width ?? 'auto'}" class={col.class}>{col.header}</th>
            {/if}
          {/each}
        </tr>
      </thead>
    {/if}
    {#if loadData}
      <thead>
        <tr>
          {#each columns as col}
            <th>
              <input type="text" class="form-control form-control-sm" placeholder="Filter"
                     on:input={(e) => handleFilterInput(col.id, (e.target as HTMLInputElement).value)}
                     value={col.id === filterField ? (filterValue ?? '') : ''}
              />
            </th>
          {/each}
        </tr>
      </thead>
    {/if}
    <tbody>
      {#if visibleRows.length === 0}
        <tr>
          <td colspan={columns.length} class="text-center text-muted py-4">No data</td>
        </tr>
      {:else}
        {#if isLoading}
          <tr>
            <td colspan={columns.length} class="text-center py-4">
              <LoadingSpinner />
            </td>
          </tr>
        {:else}
          {#each visibleRows as row (row.id ?? row.slug ?? row)}
            <tr role="button" on:click={() => onRowClick(row)} style="cursor: pointer;">
              {#each columns as col}
                <td class={col.class}>
                  {#if col.accessor}
                    {#if col.isHtml}
                      {@html col.accessor(row) }
                    {:else}
                      {col.accessor(row)}
                    {/if}
                  {:else}
                    {row[col.id]}
                  {/if}
                </td>
              {/each}
            </tr>
          {/each}
        {/if}
      {/if}
    </tbody>
  </table>
</div>

<!-- Pagination -->
{#if loadData && totalPages() > 1}
  <div class="pagination-buttons mt-2 d-flex align-items-center gap-2">
    <button class="button" on:click={() => goToPage(1)} disabled={page === 1} title="First Page">
      <CaretDoubleLeft size={16} weight="bold" />
    </button>
    <button class="button" on:click={() => goToPage(page - 1)} disabled={page === 1} title="Previous Page">
      <CaretLeft size={16} weight="bold" />
    </button>
    <span class="file-position">({page}/{totalPages()})</span>
    <button class="button" on:click={() => goToPage(page + 1)} disabled={page === totalPages()} title="Next Page">
      <CaretRight size={16} weight="bold" />
    </button>
    <button class="button" on:click={() => goToPage(totalPages())} disabled={page === totalPages()} title="Last Page">
      <CaretDoubleRight size={16} weight="bold" />
    </button>
  </div>
{/if}

<style>
  .hz-datagrid {
    border-collapse: collapse;
  }

  .hz-datagrid thead th {
    background-color: var(--hz-color-primary-green-dark);
    color: var(--hz-color-text-main);
    border-bottom: none; /* remove bottom border */
  }

  .hz-datagrid tbody tr {
    border-top: 1px solid var(--hz-color-border-subtle);
    transition: background-color 0.15s ease-in-out;
  }

  .hz-datagrid tbody tr:hover {
    background-color: rgba(102, 154, 115, 0.07); /* subtle green overlay */
  }

  .hz-datagrid td, .hz-datagrid th {
    padding: 0.6rem 0.75rem;
  }

  /* remove left/right borders */
  .hz-datagrid td, .hz-datagrid th {
    border-left: none;
    border-right: none;
  }

  /* --- Pagination button styles (borrowed from NavButtons) --- */
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
  }
</style> 