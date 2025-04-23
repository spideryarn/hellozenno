<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import PencilSimple from 'phosphor-svelte/lib/PencilSimple';
  import Trash from 'phosphor-svelte/lib/Trash';

  const dispatch = createEventDispatcher();

  function rename() {
    dispatch('rename');
  }

  function deleteItem() {
    dispatch('delete');
  }
</script>

<div class="directory-operations">
  <h3>Directory Operations</h3>
  <div class="button-group">
    <button on:click={rename} class="btn btn-sm btn-primary">
      <PencilSimple size={16} weight="bold" /> Rename
    </button>
    <button on:click={deleteItem} class="btn btn-sm btn-danger">
      <Trash size={16} weight="bold" /> Delete
    </button>
  </div>
</div>

<style>
  .directory-operations {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--hz-color-border-subtle);
  }

  h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    color: var(--hz-color-text-secondary);
  }

  .button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
  }

  .btn > svg {
    vertical-align: text-bottom;
    margin-right: 0.25rem;
  }
</style> 