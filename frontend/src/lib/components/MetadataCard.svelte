<script lang="ts">
  // MetadataCard component for displaying creation and update timestamps
  // Used across various pages for consistent metadata display
  import UserLookup from './UserLookup.svelte';
  
  export let metadata: { 
    created_at?: string; 
    updated_at?: string;
    num_words?: number;
    language_level?: string;
    url?: string;
    created_by_id?: string;
    title_translation?: string;
    ai_generated?: boolean;
  } = {};
  
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

  // Get hostname from URL
  function getHostname(url: string): string {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch (e) {
      return url;
    }
  }
</script>

<div class="metadata-card">
  {#if metadata.created_at}
    <p class="metadata-item">Created: <span class="metadata-timestamp">{formatTimestamp(metadata.created_at)}</span></p>
  {/if}
  {#if metadata.updated_at}
    <p class="metadata-item">Updated: <span class="metadata-timestamp">{formatTimestamp(metadata.updated_at)}</span></p>
  {/if}
  
  {#if metadata.num_words !== undefined && metadata.num_words !== null}
    <p class="metadata-item">Word count: <span class="metadata-value">{metadata.num_words}</span></p>
  {/if}
  
  {#if metadata.language_level}
    <p class="metadata-item">Language level: <span class="metadata-value">{metadata.language_level.toUpperCase()}</span></p>
  {/if}

  {#if metadata.ai_generated !== undefined}
    <p class="metadata-item">AI-generated? <span class="metadata-value">{metadata.ai_generated ? 'Yes' : 'No'}</span></p>
  {/if}
  
  {#if metadata.url}
    <p class="metadata-item">Source: <a href={metadata.url} target="_blank" rel="noopener noreferrer" class="metadata-link">{getHostname(metadata.url)}</a></p>
  {/if}
  
  {#if metadata.created_by_id}
    <p class="metadata-item">Created by: <UserLookup userId={metadata.created_by_id} loadingText="Loading..." /></p>
  {/if}
  
  {#if metadata.title_translation}
    <p class="metadata-item">Title: <span class="metadata-value">{metadata.title_translation}</span></p>
  {/if}
</div>

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
  
  .metadata-value {
    font-weight: 500;
  }
  
  .metadata-link {
    color: var(--hz-color-primary-green);
    text-decoration: none;
    font-weight: 500;
  }
  
  .metadata-link:hover {
    text-decoration: underline;
  }
</style>