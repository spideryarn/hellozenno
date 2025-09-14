<script module lang="ts">
  import { defineMeta } from '@storybook/addon-svelte-csf';
  import DataGrid from '$lib/components/DataGrid.svelte';

  const { Story } = defineMeta({
    title: 'Components/DataGrid',
    component: DataGrid,
    tags: ['autodocs']
  });
</script>

<script lang="ts">
  const columns = [
    { id: 'id', header: 'ID', width: 60 },
    { id: 'word', header: 'Word' },
    { id: 'pos', header: 'POS', width: 80 }
  ];

  const rows = Array.from({ length: 10 }).map((_, i) => ({
    id: i + 1,
    word: `word_${i + 1}`,
    pos: 'noun'
  }));

  function getRowUrl(row: any) {
    return `#/items/${row.id}`;
  }
  
</script>

<Story name="Default No Links" args={{ columns, rows }} />

<Story name="With Hyperlinks" args={{ columns, rows, getRowUrl }} />