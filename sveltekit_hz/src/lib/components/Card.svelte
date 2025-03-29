<script lang="ts">
  export let title: string = '';
  export let subtitle: string = '';
  export let href: string = '';
  export let className: string = '';
</script>

<a {href} class="text-decoration-none">
  <div class="card h-100 hz-language-item {className}">
    <div class="card-body text-center">
      {#if title}
        <h2 class="card-title">{title}</h2>
      {/if}
      {#if subtitle}
        <p class="hz-language-code">({subtitle})</p>
      {/if}
      <slot />
    </div>
  </div>
</a> 