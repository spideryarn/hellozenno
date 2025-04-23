<script lang="ts">
  import { slide } from 'svelte/transition';
  
  // Props
  export let isExpanded = false;
  export let title: string;
  export let icon: any = null; // Component for the file type icon
  export let iconSize = 24;
  
  // Function to toggle expanded state
  function toggleExpanded() {
    isExpanded = !isExpanded;
  }
</script>

<div class="collapsible-header">
  <div class="header-visible">
    <h1>
      {#if icon}
        <span class="file-icon">
          <svelte:component this={icon} size={iconSize} />
        </span>
      {/if}
      {title}
      <button on:click={toggleExpanded} class="button small-button expand-button" aria-expanded={isExpanded}>
        {#if isExpanded}
          ▲ Collapse
        {:else}
          ▼ Expand
        {/if}
      </button>
    </h1>
  </div>
  
  {#if isExpanded}
    <div class="collapsible-content" transition:slide={{ duration: 300 }}>
      <slot></slot>
    </div>
  {/if}
</div>

<style>
  .collapsible-header {
    margin-bottom: 1rem;
  }
  
  .header-visible {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  h1 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0;
    flex: 1;
  }
  
  .file-icon {
    display: flex;
    align-items: center;
  }
  
  .expand-button {
    margin-left: auto;
  }
  
  .button {
    background-color: var(--hz-color-primary-green);
    color: var(--hz-color-text-main);
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }
  
  .small-button {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
  }
  
  .collapsible-content {
    margin-top: 1rem;
    border-top: 1px solid var(--hz-color-border-subtle);
    padding-top: 1rem;
  }
</style>