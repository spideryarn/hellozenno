<script lang="ts">
  import type { PageData } from './$types';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { Spinner, Trash, ArrowUp } from 'phosphor-svelte';
  import { onMount } from 'svelte';
  import { DescriptionFormatted } from '$lib';
  import { user } from '$lib/stores/authStore';
  import { page } from '$app/stores';
  
  export let data: PageData;
  
  // Define login URL with redirect back to current page
  $: loginUrl = `/auth?next=${encodeURIComponent($page.url.pathname + $page.url.search)}`;
  
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
  
  let showCreateTextModal = false;
  let showYoutubeModal = false;
  let textTitle = '';
  let textContent = '';
  let textDescription = '';
  let youtubeUrl = '';
  let uploadProgress = false;
  let uploadProgressValue = 0;
  let isCreatingText = false;
  let isDownloadingYoutube = false;
  let isRenamingDir = false;
  
  async function renameSourcedir() {
    if (isRenamingDir) return;
    
    try {
      const newName = prompt('Enter new directory name:', sourcedir.path);
      if (!newName || newName === sourcedir.path) return;
      
      isRenamingDir = true;
      
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_RENAME_SOURCEDIR_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ new_name: newName })
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to rename directory');
      }
      
      const data = await response.json();
      // Redirect to the new URL with the new slug
      window.location.href = `/language/${target_language_code}/source/${data.slug}`;
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
      isRenamingDir = false;
    }
  }
  
  async function deleteSourcedir() {
    if (!confirm('Are you sure you want to delete this directory? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_DELETE_SOURCEDIR_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'DELETE',
        }
      );
      
      if (response.ok) {
        window.location.href = `/language/${target_language_code}/sources`;
      } else {
        const data = await response.json();
        throw new Error(data.error || 'Failed to delete directory. If the directory contains files, you must delete all files first.');
      }
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  async function deleteSourcefile(slug: string) {
    if (!confirm('Are you sure you want to delete this sourcefile? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(
        getApiUrl(RouteName.SOURCEFILE_API_DELETE_SOURCEFILE_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug,
          sourcefile_slug: slug
        }),
        {
          method: 'DELETE',
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
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
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
    
    try {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files[]', files[i]);
      }
      
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'POST',
          body: formData,
          headers: {
            'Accept': 'application/json'
          }
        }
      );
      
      // Parse the response JSON
      const data = await response.json().catch(() => ({}));
      
      if (response.ok) {
        // Successful upload - just reload the page
        // The newly uploaded files will appear in the list
        window.location.reload();
      } else {
        // Show error message
        throw new Error(data.error || `Upload failed with status: ${response.status}`);
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
      const response = await fetch(
        getApiUrl(RouteName.SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
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
      const response = await fetch(
        getApiUrl(RouteName.SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API, {
          target_language_code: target_language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
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

  <div class="card mb-4">
    <div class="card-body">
      <h1 class="card-title">{sourcedir.path}</h1>
      
      <!-- Description section -->
      <DescriptionFormatted 
        description={sourcedir.description} 
        placeholder="No description available for this directory"
        onSave={async (text) => {
          try {
            const response = await fetch(
              getApiUrl(RouteName.SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API, {
                target_language_code: target_language_code,
                sourcedir_slug: sourcedir.slug
              }),
              {
                method: 'PUT',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ description: text })
              }
            );
            
            if (!response.ok) {
              throw new Error('Failed to update description');
            }
            
            // Update local state
            sourcedir.description = text;
          } catch (error) {
            alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
            throw error; // Propagate error to component
          }
        }}
      />
      
      <!-- Top controls -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="language-selector">
          <label for="language-select" class="me-2">Language:</label>
          <select id="language-select" class="form-select form-select-sm d-inline-block w-auto" 
                  value={target_language_code} on:change={handleLanguageChange}>
            {#each supported_languages as lang}
              <option value={lang.code} selected={lang.code === target_language_code}>
                {lang.name}
              </option>
            {/each}
          </select>
        </div>
        
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
        </div>
      </div>
      
      <!-- Directory actions -->
      <div class="btn-group mb-4">
        <button class="btn btn-outline-secondary" on:click={renameSourcedir}>
          Rename Directory
        </button>
        <button class="btn btn-outline-danger" on:click={deleteSourcedir}>
          <Trash size={16} weight="bold" class="me-1" /> Delete Directory
        </button>
      </div>
      
      <!-- File upload section -->
      <div class="card mb-4">
        <div class="card-header">Add Files</div>
        <div class="card-body">
          {#if $user}
            <div class="row mb-3">
              <div class="col">
                <label for="fileInput" class="btn btn-outline-primary me-2">Upload Image Files</label>
                <input type="file" id="fileInput" class="d-none" multiple accept="image/*" on:change={handleFileSelect}>
                
                <label for="audioInput" class="btn btn-outline-primary me-2">Upload Audio Files</label>
                <input type="file" id="audioInput" class="d-none" multiple accept=".mp3" on:change={handleFileSelect}>
                
                <div class="d-inline-block position-relative me-2">
                  <label for="textInput" class="btn btn-outline-primary" 
                         data-bs-toggle="tooltip" 
                         data-bs-html="true"
                         title="<strong>Format:</strong><br>For files with descriptions, use:<br><code>Description text<br>----<br>Main content</code>">
                    Upload Text Files
                  </label>
                  <input type="file" id="textInput" class="d-none" multiple accept=".txt,.md" on:change={handleFileSelect}>
                </div>
                
                <button class="btn btn-outline-primary me-2" on:click={() => showCreateTextModal = true}>Create From Text</button>
                <!-- Leave this commented. We've disabled it for now, but might want to try it again in the future. -->
                <!-- <button class="btn btn-outline-primary" on:click={() => showYoutubeModal = true}>Upload YouTube Video</button> -->
              </div>
            </div>
            
            <!-- Mobile-specific options would go here -->
            
            {#if uploadProgress}
              <div class="progress mb-3">
                <div class="progress-bar bg-success" 
                     role="progressbar" 
                     style="width: {uploadProgressValue}%" 
                     aria-valuenow={uploadProgressValue} 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                  {uploadProgressValue}%
                </div>
              </div>
            {/if}
          {:else}
            <!-- Use standard Bootstrap alert -->
            <div class="alert alert-info" role="alert">
              Please <a href={loginUrl}>login</a> to upload files or create text sources.
            </div>
          {/if}
        </div>
      </div>
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
                  on:click={() => deleteSourcefile(file.slug)}
                  title="Delete this file"
                  aria-label="Delete file {file.filename}">
            <Trash size={16} weight="bold" />
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Create from Text Modal -->
{#if showCreateTextModal}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog">
      <div class="modal-content" 
           role="dialog"
           aria-labelledby="create-text-modal-title"
           tabindex="-1"
           on:keydown|stopPropagation={(e) => {
             if (e.key === 'Escape') closeCreateTextModal();
             if (e.key === 'Enter' && e.ctrlKey && textTitle.trim() && textContent.trim() && !isCreatingText) submitCreateText();
           }}>
        <div class="modal-header">
          <h5 class="modal-title" id="create-text-modal-title">Create Sourcefile from Text</h5>
          <button type="button" class="btn-close" aria-label="Close" on:click={closeCreateTextModal}></button>
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
          <button type="button" class="btn btn-outline-secondary" on:click={closeCreateTextModal} disabled={isCreatingText}>
            Cancel
          </button>
          <button type="button" class="btn btn-success" 
                  on:click={submitCreateText} 
                  disabled={!textTitle.trim() || !textContent.trim() || isCreatingText}
                  title={!textTitle.trim() || !textContent.trim() ? "Please fill in both title and text content" : ""}>
            {#if isCreatingText}
              <span class="me-2"><Spinner size={16} weight="bold" /></span>
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
           on:keydown|stopPropagation={(e) => {
             if (e.key === 'Escape') closeYoutubeModal();
             if (e.key === 'Enter' && youtubeUrl.trim() && !isDownloadingYoutube) downloadYoutube();
           }}>
        <div class="modal-header">
          <h5 class="modal-title" id="youtube-modal-title">Download YouTube Audio</h5>
          <button type="button" class="btn-close" aria-label="Close" on:click={closeYoutubeModal}></button>
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
          <button type="button" class="btn btn-outline-secondary" on:click={closeYoutubeModal} disabled={isDownloadingYoutube}>
            Cancel
          </button>
          <button type="button" class="btn btn-primary" 
                  on:click={downloadYoutube} 
                  disabled={!youtubeUrl.trim() || isDownloadingYoutube}
                  title={!youtubeUrl.trim() ? "Please enter a YouTube URL" : ""}>
            {#if isDownloadingYoutube}
              <span class="me-2"><Spinner size={16} weight="bold" /></span>
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