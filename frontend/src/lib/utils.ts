// Helper function to get language name from language code
// This now uses the API instead of hardcoded values
import { getApiUrl } from "./api";
import { RouteName } from "./generated/routes";

export async function get_language_name(
    target_language_code: string,
    customFetch?: typeof fetch,
): Promise<string> {
    const fetchFunc = customFetch || fetch;
    try {
        const response = await fetchFunc(
            getApiUrl(RouteName.LANGUAGES_API_GET_LANGUAGE_NAME_API, {
                target_language_code: target_language_code,
            }),
        );
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        return data.name;
    } catch (error) {
        console.error(
            `Error fetching language name for ${target_language_code}:`,
            error,
        );
        return target_language_code; // Fallback to the code itself if API fails
    }
}
