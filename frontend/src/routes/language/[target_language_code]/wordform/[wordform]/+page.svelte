<script lang="ts">
  import type { PageData } from './$types';  
  import { Card, MetadataCard } from '$lib';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { SITE_NAME } from '$lib/config';
  import { truncate, generateMetaDescription } from '$lib/utils';
  
  export let data: PageData;
  const { wordformData } = data;
  
  // Make sure we have valid data before unwrapping
  $: isValidData = wordformData && wordformData.wordform_metadata;
  
  // Unwrap the data from the response
  $: wordform_metadata = isValidData ? wordformData.wordform_metadata : null;
  $: lemma_metadata = isValidData ? wordformData.lemma_metadata : null;
  $: target_language_code = isValidData ? wordformData.target_language_code : '';
  $: target_language_name = isValidData ? wordformData.target_language_name : '';
  $: metadata = isValidData ? wordformData.metadata : null;
  
  // Generate API URL for delete action only if we have valid data
  $: deleteUrl = isValidData ? getApiUrl(RouteName.WORDFORM_VIEWS_DELETE_WORDFORM_VW, {
    target_language_code,
    wordform: wordform_metadata.wordform
  }) : '';
  
  function handleDeleteSubmit(event: SubmitEvent) {
    const confirmed = confirm('Are you sure you want to delete this wordform? This action cannot be undone.');
    if (!confirmed) {
      event.preventDefault();
    }
  }
</script>

<svelte:head>
  <title>{truncate(isValidData ? wordform_metadata.wordform : '', 30)} | Wordform | {target_language_name || target_language_code} | {SITE_NAME}</title>
  {#if isValidData && wordform_metadata.translations}
    <meta name="description" content="{generateMetaDescription(
      wordform_metadata.translations.join('; '),
      `${wordform_metadata.wordform} - ${target_language_name || target_language_code} wordform`
    )}">
  {/if}
</svelte:head>

<div class="container py-4">
  {#if !isValidData}
    <div class="alert alert-info" role="alert">
      <div class="d-flex align-items-center">
        <div class="spinner-border spinner-border-sm me-3" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <div>
          <h4 class="alert-heading mb-1">Loading Wordform Data...</h4>
          <p class="mb-0">Please wait while we load or generate the wordform information.</p>
        </div>
      </div>
    </div>
  {:else}
    <div class="row mb-4">
      <div class="col">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="/">Languages</a></li>
            <li class="breadcrumb-item"><a href="/language/{target_language_code}/sources">{target_language_name}</a></li>
            <li class="breadcrumb-item"><a href="/language/{target_language_code}/wordforms">Wordforms</a></li>
            <li class="breadcrumb-item active" aria-current="page">{wordform_metadata.wordform}</li>
          </ol>
        </nav>
      </div>
    </div>
    
    <div class="row mb-3">
      <div class="col-md-8">
        <h1 class="display-4 mb-3 hz-foreign-text">{wordform_metadata.wordform}</h1>
      </div>
      <div class="col-md-4 text-md-end">
        {#if metadata}
        <MetadataCard {metadata} />
        {/if}
      </div>
    </div>

    <div class="row mb-4">
      <div class="col">
        <form action={deleteUrl} method="POST" 
              on:submit={handleDeleteSubmit}>
          <button type="submit" class="btn btn-sm btn-danger">Delete wordform</button>
        </form>
      </div>
    </div>
    
    <div class="row">
      <div class="col-md-6">
        <Card title="Wordform Details">
          <div class="translations mb-3">
            <p><strong>Translation:</strong> 
              {#if wordform_metadata.translations && wordform_metadata.translations.length > 0}
                {#each wordform_metadata.translations as translation}
                  <span class="badge bg-secondary me-1">{translation}</span>
                {/each}
              {:else}
                <span class="text-muted">No translation available</span>
              {/if}
            </p>
          </div>
          
          <p><strong>Part of Speech:</strong> <span class="badge rounded-pill bg-light-subtle me-1">{wordform_metadata.part_of_speech || 'Unknown'}</span></p>
          
          <div class="mb-3">
            <p class="mb-2"><strong>Inflection Type:</strong></p> 
            {#if wordform_metadata.inflection_types && wordform_metadata.inflection_types.length > 0}
              {#each wordform_metadata.inflection_types as inflection_type}
                <span class="badge bg-light-subtle me-1 mb-1">{inflection_type}</span>
              {/each}
            {:else if wordform_metadata.inflection_type}
              <span class="badge bg-light-subtle me-1">{wordform_metadata.inflection_type}</span>
            {:else}
              <span class="text-muted">Not available</span>
            {/if}
          </div>
          
          <p>
            <strong>Is Dictionary Form:</strong> 
            {#if wordform_metadata.is_lemma}
              <span class="text-success">Yes</span>
            {:else}
              <span class="text-warning">No</span>
            {/if}
          </p>
        </Card>
      </div>
      
      <div class="col-md-6">
        {#if lemma_metadata && Object.keys(lemma_metadata).length > 0}
          <Card title="Dictionary Form Information">
            <div class="text-center mb-3">
              <a href="/language/{target_language_code}/lemma/{lemma_metadata.lemma}" 
                class="btn btn-lg btn-primary hz-foreign-text fw-bold">
                {lemma_metadata.lemma}
              </a>
            </div>
            
            {#if wordform_metadata.possible_misspellings && wordform_metadata.possible_misspellings.length > 0}
              <div class="possible-misspellings mb-3">
                <p><strong>Possible Corrections:</strong></p>
                <ul class="list-group">
                  {#each wordform_metadata.possible_misspellings as misspelling}
                    <li class="list-group-item hz-foreign-text">{misspelling}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </Card>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .hz-foreign-text {
    font-family: 'Times New Roman', Times, serif;
    font-style: italic;
  }
  
  .breadcrumb {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
  }
  
  .badge {
    font-weight: normal;
    padding: 0.5em 0.8em;
  }
</style> 