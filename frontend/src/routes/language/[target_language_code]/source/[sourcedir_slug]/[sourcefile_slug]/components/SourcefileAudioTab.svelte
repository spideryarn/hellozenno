<script lang="ts">
  import { SourcefileAudio } from '$lib';
  
  export let audioUrl: string;
  export let downloadUrl: string;
  export let filename: string = '';
</script>

<SourcefileAudio {audioUrl} {downloadUrl} {filename} />