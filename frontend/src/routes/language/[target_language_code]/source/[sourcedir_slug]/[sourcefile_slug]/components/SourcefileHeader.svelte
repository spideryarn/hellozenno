<script lang="ts">
  import type { Sourcefile, Sourcedir, Metadata, Navigation, Stats } from '$lib/types/sourcefile';
  import { getApiUrl, apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { 
    CollapsibleHeader, 
    MetadataSection, 
    DescriptionSection, 
    FileOperationsSection 
  } from '$lib';
  import Info from 'phosphor-svelte/lib/Info';
  import { goto } from '$app/navigation';
  import { getPageUrl } from '$lib/navigation';
  import { onMount } from 'svelte';
  import Trash from 'phosphor-svelte/lib/Trash';
  import Image from 'phosphor-svelte/lib/Image';
  import Download from 'phosphor-svelte/lib/Download';
  import FileText from 'phosphor-svelte/lib/FileText';
  import SpeakerHigh from 'phosphor-svelte/lib/SpeakerHigh';
  import MusicNotes from 'phosphor-svelte/lib/MusicNotes';
  import PencilSimple from 'phosphor-svelte/lib/PencilSimple';
  import FolderOpen from 'phosphor-svelte/lib/FolderOpen';
  import SourcefileNavButtons from './SourcefileNavButtons.svelte';
  import { SourcefileProcessingQueue, processingState } from '$lib/processing-queue';
  import { page } from '$app/stores';
  import type { SupabaseClient } from '@supabase/supabase-js';
  
  export let sourcefile: Sourcefile;
  export const sourcedir: Sourcedir = undefined as unknown as Sourcedir;
  export let metadata: Metadata;
  export let navigation: Navigation;
  export const stats: Stats = undefined as unknown as Stats;
  export let target_language_code: string;
  export let sourcedir_slug: string;
  export let sourcefile_slug: string;
  export let available_sourcedirs: any[] = [];
  export let data: {
    supabase?: SupabaseClient;
    session?: any;
    user?: any;
    [key: string]: any;
  }; // Add data prop to receive layout data including supabase client
  
  // Variables for sourcedir dropdown
  let moveError = '';
  
  // Collapsible header state - default to collapsed
  let isHeaderExpanded = false;
  
  // Auto-processing settings
  let autoProcessEnabled = true; // Default to enabled, could be user-configurable
  let showAutoProcessNotification = false;
  let autoProcessNotificationMessage = '';
  
  // Multi-processing counter and queue system
  let processingClicks = 0; // Tracks total clicks for UI text
  let pendingRuns = 0; // Tracks how many times the button was clicked while processing
  
  // Progress detail display state
  let showDetailedProgress = false;
  
  // Success notification
  let showSuccessNotification = false;
  let successMessage = '';
  let successNotificationTimeout: ReturnType<typeof setTimeout> | null = null;
  
  // Initialize the processing queue when the component mounts
  let processingQueue: SourcefileProcessingQueue;
  onMount(() => {
    // Make sure sourcefile and its type are available and NOT youtube_audio
    if (sourcefile && sourcefile.sourcefile_type && sourcefile.sourcefile_type !== 'youtube_audio') {
      // Get supabase client from the client-side data
      const supabaseClient = data.supabase;
      
      processingQueue = new SourcefileProcessingQueue(
        supabaseClient ?? null, // Pass null if undefined
        target_language_code,
        sourcedir_slug,
        sourcefile_slug,
        sourcefile.sourcefile_type as 'text' | 'image' | 'audio' // Type assertion after check
      );
    } else {
      console.error("Sourcefile data missing, or type is 'youtube_audio', cannot initialize processing queue.");
      // Optionally disable the process button or show an error
    }
  });
  
  // Check if sourcefile needs INITIAL processing - only trigger for files that 
  // haven't been processed at all for a specific step
  function shouldAutoProcess(sourcefile: Sourcefile): boolean {
    console.log('Auto-process check - Sourcefile state:', {
      text_target: !!sourcefile.text_target,
      text_english: !!sourcefile.text_english,
      has_image: sourcefile.has_image,
      has_audio: sourcefile.has_audio,
      wordforms_count: stats?.wordforms_count || 0,
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
    const hasAbsolutelyNoWordforms = hasContent && (stats?.wordforms_count === 0);
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
      
      // Use Supabase client to get auth token
      if (!data.supabase) {
        throw new Error('Authentication required to move files');
      }
      
      // Use apiFetch from imports for proper auth handling
      
      // Use apiFetch instead of raw fetch to ensure proper auth handling
      const result = await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEFILE_API_MOVE_SOURCEFILE_API,
        params: {
          target_language_code,
          sourcedir_slug,
          sourcefile_slug
        },
        options: {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ new_sourcedir_slug: newSourcedirSlug })
        }
      });
      
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
  
  // Function to dispatch event after processing is complete
  const dispatchProcessingComplete = (detail: any) => {
    // Use a custom event to notify parent components about the updated data
    const event = new CustomEvent('processingComplete', {
      detail,
      bubbles: true, // Allow event to bubble up the DOM tree
    });
    
    // Also update the stats object if available in the processed data
    if (detail && detail.stats && stats) {
      // Update local stats to refresh the tabs
      stats.wordforms_count = detail.stats.wordforms_count;
      stats.phrases_count = detail.stats.phrases_count;
    }
    
    // Dispatch the event from this component
    if (typeof document !== 'undefined') {
      document.dispatchEvent(event);
    }
  };

  async function processSourcefile() {
    if (!processingQueue) {
      console.error("Processing queue not initialized.");
      alert("Error: Processing cannot start. Please refresh the page.");
      return;
    }
    
    try {
      // Hide auto-process notification if showing
      showAutoProcessNotification = false;
      
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
        // The processAll method now handles initialization internally
        await processingQueue.processAll(iterations);
        
        // Check if we have processed data
        if ($processingState.processedSourcefileData && !$processingState.error) {
          // Dispatch the event with the updated data
          dispatchProcessingComplete($processingState.processedSourcefileData);
          
          // Show success notification briefly (only for the last batch)
          if (pendingRuns === 0) {
            // Clear any existing timeout
            if (successNotificationTimeout) {
              clearTimeout(successNotificationTimeout);
            }
            
            // Set success notification
            successMessage = `Successfully processed text ${iterations} time${iterations !== 1 ? 's' : ''}.`;
            showSuccessNotification = true;
            
            // Auto-hide after 5 seconds
            successNotificationTimeout = setTimeout(() => {
              showSuccessNotification = false;
            }, 5000);
          }
        } else {
          // Handle cases where processing finished but might have had errors
          // or failed to return data (check $processingState.error)
          console.log("Processing finished, but no data returned or error occurred. State:", $processingState);
          if (!$processingState.error) {
             // If no specific error, maybe just skip reload or show generic message?
             // alert('Processing finished, but failed to retrieve updated data.'); 
          }
          // No reload here, rely on error message in processing state
          // window.location.reload(); 
          // return; 
        }
        
        // If more requests came in while we were processing, handle them in the next iteration
      }
    } catch (error) {
      console.error('Error processing file:', error);
      processingState.update(state => ({ 
        ...state, 
        error: error instanceof Error ? error.message : 'Unknown error processing file',
        isProcessing: false
      }));
      // Reset pending runs on error to avoid getting stuck
      pendingRuns = 0;
    }
  }
  
  async function deleteSourcefile() {
    if (!confirm(`Are you sure you want to delete "${sourcefile.filename}"? This cannot be undone.`)) {
      return;
    }
    
    try {
      // Use Supabase client to get auth token
      if (!data.supabase) {
        throw new Error('Authentication required to delete files');
      }
      
      // Use apiFetch from imports for proper auth handling
      
      // Use apiFetch instead of raw fetch to ensure proper auth handling
      await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEFILE_API_DELETE_SOURCEFILE_API,
        params: {
          target_language_code,
          sourcedir_slug,
          sourcefile_slug
        },
        options: {
          method: 'DELETE'
        }
      });
      
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
      // Use Supabase client to get auth token
      if (!data.supabase) {
        throw new Error('Authentication required to rename files');
      }
      
      // Use apiFetch from imports for proper auth handling
      
      // Use apiFetch instead of raw fetch to ensure proper auth handling
      const result = await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEFILE_API_RENAME_SOURCEFILE_API,
        params: {
          target_language_code,
          sourcedir_slug,
          sourcefile_slug
        },
        options: {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ new_name: newName })
        }
      });
      
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
      // Use apiFetch from imports for proper auth handling
      
      // Use apiFetch instead of raw fetch to ensure proper auth handling
      await apiFetch({
        supabaseClient: data.supabase,
        routeName: RouteName.SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API,
        params: {
          target_language_code,
          sourcedir_slug,
          sourcefile_slug
        },
        options: {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ description: text })
        }
      });
      
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
    
    <FileOperationsSection
      onRename={renameSourcefile}
      onDelete={deleteSourcefile}
      onMove={moveSourcefile}
      {available_sourcedirs}
    />
    
    <DescriptionSection 
      description={sourcefile.description ?? undefined}
      onSave={saveDescription}
    />
  </div>
</CollapsibleHeader>

<!-- Add a bottom divider when header is expanded -->
{#if isHeaderExpanded}
  <div class="bottom-divider"></div>
{/if}

<div class="actions">
  <!-- Show divider for expanded operations when header is expanded -->
  {#if isHeaderExpanded}
    <div class="expanded-operations-divider">
      <span>Learning Operations</span>
    </div>
  {/if}

  <div class="action-row">
    <div class="section process-section">
      {#if data.session}
        <div class="process-controls">
          <button on:click={processSourcefile} class="button {$processingState.isProcessing ? 'is-processing' : ''}">
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
          <!-- Use {@html} to allow rendered HTML links in error messages -->
          <span class="error-message">{@html $processingState.error}</span>
        {/if}
      {:else}
        <div class="process-controls login-prompt">
          <a href={`/auth?next=${encodeURIComponent($page.url.pathname)}`} class="button is-light">
            Login to Process Text
          </a>
        </div>
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
      <SourcefileNavButtons 
        {navigation}
        {target_language_code}
        {sourcedir_slug}
        view="text"
      />
    </div>
  </div>
</div>

<!-- Notifications area -->
{#if showAutoProcessNotification && !$processingState.isProcessing}
  <div class="auto-process-notification">
    <div class="notification-text">{autoProcessNotificationMessage}</div>
  </div>
{/if}

{#if showSuccessNotification}
  <div class="success-notification">
    <div class="notification-content">
      <span class="success-icon">✓</span>
      <div class="notification-text">{successMessage}</div>
    </div>
    <button class="close-notification" on:click={() => showSuccessNotification = false}>×</button>
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
      {:else if $processingState.currentStep === 'lemma_metadata'}
        <span>{$processingState.description} ({$processingState.progress}/{$processingState.totalSteps})</span>
      {:else}
        <span>{$processingState.description || 'Processing...'} ({$processingState.progress}/{$processingState.totalSteps})</span>
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
  
  .bottom-divider {
    position: relative;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: 1rem;
    margin-top: -0.5rem;
  }

  .expanded-operations-divider {
    position: relative;
    text-align: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: 1rem;
    margin-top: 0.5rem;
  }
  
  .expanded-operations-divider span {
    position: relative;
    top: 0.7em;
    background-color: var(--bs-body-bg, #212529);
    padding: 0 0.75rem;
    font-size: 0.85rem;
    color: #adb5bd;
    text-transform: uppercase;
    letter-spacing: 0.05em;
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
  
  .section-divider {
    height: 24px;
    width: 1px;
    background-color: rgba(255, 255, 255, 0.2);
    margin: 0 0.5rem;
  }
  
  .error-message {
    color: #d9534f;
    font-size: 0.9rem;
    margin-left: 0.5rem;
  }
  
  .button {
    background-color: var(--hz-color-primary-green);
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
  
  .processing-status {
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
    padding: 0.5rem;
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.1);
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
    background-color: var(--hz-color-primary-green);
    transition: width 0.3s ease;
  }
  
  .progress-text {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: var(--hz-color-primary-green);
  }
  
  .iteration-indicator {
    font-weight: bold;
    margin-bottom: 0.3rem;
    font-size: 0.85rem;
    color: var(--hz-color-primary-green-dark);
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    display: inline-block;
  }
  
  .queued-runs {
    margin-left: 0.5rem;
    font-size: 0.85rem;
    font-weight: bold;
    color: #fff;
    background-color: var(--hz-color-primary-green-dark);
    padding: 2px 6px;
    border-radius: 4px;
    display: inline-block;
  }
  
  .auto-process-notification {
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.5rem;
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.1);
    border-radius: 4px;
    border-left: 3px solid var(--hz-color-primary-green);
    animation: fadeIn 0.5s ease-in-out;
  }
  
  .notification-text {
    color: var(--hz-color-primary-green);
    font-size: 0.9rem;
  }
  
  .success-notification {
    margin-top: 0.5rem;
    margin-bottom: 1rem;
    padding: 0.5rem 1rem;
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.1);
    border-radius: 4px;
    border-left: 3px solid var(--hz-color-primary-green);
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: slideDown 0.3s ease-in-out;
  }
  
  .notification-content {
    display: flex;
    align-items: center;
  }
  
  .success-icon {
    color: var(--hz-color-primary-green);
    font-size: 1.2rem;
    font-weight: bold;
    margin-right: 0.5rem;
  }
  
  .close-notification {
    background: none;
    border: none;
    color: #6c757d;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0;
    margin: 0;
  }
  
  .close-notification:hover {
    color: #343a40;
  }
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .processing-status {
    cursor: pointer;
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
    
    .button {
      width: 100%;
      justify-content: center;
    }
    
    .expanded-operations-divider {
      margin-top: 0.25rem;
      margin-bottom: 0.75rem;
    }
    
    .expanded-operations-divider span {
      font-size: 0.8rem;
      padding: 0 0.5rem;
    }
  }
  
  .process-controls.login-prompt a.button.is-light {
    background-color: #f5f5f5;
    color: #363636;
    border: 1px solid #dbdbdb;
  }
  
  .process-controls.login-prompt a.button.is-light:hover {
    background-color: #e8e8e8;
    border-color: #b5b5b5;
  }
  
  .button.is-processing {
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.7);
    position: relative;
    overflow: hidden;
  }
  
  .button.is-processing::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.2),
      transparent
    );
    animation: shimmer 1.5s infinite;
  }
  
  @keyframes shimmer {
    100% {
      left: 100%;
    }
  }
</style>