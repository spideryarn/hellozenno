<script lang="ts">
    import type { PageData } from './$types';
    import DataGrid from '$lib/components/DataGrid.svelte';
    import { SITE_NAME } from '$lib/config';
    import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
    import { apiFetch } from '$lib/api';
    import { RouteName } from '$lib/generated/routes';
    import { createUserIdColumn } from '$lib/datagrid/utils';
    import { onMount } from 'svelte';
    import { browser } from '$app/environment';
    
    // Define a type for the sentence row data
    interface SentenceRow {
      id: number;
      sentence: string;
      translation: string | null;
      language_level: string | null;
      updated_at: string;
      slug: string;
      lemma_words: string[] | null;
      created_by_id: string | null;
    }

    export let data: PageData;
    
    // Destructure data for easier access
    const { target_language_code, language_name, sentences, total, supabase: supabaseClient, session } = data;

    // Ensure supabaseClient is non-null for the DataGrid provider and delete actions
    if (!supabaseClient) {
      console.error("CRITICAL: Supabase client not available in sentences page. DataGrid may not function correctly.");
    }

    // Function to handle sentence deletion
    async function handleDeleteSentence(sentenceSlug: string, sentenceText: string) {
      if (!supabaseClient) {
        console.error('Supabase client is not available on the DataGrid page for API call.');
        alert('Authentication context not available. Please try refreshing the page.');
        return;
      }
      if (!session) {
        alert('You must be logged in to delete sentences. Please refresh and log in.');
        return;
      }

      if (confirm(`Are you sure you want to delete the sentence "${sentenceText}"?`)) {
        try {
          await apiFetch({
            supabaseClient: supabaseClient,
            routeName: RouteName.SENTENCE_API_DELETE_SENTENCE_API,
            params: {
              target_language_code: target_language_code,
              slug: sentenceSlug
            },
            options: { method: 'DELETE' }
          });
          
          window.location.reload(); // Reload to reflect changes
        } catch (error: any) {
          console.error('Error deleting sentence (DataGrid):', error);
          alert(`Failed to delete sentence: ${error.message || 'Unknown error'}. Please try again.`);
        }
      }
    }

    const columns = [
      { 
        id: 'sentence', 
        header: 'Sentence',
        accessor: (row: SentenceRow) => `<span class="hz-column-primary-green">${row.sentence}</span>`,
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
        accessor: (row: SentenceRow) => {
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
      {
        id: 'actions',
        header: '',
        width: 60,
        sortable: false,
        filterable: false,
        accessor: (row: SentenceRow) => {
          return `
            <button 
              class="btn btn-sm btn-danger delete-sentence-btn" 
              data-sentence-slug="${row.slug}"
              data-sentence-text="${row.sentence}"
              aria-label="Delete sentence"
              title="Delete sentence"
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
      table: 'sentence',
      selectableColumns: 'id,sentence,translation,language_level,updated_at,slug,lemma_words,created_by_id',
      client: supabaseClient,
      jsonArrayColumns: ['lemma_words']
    }) : undefined;
    
    // Function to generate URLs for each row
    function getSentenceUrl(row: SentenceRow): string {
      return `/language/${target_language_code}/sentence/${row.slug}`;
    }

    let mounted = false;

    function setupDeleteButtons() {
      document.addEventListener('click', function(e) {
        const target = e.target as HTMLElement;
        const deleteBtn = target.closest('.delete-sentence-btn');
        
        if (deleteBtn) {
          // Prevent default and stop propagation to avoid unintended navigation if inside a link
          e.preventDefault();
          e.stopPropagation(); 
          e.stopImmediatePropagation();

          const sentenceSlug = deleteBtn.getAttribute('data-sentence-slug');
          const sentenceText = deleteBtn.getAttribute('data-sentence-text');
          if (sentenceSlug && sentenceText) {
            handleDeleteSentence(sentenceSlug, sentenceText);
          }
        }
      }, true); // Use capture phase
      
      mounted = true;
    }
    
    onMount(() => {
      if (!loadData) {
        console.error("DataGrid cannot be initialized for sentences because supabaseClient is not available.");
      }
      if (!mounted) {
        setupDeleteButtons();
      }
    });
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
                  {loadData} 
                  initialRows={sentences}
                  initialTotal={total}
                  getRowUrl={getSentenceUrl}
                  defaultSortField="updated_at"
                  defaultSortDir="desc"
                  queryModifier={(query) => query.eq('target_language_code', target_language_code)}
        />
    {:else if browser && !loadData && sentences.length > 0}
        <div class="alert alert-danger">
            Could not initialize sentence data. Authentication context might be missing, or there was an issue loading the data provider.
        </div>
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

    /* Styles for delete button, similar to wordforms page */
    :global(.delete-sentence-btn) {
        padding: 0.25rem 0.5rem;
    }
    
    :global(.delete-sentence-btn:hover) {
        background-color: var(--bs-danger-dark, #bb2d3b);
    }
</style> 