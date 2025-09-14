<script lang="ts">
  // A component that formats text descriptions with proper line breaks
  // Single line breaks (\n) become <br> tags
  // Multiple line breaks (\n\n+) become separate paragraphs
  // Also includes edit functionality with keyboard shortcuts
  
  import PencilSimple from 'phosphor-svelte/lib/PencilSimple';
  
  export let description: string = '';
  export let placeholder: string = 'No description available';
  export let cssClass: string = '';
  export let onSave: (text: string) => Promise<void> | void = async () => {}; // Callback for saving
  export let editable: boolean = true; // Whether to show edit button
  
  let isEditing = false;
  let editedText = description;
  
  function startEditing() {
    editedText = description;
    isEditing = true;
  }
  
  function cancelEditing() {
    isEditing = false;
    editedText = description;
  }
  
  async function saveChanges() {
    try {
      await onSave(editedText.trim());
      description = editedText.trim();
      isEditing = false;
    } catch (error) {
      console.error('Error saving description:', error);
      alert('Failed to save description. Please try again.');
    }
  }
  
  function handleKeydown(event: KeyboardEvent) {
    // Ctrl+Enter to save
    if (event.key === 'Enter' && event.ctrlKey) {
      event.preventDefault();
      saveChanges();
    }
    
    // Escape to cancel
    if (event.key === 'Escape') {
      event.preventDefault();
      cancelEditing();
    }
  }
</script>

<div class="description-container">
  {#if isEditing}
    <div class="description-edit mb-3 p-3 border rounded">
      <!-- svelte-ignore a11y_autofocus -->
      <textarea 
        class="form-control" 
        rows="3" 
        bind:value={editedText} 
        placeholder="Enter description..." 
        on:keydown={handleKeydown}
        autofocus
      ></textarea>
      <div class="text-muted small mt-1 mb-2">
        Press <kbd>Ctrl+Enter</kbd> to save or <kbd>Esc</kbd> to cancel
      </div>
      <div class="d-flex justify-content-end">
        <button class="btn btn-outline-secondary me-2" on:click={cancelEditing}>Cancel</button>
        <button class="btn btn-success" on:click={saveChanges}>Save</button>
      </div>
    </div>
  {:else}
    <div class="d-flex align-items-start mb-3 p-3 border rounded {cssClass}">
      <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
      <div class="description-content w-100" 
           on:click={editable ? startEditing : undefined} 
           class:editable={editable}
           role={editable ? 'button' : undefined}
           tabindex={editable ? 0 : undefined}
           on:keydown={(e) => {
             if (!editable) return;
             if (e.key === 'Enter' || e.key === ' ') {
               e.preventDefault();
               startEditing();
             }
           }}>
        {#if description}
          <div>
            {#each description.split(/\n\n+/).map(para => para.trim()) as paragraph, i}
              <p class={i === description.split(/\n\n+/).length - 1 ? "mb-0" : "mb-2"}>
                {#each paragraph.split(/\n/).map(line => line.trim()) as line, j}
                  {line}
                  {#if j < paragraph.split(/\n/).length - 1}
                    <br>
                  {/if}
                {/each}
              </p>
            {/each}
          </div>
        {:else}
          <p class="text-muted fst-italic mb-0">{placeholder}</p>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  textarea {
    width: 100%;
    min-height: 100px;
  }
  
  kbd {
    /* Updated kbd styles for dark theme using variables */
    background-color: var(--hz-color-surface);
    border: 1px solid var(--hz-color-border);
    border-radius: 3px;
    box-shadow: 0 1px 0 rgba(0,0,0,0.2); /* Keep subtle shadow? Or remove? */
    color: var(--hz-color-text-main);
    display: inline-block;
    font-family: var(--hz-font-monospace); /* Use monospace font */
    font-size: 0.85em;
    font-weight: 700;
    line-height: 1;
    padding: 2px 4px;
    white-space: nowrap;
  }
  
  .editable {
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
  }
  
  .editable:hover {
    background-color: var(--hz-color-surface-hover, rgba(255, 255, 255, 0.05));
  }
  
  .editable:hover::after {
    content: 'Click to edit';
    position: absolute;
    right: 0;
    top: 0;
    font-size: 0.75rem;
    color: var(--hz-color-text-muted, #888);
    background-color: var(--hz-color-surface, #222);
    padding: 2px 6px;
    border-radius: 4px;
    opacity: 0.8;
  }
</style>