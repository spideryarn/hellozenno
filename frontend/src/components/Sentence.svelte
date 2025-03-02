<!-- Sentence.svelte -->
<script lang="ts">
  import type { SentenceProps } from '../lib/types';

  export let sentence: SentenceProps['sentence'];
  export let metadata: SentenceProps['metadata'];
  export let enhanced_sentence_text: SentenceProps['enhanced_sentence_text'];
  
  // State for audio player
  let audioPlayer: HTMLAudioElement;
  let isGeneratingAudio = false;

  // Function to generate audio
  async function generateAudio() {
    if (isGeneratingAudio) return;
    
    isGeneratingAudio = true;
    try {
      const response = await fetch(
        `/api/sentence/${sentence.language_code}/${sentence.slug}/generate_audio`,
        { method: 'POST' }
      );
      
      if (!response.ok) throw new Error('Failed to generate audio');
      
      // Reload the page to show the new audio player
      window.location.reload();
    } catch (error) {
      console.error('Error generating audio:', error);
    } finally {
      isGeneratingAudio = false;
    }
  }

  // Function to set playback rate
  function setPlaybackRate(rate: number) {
    if (audioPlayer) {
      audioPlayer.playbackRate = rate;
    }
  }
</script>

<div class="container mx-auto px-4 py-6">
  <!-- Metadata -->
  {#if metadata}
    <div class="text-sm text-gray-600 mb-4">
      <p>Created: <span>{metadata.created_at ? new Date(metadata.created_at).toLocaleString() : 'N/A'}</span></p>
      <p>Updated: <span>{metadata.updated_at ? new Date(metadata.updated_at).toLocaleString() : 'N/A'}</span></p>
    </div>
  {/if}

  <!-- Sentence Content -->
  <div class="space-y-4">
    <div class="text-xl leading-relaxed">
      {@html enhanced_sentence_text}
    </div>
    
    {#if sentence.translation}
      <div class="text-gray-600 italic">
        {sentence.translation}
      </div>
    {/if}

    <!-- Audio Section -->
    {#if sentence.has_audio}
      <div class="mt-4">
        <audio
          bind:this={audioPlayer}
          controls
          src="/api/{sentence.language_code}/sentences/{sentence.id}/audio"
        >
          Your browser does not support the audio element.
        </audio>
        
        <div class="flex gap-2 mt-2">
          <button
            class="px-2 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
            on:click={() => setPlaybackRate(0.8)}>0.8x</button>
          <button
            class="px-2 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
            on:click={() => setPlaybackRate(1.0)}>1.0x</button>
          <button
            class="px-2 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300"
            on:click={() => setPlaybackRate(1.5)}>1.5x</button>
        </div>
      </div>
    {:else}
      <button
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-blue-300"
        on:click={generateAudio}
        disabled={isGeneratingAudio}
      >
        {isGeneratingAudio ? 'Generating...' : 'Generate audio'}
      </button>
    {/if}
  </div>
</div> 