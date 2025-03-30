import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { get_language_name } from "$lib/utils";
import { getPhrasesForLanguage } from "$lib/api";

export const load: PageServerLoad = async ({ params, url }) => {
    const { language_code } = params;
    const sort = url.searchParams.get("sort") || "alpha";

    try {
        // Fetch phrases using the API helper
        const phrases = await getPhrasesForLanguage(language_code, sort);

        // Get language name
        const language_name = await get_language_name(language_code);

        return {
            phrases,
            language_code,
            language_name,
            current_sort: sort,
        };
    } catch (err) {
        console.error("Error loading phrases:", err);
        throw error(500, "Failed to load phrases data");
    }
};
