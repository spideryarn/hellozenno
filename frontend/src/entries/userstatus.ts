import UserStatus from '../components/UserStatus.svelte';

export default function(target: HTMLElement, props: any) {
  return new UserStatus({ target, props });
}

export { UserStatus };