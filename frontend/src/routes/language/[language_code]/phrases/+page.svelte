<script lang="ts">
    import { PhraseCard } from '$lib';
    import type { Phrase } from '$lib/types';
    import { page } from '$app/state';
    
    export let data: {
        phrases: Phrase[],
        language_name: string,
        language_code: string
    };
</script>

<svelte:head>
    <title>{data.language_name} phrases and idioms - Hello Zenno</title>
</svelte:head>

<div class="container my-5">
    <h1 class="mb-4">{data.language_name} phrases and idioms <span class="text-muted">({data.phrases?.length || 0})</span></h1>

    <div class="sort-options mb-4">
        <a href="{`/language/${data.language_code}/phrases?sort=alpha`}" class="sort-link me-3 {page.url.searchParams.get('sort') === 'alpha' || !page.url.searchParams.get('sort') ? 'active' : ''}">
            Sort alphabetically
        </a>
        <a href="{`/language/${data.language_code}/phrases?sort=date`}" class="sort-link {page.url.searchParams.get('sort') === 'date' ? 'active' : ''}">
            Sort by date
        </a>
    </div>

    {#if data.phrases?.length > 0}
        <div class="phrases-list">
            {#each data.phrases as phrase}
                <div class="phrase-item mb-4">
                    <PhraseCard 
                        phrase={phrase.canonical_form} 
                        translations={phrase.translations} 
                        slug={phrase.slug}
                        part_of_speech={phrase.part_of_speech}
                        notes={phrase.usage_notes}
                        language_code={data.language_code}
                    />
                </div>
            {/each}
        </div>
    {:else}
        <div class="alert alert-info">No phrases available</div>
    {/if}
</div>

<style>
    .sort-link {
        text-decoration: none;
        padding: 0.5em 0.8em;
        border-radius: 4px;
        color: var(--bs-secondary);
        transition: all 0.2s ease;
    }
    
    .sort-link:hover {
        background-color: rgba(76, 173, 83, 0.1);
    }
    
    .sort-link.active {
        font-weight: bold;
        color: var(--bs-primary);
        background-color: rgba(76, 173, 83, 0.15);
    }
    
    .phrases-list {
        display: grid;
        gap: 1.5rem;
    }
    
    .phrase-item {
        transition: transform 0.2s ease;
    }
    
    .phrase-item:hover {
        transform: translateY(-2px);
    }
    
    @media (min-width: 768px) {
        .phrases-list {
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
        }
    }
</style> 