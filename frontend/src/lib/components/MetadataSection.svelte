<script lang="ts">
  import { MetadataCard } from '$lib';
  import type { Metadata } from '$lib/types/sourcefile';
  
  export let metadata: Metadata;
</script>

<div class="metadata-section">
  <h3>File Information</h3>
  <MetadataCard {metadata} />
</div>

<style>
  .metadata-section {
    margin-top: 0.5rem;
  }
  
  h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }
</style>