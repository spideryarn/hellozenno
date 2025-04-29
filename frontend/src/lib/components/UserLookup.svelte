<script lang="ts">
  import { formatUserId } from '$lib/user-utils';
  
  // User ID to display
  export let userId: string;
  export const loadingText: string = "Loading...";
</script>

<span class="user-id">{formatUserId(userId)}</span>

<style>
  .user-id {
    opacity: 0.7;
    font-family: var(--bs-font-monospace, monospace);
    font-size: 0.85em;
  }
</style>