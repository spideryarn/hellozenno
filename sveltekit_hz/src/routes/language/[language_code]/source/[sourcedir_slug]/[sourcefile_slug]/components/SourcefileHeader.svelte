<script lang="ts">
  import type { Sourcefile, Sourcedir, Metadata, Navigation, Stats } from '$lib/types/sourcefile';
  
  export let sourcefile: Sourcefile;
  export let sourcedir: Sourcedir;
  export let metadata: Metadata;
  export let navigation: Navigation;
  export let stats: Stats;
  export let language_code: string;
  export let sourcedir_slug: string;
  export let sourcefile_slug: string;
  
  // For description editing
  let isEditingDescription = false;
  let descriptionText = sourcefile.description || '';
  
  function editDescription() {
    isEditingDescription = true;
  }
  
  async function saveDescription() {
    // This would call the API to save the description
    // For now, just toggle the edit mode off
    isEditingDescription = false;
  }
  
  function getSourcefileTypeIcon(type: string) {
    switch (type) {
      case 'text':
        return '📄';
      case 'image':
        return '🖼️';
      case 'audio':
        return '🔊';
      case 'youtube_audio':
        return '🎵';
      default:
        return '📄';
    }
  }
</script>

<div class="metadata-display">
  {#if metadata}
    <p>Created: <span class="metadata-timestamp">{metadata.created_at}</span></p>
    <p>Updated: <span class="metadata-timestamp">{metadata.updated_at}</span></p>
    {#if metadata.image_processing && metadata.image_processing.was_resized}
      <p>Image resized: {Math.round(metadata.image_processing.original_size / 1024)}KB → {Math.round(metadata.image_processing.final_size / 1024)}KB</p>
    {/if}
  {/if}
</div>

<h1>
  <span class="file-icon">{getSourcefileTypeIcon(sourcefile.sourcefile_type)}</span>
  {sourcefile.filename}
  <button on:click={() => alert('Rename feature not implemented yet')} class="button small-button">
    <i class="fas fa-edit"></i> Rename
  </button>
  <div class="icon-delete-wrapper" on:click={() => alert('Delete feature not implemented yet')} style="display: inline-block; cursor: pointer;">
    <span class="delete-button">🗑️ Delete</span>
  </div>
</h1>

<div class="description-container">
  {#if isEditingDescription}
    <div class="description-edit">
      <textarea bind:value={descriptionText}></textarea>
      <div class="description-buttons">
        <button on:click={saveDescription} class="button small-button">Save</button>
        <button on:click={() => isEditingDescription = false} class="button small-button">Cancel</button>
      </div>
    </div>
  {:else}
    <div class="description-content" id="description-display">
      {#if sourcefile.description}
        <p>{sourcefile.description}</p>
      {:else}
        <p class="no-description"><em>No description available</em></p>
      {/if}
    </div>
    <button on:click={editDescription} class="button small-button">
      <i class="fas fa-edit"></i> Edit
    </button>
  {/if}
</div>

<div class="actions">
  <ul>
    <li class="button-group">
      {#if sourcefile.sourcefile_type === "image"}
        <a href="/api/lang/sourcefile/{language_code}/{sourcedir_slug}/{sourcefile_slug}/view" class="button">
          View image
        </a>
        <a href="/api/lang/sourcefile/{language_code}/{sourcedir_slug}/{sourcefile_slug}/download" class="button">
          Download image
        </a>
      {:else if sourcefile.sourcefile_type === "audio" || sourcefile.sourcefile_type === "youtube_audio"}
        <a href="/api/lang/sourcefile/{language_code}/{sourcedir_slug}/{sourcefile_slug}/download" class="button">
          Download audio
        </a>
      {/if}
    </li>
    <li class="button-group">
      <a href="/api/lang/sourcefile/{language_code}/{sourcedir_slug}/{sourcefile_slug}/process" class="button">
        Process this text
      </a>
    </li>
    {#if sourcefile.text_target}
      <li class="button-group">
        <a href="/flashcard/{language_code}/{sourcefile_slug}" class="button">
          Practice Flashcards
        </a>
      </li>
    {/if}
    <li class="navigation-buttons">
      {#if navigation.is_first}
        <span class="button disabled">Prev</span>
      {:else}
        <a href="/language/{language_code}/source/{sourcedir_slug}/{navigation.prev_slug}" class="button">
          Prev
        </a>
      {/if}
      
      <a href="/language/{language_code}/sourcedir/{sourcedir_slug}" class="button">
        Up
      </a>
      
      {#if navigation.is_last}
        <span class="button disabled">Next</span>
      {:else}
        <a href="/language/{language_code}/source/{sourcedir_slug}/{navigation.next_slug}" class="button">
          Next
        </a>
      {/if}
      
      <span class="file-position">({navigation.current_position}/{navigation.total_files})</span>
    </li>
  </ul>
</div>

<style>
  .metadata-display {
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 1rem;
  }
  
  .metadata-timestamp {
    font-family: monospace;
  }
  
  h1 {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    gap: 0.5rem;
  }
  
  .file-icon {
    font-size: 1.5rem;
  }
  
  .button {
    background-color: #4CAD53;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    border: none;
    cursor: pointer;
  }
  
  .small-button {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
  }
  
  .button.disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .description-container {
    display: flex;
    align-items: flex-start;
    margin-bottom: 1.5rem;
  }
  
  .description-content {
    flex: 1;
  }
  
  .no-description {
    color: #666;
  }
  
  .description-edit {
    flex: 1;
  }
  
  textarea {
    width: 100%;
    min-height: 100px;
    padding: 0.5rem;
  }
  
  .description-buttons {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
  
  .actions ul {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .button-group {
    display: flex;
    gap: 0.5rem;
  }
  
  .navigation-buttons {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .file-position {
    margin-left: 0.5rem;
  }
  
  .delete-button {
    color: #d9534f;
    font-size: 0.9rem;
  }
</style> 