<script lang="ts">
	// Support for size variants and custom styling using the new runes syntax
	let { size = undefined, style = '', className = '' }: { 
		size?: 'sm' | 'md' | 'lg', 
		style?: string,
		className?: string 
	} = $props();
	
	// Determine size based on the size prop using the new runes syntax
	const sizeClass = $derived(
		size === 'sm' ? 'spinner-sm' : 
		size === 'lg' ? 'spinner-lg' : ''
	);
</script>

<style>
	.spinner-svg {
		/* Apply animation to the SVG element */
		animation: spin 2s linear infinite;

		/* Set default size - can be overridden by parent or props */
		width: 36px;
		height: 36px;

		/* Ensure the color defaults to the text color or a specific var */
		color: var(--spinner-color, currentColor);
	}
	
	/* Size variants */
	.spinner-sm {
		width: 16px;
		height: 16px;
	}
	
	.spinner-lg {
		width: 48px;
		height: 48px;
	}

	/* Keep the keyframes */
	@keyframes spin {
		0% {
			transform: rotate(0deg);
		}
		100% {
			transform: rotate(360deg);
		}
	}
</style>

<!-- Phosphor Spinner SVG -->
<svg
	xmlns="http://www.w3.org/2000/svg"
	width="1em"
	height="1em"
	fill="currentColor"
	viewBox="0 0 256 256"
	class="spinner-svg {sizeClass} {className}"
	role="status"
	aria-live="polite"
	aria-label="Loading..."
	{style}
>
	<rect width="256" height="256" fill="none"></rect>
	<line
		x1="128"
		y1="32"
		x2="128"
		y2="64"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="24"
	></line>
	<line
		x1="195.9"
		y1="60.1"
		x2="173.3"
		y2="82.7"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="24"
	></line>
	<line
		x1="224"
		y1="128"
		x2="192"
		y2="128"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="24"
	></line>
	<line
		x1="195.9"
		y1="195.9"
		x2="173.3"
		y2="173.3"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="24"
	></line>
	<line
		x1="128"
		y1="224"
		x2="128"
		y2="192"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="24"
	></line>
	<line
		x1="60.1"
		y1="195.9"
		x2="82.7"
		y2="173.3"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="24"
	></line>
	<line
		x1="32"
		y1="128"
		x2="64"
		y2="128"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="24"
	></line>
	<line
		x1="60.1"
		y1="60.1"
		x2="82.7"
		y2="82.7"
		stroke="currentColor"
		stroke-linecap="round"
		stroke-linejoin="round"
		stroke-width="24"
	></line>
	<!-- Removed the visually-hidden span as aria-label handles accessibility -->
</svg> 