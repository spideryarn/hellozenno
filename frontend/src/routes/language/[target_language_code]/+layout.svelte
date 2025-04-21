<script lang="ts">
    import { page } from '$app/stores';
    import { SITE_NAME } from '$lib/config';
    import { SearchBarMini } from '$lib';
</script>

<svelte:head>
    <title>{$page.data?.language_name || ''} | {SITE_NAME}</title>
</svelte:head>

<div class="container mt-2 mb-3">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2">
        <div class="breadcrumbs">
            <a href="/" class="text-decoration-none">Home</a>
            » <a href="/languages" class="text-decoration-none">Languages</a>
            {#if $page.data?.target_language_code && $page.data?.language_name} 
                » <a href={`/language/${$page.data.target_language_code}/sources`} class="text-decoration-none">{$page.data.language_name}</a>
            {/if}
        </div>
        
        {#if $page.data?.target_language_code && $page.data?.language_name && !$page.url.pathname.includes('/search')}
            <SearchBarMini 
                languageName={$page.data.language_name}
                targetLanguageCode={$page.data.target_language_code}
            />
        {/if}
    </div>
</div>

<div class="container">
    <slot></slot>
</div> 