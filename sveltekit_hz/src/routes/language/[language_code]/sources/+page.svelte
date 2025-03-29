<script lang="ts">
  import type { PageData } from './$types';
  import SourceItem from '$lib/components/SourceItem.svelte';
  
  export let data: PageData;
  
  const { languageCode, languageName, sources, currentSort } = data;
</script>

<h1 class="mb-4">{languageName} Sources</h1>

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