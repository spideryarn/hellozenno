<script lang="ts">
    import { RouteName, resolveRoute } from '$lib/generated/routes';
    import SentenceAudioButton from './SentenceAudioButton.svelte';
    import { page } from '$app/stores';
    import type { SupabaseClient } from '@supabase/supabase-js';
    
    export let text: string;
    export let translation: string;
    export let slug: string;
    export let lemma_words: string[] = [];
    export let target_language_code: string;
    export let supabaseClient: SupabaseClient | null = null;
    
    // Generate typed route for navigation
    const sentenceUrl = resolveRoute(RouteName.SENTENCE_VIEWS_GET_SENTENCE_VW, {
        target_language_code: target_language_code,
        slug
    });
</script>

<a href={sentenceUrl} class="text-decoration-none">
    <div class="hz-sentence-item card-hover-effect">
        <h3 class="mb-2 d-flex align-items-start gap-2">
            <span class="hz-foreign-text flex-grow-1">{text}</span>
            <SentenceAudioButton
              target_language_code={target_language_code}
              sentenceSlug={slug}
              supabaseClient={supabaseClient}
              className="ms-2"
              iconSize={16}
            />
        </h3>
        <p class="text-secondary">{translation}</p>
        {#if lemma_words && lemma_words.length > 0}
            <div class="mt-2">
                <small class="text-muted">
                    Vocabulary: {lemma_words.join(', ')}
                </small>
            </div>
        {/if}
    </div>
</a>

<style>
    h3 {
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }
    
    p {
        margin-bottom: 0;
    }

    .card-hover-effect:hover {
      background-color: rgba(var(--hz-color-primary-green-rgb, 102, 154, 115), 0.05);
      /* Optional: Add a subtle transition */
      transition: background-color 0.2s ease-in-out;
    }
</style> 