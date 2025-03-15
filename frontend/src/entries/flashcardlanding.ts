import FlashcardLanding from "../components/FlashcardLanding.svelte";
import type { SvelteComponent } from "svelte";

// Export the component directly
export { FlashcardLanding };

// Export the mount function as default
export default function (target: HTMLElement, props: any): SvelteComponent {
    return new FlashcardLanding({
        target,
        props,
    });
}