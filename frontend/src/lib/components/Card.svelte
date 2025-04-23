<script lang="ts">
  export let title: string = '';
  export let subtitle: string = '';
  /**
   * When provided, the entire card becomes a link to this URL.
   * IMPORTANT: Do not place <a> elements inside the card content when using this prop,
   * as nested anchor tags are invalid HTML and will cause errors.
   */
  export let linkUrl: string = '';
  export let className: string = '';
</script>

{#if linkUrl}
  <a href={linkUrl} class="text-decoration-none">
    <div class="card hz-language-item {className}">
      <div class="card-body">
        {#if title}
          <h2 class="card-title">{title}</h2>
        {/if}
        {#if subtitle}
          <p class="hz-language-code">{subtitle}</p>
        {/if}
        <slot />
      </div>
    </div>
  </a>
{:else}
  <div class="card hz-language-item {className}">
    <div class="card-body">
      {#if title}
        <h2 class="card-title">{title}</h2>
      {/if}
      {#if subtitle}
        <p class="hz-language-code">{subtitle}</p>
      {/if}
      <slot />
    </div>
  </div>
{/if}

<style>
  .card {
    border: none;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  }
  
  .card-body {
    position: relative;
    padding: 1.5rem;
    z-index: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  .card-title {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: var(--hz-color-text-main);
    font-weight: 500;
  }
  
  .hz-language-code {
    font-size: 0.9rem;
    color: var(--hz-color-text-secondary);
    background: var(--hz-color-surface-transparent-15);
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    margin-top: auto;
    align-self: flex-start;
  }

  a {
    text-decoration: none;
    color: inherit;
  }
</style> 