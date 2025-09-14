<script module lang="ts">
  import { defineMeta } from '@storybook/addon-svelte-csf';
  import DataGridComponent from '$lib/components/DataGrid.svelte';
  
  const { Story } = defineMeta({
    title: 'Components/DataGrid',
    component: DataGridComponent
  });
</script>

<script lang="ts">
  import DataGrid from '$lib/components/DataGrid.svelte';

  const columns = [
    { id: 'id', header: 'ID', width: 60 },
    { id: 'word', header: 'Word' },
    { id: 'pos', header: 'POS', width: 80 },
  ];

  const rows = Array.from({ length: 10 }).map((_, i) => ({ id: i + 1, word: `word_${i + 1}`, pos: 'noun' }));
  
  // URL generator function for hyperlink mode
  function getRowUrl(row: any) {
    return `#/items/${row.id}`;
  }
</script>

<!-- Disabled meta/template to avoid svelte-check errors in disabled story -->

<Story name="Default (No Links)" args={{ columns, rows }} />

<Story name="With Hyperlinks" args={{ columns, rows, getRowUrl }} /> 