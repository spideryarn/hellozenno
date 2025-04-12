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
  import { onMount } from 'svelte';
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
  import { SourcefileProcessingQueue, processingState } from '$lib/processing-queue';
  
  export let sourcefile: Sourcefile;
  export const sourcedir: Sourcedir = undefined as unknown as Sourcedir;
  export let metadata: Metadata;
  export let navigation: Navigation;
  export const stats: Stats = undefined as unknown as Stats;
  export let target_language_code: string;
  export let sourcedir_slug: string;
  export let sourcefile_slug: string;
  export let available_sourcedirs: any[] = [];
  
  // Variables for sourcedir dropdown
  let moveError = '';
  
  // Collapsible header state - default to collapsed
  let isHeaderExpanded = false;
  
  // Auto-processing settings
  let autoProcessEnabled = true; // Default to enabled, could be user-configurable
  let showAutoProcessNotification = false;
  let autoProcessNotificationMessage = '';
  
  // Multi-processing counter and queue system
  let processingClicks = 0; // Count of process button clicks
  let pendingRuns = 0; // Number of queued processing runs
  
  // Create a reactive variable for the processing queue
  $: processingQueue = new SourcefileProcessingQueue(
    target_language_code,
    sourcedir_slug,
    sourcefile_slug
  );
  
  // Check if sourcefile needs INITIAL processing - only trigger for files that 
  // haven't been processed at all for a specific step
  function shouldAutoProcess(sourcefile: Sourcefile): boolean {
    console.log('Auto-process check - Sourcefile state:', {
      text_target: !!sourcefile.text_target,
      text_english: !!sourcefile.text_english,
      has_image: sourcefile.has_image,
      has_audio: sourcefile.has_audio,
      wordforms_count: metadata.wordforms_count || 0,
      stats: stats
    });
    
    // Case 1: No text extracted yet for image or audio files
    // Only trigger if the file has image/audio but NO text at all
    if (sourcefile.has_image || sourcefile.has_audio) {
      if (!sourcefile.text_target || sourcefile.text_target === '') {
        autoProcessNotificationMessage = 'Automatically extracting text from this file...';
        console.log('Auto-process: Triggering text extraction for image/audio');
        return true;
      }
    }
    
    // Case 2: Has text but COMPLETELY missing translation
    // Only trigger if there's content but NO translation at all
    if (sourcefile.text_target && sourcefile.text_target.trim() !== '' && sourcefile.text_target !== '-') {
      if (!sourcefile.text_english || sourcefile.text_english === '') {
        autoProcessNotificationMessage = 'Automatically translating text...';
        console.log('Auto-process: Triggering translation');
        return true;
      }
    }
    
    // Case 3: Has text with content but ZERO wordforms extracted
    // Only trigger if there's text content but NO wordforms at all
    const hasContent = sourcefile.text_target && sourcefile.text_target.trim() !== '' && sourcefile.text_target !== '-';
    const hasAbsolutelyNoWordforms = hasContent && (metadata.wordforms_count === 0);
    if (hasContent && hasAbsolutelyNoWordforms) {
      autoProcessNotificationMessage = 'Automatically extracting initial vocabulary from this text...';
      console.log('Auto-process: Triggering wordform extraction');
      return true;
    }
    
    console.log('Auto-process: No processing needed');
    return false;
  }
  
  // Trigger auto-processing if needed when component mounts
  onMount(() => {
    if (autoProcessEnabled && shouldAutoProcess(sourcefile)) {
      console.log('Auto-processing enabled and needed for this sourcefile');
      showAutoProcessNotification = true;
      
      // Add a slight delay to allow the UI to render first
      setTimeout(() => {
        processSourcefile();
      }, 500);
    }
  });
  
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
  
  // Create a custom event to signal data updates
  const dispatchProcessingComplete = (detail: any) => {
    // Use a custom event to notify parent components about the updated data
    const event = new CustomEvent('processingComplete', {
      detail,
      bubbles: true, // Allow event to bubble up the DOM tree
    });
    // Dispatch the event from this component
    if (typeof document !== 'undefined') {
      document.dispatchEvent(event);
    }
  };

  async function processSourcefile() {
    try {
      // Hide auto-process notification if showing
      showAutoProcessNotification = false;
      
      // Initialize the queue based on what needs to be processed
      const hasSteps = processingQueue.initializeQueue(sourcefile);
      
      if (!hasSteps) {
        // Nothing to process
        alert('No processing steps needed.');
        return;
      }
      
      // Increment the processing clicks counter and pending runs
      processingClicks++;
      pendingRuns++;
      
      // If already processing, just queue this run (don't execute yet)
      if ($processingState.isProcessing) {
        console.log(`Added processing run to queue. Now have ${pendingRuns} pending runs.`);
        return;
      }
      
      // Process all pending runs sequentially
      while (pendingRuns > 0) {
        // Use current pending runs count as iterations for this batch
        const iterations = pendingRuns;
        
        // Reset pending runs counter since we're about to process them all
        pendingRuns = 0;
        
        // Start processing with the current number of iterations
        await processingQueue.processAll(iterations);
        
        // Check if we have processed data
        if ($processingState.processedSourcefileData) {
          // Dispatch the event with the updated data
          dispatchProcessingComplete($processingState.processedSourcefileData);
          
          // Show success notification briefly (only for the last batch)
          if (pendingRuns === 0) {
            alert(`Successfully processed text ${iterations} time${iterations !== 1 ? 's' : ''}.`);
          }
        } else {
          // Fall back to page reload if no data returned
          window.location.reload();
          return;
        }
        
        // If more requests came in while we were processing, handle them in the next iteration
      }
    } catch (error) {
      console.error('Error processing file:', error);
      // Reset pending runs on error to avoid getting stuck
      pendingRuns = 0;
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
      <div class="process-controls">
        <button on:click={processSourcefile} class="button">
          {#if $processingState.isProcessing}
            {$processingState.description || 'Processing...'}
            {#if $processingState.totalIterations > 1}
              (Run {$processingState.currentIteration}/{$processingState.totalIterations})
            {/if}
            ({$processingState.progress}/{$processingState.totalSteps})
            {#if pendingRuns > 0}
              <span class="queued-runs">+{pendingRuns} queued</span>
            {/if}
          {:else}
            {#if processingClicks > 0}
              Process again (×{processingClicks + 1})
            {:else}
              Process this text
            {/if}
          {/if}
        </button>
      </div>
      {#if $processingState.error}
        <span class="error-message">{$processingState.error}</span>
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

<!-- Add a progress bar if processing -->
{#if showAutoProcessNotification && !$processingState.isProcessing}
  <div class="auto-process-notification">
    <div class="notification-text">{autoProcessNotificationMessage}</div>
  </div>
{/if}

{#if $processingState.isProcessing && $processingState.totalSteps > 0}
  <div class="processing-status">
    <div class="progress-container">
      <div class="progress-bar" style="width: {($processingState.progress / $processingState.totalSteps) * 100}%"></div>
    </div>
    <div class="progress-text">
      {#if $processingState.totalIterations > 1}
        <div class="iteration-indicator">
          Run {$processingState.currentIteration} of {$processingState.totalIterations}
        </div>
      {/if}
      {#if $processingState.currentStep === 'text_extraction'}
        <span>Transcribing content... ({$processingState.progress}/{$processingState.totalSteps})</span>
      {:else if $processingState.currentStep === 'translation'}
        <span>Translating to English... ({$processingState.progress}/{$processingState.totalSteps})</span>
      {:else if $processingState.currentStep === 'wordforms'}
        <span>Extracting vocabulary... ({$processingState.progress}/{$processingState.totalSteps})</span>
      {:else if $processingState.currentStep === 'phrases'}
        <span>Finding useful phrases... ({$processingState.progress}/{$processingState.totalSteps})</span>
      {:else}
        <span>Processing... ({$processingState.progress}/{$processingState.totalSteps})</span>
      {/if}
    </div>
  </div>
{/if}

<style>
  .collapsible-sections {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .actions {
    margin-bottom: 1rem;
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
  
  .process-controls {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  /* Removed iterations control styles */
  
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
  
  .processing-status {
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
    padding: 0.5rem;
    background-color: rgba(76, 173, 83, 0.1);
    border-radius: 4px;
  }
  
  .progress-container {
    width: 100%;
    height: 8px;
    background-color: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
  }
  
  .progress-bar {
    height: 100%;
    background-color: #4CAD53;
    transition: width 0.3s ease;
  }
  
  .progress-text {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: #4CAD53;
  }
  
  .iteration-indicator {
    font-weight: bold;
    margin-bottom: 0.3rem;
    font-size: 0.85rem;
    color: #3c8c41;
    background-color: rgba(76, 173, 83, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    display: inline-block;
  }
  
  .queued-runs {
    margin-left: 0.5rem;
    font-size: 0.85rem;
    font-weight: bold;
    color: #fff;
    background-color: #3c8c41;
    padding: 2px 6px;
    border-radius: 4px;
    display: inline-block;
  }
  
  .auto-process-notification {
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.5rem;
    background-color: rgba(76, 173, 83, 0.1);
    border-radius: 4px;
    border-left: 3px solid #4CAD53;
    animation: fadeIn 0.5s ease-in-out;
  }
  
  .notification-text {
    color: #4CAD53;
    font-size: 0.9rem;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
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
    
    .process-controls {
      width: 100%;
    }
    
    .iterations-control {
      margin-bottom: 0.3rem;
    }
    
    .button {
      width: 100%;
      justify-content: center;
    }
  }
</style>