<script context="module" lang="ts">
  /**
   * Breadcrumbs.svelte - Unified breadcrumb navigation component
   * 
   * Renders Bootstrap-style breadcrumbs with proper ARIA attributes.
   * The last item is always rendered as active (no link), regardless of href.
   */

  /** A single breadcrumb item */
  export interface BreadcrumbItem {
    /** Display label for the breadcrumb */
    label: string;
    /** Optional href for navigation (ignored for last item) */
    href?: string;
  }
</script>

<script lang="ts">
  /** Array of breadcrumb items to display */
  export let items: BreadcrumbItem[] = [];
  
  /** Optional additional CSS class for the nav wrapper */
  export let className: string = '';
</script>

{#if items.length > 0}
  <nav aria-label="breadcrumb" class={className || undefined}>
    <ol class="breadcrumb mb-0">
      {#each items as item, index}
        {@const isLast = index === items.length - 1}
        <li 
          class="breadcrumb-item"
          class:active={isLast}
          aria-current={isLast ? 'page' : undefined}
        >
          {#if isLast}
            <span class="breadcrumb-label" title={item.label}>{item.label}</span>
          {:else if item.href}
            <a href={item.href} class="breadcrumb-label" title={item.label}>{item.label}</a>
          {:else}
            <span class="breadcrumb-label" title={item.label}>{item.label}</span>
          {/if}
        </li>
      {/each}
    </ol>
  </nav>
{/if}

<style>
  .breadcrumb {
    background-color: rgba(0, 0, 0, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
  }
  
  .breadcrumb-label {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: inline-block;
    vertical-align: bottom;
  }
  
  /* Ensure links inherit proper styling */
  .breadcrumb-item a {
    color: var(--hz-color-text-secondary, #d7dadd);
    text-decoration: none;
  }
  
  .breadcrumb-item a:hover {
    color: var(--hz-color-text-main, #f8f9fa);
    text-decoration: underline;
  }
  
  .breadcrumb-item.active {
    color: var(--hz-color-text-main, #f8f9fa);
  }
</style>
