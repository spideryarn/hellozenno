import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getPhrasesForLanguage } from "$lib/api";
import { get_language_name } from "$lib/utils";

export const load: PageServerLoad = async ({ params, url }) => {
    const { target_language_code } = params;
    const sort = url.searchParams.get("sort") || "alpha";

    try {
        // Fetch the phrases for the language
        const phrases = await getPhrasesForLanguage(target_language_code, sort);

        // Get language name
        const language_name = await get_language_name(target_language_code);

        return {
            phrases,
            language_name,
            target_language_code,
            current_sort: sort,
        };
    } catch (err) {
        console.error("Error loading phrases data:", err);
        throw error(500, {
            message: "Failed to load phrases data",
        });
    }
};
