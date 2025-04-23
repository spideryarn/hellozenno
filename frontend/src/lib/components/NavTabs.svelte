<script lang="ts">
  // NavTabs.svelte - A reusable component for navigation tabs
  export let tabs: {
    label: string;
    href: string;
    count?: number | null;
    active: boolean;
  }[] = [];
</script>

<div class="nav-tabs-container">
  <ul class="nav nav-tabs">
    {#each tabs as tab}
      <li class="nav-item">
        <a 
          class="nav-link {tab.active ? 'active' : ''}" 
          href={tab.href}
          aria-current={tab.active ? 'page' : undefined}
        >
          {tab.label}
          {#if tab.count !== undefined && tab.count !== null}
            <span class="count">({tab.count})</span>
          {/if}
        </a>
      </li>
    {/each}
  </ul>
</div>

<style>
  .nav-tabs-container {
    margin-bottom: 2rem;
  }
  
  /* Override Bootstrap styles to match the site's color scheme */
  :global(.nav-tabs .nav-link) {
    color: var(--hz-color-text-secondary);
    border: none;
    border-bottom: 2px solid transparent;
    padding: 0.5rem 1rem;
  }
  
  :global(.nav-tabs .nav-link:hover) {
    color: var(--hz-color-text-main);
    border-color: rgba(var(--hz-color-primary-green-rgb), 0.3);
    background-color: transparent;
  }
  
  :global(.nav-tabs .nav-link.active) {
    color: var(--hz-color-primary-green);
    font-weight: bold;
    background-color: transparent;
    border-bottom: 2px solid var(--hz-color-primary-green);
  }
  
  .count {
    margin-left: 0.25rem;
  }
  
  /* For dark background compatibility */
  :global(.nav-tabs) {
    border-bottom: 1px solid var(--hz-color-border);
  }
</style> 