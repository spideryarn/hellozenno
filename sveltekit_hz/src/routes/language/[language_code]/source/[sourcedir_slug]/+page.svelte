<script lang="ts">
  import type { PageData } from './$types';
  
  export let data: PageData;
  
  const { sourcedir, sourcefiles, language_code, language_name, has_vocabulary } = data;
</script>

<svelte:head>
  <title>{sourcedir.path} | {language_name}</title>
</svelte:head>

<div class="container">
  <nav class="breadcrumb">
    <a href="/">Home</a>
    » <a href="/language">Languages</a>
    » <a href="/language/{language_code}/sources">{language_name}</a>
    » {sourcedir.path}
  </nav>

  <header class="sourcedir-header">
    <h1>{sourcedir.path}</h1>
    {#if sourcedir.description}
      <p class="description">{sourcedir.description}</p>
    {/if}
  </header>

  <div class="files-list">
    <h2>Source Files</h2>
    {#if sourcefiles.length === 0}
      <p class="empty-message">No files in this directory.</p>
    {:else}
      <div class="source-files">
        {#each sourcefiles as file}
          <div class="source-file-item">
            <div class="file-icon">
              {#if file.sourcefile_type === 'text'}
                <span class="icon">📄</span>
              {:else if file.sourcefile_type === 'audio'}
                <span class="icon">🔊</span>
              {:else if file.sourcefile_type === 'image'}
                <span class="icon">🖼️</span>
              {:else if file.sourcefile_type === 'youtube_audio'}
                <span class="icon">📺</span>
              {:else}
                <span class="icon">📁</span>
              {/if}
            </div>
            <div class="file-details">
              <a href="/language/{language_code}/source/{sourcedir.slug}/{file.slug}" class="file-link">
                {file.filename}
              </a>
              <div class="file-metadata">
                {#if file.metadata.has_audio}
                  <span class="badge audio-badge">Audio</span>
                {/if}
                {#if file.metadata.wordform_count > 0}
                  <span class="badge vocab-badge">Words: {file.metadata.wordform_count}</span>
                {/if}
                {#if file.metadata.phrase_count > 0}
                  <span class="badge phrases-badge">Phrases: {file.metadata.phrase_count}</span>
                {/if}
                {#if file.metadata.duration}
                  <span class="badge duration-badge">{Math.floor(file.metadata.duration / 60)}:{(file.metadata.duration % 60).toString().padStart(2, '0')}</span>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  }
  
  .breadcrumb {
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
  }
  
  .breadcrumb a {
    text-decoration: none;
  }
  
  .breadcrumb a:hover {
    text-decoration: underline;
  }
  
  .sourcedir-header {
    margin-bottom: 2rem;
  }
  
  .description {
    font-style: italic;
    color: #888;
    margin-top: 0.5rem;
  }
  
  .source-files {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }
  
  .source-file-item {
    display: flex;
    padding: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #1a1a1a;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .source-file-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  }
  
  .file-icon {
    margin-right: 1rem;
    font-size: 1.5rem;
  }
  
  .file-details {
    flex: 1;
  }
  
  .file-link {
    display: block;
    font-weight: bold;
    margin-bottom: 0.5rem;
    text-decoration: none;
    color: #4CAD53;
  }
  
  .file-link:hover {
    text-decoration: underline;
  }
  
  .file-metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .badge {
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    background-color: #222;
  }
  
  .audio-badge {
    background-color: #2d5d9b;
  }
  
  .vocab-badge {
    background-color: #4CAD53;
  }
  
  .phrases-badge {
    background-color: #D97A27;
  }
  
  .duration-badge {
    background-color: #6a6a6a;
  }
  
  .empty-message {
    padding: 2rem;
    text-align: center;
    border: 1px dashed #555;
    border-radius: 4px;
    color: #888;
  }
</style> 