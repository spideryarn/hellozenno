<script lang="ts">
  import type { PageData } from './$types';
  
  export let data: PageData;
  
  const { languageCode, languageName, sources, currentSort } = data;
</script>

<div class="container">
  <h1>{languageName} Sources</h1>
  
  <!-- Sort options -->
  <div class="sort-options">
    Sort by:
    <a href="/language/{languageCode}/sources?sort=alpha" 
       class="sort-link {currentSort === 'alpha' ? 'active' : ''}">
      Alphabetical
    </a> |
    <a href="/language/{languageCode}/sources?sort=date"
       class="sort-link {currentSort === 'date' ? 'active' : ''}">
      Recently Modified
    </a>
  </div>

  {#if sources.length === 0}
    <p>No sources available for {languageName} yet.</p>
  {:else}
    <ul class="source-list">
      {#each sources as source}
        <li class="source-item card">
          <div class="source-header">
            <h3>
              <a href="/language/{languageCode}/source/{source.slug}">
                {source.display_name || source.name}
              </a>
            </h3>
          </div>
          <div class="source-stats">
            <span>{source.statistics.file_count} files</span>
            {#if source.statistics.sentence_count}
              <span>{source.statistics.sentence_count} sentences</span>
            {/if}
          </div>
          {#if source.description}
            <div class="source-description">
              {source.description}
            </div>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  .sort-options {
    margin: 1rem 0;
    font-size: 0.9rem;
    color: #666;
  }
  
  .sort-link {
    margin: 0 0.25rem;
    text-decoration: none;
    color: #0066cc;
  }
  
  .sort-link.active {
    font-weight: bold;
  }
  
  .source-list {
    list-style: none;
    padding: 0;
    margin: 20px 0;
  }

  .source-item {
    margin-bottom: 20px;
    padding: 15px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .source-header {
    margin-bottom: 10px;
  }

  .source-header h3 {
    margin: 0;
  }

  .source-stats {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 10px;
  }

  .source-stats span {
    margin-right: 15px;
  }

  .source-description {
    color: #333;
    font-size: 0.95rem;
    line-height: 1.5;
  }
</style> 