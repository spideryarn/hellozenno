<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { PencilSimple, Trash } from 'phosphor-svelte';

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
    <button on:click={rename} class="button small-button">
      <PencilSimple size={16} weight="bold" /> Rename
    </button>
    <button on:click={deleteItem} class="button delete-button small-button">
      <Trash size={16} weight="bold" /> Delete
    </button>
  </div>
</div>

<style>
  .directory-operations {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  h3 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
  }

  .button-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;
  }

  /* Copied styles from FileOperationsSection */
  .button {
    background-color: #4CAD53;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }

  .small-button {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
  }

  .delete-button {
    background-color: #d9534f;
  }
</style> 