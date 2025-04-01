import AuthPage from '../components/AuthPage.svelte';

export default function(target: HTMLElement, props: any) {
  return new AuthPage({ target, props });
}

export { AuthPage };