<script lang="ts">
  // Component props
  export let name: string = "World";
  
  // Reactive state
  let count: number = 0;
  
  // Methods
  function incrementCount(): void {
    count += 1;
  }
</script>

<div class="tw-p-4 tw-bg-white tw-rounded-lg tw-shadow">
  <h3 class="tw-text-xl tw-font-bold tw-mb-2">Hello, {name}!</h3>
  
  <p class="tw-mb-4">
    This is a Svelte component with TypeScript and Tailwind CSS.
  </p>
  
  <div class="tw-flex tw-items-center tw-gap-4">
    <button 
      on:click={incrementCount}
      class="tw-btn"
    >
      Count: {count}
    </button>
    
    <span class="tw-text-sm tw-text-gray-600">
      Click the button to increment the counter
    </span>
  </div>
</div>

<style>
  /* Component-specific styles that don't use Tailwind */
  /* These styles are scoped to this component only */
</style> 