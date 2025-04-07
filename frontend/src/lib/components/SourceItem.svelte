<script lang="ts">
  import { RouteName, resolveRoute } from '$lib/generated/routes';
  
  export let name: string = '';
  export let displayName: string = '';
  export let slug: string = '';
  export let languageCode: string = '';
  export let description: string = '';
  export let statistics = { file_count: 0, sentence_count: 0 };
  export let className: string = '';
  
  // Generate typed route for navigation
  const sourceUrl = resolveRoute(RouteName.SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW, {
    target_language_code: languageCode,
    sourcedir_slug: slug
  });
</script>

<div class="list-group-item hz-language-item hz-source-item mb-3 {className}">
  <div class="d-flex flex-column">
    <div class="mb-2">
      <h3 class="mb-0">
        <a href={sourceUrl} class="text-decoration-none">
          {displayName || name}
        </a>
      </h3>
    </div>
    <div class="text-secondary small mb-2 source-stats">
      <span class="me-3">{statistics.file_count} files</span>
      {#if statistics.sentence_count}
        <span>{statistics.sentence_count} sentences</span>
      {/if}
    </div>
    {#if description}
      <div class="small source-description">
        <!-- Keep descriptions short in listing pages to avoid overwhelming the UI -->
        {description.length > 100 ? description.substring(0, 100) + '...' : description}
      </div>
    {/if}
  </div>
</div> 