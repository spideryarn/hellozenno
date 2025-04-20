<script lang="ts">
	import LoadingSpinner from '$lib/components/LoadingSpinner.svelte';
</script>

<h1>Spinner Experiment</h1>

<p>This page displays the LoadingSpinner component for debugging:</p>

<div style="margin: 20px; font-size: 48px;">
	<LoadingSpinner />
</div>

<p>Testing with primary color:</p>
<div style="margin: 20px; font-size: 48px; color: var(--bs-primary);">
	<LoadingSpinner />
</div>

<p>Testing with danger color:</p>
<div style="margin: 20px; font-size: 48px; color: var(--bs-danger);">
	<LoadingSpinner />
</div> 