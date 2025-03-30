<script lang="ts">
  import { page } from '$app/stores';
  import { get_api_url } from '$lib/utils';
  import { MetadataCard } from '$lib';
  
  // Get parameters
  export let data;
  const { phrase, language_code: languageCode } = data;
  const slug = $page.params.slug;
  
  // Create metadata object for MetadataCard
  const metadata = {
    created_at: phrase.created_at,
    updated_at: phrase.updated_at
  };
</script>

<svelte:head>
  <title>{phrase.canonical_form} | Hello Zenno</title>
</svelte:head>

<div class="container mt-4">
  <div class="row">
    <div class="col">
      <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
          <li class="breadcrumb-item"><a href="/">Home</a></li>
          <li class="breadcrumb-item">
            <a href="/language/{languageCode}/phrases">Phrases</a>
          </li>
          <li class="breadcrumb-item active" aria-current="page">
            {phrase.canonical_form}
          </li>
        </ol>
      </nav>
    </div>
  </div>
  
  <div class="row mb-4">
    <div class="col-md-8">
      <h1 class="display-4 mb-2 hz-foreign-text">{phrase.canonical_form}</h1>
      <div class="phrase-meta mb-3">
        {#if phrase.part_of_speech}
          <span class="badge bg-secondary me-2">{phrase.part_of_speech}</span>
        {/if}
        {#if phrase.difficulty_level}
          <span class="badge bg-info me-2">{phrase.difficulty_level}</span>
        {/if}
        {#if phrase.register}
          <span class="badge bg-warning me-2">{phrase.register}</span>
        {/if}
      </div>
    </div>
    <div class="col-md-4 text-md-end">
      <MetadataCard {metadata} />
    </div>
  </div>
  
  <div class="row">
    <div class="col-lg-8">
      <div class="card phrase-card mb-4">
        <div class="card-body">
          {#if phrase.translations && phrase.translations.length > 0}
            <h5 class="section-title">Translations</h5>
            <ul class="list-group list-group-flush translations-list mb-4">
              {#each phrase.translations as translation}
                <li class="list-group-item bg-transparent">{translation}</li>
              {/each}
            </ul>
          {/if}
          
          {#if phrase.raw_forms && phrase.raw_forms.length > 0}
            <h5 class="section-title">Forms</h5>
            <div class="phrase-forms mb-4">
              {#each phrase.raw_forms as form}
                <span class="form-badge hz-foreign-text me-2 mb-1">{form}</span>
              {/each}
            </div>
          {/if}
          
          {#if phrase.usage_notes}
            <h5 class="section-title">Usage Notes</h5>
            <p class="usage-notes">{phrase.usage_notes}</p>
          {/if}
        </div>
      </div>
    </div>
    
    <div class="col-lg-4">
      <div class="card action-card">
        <div class="card-header">
          <h3 class="h5 mb-0">Actions</h3>
        </div>
        <div class="card-body">
          <button 
            class="btn btn-danger" 
            on:click={() => {
              if (confirm('Are you sure you want to delete this phrase?')) {
                fetch(get_api_url(`lang/phrase/${languageCode}/detail/${slug}/delete`), {
                  method: 'POST'
                }).then(async (response) => {
                  if (response.ok) {
                    window.location.href = `/language/${languageCode}/phrases`;
                  } else {
                    const errorData = await response.json();
                    alert(errorData.description || 'Failed to delete phrase');
                  }
                }).catch(err => {
                  console.error('Error deleting phrase:', err);
                  alert('An error occurred while trying to delete this phrase');
                });
              }
            }}
          >
            Delete Phrase
          </button>
        </div>
      </div>
    </div>
  </div>
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

  .phrase-meta {
    padding: 0.5rem 0;
    border-left: 3px solid #4CAD53;
    padding-left: 0.8rem;
  }

  .phrase-card {
    border-color: #333;
    background-color: #1e1e1e;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .action-card {
    border-color: #333;
    background-color: #1e1e1e;
  }

  .section-title {
    color: #4CAD53;
    margin-bottom: 1rem;
    border-bottom: 1px solid #333;
    padding-bottom: 0.5rem;
  }

  .translations-list .list-group-item {
    border-color: #333;
    color: #e9e9e9;
  }

  .form-badge {
    display: inline-block;
    background-color: #252525;
    padding: 0.5em 0.8em;
    border-radius: 0.25rem;
    border: 1px solid #333;
  }

  .usage-notes {
    line-height: 1.5;
  }
</style> 