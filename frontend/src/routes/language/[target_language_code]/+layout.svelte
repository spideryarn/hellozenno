<script lang="ts">
    import { page } from '$app/stores'; // Use $app/stores now
    import { goto } from '$app/navigation';
    import { SITE_NAME } from '$lib/config';

    let searchQuery = '';
    
    function handleSearch(event: MouseEvent | KeyboardEvent) { // Accept both event types
        if (!searchQuery.trim()) return;
        
        // Check page.data exists before accessing properties
        const target_language_code = $page.data?.target_language_code;
        if (!target_language_code) {
            console.error('Target language code not found in page data');
            return; // Exit if language code is missing
        }
        
        const url = `/language/${target_language_code}/search?q=${encodeURIComponent(searchQuery)}`;
        
        // Check event type for metaKey/ctrlKey (only on MouseEvent or KeyboardEvent)
        if ('metaKey' in event && (event.metaKey || event.ctrlKey)) {
            window.open(url, '_blank');
        } else {
            goto(url);
        }
    }
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
        
        {#if $page.data?.target_language_code && $page.data?.language_name}
            <div class="search-box">
                <div class="d-flex" id="top-search-form">
                    <input 
                        type="text" 
                        placeholder={`Search ${$page.data.language_name} words...`} 
                        required
                        class="form-control me-2"
                        id="top-search-input"
                        bind:value={searchQuery}
                        on:keydown={(e) => {
                            if (e.key === 'Enter') {
                                e.preventDefault();
                                handleSearch(e);
                            }
                        }}
                    >
                    <button 
                        class="btn btn-primary"
                        on:click={(event) => handleSearch(event)}
                    >Search</button>
                </div>
            </div>
        {/if}
    </div>
</div>

<div class="container">
    <slot></slot>
</div> 