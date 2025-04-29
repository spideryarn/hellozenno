<script lang="ts">
    import type { PageData } from './$types';
    import DataGrid from '$lib/components/DataGrid.svelte';
    import { SITE_NAME } from '$lib/config';
    import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
    import { supabase } from '$lib/supabaseClient';
    import { createUserIdColumn } from '$lib/datagrid/utils';
    
    export let data: PageData;
    
    // Destructure data for easier access
    const { target_language_code, language_name, sentences, total } = data;

    const columns = [
      { 
        id: 'sentence', 
        header: 'Sentence',
        accessor: row => `<span class="hz-column-primary-green">${row.sentence}</span>`,
        isHtml: true
      },
      { 
        id: 'translation', 
        header: 'Translation'
      },
      { 
        id: 'language_level', 
        header: 'Level',
        width: 90
      },
      createUserIdColumn({ header: 'Created By', width: 170 }),
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
        isHtml: true,
        width: 170
      },
    ];

    // Use the supabase data provider
    const loadData = supabaseDataProvider({
      table: 'sentence',
      selectableColumns: 'id,sentence,translation,language_level,updated_at,slug,lemma_words,created_by_id',
      client: supabase,
      jsonArrayColumns: ['lemma_words']
    });
    
    // Function to generate URLs for each row
    function getSentenceUrl(row: any): string {
      return `/language/${target_language_code}/sentence/${row.slug}`;
    }
</script>

<svelte:head>
    <title>Sentences | {language_name} | {SITE_NAME}</title>
</svelte:head>

<div class="container mt-4">
    <div class="row mb-4">
        <div class="col">
            <h1>Sentences in {language_name}</h1>
            <p>
                <a href="/language/{target_language_code}/sources" class="btn btn-outline-primary">
                    Browse {language_name} Sources
                </a>
            </p>
        </div>
    </div>
    
    {#if sentences.length > 0}
        <DataGrid {columns}
                loadData={loadData}
                initialRows={sentences}
                initialTotal={total}
                getRowUrl={getSentenceUrl}
                defaultSortField="updated_at"
                defaultSortDir="desc"
                queryModifier={(query) => query.eq('target_language_code', target_language_code)}
        />
    {:else}
        <div class="alert alert-info">
            No sentences found for {language_name}. Start by adding sources!
        </div>
    {/if}
</div>

<style>
    .metadata-timestamp {
        font-family: var(--bs-font-monospace, monospace);
    }
</style> 