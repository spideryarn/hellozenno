<script lang="ts">
  import type { PageData } from './$types';
  import { RouteName } from '$lib/generated/routes';
  import { SITE_NAME } from '$lib/config';
  import DataGrid from '$lib/components/DataGrid.svelte';
  import { supabaseDataProvider } from '$lib/datagrid/providers/supabase';
  import { apiFetch } from '$lib/api';
  import { createUserIdColumn } from '$lib/datagrid/utils';
  import { Breadcrumbs, type BreadcrumbItem } from '$lib';
  
  export let data: PageData;
  
  // Extract data with reactive declarations
  $: ({ target_language_code: languageCode, languageName, sources, total } = data);

  // Breadcrumb items
  $: breadcrumbItems = [
    { label: 'Home', href: '/' },
    { label: 'Languages', href: '/languages' },
    { label: languageName ?? languageCode, href: `/language/${languageCode}/sources` },
    { label: 'Sources' }
  ] as BreadcrumbItem[];
  
  // Define columns for the DataGrid
  const columns = [
    { 
      id: 'path', 
      header: 'Path',
      accessor: (row: any) => `<span class="hz-column-primary-green">${row.path}</span>`,
      isHtml: true
    },
    createUserIdColumn({ header: 'Created By' }),
    { 
      id: 'updated_at', 
      header: 'Modified',
      accessor: (row: any) => {
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
    }
  ];

  // Set up the data provider using Supabase (reactive to handle client initialization)
  $: loadData = data.supabase ? supabaseDataProvider({
    table: 'sourcedir',
    selectableColumns: 'id,path,slug,description,created_by_id,updated_at', 
    client: data.supabase
  }) : null;

  // Function to generate URLs for each row
  function getSourcedirUrl(row: any): string {
    return `/language/${languageCode}/source/${row.slug}`;
  }
  
  // Function to generate tooltips for each row
  function getSourcedirTooltip(row: any): string {
    return row.description || '';
  }
  
  // Function to create a new source directory
  async function createNewSourceDir() {
    try {
      // Prompt for source directory name
      const dirName = prompt('Enter new source directory name:');
      if (!dirName) return; // User cancelled
      
      // Check if user is authenticated
      if (!data.supabase) {
        throw new Error('Authentication required to create directories');
      }
      
      // API call to create directory using apiFetch
      const response = await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEDIR_API_CREATE_SOURCEDIR_API,
        params: { target_language_code: languageCode },
        options: {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ path: dirName })
        }
      });
      
      // Navigate to the new sourcedir using the slug from the response
      if (response && response.slug) {
        window.location.href = `/language/${languageCode}/source/${response.slug}`;
      } else {
        // Fallback to reload if slug is not available
        window.location.reload();
      }
      
    } catch (error) {
      alert('Error creating directory: ' + (error instanceof Error ? error.message : String(error)));
    }
  }
</script>

<svelte:head>
  <title>Sources | {languageName} | {SITE_NAME}</title>
</svelte:head>

<div class="container mt-4">
  <Breadcrumbs items={breadcrumbItems} />
  
  <div class="row mb-4">
    <div class="col">
      <h1 class="mb-3">{languageName} Sources</h1>
      
      <!-- Navigation links -->
      <div class="mb-3">
        <nav class="nav nav-pills gap-2">
          <a class="nav-link active" href="/language/{languageCode}/sources">Sources</a>
          <a class="nav-link" href="/language/{languageCode}/wordforms">Wordforms</a>
          <a class="nav-link" href="/language/{languageCode}/lemmas">Lemmas</a>
          <a class="nav-link" href="/language/{languageCode}/sentences">Sentences</a>
          <a class="nav-link" href="/language/{languageCode}/phrases">Phrases</a>
          <a class="nav-link" href="/language/{languageCode}/flashcards">Flashcards</a>
          <!-- Generate moved to Sourcedir page Add Files dropdown -->
        </nav>
      </div>
      
      <!-- Actions toolbar -->
      <div class="mb-4 d-flex justify-content-between align-items-center">
        <button type="button" class="btn btn-success" on:click={createNewSourceDir}>
          New Source Directory
        </button>
      </div>
    </div>
  </div>
  
  <!-- DataGrid with built-in loading indicator -->
  {#if sources !== undefined && loadData}
    <DataGrid 
      {columns}
      loadData={loadData}
      initialRows={sources}
      initialTotal={total}
      getRowUrl={getSourcedirUrl}
      getRowTooltip={getSourcedirTooltip}
      defaultSortField="updated_at"
      defaultSortDir="desc"
      queryModifier={(query) => query.eq('target_language_code', languageCode)}
    />
  {:else if sources === undefined}
    <div class="alert alert-info">
      No sources found for {languageName}.
    </div>
  {/if}
</div>

<style>
  /* Removed unused .metadata-timestamp; timestamp styling now in cell HTML */
  
  /* UserLookup.svelte styling is now in global theme.css */
</style>