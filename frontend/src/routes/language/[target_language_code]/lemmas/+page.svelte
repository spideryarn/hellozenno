<script lang="ts">
  import type { PageData } from './$types';
  import DataGrid from '$lib/components/DataGrid.svelte';
  import { SITE_NAME } from '$lib/config';
  
  export let data: PageData;
  
  // Destructure data for easier access
  const { target_language_code, language_name, lemmas, total } = data;

  import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
  import { supabase } from '$lib/supabaseClient';

  const columns = [
    { 
      id: 'lemma', 
      header: 'Lemma',
      accessor: row => `<span class="hz-column-primary-green">${row.lemma}</span>`,
      isHtml: true
    },
    { 
      id: 'translations', 
      header: 'Translations', 
      accessor: row => Array.isArray(row.translations) ? row.translations.join(', ') : '',
      filterType: 'json_array'
    },
    { id: 'part_of_speech', header: 'POS', width: 80 },
    { id: 'language_level', header: 'Level', width: 90 },
    { 
      id: 'is_complete', 
      header: 'Complete',
      accessor: row => row.is_complete ? 'Yes' : 'No',
      width: 90
    },
    { 
      id: 'commonality', 
      header: 'Commonality',
      accessor: row => row.commonality !== null ? row.commonality.toFixed(1) : '-',
      width: 110
    },
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
    }
  ];

  // Use the supabase data provider
  const loadData = supabaseDataProvider({
    table: 'lemma',
    selectableColumns: 'id,lemma,part_of_speech,translations,updated_at,language_level,is_complete,commonality',
    client: supabase,
    jsonArrayColumns: ['translations']
  });
  
  // Function to generate URLs for each row
  function getLemmaUrl(row: any): string {
    return `/language/${target_language_code}/lemma/${row.lemma}`;
  }

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

  {#if lemmas.length > 0}
    <DataGrid {columns}
              loadData={loadData}
              initialRows={lemmas}
              initialTotal={total}
              getRowUrl={getLemmaUrl}
              queryModifier={(query) => query.eq('target_language_code', target_language_code)}
    />
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

  <div class="mt-4 mb-4">
    <a href="/language/{target_language_code}/sources" class="btn btn-outline-secondary">
      Back to Sources
    </a>
  </div>
</div>

<style>
  .metadata-timestamp {
    font-family: var(--bs-font-monospace, monospace);
  }
  
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