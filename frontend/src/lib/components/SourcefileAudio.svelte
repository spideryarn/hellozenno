<script lang="ts">
  import { AudioPlayer } from '$lib';
  
  export let audioUrl: string;
  export let downloadUrl: string;
  export let filename: string = '';
  
  let audioPlayer;
</script>

<div class="audio-view">
  <h3>Audio Player{#if filename} - {filename}{/if}</h3>
  
  <AudioPlayer 
    bind:this={audioPlayer}
    src={audioUrl}
    downloadUrl={downloadUrl}
    showControls={true}
    showSpeedControls={true}
    showDownload={true}
  />
</div>

<style>
  .audio-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: var(--hz-color-text-main);
  }
</style>