<!-- Define the props -->
<script lang="ts">
  export let phrase: string;
  export let translation: string;
  export let href: string;
</script>

<!-- Component template -->
<div class="mini-sentence">
  <a {href} class="sentence-link">
    <div class="sentence-content">
      <div class="phrase">{phrase}</div>
      {#if translation}
        <div class="translation">{translation}</div>
      {/if}
    </div>
  </a>
</div>

<!-- Component styles -->
<style>
  .mini-sentence {
    margin: 0.25rem 0;
  }

  .sentence-link {
    text-decoration: none;
    color: inherit;
    display: block;
  }

  .sentence-content {
    padding: 0.5rem 0.75rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
    transition: all 0.2s;
  }

  .sentence-content:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
  }

  .phrase {
    font-size: 1rem;
    line-height: 1.4;
    margin-bottom: 0.125rem;
  }

  .translation {
    font-size: 0.875rem;
    color: #64748b;
    line-height: 1.4;
  }

  /* Add to base.css */
  :global(.example-usage-section) {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 2rem;
    align-items: start;
  }

  :global(.example-usage-section h2) {
    margin: 0;
    padding-top: 0.5rem;
  }
</style> 