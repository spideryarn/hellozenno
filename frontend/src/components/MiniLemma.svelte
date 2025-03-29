<!-- Define the props -->
<script lang="ts">
  import '../styles/bulma-imports.css';
  
  export let lemma: string;
  export let partOfSpeech: string = "";
  export let translations: string[] = [];
  export let href: string;
</script>

<!-- Component template with Bulma classes -->
<div class="box p-3 mb-2 has-background-dark">
  <a {href} class="has-text-white">
    <div class="content">
      <p class="is-size-5 has-text-weight-bold mb-1">{lemma}</p>
      {#if partOfSpeech}
        <p class="is-size-7 has-text-grey-light is-italic mb-1">{partOfSpeech}</p>
      {/if}
      {#if translations && translations.length > 0}
        <p class="is-size-7 has-text-grey-light">{translations.join(', ')}</p>
      {/if}
    </div>
  </a>
</div>

<style>
  /* Minimal styles that aren't covered by Bulma */
  a {
    text-decoration: none;
  }
  
  .box {
    transition: transform 0.2s ease;
  }
  
  .box:hover {
    transform: translateY(-2px);
  }
</style>