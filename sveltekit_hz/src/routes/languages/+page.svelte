<script lang="ts">
  import type { PageData } from './$types';
  
  // Data is now loaded from the server-side load function
  export let data: PageData;
  
  const { languages } = data;
</script>

<h1 class="mb-4">Available Languages ({languages.length})</h1>

{#if languages.length === 0}
  <div class="alert alert-info">No languages available</div>
{:else}
  <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-4 g-4">
    {#each languages as language}
      <div class="col">
        <a href="/language/{language.code}/sources" class="text-decoration-none">
          <div class="card h-100 hz-language-item">
            <div class="card-body text-center">
              <h2 class="card-title">{language.name}</h2>
              <p class="hz-language-code">({language.code})</p>
            </div>
          </div>
        </a>
      </div>
    {/each}
  </div>
{/if} 