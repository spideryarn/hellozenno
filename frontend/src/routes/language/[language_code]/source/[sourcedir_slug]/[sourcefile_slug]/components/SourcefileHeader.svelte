<script lang="ts">
  import type { Sourcefile, Sourcedir, Metadata, Navigation, Stats } from '$lib/types/sourcefile';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { MetadataCard } from '$lib';
  import { goto } from '$app/navigation';
  
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
  let isProcessing = false;
  let processingError = '';
  
  function editDescription() {
    isEditingDescription = true;
  }
  
  // Helper function for navigation
  function navigateTo(url: string) {
    window.location.href = url;
  }
  
  async function saveDescription() {
    try {
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API,
          {
            target_language_code: language_code,
            sourcedir_slug,
            sourcefile_slug
          }
        ),
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ description: descriptionText }),
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to update description: ${response.statusText}`);
      }
      
      // Update the local state to reflect the change
      sourcefile.description = descriptionText;
      isEditingDescription = false;
    } catch (error) {
      console.error('Error updating description:', error);
      alert('Failed to update description. Please try again.');
    }
  }
  
  async function processSourcefile() {
    if (isProcessing) return;
    
    try {
      isProcessing = true;
      processingError = '';
      
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_PROCESS_SOURCEFILE_API,
          {
            target_language_code: language_code,
            sourcedir_slug,
            sourcefile_slug
          }
        ),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || `Failed to process file: ${response.statusText}`);
      }
      
      // Reload the page to see the processed results
      window.location.reload();
    } catch (error) {
      console.error('Error processing file:', error);
      processingError = error instanceof Error ? error.message : 'Unknown error';
    } finally {
      isProcessing = false;
    }
  }
  
  async function deleteSourcefile() {
    if (!confirm(`Are you sure you want to delete "${sourcefile.filename}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_DELETE_SOURCEFILE_API,
          {
            target_language_code: language_code,
            sourcedir_slug,
            sourcefile_slug
          }
        ),
        {
          method: 'DELETE',
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to delete file: ${response.statusText}`);
      }
      
      // Navigate back to the sourcedir page
      window.location.href = `/language/${language_code}/source/${sourcedir_slug}`;
    } catch (error) {
      console.error('Error deleting file:', error);
      alert('Failed to delete file. Please try again.');
    }
  }
  
  async function renameSourcefile() {
    const newName = prompt('Enter new filename:', sourcefile.filename);
    if (!newName || newName === sourcefile.filename) return;
    
    try {
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_RENAME_SOURCEFILE_API,
          {
            target_language_code: language_code,
            sourcedir_slug,
            sourcefile_slug
          }
        ),
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ new_name: newName }),
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || `Failed to rename file: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Redirect to the new URL with the updated slug
      window.location.href = `/language/${language_code}/source/${sourcedir_slug}/${result.new_slug}`;
    } catch (error) {
      console.error('Error renaming file:', error);
      alert('Failed to rename file: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
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

  // Generate URLs for view and download
  const viewUrl = getApiUrl(
    RouteName.SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW,
    {
      target_language_code: language_code,
      sourcedir_slug,
      sourcefile_slug
    }
  );

  const downloadUrl = getApiUrl(
    RouteName.SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW,
    {
      target_language_code: language_code,
      sourcedir_slug,
      sourcefile_slug
    }
  );
</script>

<div class="header-container">
  <div class="header-content">
    <h1>
      <span class="file-icon">{getSourcefileTypeIcon(sourcefile.sourcefile_type)}</span>
      {sourcefile.filename}
      <button on:click={renameSourcefile} class="button small-button">
        <i class="fas fa-edit"></i> Rename
      </button>
      <div class="icon-delete-wrapper" on:click={deleteSourcefile} style="display: inline-block; cursor: pointer;">
        <span class="delete-button">🗑️ Delete</span>
      </div>
    </h1>
  </div>
  <div class="metadata-container">
    <MetadataCard {metadata} />
  </div>
</div>

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
        <a href={viewUrl} class="button">
          View image
        </a>
        <a href={downloadUrl} class="button">
          Download image
        </a>
      {:else if sourcefile.sourcefile_type === "audio" || sourcefile.sourcefile_type === "youtube_audio"}
        <a href={downloadUrl} class="button">
          Download audio
        </a>
      {/if}
    </li>
    <li class="button-group">
      <button on:click={processSourcefile} class="button" disabled={isProcessing}>
        {#if isProcessing}
          Processing...
        {:else}
          Process this text
        {/if}
      </button>
      {#if processingError}
        <span class="error-message">{processingError}</span>
      {/if}
    </li>
    {#if sourcefile.text_target}
      <li class="button-group">
        <a href="/language/{language_code}/flashcards?sourcefile={sourcefile_slug}" class="button">
          Practice Flashcards
        </a>
      </li>
    {/if}
    <li class="navigation-buttons">
      {#if navigation.is_first}
        <span class="button disabled">First</span>
      {:else}
        <a 
          href="/language/{language_code}/source/{sourcedir_slug}/{navigation.first_slug}" 
          class="button"
          on:click|preventDefault={() => navigateTo(`/language/${language_code}/source/${sourcedir_slug}/${navigation.first_slug}/text`)}
        >
          First
        </a>
      {/if}
      
      {#if navigation.is_first}
        <span class="button disabled">Prev</span>
      {:else}
        <a 
          href="/language/{language_code}/source/{sourcedir_slug}/{navigation.prev_slug}" 
          class="button"
          on:click|preventDefault={() => navigateTo(`/language/${language_code}/source/${sourcedir_slug}/${navigation.prev_slug}/text`)}
        >
          Prev
        </a>
      {/if}
      
      <a href="/language/{language_code}/source/{sourcedir_slug}" class="button">
        Up
      </a>
      
      {#if navigation.is_last}
        <span class="button disabled">Next</span>
      {:else}
        <a 
          href="/language/{language_code}/source/{sourcedir_slug}/{navigation.next_slug}" 
          class="button"
          on:click|preventDefault={() => navigateTo(`/language/${language_code}/source/${sourcedir_slug}/${navigation.next_slug}/text`)}
        >
          Next
        </a>
      {/if}

      {#if navigation.is_last}
        <span class="button disabled">Last</span>
      {:else}
        <a 
          href="/language/{language_code}/source/{sourcedir_slug}/{navigation.last_slug}" 
          class="button"
          on:click|preventDefault={() => navigateTo(`/language/${language_code}/source/${sourcedir_slug}/${navigation.last_slug}/text`)}
        >
          Last
        </a>
      {/if}
      
      <span class="file-position">({navigation.current_position}/{navigation.total_files})</span>
    </li>
  </ul>
</div>

<style>
  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
  }
  
  .header-content {
    flex: 1;
  }
  
  .metadata-container {
    margin-left: 1rem;
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
  
  .button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
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
    align-items: center;
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
  
  .error-message {
    color: #d9534f;
    font-size: 0.9rem;
  }
</style> 