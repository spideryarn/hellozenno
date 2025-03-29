<script lang="ts">
  import type { PageData } from './$types';
  
  // Data is now loaded from the server-side load function
  export let data: PageData;
  
  const { languages } = data;
</script>

<div class="container">
  <h1>Available Languages ({languages.length})</h1>
  
  {#if languages.length === 0}
    <p>No languages available</p>
  {:else}
    <ul class="languages-list">
      {#each languages as language}
        <li>
          <a href="/language/{language.code}/sources">
            {language.name}
            <span class="language-code">({language.code})</span>
          </a>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  h1 {
    margin-bottom: 2rem;
  }
  
  .languages-list {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    list-style: none;
    padding: 0;
  }
  
  .languages-list li {
    margin: 0;
  }
  
  .languages-list a {
    display: block;
    padding: 1.5rem;
    font-size: 1.25rem;
    font-weight: 500;
    text-align: center;
    text-decoration: none;
    color: #333;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .languages-list a:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  
  .language-code {
    display: block;
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.25rem;
  }
</style> 