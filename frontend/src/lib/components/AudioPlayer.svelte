<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import Download from 'phosphor-svelte/lib/Download';
  import LoadingSpinner from './LoadingSpinner.svelte';
  
  const dispatch = createEventDispatcher();
  
  // Props
  export let src: string;
  export let downloadUrl: string = src;
  export let autoplay: boolean = false;
  export let showControls: boolean = true;
  export let showSpeedControls: boolean = true;
  export let showDownload: boolean = true;
  export let className: string = '';
  export let containerStyle: string = '';
  
  // State
  let audioElement: HTMLAudioElement;
  let currentPlaybackRate: number = 1.0;
  let isLoading: boolean = true;
  let hasError: boolean = false;
  let errorMessage: string = '';
  let autoplayBlocked: boolean = false;
  
  // Exposed properties and methods
  export function play() {
    if (audioElement) {
      audioElement.play().catch(handleError);
    }
  }
  
  export function pause() {
    if (audioElement) {
      audioElement.pause();
    }
  }
  
  export function setPlaybackRate(rate: number, userInitiated: boolean = false) {
    if (audioElement) {
      audioElement.playbackRate = rate;
      currentPlaybackRate = rate;
      
      // Dispatch an event when the user manually changes the speed
      if (userInitiated) {
        dispatch('speedChanged', { rate, userInitiated });
      }
    }
  }
  
  export const isPlaying = (): boolean => {
    return audioElement ? !audioElement.paused : false;
  }
  
  // Event handlers
  function handleError(error: any) {
    console.error('Audio playback error:', error);
    isLoading = false;
    
    // Special handling for autoplay errors - common on mobile devices
    // This catches various browser-specific autoplay restriction messages
    if (
      error?.message?.includes("play() failed because the user didn't interact") ||
      error?.message?.includes("request is not allowed by the user agent") ||
      error?.message?.includes("user denied permission") ||
      error?.message?.includes("user gesture is required") ||
      error?.name === 'NotAllowedError'
    ) {
      // Don't show error for autoplay - just stop the loading spinner
      hasError = false;
      autoplayBlocked = true;
      dispatch('autoplayBlocked', { error });
      return;
    }
    
    // For all other errors, show error message
    hasError = true;
    errorMessage = error?.message || 'Failed to play audio';
  }
  
  function handleCanPlay() {
    isLoading = false;
    hasError = false;
  }
  
  function handleLoadStart() {
    isLoading = true;
    hasError = false;
  }
  
  // Component lifecycle
  onMount(() => {
    if (audioElement && autoplay) {
      audioElement.play().catch(handleError);
    }
    
    // Safety timeout to stop loading spinner if audio never loads
    const safetyTimer = setTimeout(() => {
      if (isLoading) {
        isLoading = false;
      }
    }, 5000); // 5 second safety timeout
    
    return () => clearTimeout(safetyTimer);
  });
</script>

<div class="audio-view {className} {autoplayBlocked ? 'audio-player-needs-interaction' : ''}" style={containerStyle}>
  <div class="audio-container">
    {#if isLoading}
      <div class="loading-container">
        <LoadingSpinner size="small" />
        <span>Loading audio...</span>
      </div>
    {/if}
    
    {#if hasError}
      <div class="error-message alert alert-danger">
        <p>Error loading audio: {errorMessage}</p>
      </div>
    {/if}
    
    <audio 
      bind:this={audioElement}
      {src}
      controls={showControls}
      class="audio-player"
      on:canplay={handleCanPlay}
      on:loadstart={handleLoadStart}
      on:error={() => handleError(new Error('Audio could not be loaded'))}
      on:play
      on:pause
      on:ended
    >
      Your browser does not support the audio element.
    </audio>
    
    {#if showSpeedControls}
      <div class="speed-controls-container mt-2">
        <div class="d-flex gap-2 justify-content-center">
          <button
            class="btn btn-sm {currentPlaybackRate === 0.8 ? 'btn-primary' : 'btn-outline-secondary'}"
            on:click={() => setPlaybackRate(0.8, true)}
            aria-label="Set playback speed to 0.8x"
          >
            0.8x
          </button>
          <button
            class="btn btn-sm {currentPlaybackRate === 0.85 ? 'btn-primary' : 'btn-outline-secondary'}"
            on:click={() => setPlaybackRate(0.85, true)}
            aria-label="Set playback speed to 0.85x"
          >
            0.85x
          </button>
          <button
            class="btn btn-sm {currentPlaybackRate === 0.9 ? 'btn-primary' : 'btn-outline-secondary'}"
            on:click={() => setPlaybackRate(0.9, true)}
            aria-label="Set playback speed to 0.9x"
          >
            0.9x
          </button>
          <button
            class="btn btn-sm {currentPlaybackRate === 0.95 ? 'btn-primary' : 'btn-outline-secondary'}"
            on:click={() => setPlaybackRate(0.95, true)}
            aria-label="Set playback speed to 0.95x"
          >
            0.95x
          </button>
          <button
            class="btn btn-sm {currentPlaybackRate === 1.0 ? 'btn-primary' : 'btn-outline-secondary'}"
            on:click={() => setPlaybackRate(1.0, true)}
            aria-label="Set playback speed to 1.0x"
          >
            1.0x
          </button>
          <button
            class="btn btn-sm {currentPlaybackRate === 1.2 ? 'btn-primary' : 'btn-outline-secondary'}"
            on:click={() => setPlaybackRate(1.2, true)}
            aria-label="Set playback speed to 1.2x"
          >
            1.2x
          </button>
        </div>
      </div>
    {/if}
  </div>
  
  {#if showDownload}
    <div class="audio-actions d-flex justify-content-end mt-2">
      <a href={downloadUrl} download class="button download-button">
        <Download size={16} weight="bold" /> Download
      </a>
    </div>
  {/if}
</div>

<style>
  .audio-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .audio-container {
    background-color: var(--hz-color-surface-transparent-15);
    border-radius: 8px;
    padding: 1rem;
    position: relative;
    min-height: 60px;
  }
  
  .audio-player {
    width: 100%;
  }
  
  .loading-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  
  .audio-actions {
    display: flex;
    align-items: center;
  }
  
  .button {
    background-color: var(--hz-color-primary-green);
    color: var(--hz-color-text-main);
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }
  
  .download-button {
    background-color: var(--hz-color-accent-sky-blue);
    color: var(--hz-color-surface);
  }
  
  .error-message {
    margin-bottom: 1rem;
  }
</style>