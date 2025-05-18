import { error, redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getWordformWithSearch } from "$lib/api";
import type { SearchResult } from "$lib/types";

export const load: PageServerLoad = async ({ params, locals }) => {
    let { target_language_code, wordform } = params; // Make wordform mutable
    const { supabase, session } = locals;

    // Ensure wordform is in NFC for consistent handling
    if (wordform) {
        wordform = wordform.normalize('NFC');
    }

    // Diagnostic: Log the wordform as received by SvelteKit
    console.log(
        `[+page.server.ts] Initial params.wordform (normalized): "${wordform}" (Code points: ${
            Array.from(wordform).map((c) => c.charCodeAt(0).toString(16)).join(
                " ",
            )
        })`,
    );

    // Attempt to fix a known malformation
    // "croisĂŠs" (c r o i s U+0102 U+00E9 s)
    // should be "croisés" (c r o i s U+00E9 s)
    // const malformedSequence = "crois\u0102\u00E9s"; // "croisĂŠs"
    // const correctSequence = "crois\u00E9s"; // "croisés"

    // if (wordform === malformedSequence) {
    //     console.log(
    //         `[+page.server.ts] Detected malformed sequence "${malformedSequence}", correcting to "${correctS
    // equence}"`,
    //     );
    //     wordform = correctSequence;
    // }

    try {
        // Use our enhanced search function to handle various result types

        // Set a reasonable timeout for server-side rendering
        // This is important since we now wait for wordform generation to complete
        const data = await getWordformWithSearch(
            null,
            target_language_code,
            wordform, // Use the potentially corrected wordform
            session?.access_token ?? null,
        );

        // Handle different response types based on status
        if (data.status === "found") {
            // Direct wordform match found - return the data as is
            // This now includes newly generated wordforms too
            console.log(`Wordform found: ${wordform}`);
            return {
                wordformData: data.data,
            };
        } else if (data.status === "multiple_matches") {
            // Multiple matches found - redirect to search results page
            console.log(
                `Multiple matches found for: ${wordform}, redirecting to search`,
            );
            throw redirect(
                302,
                `/language/${target_language_code}/search/${
                    encodeURIComponent(wordform)
                }`,
            );
        } else if (data.status === "redirect") {
            // Should redirect to another wordform
            // This is now only used as a fallback
            console.log(`Redirecting to: ${data.redirect_to}`);
            throw redirect(
                302,
                `/language/${target_language_code}/wordform/${
                    encodeURIComponent(data.redirect_to)
                }`,
            );
        } else if (data.status === "invalid") {
            // Invalid word - redirect to search to show the error
            console.log(`Invalid word: ${wordform}, redirecting to search`);
            throw redirect(
                302,
                `/language/${target_language_code}/search/${
                    encodeURIComponent(wordform)
                }`,
            );
        } else {
            // For older API responses that don't have a status field
            // console.log(`No status field, using data as is:`, data);
            return {
                wordformData: data,
            };
        }
    } catch (err: any) {
        // Check if err is a SvelteKit redirect object (thrown by `redirect()`)
        // SvelteKit's redirect throws an error-like object with status and location
        if (err && typeof err.status === 'number' && typeof err.location === 'string') {
            // This is a SvelteKit redirect, pass it through
            throw err;
        }
        
        // Keep existing check for native Response objects (though less likely here now)
        if (err instanceof Response && err.status === 302) {
            // This is our redirect, pass it through
            throw err;
        }

        console.error("Error loading wordform:", err);

        // Check for the 401 Authentication Required error specifically
        // The error thrown by apiFetch should be an object with status and body
        if (
            typeof err === "object" &&
            err !== null &&
            "status" in err &&
            err.status === 401 &&
            "body" in err &&
            typeof err.body === "object" &&
            err.body !== null &&
            "authentication_required_for_generation" in err.body &&
            err.body.authentication_required_for_generation
        ) {
            console.log(
                "Authentication required for generation, returning specific state",
            );
            return {
                wordformData: {
                    authentication_required_for_generation: true,
                    target_language_code: target_language_code,
                    wordform: wordform,
                    target_language_name: null, // Language name is not directly available in locals here
                },
            };
        }

        // Handle timeout errors specifically
        if (err instanceof Error && err.message.includes("timed out")) {
            // If we time out during wordform generation, still return a loading state
            // The client-side JS will retry fetching the data
            console.log(
                "Request timed out, returning empty wordform data for client-side handling",
            );
            return {
                wordformData: null,
            };
        }

        // If it's a 404, redirect to search page to show not found
        if (err instanceof Error && err.message.includes("404")) {
            throw redirect(
                302,
                `/language/${target_language_code}/search/${
                    encodeURIComponent(wordform)
                }`,
            );
        }

        throw error(
            500,
            `Failed to load wordform: ${
                err instanceof Error ? err.message : String(err)
            }`,
        );
    }
};
