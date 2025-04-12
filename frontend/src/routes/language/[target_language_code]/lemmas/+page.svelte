<script lang="ts">
  import type { PageData } from './$types';
  import { Card, LemmaCard } from '$lib';
  
  export let data: PageData;
  
  // Group lemmas by first letter for alphabetical display
  $: lemmasByLetter = data.lemmas.reduce((acc, lemma) => {
    const firstLetter = lemma.lemma.charAt(0).toUpperCase();
    if (!acc[firstLetter]) {
      acc[firstLetter] = [];
    }
    acc[firstLetter].push(lemma);
    return acc;
  }, {} as Record<string, typeof data.lemmas>);
  
  // Get sorted list of first letters
  $: letters = Object.keys(lemmasByLetter).sort();
</script>

<svelte:head>
  <title>Lemmas - {data.language_name}</title>
</svelte:head>

<div class="container mt-4">
  <div class="row mb-4">
    <div class="col">
      <h1>Lemmas in {data.language_name}</h1>
      <p class="lead">Browse {data.lemmas.length} lemmas in the {data.language_name} language.</p>
    </div>
  </div>

  <div class="row mb-4">
    <div class="col">
      <div class="btn-group" role="group" aria-label="Sort options">
        <a href="?sort=alpha" class="btn btn-outline-primary {data.current_sort === 'alpha' ? 'active' : ''}">
          Alphabetical
        </a>
        <a href="?sort=date" class="btn btn-outline-primary {data.current_sort === 'date' ? 'active' : ''}">
          Recently Updated
        </a>
        <a href="?sort=commonality" class="btn btn-outline-primary {data.current_sort === 'commonality' ? 'active' : ''}">
          Most Common
        </a>
      </div>
    </div>
  </div>

  {#if data.current_sort === 'alpha'}
    <!-- Alphabetical display with letter groups -->
    <div class="mb-4">
      <div class="alphabet-nav d-flex flex-wrap mb-3">
        {#each letters as letter}
          <a href="#{letter}" class="letter-link me-2 mb-2 px-2 py-1 border rounded text-decoration-none">
            {letter}
          </a>
        {/each}
      </div>

      {#each letters as letter}
        <div id={letter} class="mb-4">
          <h2 class="letter-heading">{letter}</h2>
          <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
            {#each lemmasByLetter[letter] as lemma}
              <div class="col">
                <LemmaCard lemma={lemma} target_language_code={data.target_language_code} />
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <!-- Linear list for date or commonality sort -->
    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
      {#each data.lemmas as lemma}
        <div class="col">
          <LemmaCard lemma={lemma} target_language_code={data.target_language_code} />
        </div>
      {/each}
    </div>
  {/if}

  <div class="mt-4 mb-4">
    <a href="/language/{data.target_language_code}/sources" class="btn btn-outline-secondary">
      Back to Sources
    </a>
  </div>
</div>

<style>
  .foreign-text {
    font-style: italic;
    font-family: "Times New Roman", Times, serif;
  }

  .letter-link {
    color: var(--bs-primary);
    background-color: var(--bs-dark);
    border-color: var(--bs-gray-700);
    transition: all 0.2s ease;
  }

  .letter-link:hover {
    background-color: var(--bs-primary);
    color: var(--bs-dark);
  }

  .letter-heading {
    border-bottom: 1px solid var(--bs-gray-700);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
  }

  .lemma-card {
    padding: 0.25rem;
  }
</style> 