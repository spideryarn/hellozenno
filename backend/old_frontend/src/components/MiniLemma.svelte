<!-- Define the props -->
<script lang="ts">
  export let lemma: string;
  export let partOfSpeech: string = "";
  export let translations: string[] = [];
  export let href: string;
</script>

<!-- Component template -->
<div class="mini-lemma">
  <a {href} class="lemma-link">
    <div class="lemma-content">
      <div class="lemma-text">{lemma}</div>
      {#if partOfSpeech}
        <div class="part-of-speech">{partOfSpeech}</div>
      {/if}
      {#if translations && translations.length > 0}
        <div class="translations">{translations.join(', ')}</div>
      {/if}
    </div>
  </a>
</div>

<!-- Component styles -->
<style>
  .mini-lemma {
    margin: 0.25rem 0;
  }

  .lemma-link {
    text-decoration: none;
    color: inherit;
    display: block;
  }

  .lemma-content {
    padding: 0.5rem 0.75rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
    transition: all 0.2s;
  }

  .lemma-content:hover {
    background-color: #f8fafc;
    border-color: #cbd5e1;
  }

  .lemma-text {
    font-size: 1.1rem;
    font-weight: bold;
    line-height: 1.4;
    margin-bottom: 0.125rem;
  }

  .part-of-speech {
    font-size: 0.875rem;
    color: #64748b;
    font-style: italic;
    line-height: 1.4;
    margin-bottom: 0.125rem;
  }

  .translations {
    font-size: 0.875rem;
    color: #64748b;
    line-height: 1.4;
  }
</style>