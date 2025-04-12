<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import { KeyReturn } from 'phosphor-svelte';
  import { getPageUrl } from '$lib/navigation';
  
  export let data;
  
  
  let currentStage = 1; // 1: Audio only, 2: Show sentence, 3: Show translation
  
  function nextStage() {
    if (currentStage < 3) {
      currentStage += 1;
    }
  }
  
  function playAudio() {
    const audioElement = document.getElementById('audio-player') as HTMLAudioElement;
    if (audioElement) {
      // Only restart if audio is not currently playing
      if (audioElement.paused || audioElement.ended) {
        audioElement.currentTime = 0; // Restart from beginning
        audioElement.play().catch(err => {
          console.error('Failed to play audio:', err);
        });
      }
    }
  }

  function prevStage() {
    if (currentStage > 1) {
      currentStage -= 1;
    }
    playAudio();
  }
  
  function nextSentence() {
    // Get parameters for the URL
    const params = new URLSearchParams(window.location.search);
    const baseUrl = `/language/${data.metadata.target_language_code}/flashcards/random`;
    
    if (params.toString()) {
      window.location.href = `${baseUrl}?${params.toString()}`;
    } else {
      window.location.href = baseUrl;
    }
  }
  
  // Handle keyboard shortcuts
  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'ArrowRight') {
      nextStage();
    } else if (event.key === 'ArrowLeft') {
      if (currentStage === 1) {
        playAudio();
      } else {
        prevStage(); // This already plays audio via the prevStage function
      }
    } else if (event.key === 'Enter') {
      nextSentence();
    }
  }
  
  onMount(() => {
    // Autoplay audio on load
    const audioElement = document.getElementById('audio-player') as HTMLAudioElement;
    if (audioElement) {
      audioElement.play().catch(err => {
        console.error('Failed to autoplay audio:', err);
      });
    }
    
    // Add keyboard event listener
    window.addEventListener('keydown', handleKeyDown);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  });
</script>

<svelte:head>
  <title>Flashcard | {data.metadata.language_name}</title>
</svelte:head>

<div class="container my-4">
  <div class="row justify-content-center">
    <div class="col-12 col-lg-10">
      <Card>
        <div class="text-center mb-4">
          <h2>{data.metadata.language_name} Flashcard</h2>
          
          {#if data.sourcefile}
            <p class="text-muted">
              From sourcefile: <a href={getPageUrl('sourcefile', {
                target_language_code: data.metadata.target_language_code,
                sourcedir_slug: data.sourcefile.sourcedir_slug,
                sourcefile_slug: data.sourcefile.slug
              })}>{data.sourcefile.name}</a>
            </p>
          {:else if data.sourcedir}
            <p class="text-muted">
              From sourcedir: <a href={getPageUrl('sourcedir', {
                target_language_code: data.metadata.target_language_code,
                sourcedir_slug: data.sourcedir.slug
              })}>{data.sourcedir.name}</a>
            </p>
          {/if}
        </div>
        
        <div class="row align-items-center mb-4">
          <div class="col-12">
            <!-- Audio player (always visible) -->
            <audio id="audio-player" src={data.audio_url} controls class="w-100 mb-3"></audio>
            
            <!-- Sentence (visible in stage 2+) -->
            {#if currentStage >= 2}
              <div class="alert alert-primary py-4">
                <h3 class="text-center font-weight-bold fs-2">{data.text}</h3>
              </div>
            {/if}
            
            <!-- Translation (visible in stage 3) -->
            {#if currentStage >= 3}
              <div class="alert alert-info py-3">
                <p class="text-center mb-0 fs-4">{data.translation}</p>
              </div>
            {/if}
          </div>
        </div>
        
        <div class="row g-3 mt-3">
          <!-- Navigation buttons -->
          <div class="col-4">
            <button 
              class="btn btn-secondary w-100 py-3" 
              on:click={currentStage === 1 ? playAudio : prevStage}>
              {currentStage === 1 ? 'Play audio (←)' : currentStage === 2 ? 'Play audio (←)' : 'Show sentence (←)'}
            </button>
          </div>
          
          <div class="col-4">
            <button 
              class="btn btn-primary w-100 py-3" 
              on:click={nextSentence}>
              New sentence <KeyReturn size={18} weight="bold" class="ms-1" />
            </button>
          </div>
          
          <div class="col-4">
            <button 
              class="btn btn-secondary w-100 py-3" 
              on:click={nextStage}
              disabled={currentStage === 3}>
              {currentStage === 1 ? 'Show sentence (→)' : currentStage === 2 ? 'Show translation (→)' : 'Next step (→)'}
            </button>
          </div>
        </div>
        
        <div class="text-center mt-4">
          <p class="text-muted small">
            Press ← → arrow keys to navigate, ENTER for next sentence
          </p>
        </div>
      </Card>
    </div>
  </div>
</div> 