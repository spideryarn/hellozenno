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

  // Only show first page for now – full pagination comes later
  $: visibleRows = rows.slice(0, pageSize);

  function onRowClick(row: any) {
    dispatch('rowClick', row);
  }
</script>

<!-- Responsive wrapper so the table can scroll on small screens -->
<div class="table-responsive">
  <table class="table table-hover table-sm align-middle mb-0 hz-datagrid">
    {#if showHeader}
      <thead>
        <tr>
          {#each columns as col}
            <th scope="col" style="width: {col.width ?? 'auto'}" class={col.class}>{col.header}</th>
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
    </tbody>
  </table>
</div>

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
</style> 