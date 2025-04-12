<script lang="ts">
    import { RouteName, resolveRoute } from '$lib/generated/routes';
    
    export let wordform: string;
    export let translations: string[] = [];
    export let part_of_speech: string | undefined = undefined;
    export let lemma: string | undefined = undefined;
    export let target_language_code: string;

    // Generate typed routes for navigation
    const wordformUrl = resolveRoute(RouteName.WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW, {
        target_language_code: target_language_code,
        wordform
    });
    
    function navigateToLemma() {
        if (lemma) {
            const lemmaUrl = resolveRoute(RouteName.LEMMA_VIEWS_GET_LEMMA_METADATA_VW, {
                target_language_code: target_language_code,
                lemma
            });
            window.location.href = lemmaUrl;
        }
    }
</script>

<a href={wordformUrl} class="text-decoration-none">
    <div class="hz-wordform-item">
        <h3 class="mb-2">
            <span class="hz-foreign-text">{wordform}</span>
            {#if part_of_speech}
                <small class="text-muted ms-2">({part_of_speech})</small>
            {/if}
        </h3>
        {#if translations && translations.length > 0}
            <p class="text-secondary">{translations.join(', ')}</p>
        {/if}
        {#if lemma && lemma !== wordform}
            <div class="mt-2">
                <small class="text-muted">
                    Lemma: <button type="button" class="hz-lemma-link" on:click|preventDefault={navigateToLemma} on:keydown={(e) => e.key === 'Enter' && navigateToLemma()}>{lemma}</button>
                </small>
            </div>
        {/if}
    </div>
</a>

<style>
    .hz-wordform-item {
        padding: 1rem;
        border-radius: 0.5rem;
        transition: all 0.2s ease;
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    .hz-wordform-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    h3 {
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }
    
    p {
        margin-bottom: 0;
    }
    
    .hz-lemma-link {
        text-decoration: underline;
        color: var(--bs-primary, #4CAD53);
        cursor: pointer;
        transition: color 0.2s ease;
        background: none;
        border: none;
        padding: 0;
        font: inherit;
        display: inline;
    }
    
    .hz-lemma-link:hover {
        color: var(--bs-success, #28a745);
    }
</style> 