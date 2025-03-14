import ExperimCounter from "../components/ExperimCounter.svelte";
import type { SvelteComponent } from "svelte";

// Export the component directly
export { ExperimCounter };

// Export the mount function as default
export default function (target: HTMLElement, props: any): SvelteComponent {
    return new ExperimCounter({
        target,
        props,
    });
}
