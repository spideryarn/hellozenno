<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { PencilSimple, Trash } from 'phosphor-svelte';

  const dispatch = createEventDispatcher();

  function handleRename() {
    dispatch('rename');
  }

  function handleDelete() {
    dispatch('delete');
  }
</script>

<div class="operations-section">
  <h3 class="section-title">Directory Operations</h3>
  <div class="button-group">
    <button on:click={handleRename} class="button is-small is-light">
      <PencilSimple size={16} />
      <span>Rename Directory</span>
    </button>
    <button on:click={handleDelete} class="button is-small is-danger is-light">
      <Trash size={16} />
      <span>Delete Directory</span>
    </button>
  </div>
</div>

<style>
  .operations-section {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 0.75rem;
    margin-top: 0.75rem;
  }

  .section-title {
    font-size: 0.85rem;
    color: #adb5bd;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
  }

  .button-group {
    display: flex;
    gap: 0.5rem;
  }

  .button {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.4rem 0.8rem; /* Slightly smaller padding for is-small */
    border-radius: 4px;
    text-decoration: none;
    border: 1px solid transparent;
    cursor: pointer;
    font-size: 0.9rem; /* Adjust font size if needed */
  }

  .button.is-light {
    background-color: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: #f8f9fa;
  }
  .button.is-light:hover {
    background-color: rgba(255, 255, 255, 0.15);
  }

  .button.is-danger.is-light {
    background-color: rgba(220, 53, 69, 0.1); /* Bootstrap danger color with alpha */
    border-color: rgba(220, 53, 69, 0.3);
    color: #dc3545; /* Bootstrap danger color */
  }

  .button.is-danger.is-light:hover {
    background-color: rgba(220, 53, 69, 0.2);
    color: #f8f9fa; /* White text on hover */
  }
</style> 