<script lang="ts">
	export let type: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark' = 'info';
</script>

<div class={`alert alert-${type}`} role="alert">
	<slot />
</div> 