<script lang="ts">
    import { page } from '$app/state';
</script>

<div class="container mt-2 mb-3">
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2">
        <div class="breadcrumbs">
            <a href="/" class="text-decoration-none">Home</a>
            » <a href="/languages" class="text-decoration-none">Languages</a>
            {#if page.data.language_code && page.data.language_name}
                » <a href="/language/{page.data.language_code}/sources" class="text-decoration-none">{page.data.language_name}</a>
            {/if}
        </div>
        
        {#if page.data.language_code && page.data.language_name}
            <div class="search-box">
                <form method="GET" action="/language/{page.data.language_code}/search" class="d-flex">
                    <input 
                        type="text" 
                        name="q" 
                        placeholder="Search {page.data.language_name} words..." 
                        required
                        class="form-control me-2"
                    >
                    <button type="submit" class="btn btn-primary">Search</button>
                </form>
            </div>
        {/if}
    </div>
</div>

<div class="container">
    <slot></slot>
</div> 