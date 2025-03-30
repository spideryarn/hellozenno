<script lang="ts">
  import type { PageData } from './$types';
  import SourceItem from '$lib/components/SourceItem.svelte';
  
  export let data: PageData;
  
  const { languageCode, languageName, sources, currentSort } = data;
</script>

<h1 class="mb-4">{languageName} Sources</h1>

<!-- Navigation links -->
<div class="mb-3">
  <nav class="nav nav-pills gap-2">
    <a class="nav-link active" href="/language/{languageCode}/sources">Sources</a>
    <a class="nav-link" href="/language/{languageCode}/wordforms">Wordforms</a>
    <a class="nav-link" href="/language/{languageCode}/lemmas">Lemmas</a>
    <a class="nav-link" href="/language/{languageCode}/sentences">Sentences</a>
    <a class="nav-link" href="/language/{languageCode}/phrases">Phrases</a>
    <a class="nav-link" href="/language/{languageCode}/flashcards">Flashcards</a>
  </nav>
</div>

<!-- Sort options -->
<div class="mb-4 text-secondary">
  Sort by:
  <a href="/language/{languageCode}/sources?sort=alpha" 
     class="text-decoration-none ms-2 me-2 {currentSort === 'alpha' ? 'fw-bold text-primary' : ''}">
    Alphabetical
  </a> |
  <a href="/language/{languageCode}/sources?sort=date"
     class="text-decoration-none ms-2 {currentSort === 'date' ? 'fw-bold text-primary' : ''}">
    Recently Modified
  </a>
</div>

{#if sources.length === 0}
  <div class="alert alert-info">No sources available for {languageName} yet.</div>
{:else}
  <div class="list-group">
    {#each sources as source}
      <SourceItem 
        name={source.name}
        displayName={source.display_name}
        slug={source.slug}
        {languageCode}
        description={source.description}
        statistics={source.statistics}
      />
    {/each}
  </div>
{/if} 