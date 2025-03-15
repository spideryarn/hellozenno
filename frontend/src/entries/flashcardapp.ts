import FlashcardApp from "../components/FlashcardApp.svelte";
import FlashcardLanding from "../components/FlashcardLanding.svelte";
import type { SvelteComponent } from "svelte";

// Export the components directly
export { FlashcardApp, FlashcardLanding };

// Export the mount function as default
export default function (target: HTMLElement, props: any): SvelteComponent {
    // Determine which component to render based on the target element's ID
    const targetId = target.id;
    
    if (targetId === 'flashcard-landing') {
        return new FlashcardLanding({
            target,
            props,
        });
    } else if (targetId === 'flashcard-app') {
        return new FlashcardApp({
            target,
            props,
        });
    } else {
        console.error(`Unknown target ID: ${targetId}`);
        throw new Error(`Unknown target ID: ${targetId}`);
    }
}