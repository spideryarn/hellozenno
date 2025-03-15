<script lang="ts">
  export let targetLanguageCode: string;
  export let targetLanguageName: string;
  export let sourcefile: string | null = null;
  export let sourcedir: string | null = null;
  export let lemmaCount: number | null = null;

  // Build the URL for starting the flashcards
  let startUrl = `/${targetLanguageCode}/flashcards2/random`;
  
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
</style>