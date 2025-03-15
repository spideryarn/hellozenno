import MiniPhrase from '../components/MiniPhrase.svelte';
export { MiniPhrase };
export default function(target: HTMLElement, props: any) {
  return new MiniPhrase({ target, props });
}