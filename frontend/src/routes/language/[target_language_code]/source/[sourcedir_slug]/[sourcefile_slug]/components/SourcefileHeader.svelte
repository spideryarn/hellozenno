<script lang="ts">
  import type { Sourcefile, Sourcedir, Metadata, Navigation, Stats } from '$lib/types/sourcefile';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { 
    CollapsibleHeader, 
    MetadataSection, 
    DescriptionSection, 
    FileOperationsSection 
  } from '$lib';
  import { goto } from '$app/navigation';
  import { getPageUrl } from '$lib/navigation';
  import { 
    CaretDoubleLeft, 
    CaretDoubleRight, 
    CaretLeft, 
    CaretRight, 
    ArrowUp, 
    Trash, 
    Image, 
    Download,
    FileText,
    SpeakerHigh,
    MusicNotes,
    PencilSimple,
    FolderOpen
  } from 'phosphor-svelte';
  
  export let sourcefile: Sourcefile;
  export const sourcedir: Sourcedir = undefined as unknown as Sourcedir;
  export let metadata: Metadata;
  export let navigation: Navigation;
  export const stats: Stats = undefined as unknown as Stats;
  export let target_language_code: string;
  export let sourcedir_slug: string;
  export let sourcefile_slug: string;
  export let available_sourcedirs: any[] = [];
  
  // Variables for processing state
  let isProcessing = false;
  let processingError = '';
  
  // Collapsible header state - default to collapsed
  let isHeaderExpanded = false;
  
  // Variables for sourcedir dropdown
  let moveError = '';
  
  async function moveSourcefile(newSourcedirSlug: string) {
    if (newSourcedirSlug === sourcedir_slug) {
      return; // No need to move if it's the same directory
    }
    
    // Find the directory name for the confirmation message
    const targetDir = available_sourcedirs.find(dir => dir.slug === newSourcedirSlug);
    const targetDirName = targetDir ? targetDir.display_name : newSourcedirSlug;
    
    // Confirm before moving
    if (!confirm(`Move "${sourcefile.filename}" to "${targetDirName}"?`)) {
      return;
    }
    
    try {
      moveError = '';
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_MOVE_SOURCEFILE_API,
          {
            target_language_code,
            sourcedir_slug,
            sourcefile_slug
          }
        ),
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ new_sourcedir_slug: newSourcedirSlug }),
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to move file');
      }
      
      const result = await response.json();
      
      // After successful move, navigate to the file in its new location
      window.location.href = `/language/${target_language_code}/source/${newSourcedirSlug}/${result.new_sourcefile_slug}/text`;
      
    } catch (error) {
      console.error('Error moving file:', error);
      moveError = error instanceof Error ? error.message : 'Unknown error';
    }
  }
  
  // Helper function for navigation using Svelte's goto
  function navigateTo(url: string) {
    // Using SvelteKit's client-side routing with invalidation
    goto(url, { invalidateAll: true });
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
            target_language_code: target_language_code,
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
            target_language_code: target_language_code,
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
        target_language_code,
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
            target_language_code: target_language_code,
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
        target_language_code,
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

  // Handle description save
  async function saveDescription(text: string) {
    try {
      const response = await fetch(
        getApiUrl(
          RouteName.SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API,
          {
            target_language_code: target_language_code,
            sourcedir_slug,
            sourcefile_slug
          }
        ),
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ description: text }),
        }
      );
      
      if (!response.ok) {
        throw new Error(`Failed to update description: ${response.statusText}`);
      }
      
      // Update the local state to reflect the change
      sourcefile.description = text;
    } catch (error) {
      console.error('Error updating description:', error);
      alert('Failed to update description. Please try again.');
      throw error; // Propagate error to component
    }
  }

  // Generate URLs for view and download - these are actual API endpoints
  // Use reactive statements to ensure these update when sourcefile_slug changes
  $: viewUrl = getApiUrl(
    RouteName.SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW,
    {
      target_language_code: target_language_code,
      sourcedir_slug,
      sourcefile_slug
    }
  );

  $: downloadUrl = getApiUrl(
    RouteName.SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW,
    {
      target_language_code: target_language_code,
      sourcedir_slug,
      sourcefile_slug
    }
  );
  
  // Generate navigation URLs using getPageUrl
  $: sourcedirUrl = getPageUrl('sourcedir', {
    target_language_code,
    sourcedir_slug
  });
  
  // Prepare navigation URLs only if the corresponding slugs exist
  $: firstSourcefileUrl = navigation.first_slug ? 
    getPageUrl('sourcefile_text', {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.first_slug
    }) : undefined;
    
  $: prevSourcefileUrl = navigation.prev_slug ? 
    getPageUrl('sourcefile_text', {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.prev_slug
    }) : undefined;
    
  $: nextSourcefileUrl = navigation.next_slug ? 
    getPageUrl('sourcefile_text', {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.next_slug
    }) : undefined;
    
  $: lastSourcefileUrl = navigation.last_slug ? 
    getPageUrl('sourcefile_text', {
      target_language_code,
      sourcedir_slug,
      sourcefile_slug: navigation.last_slug
    }) : undefined;
    
  $: flashcardsUrl = getPageUrl('flashcards', {
    target_language_code
  }, { sourcefile: sourcefile_slug });
</script>

<CollapsibleHeader
  bind:isExpanded={isHeaderExpanded}
  title={sourcefile.filename}
  icon={getSourcefileTypeIcon(sourcefile.sourcefile_type)}
  iconSize={24}
>
  <!-- Content inside the collapsible section -->
  <div class="collapsible-sections">
    <MetadataSection {metadata} />
    
    <DescriptionSection 
      description={sourcefile.description}
      onSave={saveDescription}
    />
    
    <FileOperationsSection
      onRename={renameSourcefile}
      onDelete={deleteSourcefile}
      onMove={moveSourcefile}
      {available_sourcedirs}
    />
  </div>
</CollapsibleHeader>

<div class="actions">
  <div class="action-row">
    <div class="section process-section">
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
    </div>
    
    {#if sourcefile.text_target}
      <div class="section flashcards-section">
        <div class="section-divider"></div>
        <a href={flashcardsUrl} class="button">
          Practice Flashcards
        </a>
      </div>
    {/if}
    
    <div class="section navigation-section">
      <div class="section-divider"></div>
      <div class="navigation-buttons">
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
      </div>
    </div>
  </div>
</div>

<style>
  .collapsible-sections {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .actions {
    margin-bottom: 2rem;
  }
  
  .action-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem 1rem;
  }
  
  .section {
    display: flex;
    align-items: center;
  }
  
  .section-divider {
    height: 24px;
    width: 1px;
    background-color: rgba(255, 255, 255, 0.2);
    margin: 0 0.5rem;
  }
  
  .navigation-buttons {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .file-position {
    margin-left: 0.5rem;
    white-space: nowrap;
  }
  
  .error-message {
    color: #d9534f;
    font-size: 0.9rem;
    margin-left: 0.5rem;
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
    white-space: nowrap;
  }
  
  .button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .button.disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .action-row {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .section-divider {
      display: none;
    }
    
    .section {
      width: 100%;
      margin-bottom: 0.5rem;
    }
  }
</style>