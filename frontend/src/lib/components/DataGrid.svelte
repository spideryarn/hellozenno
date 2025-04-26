<script lang="ts">
  /**
   * Very‑lightweight, reusable data grid for Hello Zenno.
   * Stage‑1 scope: static rows with Bootstrap table markup, proper hyperlinks.
   * More functionality (pagination, sort, filter) will be layered in future stages.
   */
  import { createEventDispatcher } from 'svelte';
  import DataGridNavButtons from './DataGridNavButtons.svelte';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';

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
    /** Disable sorting for this column (defaults to true) */
    sortable?: boolean;
    /** Disable filtering for this column (defaults to true) */
    filterable?: boolean;
  }

  /* ---------- props ---------- */
  export let columns: ColumnDef[] = [];
  export let rows: any[] = [];
  export let pageSize = 100;
  /** Whether to render the header row */
  export let showHeader: boolean = true;
  /** Whether to show navigation buttons at the top */
  export let showTopNav: boolean = true;
  /**
   * Function to generate the URL for each row
   * When provided, rows will be rendered as actual hyperlinks (<a> tags)
   * making the entire row clickable with standard browser link behavior
   */
  export let getRowUrl: ((row: any) => string) | null = null;

  const dispatch = createEventDispatcher();

  // visibleRows will be assigned reactively further below

  /** Optional async data provider. If supplied, grid becomes server-driven. */
  interface LoadParams {
    page: number;
    pageSize: number;
    sortField?: string | null;
    sortDir?: 'asc' | 'desc' | null;
    filterField?: string | null;
    filterValue?: string | null;
    queryModifier?: (query: any) => any;
  }

  type LoadDataFn = (params: LoadParams) => Promise<{ rows: any[]; total: number }>;

  export let loadData: LoadDataFn | undefined = undefined;
  
  /** 
   * Optional query modifier function that can apply custom filters 
   * or transformations to the query before execution
   */
  export let queryModifier: ((query: any) => any) | undefined = undefined;

  /** Optional rows + total to seed serverRows for SSR (page pre‑fetch). */
  export let initialRows: any[] = [];
  export let initialTotal: number | null = null;

  // --- internal state (server‑driven) ---
  let page = 1;
  let sortField: string | null = null;
  let sortDir: 'asc' | 'desc' | null = null;
  let filterField: string | null = null;
  let filterValue: string | null = null;

  let total = 0;
  let isLoading = false;
  let serverRows: any[] = initialRows;

  // If initialTotal provided, use it; else fallback to initialRows length until first fetch.
  total = initialTotal ?? initialRows.length;

  /** Debounce timer for filter input */
  let filterTimer: number | undefined;

  async function fetchRows() {
    if (!loadData) return;
    // If we already have serverRows for this state, skip
    if (!isLoading && serverRows.length && page === 1 && !sortField && !filterField) {
      return;
    }
    isLoading = true;
    try {
      const params = {
        page,
        pageSize,
        sortField,
        sortDir,
        filterField,
        filterValue
      };
      
      // Pass the queryModifier function if provided
      if (queryModifier) {
        params.queryModifier = queryModifier;
      }
      
      const { rows: fetchedRows, total: fetchedTotal } = await loadData(params);
      serverRows = fetchedRows;
      total = fetchedTotal;
    } finally {
      isLoading = false;
    }
  }

  // reactively fetch when page / sort / filter changes
  $: if (loadData) {
    // reference deps so Svelte re-runs this statement when they change
    page;
    pageSize;
    sortField;
    sortDir;
    filterField;
    filterValue;
    fetchRows();
  }

  $: visibleRows = loadData ? serverRows : rows.slice(0, pageSize);

  $: totalPagesValue = Math.max(1, Math.ceil((loadData ? total : rows.length) / pageSize));

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
  function handlePageChange(newPage: number) {
    page = newPage; // This will trigger a reactive update
  }
  
  // Show navigation only if we have server-driven pagination and more than one page
  $: showNavigation = loadData && totalPagesValue > 1;
</script>

<!-- Top navigation (optional - shows when showTopNav prop is true and we have pagination) -->
{#if showNavigation && showTopNav}
  <div class="top-nav-container mb-3">
    <DataGridNavButtons 
      page={page} 
      totalPages={totalPagesValue} 
      isLoading={isLoading} 
      onPageChange={handlePageChange} 
    />
  </div>
{/if}

<!-- Responsive wrapper so the table can scroll on small screens -->
<div class="table-responsive">
  <table class="table table-hover table-sm align-middle mb-0 hz-datagrid">
    {#if showHeader}
      <thead>
        <tr>
          {#each columns as col}
            {#if loadData}
              {#if col.sortable !== false}
                <th scope="col"
                    style="width: {col.width ?? 'auto'}"
                    class={`${col.class ?? ''} ${col.id === sortField ? 'sorted' : ''}`}
                    role="button"
                    aria-sort={col.id === sortField ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'}
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
            {#if col.filterable !== false}
              <th>
                <input type="text" class="form-control form-control-sm" placeholder="Filter"
                       on:input={(e) => handleFilterInput(col.id, (e.target as HTMLInputElement).value)}
                       value={col.id === filterField ? (filterValue ?? '') : ''}
                />
              </th>
            {:else}
              <th></th>
            {/if}
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
            {#if getRowUrl}
              <!-- Render as proper hyperlink -->
              <tr class="data-grid-row-link">
                {#each columns as col}
                  <td class={col.class}>
                    <!-- Apply the anchor to each cell -->
                    <a href={getRowUrl(row)} class="grid-row-link">
                      {#if col.accessor}
                        {#if col.isHtml}
                          {@html col.accessor(row) }
                        {:else}
                          {col.accessor(row)}
                        {/if}
                      {:else}
                        {row[col.id]}
                      {/if}
                    </a>
                  </td>
                {/each}
              </tr>
            {:else}
              <!-- No URL provided, render as non-clickable row -->
              <tr>
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
            {/if}
          {/each}
        {/if}
      {/if}
    </tbody>
  </table>
</div>

<!-- Bottom navigation -->
{#if showNavigation}
  <div class="bottom-nav-container mt-3">
    <DataGridNavButtons 
      page={page} 
      totalPages={totalPagesValue} 
      isLoading={isLoading} 
      onPageChange={handlePageChange} 
    />
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
  
  /* Top navigation container */
  .top-nav-container {
    display: flex;
    justify-content: flex-end;
  }
  
  /* Bottom navigation container */
  .bottom-nav-container {
    display: flex;
    justify-content: flex-end;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .top-nav-container,
    .bottom-nav-container {
      justify-content: center;
    }
  }

  /* Data grid row link styling */
  .data-grid-row-link {
    transition: background-color 0.15s ease-in-out;
  }

  .data-grid-row-link:hover {
    background-color: rgba(102, 154, 115, 0.07); /* subtle green overlay */
  }

  /* Make the link fill the entire cell */
  .grid-row-link {
    display: block;
    width: 100%;
    height: 100%;
    text-decoration: none;
    color: inherit;
    padding: 0;
    margin: -0.6rem -0.75rem; /* Negative margin to counter td padding */
    padding: 0.6rem 0.75rem;  /* Match td padding */
    position: relative;       /* Create stacking context for nested interactive elements */
  }

  /* Ensure text color doesn't change */
  .grid-row-link:hover, 
  .grid-row-link:focus, 
  .grid-row-link:active, 
  .grid-row-link:visited {
    color: inherit;
    text-decoration: none;
  }
</style> 