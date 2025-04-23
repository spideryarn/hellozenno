<script lang="ts">
  import { DescriptionFormatted } from '$lib';
  
  export let description: string = '';
  export let onSave: (text: string) => Promise<void>;
</script>

<div class="description-section">
  <h3>Description</h3>
  <DescriptionFormatted 
    {description} 
    placeholder="No description available for this file"
    cssClass=""
    {onSave}
  />
</div>

<style>
  .description-section {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--hz-color-border-subtle);
  }
  
  h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }
</style>