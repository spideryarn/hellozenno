import MiniWordform from '../components/MiniWordform.svelte';
export { MiniWordform };
export default function(target: HTMLElement, props: any) {
  return new MiniWordform({ target, props });
} 