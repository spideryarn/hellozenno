<script lang="ts">
    import type { PageData } from './$types';
    import DataGrid from '$lib/components/DataGrid.svelte';
    import { SITE_NAME } from '$lib/config';
    import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
    import { createUserIdColumn } from '$lib/datagrid/utils';
    import { apiFetch } from '$lib/api';
    import { RouteName } from '$lib/generated/routes';
    import { onMount } from 'svelte';

    // Define a type for the wordform row data
    interface WordformRow {
      id: number;
      wordform: string;
      translations: string[];
      part_of_speech: string;
      updated_at: string;
      created_by_id: string;
    }

    export let data: PageData;
    
    // Destructure data for easier access
    const { target_language_code, language_name, wordforms, total, supabase: supabaseClient, session } = data;

    // Ensure supabaseClient is non-null for the DataGrid provider
    if (!supabaseClient) {
      console.error("CRITICAL: Supabase client not available in wordforms page. DataGrid may not function.");
    }
    
    // Function to handle wordform deletion
    async function handleDeleteWordform(wordformValue: string) {
      if (!supabaseClient) {
        console.error('Supabase client is not available on the DataGrid page for API call.');
        alert('Authentication context not available. Please try refreshing the page.');
        return;
      }
      if (!session) {
        alert('You must be logged in to delete wordforms. Please refresh and log in.');
        return;
      }

      if (confirm(`Are you sure you want to delete the wordform "${wordformValue}"?`)) {
        try {
          await apiFetch({
            supabaseClient: supabaseClient, // Pass the client from data prop
            routeName: RouteName.WORDFORM_API_DELETE_WORDFORM_API,
            params: {
              target_language_code: target_language_code,
              wordform: wordformValue
            },
            options: { method: 'POST' }
          });
          
          window.location.reload();
        } catch (error: any) {
          console.error('Error deleting wordform (DataGrid):', error);
          alert(`Failed to delete wordform: ${error.message || 'Unknown error'}. Please try again.`);
        }
      }
    }

    const columns = [
      { 
        id: 'wordform', 
        header: 'Wordform',
        accessor: (row: WordformRow) => `<span class="hz-column-primary-green">${row.wordform}</span>`,
        isHtml: true
      },
      { 
        id: 'translations', 
        header: 'Translations', 
        accessor: (row: WordformRow) => Array.isArray(row.translations) ? row.translations.join(', ') : '',
        filterType: 'json_array'
      },
      { id: 'part_of_speech', header: 'POS', width: 80 },
      { 
        id: 'updated_at', 
        header: 'Modified', 
        accessor: (row: WordformRow) => {
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
        width: 170 // Added width similar to lemmas page
      },
      createUserIdColumn({ header: 'Created By', width: 170 }),
      {
        id: 'actions',
        header: '',
        width: 60,
        sortable: false,
        filterable: false,
        accessor: (row: WordformRow) => {
          return `
            <button 
              class="btn btn-sm btn-danger delete-wordform-btn" 
              data-wordform="${row.wordform}" 
              aria-label="Delete wordform"
              title="Delete wordform"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                <path d="M216,48H176V40a24,24,0,0,0-24-24H104A24,24,0,0,0,80,40v8H40a8,8,0,0,0,0,16h8V208a16,16,0,0,0,16,16H192a16,16,0,0,0,16-16V64h8a8,8,0,0,0,0-16ZM96,40a8,8,0,0,1,8-8h48a8,8,0,0,1,8,8v8H96Zm96,168H64V64H192ZM112,104v64a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Zm48,0v64a8,8,0,0,1-16,0V104a8,8,0,0,1,16,0Z"></path>
              </svg>
            </button>
          `;
        },
        isHtml: true,
      }
    ];

    // Use the supabase data provider with the supabaseClient from data prop
    const loadData = supabaseClient ? supabaseDataProvider({
      table: 'wordform',
      selectableColumns: 'id,wordform,part_of_speech,translations,updated_at,created_by_id',
      client: supabaseClient, // Use client from data prop
    }) : null;
    
    // Function to generate URLs for each row
    function getWordformUrl(row: WordformRow): string {
      return `/language/${target_language_code}/wordform/${row.wordform}`;
    }

    // Add event listener for delete buttons after the DOM is loaded
    let mounted = false;

    function setupDeleteButtons() {
      document.addEventListener('click', function(e) {
        const target = e.target as HTMLElement;
        const deleteBtn = target.closest('.delete-wordform-btn');
        
        if (deleteBtn) {
          e.preventDefault();
          e.stopPropagation();
          e.stopImmediatePropagation();

          const wordform = deleteBtn.getAttribute('data-wordform');
          if (wordform) {
            handleDeleteWordform(wordform);
          }
        }
      }, true); // Use capture phase
      
      mounted = true;
    }
    
    onMount(() => {
      if (!loadData) {
        console.error("DataGrid cannot be initialized because supabaseClient is not available.");
      }
      if (!mounted) {
        setupDeleteButtons();
      }
    });

</script>

<svelte:head>
    <title>Wordforms | {language_name} | {SITE_NAME}</title>
</svelte:head>

<div class="container mt-4">
    <div class="row mb-4">
        <div class="col">
            <h1 class="mb-3">Wordforms in {language_name}</h1>
        </div>
    </div>
    
    {#if wordforms !== undefined && loadData}
        <DataGrid {columns}
                  {loadData} 
                  initialRows={wordforms}
                  initialTotal={total}
                  getRowUrl={getWordformUrl}
                  defaultSortField="wordform"
                  defaultSortDir="asc"
                  queryModifier={(query) => query.eq('target_language_code', target_language_code)}
        />
    {:else if !loadData}
        <div class="alert alert-danger">
            Could not initialize wordform data. Authentication context might be missing.
        </div>
    {:else}
        <div class="alert alert-info">
            No wordforms found for {language_name}.
        </div>
    {/if}
</div>

<style>
    /* Removed unused .metadata-timestamp; timestamp styling now in cell HTML */

    /* Copied from lemmas page for consistency */
    :global(.delete-wordform-btn) {
        padding: 0.25rem 0.5rem;
    }
    
    :global(.delete-wordform-btn:hover) {
        background-color: var(--bs-danger-dark, #bb2d3b);
    }
</style>