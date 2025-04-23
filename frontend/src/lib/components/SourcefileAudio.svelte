<script lang="ts">
  import { Download } from 'phosphor-svelte';
  
  export let audioUrl: string;
  export let downloadUrl: string;
  
  // Set default playback rate to 1.0
  let currentPlaybackRate: number = 1.0;
  let audioElement: HTMLAudioElement;
  
  // Function to set the playback rate
  function setPlaybackRate(rate: number) {
    if (audioElement) {
      audioElement.playbackRate = rate;
      currentPlaybackRate = rate;
    }
  }
</script>

<div class="audio-view">
  <div class="audio-container">
    <h3>Audio Player</h3>
    <audio bind:this={audioElement} controls src={audioUrl} class="audio-player">
      Your browser does not support the audio element.
    </audio>
  </div>
  
  <div class="audio-actions">
    <a href={downloadUrl} class="button download-button">
      <Download size={16} weight="bold" /> Download audio
    </a>
  </div>
  
  <div class="d-flex gap-2">
    <button
      class="btn btn-sm {currentPlaybackRate === 0.85 ? 'btn-primary' : 'btn-outline-secondary'}"
      on:click={() => setPlaybackRate(0.85)}
    >
      0.85x
    </button>
    <button
      class="btn btn-sm {currentPlaybackRate === 1.0 ? 'btn-primary' : 'btn-outline-secondary'}"
      on:click={() => setPlaybackRate(1.0)}
    >
      1.0x
    </button>
    <button
      class="btn btn-sm {currentPlaybackRate === 1.2 ? 'btn-primary' : 'btn-outline-secondary'}"
      on:click={() => setPlaybackRate(1.2)}
    >
      1.2x
    </button>
  </div>
</div>

<style>
  .audio-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .audio-container {
    background-color: var(--hz-color-surface-transparent-15);
    border-radius: 4px;
    padding: 1rem;
  }
  
  h3 {
    font-size: 1rem;
    margin-bottom: 1rem;
    color: var(--hz-color-text-main);
  }
  
  .audio-player {
    width: 100%;
  }
  
  .audio-actions {
    display: flex;
    gap: 0.5rem;
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
</style>