<script lang="ts">
    export let phrase: string;
    export let translations: string[] = [];
    export let slug: string;
    export let part_of_speech: string | null = null;
    export let notes: string | null = null;
    export let language_code: string;
</script>

<a href={`/language/${language_code}/phrase/${slug}`} class="text-decoration-none">
    <div class="hz-phrase-item">
        <h3 class="mb-2">
            <span class="hz-foreign-text">{phrase}</span>
            {#if part_of_speech}
                <small class="text-muted ms-2">({part_of_speech})</small>
            {/if}
        </h3>
        {#if translations && translations.length > 0}
            <p class="text-secondary translations">{translations.join('; ')}</p>
        {/if}
        {#if notes}
            <div class="mt-2 notes">
                <small class="text-muted">{notes}</small>
            </div>
        {/if}
    </div>
</a>

<style>
    .hz-phrase-item {
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background-color: rgba(18, 18, 18, 0.4);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .hz-phrase-item:hover {
        border-color: var(--bs-primary);
        background-color: rgba(18, 18, 18, 0.6);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    h3 {
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
        color: var(--bs-primary);
    }
    
    .hz-foreign-text {
        font-weight: 500;
    }
    
    .translations {
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .notes {
        font-size: 0.875rem;
        color: #999;
        line-height: 1.4;
    }
    
    p {
        margin-bottom: 0;
    }
</style> 