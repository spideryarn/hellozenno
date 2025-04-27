<script lang="ts">
  // Use correct path imports for Svelte 5 compatibility
  import PencilSimple from 'phosphor-svelte/lib/PencilSimple';
  import Trash from 'phosphor-svelte/lib/Trash';
  import FolderOpen from 'phosphor-svelte/lib/FolderOpen';
  import { onMount } from 'svelte';
  
  // Event handlers as props
  export let onRename: () => Promise<void>;
  export let onDelete: () => Promise<void>;
  export let onMove: (sourcedirSlug: string) => Promise<void>;
  
  // Data
  export let available_sourcedirs: Array<{
    slug: string;
    display_name: string;
    is_empty?: boolean;
  }> = [];
  
  // State
  let isDropdownOpen = false;
  let moveError = '';
  
  // Toggle dropdown visibility
  function toggleDropdown() {
    isDropdownOpen = !isDropdownOpen;
  }
  
  // Close dropdown when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const dropdown = document.querySelector('.sourcedir-dropdown');
    
    if (isDropdownOpen && dropdown && !dropdown.contains(event.target as Node)) {
      isDropdownOpen = false;
    }
  }
  
  // Setup dropdown handling on component mount
  onMount(() => {
    // Add event listener to close dropdown when clicking outside
    if (typeof document !== 'undefined') {
      document.addEventListener('click', handleClickOutside);
    }
    
    // Cleanup when component is destroyed
    return () => {
      if (typeof document !== 'undefined') {
        document.removeEventListener('click', handleClickOutside);
      }
    };
  });
</script>

<div class="file-operations">
  <h3>File Operations</h3>
  <div class="button-group">
    <button on:click={onRename} class="btn btn-sm btn-primary">
      <PencilSimple size={16} weight="bold" /> Rename
    </button>
    <button on:click={onDelete} class="btn btn-sm btn-danger">
      <Trash size={16} weight="bold" /> Delete
    </button>
    
    <div class="dropdown sourcedir-dropdown">
      <button 
        class="btn btn-sm btn-secondary"
        type="button"
        on:click|preventDefault|stopPropagation={toggleDropdown}
      >
        <FolderOpen size={16} weight="bold" /> Move to folder
      </button>
      
      {#if isDropdownOpen}
        <ul class="dropdown-menu dropdown-menu-end show hz-dropdown-menu">
          {#if available_sourcedirs.length === 0}
            <li><span class="dropdown-item disabled">No other folders available</span></li>
          {:else}
            {#each available_sourcedirs as dir}
              <li>
                <button 
                  class="dropdown-item" 
                  type="button" 
                  on:click={() => onMove(dir.slug)}
                >
                  {dir.display_name} 
                  {#if dir.is_empty}<span class="text-body-secondary">(empty)</span>{/if}
                </button>
              </li>
            {/each}
          {/if}
        </ul>
      {/if}
    </div>
    {#if moveError}
      <span class="error-message text-danger">{moveError}</span>
    {/if}
  </div>
</div>

<style>
  .file-operations {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--hz-color-border-subtle);
  }
  
  h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: var(--hz-color-text-secondary);
  }
  
  .button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
  }
  
  
  .dropdown {
    position: relative;
    display: inline-block;
  }
  
  .hz-dropdown-menu {
    position: absolute;
    z-index: 1000;
    display: none;
    min-width: 10rem;
    padding: 0.5rem 0;
    margin: 0.125rem 0 0;
    font-size: 0.9rem;
    color: var(--hz-color-text-main);
    text-align: left;
    list-style: none;
    background-color: var(--hz-color-surface);
    background-clip: padding-box;
    border: 1px solid var(--hz-color-border);
    border-radius: 0.375rem;
  }
  
  .hz-dropdown-menu.show {
    display: block;
  }

  .dropdown-menu-end {
    right: 0;
    left: auto;
  }
    
  .hz-dropdown-menu .dropdown-item {
    display: block;
    width: 100%;
    padding: 0.25rem 1rem;
    clear: both;
    font-weight: 400;
    color: var(--hz-color-text-main);
    text-align: inherit;
    text-decoration: none;
    white-space: nowrap;
    background-color: transparent;
    border: 0;
    cursor: pointer;
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out;
  }
  
  .hz-dropdown-menu .dropdown-item:hover,
  .hz-dropdown-menu .dropdown-item:focus {
    color: var(--hz-color-text-main);
    background-color: var(--hz-color-primary-green);
  }

  .hz-dropdown-menu .dropdown-item.disabled,
  .hz-dropdown-menu .dropdown-item:disabled {
    color: var(--hz-color-text-secondary);
    pointer-events: none;
    background-color: transparent;
  }
</style>