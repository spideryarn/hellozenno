<script lang="ts">
    export let text: string;
    export let translation: string;
    export let slug: string;
    export let lemma_words: string[] = [];
    export let language_code: string;
</script>

<a href={`/language/${language_code}/sentence/${slug}`} class="text-decoration-none">
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