<script lang="ts">
  import type { Sentence, SentenceMetadata } from '$lib/types';
  import { MetadataCard, AudioPlayer } from '$lib';
  import { getApiUrl } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { goto } from '$app/navigation';
  import Trash from 'phosphor-svelte/lib/Trash';
  
  // Props for the Sentence component
  export let sentence: Sentence;
  export let metadata: SentenceMetadata = {};
  export let enhanced_sentence_text: string = '';
  
  // State for audio player
  let audioPlayer;
  let isDeleting = false;
  
  // Generate the audio URL using type-safe route resolution
  const audioUrl = getApiUrl(RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_API, {
    target_language_code: sentence.target_language_code,
    sentence_id: String(sentence.id)
  });
  
  // Function to handle sentence deletion
  async function deleteSentence() {
    if (!confirm('Are you sure you want to delete this sentence?')) {
      return;
    }
    
    isDeleting = true;
    
    try {
      const deleteUrl = getApiUrl(RouteName.SENTENCE_API_DELETE_SENTENCE_API, {
        target_language_code: sentence.target_language_code,
        slug: sentence.slug
      });
      
      const response = await fetch(deleteUrl, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to delete: ${response.status} ${response.statusText}`);
      }
      
      // Redirect to sentences list after successful deletion
      goto(`/language/${sentence.target_language_code}/sentences`);
    } catch (error) {
      alert(`Error deleting sentence: ${error}`);
      isDeleting = false;
    }
  }
</script>

<div class="container py-3">
  <div class="card">
    <div class="card-body">
      <!-- Metadata and Actions Row -->
      <div class="d-flex justify-content-between align-items-start mb-3">
        <!-- Delete Button -->
        <div>
          <button 
            type="button" 
            class="btn btn-outline-warning btn-sm"
            on:click={deleteSentence}
            disabled={isDeleting}
            aria-label="Delete sentence"
          >
            <Trash size={16} weight="bold" />
            {#if isDeleting}
              Deleting...
            {:else}
              Delete
            {/if}
          </button>
        </div>
        
        <!-- Metadata -->
        {#if metadata && (metadata.created_at || metadata.updated_at)}
          <div>
            <MetadataCard {metadata} />
          </div>
        {/if}
      </div>

      <div class="mb-4">
        <div class="hz-foreign-text fs-4 mb-3">
          <!-- Render the enhanced text with fallback -->
          {@html enhanced_sentence_text || `<p>${sentence.text}</p>`}
        </div>
        
        {#if sentence.translation}
          <div class="text-secondary fst-italic">
            {sentence.translation}
          </div>
        {/if}
      </div>

      <!-- Audio Section -->
      {#if sentence.has_audio}
        <div class="mt-4">
          <AudioPlayer 
            bind:this={audioPlayer}
            src={audioUrl}
            showControls={true}
            showSpeedControls={true}
            showDownload={false}
          />
        </div>
      {/if}
    </div>
  </div>
</div> 