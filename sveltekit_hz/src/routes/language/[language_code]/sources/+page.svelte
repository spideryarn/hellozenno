<script lang="ts">
  import type { PageData } from './$types';
  
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
      <div class="list-group-item hz-language-item mb-3">
        <div class="d-flex flex-column">
          <div class="mb-2">
            <h3 class="mb-0">
              <a href="/language/{languageCode}/source/{source.slug}" class="text-decoration-none">
                {source.display_name || source.name}
              </a>
            </h3>
          </div>
          <div class="text-secondary small mb-2">
            <span class="me-3">{source.statistics.file_count} files</span>
            {#if source.statistics.sentence_count}
              <span>{source.statistics.sentence_count} sentences</span>
            {/if}
          </div>
          {#if source.description}
            <div class="small">
              {source.description}
            </div>
          {/if}
        </div>
      </div>
    {/each}
  </div>
{/if} 