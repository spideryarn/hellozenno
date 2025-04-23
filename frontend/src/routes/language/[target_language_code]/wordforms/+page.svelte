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
      { id: 'wordform', header: 'Wordform' },
      { id: 'lemma_text', header: 'Lemma' },
      { id: 'part_of_speech', header: 'POS', width: 80 },
    ];

    const loadData = supabaseDataProvider({
      table: 'wordform',
      selectableColumns: 'id,wordform,part_of_speech,lemma(lemma)',
      client: supabase
    });
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
        />
    {:else}
        <div class="alert alert-info">
            No wordforms found for {language_name}.
        </div>
    {/if}
</div> 