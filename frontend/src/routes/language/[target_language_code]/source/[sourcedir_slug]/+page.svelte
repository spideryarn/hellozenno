<script lang="ts">
  import type { PageData } from './$types';
  import { getApiUrl, apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { Trash, ArrowUp, Plus } from 'phosphor-svelte';
  import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
  import { onMount } from 'svelte';
  import { DescriptionFormatted, SourcedirHeader } from '$lib';
  import { page } from '$app/stores';
  
  let { data }: { data: PageData } = $props();
  
  // Define login URL with redirect back to current page using $derived
  const loginUrl = $derived(`/auth?next=${encodeURIComponent($page.url.pathname + $page.url.search)}`);
  
  // Helper function to create headers with auth token
  // TODO: Consider merging this with apiFetch functionality since apiFetch already handles auth headers
  // and provides a more consistent interface for API calls
  async function createAuthHeaders(contentType = 'application/json') {
    const headers = new Headers();
    
    if (contentType) {
      headers.set('Content-Type', contentType);
    }
    
    headers.set('Accept', 'application/json');
    
    // Get the Supabase client from the page data
    if (data.supabase) {
      try {
        const { data: sessionData } = await data.supabase.auth.getSession();
        const session = sessionData.session;
        if (session?.access_token) {
          headers.set('Authorization', `Bearer ${session.access_token}`);
        }
      } catch (sessionError) {
        console.warn('Error getting session:', sessionError);
        // Continue without auth token
      }
    }
    
    return headers;
  }
  
  // Initialize tooltips when the component is mounted
  onMount(() => {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => {
      try {
        // @ts-ignore - Bootstrap global isn't recognized by TypeScript
        return new bootstrap.Tooltip(tooltipTriggerEl, {
          trigger: 'hover focus',
          html: true
        });
      } catch (e) {
        console.error('Error initializing tooltip:', e);
        return null;
      }
    });
  });
  
  // Custom action to focus an element when mounted
  function focusOnMount(node: HTMLElement) {
    // Focus the element after a small delay to ensure DOM is ready
    setTimeout(() => {
      node.focus();
    }, 100);
    
    return {}; // Action must return an object
  }
  
  const { sourcedir, sourcefiles, target_language_code, language_name, has_vocabulary, supported_languages } = data;
  
  let showCreateTextModal = $state(false);
  let showYoutubeModal = $state(false);
  let textTitle = $state('');
  let textContent = $state('');
  let textDescription = $state('');
  let youtubeUrl = $state('');
  let uploadProgress = $state(false);
  let uploadProgressValue = $state(0);
  let isCreatingText = $state(false);
  let isDownloadingYoutube = $state(false);
  let isRenamingDir = $state(false);
  
  // New state for URL Upload Modal
  let isUrlModalOpen = $state(false);
  let urlToUpload = $state('');
  let isUrlLoading = $state(false);
  let urlErrorMessage = $state('');
  let urlSuccessMessage = $state('');
  
  async function deleteSourcefile(slug: string) {
    if (!confirm('Are you sure you want to delete this sourcefile? This action cannot be undone.')) {
      return;
    }
    
    try {
      // Get headers with auth token
      const headers = await createAuthHeaders();
      
      const response = await fetch(
        getApiUrl(RouteName.SOURCEFILE_API_DELETE_SOURCEFILE_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug,
          sourcefile_slug: slug
        }),
        {
          method: 'DELETE',
          headers: headers
        }
      );
      
      if (response.ok) {
        // Reload the page to show the updated list
        window.location.reload();
      } else {
        throw new Error('Failed to delete sourcefile');
      }
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  async function handleLanguageChange(event: Event) {
    const newLanguage = (event.target as HTMLSelectElement).value;
    
    try {
      // Get headers with auth token
      const headers = await createAuthHeaders('application/json');
      
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'PUT',
          headers: headers,
          body: JSON.stringify({ target_language_code: newLanguage })
        }
      );
      
      if (response.ok) {
        window.location.href = `/language/${newLanguage}/source/${sourcedir.slug}`;
      } else {
        throw new Error('Failed to update language');
      }
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  // File Upload Functions
  function handleFileSelect(event: Event) {
    const inputElement = event.target as HTMLInputElement;
    
    if (inputElement.files && inputElement.files.length > 0) {
      uploadFiles(inputElement.files);
    }
  }
  
  async function uploadFiles(files: FileList) {
    uploadProgress = true;
    uploadProgressValue = 0;
    
    // Track successful uploads count
    let successCount = 0;
    let errorCount = 0;
    const totalFiles = files.length;
    
    try {
      // Process files sequentially to avoid payload size limits
      // This maintains the ability for users to select multiple files at once
      // while uploading them one by one to avoid Vercel's 4.5MB payload limit
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Update progress for each file
        uploadProgressValue = Math.round((i / totalFiles) * 100);
        
        try {
          // Create a new FormData for each file
          const formData = new FormData();
          formData.append('files[]', file);
          
          // Get headers with auth token
          const headers = await createAuthHeaders('application/json');
          headers.delete('Content-Type'); // Let the browser set the content type for FormData
          headers.set('Accept', 'application/json');
          
          const response = await fetch(
            getApiUrl(RouteName.SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API, {
              target_language_code: target_language_code,
              sourcedir_slug: sourcedir.slug
            }),
            {
              method: 'POST',
              body: formData,
              headers: headers
            }
          );
          
          // Parse the response JSON
          const responseData = await response.json().catch(() => ({}));
          
          if (response.ok) {
            successCount++;
          } else {
            errorCount++;
            console.error(`Error uploading ${file.name}: ${responseData.error || response.statusText}`);
          }
        } catch (fileError) {
          errorCount++;
          console.error(`Error uploading ${file.name}:`, fileError);
        }
      }
      
      // Final progress update
      uploadProgressValue = 100;
      
      // Report results and reload if any files were uploaded successfully
      if (successCount > 0) {
        if (errorCount > 0) {
          alert(`Uploaded ${successCount} file(s) successfully. ${errorCount} file(s) failed.`);
        }
        // Successful upload - reload the page to show newly uploaded files
        window.location.reload();
      } else {
        // All files failed
        throw new Error(`Failed to upload any files. Please try again with smaller files.`);
      }
    } catch (error) {
      // Only show alerts for errors since they're important
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error("Upload error:", errorMessage);
      alert(`Error: ${errorMessage}`);
    } finally {
      uploadProgress = false;
    }
  }
  
  // Create from Text Modal Functions
  function openCreateTextModal() {
    showCreateTextModal = true;
    textTitle = '';
    textContent = '';
    textDescription = '';
  }
  
  function closeCreateTextModal() {
    showCreateTextModal = false;
  }
  
  async function submitCreateText() {
    if (!textTitle.trim() || !textContent.trim() || isCreatingText) {
      return; // Validation should prevent this, but double-check
    }
    
    isCreatingText = true;
    
    try {
      // Get headers with auth token
      const headers = await createAuthHeaders('application/json');
      
      const response = await fetch(
        getApiUrl(RouteName.SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({
            title: textTitle.trim(),
            text_target: textContent.trim(),
            description: textDescription.trim() || null
          })
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to create text file');
      }
      
      const data = await response.json();
      window.location.href = `/language/${target_language_code}/source/${sourcedir.slug}/${data.slug}`;
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
      isCreatingText = false; // Reset only on error, since on success we navigate away
    }
  }
  
  // YouTube Modal Functions
  function openYoutubeModal() {
    showYoutubeModal = true;
    youtubeUrl = '';
  }
  
  function closeYoutubeModal() {
    showYoutubeModal = false;
  }
  
  async function downloadYoutube() {
    if (!youtubeUrl.trim() || isDownloadingYoutube) {
      return;
    }
    
    isDownloadingYoutube = true;
    
    try {
      // Get headers with auth token
      const headers = await createAuthHeaders('application/json');
      
      const response = await fetch(
        getApiUrl(RouteName.SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'POST',
          headers: headers,
          body: JSON.stringify({ youtube_url: youtubeUrl.trim() })
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to download YouTube audio');
      }
      
      const data = await response.json();
      window.location.href = `/language/${target_language_code}/source/${sourcedir.slug}/${data.slug}`;
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
      isDownloadingYoutube = false; // Reset only on error, since on success we navigate away
    }
  }
  
  // URL Upload Modal Function
  async function handleSubmitUrlUpload() {
    urlErrorMessage = '';
    urlSuccessMessage = '';

    if (!$page.data.session) {
      urlErrorMessage = 'Please log in to upload from a URL.';
      return;
    }
    
    if (!urlToUpload.trim()) {
      urlErrorMessage = 'Please enter a valid URL.';
      return;
    }
    
    // Basic URL format check (doesn't guarantee validity but catches obvious errors)
    try {
      new URL(urlToUpload);
    } catch (_) {
      urlErrorMessage = 'Invalid URL format.';
      return;
    }

    isUrlLoading = true;

    try {
      const result = await apiFetch({
        routeName: RouteName.SOURCEFILE_API_CREATE_SOURCEFILE_FROM_URL_API,
        params: {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        },
        options: {
          method: 'POST',
          body: JSON.stringify({ url: urlToUpload }),
          headers: {
            'Content-Type': 'application/json'
          }
        },
        supabaseClient: data.supabase,
      }) as {
        message: string;
        filename: string;
        slug: string;
      };

      urlSuccessMessage = `Successfully created: ${result.filename}`;
      urlToUpload = '';
      setTimeout(() => {
        isUrlModalOpen = false;
        window.location.reload();
      }, 1500);

    } catch (error: any) {
      console.error('URL Upload Error:', error);
      urlErrorMessage = error?.body?.error || error?.message || 'An unexpected error occurred.';
    } finally {
      isUrlLoading = false;
    }
  }
</script>

<svelte:head>
  <title>{sourcedir.path} | {language_name}</title>
</svelte:head>

<div class="container">
  <nav aria-label="breadcrumb" class="my-3">
    <ol class="breadcrumb">
      <li class="breadcrumb-item"><a href="/">Home</a></li>
      <li class="breadcrumb-item"><a href="/languages">Languages</a></li>
      <li class="breadcrumb-item"><a href="/language/{target_language_code}/sources">{language_name}</a></li>
      <li class="breadcrumb-item active" aria-current="page">{sourcedir.path}</li>
    </ol>
  </nav>

  <!-- Use the new SourcedirHeader component -->
  <SourcedirHeader {sourcedir} {target_language_code} sourcedir_slug={sourcedir.slug} />

  <!-- Main actions below the header -->
  <div class="d-flex justify-content-between align-items-center my-3">
    <!-- Language Selector (keep as is) -->
    <div class="language-selector">
      <label for="language-select" class="me-2">Language:</label>
      <select id="language-select" class="form-select form-select-sm d-inline-block w-auto" 
              value={target_language_code} onchange={handleLanguageChange}>
        {#each supported_languages as lang}
          <option value={lang.code} selected={lang.code === target_language_code}>
            {lang.name}
          </option>
        {/each}
      </select>
    </div>
    
    <!-- Up & Practice Buttons (keep as is) -->
    <div class="d-flex gap-2">
      <a href="/language/{target_language_code}/sources" 
          class="btn btn-outline-secondary"
          title="Back to Sources">
        <ArrowUp size={16} weight="bold" class="me-1" /> Up
      </a>
      <a href="/language/{target_language_code}/flashcards?sourcedir={sourcedir.slug}" 
          class="btn btn-primary {!has_vocabulary ? 'disabled' : ''}"
          title={!has_vocabulary ? 'No vocabulary found' : ''}>
        Practice with Flashcards
      </a>
      
      <!-- Add Files Dropdown -->
      {#if data.session}
        <div class="btn-group">
          <button type="button" class="btn btn-success dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" title="Add Files">
            <Plus size={16} weight="bold" />
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><button class="dropdown-item" type="button" onclick={() => document.getElementById('fileInput')?.click()}>Upload Image Files</button></li>
            <li><button class="dropdown-item" type="button" onclick={() => document.getElementById('audioInput')?.click()}>Upload Audio Files</button></li>
            <li><button class="dropdown-item" type="button" onclick={() => document.getElementById('textInput')?.click()} 
                        data-bs-toggle="tooltip" data-bs-placement="left" data-bs-html="true" 
                        title="<strong>Format:</strong><br>For files with descriptions, use:<br><code>Description text<br>----<br>Main content</code>">Upload Text Files</button></li>
            <li><hr class="dropdown-divider"></li>
            <li><button class="dropdown-item" type="button" onclick={openCreateTextModal}>Create From Text</button></li>
            <li><button class="dropdown-item" type="button" onclick={() => isUrlModalOpen = true}>Upload from URL</button></li>
            <!-- Uncomment if YouTube upload is desired -->
            <!-- <li><button class="dropdown-item" type="button" onclick={openYoutubeModal}>Upload YouTube Video</button></li> -->
          </ul>
        </div>
      {/if}
    </div>
  </div>

  <!-- Files list -->
  <h2 class="mb-3">Source Files</h2>
  
  {#if sourcefiles.length === 0}
    <div class="alert alert-info">No files in this directory.</div>
  {:else}
    <div class="list-group">
      {#each sourcefiles as file}
        <div class="list-group-item d-flex align-items-center">
          <div class="file-icon me-3">
            {#if file.sourcefile_type === 'text'}
              <i class="bi bi-file-text fs-4"></i>
            {:else if file.sourcefile_type === 'audio'}
              <i class="bi bi-file-music fs-4"></i>
            {:else if file.sourcefile_type === 'image'}
              <i class="bi bi-file-image fs-4"></i>
            {:else if file.sourcefile_type === 'youtube_audio'}
              <i class="bi bi-youtube fs-4"></i>
            {:else}
              <i class="bi bi-file fs-4"></i>
            {/if}
          </div>
          
          <div class="flex-grow-1">
            <a href="/language/{target_language_code}/source/{sourcedir.slug}/{file.slug}" class="text-decoration-none fs-5">
              {file.filename}
            </a>
            <div class="d-flex mt-1 flex-wrap">
              {#if file.metadata.has_audio}
                <span class="badge bg-primary me-2"><i class="bi bi-volume-up me-1"></i> Audio</span>
              {/if}
              {#if file.metadata.wordform_count > 0}
                <span class="badge bg-success me-2"><i class="bi bi-book me-1"></i> Words: {file.metadata.wordform_count}</span>
              {/if}
              {#if file.metadata.phrase_count > 0}
                <span class="badge bg-warning text-dark me-2"><i class="bi bi-chat-quote me-1"></i> Phrases: {file.metadata.phrase_count}</span>
              {/if}
              {#if file.metadata.duration}
                <span class="badge bg-secondary me-2">
                  <i class="bi bi-clock me-1"></i>
                  {Math.floor(file.metadata.duration / 60)}:{(file.metadata.duration % 60).toString().padStart(2, '0')}
                </span>
              {/if}
            </div>
          </div>
          
          <button class="btn btn-sm btn-outline-danger" 
                  onclick={() => deleteSourcefile(file.slug)}
                  title="Delete this file"
                  aria-label="Delete file {file.filename}">
            <Trash size={16} weight="bold" />
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Hidden File Inputs (needed for upload buttons in dropdown) -->
<input type="file" id="fileInput" class="d-none" multiple accept="image/*" onchange={handleFileSelect}>
<input type="file" id="audioInput" class="d-none" multiple accept=".mp3" onchange={handleFileSelect}>
<input type="file" id="textInput" class="d-none" multiple accept=".txt,.md" onchange={handleFileSelect}>

<!-- Create from Text Modal -->
{#if showCreateTextModal}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog">
      <div class="modal-content" 
           role="dialog"
           aria-labelledby="create-text-modal-title"
           tabindex="-1"
           onkeydown={(e) => {
             e.stopPropagation(); // Explicitly stop propagation
             if (e.key === 'Escape') closeCreateTextModal();
             if (e.key === 'Enter' && e.ctrlKey && textTitle.trim() && textContent.trim() && !isCreatingText) submitCreateText();
           }}>
        <div class="modal-header">
          <h5 class="modal-title" id="create-text-modal-title">Create Sourcefile from Text</h5>
          <button type="button" class="btn-close" aria-label="Close" onclick={closeCreateTextModal}></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="textTitle" class="form-label">Title (will be used as the actual filename):</label>
            <input type="text" class="form-control" id="textTitle" bind:value={textTitle} 
                   placeholder="Enter title for the text" autocomplete="off"
                   use:focusOnMount>
          </div>
          <div class="mb-3">
            <label for="textDescription" class="form-label">Description (optional):</label>
            <textarea class="form-control" id="textDescription" rows="3" bind:value={textDescription} 
                      placeholder="Enter an optional description for this text"></textarea>
          </div>
          <div class="mb-3">
            <label for="textContent" class="form-label">Text Content:</label>
            <textarea class="form-control" id="textContent" rows="10" bind:value={textContent} 
                      placeholder="Enter or paste your text here"></textarea>
          </div>
          <div class="text-muted small">
            <p class="mb-1">Keyboard shortcuts:</p>
            <ul class="mb-0">
              <li>ESC to cancel</li>
              <li>CTRL+ENTER to create</li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" onclick={closeCreateTextModal} disabled={isCreatingText}>
            Cancel
          </button>
          <button type="button" class="btn btn-success" 
                  onclick={submitCreateText} 
                  disabled={!textTitle.trim() || !textContent.trim() || isCreatingText}
                  title={!textTitle.trim() || !textContent.trim() ? "Please fill in both title and text content" : ""}>
            {#if isCreatingText}
              <span class="me-2"><LoadingSpinner /></span>
              Creating...
            {:else}
              Create
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- YouTube URL Modal -->
{#if showYoutubeModal}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog">
      <div class="modal-content"
           role="dialog"
           aria-labelledby="youtube-modal-title"
           tabindex="-1"
           onkeydown={(e) => {
             e.stopPropagation(); // Explicitly stop propagation
             if (e.key === 'Escape') closeYoutubeModal();
             if (e.key === 'Enter' && youtubeUrl.trim() && !isDownloadingYoutube) downloadYoutube();
           }}>
        <div class="modal-header">
          <h5 class="modal-title" id="youtube-modal-title">Download YouTube Audio</h5>
          <button type="button" class="btn-close" aria-label="Close" onclick={closeYoutubeModal}></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="youtubeUrl" class="form-label">YouTube URL:</label>
            <input type="text" class="form-control" id="youtubeUrl" bind:value={youtubeUrl} 
                   placeholder="Enter YouTube URL" autocomplete="off" 
                   use:focusOnMount>
            <div class="form-text">
              Supports full YouTube URLs, short URLs (youtu.be), and mobile URLs (m.youtube.com).<br>
              Maximum audio length: 60 minutes
            </div>
          </div>
          <div class="text-muted small">
            <p class="mb-1">Keyboard shortcuts:</p>
            <ul class="mb-0">
              <li>ESC to cancel</li>
              <li>ENTER to download</li>
            </ul>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" onclick={closeYoutubeModal} disabled={isDownloadingYoutube}>
            Cancel
          </button>
          <button type="button" class="btn btn-primary" 
                  onclick={downloadYoutube} 
                  disabled={!youtubeUrl.trim() || isDownloadingYoutube}
                  title={!youtubeUrl.trim() ? "Please enter a YouTube URL" : ""}>
            {#if isDownloadingYoutube}
              <span class="me-2"><LoadingSpinner /></span>
              Downloading...
            {:else}
              Download Audio
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- URL Upload Modal -->
{#if isUrlModalOpen}
<div class="modal fade show" style="display: block;" tabindex="-1" role="dialog" aria-labelledby="urlUploadModalLabel" aria-modal="true">
  <div class="modal-dialog modal-dialog-centered" role="document">
    <div class="modal-content"
         role="dialog" 
         aria-labelledby="urlUploadModalLabel" 
         tabindex="-1"
         onkeydown={(e) => {
           e.stopPropagation(); // Explicitly stop propagation
           if (e.key === 'Escape') {
             isUrlModalOpen = false;
           }
           if (e.key === 'Enter' && urlToUpload.trim() && !isUrlLoading) {
             handleSubmitUrlUpload();
           }
         }}>
      <div class="modal-header">
        <h5 class="modal-title" id="urlUploadModalLabel">Upload from URL</h5>
        <button type="button" class="btn-close" aria-label="Close" onclick={() => isUrlModalOpen = false}></button>
      </div>
      <div class="modal-body">
        {#if urlSuccessMessage}
          <div class="alert alert-success" role="alert">{urlSuccessMessage}</div>
        {/if}
        {#if urlErrorMessage}
          <div class="alert alert-danger" role="alert">{urlErrorMessage}</div>
        {/if}
        
        <div class="mb-3">
          <label for="urlInput" class="form-label">Enter URL:</label>
          <input type="url" class="form-control" id="urlInput" bind:value={urlToUpload} placeholder="https://example.com/article" required use:focusOnMount>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" onclick={() => isUrlModalOpen = false}>Cancel</button>
        <button type="button" class="btn btn-primary" onclick={handleSubmitUrlUpload} disabled={isUrlLoading || !urlToUpload}>
          {#if isUrlLoading}
            <LoadingSpinner style="width: 16px; height: 16px; color: #fff; margin-right: 0.25rem; vertical-align: text-bottom;" /> Uploading...
          {:else}
            Upload
          {/if}
        </button>
      </div>
    </div>
  </div>
</div>
<!-- Backdrop for Modal -->
<div class="modal-backdrop fade show"></div>
{/if} 