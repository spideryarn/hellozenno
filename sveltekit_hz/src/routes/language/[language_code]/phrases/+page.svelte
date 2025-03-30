<script lang="ts">
    import type { PageData } from './$types';
    import { Card } from '$lib';
    
    export let data: PageData;
    
    // Destructure data for easier access
    const { language_code, language_name, phrases, current_sort } = data;
</script>

<svelte:head>
    <title>Phrases - {language_name}</title>
</svelte:head>

<div class="container mt-4">
    <div class="row mb-4">
        <div class="col">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="/">Languages</a></li>
                    <li class="breadcrumb-item"><a href="/language/{language_code}/sources">{language_name}</a></li>
                    <li class="breadcrumb-item active" aria-current="page">Phrases</li>
                </ol>
            </nav>
            
            <h1>Phrases in {language_name}</h1>
            
            <div class="mb-3">
                <a href="/language/{language_code}/sources" class="btn btn-outline-primary me-2">
                    Browse Sources
                </a>
                <a href="/language/{language_code}/lemmas" class="btn btn-outline-primary me-2">
                    Browse Lemmas
                </a>
                <a href="/language/{language_code}/sentences" class="btn btn-outline-primary">
                    Browse Sentences
                </a>
            </div>
            
            <div class="mb-3">
                <div class="btn-group" role="group" aria-label="Sorting options">
                    <a href="?sort=alpha" class="btn btn-outline-secondary {current_sort === 'alpha' ? 'active' : ''}">
                        Sort Alphabetically
                    </a>
                    <a href="?sort=date" class="btn btn-outline-secondary {current_sort === 'date' ? 'active' : ''}">
                        Sort by Date
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    {#if phrases && phrases.length > 0}
        <div class="row">
            {#each phrases as phrase}
                <div class="col-12 col-md-6 col-lg-4 mb-4">
                    <Card>
                        <div class="phrase-card">
                            <h3 class="mb-2">
                                <a href="/language/{language_code}/phrases/{phrase.slug}" class="hz-foreign-text text-decoration-none">
                                    {phrase.canonical_form}
                                </a>
                            </h3>
                            
                            <p>
                                <strong>Translation:</strong> 
                                {#if phrase.translations && phrase.translations.length > 0}
                                    {phrase.translations.join('; ')}
                                {:else}
                                    No translation available
                                {/if}
                            </p>
                            
                            {#if phrase.part_of_speech}
                                <p><strong>Part of Speech:</strong> {phrase.part_of_speech}</p>
                            {/if}
                            
                            {#if phrase.usage_notes}
                                <p><strong>Usage:</strong> {phrase.usage_notes}</p>
                            {/if}
                            
                            {#if phrase.raw_forms && phrase.raw_forms.length > 0}
                                <p><strong>Raw Forms:</strong> {phrase.raw_forms.join(', ')}</p>
                            {/if}
                        </div>
                    </Card>
                </div>
            {/each}
        </div>
    {:else}
        <div class="alert alert-info">
            No phrases found for {language_name}.
        </div>
    {/if}
</div>

<style>
    .hz-foreign-text {
        font-family: 'Times New Roman', Times, serif;
        font-style: italic;
        color: var(--bs-primary);
    }
    
    .phrase-card h3 {
        font-size: 1.4rem;
    }
</style> 