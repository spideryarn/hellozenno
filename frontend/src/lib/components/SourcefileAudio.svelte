<script lang="ts">
  import { Download } from 'phosphor-svelte';
  
  export let audioUrl: string;
  export let downloadUrl: string;
  export let filename: string = 'Audio file';
</script>

<div class="audio-view">
  <div class="audio-container">
    <h3>Audio Player</h3>
    <audio controls src={audioUrl} class="audio-player">
      Your browser does not support the audio element.
    </audio>
  </div>
  
  <div class="audio-actions">
    <a href={downloadUrl} class="button download-button">
      <Download size={16} weight="bold" /> Download audio
    </a>
  </div>
</div>

<style>
  .audio-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .audio-container {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    padding: 1rem;
  }
  
  h3 {
    font-size: 1rem;
    margin-bottom: 1rem;
  }
  
  .audio-player {
    width: 100%;
  }
  
  .audio-actions {
    display: flex;
    gap: 0.5rem;
  }
  
  .button {
    background-color: #4CAD53;
    color: white;
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
    background-color: #0275d8;
  }
</style>