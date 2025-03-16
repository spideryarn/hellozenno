<script lang="ts">
  export let targetLanguageCode: string;
  export let targetLanguageName: string;
  export let sourcefile: string | null = null;
  export let sourcedir: string | null = null;
  export let lemmaCount: number | null = null;

  // Build the URL for starting the flashcards
  let startUrl = `/lang/${targetLanguageCode}/flashcards/random`;
  
  // Add query parameters if we have source filtering
  if (sourcefile) {
    startUrl += `?sourcefile=${sourcefile}`;
  } else if (sourcedir) {
    startUrl += `?sourcedir=${sourcedir}`;
  }

  // Handle keyboard shortcut (Enter to start)
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      window.location.href = startUrl;
    }
  }
</script>

<div class="flashcard-landing">
  <!-- Source filter info banner -->
  {#if sourcefile || sourcedir}
    <div class="source-filter-banner">
      <i class="ph-fill ph-filter"></i>
      Filtered by {sourcedir ? 'directory' : 'file'}: 
      <strong>{sourcedir || sourcefile}</strong>
      {#if lemmaCount !== null}
        <span class="lemma-count">({lemmaCount} words)</span>
      {/if}
      <a href="/lang/{targetLanguageCode}/flashcards" class="clear-filter">
        <i class="ph-fill ph-x"></i>
      </a>
    </div>
  {/if}

  <div class="flashcard-description">
    <p>
      Practice your {targetLanguageName} vocabulary with interactive flashcards.
      Each flashcard has three stages:
    </p>
    <ol>
      <li>Listen to the audio</li>
      <li>View the {targetLanguageName} sentence</li>
      <li>See the translation</li>
    </ol>
    
    <p class="keyboard-hints">
      <strong>Keyboard shortcuts:</strong>
      <span class="shortcut">←</span> Previous stage
      <span class="shortcut">→</span> Next stage
      <span class="shortcut">Enter</span> New sentence
    </p>
  </div>
  
  <div class="start-button-container">
    <a href={startUrl} class="start-button" on:keydown={handleKeydown}>
      Start Flashcards <span class="shortcut-hint">(Enter)</span>
    </a>
  </div>
</div>

<style>
  .flashcard-landing {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
  }
  
  .flashcard-description {
    margin-bottom: 2rem;
    text-align: left;
  }
  
  .start-button-container {
    display: flex;
    justify-content: center;
    margin: 1rem 0;
  }
  
  .start-button {
    background-color: #2563eb;
    color: white;
    padding: 1rem 2rem;
    border-radius: 0.5rem;
    font-size: 1.25rem;
    text-decoration: none;
    transition: background-color 0.2s ease;
    display: inline-block;
  }
  
  .start-button:hover {
    background-color: #1d4ed8;
  }
  
  .keyboard-hints {
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #64748b;
  }
  
  .shortcut {
    display: inline-block;
    padding: 0.15rem 0.4rem;
    margin: 0 0.25rem;
    border: 1px solid #e2e8f0;
    border-radius: 0.25rem;
    background-color: #f8fafc;
    font-size: 0.8rem;
    font-family: monospace;
  }
  
  .shortcut-hint {
    font-size: 0.9rem;
    opacity: 0.7;
  }
  
  .source-filter-banner {
    background-color: #f0f7ff;
    border: 1px solid #bfdbfe;
    color: #1e40af;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    font-size: 0.9rem;
    gap: 0.5rem;
    width: 100%;
    max-width: 600px;
    align-self: center;
  }
  
  .source-filter-banner i {
    font-size: 1.1rem;
  }
  
  .lemma-count {
    color: #4b5563;
    margin-left: 0.25rem;
  }
  
  .clear-filter {
    margin-left: auto;
    color: #6b7280;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.5rem;
    height: 1.5rem;
    border-radius: 50%;
    background-color: #e5e7eb;
    transition: background-color 0.2s ease;
  }
  
  .clear-filter:hover {
    background-color: #d1d5db;
    color: #4b5563;
  }
</style>