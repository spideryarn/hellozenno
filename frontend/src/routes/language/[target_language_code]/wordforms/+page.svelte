<script lang="ts">
    import type { PageData } from './$types';
    import DataGrid from '$lib/components/DataGrid.svelte';
    import { SITE_NAME } from '$lib/config';
    
    export let data: PageData;
    
    // Destructure data for easier access
    const { target_language_code, language_name, wordforms, total } = data;

    import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
    import { supabase } from '$lib/supabaseClient';

    const columns = [
      { 
        id: 'wordform', 
        header: 'Wordform',
        // width: '25%', // Set the wordform column to 25% of table width
        accessor: row => `<span class="hz-column-primary-green">${row.wordform}</span>`,
        isHtml: true
      },
      { 
        id: 'translations', 
        header: 'Translations', 
        accessor: row => Array.isArray(row.translations) ? row.translations.join(', ') : '',
        filterType: 'json_array' // Explicitly mark this column as a JSON array for filtering
      },
      { id: 'part_of_speech', header: 'POS', width: 80 },
      { 
        id: 'updated_at', 
        header: 'Modified', 
        accessor: row => {
          if (!row.updated_at) return '';
          try {
            const date = new Date(row.updated_at);
            const formatted = date.toLocaleString('en-US', {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              hour12: false
            });
            return `<span class="metadata-timestamp">${formatted}</span>`;
          } catch (e) {
            return row.updated_at;
          }
        },
        isHtml: true
      },
    ];

    // Use the supabase data provider with the new column-based filterType approach
    const loadData = supabaseDataProvider({
      table: 'wordform',
      selectableColumns: 'id,wordform,part_of_speech,translations,updated_at',
      client: supabase,
      // We don't need to list jsonArrayColumns anymore since we use filterType in column definitions
    });
    
    // Function to generate URLs for each row
    function getWordformUrl(row: any): string {
      return `/language/${target_language_code}/wordform/${row.wordform}`;
    }
</script>

<svelte:head>
    <title>Wordforms | {language_name} | {SITE_NAME}</title>
</svelte:head>

<div class="container mt-4">
    <div class="row mb-4">
        <div class="col">
            <h1 class="mb-3">Wordforms in {language_name}</h1>
            <p class="d-flex gap-2">
                <a href="/language/{target_language_code}/sources" class="btn btn-outline-primary">
                    Browse {language_name} Sources
                </a>
                <a href="/language/{target_language_code}/sentences" class="btn btn-outline-secondary">
                    View {language_name} Sentences
                </a>
            </p>
        </div>
    </div>
    
    {#if wordforms.length > 0}
        <DataGrid {columns}
                  loadData={loadData}
                  initialRows={wordforms}
                  initialTotal={total}
                  getRowUrl={getWordformUrl}
                  queryModifier={(query) => query.eq('target_language_code', target_language_code)}
        />
    {:else}
        <div class="alert alert-info">
            No wordforms found for {language_name}.
        </div>
    {/if}
</div>

<style>
    .metadata-timestamp {
        font-family: var(--bs-font-monospace, monospace);
    }
</style>