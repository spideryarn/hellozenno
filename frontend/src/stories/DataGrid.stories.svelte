<script lang="ts">
  import DataGrid from '$lib/components/DataGrid.svelte';

  const columns = [
    { id: 'id', header: 'ID', width: 60 },
    { id: 'word', header: 'Word' },
    { id: 'pos', header: 'POS', width: 80 },
  ];

  const rows = Array.from({ length: 10 }).map((_, i) => ({ id: i + 1, word: `word_${i + 1}`, pos: 'noun' }));

  /** @param {CustomEvent<any>} e */
  function handleRowClick(e: CustomEvent<any>) {
    // eslint-disable-next-line no-console
    console.log('rowClick', e.detail);
  }
</script>

<DataGrid {columns} {rows} on:rowClick={handleRowClick} /> 