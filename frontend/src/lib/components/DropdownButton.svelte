<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';

  // Event dispatcher for component events
  const dispatch = createEventDispatcher();

  // Props
  export let buttonText: string = '';
  export let buttonContent: string = ''; // Alternative to buttonText for icon/HTML content
  export let buttonSvelteContent = null; // For Svelte component content (like Phosphor icons)
  export let buttonClass: string = 'btn btn-secondary';
  export let tooltipText: string = ''; // Optional tooltip for the button
  export let items: Array<{
    type: 'link' | 'button' | 'divider' | 'header';
    text?: string;
    href?: string;
    onClick?: () => void;
    class?: string;
  }> = [];
  export let isOpen: boolean = false;

  // Handle toggle dropdown
  function toggleDropdown() {
    isOpen = !isOpen;
    dispatch('toggle', isOpen);
  }

  // Handle click outside to close the dropdown
  function handleClickOutside(event: MouseEvent) {
    const dropdownElement = document.querySelector(`#${dropdownId}`);
    if (isOpen && dropdownElement && !dropdownElement.contains(event.target as Node)) {
      isOpen = false;
      dispatch('toggle', isOpen);
    }
  }

  // Generate a unique ID for this dropdown
  const dropdownId = `dropdown-${Math.random().toString(36).substring(2, 9)}`;

  // Setup click outside listener
  onMount(() => {
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });

  // Handle item click
  function handleItemClick(item: any) {
    if (item.onClick) {
      item.onClick();
    }
    // Close dropdown after action unless it's a header
    if (item.type !== 'header' && item.type !== 'divider') {
      isOpen = false;
    }
  }
</script>

<div class="dropdown" id={dropdownId}>
  <button
    class={buttonClass}
    type="button"
    aria-haspopup="true"
    aria-expanded={isOpen}
    on:click={toggleDropdown}
    title={tooltipText}
  >
    {#if buttonSvelteContent}
      <span class="d-flex align-items-center">
        <svelte:component this={buttonSvelteContent} size={16} weight="bold" class="me-1" />
        {buttonText}
      </span>
    {:else if buttonContent}
      {@html buttonContent}
    {:else}
      {buttonText}
    {/if}
  </button>

  {#if isOpen}
    <div class="dropdown-menu show" aria-labelledby={dropdownId}>
      {#each items as item}
        {#if item.type === 'header'}
          <h6 class="dropdown-header">{item.text}</h6>
        {:else if item.type === 'divider'}
          <hr class="dropdown-divider">
        {:else if item.type === 'link'}
          <a 
            class="dropdown-item {item.class || ''}"
            href={item.href || '#'}
            on:click={() => handleItemClick(item)}
          >
            {item.text}
          </a>
        {:else if item.type === 'button'}
          <button 
            class="dropdown-item {item.class || ''}"
            type="button" 
            on:click={() => handleItemClick(item)}
          >
            {item.text}
          </button>
        {/if}
      {/each}
    </div>
  {/if}
</div>

<style>
  .dropdown {
    position: relative;
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    z-index: 1000;
    display: none;
    min-width: 10rem;
    padding: 0.5rem 0;
    margin: 0.125rem 0 0;
    font-size: 1rem;
    color: #212529;
    text-align: left;
    list-style: none;
    background-color: #fff;
    background-clip: padding-box;
    border: 1px solid rgba(0,0,0,.15);
    border-radius: 0.25rem;
    width: auto;
    white-space: nowrap;
  }

  /* Only show dropdown menu when open */
  .dropdown-menu.show {
    display: block !important;
  }

  /* Dropdown item styles */
  .dropdown-header {
    display: block;
    padding: 0.5rem 1rem;
    margin-bottom: 0;
    font-size: 0.875rem;
    color: #6c757d;
    white-space: nowrap;
  }

  .dropdown-item {
    display: block;
    width: 100%;
    padding: 0.25rem 1rem;
    clear: both;
    font-weight: 400;
    color: #212529;
    text-align: inherit;
    white-space: nowrap;
    background-color: transparent;
    border: 0;
    text-decoration: none;
  }

  .dropdown-item:hover,
  .dropdown-item:focus {
    color: #1e2125;
    background-color: #e9ecef;
  }

  .dropdown-divider {
    height: 0;
    margin: 0.5rem 0;
    overflow: hidden;
    border-top: 1px solid rgba(0,0,0,.15);
  }
</style>