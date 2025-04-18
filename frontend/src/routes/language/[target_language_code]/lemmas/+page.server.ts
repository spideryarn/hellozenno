import { error } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { get_language_name } from "$lib/utils";
import { getLemmasForLanguage } from "$lib/api";

export const load: PageServerLoad = async ({ params, url }) => {
    const { target_language_code } = params;
    const sort = url.searchParams.get("sort") || "alpha";

    try {
        // Fetch lemmas using the API helper
        const lemmas = await getLemmasForLanguage(target_language_code, sort);

        // Get language name
        const language_name = await get_language_name(target_language_code);

        return {
            lemmas,
            target_language_code,
            language_name,
            current_sort: sort,
        };
    } catch (err) {
        console.error("Error loading lemmas:", err);
        throw error(500, "Failed to load lemmas data");
    }
};
