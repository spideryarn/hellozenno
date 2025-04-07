<script lang="ts">

  import type { Sourcefile, Sourcedir, Metadata, Navigation, Stats } from '$lib/types/sourcefile';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { MetadataCard, DescriptionFormatted } from '$lib';
  import { goto } from '$app/navigation';
  import { getPageUrl } from '$lib/navigation';
  import { route } from '$lib/ROUTES';
  import { 
    CaretDoubleLeft, 
    CaretDoubleRight, 
    CaretLeft, 
    CaretRight, 
    ArrowUp, 
    PencilSimple, 
    Trash, 
    Image, 
    Download,
    FileText,
    SpeakerHigh,
    MusicNotes
  } from 'phosphor-svelte';
  
  export let sourcefile: Sourcefile;
  export const sourcedir: Sourcedir = undefined as unknown as Sourcedir;
  export let metadata: Metadata;
  export let navigation: Navigation;
  export const stats: Stats = undefined as unknown as Stats;
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
  
  // Helper function for navigation using Svelte's goto
  function navigateTo(url: string) {
    // Using SvelteKit's client-side routing with invalidation
    goto(url, { invalidateAll: true });
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
          body: JSON.stringify({}), // Add empty JSON object as body
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
      
      // Navigate back to the sourcedir page using hard reload
      const sourcedirUrl = getPageUrl('sourcedir', {
        language_code,
        sourcedir_slug
      });
      window.location.href = sourcedirUrl;
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
      
      // Update the local state to reflect the filename change
      sourcefile.filename = newName;
      
      // Get the new URL with the updated slug
      const sourcefileTextUrl = getPageUrl('sourcefile_text', {
        language_code,
        sourcedir_slug,
        sourcefile_slug: result.new_slug
      });
      
      // Use window.location.href instead of SvelteKit navigation
      // This forces a full page reload to ensure all components are fresh
      window.location.href = sourcefileTextUrl;
    } catch (error) {
      console.error('Error renaming file:', error);
      alert('Failed to rename file: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  }
  
  function getSourcefileTypeIcon(type: string) {
    switch (type) {
      case 'text':
        return FileText;
      case 'image':
        return Image;
      case 'audio':
        return SpeakerHigh;
      case 'youtube_audio':
        return MusicNotes;
      default:
        return FileText;
    }
  }

  // Generate URLs for view and download - these are actual API endpoints
  // Use reactive statements to ensure these update when sourcefile_slug changes
  $: viewUrl = getApiUrl(
    RouteName.SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW,
    {
      target_language_code: language_code,
      sourcedir_slug,
      sourcefile_slug
    }
  );

  $: downloadUrl = getApiUrl(
    RouteName.SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW,
    {
      target_language_code: language_code,
      sourcedir_slug,
      sourcefile_slug
    }
  );
  
  // Generate navigation URLs using the new route function
  $: sourcedirUrl = route('/language/[language_code]/source/[sourcedir_slug]', {
    language_code,
    sourcedir_slug
  });
  
  // Prepare navigation URLs only if the corresponding slugs exist
  $: firstSourcefileUrl = navigation.first_slug ? 
    route('/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text', {
      language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.first_slug
    }) : undefined;
    
  $: prevSourcefileUrl = navigation.prev_slug ? 
    route('/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text', {
      language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.prev_slug
    }) : undefined;
    
  $: nextSourcefileUrl = navigation.next_slug ? 
    route('/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text', {
      language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.next_slug
    }) : undefined;
    
  $: lastSourcefileUrl = navigation.last_slug ? 
    route('/language/[language_code]/source/[sourcedir_slug]/[sourcefile_slug]/text', {
      language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.last_slug
    }) : undefined;
    
  $: flashcardsUrl = route('/language/[language_code]/flashcards', {
    language_code
  }, { sourcefile: sourcefile_slug });
</script>

<div class="header-container">
  <div class="header-content">
    <h1>
      <span class="file-icon">
        {#if typeof getSourcefileTypeIcon(sourcefile.sourcefile_type) === 'string'}
          {getSourcefileTypeIcon(sourcefile.sourcefile_type)}
        {:else}
          <svelte:component this={getSourcefileTypeIcon(sourcefile.sourcefile_type)} size={24} />
        {/if}
      </span>
      {sourcefile.filename}
      <button on:click={renameSourcefile} class="button small-button">
        <PencilSimple size={16} weight="bold" /> Rename
      </button>
      <button on:click={deleteSourcefile} class="button delete-button small-button">
        <Trash size={16} weight="bold" /> Delete
      </button>
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
      <DescriptionFormatted 
        description={sourcefile.description} 
        placeholder="No description available"
        cssClass="" 
      />
    </div>
    <button on:click={editDescription} class="button small-button">
      <PencilSimple size={16} weight="bold" /> Edit
    </button>
  {/if}
</div>

<div class="actions">
  <ul>
    <li class="button-group">
      {#if sourcefile.sourcefile_type === "image"}
        <a href={viewUrl} class="button">
          <Image size={16} weight="bold" /> View image
        </a>
        <a href={downloadUrl} class="button">
          <Download size={16} weight="bold" /> Download image
        </a>
      {:else if sourcefile.sourcefile_type === "audio" || sourcefile.sourcefile_type === "youtube_audio"}
        <a href={downloadUrl} class="button">
          <Download size={16} weight="bold" /> Download audio
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
        <a href={flashcardsUrl} class="button">
          Practice Flashcards
        </a>
      </li>
    {/if}
    <li class="navigation-buttons">
      {#if navigation.is_first}
        <span class="button disabled" title="First file">
          <CaretDoubleLeft size={16} weight="bold" />
        </span>
      {:else if firstSourcefileUrl}
        <a 
          href={firstSourcefileUrl}
          class="button"
          data-sveltekit-reload
          title="First file: '{navigation.first_filename || 'Unknown'}'"
        >
          <CaretDoubleLeft size={16} weight="bold" />
        </a>
      {/if}
      
      {#if navigation.is_first}
        <span class="button disabled" title="Previous file">
          <CaretLeft size={16} weight="bold" />
        </span>
      {:else if prevSourcefileUrl}
        <a 
          href={prevSourcefileUrl}
          class="button"
          data-sveltekit-reload
          title="Previous file: '{navigation.prev_filename || 'Unknown'}'"
        >
          <CaretLeft size={16} weight="bold" />
        </a>
      {/if}
      
      <a 
        href={sourcedirUrl}
        class="button"
        data-sveltekit-reload
        title="Up to directory: '{navigation.sourcedir_path || sourcedir_slug}'"
      >
        <ArrowUp size={16} weight="bold" />
      </a>
      
      {#if navigation.is_last}
        <span class="button disabled" title="Next file">
          <CaretRight size={16} weight="bold" />
        </span>
      {:else if nextSourcefileUrl}
        <a 
          href={nextSourcefileUrl}
          class="button"
          data-sveltekit-reload
          title="Next file: '{navigation.next_filename || 'Unknown'}'"
        >
          <CaretRight size={16} weight="bold" />
        </a>
      {/if}

      {#if navigation.is_last}
        <span class="button disabled" title="Last file">
          <CaretDoubleRight size={16} weight="bold" />
        </span>
      {:else if lastSourcefileUrl}
        <a 
          href={lastSourcefileUrl}
          class="button"
          data-sveltekit-reload
          title="Last file: '{navigation.last_filename || 'Unknown'}'"
        >
          <CaretDoubleRight size={16} weight="bold" />
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
    display: flex;
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
  
  .delete-button {
    background-color: #d9534f;
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
  
  .error-message {
    color: #d9534f;
    font-size: 0.9rem;
  }
</style> 