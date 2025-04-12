<script lang="ts">
    import { page } from '$app/state';
    import { goto } from '$app/navigation';
    
    let searchQuery = '';
    
    function handleSearch(event: MouseEvent) {
        if (!searchQuery.trim()) return;
        
        const url = `/language/${page.data.target_language_code}/search?q=${encodeURIComponent(searchQuery)}`;
        
        // Open in new tab when Cmd (Mac) or Ctrl (Windows/Linux) is pressed
        if (event.metaKey || event.ctrlKey) {
            window.open(url, '_blank');
        } else {
            goto(url);
        }
    }
</script>

<div class="container mt-2 mb-3">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2">
        <div class="breadcrumbs">
            <a href="/" class="text-decoration-none">Home</a>
            » <a href="/languages" class="text-decoration-none">Languages</a>
            {#if page.data.target_language_code && page.data.language_name}
                » <a href="/language/{page.data.target_language_code}/sources" class="text-decoration-none">{page.data.language_name}</a>
            {/if}
        </div>
        
        {#if page.data.target_language_code && page.data.language_name}
            <div class="search-box">
                <div class="d-flex" id="top-search-form">
                    <input 
                        type="text" 
                        placeholder="Search {page.data.language_name} words..." 
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