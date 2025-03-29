import type { PageServerLoad } from "./$types";
import { error } from "@sveltejs/kit";
import { get_language_name } from "$lib/utils";

export const load: PageServerLoad = async ({ params, fetch, url }) => {
    const { language_code } = params;

    try {
        // Get sort parameter (default to 'alpha')
        const sort = url.searchParams.get("sort") || "alpha";

        // Fetch language name from API using the provided fetch instance
        const language_name = await get_language_name(language_code, fetch);

        // Since there isn't a dedicated API endpoint for sources,
        // we'll create a simplified version with mock data
        // In a real implementation, we would call a proper API endpoint

        // Mock data for demonstration purposes
        const mockSources = [
            {
                name: "News Articles",
                display_name: "News Articles",
                slug: "news-articles",
                description: "Collection of news articles in " + language_name,
                statistics: {
                    file_count: 5,
                    sentence_count: 120,
                },
            },
            {
                name: "Basic Vocabulary",
                display_name: "Basic Vocabulary",
                slug: "basic-vocabulary",
                description: "Essential everyday words and phrases",
                statistics: {
                    file_count: 3,
                    sentence_count: 75,
                },
            },
            {
                name: "Literature",
                display_name: "Literature Excerpts",
                slug: "literature",
                description: "Excerpts from famous literary works",
                statistics: {
                    file_count: 8,
                    sentence_count: 200,
                },
            },
        ];

        // Filter and sort the mock data according to the same logic
        // Sort sources by name alphabetically if requested
        if (sort === "alpha") {
            mockSources.sort((a, b) =>
                (a.name || "").toLowerCase().localeCompare(
                    (b.name || "").toLowerCase(),
                )
            );
        }

        return {
            languageCode: language_code,
            languageName: language_name,
            sources: mockSources,
            currentSort: sort,
        };
    } catch (err) {
        console.error("Failed to load sources:", err);
        throw error(500, "Failed to load sources");
    }
};
