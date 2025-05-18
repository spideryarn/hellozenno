import { error, redirect } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import { getWordformWithSearch } from "$lib/api";
import type { SearchResult } from "$lib/types";

export const load: PageServerLoad = async ({ params, locals }) => {
    let { target_language_code, wordform } = params; // Make wordform mutable
    const { supabase, session } = locals;

    console.log(
        `[Wordform Page Server] Initiating load for wordform: "${wordform}", lang: "${target_language_code}"`
    );

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
        console.log(
            `[Wordform Page Server] Calling getWordformWithSearch for wordform: "${wordform}"`
        );
        const apiResult = await getWordformWithSearch(
            supabase, // Pass supabase client
            target_language_code,
            wordform, // Use the potentially corrected wordform
            session?.access_token ?? null,
        );

        console.log(
            `[Wordform Page Server] Raw apiResult from getWordformWithSearch for "${wordform}":`,
            JSON.stringify(apiResult, null, 2)
        );

        // Handle different response types based on status
        if (apiResult && apiResult.status === "found") {
            // Direct wordform match found - return the data as is
            // This now includes newly generated wordforms too
            console.log(`[Wordform Page Server] Wordform found: ${wordform}. Returning data.`);
            return {
                wordformData: apiResult.data,
            };
        } else if (apiResult && apiResult.status === "multiple_matches") {
            // Multiple matches found - redirect to search results page
            console.log(
                `[Wordform Page Server] Multiple matches for: ${wordform}, redirecting to search.`
            );
            throw redirect(
                302,
                `/language/${target_language_code}/search/${
                    encodeURIComponent(wordform)
                }`,
            );
        } else if (apiResult && apiResult.status === "redirect") {
            // Should redirect to another wordform
            // This is now only used as a fallback
            console.log(`[Wordform Page Server] Redirecting to: ${apiResult.data.redirect_to}`);
            throw redirect(
                302,
                `/language/${target_language_code}/wordform/${
                    encodeURIComponent(apiResult.data.redirect_to)
                }`,
            );
        } else if (apiResult && apiResult.status === "invalid") {
            // Invalid word - redirect to search to show the error
            console.log(`[Wordform Page Server] Invalid word: ${wordform}, redirecting to search.`);
            throw redirect(
                302,
                `/language/${target_language_code}/search/${
                    encodeURIComponent(wordform)
                }`,
            );
        } else {
            // For older API responses that don't have a status field,
            // or if apiResult is {}, which means apiFetch returned an empty object.
            console.warn(
                `[Wordform Page Server] Unexpected apiResult structure or empty object for "${wordform}". apiResult:`,
                JSON.stringify(apiResult, null, 2)
            );
            return {
                wordformData: apiResult, // This will be {} if apiFetch returned an empty object
            };
        }
    } catch (err: any) {
        console.error(
            `[Wordform Page Server] Error during load for wordform "${wordform}":`,
            err
        );
        // Check if err is a SvelteKit redirect object (thrown by `redirect()`)
        // SvelteKit's redirect throws an error-like object with status and location
        if (err && typeof err.status === 'number' && typeof err.location === 'string') {
            // This is a SvelteKit redirect, pass it through
            throw err;
        }
        
        // Keep existing check for native Response objects (though less likely here now)
        if (err instanceof Response && err.status === 302) {
            // This is our redirect, pass it through
            console.log(`[Wordform Page Server] Propagating redirect for "${wordform}".`);
            throw err;
        }

        console.error(
            `[Wordform Page Server] Unhandled error for "${wordform}". Status: ${err?.status}, Message: ${err?.message}, Body: ${JSON.stringify(err?.body)}`
        );

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
                `[Wordform Page Server] Request timed out for "${wordform}", returning null wordformData.`
            );
            return {
                wordformData: null,
            };
        }

        // If it's a 404, redirect to search page to show not found
        if (err instanceof Error && err.message.includes("404")) {
            console.log(
                `[Wordform Page Server] Received 404 for "${wordform}", redirecting to search.`
            );
            throw redirect(
                302,
                `/language/${target_language_code}/search/${
                    encodeURIComponent(wordform)
                }`,
            );
        }

        console.error(
            `[Wordform Page Server] Throwing 500 error for "${wordform}". Original error: ${err?.message || err}`
        );
        throw error(
            500,
            `Failed to load wordform: ${
                err instanceof Error ? err.message : String(err)
            }`,
        );
    }
};
