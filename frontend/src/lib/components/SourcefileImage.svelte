<script lang="ts">
  import { Download } from 'phosphor-svelte';
  
  export let viewUrl: string;
  export let downloadUrl: string;
  export let altText: string = 'Image content';
</script>

<div class="image-view">
  <div class="image-container">
    <img src={viewUrl} alt={altText} class="source-image" />
  </div>
  
  <div class="image-actions">
    <a href={downloadUrl} class="button download-button">
      <Download size={16} weight="bold" /> Download image
    </a>
  </div>
</div>

<style>
  .image-view {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .image-container {
    max-width: 100%;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    padding: 1rem;
  }
  
  .source-image {
    max-width: 100%;
    height: auto;
  }
  
  .image-actions {
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