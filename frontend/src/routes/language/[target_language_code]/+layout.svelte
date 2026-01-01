<script lang="ts">
    import { page } from '$app/stores';
    import { SITE_NAME } from '$lib/config';
    import { SearchBarMini } from '$lib';
</script>

<svelte:head>
    <title>{$page.data?.language_name || ''} | {SITE_NAME}</title>
</svelte:head>

{#if $page.data?.target_language_code && $page.data?.language_name && !$page.url.pathname.includes('/search')}
    <div class="container mt-2 mb-3">
        <div class="d-flex justify-content-end">
            <SearchBarMini 
                languageName={$page.data.language_name}
                targetLanguageCode={$page.data.target_language_code}
            />
        </div>
    </div>
{/if}

<div class="container">
    <slot></slot>
</div>