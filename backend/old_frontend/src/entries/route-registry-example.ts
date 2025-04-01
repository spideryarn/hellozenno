/**
 * Entry point for the route registry example component.
 * 
 * This demonstrates how to use the TypeScript route registry for type-safe URL resolution.
 */
import RouteRegistryExample from '../examples/RouteRegistryExample.svelte';

// Get container element for mounting the component
const container = document.getElementById('route-registry-example');

// Check if container exists
if (!container) {
  console.error('Container element #route-registry-example not found');
} else {
  // Get data attributes from the container
  const wordform = container.getAttribute('data-wordform') || '';
  const targetLanguageCode = container.getAttribute('data-target-language-code') || '';

  // Create and mount the component with props
  const app = new RouteRegistryExample({
    target: container,
    props: {
      wordform,
      target_language_code: targetLanguageCode
    }
  });
  
  console.log('Route registry example component mounted:', { wordform, targetLanguageCode });
}