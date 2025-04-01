import MiniWordformList from '../components/MiniWordformList.svelte';
export { MiniWordformList };
export default function(target: HTMLElement, props: any) {
  return new MiniWordformList({ target, props });
}