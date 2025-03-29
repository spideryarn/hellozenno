<script lang="ts">
  import type { PageData } from './$types';
  import Card from '$lib/components/Card.svelte';
  
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
        <Card 
          title={language.name}
          subtitle={language.code}
          href="/language/{language.code}/sources"
        />
      </div>
    {/each}
  </div>
{/if} 