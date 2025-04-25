<script lang="ts">
  import DataGrid from '$lib/components/DataGrid.svelte';
  import { Meta, Story, Template } from '@storybook/addon-svelte-csf';

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

<Meta title="Components/DataGrid" component={DataGrid} />

<Template let:args>
  <div style="margin: 1em;">
    <DataGrid {...args} />
  </div>
</Template>

<Story name="Default (No Links)" args={{ columns, rows }} />

<Story name="With Hyperlinks" args={{ columns, rows, getRowUrl }} /> 