import FlashcardApp from "../components/FlashcardApp.svelte";
import type { SvelteComponent } from "svelte";

// Export the component directly
export { FlashcardApp };

// Export the mount function as default
export default function (target: HTMLElement, props: any): SvelteComponent {
    return new FlashcardApp({
        target,
        props,
    });
}