<script lang="ts">
  // User ID to display
  export let userId: string;
  export const loadingText: string = "Loading...";
  
  // Format a UUID to be shorter and more readable
  function formatUserId(id: string): string {
    // If it looks like a UUID, format it to be shorter
    if (id && id.length > 8 && id.includes('-')) {
      // Return first part of the UUID
      return id.split('-')[0] + '...';
    }
    return id;
  }
</script>

<span class="user-id">{formatUserId(userId)}</span>

<style>
  .user-id {
    opacity: 0.7;
    font-family: var(--bs-font-monospace, monospace);
    font-size: 0.85em;
  }
</style>