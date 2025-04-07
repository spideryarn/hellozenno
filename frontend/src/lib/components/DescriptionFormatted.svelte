<script lang="ts">
  // A component that formats text descriptions with proper line breaks
  // Single line breaks (\n) become <br> tags
  // Multiple line breaks (\n\n+) become separate paragraphs
  
  export let description: string = '';
  export let placeholder: string = 'No description available';
  export let cssClass: string = '';
</script>

{#if description}
  <div class={cssClass}>
    {#each description.split(/\n\n+/).map(para => para.trim()) as paragraph, i}
      <p class={i === description.split(/\n\n+/).length - 1 ? "mb-0" : "mb-2"}>
        {#each paragraph.split(/\n/).map(line => line.trim()) as line, j}
          {line}
          {#if j < paragraph.split(/\n/).length - 1}
            <br>
          {/if}
        {/each}
      </p>
    {/each}
  </div>
{:else}
  <p class="text-muted fst-italic mb-0">{placeholder}</p>
{/if}