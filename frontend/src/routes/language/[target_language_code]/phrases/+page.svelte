<script lang="ts">
    import type { PageData } from './$types';
    import DataGrid from '$lib/components/DataGrid.svelte';
    import { SITE_NAME } from '$lib/config';
    // import { page } from '$app/stores'; // page store not used, can be removed or commented if planned for future
    
    export let data: PageData;
    
    // Destructure data for easier access
    const { target_language_code, language_name, phrases, total, supabase: supabaseClient, session } = data;

    import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
    // import { supabase } from '$lib/supabaseClient'; // page store not used, can be removed or commented if planned for future
    import { createUserIdColumn } from '$lib/datagrid/utils';
    import { apiFetch } from '$lib/api';
    import { RouteName } from '$lib/generated/routes';
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';

    // Define a type for the phrase row data
    interface PhraseRow {
      id: number;
      canonical_form: string;
      part_of_speech: string | null;
      translations: string[] | null; 
      updated_at: string;
      usage_notes: string | null;
      slug: string;
      language_level: string | null;
      created_by_id: string | null;
    }

    // Ensure supabaseClient is non-null for the DataGrid provider and delete actions
    if (!supabaseClient) {
      console.error("CRITICAL: Supabase client not available in phrases page. DataGrid may not function correctly.");
    }

    // Function to handle phrase deletion
    async function handleDeletePhrase(phraseSlug: string, phraseText: string) {
      if (!supabaseClient) {
        console.error('Supabase client is not available on the DataGrid page for API call.');
        alert('Authentication context not available. Please try refreshing the page.');
        return;
      }
      if (!session) {
        alert('You must be logged in to delete phrases. Please refresh and log in.');
        return;
      }

      if (confirm(`Are you sure you want to delete the phrase "${phraseText}"?`)) {
        try {
          await apiFetch({
            supabaseClient: supabaseClient,
            routeName: RouteName.PHRASE_API_DELETE_PHRASE_API,
            params: {
              target_language_code: target_language_code,
              slug: phraseSlug
            },
            options: { method: 'POST' }
          });
          
          window.location.reload(); // Reload to reflect changes
        } catch (error: any) {
          console.error('Error deleting phrase (DataGrid):', error);
          alert(`Failed to delete phrase: ${error.message || 'Unknown error'}. Please try again.`);
        }
      }
    }

    const columns = [
      { 
        id: 'canonical_form', 
        header: 'Phrase',
        accessor: (row: PhraseRow) => `<span class="hz-column-primary-green">${row.canonical_form}</span>`,
        isHtml: true
      },
      { 
        id: 'translations', 
        header: 'Translations', 
        accessor: (row: PhraseRow) => Array.isArray(row.translations) ? row.translations.join(', ') : '',
        filterType: 'json_array'
      },
      { id: 'part_of_speech', header: 'Part of Speech', width: 120 },
      { 
        id: 'language_level', 
        header: 'Level', 
        width: 80,
        accessor: (row: PhraseRow) => row.language_level || '—'
      },
      createUserIdColumn({ header: 'Created By', width: 170 }),
      { 
        id: 'updated_at', 
        header: 'Modified', 
        accessor: (row: PhraseRow) => {
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
      {
        id: 'actions',
        header: '',
        width: 60,
        sortable: false,
        filterable: false,
        accessor: (row: PhraseRow) => {
          return `
            <button 
              class="btn btn-sm btn-danger delete-phrase-btn" 
              data-phrase-slug="${row.slug}"
              data-phrase-text="${row.canonical_form}"
              aria-label="Delete phrase"
              title="Delete phrase"
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

    // Use the supabase data provider
    const loadData = supabaseClient ? supabaseDataProvider({
      table: 'phrase',
      selectableColumns: 'id,canonical_form,part_of_speech,translations,updated_at,usage_notes,slug,language_level,created_by_id',
      client: supabaseClient,
    }) : undefined;
    
    // Function to generate URLs for each row
    function getPhraseUrl(row: PhraseRow): string {
      return `/language/${target_language_code}/phrase/${row.slug}`;
    }

    // Function to generate tooltips for each row
    function getPhraseTooltip(row: PhraseRow): string {
      return row.usage_notes || '';
    }

    let mounted = false;

    function setupDeleteButtons() {
      document.addEventListener('click', function(e) {
        const target = e.target as HTMLElement;
        const deleteBtn = target.closest('.delete-phrase-btn');
        
        if (deleteBtn) {
          e.preventDefault();
          e.stopPropagation(); 
          e.stopImmediatePropagation();

          const phraseSlug = deleteBtn.getAttribute('data-phrase-slug');
          const phraseText = deleteBtn.getAttribute('data-phrase-text');
          if (phraseSlug && phraseText) {
            handleDeletePhrase(phraseSlug, phraseText);
          }
        }
      }, true); 
      
      mounted = true;
    }
    
    onMount(() => {
      if (!loadData) {
        console.error("DataGrid cannot be initialized for phrases because supabaseClient is not available.");
      }
      if (!mounted) {
        setupDeleteButtons();
      }
    });
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
                  {loadData}
                  initialRows={phrases}
                  initialTotal={total}
                  getRowUrl={getPhraseUrl}
                  getRowTooltip={getPhraseTooltip}
                  defaultSortField="updated_at"
                  defaultSortDir="desc"
                  queryModifier={(query) => query.eq('target_language_code', target_language_code)}
        />
    {:else if browser && !loadData && phrases.length > 0}
        <div class="alert alert-danger">
            Could not initialize phrase data. Authentication context might be missing, or there was an issue loading the data provider.
        </div>
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

    /* Styles for delete button */
    :global(.delete-phrase-btn) {
        padding: 0.25rem 0.5rem;
    }
    
    :global(.delete-phrase-btn:hover) {
        background-color: var(--bs-danger-dark, #bb2d3b);
    }
</style> 