<script lang="ts">
    import type { PageData } from './$types';
    import Card from '$lib/components/Card.svelte';
    
    export let data: PageData;
    
    // Destructure data for easier access
    const { language_code, language_name, sentences } = data;
</script>

<svelte:head>
    <title>Sentences - {language_name}</title>
</svelte:head>

<div class="container mt-4">
    <div class="row mb-4">
        <div class="col">
            <h1>Sentences in {language_name}</h1>
            <p>
                <a href="/language/{language_code}/sources" class="btn btn-outline-primary">
                    Browse {language_name} Sources
                </a>
            </p>
        </div>
    </div>
    
    {#if sentences.length > 0}
        <div class="row">
            {#each sentences as sentence (sentence.id)}
                <div class="col-12 mb-3">
                    <Card href={`/language/${language_code}/sentence/${sentence.slug}`}>
                        <div class="sentence-item">
                            <h3 class="mb-2">
                                <span class="text-foreign">{sentence.text}</span>
                            </h3>
                            <p class="text-secondary">{sentence.translation}</p>
                            {#if sentence.lemma_words && sentence.lemma_words.length > 0}
                                <div class="mt-2">
                                    <small class="text-muted">
                                        Vocabulary: {sentence.lemma_words.join(', ')}
                                    </small>
                                </div>
                            {/if}
                        </div>
                    </Card>
                </div>
            {/each}
        </div>
    {:else}
        <div class="alert alert-info">
            No sentences found for {language_name}. Start by adding sources!
        </div>
    {/if}
</div>

<style>
    .text-foreign {
        font-style: italic;
    }
</style> 