<script lang="ts">
    import type { PageData } from './$types';
    import DataGrid from '$lib/components/DataGrid.svelte';
    import { SITE_NAME } from '$lib/config';
    import { page } from '$app/stores';
    
    export let data: PageData;
    
    // Destructure data for easier access
    const { target_language_code, language_name, phrases, total } = data;

    import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
    import { supabase } from '$lib/supabaseClient';
    import { createUserIdColumn } from '$lib/datagrid/utils';

    const columns = [
      { 
        id: 'canonical_form', 
        header: 'Phrase',
        accessor: row => `<span class="hz-column-primary-green">${row.canonical_form}</span>`,
        isHtml: true
      },
      { 
        id: 'translations', 
        header: 'Translations', 
        accessor: row => Array.isArray(row.translations) ? row.translations.join(', ') : '',
        filterType: 'json_array'
      },
      { id: 'part_of_speech', header: 'Part of Speech', width: 120 },
      { 
        id: 'difficulty_level', 
        header: 'Level', 
        width: 80,
        accessor: row => row.difficulty_level || '—'
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
        isHtml: true
      },
    ];

    // Use the supabase data provider
    const loadData = supabaseDataProvider({
      table: 'phrase',
      selectableColumns: 'id,canonical_form,part_of_speech,translations,updated_at,usage_notes,slug,difficulty_level,created_by_id',
      client: supabase,
    });
    
    // Function to generate URLs for each row
    function getPhraseUrl(row: any): string {
      return `/language/${target_language_code}/phrase/${row.slug}`;
    }

    // Function to generate tooltips for each row
    function getPhraseTooltip(row: any): string {
      return row.usage_notes || '';
    }
</script>

<svelte:head>
    <title>Phrases | {language_name} | {SITE_NAME}</title>
</svelte:head>

<div class="container mt-4">
    <div class="row mb-4">
        <div class="col">
            <h1 class="mb-3">Phrases and idioms in {language_name}</h1>
        </div>
    </div>
    
    {#if phrases.length > 0}
        <DataGrid {columns}
                  loadData={loadData}
                  initialRows={phrases}
                  initialTotal={total}
                  getRowUrl={getPhraseUrl}
                  getRowTooltip={getPhraseTooltip}
                  defaultSortField="updated_at"
                  defaultSortDir="desc"
                  queryModifier={(query) => query.eq('target_language_code', target_language_code)}
        />
    {:else}
        <div class="alert alert-info">
            No phrases found for {language_name}.
        </div>
    {/if}
</div>

<style>
    .metadata-timestamp {
        font-family: var(--bs-font-monospace, monospace);
    }
</style> 