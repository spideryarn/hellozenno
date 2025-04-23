/**
 * Language utility functions for the frontend.
 * 
 * These functions use the auto-generated language data whenever possible,
 * falling back to API calls when necessary for backward compatibility.
 */

import { getApiUrl, apiFetch } from "./api";
import { RouteName } from "./generated/routes";
import { LANGUAGES, LANGUAGE_NAMES, getLanguageName as getStaticLanguageName } from "./generated/languages";
import { error } from "@sveltejs/kit";

/**
 * Get all supported languages.
 * Uses the generated static data instead of making an API call.
 * 
 * @returns An array of language objects with code and name
 */
export function getLanguages() {
  return LANGUAGES;
}

/**
 * Get the display name for a language code.
 * Uses the generated static data first, falling back to API call if needed.
 * 
 * @param target_language_code The 2-letter language code
 * @param customFetch Optional custom fetch function (for SSR)
 * @returns The language name
 * @throws SvelteKit error if language not found
 */
export async function get_language_name(
  target_language_code: string,
  customFetch?: typeof fetch,
): Promise<string> {
  // First try to get from static data
  if (LANGUAGE_NAMES[target_language_code]) {
    return LANGUAGE_NAMES[target_language_code];
  }
  
  // If not found, fall back to API call for backward compatibility
  const fetchFunc = customFetch || fetch;
  try {
    const response = await fetchFunc(
      getApiUrl(RouteName.LANGUAGES_API_GET_LANGUAGE_NAME_API, {
        target_language_code: target_language_code,
      }),
    );
    
    if (!response.ok) {
      throw error(
        response.status, 
        `Language not found: ${target_language_code}`
      );
    }
    
    const data = await response.json();
    
    if (!data.name) {
      throw error(404, `Invalid language data received for: ${target_language_code}`);
    }
    
    return data.name;
  } catch (err) {
    // If it's already a SvelteKit error, just rethrow it
    if (err && typeof err === 'object' && 'status' in err) {
      throw err;
    }
    
    // Otherwise log and throw a new error
    console.error(
      `Error fetching language name for ${target_language_code}:`,
      err,
    );
    throw error(500, `Failed to fetch language data: ${target_language_code}`);
  }
}

/**
 * Synchronous version of get_language_name that doesn't make API calls.
 * Useful for UI components that don't need to wait for data.
 * 
 * @param target_language_code The 2-letter language code
 * @returns The language name, or the code itself if not found
 */
export function getLanguageNameSync(target_language_code: string): string {
  return getStaticLanguageName(target_language_code);
}