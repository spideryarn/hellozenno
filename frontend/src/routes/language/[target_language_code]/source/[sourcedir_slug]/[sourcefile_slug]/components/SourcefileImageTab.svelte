<script lang="ts">
  import { SourcefileImage } from '$lib';
  
  export let viewUrl: string;
  export let downloadUrl: string;
  export let filename: string = '';
</script>

<SourcefileImage {viewUrl} {downloadUrl} altText={filename} />