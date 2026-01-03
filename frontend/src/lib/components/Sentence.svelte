<script lang="ts">
  import type { Sentence, SentenceMetadata } from '$lib/types';
  import { MetadataCard, AudioPlayer } from '$lib';
  import SentenceAudioButton from './SentenceAudioButton.svelte';
  import { getApiUrl, apiFetch } from '$lib/api';
  import { RouteName } from '$lib/generated/routes';
  import { goto } from '$app/navigation';
  import Trash from 'phosphor-svelte/lib/Trash';
  import type { SupabaseClient, Session } from '@supabase/supabase-js';
  import { sanitizeHtml, escapeHtml } from '$lib/utils/sanitize';
  
  // Props for the Sentence component
  export let sentence: Sentence;
  export let metadata: SentenceMetadata = {};
  export let enhanced_sentence_text: string = '';
  export let supabase: SupabaseClient | null = null;
  export let session: Session | null = null;
  
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
    
    if (!supabase) {
      alert('Authentication context not available. Cannot delete sentence.');
      return;
    }
    if (!session) {
      alert('You must be logged in to delete this sentence.');
      return;
    }
    
    isDeleting = true;
    
    try {
      await apiFetch({
        supabaseClient: supabase,
        routeName: RouteName.SENTENCE_API_DELETE_SENTENCE_API,
        params: {
          target_language_code: sentence.target_language_code,
          slug: sentence.slug
        },
        options: { method: 'DELETE' }
      });
      
      // Redirect to sentences list after successful deletion
      goto(`/language/${sentence.target_language_code}/sentences`);
    } catch (error: any) {
      alert(`Error deleting sentence: ${error.message || 'Unknown error'}`);
      isDeleting = false;
    }
  }
</script>

<div class="container py-3">
  <div class="card">
    <div class="card-body">
      <!-- Metadata and Actions Row -->
      <div class="d-flex justify-content-between align-items-start mb-3">
        <!-- Delete Button for individual sentence -->
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
              Delete sentence
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
        <div class="d-flex align-items-start gap-2 mb-3">
          <div class="hz-foreign-text fs-4 flex-grow-1">
            <!-- Render the enhanced text with fallback (sanitized for XSS prevention) -->
            {@html sanitizeHtml(enhanced_sentence_text) || `<p>${escapeHtml(sentence.text)}</p>`}
          </div>
          <!-- Quick audio icon: always visible; generates on demand if needed -->
          <SentenceAudioButton
            target_language_code={sentence.target_language_code}
            sentenceId={sentence.id}
            sentenceSlug={sentence.slug}
            hasAudio={sentence.has_audio}
            supabaseClient={supabase}
            className="ms-2"
            iconSize={18}
          />
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