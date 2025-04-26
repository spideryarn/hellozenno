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
      { id: 'translations', header: 'Translations', accessor: row => Array.isArray(row.translations) ? row.translations.join(', ') : '' },
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

    // For this page, extend the data provider with client-side filtering for translations
    const baseLoadData = supabaseDataProvider({
      table: 'wordform',
      selectableColumns: 'id,wordform,part_of_speech,translations,updated_at',
      client: supabase,
      jsonArrayColumns: ['translations'] // This isn't working directly with Supabase
    });
    
    // Wrap the data provider to add client-side translation filtering
    const loadData = async (params) => {
      // Special handling for translations filter
      if (params.filterField === 'translations' && params.filterValue) {
        // Fetch all data for the language without server-side filter
        const filterValue = params.filterValue;
        
        // Remove the filter for server request
        const serverParams = {
          ...params,
          filterField: null,
          filterValue: null
        };
        
        // Get all data for this language
        const result = await baseLoadData(serverParams);
        
        // Apply client-side filter for translations
        const filteredRows = result.rows.filter(row => {
          // If no translations, skip
          if (!row.translations || !Array.isArray(row.translations)) return false;
          
          // Check if any translation contains the filter text (case insensitive)
          return row.translations.some(translation => 
            translation.toLowerCase().includes(filterValue.toLowerCase())
          );
        });
        
        console.log(`Client-side filtering for '${filterValue}' in translations: Found ${filteredRows.length} of ${result.rows.length} rows`);
        
        // Return filtered data
        return {
          rows: filteredRows,
          total: filteredRows.length
        };
      }
      
      // For all other cases, use the base provider
      return baseLoadData(params);
    };
    
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