<!-- Define the props -->
<script lang="ts">
  export let wordform: string;
  export let translation: string | null = null;
  export let href: string;
</script>

<!-- Component template -->
<div class="mini-wordform">
  <a {href} class="wordform-link" title={translation || ''}>
    <div class="wordform-content">
      <span class="wordform">{wordform}</span>
      {#if translation}
        <span class="translation">- {translation}</span>
      {/if}
    </div>
  </a>
</div>

<!-- Component styles -->
<style>
  .mini-wordform {
    margin: 0.25rem 0;
    display: inline-block;
    margin-right: 1rem;
  }

  .wordform-link {
    text-decoration: none;
    color: inherit;
    display: block;
  }

  .wordform-content {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    transition: all 0.2s;
  }

  .wordform-content:hover {
    background-color: #f8fafc;
  }

  .wordform {
    font-size: 1rem;
    line-height: 1.4;
  }

  .translation {
    font-size: 0.875rem;
    color: #64748b;
    margin-left: 0.25rem;
  }
</style> 