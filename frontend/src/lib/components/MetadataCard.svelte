<script lang="ts">
  // MetadataCard component for displaying creation and update timestamps
  // Used across various pages for consistent metadata display
  
  export let metadata: { created_at?: string; updated_at?: string } = {};
  
  // Format the timestamp for display
  function formatTimestamp(timestamp: string): string {
    if (!timestamp) return '';
    
    // Try to parse the date and format it
    try {
      const date = new Date(timestamp);
      
      // Format as: Thu, 27 Mar 2025 02:14
      const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      
      const day = dayNames[date.getDay()];
      const dateNum = date.getDate();
      const month = monthNames[date.getMonth()];
      const year = date.getFullYear();
      const hours = date.getHours().toString().padStart(2, '0');
      const minutes = date.getMinutes().toString().padStart(2, '0');
      
      return `${day}, ${dateNum} ${month} ${year} ${hours}:${minutes}`;
    } catch (e) {
      // If parsing fails, return the original timestamp
      return timestamp;
    }
  }
</script>

{#if metadata && (metadata.created_at || metadata.updated_at)}
  <div class="metadata-card">
    {#if metadata.created_at}
      <p class="metadata-item">Created: <span class="metadata-timestamp">{formatTimestamp(metadata.created_at)}</span></p>
    {/if}
    {#if metadata.updated_at}
      <p class="metadata-item">Updated: <span class="metadata-timestamp">{formatTimestamp(metadata.updated_at)}</span></p>
    {/if}
  </div>
{/if}

<style>
  .metadata-card {
    text-align: right;
    margin-bottom: 0.75rem;
    opacity: 0.7;
    transition: opacity 0.2s ease;
  }
  
  .metadata-card:hover {
    opacity: 1;
  }
  
  .metadata-item {
    font-size: 0.8rem;
    color: var(--hz-color-text-secondary);
    margin-bottom: 0.2rem;
  }
  
  .metadata-timestamp {
    font-family: var(--bs-font-monospace, monospace);
  }
</style> 