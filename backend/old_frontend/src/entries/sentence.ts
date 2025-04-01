import SentenceComponent from '../components/Sentence.svelte';

// Export the Svelte component
export { SentenceComponent as Sentence };

// Add default export for dynamic imports
export default function(target: HTMLElement, props: any) {
  return new SentenceComponent({ target, props });
}