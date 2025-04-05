<script lang="ts">
  import type { PageData } from './$types';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  
  export let data: PageData;
  
  const { sourcedir, sourcefiles, language_code, language_name, has_vocabulary, supported_languages } = data;
  
  let showCreateTextModal = false;
  let showYoutubeModal = false;
  let textTitle = '';
  let textContent = '';
  let youtubeUrl = '';
  let isEditingDescription = false;
  let editedDescription = sourcedir.description || '';
  let uploadProgress = false;
  let uploadProgressValue = 0;
  
  // API functions
  async function editSourcedirDescription() {
    isEditingDescription = true;
  }
  
  async function saveSourcedirDescription() {
    try {
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API, {
          target_language_code: language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ description: editedDescription.trim() })
        }
      );
      
      if (!response.ok) {
        throw new Error('Failed to update description');
      }
      
      // Update local state
      sourcedir.description = editedDescription.trim();
      isEditingDescription = false;
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  async function renameSourcedir() {
    try {
      const newName = prompt('Enter new directory name:', sourcedir.path);
      if (!newName || newName === sourcedir.path) return;
      
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_RENAME_SOURCEDIR_API, {
          target_language_code: language_code,
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
      window.location.href = `/language/${language_code}/source/${data.slug}`;
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  
  async function deleteSourcedir() {
    if (!confirm('Are you sure you want to delete this directory? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(
        getApiUrl(RouteName.SOURCEDIR_API_DELETE_SOURCEDIR_API, {
          target_language_code: language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'DELETE',
        }
      );
      
      if (response.ok) {
        window.location.href = `/language/${language_code}/sources`;
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
          target_language_code: language_code,
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
          target_language_code: language_code,
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
          target_language_code: language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'POST',
          body: formData
        }
      );
      
      if (response.ok) {
        window.location.reload();
      } else {
        const data = await response.json();
        throw new Error(data.error || 'Upload failed');
      }
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      uploadProgress = false;
    }
  }
  
  // Create from Text Modal Functions
  function openCreateTextModal() {
    showCreateTextModal = true;
    textTitle = '';
    textContent = '';
  }
  
  function closeCreateTextModal() {
    showCreateTextModal = false;
  }
  
  async function submitCreateText() {
    if (!textTitle.trim()) {
      alert('Please enter a title');
      return;
    }
    
    if (!textContent.trim()) {
      alert('Please enter some text');
      return;
    }
    
    try {
      const response = await fetch(
        getApiUrl(RouteName.SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API, {
          target_language_code: language_code,
          sourcedir_slug: sourcedir.slug
        }),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: textTitle.trim(),
            text_target: textContent.trim()
          })
        }
      );
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to create text file');
      }
      
      const data = await response.json();
      window.location.href = `/language/${language_code}/source/${sourcedir.slug}/${data.slug}`;
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
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
    if (!youtubeUrl.trim()) {
      alert('Please enter a YouTube URL');
      return;
    }
    
    try {
      const response = await fetch(
        getApiUrl(RouteName.SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API, {
          target_language_code: language_code,
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
      window.location.href = `/language/${language_code}/source/${sourcedir.slug}/${data.slug}`;
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : String(error)}`);
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
      <li class="breadcrumb-item"><a href="/language/{language_code}/sources">{language_name}</a></li>
      <li class="breadcrumb-item active" aria-current="page">{sourcedir.path}</li>
    </ol>
  </nav>

  <div class="card mb-4">
    <div class="card-body">
      <h1 class="card-title">{sourcedir.path}</h1>
      
      <!-- Description section -->
      <div class="mb-3 p-3 border rounded">
        {#if isEditingDescription}
          <div class="mb-3">
            <textarea 
              class="form-control" 
              rows="3" 
              bind:value={editedDescription} 
              placeholder="Enter description for this directory..."></textarea>
          </div>
          <div class="d-flex justify-content-end">
            <button class="btn btn-outline-secondary me-2" on:click={() => isEditingDescription = false}>Cancel</button>
            <button class="btn btn-success" on:click={saveSourcedirDescription}>Save</button>
          </div>
        {:else}
          <div class="d-flex justify-content-between align-items-start">
            <div>
              {#if sourcedir.description}
                <p class="mb-0">{sourcedir.description}</p>
              {:else}
                <p class="text-muted fst-italic mb-0">No description available</p>
              {/if}
            </div>
            <button class="btn btn-sm btn-outline-secondary" on:click={editSourcedirDescription}>
              <i class="bi bi-pencil"></i> Edit Description
            </button>
          </div>
        {/if}
      </div>
      
      <!-- Top controls -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="language-selector">
          <label for="language-select" class="me-2">Language:</label>
          <select id="language-select" class="form-select form-select-sm d-inline-block w-auto" 
                  value={language_code} on:change={handleLanguageChange}>
            {#each supported_languages as lang}
              <option value={lang.code} selected={lang.code === language_code}>
                {lang.name}
              </option>
            {/each}
          </select>
        </div>
        
        <div>
          <a href="/language/{language_code}/flashcards?sourcedir={sourcedir.slug}" 
             class="btn btn-primary {!has_vocabulary ? 'disabled' : ''}"
             title={!has_vocabulary ? 'No vocabulary found' : ''}>
            Practice with Flashcards
          </a>
        </div>
      </div>
      
      <!-- Directory actions -->
      <div class="btn-group mb-4">
        <button class="btn btn-outline-secondary" on:click={renameSourcedir}>Rename Directory</button>
        <button class="btn btn-outline-danger" on:click={deleteSourcedir}>Delete Directory</button>
      </div>
      
      <!-- File upload section -->
      <div class="card mb-4">
        <div class="card-header">Add Files</div>
        <div class="card-body">
          <div class="row mb-3">
            <div class="col">
              <label for="fileInput" class="btn btn-outline-primary me-2">Upload Image Files</label>
              <input type="file" id="fileInput" class="d-none" multiple accept="image/*" on:change={handleFileSelect}>
              
              <label for="audioInput" class="btn btn-outline-primary me-2">Upload Audio Files</label>
              <input type="file" id="audioInput" class="d-none" multiple accept=".mp3" on:change={handleFileSelect}>
              
              <button class="btn btn-outline-primary me-2" on:click={() => showCreateTextModal = true}>Create From Text</button>
              <button class="btn btn-outline-primary" on:click={() => showYoutubeModal = true}>Upload YouTube Video</button>
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
            <a href="/language/{language_code}/source/{sourcedir.slug}/{file.slug}" class="text-decoration-none fs-5">
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
          
          <button class="btn btn-sm btn-outline-danger" on:click={() => deleteSourcefile(file.slug)}>
            <i class="bi bi-trash"></i>
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
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Create Sourcefile from Text</h5>
          <button type="button" class="btn-close" on:click={closeCreateTextModal}></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="textTitle" class="form-label">Title:</label>
            <input type="text" class="form-control" id="textTitle" bind:value={textTitle} placeholder="Enter title for the text">
          </div>
          <div class="mb-3">
            <label for="textContent" class="form-label">Text Content:</label>
            <textarea class="form-control" id="textContent" rows="10" bind:value={textContent} placeholder="Enter or paste your text here"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" on:click={closeCreateTextModal}>Cancel</button>
          <button type="button" class="btn btn-success" on:click={submitCreateText}>Create</button>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- YouTube URL Modal -->
{#if showYoutubeModal}
  <div class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Download YouTube Audio</h5>
          <button type="button" class="btn-close" on:click={closeYoutubeModal}></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label for="youtubeUrl" class="form-label">YouTube URL:</label>
            <input type="text" class="form-control" id="youtubeUrl" bind:value={youtubeUrl} placeholder="Enter YouTube URL">
            <div class="form-text">
              Supports full YouTube URLs, short URLs (youtu.be), and mobile URLs (m.youtube.com).<br>
              Maximum audio length: 60 minutes
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" on:click={closeYoutubeModal}>Cancel</button>
          <button type="button" class="btn btn-primary" on:click={downloadYoutube}>Download Audio</button>
        </div>
      </div>
    </div>
  </div>
{/if} 