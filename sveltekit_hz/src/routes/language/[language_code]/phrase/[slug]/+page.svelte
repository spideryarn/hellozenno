<script lang="ts">
  import { page } from '$app/stores';
  import { get_api_url } from '$lib/utils';
  import { MetadataCard, Card } from '$lib';
  import WordformCard from '$lib/components/WordformCard.svelte';
  import PhraseCard from '$lib/components/PhraseCard.svelte';
  
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
      <!-- Main information card -->
      <Card className="mb-4">
        <div class="card-body">
          {#if phrase.translations && phrase.translations.length > 0}
            <h5 class="section-title">Translations</h5>
            <ul class="list-group list-group-flush translations-list mb-4">
              {#each phrase.translations as translation}
                <li class="list-group-item bg-transparent">{translation}</li>
              {/each}
            </ul>
          {/if}
          
          {#if phrase.literal_translation}
            <h5 class="section-title">Literal Translation</h5>
            <p class="mb-4">{phrase.literal_translation}</p>
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
            <p class="usage-notes mb-4">{phrase.usage_notes}</p>
          {/if}

          {#if phrase.etymology}
            <h5 class="section-title">Etymology</h5>
            <p class="mb-4">{phrase.etymology}</p>
          {/if}
          
          {#if phrase.cultural_context}
            <h5 class="section-title">Cultural Context</h5>
            <p class="mb-4">{phrase.cultural_context}</p>
          {/if}
          
          {#if phrase.commonality !== undefined || phrase.guessability !== undefined}
            <div class="row mb-4">
              {#if phrase.commonality !== undefined}
                <div class="col-md-6">
                  <h5 class="section-title">Commonality</h5>
                  <div class="progress mb-2">
                    <div class="progress-bar" role="progressbar" 
                      style="width: {Math.round((phrase.commonality || 0) * 100)}%;" 
                      aria-valuenow={Math.round((phrase.commonality || 0) * 100)} 
                      aria-valuemin="0" 
                      aria-valuemax="100">
                    </div>
                  </div>
                  <p>{Math.round((phrase.commonality || 0) * 100)}%</p>
                </div>
              {/if}
              
              {#if phrase.guessability !== undefined}
                <div class="col-md-6">
                  <h5 class="section-title">Guessability</h5>
                  <div class="progress mb-2">
                    <div class="progress-bar bg-info" role="progressbar" 
                      style="width: {Math.round((phrase.guessability || 0) * 100)}%;" 
                      aria-valuenow={Math.round((phrase.guessability || 0) * 100)} 
                      aria-valuemin="0" 
                      aria-valuemax="100">
                    </div>
                  </div>
                  <p>{Math.round((phrase.guessability || 0) * 100)}%</p>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      </Card>
      
      <!-- Example Sentences -->
      {#if phrase.example_sentences && phrase.example_sentences.length > 0}
        <Card title="Example Usage" className="mb-4">
          <div class="card-body">
            <ul class="list-group list-group-flush">
              {#each phrase.example_sentences as example}
                <li class="list-group-item bg-transparent">
                  <p class="hz-foreign-text mb-1">{example.sentence.sentence}</p>
                  <p>{example.sentence.translation}</p>
                  {#if example.context}
                    <small class="text-muted fst-italic">{example.context}</small>
                  {/if}
                </li>
              {/each}
            </ul>
          </div>
        </Card>
      {/if}
      
      <!-- Component Words -->
      {#if phrase.component_words && phrase.component_words.length > 0}
        <Card title="Component Words" className="mb-4">
          <div class="card-body">
            <div class="row row-cols-1 row-cols-md-2 g-4">
              {#each phrase.component_words as word}
                <div class="col">
                  <WordformCard
                    wordform={word.lemma}
                    translations={word.translation ? [word.translation] : []}
                    part_of_speech={word.notes}
                    language_code={languageCode}
                  />
                </div>
              {/each}
            </div>
          </div>
        </Card>
      {/if}
      
      <!-- Mnemonics -->
      {#if phrase.mnemonics && phrase.mnemonics.length > 0}
        <Card title="Mnemonics" className="mb-4">
          <div class="card-body">
            <ul class="list-group list-group-flush">
              {#each phrase.mnemonics as mnemonic}
                <li class="list-group-item bg-transparent">{mnemonic}</li>
              {/each}
            </ul>
          </div>
        </Card>
      {/if}
      
      <!-- Related Phrases -->
      {#if (phrase.related_to && phrase.related_to.length > 0) || (phrase.related_from && phrase.related_from.length > 0)}
        <Card title="Related Phrases" className="mb-4">
          <div class="card-body">
            <div class="row row-cols-1 row-cols-md-2 g-4">
              {#if phrase.related_to && phrase.related_to.length > 0}
                {#each phrase.related_to as relation}
                  <div class="col">
                    <PhraseCard 
                      phrase={relation.to_phrase.canonical_form}
                      translations={relation.to_phrase.translations}
                      slug={relation.to_phrase.slug}
                      part_of_speech={relation.to_phrase.part_of_speech}
                      notes={relation.relationship_type}
                      language_code={languageCode}
                    />
                  </div>
                {/each}
              {/if}
              
              {#if phrase.related_from && phrase.related_from.length > 0}
                {#each phrase.related_from as relation}
                  <div class="col">
                    <PhraseCard 
                      phrase={relation.from_phrase.canonical_form}
                      translations={relation.from_phrase.translations}
                      slug={relation.from_phrase.slug}
                      part_of_speech={relation.from_phrase.part_of_speech}
                      notes={relation.relationship_type}
                      language_code={languageCode}
                    />
                  </div>
                {/each}
              {/if}
            </div>
          </div>
        </Card>
      {/if}
    </div>
    
    <div class="col-lg-4">
      <!-- Actions Card -->
      <Card title="Actions" className="mb-4">
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
      </Card>
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
  
  .list-group-item {
    border-color: #333;
  }
  
  .progress {
    height: 8px;
    background-color: #333;
  }
</style> 