<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  
  export let data;
  
  // Destructure data
  const { language_code, language_name, sourcefile, sourcedir, lemma_count } = data;
  
  // Get error message from URL if present
  let error = '';
  let isError = false;
  
  // Helper for generating the start button URL
  function getStartUrl() {
    const baseUrl = `/language/${language_code}/flashcards/random`;
    let params = new URLSearchParams();
    
    if (sourcefile) {
      params.append('sourcefile', sourcefile.slug);
      return `${baseUrl}?${params.toString()}`;
    }
    
    if (sourcedir) {
      params.append('sourcedir', sourcedir.slug);
      return `${baseUrl}?${params.toString()}`;
    }
    
    return baseUrl;
  }
  
  let startUrl = getStartUrl();
  
  // Handle keyboard events
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      window.location.href = startUrl;
    }
  }
  
  onMount(() => {
    // Check for error message in URL
    const searchParams = new URLSearchParams(window.location.search);
    if (searchParams.has('error')) {
      isError = true;
      const errorType = searchParams.get('error');
      if (errorType === 'no_sentences_found') {
        error = 'No matching sentences found for this language.';
      } else {
        error = 'An error occurred while loading flashcards.';
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  });
</script>

<svelte:head>
  <title>{language_name} Flashcards</title>
</svelte:head>

<div class="container my-4">
  <div class="row justify-content-center">
    <div class="col-md-8">
      <Card>
        <h1 class="card-title text-center mb-4 hz-title">{language_name} Flashcards</h1>
        
        {#if isError}
          <div class="alert alert-danger mb-4">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {error}
          </div>
        {/if}
        
        <!-- Source filter banner -->
        {#if sourcefile || sourcedir}
          <div class="hz-filter-banner mb-4">
            <i class="bi bi-filter me-2"></i>
            <div>
              <p class="mb-1">
                Filtered by {sourcedir ? 'directory' : 'file'}: 
                <strong>{sourcedir ? sourcedir.name : sourcefile.name}</strong>
              </p>
              {#if lemma_count !== null}
                <p class="mb-0 small text-muted">({lemma_count} unique words)</p>
              {/if}
            </div>
            <a href={`/language/${language_code}/flashcards`} class="ms-auto btn btn-sm btn-outline-secondary clear-filter">
              <i class="bi bi-x"></i>
            </a>
          </div>
        {/if}
        
        <div class="flashcard-description mb-4">
          <p>
            Practice your <span class="hz-language-name">{language_name}</span> vocabulary with interactive flashcards.
            Each flashcard has three stages:
          </p>
          <ol class="hz-steps">
            <li>Listen to the audio</li>
            <li>View the <span class="hz-foreign-text">{language_name}</span> sentence</li>
            <li>See the translation</li>
          </ol>
        </div>
        
        <div class="hz-keyboard-hints mb-4">
          <p>
            <strong>Keyboard shortcuts:</strong><br>
            <span class="hz-key">←</span> Previous stage 
            <span class="hz-key">→</span> Next stage
            <span class="hz-key">Enter</span> New sentence
          </p>
        </div>
        
        <div class="start-button-container d-grid gap-2 col-md-8 mx-auto mt-4">
          <a href={startUrl} class="btn hz-start-button" tabindex="0">
            Start Flashcards <span class="ms-1 shortcut-hint">(Enter)</span>
          </a>
        </div>
      </Card>
    </div>
  </div>
</div>

<style>
  :global(body) {
    background-color: #121212;
    color: #e9e9e9;
  }
  
  .hz-title {
    font-weight: 700;
    margin-bottom: 1.5rem;
    color: #4CAD53;
  }
  
  .hz-language-name {
    font-weight: 600;
  }

  .hz-foreign-text {
    font-style: italic;
    font-weight: 600;
  }
  
  .flashcard-description {
    color: #e9e9e9;
    font-size: 1.1rem;
    line-height: 1.6;
  }
  
  .hz-steps {
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    padding-left: 1.5rem;
  }
  
  .hz-steps li {
    margin-bottom: 0.5rem;
    padding-left: 0.5rem;
  }
  
  .hz-keyboard-hints {
    background-color: rgba(76, 173, 83, 0.1);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1.5rem;
  }
  
  .hz-key {
    display: inline-block;
    padding: 0.15rem 0.4rem;
    margin: 0 0.25rem;
    border: 1px solid #4CAD53;
    border-radius: 0.25rem;
    background-color: rgba(76, 173, 83, 0.2);
    color: #e9e9e9;
    font-size: 0.9rem;
    font-family: monospace;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  }
  
  .shortcut-hint {
    font-size: 0.9rem;
    opacity: 0.7;
  }
  
  .hz-filter-banner {
    background-color: rgba(217, 122, 39, 0.1);
    border: 1px solid rgba(217, 122, 39, 0.3);
    color: #e9e9e9;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    display: flex;
    align-items: center;
  }
  
  .clear-filter {
    background-color: rgba(217, 122, 39, 0.2);
    border-color: rgba(217, 122, 39, 0.4);
    color: #e9e9e9;
  }
  
  .clear-filter:hover {
    background-color: rgba(217, 122, 39, 0.3);
    border-color: rgba(217, 122, 39, 0.5);
    color: #fff;
  }

  .hz-start-button {
    background-color: #4CAD53;
    color: #121212;
    font-weight: 600;
    font-size: 1.1rem;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    transition: all 0.2s ease;
  }
  
  .hz-start-button:hover {
    background-color: #5abe61;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
    color: #121212;
  }
  
  .hz-start-button:active {
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  }
</style> 