<script lang="ts">
  import type { PageData } from './$types';
  
  export let data: PageData;
</script>

<div class="container mt-4">
  <div class="d-flex justify-content-center">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
  <p class="text-center mt-3">Searching...</p>
</div> 