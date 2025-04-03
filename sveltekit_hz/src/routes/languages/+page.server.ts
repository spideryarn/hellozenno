import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { getApiUrl } from "$lib/api";
import { RouteName } from "$lib/generated/routes";

export const load: PageServerLoad = async ({ fetch }) => {
    try {
        // Use the type-safe getApiUrl function instead of hardcoded URL
        const url = getApiUrl(RouteName.LANGUAGES_API_GET_LANGUAGES_API, {});
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(
                `API returned ${response.status}: ${response.statusText}`,
            );
        }

        const data = await response.json();

        return {
            languages: data,
        };
    } catch (err) {
        console.error("Failed to load languages:", err);
        throw error(500, "Failed to load languages");
    }
};
