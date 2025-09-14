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
      <span class="title-text" title={title}>{title}</span>
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
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0;
    flex: 1;
    overflow: hidden;
    min-width: 0;
    padding-right: 0.5rem;
  }
  
  /* Reduce the padding and gap on small screens */
  @media (max-width: 576px) {
    h1 {
      padding-right: 0.25rem;
      gap: 0.3rem;
    }
  }
  
  .file-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    margin-top: 0.15rem;
  }
  
  .title-text {
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    line-clamp: 2;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.3;
    max-height: 2.6em;
    min-width: 0;
    /* Add small margin to ensure button doesn't overlap with second line */
    margin-right: 1rem;
  }
  
  /* Reduce right margin on small screens */
  @media (max-width: 576px) {
    .title-text {
      margin-right: 0.25rem;
    }
  }
  
  .expand-button {
    margin-left: auto;
    flex-shrink: 0;
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
  
  /* Make the button smaller on mobile screens */
  @media (max-width: 576px) {
    .small-button {
      padding: 0.15rem 0.4rem;
      font-size: 0.7rem;
    }
  }
  
  .collapsible-content {
    margin-top: 1rem;
    border-top: 1px solid var(--hz-color-border-subtle);
    padding-top: 1rem;
  }
</style>