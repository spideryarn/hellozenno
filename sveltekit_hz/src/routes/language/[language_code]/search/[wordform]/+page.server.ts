import { error, redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { searchWord } from "$lib/api";

export const load: PageServerLoad = async ({ params }) => {
    const { language_code, wordform } = params;

    try {
        // Use the search API to get redirect information
        const data = await searchWord(language_code, wordform);

        // Redirect to the wordform view using the URL returned from the API
        throw redirect(302, data.redirect_url);
    } catch (err) {
        if (err instanceof Response && err.status === 302) {
            // This is our redirect, pass it through
            throw err;
        }

        console.error("Error searching word:", err);
        throw error(500, "Failed to search for word");
    }
};
