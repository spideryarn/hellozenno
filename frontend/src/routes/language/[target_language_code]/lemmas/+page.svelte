<script lang="ts">
  import type { PageData } from './$types';
  import DataGrid from '$lib/components/DataGrid.svelte';
  import { SITE_NAME } from '$lib/config';
  import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
  import { createUserIdColumn } from '$lib/datagrid/utils';
  import { apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';

  // Define a type for the lemma row data
  interface LemmaRow {
    id: number;
    lemma: string;
    part_of_speech: string;
    translations: string[];
    updated_at: string;
    language_level: string;
    is_complete: boolean;
    commonality: number | null;
    etymology?: string;
    created_by_id: string;
  }

  export let data: PageData;
  
  // Destructure data for easier access
  const { target_language_code, language_name, lemmas, total, supabase: supabaseClient, session } = data;

  // Ensure supabaseClient is non-null for the DataGrid provider
  // +layout.ts should always provide a valid client instance (browser or server)
  if (!supabaseClient) {
    // This should ideally not happen if +layout.ts is set up correctly.
    // Handle critical error, maybe by not rendering the DataGrid or showing an error message.
    console.error("CRITICAL: Supabase client not available in lemmas page. DataGrid may not function.");
    // You might throw an error here or set a flag to prevent DataGrid rendering.
  }

  // Function to handle lemma deletion
  async function handleDeleteLemma(lemmaValue: string) {
    if (!supabaseClient) {
      console.error('Supabase client is not available on the DataGrid page for API call.');
      alert('Authentication context not available. Please try refreshing the page.');
      return;
    }
    if (!session) { // Also check for session as an indicator of auth state for user feedback
        alert('You must be logged in to delete lemmas. Please refresh and log in.');
        return;
    }

    if (confirm(`Are you sure you want to delete the lemma "${lemmaValue}"?\nThis will also delete all associated wordforms.`)) {
      try {
        await apiFetch({
          supabaseClient: supabaseClient,
          routeName: RouteName.LEMMA_API_DELETE_LEMMA_API,
          params: {
            target_language_code: target_language_code,
            lemma: lemmaValue
          },
          options: { method: 'POST' }
        });
        
        window.location.reload();
      } catch (error: any) {
        console.error('Error deleting lemma (DataGrid):', error);
        alert(`Failed to delete lemma: ${error.message || 'Unknown error'}. Please try again.`);
      }
    }
  }

  const columns = [
    { 
      id: 'lemma', 
      header: 'Lemma',
      accessor: (row: LemmaRow) => `<span class="hz-column-primary-green">${row.lemma}</span>`,
      isHtml: true
    },
    { 
      id: 'translations', 
      header: 'Translations', 
      accessor: (row: LemmaRow) => Array.isArray(row.translations) ? row.translations.join(', ') : '',
      filterType: 'json_array'
    },
    { id: 'part_of_speech', header: 'POS', width: 80 },
    { id: 'language_level', header: 'Level', width: 90 },
    { 
      id: 'is_complete', 
      header: 'Complete',
      accessor: (row: LemmaRow) => row.is_complete ? 'Yes' : 'No',
      width: 90
    },
    { 
      id: 'commonality', 
      header: 'Commonality',
      accessor: (row: LemmaRow) => row.commonality !== null ? row.commonality.toFixed(1) : '-',
      width: 110
    },
    createUserIdColumn({ 
      header: 'Created By', 
      width: 170 
    }),
    { 
      id: 'updated_at', 
      header: 'Modified', 
      accessor: (row: LemmaRow) => {
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
      accessor: (row: LemmaRow) => {
        return `
          <button 
            class="btn btn-sm btn-danger delete-lemma-btn" 
            data-lemma="${row.lemma}" 
            aria-label="Delete lemma"
            title="Delete lemma"
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
    table: 'lemma',
    selectableColumns: 'id,lemma,part_of_speech,translations,updated_at,language_level,is_complete,commonality,etymology,created_by_id',
    client: supabaseClient,
    jsonArrayColumns: ['translations']
  }) : undefined;
  
  // Function to generate URLs for each row
  function getLemmaUrl(row: LemmaRow): string {
    return `/language/${target_language_code}/lemma/${row.lemma}`;
  }
  
  // Function to generate tooltip content from etymology field
  function getLemmaTooltip(row: LemmaRow): string {
    return row.etymology ? `Etymology: ${row.etymology}` : '';
  }

  // Add event listener for delete buttons after the DOM is loaded
  let mounted = false;
  
  function setupDeleteButtons() {
    // Use event delegation for dynamically added buttons, in the CAPTURE phase
    document.addEventListener('click', function(e) {
      const target = e.target as HTMLElement;
      const deleteBtn = target.closest('.delete-lemma-btn');
      
      if (deleteBtn) {
        // This click is on our delete button or its child (e.g., SVG)
        e.preventDefault();  // Prevent the default action (e.g., link navigation)
        e.stopPropagation(); // Stop the event from bubbling up further
        e.stopImmediatePropagation(); // Stop any other listeners on the same element (document) for this event phase

        const lemma = deleteBtn.getAttribute('data-lemma');
        if (lemma) {
          handleDeleteLemma(lemma);
        }
      }
    }, true); // *** Use capture phase: true ***
    
    mounted = true;
  }
  
  // Set up the delete button functionality
  onMount(() => {
    if (!loadData) {
      // Handle the case where DataGrid cannot be initialized
      console.error("DataGrid cannot be initialized because supabaseClient is not available.");
      // Potentially show an error message to the user in the UI
    }
    if (!mounted) {
      setupDeleteButtons();
    }
  });

  // Note: The letter navigation feature is commented out but preserved for potential future use
  /*
  // Group lemmas by first letter for alphabetical display
  $: lemmasByLetter = data.lemmas.reduce((acc, lemma) => {
    const firstLetter = lemma.lemma.charAt(0).toUpperCase();
    if (!acc[firstLetter]) {
      acc[firstLetter] = [];
    }
    acc[firstLetter].push(lemma);
    return acc;
  }, {} as Record<string, typeof data.lemmas>);
  
  // Get sorted list of first letters
  $: letters = Object.keys(lemmasByLetter).sort();
  */
</script>

<svelte:head>
  <title>Lemmas | {language_name} | {SITE_NAME}</title>
</svelte:head>

<div class="container mt-4">
  <div class="row mb-4">
    <div class="col">
      <h1>Lemmas in {language_name}</h1>
      <p class="lead">Browse lemmas in the {language_name} language.</p>
    </div>
  </div>

  {#if lemmas && lemmas.length > 0}
    <DataGrid {columns}
              {loadData} 
              initialRows={lemmas}
              initialTotal={total}
              getRowUrl={getLemmaUrl}
              getRowTooltip={getLemmaTooltip}
              defaultSortField="lemma"
              defaultSortDir="asc"
              queryModifier={(query) => query.eq('target_language_code', target_language_code)}
    />
  {:else if browser && !loadData}
    <div class="alert alert-danger">
      Could not initialize lemma data. Authentication context might be missing.
    </div>
  {:else}
    <div class="alert alert-info">
      No lemmas found for {language_name}.
    </div>
  {/if}

  <!-- 
    Note: Letter navigation is commented out for now but might be brought back in the future
    <div class="alphabet-nav d-flex flex-wrap mb-3">
      {#each letters as letter}
        <a href="#{letter}" class="letter-link me-2 mb-2 px-2 py-1 border rounded text-decoration-none">
          {letter}
        </a>
      {/each}
    </div>
  -->

</div>

<style>
  .metadata-timestamp {
    font-family: var(--bs-font-monospace, monospace);
  }
  
  :global(.delete-lemma-btn) {
    padding: 0.25rem 0.5rem;
  }
  
  :global(.delete-lemma-btn:hover) {
    background-color: var(--bs-danger-dark, #bb2d3b);
  }
  
  /* UserLookup.svelte styling is now in global theme.css */
  
  /* Preserved styles for letter navigation if needed in the future
  .foreign-text {
    font-style: italic;
    font-family: "Times New Roman", Times, serif;
  }

  .letter-link {
    color: var(--bs-primary);
    background-color: var(--bs-dark);
    border-color: var(--bs-gray-700);
    transition: all 0.2s ease;
  }

  .letter-link:hover {
    background-color: var(--bs-primary);
    color: var(--bs-dark);
  }

  .letter-heading {
    border-bottom: 1px solid var(--bs-gray-700);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
  }
  */
</style> 