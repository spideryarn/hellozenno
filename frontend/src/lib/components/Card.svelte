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
  export let cardColor: string = '';
</script>

{#if linkUrl}
  <a href={linkUrl} class="text-decoration-none">
    <div class="card hz-language-item {className}" style={cardColor ? `--card-color: ${cardColor}` : ''}>
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
  <div class="card hz-language-item {className}" style={cardColor ? `--card-color: ${cardColor}` : ''}>
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
    --card-color: var(--hz-color-primary-green);
    position: relative;
    overflow: hidden;
  }
  
  .card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--card-color), rgba(var(--hz-color-background-rgb), 0.2));
    opacity: 0.7;
    transition: height 0.3s ease;
  }
  
  .card::after {
    content: "";
    position: absolute;
    bottom: 0;
    right: 0;
    width: 40%;
    height: 100%;
    background: linear-gradient(135deg, transparent 0%, rgba(var(--hz-color-background-rgb), 0.05) 40%, rgba(var(--card-color), 0.1) 100%);
    z-index: 0;
  }
  
  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  }
  
  .card:hover::before {
    height: 5px;
    opacity: 1;
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
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
    color: var(--hz-color-text-main);
    font-weight: 500;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    max-width: 75%;
    min-height: 2.6rem; /* Ensures consistent height regardless of line breaks */
    display: flex;
    align-items: flex-start;
    line-height: 1.3;
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