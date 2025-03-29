import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";

export const load: PageServerLoad = async ({ fetch }) => {
    try {
        // In server-side code, we need to use the full URL
        const response = await fetch("http://localhost:3000/api/languages");

        if (!response.ok) {
            throw new Error(
                `API returned ${response.status}: ${response.statusText}`,
            );
        }

        const data = await response.json();

        return {
            languages: data.languages,
        };
    } catch (err) {
        console.error("Failed to load languages:", err);
        throw error(500, "Failed to load languages");
    }
};
