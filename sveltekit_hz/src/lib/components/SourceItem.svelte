<script lang="ts">
  export let name: string = '';
  export let displayName: string = '';
  export let slug: string = '';
  export let languageCode: string = '';
  export let description: string = '';
  export let statistics = { file_count: 0, sentence_count: 0 };
</script>

<div class="list-group-item hz-language-item hz-source-item mb-3">
  <div class="d-flex flex-column">
    <div class="mb-2">
      <h3 class="mb-0">
        <a href="/language/{languageCode}/source/{slug}" class="text-decoration-none">
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
        {description}
      </div>
    {/if}
  </div>
</div> 