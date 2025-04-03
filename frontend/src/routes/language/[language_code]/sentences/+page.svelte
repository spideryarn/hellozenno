<script lang="ts">
    import type { PageData } from './$types';
    import SentenceCard from '$lib/components/SentenceCard.svelte';
    
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
                    <SentenceCard 
                        text={sentence.text}
                        translation={sentence.translation}
                        slug={sentence.slug}
                        lemma_words={sentence.lemma_words || []}
                        language_code={language_code}
                    />
                </div>
            {/each}
        </div>
    {:else}
        <div class="alert alert-info">
            No sentences found for {language_name}. Start by adding sources!
        </div>
    {/if}
</div> 