<script lang="ts">
    import { RouteName, resolveRoute } from '$lib/generated/routes';
    
    export let text: string;
    export let translation: string;
    export let slug: string;
    export let lemma_words: string[] = [];
    export let target_language_code: string;
    
    // Generate typed route for navigation
    const sentenceUrl = resolveRoute(RouteName.SENTENCE_VIEWS_GET_SENTENCE_VW, {
        target_language_code: target_language_code,
        slug
    });
</script>

<a href={sentenceUrl} class="text-decoration-none">
    <div class="hz-sentence-item">
        <h3 class="mb-2">
            <span class="hz-foreign-text">{text}</span>
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
</style> 