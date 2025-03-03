import MiniSentence from '../components/MiniSentence.svelte';
import type { SvelteComponent } from 'svelte';

// Export the component directly
export { MiniSentence };

// Export the mount function as default
export default function(target: HTMLElement, props: any): SvelteComponent {
  return new MiniSentence({
    target,
    props
  });
} 