import { error } from "@sveltejs/kit";
import type { PageLoad } from "./$types";
import { get_api_url } from "$lib/utils";

export const load: PageLoad = async ({ params, fetch }) => {
    const { language_code, slug } = params;

    try {
        const response = await fetch(
            get_api_url(`lang/phrase/${language_code}/detail/${slug}`),
        );

        if (!response.ok) {
            const errorData = await response.json();
            throw error(
                response.status,
                errorData.description ||
                    `Failed to load phrase with slug "${slug}"`,
            );
        }

        const phraseData = await response.json();

        return {
            phrase: phraseData,
            language_code,
        };
    } catch (err) {
        console.error("Error in load function:", err);
        throw error(500, "Failed to load phrase data");
    }
};
