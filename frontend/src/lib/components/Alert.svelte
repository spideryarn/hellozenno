<script lang="ts">
	export let type: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info' | 'light' | 'dark' = 'info';
	export let className = '';
</script>

<div class={`alert alert-${type} ${className}`} role="alert">
	<slot />
</div> 