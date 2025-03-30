<script lang="ts">
  import { onMount } from 'svelte';
  import type { PageData } from '../$types';
  
  export let data: PageData;
  
  // This is just a route for the tab - the actual content is rendered in the parent
  onMount(() => {
    // Nothing needed here, parent component will handle everything based on the URL
  });
</script> 