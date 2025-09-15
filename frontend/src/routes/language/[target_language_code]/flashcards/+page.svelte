<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import { getPageUrl } from '$lib/navigation';
  import { SITE_NAME } from '$lib/config';
  import X from 'phosphor-svelte/lib/X';
  import FunnelSimple from 'phosphor-svelte/lib/FunnelSimple';
  
  export let data;
  
  // Destructure data
  const { target_language_code, language_name, sourcefile, sourcedir, lemma_count } = data;
  
  // Get error message from URL if present
  let error = '';
  let isError = false;
  let errorCode = '';
  let errorLemmaCount: number | null = null;
  let errorSourcefile = '';
  let errorSourcedir = '';
  
  // Helper for generating the start button URL
  function getStartUrl() {
    const baseUrl = `/language/${target_language_code}/flashcards/random`;
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
  
  // Function to clear filter and navigate
  function clearFilter(event: Event) {
    event.preventDefault();
    window.location.href = `/language/${target_language_code}/flashcards`;
  }
  
  // Handle keyboard events
  // For complete keyboard shortcuts reference, see frontend/docs/KEYBOARD_SHORTCUTS.md
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      window.location.href = startUrl;
    }
  }
  
  onMount(() => {
    // Check for structured error message in URL
    const searchParams = new URLSearchParams(window.location.search);
    const ec = searchParams.get('error_code');
    if (ec) {
      isError = true;
      errorCode = ec;
      errorLemmaCount = searchParams.get('lemma_count') ? Number(searchParams.get('lemma_count')) : null;
      errorSourcefile = searchParams.get('sourcefile') || '';
      errorSourcedir = searchParams.get('sourcedir') || '';

      switch (errorCode) {
        case 'sourcefile_has_no_vocabulary':
          error = 'This file has no processed vocabulary yet.';
          break;
        case 'sourcedir_has_no_vocabulary':
          error = 'This directory has no processed vocabulary yet.';
          break;
        case 'invalid_sourcefile_slug':
        case 'invalid_sourcedir_slug':
          error = 'Not found. Check the link or try a different filter.';
          break;
        case 'no_sentences_match_required_lemmas':
          error = 'No sentences contain the selected words.';
          break;
        case 'no_sentences_for_language':
          error = 'No sentences are available for this language yet.';
          break;
        default:
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
  <title>Flashcards | {language_name} | {SITE_NAME}</title>
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
            <span class="d-flex align-items-center me-2" title="This content is filtered to show words from a specific source">
              <FunnelSimple size={24} weight="fill" />
            </span>
            <div>
              <p class="mb-1">
                Filtered by {sourcedir ? 'directory' : 'file'}: 
                {#if sourcedir}
                  <strong>
                    <a href={getPageUrl('sourcedir', {
                      target_language_code: target_language_code,
                      sourcedir_slug: sourcedir.slug
                    })} class="text-decoration-none">{sourcedir.name}</a>
                  </strong>
                {:else if sourcefile}
                  <strong>
                    <a href={getPageUrl('sourcefile', {
                      target_language_code: target_language_code,
                      sourcedir_slug: sourcefile.sourcedir_slug,
                      sourcefile_slug: sourcefile.slug
                    })} class="text-decoration-none">{sourcefile.name}</a>
                  </strong>
                {/if}
              </p>
              {#if lemma_count !== null}
                <p class="mb-0 small text-muted">({lemma_count} unique words)</p>
              {/if}
            </div>
            <button type="button" on:click={clearFilter} class="ms-auto btn btn-outline-secondary clear-filter d-flex align-items-center justify-content-center" aria-label="Clear filter" title="Remove filter">
              <X size={18} weight="bold" />
            </button>
          </div>
        {/if}
        
        <!-- Start button - moved up for better visibility on mobile -->
        <div class="start-button-container d-grid gap-2 col-md-8 mx-auto mb-4">
          <div class="start-button-wrapper p-3 text-center">
            <a href={startUrl} class="btn hz-start-button" tabindex="0">
              Start Flashcards <span class="ms-1 shortcut-hint">(Enter)</span>
            </a>
          </div>
        </div>

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
          <h5>Keyboard shortcuts:</h5>
          <div class="d-flex justify-content-center gap-4 flex-wrap">
            <div class="shortcut-item">
              <span class="hz-key">←</span> Previous stage
            </div>
            <div class="shortcut-item">
              <span class="hz-key">→</span> Next stage
            </div>
            <div class="shortcut-item">
              <span class="hz-key hz-key-enter">Enter</span> New sentence
            </div>
          </div>
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
    background-color: var(--hz-color-border-subtle);
    border-radius: 8px;
    padding: 1rem 1.5rem;
    margin-top: 1.5rem;
  }
  
  .hz-keyboard-hints h5 {
    text-align: center;
    margin-bottom: 1rem;
    font-weight: 600;
  }
  
  .hz-key {
    display: inline-block;
    padding: 0.15rem 0.4rem;
    margin-right: 0.5rem;
    border: 1px solid var(--hz-color-primary-green);
    border-radius: 0.25rem;
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.15);
    color: var(--hz-color-text-main);
    font-size: 0.9rem;
    font-family: monospace;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    min-width: 2rem;
    text-align: center;
  }
  
  .shortcut-item {
    display: flex;
    align-items: center;
    font-size: 0.95rem;
  }
  
  .hz-key-enter {
    min-width: 3.5rem;
  }
  
  .shortcut-hint {
    font-size: 0.9rem;
    opacity: 0.7;
  }
  
  /* Using global .hz-filter-banner class from theme.css */
  
  .clear-filter {
    background-color: transparent;
    border-color: var(--hz-color-border);
    color: var(--hz-color-text-main);
    width: 36px;
    height: 36px;
    padding: 0;
  }
  
  .clear-filter:hover {
    background-color: var(--hz-color-primary-green-dark);
    border-color: var(--hz-color-primary-green);
    color: var(--hz-color-text-main);
  }

  .hz-start-button {
    background-color: var(--hz-color-primary-green);
    color: white;
    font-weight: 600;
    font-size: 1.2rem;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    border: none;
    box-shadow: var(--hz-shadow-primary-green);
    transition: all 0.2s ease;
    margin-top: 0.5rem;
  }
  
  .hz-start-button:hover {
    background-color: var(--hz-color-primary-green-light);
    transform: translateY(-2px);
    box-shadow: var(--hz-shadow-primary-green-lg);
    color: white;
  }
  
  .hz-start-button:active {
    transform: translateY(0);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  }
  
  .start-button-wrapper {
    background-color: rgba(var(--hz-color-primary-green-rgb), 0.08);
    border-radius: 12px;
    /* Removed dashed border */
  }
</style> 