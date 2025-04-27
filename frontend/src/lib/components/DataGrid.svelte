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
    /** Specify special filter handling for this column (e.g. 'json_array') */
    filterType?: 'json_array' | string;
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
   * Whether to show loading spinner on initial load
   * Default is true for better user experience - prevents "No data" flash
   */
  export let showLoadingOnInitial: boolean = true;
  /**
   * Function to generate the URL for each row
   * When provided, rows will be rendered as actual hyperlinks (<a> tags)
   * making the entire row clickable with standard browser link behavior
   */
  export let getRowUrl: ((row: any) => string) | null = null;
  /**
   * Function to generate the tooltip content for each row
   * When provided, rows will have a title attribute with the tooltip content
   */
  export let getRowTooltip: ((row: any) => string) | null = null;

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

  /** Optional default sort field and direction for initial display */
  export let defaultSortField: string | null = null;
  export let defaultSortDir: 'asc' | 'desc' | null = null;

  /** Optional rows + total to seed serverRows for SSR (page pre‑fetch). */
  export let initialRows: any[] = [];
  export let initialTotal: number | null = null;

  // --- internal state (server‑driven) ---
  let page = 1;
  let sortField: string | null = defaultSortField;
  let sortDir: 'asc' | 'desc' | null = defaultSortDir;
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
    isLoading = true;
    try {
      const params: any = {
        page,
        pageSize,
        sortField,
        sortDir,
        filterField,
        filterValue,
        columns // Pass column definitions to allow providers to check filterType
      };
      
      // @ts-ignore – dynamic property added for provider
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
      // If the value is empty and this column was previously filtered,
      // we need to make sure we clear the filter
      if (!value && filterField === colId) {
        filterField = null;
        filterValue = null;
      } else if (value) {
        // Find the column definition to check if it has a special filterType
        const column = columns.find(col => col.id === colId);
        
        // Set the filter field and value
        filterField = colId;
        filterValue = value;
        
        // Log additional debug info for special filter types
        if (column?.filterType) {
          console.log(`Applying ${column.filterType} filter on ${filterField}: ${filterValue}`);
        }
      } else {
        // No value and not previously this column, no change needed
        return;
      }
      page = 1;
      // For debugging
      console.log(`Filtering on ${filterField ?? 'none'}: ${filterValue ?? 'none'}`);
    }, 300) as unknown as number;
  }

  /* Pagination helpers */
  function handlePageChange(newPage: number) {
    page = newPage; // This will trigger a reactive update
  }
  
  // Show navigation only if we have server-driven pagination and more than one page
  $: showNavigation = loadData && totalPagesValue > 1;

  /**
   * NOTE: Filter inputs are temporarily hidden until filtering functionality can be properly fixed.
   * The filtering code is kept intact for future re-enablement when resources are available.
   * This is a temporary workaround to avoid confusing users with non-working filters.
   */
  const showFilters = false; // Temporarily disable filter inputs
</script>

<!-- Top navigation (optional - shows when showTopNav prop is true) -->
{#if showTopNav}
  <div class="top-nav-container mb-3">
    <DataGridNavButtons 
      page={page} 
      totalPages={totalPagesValue} 
      isLoading={isLoading} 
      onPageChange={handlePageChange} 
      totalRows={total}
      filteredRows={filterField ? visibleRows.length : null}
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
              <th scope="col" 
                  style="width: {col.width ?? 'auto'}" 
                  class={`${col.class ?? ''} ${col.id === sortField ? 'sorted' : ''}`}>
                {col.header}
                {#if col.id === sortField}
                  {#if sortDir === 'asc'}
                    ↑
                  {:else if sortDir === 'desc'}
                    ↓
                  {/if}
                {/if}
              </th>
            {/if}
          {/each}
        </tr>
      </thead>
    {/if}
    {#if loadData && showFilters}
      <thead>
        <tr>
          {#each columns as col}
            {#if col.filterable !== false}
              <th>
                <div class="input-group input-group-sm">
                  <input type="text" class="form-control form-control-sm" placeholder="Filter"
                         on:input={(e) => handleFilterInput(col.id, (e.target as HTMLInputElement).value)}
                         on:change={(e) => handleFilterInput(col.id, (e.target as HTMLInputElement).value)}
                         value={col.id === filterField ? (filterValue ?? '') : ''}
                  />
                  {#if col.id === filterField && filterValue}
                    <button class="btn btn-outline-secondary btn-sm" 
                            type="button" 
                            title="Clear filter"
                            on:click={() => handleFilterInput(col.id, '')}>
                      ×
                    </button>
                  {/if}
                </div>
              </th>
            {:else}
              <th></th>
            {/if}
          {/each}
        </tr>
      </thead>
    {/if}
    <tbody>
      {#if isLoading || (visibleRows.length === 0 && loadData && showLoadingOnInitial)}
        <tr>
          <td colspan={columns.length} class="text-center py-4">
            <LoadingSpinner />
          </td>
        </tr>
      {:else if visibleRows.length === 0}
        <tr>
          <td colspan={columns.length} class="text-center text-muted py-4">No data</td>
        </tr>
      {:else}
        {#each visibleRows as row (row.id ?? row.slug ?? row)}
          {#if getRowUrl}
            <!-- Render as proper hyperlink -->
            <tr class="data-grid-row-link" title={getRowTooltip ? getRowTooltip(row) : undefined}>
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
            <tr title={getRowTooltip ? getRowTooltip(row) : undefined}>
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
    </tbody>
  </table>
</div>

<!-- Bottom navigation -->
<div class="bottom-nav-container mt-3">
  <DataGridNavButtons 
    page={page} 
    totalPages={totalPagesValue} 
    isLoading={isLoading} 
    onPageChange={handlePageChange} 
    totalRows={total}
    filteredRows={filterField ? visibleRows.length : null}
  />
</div>

<style>
  .hz-datagrid {
    border-collapse: collapse;
    border-radius: var(--hz-border-radius-md);
    overflow: hidden;
    box-shadow: 0 0 0 1px var(--hz-color-border);
  }

  .hz-datagrid thead th {
    /* Make the header less obtrusive */
    background-color: rgba(83, 126, 92, 0.6); /* Semi-transparent version of var(--hz-color-primary-green-dark) */
    color: var(--hz-color-text-main);
    border-bottom: none; /* remove bottom border */
    font-weight: 500; /* Slightly reduce font weight */
    font-size: 0.95rem; /* Slightly reduce font size */
    text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3); /* Subtle text shadow for better readability */
    letter-spacing: 0.02em; /* Slightly increased letter spacing */
  }
  
  .input-group .btn-outline-secondary {
    color: var(--hz-color-text-main);
    border-color: var(--hz-color-border-main);
  }
  
  .input-group .btn-outline-secondary:hover {
    background-color: var(--hz-color-primary-green);
    border-color: var(--hz-color-primary-green);
  }

  .hz-datagrid tbody tr {
    border-top: 1px solid var(--hz-color-border-subtle);
    transition: background-color 0.15s ease-in-out;
  }

  .hz-datagrid tbody tr:hover {
    background-color: rgba(102, 154, 115, 0.1); /* slightly enhanced green overlay */
  }

  .hz-datagrid td {
    padding: 0.8rem 0.75rem; /* increased vertical padding for data cells */
  }
  
  .hz-datagrid th {
    padding: 0.6rem 0.75rem; /* slightly reduced padding for header cells */
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
    width: 100%;
  }
  
  /* Bottom navigation container */
  .bottom-nav-container {
    display: flex;
    justify-content: flex-end;
    width: 100%;
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
    background-color: rgba(102, 154, 115, 0.1); /* subtle green overlay */
  }

  /* Make the link fill the entire cell */
  .grid-row-link {
    display: block;
    width: 100%;
    height: 100%;
    text-decoration: none;
    color: inherit;
    padding: 0;
    margin: -0.8rem -0.75rem; /* Negative margin to counter td padding */
    padding: 0.8rem 0.75rem;  /* Match td padding */
    position: relative;       /* Create stacking context for nested interactive elements */
  }

  /* Ensure text color doesn't change (unless explicitly overridden with .hz-column-primary-green) */
  .grid-row-link:hover, 
  .grid-row-link:focus, 
  .grid-row-link:active, 
  .grid-row-link:visited {
    color: inherit;
    text-decoration: none;
  }
  
  /* Don't override the primary green color for links that contain spans with this class */
  .grid-row-link .hz-column-primary-green {
    color: var(--hz-color-primary-green) !important;
  }
</style> 