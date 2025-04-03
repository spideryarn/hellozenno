<script lang="ts">
    import type { PageData } from './$types';
    import { WordformCard } from '$lib';
    
    export let data: PageData;
    
    // Destructure data for easier access
    const { language_code, language_name, wordforms } = data;
</script>

<svelte:head>
    <title>Wordforms - {language_name}</title>
</svelte:head>

<div class="container mt-4">
    <div class="row mb-4">
        <div class="col">
            <h1 class="mb-3">Wordforms in {language_name}</h1>
            <p class="d-flex gap-2">
                <a href="/language/{language_code}/sources" class="btn btn-outline-primary">
                    Browse {language_name} Sources
                </a>
                <a href="/language/{language_code}/sentences" class="btn btn-outline-secondary">
                    View {language_name} Sentences
                </a>
            </p>
        </div>
    </div>
    
    {#if wordforms.length > 0}
        <div class="row">
            <div class="col">
                <p class="text-muted mb-3">Showing {wordforms.length} wordforms</p>
            </div>
        </div>
        <div class="row gy-4">
            {#each wordforms as wordform (wordform.wordform)}
                <div class="col-12">
                    <WordformCard 
                        wordform={wordform.wordform}
                        translations={wordform.translations || []}
                        part_of_speech={wordform.part_of_speech}
                        lemma={wordform.lemma}
                        language_code={language_code}
                    />
                </div>
            {/each}
        </div>
    {:else}
        <div class="alert alert-info">
            No wordforms found for {language_name}. Start by adding sources!
        </div>
    {/if}
</div> 