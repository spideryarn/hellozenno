<script lang="ts">
  import { PencilSimple, Trash, FolderOpen } from 'phosphor-svelte';
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
    <button on:click={onRename} class="button small-button">
      <PencilSimple size={16} weight="bold" /> Rename
    </button>
    <button on:click={onDelete} class="button delete-button small-button">
      <Trash size={16} weight="bold" /> Delete
    </button>
    
    <div class="dropdown sourcedir-dropdown">
      <button 
        class="button small-button" 
        type="button"
        on:click|preventDefault|stopPropagation={toggleDropdown}
      >
        <FolderOpen size={16} weight="bold" /> Move to folder
      </button>
      
      {#if isDropdownOpen}
        <ul class="dropdown-menu dropdown-menu-end show">
          {#if available_sourcedirs.length === 0}
            <li><span class="dropdown-item">No other folders available</span></li>
          {:else}
            {#each available_sourcedirs as dir}
              <li>
                <button 
                  class="dropdown-item" 
                  type="button" 
                  on:click={() => onMove(dir.slug)}
                >
                  {dir.display_name} 
                  {#if dir.is_empty}<span class="text-muted">(empty)</span>{/if}
                </button>
              </li>
            {/each}
          {/if}
        </ul>
      {/if}
    </div>
    {#if moveError}
      <span class="error-message">{moveError}</span>
    {/if}
  </div>
</div>

<style>
  .file-operations {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }
  
  .button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
  }
  
  .button {
    background-color: #4CAD53;
    color: white;
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
  
  .delete-button {
    background-color: #d9534f;
  }
  
  .error-message {
    color: #d9534f;
    font-size: 0.9rem;
  }
  
  /* Dropdown styling */
  .dropdown {
    position: relative;
    display: inline-block;
  }
  
  .dropdown-menu {
    position: absolute;
    z-index: 1000;
    display: none;
    min-width: 10rem;
    padding: 0.5rem 0;
    margin: 0;
    font-size: 0.9rem;
    color: #e9e9e9;
    text-align: left;
    list-style: none;
    background-color: #1e1e1e;
    background-clip: padding-box;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 4px;
  }
  
  .dropdown-menu-end {
    right: 0;
    left: auto;
  }
  
  .dropdown-menu.show {
    display: block;
  }
  
  .dropdown-item {
    display: block;
    width: 100%;
    padding: 0.25rem 1rem;
    clear: both;
    font-weight: 400;
    color: #e9e9e9;
    text-align: inherit;
    text-decoration: none;
    white-space: nowrap;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
  
  .dropdown-item:hover, .dropdown-item:focus {
    color: #fff;
    background-color: #4CAD53;
  }
  
  .text-muted {
    color: #6c757d;
    font-style: italic;
  }
</style>