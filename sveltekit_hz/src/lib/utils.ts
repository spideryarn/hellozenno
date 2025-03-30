// Helper function to get language name from language code
// This now uses the API instead of hardcoded values
import { getApiUrl } from "./api";
import { RouteName } from "./generated/routes";

export async function get_language_name(
    language_code: string,
    customFetch?: typeof fetch,
): Promise<string> {
    const fetchFunc = customFetch || fetch;
    try {
        const response = await fetchFunc(
            getApiUrl(RouteName.LANGUAGES_API_GET_LANGUAGE_NAME_API, {
                language_code: language_code,
            }),
        );
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        return data.name;
    } catch (error) {
        console.error(
            `Error fetching language name for ${language_code}:`,
            error,
        );
        return language_code; // Fallback to the code itself if API fails
    }
}

// Helper to create consistent API URLs
export function get_api_url(endpoint: string): string {
    // In a real app, this would come from environment variables
    const API_BASE_URL = "http://localhost:3000/api";
    return `${API_BASE_URL}/${endpoint}`;
}
