// AUTO-GENERATED. Do not edit directly.
// Regenerate via: npm run generate:changelog

export interface ChangelogEntry { date: string; text: string; sha: string; }
export interface ChangelogTheme { id: string; title: string; entries: ChangelogEntry[]; }
export interface ChangelogMonth { id: string; title: string; themes: ChangelogTheme[]; }
export const changelog: ChangelogMonth[] = [
  {
    "id": "march-2025",
    "title": "March 2025",
    "themes": [
      {
        "id": "auth-security",
        "title": "Auth & Security",
        "entries": [
          {
            "date": "2025-03-31",
            "text": "Auto-focus on search languages box Co-Authored-By: Claude <noreply@anthropic",
            "sha": "86c75e5"
          },
          {
            "date": "2025-03-30",
            "text": "Added buttons to main language page Co-Authored-By: Claude <noreply@anthropic",
            "sha": "27bf109"
          },
          {
            "date": "2025-03-30",
            "text": "Removed extraneous `static_folder` arg Co-Authored-By: Claude <noreply@anthropic",
            "sha": "2dc6f6d"
          },
          {
            "date": "2025-03-30",
            "text": "Doc thinking about page titles Co-Authored-By: Claude <noreply@anthropic",
            "sha": "4a45986"
          },
          {
            "date": "2025-03-27",
            "text": "Trying to get Supabase_local MCP to work I don't think this succeeded",
            "sha": "899a2de"
          },
          {
            "date": "2025-03-22",
            "text": "Moved auth out of system_views and updated Blueprint prefixes",
            "sha": "3286003"
          },
          {
            "date": "2025-03-16",
            "text": "Create 250701_Supabase_Authentication_Integration",
            "sha": "a494e64"
          },
          {
            "date": "2025-03-16",
            "text": "Updated Supabase auth plan",
            "sha": "0d8747e"
          },
          {
            "date": "2025-03-16",
            "text": "Updated Supabase authentication implementation details - Transformed original plan into implementation report - Documented completed work on Supabase authentication - Added details on challenges faced and solutions implemented - Included code samples and future improvement recommendations",
            "sha": "20e8e10"
          },
          {
            "date": "2025-03-15",
            "text": "Create 250317_Supabase_Realtime_for_wordforms",
            "sha": "34c49c4"
          },
          {
            "date": "2025-03-14",
            "text": "Supabase init",
            "sha": "ee24368"
          }
        ]
      },
      {
        "id": "backend-database",
        "title": "Backend & Database",
        "entries": [
          {
            "date": "2025-03-31",
            "text": "Tidied up Python code into `api/`",
            "sha": "e9243d6"
          },
          {
            "date": "2025-03-31",
            "text": "deploy_api",
            "sha": "6014479"
          },
          {
            "date": "2025-03-30",
            "text": "Remove the get_api_url function from utils",
            "sha": "d5de21b"
          },
          {
            "date": "2025-03-30",
            "text": "Update search functions in api",
            "sha": "6b9d3ed"
          },
          {
            "date": "2025-03-29",
            "text": "Move languages_list_vw to dedicated Blueprint and add languages API endpoint - Created a new languages_views_bp Blueprint to properly modularize the language views  - Extracted core get_languages_list() function for reuse  - Created new languages_api_bp with /api/lang/languages endpoint  - Updated template references to use new endpoint name  - Registered both blueprints in app initialization",
            "sha": "7209eac"
          },
          {
            "date": "2025-03-29",
            "text": "Add API endpoint for detailed sentence view - Created get_detailed_sentence_data utility function in sentence_utils",
            "sha": "340c1e0"
          },
          {
            "date": "2025-03-22",
            "text": "Fixed database MCP",
            "sha": "a61eb36"
          },
          {
            "date": "2025-03-22",
            "text": "We don't need core_api",
            "sha": "3d73186"
          },
          {
            "date": "2025-03-22",
            "text": "Move API endpoints from sourcefile_views to sourcefile_api",
            "sha": "384e9b8"
          },
          {
            "date": "2025-03-22",
            "text": "Update JS code to use API endpoint constants instead of view constants - Update sourcefile",
            "sha": "c3e31e7"
          },
          {
            "date": "2025-03-18",
            "text": "Update tests to use the new URL patterns - Updated API tests to use /api/lang/",
            "sha": "805dd39"
          },
          {
            "date": "2025-03-18",
            "text": "Fix redirect loop in wordform view - Added wordform database creation before redirect to prevent infinite redirect loops - Used existing Wordform",
            "sha": "89ce4a3"
          },
          {
            "date": "2025-03-17",
            "text": "Update MIGRATIONS",
            "sha": "46f4cca"
          },
          {
            "date": "2025-03-17",
            "text": "Standardize API URL structure with domain-specific API files - Create domain-specific API files with consistent URL patterns - Implement /api/lang/<resource>/",
            "sha": "03fa3f4"
          },
          {
            "date": "2025-03-17",
            "text": "Update 250317_API_URL_Structure_Standardization",
            "sha": "7db702d"
          },
          {
            "date": "2025-03-17",
            "text": "Standardize API URL structure across app This commit implements a standardized API URL structure following the pattern /api/lang/<resource>/",
            "sha": "eeb4922"
          },
          {
            "date": "2025-03-16",
            "text": "First stage of Vercel migration (NOT DEPLOYED SUCCESSFULLY)",
            "sha": "5e0f5d7"
          },
          {
            "date": "2025-03-16",
            "text": "Add description field to Sourcedir model - Created migration 028_add_sourcedir_description",
            "sha": "3f5010d"
          },
          {
            "date": "2025-03-16",
            "text": "Fixed Vercel migrations",
            "sha": "f71e4bd"
          },
          {
            "date": "2025-03-15",
            "text": "Fix N+1 database query issue in sourcefile_words view Optimized database queries in inspect_sourcefile_words() by using proper joins to prefetch related data in a single query rather than making separate queries for each record",
            "sha": "d23bb52"
          },
          {
            "date": "2025-03-15",
            "text": "Optimize sourcefile view functions with improved database query methods - Added support for object-based filtering in Wordform",
            "sha": "024f80c"
          },
          {
            "date": "2025-03-15",
            "text": "Simplify database query methods for cleaner API - Remove sourcedir_slug and sourcefile_slug arguments from get_all_phrases_for() - For both get_all_phrases_for() and get_all_wordforms_for(), automatically perform join when sourcefile is provided - Remove include_junction_data parameter as it's now implicit - Unify return behavior across methods for consistent API - Update documentation to reflect changes",
            "sha": "8034895"
          },
          {
            "date": "2025-03-15",
            "text": "Fix PostgreSQL query issue with DISTINCT and ORDER BY - Fixed a PostgreSQL error where ORDER BY expressions must appear in SELECT list when using DISTINCT - Modified get_all_lemmas_for in Lemma model to include fn",
            "sha": "aa296fb"
          },
          {
            "date": "2025-03-15",
            "text": "Optimize sentence loading with efficient database queries - Add get_all_sentences_for() method to Sentence model - Use a two-query strategy to avoid N+1 database queries - Fetch sentences first, then efficiently fetch all related lemmas - Preload lemma data to eliminate per-sentence queries - Fix template issue with undefined vite_entries variable",
            "sha": "ca64f7a"
          },
          {
            "date": "2025-03-14",
            "text": "Add rename button to sourcefile header • Added a button to rename sourcefiles in the header template • Leverages existing backend endpoint and JavaScript functionality",
            "sha": "b9cd297"
          },
          {
            "date": "2025-03-14",
            "text": "Add ability to move sourcefiles between sourcedirs - Add API endpoint for moving a sourcefile to a different sourcedir - Add dropdown selector in sourcefile views to select a target directory - Position the selector in the navigation bar for compact layout - Exclude current sourcedir from dropdown options - Add visual feedback during move operation - Implement error handling with appropriate messages - Consolidate selector styling in base",
            "sha": "cb0ed64"
          }
        ]
      },
      {
        "id": "deployment-ops",
        "title": "Deployment & Ops",
        "entries": [
          {
            "date": "2025-03-31",
            "text": "Update Vercel deployment strategy with dual-project organization",
            "sha": "24d70d5"
          },
          {
            "date": "2025-03-23",
            "text": "Fix route names in JavaScript files to match routes",
            "sha": "e4fd50c"
          },
          {
            "date": "2025-03-23",
            "text": "Fix circular imports",
            "sha": "8d63e48"
          },
          {
            "date": "2025-03-23",
            "text": "Avoid circular dependencies",
            "sha": "6421dfa"
          },
          {
            "date": "2025-03-23",
            "text": "Move frontend and generation earlier in deploy",
            "sha": "9aa8c43"
          },
          {
            "date": "2025-03-22",
            "text": "Add endpoint_for function and improve documentation - Added endpoint_for function to make url_for more robust against function renames - Updated documentation to explain TypeScript enum benefits - Removed unnecessary code complexity after weighing trade-offs",
            "sha": "8aae12d"
          },
          {
            "date": "2025-03-22",
            "text": "Implement URL registry for templates and JavaScript - Added endpoint_for to global context processor - Created view function references in context processor - Updated base",
            "sha": "bbedcf9"
          },
          {
            "date": "2025-03-22",
            "text": "Update URL Registry documentation - Add implementation status section showing completed work - Update planning document to reflect documentation progress - Document templates and JavaScript files that use the registry - Mark real-world usage examples as complete",
            "sha": "f5723cc"
          },
          {
            "date": "2025-03-22",
            "text": "Improve URL registry generation for production - Update deploy",
            "sha": "0b02f6b"
          },
          {
            "date": "2025-03-17",
            "text": "Copy Vite manifest to accessible location for Vercel compatibility",
            "sha": "90de93d"
          },
          {
            "date": "2025-03-16",
            "text": "Add Flask Hello World app for Vercel serverless deployment",
            "sha": "b0f6a3d"
          },
          {
            "date": "2025-03-16",
            "text": "Slow progess on Vercel deployment",
            "sha": "157506a"
          },
          {
            "date": "2025-03-16",
            "text": "/languages works on Vercel",
            "sha": "4441ae3"
          },
          {
            "date": "2025-03-16",
            "text": "Fix URL encoding issues with Greek characters in Vercel deployment - Add middleware solution to handle URL decoding centrally for all routes - Create utility functions for fixing various URL encoding scenarios - Comment out redundant explicit URL decoding in view handlers - Add comprehensive unit tests for URL utilities - Update templates to correctly display language names - Document the approach and decision in planning/250316_vercel_url_encoding_fix",
            "sha": "3cd8e3d"
          },
          {
            "date": "2025-03-16",
            "text": "Fix health check URL in deploy script Updated deploy",
            "sha": "96f81be"
          },
          {
            "date": "2025-03-16",
            "text": "Update URL encoding fix documentation after Vercel testing - Add testing results from Vercel deployment - Document approach change to defense-in-depth strategy - Mark explicit step for restoring route handler decoding - Refine implementation details based on real-world testing",
            "sha": "71d2d18"
          },
          {
            "date": "2025-03-16",
            "text": "Preserve original title when creating sourcefiles from text Previously, when creating a sourcefile from text, the title was being slugified for the filename, leading to a loss of special characters in the display name",
            "sha": "1e503c5"
          },
          {
            "date": "2025-03-16",
            "text": "Update 250316_vercel_url_encoding_fix",
            "sha": "2b498eb"
          },
          {
            "date": "2025-03-16",
            "text": "Removing Hello World Vercel app",
            "sha": "da24ab4"
          },
          {
            "date": "2025-03-15",
            "text": "Optimize Docker image size - Update",
            "sha": "185d87d"
          },
          {
            "date": "2025-03-14",
            "text": "Fix page loading performance issues by optimizing script loading - Add defer attribute to third-party scripts to prevent render blocking - Move base",
            "sha": "3196423"
          },
          {
            "date": "2025-03-02",
            "text": "Fixed description issue in tests and other syntax error",
            "sha": "d390a6e"
          }
        ]
      },
      {
        "id": "docs-testing",
        "title": "Documentation & Testing",
        "entries": [
          {
            "date": "2025-03-30",
            "text": "Tidying and docs",
            "sha": "b5654ea"
          },
          {
            "date": "2025-03-30",
            "text": "Docs",
            "sha": "dc280ed"
          },
          {
            "date": "2025-03-29",
            "text": "Playwright MCP",
            "sha": "e6af7d6"
          },
          {
            "date": "2025-03-29",
            "text": "Update documentation with Bootstrap theme details - Added Bootstrap styling documentation to README",
            "sha": "513ac76"
          },
          {
            "date": "2025-03-29",
            "text": "Renamed docs",
            "sha": "be247f0"
          },
          {
            "date": "2025-03-29",
            "text": "Moved Python docs",
            "sha": "534d56e"
          },
          {
            "date": "2025-03-26",
            "text": "Docs and tweaks",
            "sha": "b6f2bb3"
          },
          {
            "date": "2025-03-23",
            "text": "Remove endpoint_for from additional templates, update test utils and view functions",
            "sha": "750106d"
          },
          {
            "date": "2025-03-23",
            "text": "Add production frontend testing improvements - Add LOCAL_CHECK_OF_PROD_FRONTEND environment variable - Update run_flask",
            "sha": "b7e41e3"
          },
          {
            "date": "2025-03-23",
            "text": "Working frontend local/prod testing, but still feels over-complicated",
            "sha": "a0c28df"
          },
          {
            "date": "2025-03-23",
            "text": "Fix failing sourcefile view tests: slugify filenames in create_from_text, fix audio test assertions",
            "sha": "ec368fb"
          },
          {
            "date": "2025-03-23",
            "text": "Fix failing sourcefile tests with improved mocks and test approach",
            "sha": "1c248bc"
          },
          {
            "date": "2025-03-22",
            "text": "Consolidate test fixture functions and remove redundant code - Enhanced fixture functions in fixtures_for_tests",
            "sha": "f90894f"
          },
          {
            "date": "2025-03-22",
            "text": "Delete routes_test",
            "sha": "2d0a36f"
          },
          {
            "date": "2025-03-22",
            "text": "Obsolete docs",
            "sha": "f850fa5"
          },
          {
            "date": "2025-03-15",
            "text": "Renamed planning docs",
            "sha": "2d19705"
          },
          {
            "date": "2025-03-15",
            "text": "Docs",
            "sha": "b52dafd"
          },
          {
            "date": "2025-03-15",
            "text": "Docs tidying",
            "sha": "e44f140"
          },
          {
            "date": "2025-03-14",
            "text": "Reduce margins and increase font size on mobile (UNTESTED)",
            "sha": "f972181"
          },
          {
            "date": "2025-03-02",
            "text": "Docs",
            "sha": "234cc8b"
          },
          {
            "date": "2025-03-02",
            "text": "Tidying up docs etc re testing",
            "sha": "65bf797"
          },
          {
            "date": "2025-03-02",
            "text": "More test fixes",
            "sha": "93547bd"
          },
          {
            "date": "2025-03-02",
            "text": "Tidy up tests",
            "sha": "e5972ab"
          },
          {
            "date": "2025-03-02",
            "text": "Fixed tests",
            "sha": "d60bc2c"
          }
        ]
      },
      {
        "id": "flashcards-content",
        "title": "Flashcards & Content",
        "entries": [
          {
            "date": "2025-03-30",
            "text": "Refactor phrase queries into shared utility function - Created new utils/phrase_utils",
            "sha": "6315009"
          },
          {
            "date": "2025-03-30",
            "text": "Update to $app/state from deprecated $app/stores - Updated imports from $app/stores to $app/state for phrase pages - Removed $ prefix from page references (page",
            "sha": "8ffed17"
          },
          {
            "date": "2025-03-30",
            "text": "Fix wordform page to handle enhanced search responses",
            "sha": "65ce7ce"
          },
          {
            "date": "2025-03-29",
            "text": "Added sentences_list",
            "sha": "7a3b0b5"
          },
          {
            "date": "2025-03-29",
            "text": "Lemmas list vw",
            "sha": "8f1ee2d"
          },
          {
            "date": "2025-03-28",
            "text": "Abortive experiment in auto-creating lemmas",
            "sha": "fac1268"
          },
          {
            "date": "2025-03-28",
            "text": "Don't return words/phrases if empty text",
            "sha": "678e019"
          },
          {
            "date": "2025-03-28",
            "text": "Added Delete Phrase button (with icon)",
            "sha": "b8fac50"
          },
          {
            "date": "2025-03-27",
            "text": "Prompts to handle max_new_words and max_new_phrases UNTESTED",
            "sha": "22a1728"
          },
          {
            "date": "2025-03-27",
            "text": "Setting limits on max phrases/words because of timeouts and max_tokens (not sure why this is only suddenly an issue now)",
            "sha": "4f49b09"
          },
          {
            "date": "2025-03-27",
            "text": "If unprocessed, do a double-round of extracting wordforms and phrases",
            "sha": "3de9ecd"
          },
          {
            "date": "2025-03-23",
            "text": "Fix audio URL in Sentence",
            "sha": "04fab35"
          },
          {
            "date": "2025-03-23",
            "text": "Skip test_random_flashcard_vw",
            "sha": "1455023"
          },
          {
            "date": "2025-03-23",
            "text": "Fix 500 error on phrases page by adding proper Undefined checks for JSON serialization",
            "sha": "7451ab6"
          },
          {
            "date": "2025-03-22",
            "text": "Update more templates to use URL registry - Update lemmas",
            "sha": "95a339f"
          },
          {
            "date": "2025-03-22",
            "text": "Fixed skipped wordform view smoke tests by following redirects",
            "sha": "676786f"
          },
          {
            "date": "2025-03-18",
            "text": "Add English translation search feature This implementation enables searching for English words in non-English language sections",
            "sha": "be8a804"
          },
          {
            "date": "2025-03-18",
            "text": "Restored delete_wordform() erroneously deleted as part of search changes",
            "sha": "4cd2ad6"
          },
          {
            "date": "2025-03-18",
            "text": "Fix delete wordform function and update tests for new search format - Restored delete_wordform function to wordform_views",
            "sha": "75a2cfc"
          },
          {
            "date": "2025-03-17",
            "text": "Don't open lemmas in a new window",
            "sha": "02c8bac"
          },
          {
            "date": "2025-03-16",
            "text": "Still broken Sentence",
            "sha": "c014095"
          },
          {
            "date": "2025-03-16",
            "text": "Restructure URLs with consistent prefixes Reorganize URL structure to use consistent prefixes for different types of routes: - /lang/* - Language-related routes (wordforms, lemmas, flashcards, etc",
            "sha": "01cd5a6"
          },
          {
            "date": "2025-03-15",
            "text": "Add commonality sorting to get_all_wordforms_for and update wordform_views - Added commonality sorting option to Wordform",
            "sha": "cf276a5"
          },
          {
            "date": "2025-03-15",
            "text": "Add Lemma",
            "sha": "82a7a93"
          },
          {
            "date": "2025-03-15",
            "text": "Update remaining use of Lemma",
            "sha": "1dc557a"
          },
          {
            "date": "2025-03-15",
            "text": "Remove legacy get_all_for_language methods for simplicity - Removed Wordform",
            "sha": "c56ad3e"
          },
          {
            "date": "2025-03-15",
            "text": "Prevent slashes in lemmas and wordforms to avoid URL routing issues - Added explicit instructions to all relevant prompt templates - Ensures lemmas and wordforms generated by LLM won't contain slashes - Simpler solution than adding slug fields or URL encoding",
            "sha": "d26a72f"
          },
          {
            "date": "2025-03-15",
            "text": "Fix Sentence",
            "sha": "0039586"
          },
          {
            "date": "2025-03-15",
            "text": "Fixed Sentence",
            "sha": "2878bf1"
          },
          {
            "date": "2025-03-15",
            "text": "Fix mobile audio autoplay in flashcards by using HTML autoplay attribute - Changed audio initialization approach to match v1 flashcards - Added autoplay attribute to audio element in the HTML markup - Improved error message with clearer instructions - Removed programmatic Audio creation that was causing mobile autoplay issues",
            "sha": "6ba03fd"
          },
          {
            "date": "2025-03-09",
            "text": "Allow for phrase commonality & guessability to be None",
            "sha": "e9250aa"
          },
          {
            "date": "2025-03-03",
            "text": "Don't lower-case wordforms for proper nouns",
            "sha": "689bca5"
          },
          {
            "date": "2025-03-03",
            "text": "Handle missing phrase commonality",
            "sha": "b759505"
          },
          {
            "date": "2025-03-03",
            "text": "Fixed commonality sort for lemmas",
            "sha": "a273e81"
          },
          {
            "date": "2025-03-03",
            "text": "MiniWordform v1",
            "sha": "a338240"
          },
          {
            "date": "2025-03-03",
            "text": "More MiniWordforms in lemma",
            "sha": "c74f8a3"
          },
          {
            "date": "2025-03-03",
            "text": "Using MiniWordform for wordforms",
            "sha": "83be621"
          },
          {
            "date": "2025-03-02",
            "text": "Cascade delete wordform",
            "sha": "7834a8a"
          },
          {
            "date": "2025-03-02",
            "text": "Tweaks to prompt template for wordforms",
            "sha": "b783856"
          },
          {
            "date": "2025-03-02",
            "text": "Added phrase slug",
            "sha": "bd0f0d5"
          },
          {
            "date": "2025-03-02",
            "text": "Failed case-insensitive wordform and lemma sorting",
            "sha": "23f5256"
          },
          {
            "date": "2025-03-02",
            "text": "Failing to get Tailwind to work with Sentence",
            "sha": "272b2ac"
          },
          {
            "date": "2025-03-02",
            "text": "Added Sentence playback speed",
            "sha": "76195f9"
          },
          {
            "date": "2025-03-02",
            "text": "Separate Sourcefile text/words/phrases tabs",
            "sha": "8655b65"
          }
        ]
      },
      {
        "id": "misc",
        "title": "Miscellaneous",
        "entries": [
          {
            "date": "2025-03-30",
            "text": "Working on Sourcefile page",
            "sha": "d00f7a5"
          },
          {
            "date": "2025-03-30",
            "text": "Sourcefile tabs in progress",
            "sha": "feb661b"
          },
          {
            "date": "2025-03-30",
            "text": "Update STYLING",
            "sha": "37d3dfb"
          },
          {
            "date": "2025-03-30",
            "text": "Fixed sourcedir url",
            "sha": "ac345e3"
          },
          {
            "date": "2025-03-30",
            "text": "In progress on URL standardisation",
            "sha": "19abf8b"
          },
          {
            "date": "2025-03-30",
            "text": "Renaming views /lang -> /language",
            "sha": "c1cf6cd"
          },
          {
            "date": "2025-03-30",
            "text": "Avoiding duplicate headings in Sourcefile",
            "sha": "f425753"
          },
          {
            "date": "2025-03-30",
            "text": "Still fixing urls",
            "sha": "1921761"
          },
          {
            "date": "2025-03-30",
            "text": "Update CLAUDE",
            "sha": "f645861"
          },
          {
            "date": "2025-03-30",
            "text": "Refactor search functionality by extracting common code to search_utils",
            "sha": "34e1ec4"
          },
          {
            "date": "2025-03-30",
            "text": "Update SEARCH",
            "sha": "c8eedff"
          },
          {
            "date": "2025-03-29",
            "text": "Moved out iOS",
            "sha": "a3f668b"
          },
          {
            "date": "2025-03-29",
            "text": "Moved languages_list_vw -> languages_views",
            "sha": "80da008"
          },
          {
            "date": "2025-03-29",
            "text": "Improve homepage design and styling to match dark theme",
            "sha": "472b090"
          },
          {
            "date": "2025-03-28",
            "text": "Added delete button",
            "sha": "15fa2d4"
          },
          {
            "date": "2025-03-27",
            "text": "Prompts: adding delimiters and dealing with empty",
            "sha": "ced02cd"
          },
          {
            "date": "2025-03-27",
            "text": "Default language level and types",
            "sha": "44296f2"
          },
          {
            "date": "2025-03-27",
            "text": "Improving Source* header & buttons - cosmetic",
            "sha": "bb7cad0"
          },
          {
            "date": "2025-03-27",
            "text": "Refactor/malgamate process & update Sourcefile",
            "sha": "bb77225"
          },
          {
            "date": "2025-03-27",
            "text": "Don't check Git twice - it's not worth it",
            "sha": "e7e8b22"
          },
          {
            "date": "2025-03-27",
            "text": "Fire and forget",
            "sha": "7f31bca"
          },
          {
            "date": "2025-03-27",
            "text": "Improved parallelisation",
            "sha": "675b12f"
          },
          {
            "date": "2025-03-26",
            "text": "Add more languages",
            "sha": "1b618f6"
          },
          {
            "date": "2025-03-26",
            "text": "Tidying sourcefile processing and more robust",
            "sha": "4564c34"
          },
          {
            "date": "2025-03-23",
            "text": "Replace endpoint_for with direct endpoint strings in templates",
            "sha": "c5e9f6b"
          },
          {
            "date": "2025-03-23",
            "text": "Removing machinery for endpoint_for in templates",
            "sha": "6958881"
          },
          {
            "date": "2025-03-23",
            "text": "Replace redirect_to_view with redirect(url_for(endpoint_for())) pattern",
            "sha": "da3ffcb"
          },
          {
            "date": "2025-03-23",
            "text": "Use endpoint_for in Python code",
            "sha": "ebaf013"
          },
          {
            "date": "2025-03-23",
            "text": "Delete flask_view_utils",
            "sha": "c9851d6"
          },
          {
            "date": "2025-03-23",
            "text": "Remove weird hardcoded hack for search_views",
            "sha": "9c55dd4"
          },
          {
            "date": "2025-03-23",
            "text": "Updated import",
            "sha": "9342778"
          },
          {
            "date": "2025-03-23",
            "text": "Output Vite logs to both file and stdout",
            "sha": "bb90d82"
          },
          {
            "date": "2025-03-23",
            "text": "Refactor sort options template to simplify and remove if/elif chains - Modified _sort_options",
            "sha": "2a32330"
          },
          {
            "date": "2025-03-23",
            "text": "Breadcrumbs",
            "sha": "8fd554e"
          },
          {
            "date": "2025-03-23",
            "text": "MCP servers",
            "sha": "1d9460d"
          },
          {
            "date": "2025-03-23",
            "text": "Consolidate Vite helpers and fix environment detection - Create unified Vite helpers implementation in utils/vite_helpers",
            "sha": "1f57606"
          },
          {
            "date": "2025-03-23",
            "text": "Using Jinja globals - working",
            "sha": "9fc1efe"
          },
          {
            "date": "2025-03-23",
            "text": "",
            "sha": "51174d7"
          },
          {
            "date": "2025-03-22",
            "text": "Implement URL registry for frontend and template use This implements Option 4 from planning/250317_passing_urls_to_frontend",
            "sha": "68ab949"
          },
          {
            "date": "2025-03-22",
            "text": "Update URL registry planning document - Reorganized planning document for better clarity - Added action items for remaining work - Moved rejected options to an appendix - Updated implementation progress",
            "sha": "1a9b45a"
          },
          {
            "date": "2025-03-22",
            "text": "Add Jinja template URL demo - Add URL demo template with endpoint_for usage example - Inject endpoint_for into all templates via context processor - Add URL demo route in system_views",
            "sha": "d1f9067"
          },
          {
            "date": "2025-03-22",
            "text": "Add Jinja template example for URL registry - Created demo page showing URL generation with endpoint_for - Fixed function name for sourcedirs_for_language - Added example of how nested function calls work in templates",
            "sha": "62bd62c"
          },
          {
            "date": "2025-03-22",
            "text": "Remove URL demo page - Removed demo template and view function as it's no longer needed - Moving to a more integrated approach with endpoint_for",
            "sha": "92a7743"
          },
          {
            "date": "2025-03-22",
            "text": "Moved list_code_files",
            "sha": "8a9aaf4"
          },
          {
            "date": "2025-03-22",
            "text": "Update CLAUDE",
            "sha": "940382a"
          },
          {
            "date": "2025-03-22",
            "text": "Update sourcefiles template to use endpoint_for - Add additional blueprint and view function references to context processor - Update sourcefiles",
            "sha": "dcc49c9"
          },
          {
            "date": "2025-03-22",
            "text": "Fix AttributeError with Blueprint objects in URL registry - Remove Blueprint objects from view context - Provide view functions directly in context processor - Update templates to use direct function references instead of blueprint",
            "sha": "a50e277"
          },
          {
            "date": "2025-03-22",
            "text": "Update planning document with implementation challenges - Document Blueprint vs Function resolution issue - Add solution approach used for endpoint_for function - Add consideration for function naming conflicts - Update QA section with AttributeError fix",
            "sha": "2b62fe6"
          },
          {
            "date": "2025-03-22",
            "text": "Fix /lang route to handle both with and without trailing slash This ensures the language selection page is properly displayed when visiting /lang directly, matching the pattern used for other routes like /favicon",
            "sha": "2ada6fa"
          },
          {
            "date": "2025-03-22",
            "text": "Refactor context processor to use minimal function-based approach - Replace large inject_view_functions() with minimal inject_base_view_functions() - Update base",
            "sha": "a2ae49f"
          },
          {
            "date": "2025-03-22",
            "text": "Fix URL registry blueprint naming consistency - Renamed views",
            "sha": "b252091"
          },
          {
            "date": "2025-03-22",
            "text": "Renamed and refactored view functions, e",
            "sha": "1958520"
          },
          {
            "date": "2025-03-22",
            "text": "Moved stuff out of base",
            "sha": "53b363f"
          },
          {
            "date": "2025-03-22",
            "text": "Fixing a lot of endpoint_for",
            "sha": "23c14a9"
          },
          {
            "date": "2025-03-22",
            "text": "Remove route-registry-example page - Remove the route-registry-example view function from core_views",
            "sha": "1c673f3"
          },
          {
            "date": "2025-03-22",
            "text": "Updating view function names and jinja imports",
            "sha": "1e2fcc1"
          },
          {
            "date": "2025-03-22",
            "text": "We don't need get_route_registry",
            "sha": "2e7cb9a"
          },
          {
            "date": "2025-03-22",
            "text": "Add 404 error handler and fix template links - Register custom 404 error handler in Flask app to use 404",
            "sha": "9adf01b"
          },
          {
            "date": "2025-03-22",
            "text": "Removed extraneous prefixes",
            "sha": "6ec10c1"
          },
          {
            "date": "2025-03-22",
            "text": "Standardize URL parameter names to target_language_code - Updated parameter names in routes from language_code to target_language_code - Modified view functions in sourcefile_views",
            "sha": "d0c2c5e"
          },
          {
            "date": "2025-03-22",
            "text": "Count lines by file",
            "sha": "e5c1180"
          },
          {
            "date": "2025-03-22",
            "text": "Updating urls and machinery",
            "sha": "b1f93a1"
          },
          {
            "date": "2025-03-22",
            "text": "Renamed languages_vw -> languages_list_vw",
            "sha": "58c9a6a"
          },
          {
            "date": "2025-03-22",
            "text": "Trying to be surgical about renaming target_language_code",
            "sha": "4f1d167"
          },
          {
            "date": "2025-03-22",
            "text": "Create 250322_REST_url_tidying_proposal",
            "sha": "95ba538"
          },
          {
            "date": "2025-03-22",
            "text": "Gah, it's a mess",
            "sha": "0615521"
          },
          {
            "date": "2025-03-19",
            "text": "Fixed broken urls for word preview and generate_audio",
            "sha": "ee943a9"
          },
          {
            "date": "2025-03-19",
            "text": "Removing urls() list",
            "sha": "72859d6"
          },
          {
            "date": "2025-03-19",
            "text": "One more word preview url fix",
            "sha": "46dbe3d"
          },
          {
            "date": "2025-03-18",
            "text": "Working on English search",
            "sha": "6e8d9d5"
          },
          {
            "date": "2025-03-18",
            "text": "Next draft of prompt template for English search",
            "sha": "0bdade2"
          },
          {
            "date": "2025-03-18",
            "text": "More minor steps on planning the English search",
            "sha": "c00d93a"
          },
          {
            "date": "2025-03-18",
            "text": "Create 250317_passing_urls_to_frontend",
            "sha": "a87bdc1"
          },
          {
            "date": "2025-03-18",
            "text": "Delete simple",
            "sha": "7df0eda"
          },
          {
            "date": "2025-03-18",
            "text": "Create list_code_files",
            "sha": "54189b5"
          },
          {
            "date": "2025-03-18",
            "text": "Fixed doc extension",
            "sha": "e07745f"
          },
          {
            "date": "2025-03-17",
            "text": "Update CLAUDE",
            "sha": "34d336a"
          },
          {
            "date": "2025-03-17",
            "text": "Minor breadcrumbs fix",
            "sha": "452265a"
          },
          {
            "date": "2025-03-17",
            "text": "Breadcrumbs",
            "sha": "d6459d0"
          },
          {
            "date": "2025-03-17",
            "text": "Tidied up index",
            "sha": "568c30d"
          },
          {
            "date": "2025-03-17",
            "text": "Fix disabled button styling to ensure consistent size with regular buttons Added span",
            "sha": "8e7c943"
          },
          {
            "date": "2025-03-17",
            "text": "Rename doc",
            "sha": "24a2e1c"
          },
          {
            "date": "2025-03-16",
            "text": "simple",
            "sha": "3b9026e"
          },
          {
            "date": "2025-03-16",
            "text": "We don't need set_secrets",
            "sha": "c7416b1"
          },
          {
            "date": "2025-03-16",
            "text": "Modify check_git_status",
            "sha": "294d21d"
          },
          {
            "date": "2025-03-16",
            "text": "Use index",
            "sha": "a4ea8a8"
          },
          {
            "date": "2025-03-16",
            "text": "Improve breadcrumbs",
            "sha": "4b2cfa2"
          },
          {
            "date": "2025-03-16",
            "text": "Gitignore screenshots",
            "sha": "3d06109"
          },
          {
            "date": "2025-03-16",
            "text": "Sort sourcefiles case-insensitively Modified sorting of sourcefiles to use case-insensitive comparison with fn",
            "sha": "d776ee0"
          },
          {
            "date": "2025-03-16",
            "text": "Add Delete button to sourcefile view",
            "sha": "7c71259"
          },
          {
            "date": "2025-03-16",
            "text": "Fix migrate",
            "sha": "dcac61b"
          },
          {
            "date": "2025-03-16",
            "text": "Update references from Fly",
            "sha": "26572ec"
          },
          {
            "date": "2025-03-16",
            "text": "Fixed url encoding for search views",
            "sha": "4109ed9"
          },
          {
            "date": "2025-03-16",
            "text": "Move search views to dedicated search_views",
            "sha": "97e1e74"
          },
          {
            "date": "2025-03-16",
            "text": "Remaining update for app",
            "sha": "5f01958"
          },
          {
            "date": "2025-03-16",
            "text": "Improved Flask logging",
            "sha": "0a251ed"
          },
          {
            "date": "2025-03-15",
            "text": "Show mobile upload options based on device detection instead of screen width - Added isMobileOrTablet() device detection function to base",
            "sha": "923b234"
          },
          {
            "date": "2025-03-15",
            "text": "Add line-limited logging with loguru - Replace standard logging with loguru for improved formatting and features - Create LimitingFileWriter class to maintain logs at max 100 lines - Set up interception for Flask/Werkzeug logs to capture all web requests - Refactor logging code into utils/logging_utils",
            "sha": "aa19778"
          },
          {
            "date": "2025-03-15",
            "text": "Add logs directory to gitignore - Ignore logs/ directory and all *",
            "sha": "5d716fb"
          },
          {
            "date": "2025-03-15",
            "text": "Add include_junction_data parameter to query methods",
            "sha": "bf59295"
          },
          {
            "date": "2025-03-15",
            "text": "Create CLAUDE",
            "sha": "9f9d5f5"
          },
          {
            "date": "2025-03-15",
            "text": "Add frontend logging to capture Vite dev server output - Configure run_frontend_dev",
            "sha": "798eba7"
          },
          {
            "date": "2025-03-15",
            "text": "Update",
            "sha": "c3eb2a8"
          },
          {
            "date": "2025-03-15",
            "text": "cursor-tools",
            "sha": "61a26b9"
          },
          {
            "date": "2025-03-15",
            "text": "Updated cursor-tools rule",
            "sha": "4c59339"
          },
          {
            "date": "2025-03-15",
            "text": "Disable Debug Toolbar",
            "sha": "0aa09b5"
          },
          {
            "date": "2025-03-15",
            "text": "Update",
            "sha": "00bccf5"
          },
          {
            "date": "2025-03-15",
            "text": "Store screenshots",
            "sha": "765bd8b"
          },
          {
            "date": "2025-03-15",
            "text": "Prompt template for inflected word forms",
            "sha": "9d7ac11"
          },
          {
            "date": "2025-03-15",
            "text": "Update CLAUDE",
            "sha": "59755a1"
          },
          {
            "date": "2025-03-15",
            "text": "Fix JSON serialization error with Anthropic client object Fix \"Processing failed: Object of type Anthropic is not JSON serializable\" error by using gjdutils",
            "sha": "a25d0f8"
          },
          {
            "date": "2025-03-15",
            "text": "Create",
            "sha": "e34a34d"
          },
          {
            "date": "2025-03-15",
            "text": "Rules",
            "sha": "58a438c"
          },
          {
            "date": "2025-03-15",
            "text": "Planning re hosting",
            "sha": "7248bed"
          },
          {
            "date": "2025-03-14",
            "text": "First attempt at MCP",
            "sha": "54531c9"
          },
          {
            "date": "2025-03-14",
            "text": "Fixed browser-tools-mcp",
            "sha": "51f8d2f"
          },
          {
            "date": "2025-03-14",
            "text": "Experim frontend view",
            "sha": "aafa884"
          },
          {
            "date": "2025-03-14",
            "text": "Updated the frontend documentation",
            "sha": "1c25986"
          },
          {
            "date": "2025-03-14",
            "text": "Updated mcp",
            "sha": "450dc66"
          },
          {
            "date": "2025-03-14",
            "text": "Update",
            "sha": "deb79f1"
          },
          {
            "date": "2025-03-09",
            "text": "Reduce number of threads for processing",
            "sha": "fd65466"
          },
          {
            "date": "2025-03-03",
            "text": "Don't need this doc any more",
            "sha": "1a81f9a"
          },
          {
            "date": "2025-03-02",
            "text": "Tweak to Greek language display, and to prompt templates re modern",
            "sha": "f4707b3"
          },
          {
            "date": "2025-03-02",
            "text": "Fixed hard-coded link to /el/",
            "sha": "608605a"
          },
          {
            "date": "2025-03-02",
            "text": "Cursor don't ignore",
            "sha": "606f673"
          },
          {
            "date": "2025-03-02",
            "text": "Fixes for renamed Greek language in config",
            "sha": "e6584aa"
          },
          {
            "date": "2025-03-02",
            "text": "Added lots of other cascade constraints",
            "sha": "0b53e95"
          },
          {
            "date": "2025-03-02",
            "text": "Fixed utils path issue",
            "sha": "2a57157"
          },
          {
            "date": "2025-03-02",
            "text": "Changing db connections config",
            "sha": "6adfd4d"
          },
          {
            "date": "2025-03-02",
            "text": "First set of changes for helloworld Vite etc",
            "sha": "85aef0a"
          },
          {
            "date": "2025-03-02",
            "text": "helloworld_newtech works with simple env switching",
            "sha": "1b8e870"
          },
          {
            "date": "2025-03-02",
            "text": "Got rid of Tailwind",
            "sha": "4a93050"
          },
          {
            "date": "2025-03-02",
            "text": "Fixed link",
            "sha": "fca22a8"
          }
        ]
      },
      {
        "id": "profile-user",
        "title": "Profile & User",
        "entries": [
          {
            "date": "2025-03-17",
            "text": "Fix auth redirection and profile form issues - Fix profile",
            "sha": "93168b8"
          },
          {
            "date": "2025-03-17",
            "text": "Update 029_add_profile_table",
            "sha": "2b9744c"
          },
          {
            "date": "2025-03-16",
            "text": "Auth v1 nearly works - still an issue with the profile page",
            "sha": "9c3fd75"
          },
          {
            "date": "2025-03-15",
            "text": "Improve directory deletion error messages Added more descriptive error message when a user tries to delete a directory containing files",
            "sha": "30cc50d"
          }
        ]
      },
      {
        "id": "ui-components",
        "title": "UI & Components",
        "entries": [
          {
            "date": "2025-03-31",
            "text": "Warning in out-of-date docs re SvelteKit",
            "sha": "f942aab"
          },
          {
            "date": "2025-03-31",
            "text": "Prepare SvelteKit for Vercel deployment and update Flask CORS settings",
            "sha": "6310ce6"
          },
          {
            "date": "2025-03-31",
            "text": "Update deployment scripts for dual Vercel setup (API + SvelteKit)",
            "sha": "bd6f287"
          },
          {
            "date": "2025-03-30",
            "text": "Extract LemmaCard component and implement across application",
            "sha": "8b0b268"
          },
          {
            "date": "2025-03-30",
            "text": "Add MetadataCard component for consistent timestamp display across pages",
            "sha": "11c72d9"
          },
          {
            "date": "2025-03-30",
            "text": "Add phrases_list_api and SvelteKit phrases route - Created phrases_list_api function in phrase_api",
            "sha": "9885ec4"
          },
          {
            "date": "2025-03-30",
            "text": "Enhance phrases page with improved styling and component design - Implemented a responsive grid layout for phrase cards - Added PhraseCard component with proper styling - Enhanced visual appeal with card shadows, hover effects, and transitions - Improved sort buttons with better styling - Updated color scheme to match project's design system - Better spacing and typography for improved readability",
            "sha": "0ec4905"
          },
          {
            "date": "2025-03-30",
            "text": "Added Phrase SvelteKit",
            "sha": "49810a2"
          },
          {
            "date": "2025-03-30",
            "text": "Improved Phrase in SvelteKit",
            "sha": "0fda6fe"
          },
          {
            "date": "2025-03-30",
            "text": "Implement Sourcefile page components and fix API routing - Create SourcefileWords component with WordformCard integration - Create SourcefilePhrases component with PhraseCard integration  - Update SourcefileHeader component with API actions (process, rename, delete) - Fix language_name error in page",
            "sha": "57cf915"
          },
          {
            "date": "2025-03-30",
            "text": "Implement dedicated tab routes for Sourcefile pages - Created separate route directories and files for Words and Phrases tabs - Added MetadataCard to both tab pages for consistent UI - Implemented WordformCard integration on Words page - Added PhraseCard integration on Phrases page - Implemented text tab redirect back to main sourcefile page - Updated main sourcefile page links to point to dedicated tab routes - Improved styling for tab navigation - Enhanced structure for better SEO with individual page URLs",
            "sha": "5b0f1b8"
          },
          {
            "date": "2025-03-30",
            "text": "Update Sourcefile routing to redirect bare URL to /text - Changed base Sourcefile URL to redirect to /text tab - Moved data fetching logic from root route to text tab - Created text tab page component with proper navigation - Updated links in all tab pages to consistently point to /text - Ensured breadcrumbs correctly link to the text tab for the file name - Maintained consistent tab styling and navigation across all pages",
            "sha": "8588c29"
          },
          {
            "date": "2025-03-30",
            "text": "Add timestamp metadata to Phrase to_dict method to display in MetadataCard component",
            "sha": "835aa2e"
          },
          {
            "date": "2025-03-30",
            "text": "Implement type-safe route integration between Flask and SvelteKit - Move TypeScript route generation to SvelteKit's lib/generated folder - Create type-safe API utilities (getApiUrl, apiFetch) - Update components to use typed route parameters - Standardize on target_language_code parameter naming - Update documentation with type-safety benefits - Refactor phrase detail and sources page to use the new approach  This change provides compile-time checking of API routes and parameters,  creates a single source of truth for routes, and improves IDE support  with autocomplete",
            "sha": "80b664f"
          },
          {
            "date": "2025-03-30",
            "text": "Fixed run_sveltekit",
            "sha": "7e98f31"
          },
          {
            "date": "2025-03-30",
            "text": "Fix route URLs using type-safe route resolution - Update Flask view URLs to use consistent /language/[code]/source/[dir]/[file] pattern - Refactor SvelteKit page server files to use RouteName enum with proper parameters - Replace hardcoded URLs with type-safe getApiUrl function calls - Fix inconsistencies between SvelteKit routing and Flask endpoints - Update routes",
            "sha": "8201976"
          },
          {
            "date": "2025-03-30",
            "text": "Fix languages search functionality Added proper reactivity to the language search feature on the languages page, using Svelte's reactive declarations for filtering and grouping languages",
            "sha": "66e9c12"
          },
          {
            "date": "2025-03-30",
            "text": "First stage of search -> SvelteKit Co-Authored-By: Claude <noreply@anthropic",
            "sha": "3570976"
          },
          {
            "date": "2025-03-30",
            "text": "Add search bar to all language-specific pages using SvelteKit layouts",
            "sha": "bd99e62"
          },
          {
            "date": "2025-03-30",
            "text": "Replace get_api_url with type-safe getApiUrl function in SvelteKit codebase - Replaced all occurrences of get_api_url with getApiUrl in flashcard components - Updated get_language_name function to use getApiUrl - Updated README",
            "sha": "a44d6cf"
          },
          {
            "date": "2025-03-30",
            "text": "Implement enhanced search functionality for SvelteKit - Create comprehensive search documentation in SEARCH",
            "sha": "4a10490"
          },
          {
            "date": "2025-03-29",
            "text": "Init sveltekit_hz",
            "sha": "f14a814"
          },
          {
            "date": "2025-03-29",
            "text": "Add language name API and improve SvelteKit backend integration - Added new language_name API endpoint in languages_api",
            "sha": "813151b"
          },
          {
            "date": "2025-03-29",
            "text": "Docs, including sveltekit_hz README",
            "sha": "b9f120e"
          },
          {
            "date": "2025-03-29",
            "text": "Tweaks for sveltekit_hz Sentence",
            "sha": "533e795"
          },
          {
            "date": "2025-03-29",
            "text": "Implement Bootstrap styling for SvelteKit - Added Bootstrap 5",
            "sha": "46038a6"
          },
          {
            "date": "2025-03-29",
            "text": "Refactor Bootstrap implementation for reusability - Created reusable UI components (Card, SourceItem) - Restructured CSS with separate theme-variables",
            "sha": "dc975ad"
          },
          {
            "date": "2025-03-29",
            "text": "Enhance languages page with modern design and fix search functionality - Redesigned the languages page with modern UI featuring animations, gradients and responsive layout - Fixed search functionality to filter by both language name and code - Made cards more compact to display more languages at once - Added hero section with stats and illustration - Improved card design with large letter background for visual interest - Implemented alphabetical navigation - Enhanced mobile responsiveness - Updated Card component to support the new styling",
            "sha": "03e8763"
          },
          {
            "date": "2025-03-29",
            "text": "Restructure SvelteKit documentation into separate files",
            "sha": "2fdc676"
          },
          {
            "date": "2025-03-29",
            "text": "Update run_sveltekit",
            "sha": "73135a4"
          },
          {
            "date": "2025-03-29",
            "text": "Add API endpoint for source directories and connect SvelteKit sources page to real API data",
            "sha": "382329a"
          },
          {
            "date": "2025-03-29",
            "text": "Improve Card component to prevent nested anchor tag errors - Added clear documentation to warn about nested anchor tags - Renamed href prop to linkUrl for clearer API semantics - Updated all component usages to match the new API - This change prevents the HierarchyRequestError that occurs when nesting <a> tags",
            "sha": "16b4deb"
          },
          {
            "date": "2025-03-29",
            "text": "Abstract sentences into SentenceCard component with dark theme styling",
            "sha": "55cecbe"
          },
          {
            "date": "2025-03-29",
            "text": "Add Lemma view in SvelteKit with SentenceCard component integration",
            "sha": "dd967a2"
          },
          {
            "date": "2025-03-29",
            "text": "Add wordforms API, components and route for SvelteKit implementation - Created wordforms_list_api endpoint in wordform_api",
            "sha": "5570ee3"
          },
          {
            "date": "2025-03-29",
            "text": "Add wordform metadata SvelteKit page - Create get_wordform_metadata API endpoint - Abstract common functionality into get_wordform_metadata utility  - Add SvelteKit route for wordform detail page - Style wordform page with improved layout and badges - Split inflection_type field into individual badges - Use subtle styling for metadata badges - Make lemma link prominent with a large button",
            "sha": "d7f7262"
          },
          {
            "date": "2025-03-29",
            "text": "Add flashcard API, utilities, and SvelteKit routes - Create a dedicated flashcard_utils",
            "sha": "a7c5df9"
          },
          {
            "date": "2025-03-29",
            "text": "Fix flashcards functionality in SvelteKit port This commit resolves issues with the flashcards functionality:  1",
            "sha": "8dcb00e"
          },
          {
            "date": "2025-03-23",
            "text": "Update all Svelte components to use URL registry Instead of hardcoded URL strings, Svelte components now use the URL registry system: - FlashcardApp",
            "sha": "70f31aa"
          },
          {
            "date": "2025-03-23",
            "text": "Frontend seems to work with --prod-frontend and not showing \"Loading xxx component\"",
            "sha": "7faa1df"
          },
          {
            "date": "2025-03-22",
            "text": "Add URL registry testing utilities and tests - Added build_url_with_query helper function for tests to safely create URLs with query parameters - Added get_route_registry helper to access the route registry in tests - Created test_url_registry",
            "sha": "4220ec8"
          },
          {
            "date": "2025-03-22",
            "text": "Add Jinja template integration for URL registry, examples, and documentation - Added comprehensive documentation for Jinja template URL generation - Created example Svelte component using TypeScript route utilities - Updated sourcefile",
            "sha": "b423c3a"
          },
          {
            "date": "2025-03-22",
            "text": "Update URL registry planning document - Mark completed template updates - Update Phase 3 status to 'In Progress' - Refine next steps for continuing the implementation - Add details about JavaScript and template migration",
            "sha": "a86226f"
          },
          {
            "date": "2025-03-22",
            "text": "Fix trailing slash issue with wordforms view and use build_url_with_query for all tests - Added trailing slash to wordforms URL route (`/lang/{lang}/wordforms/`) - Updated utils_for_testing",
            "sha": "bb06f2f"
          },
          {
            "date": "2025-03-22",
            "text": "Replace hardcoded URLs with build_url_with_query in remaining tests - Updated test_lemma_views",
            "sha": "c5c7345"
          },
          {
            "date": "2025-03-22",
            "text": "In progress replacing test hardcoded urls with build_url_with_query",
            "sha": "92ebb70"
          },
          {
            "date": "2025-03-22",
            "text": "More build_url_with_query and languages_list_vw rename",
            "sha": "fd640e9"
          },
          {
            "date": "2025-03-17",
            "text": "Fixed tooltips with new URL structure",
            "sha": "a5aa6cc"
          },
          {
            "date": "2025-03-17",
            "text": "Fix Svelte components CSS loading in production - Added dedicated Flask route to serve CSS files dynamically - Modified template to use a consistent CSS path that doesn't depend on hash values - Simple solution that automatically adapts to new CSS files after rebuilds",
            "sha": "5a1dbb2"
          },
          {
            "date": "2025-03-17",
            "text": "Add draft investigation document for Svelte CSS loading issues",
            "sha": "2a56d4f"
          },
          {
            "date": "2025-03-17",
            "text": "Fix URL structure for audio generation in Sentence component - Update API routes in sentence_views",
            "sha": "5832946"
          },
          {
            "date": "2025-03-16",
            "text": "Fix CSS scoping issue for sentence component in production Changed from nested :global() selectors to top-level :global() blocks for better CSS compatibility between development and production",
            "sha": "b82ba62"
          },
          {
            "date": "2025-03-16",
            "text": "Further simplify CSS global styles in Sentence component Made paragraph and line break styles globally available instead of restricting to target-lang-text class, resolving CSS issues in production",
            "sha": "1cd743d"
          },
          {
            "date": "2025-03-16",
            "text": "Switched to functions instead of builds",
            "sha": "ec61779"
          },
          {
            "date": "2025-03-16",
            "text": "Update build-frontend",
            "sha": "0bd3172"
          },
          {
            "date": "2025-03-16",
            "text": "Always build frontend assets",
            "sha": "5b8c675"
          },
          {
            "date": "2025-03-16",
            "text": "Trying to fix Svelte imports",
            "sha": "0d0696e"
          },
          {
            "date": "2025-03-16",
            "text": "Add Practice Flashcards buttons to language pages - Add Practice Flashcards button to language index page (/el/) - Style the buttons consistently with existing design patterns",
            "sha": "13f8e4f"
          },
          {
            "date": "2025-03-16",
            "text": "Fix Svelte component styling in production environment This commit resolves styling issues with Svelte components in production by: - Adding CSS manifest loading to the Flask app - Configuring Vite to generate a single CSS file instead of code-splitting - Explicitly loading the CSS file in the base_svelte template - Adding fallback paths for when the manifest isn't available",
            "sha": "f527b68"
          },
          {
            "date": "2025-03-16",
            "text": "Fix tooltip preview by adding explicit URL unquote to API endpoints Added explicit URL unquoting to both word-preview and phrase-preview API endpoints to handle Greek character encoding properly in Vercel environment",
            "sha": "79022b0"
          },
          {
            "date": "2025-03-16",
            "text": "Implement WhiteNoise for static file serving in Vercel serverless environment - Add WhiteNoise dependency to requirements",
            "sha": "00c0845"
          },
          {
            "date": "2025-03-16",
            "text": "Fix auth redirect issue with trailing slashes - Fixed issue where auth redirect with trailing slash causes language code error - Added check in AuthPage component to remove trailing slash from auth URLs - Added server-side handling to redirect /auth/ to /auth",
            "sha": "0d599fe"
          },
          {
            "date": "2025-03-16",
            "text": "Fix profile page route to handle language codes properly - Updated profile route to handle language codes and trailing slashes - Added target_language_code=None to profile template context to avoid errors - Improved UserStatus component to ensure clean profile URL link",
            "sha": "7fd6a78"
          },
          {
            "date": "2025-03-16",
            "text": "Fix profile page redirect and template errors - Fixed profile page template to explicitly include target_language_name - Improved page_auth_required decorator to handle redirect URLs better - Enhanced UserStatus component to avoid trailing slash issues",
            "sha": "dc81578"
          },
          {
            "date": "2025-03-15",
            "text": "Static local versions of most js and css",
            "sha": "89d61f7"
          },
          {
            "date": "2025-03-15",
            "text": "Fixing Svelte naming issues",
            "sha": "e68eb3d"
          },
          {
            "date": "2025-03-15",
            "text": "Enhance sentence view with rich lemma displays - Add API endpoint to fetch detailed lemma information - Replace simple lemma links with MiniLemma Svelte component in sentences - Show full lemma info including part of speech and translations - Improve lemma detection by combining database links and matched wordforms - Add loading indicator during lemma data fetching",
            "sha": "c0278ba"
          },
          {
            "date": "2025-03-15",
            "text": "Fix inconsistent Svelte entry naming in vite",
            "sha": "e6e490f"
          },
          {
            "date": "2025-03-15",
            "text": "Add MiniWordformList component for better encapsulation - Create new MiniWordformList Svelte component and entry point - Update vite",
            "sha": "5aaa39d"
          },
          {
            "date": "2025-03-15",
            "text": "Fix Svelte component loading in production environment - Remove incorrect '-entry' suffix from production JS imports to match Vite output - Fix debugLog function to be a proper no-op in production - Simplify component loading code for better reliability - Remove redundant debug logging and fetch test",
            "sha": "97b96a3"
          },
          {
            "date": "2025-03-15",
            "text": "Add MiniPhrase Svelte component for consistent phrase display - Create MiniPhrase Svelte component for displaying phrases with consistent styling - Add phrase-preview API endpoint for future tooltip functionality (currently disabled) - Update templates to use MiniPhrase in sourcefile_phrases",
            "sha": "87b7a3b"
          },
          {
            "date": "2025-03-15",
            "text": "Fix Svelte components in production environment - Add custom Vite plugin to ensure component exports are correctly generated - Fix component URL path in production template (remove -entry",
            "sha": "7b910cf"
          },
          {
            "date": "2025-03-15",
            "text": "Simplify and fix frontend tests - Updated test fixtures to handle existing data with get_or_create pattern - Simplified frontend tests to remove debugging-focused code - Changed Flask test port to avoid conflicts - Added skip markers to frontend component tests requiring special setup - Used patterns from backend tests for improved consistency",
            "sha": "bfe8191"
          },
          {
            "date": "2025-03-15",
            "text": "Add Svelte-based flashcards2 system with staged learning This commit adds a new flashcard system built with Svelte and TypeScript: - Created flashcard2_views",
            "sha": "09f7533"
          },
          {
            "date": "2025-03-15",
            "text": "Fix URL paths for Svelte components in production - Update base_svelte",
            "sha": "a4665c0"
          },
          {
            "date": "2025-03-15",
            "text": "Fix Svelte components in production using library mode - Implement Vite's library mode for component building - Create central component registry in index",
            "sha": "e69124c"
          },
          {
            "date": "2025-03-15",
            "text": "Fix Docker build: add",
            "sha": "b4080c9"
          },
          {
            "date": "2025-03-15",
            "text": "Implement Svelte-based flashcards system with UMD pattern - Fixed module loading issues using UMD pattern - Updated ENTER keyboard shortcut to work document-wide - Added detailed documentation about the implementation approach - Added improved test coverage for the flashcard components - Updated FRONTEND_INFRASTRUCTURE",
            "sha": "1013fb1"
          },
          {
            "date": "2025-03-15",
            "text": "Bundle Svelte runtime into UMD build to avoid CDN dependencies - Updated vite",
            "sha": "ebea815"
          },
          {
            "date": "2025-03-15",
            "text": "Include static/build in Docker deployment",
            "sha": "c9b3713"
          },
          {
            "date": "2025-03-15",
            "text": "Create 250315_UMD_for_Svelte",
            "sha": "e3ece2f"
          },
          {
            "date": "2025-03-15",
            "text": "Add sourcefile/sourcedir filtering to Flashcards v2 - Added \"Practice Flashcards v2\" buttons to sourcefile and sourcedir pages - Added source filter banner to display current filter context - Enhanced FlashcardApp and FlashcardLanding components to show filtering info - Implemented \"Clear filter\" button to remove current filter",
            "sha": "f393e30"
          },
          {
            "date": "2025-03-15",
            "text": "Consolidate flashcards to single implementation by merging v2 into main - Replace flashcards v1 with the Svelte-based flashcards system (previously v2) - Update all routes from /flashcards2 to /flashcards - Rename template files and update templates - Update button labels to remove \"v1\" and \"v2\" references - Fix audio autoplay on mobile devices with HTML5 autoplay attribute - Improve error message for audio playback failures  🤖 Generated with [Claude Code](https://claude",
            "sha": "6eb6fa9"
          },
          {
            "date": "2025-03-15",
            "text": "Add interactive vocabulary words to flashcards - Replace simple text list of lemma words with interactive MiniLemma components - Add functionality to fetch lemma data from the API in stage 3 - Improve styling for vocabulary section in flashcards - Reuse existing MiniLemma component for consistent UI across the app",
            "sha": "cb4bdac"
          },
          {
            "date": "2025-03-15",
            "text": "Standardize Svelte component loading by removing UMD approach - Convert flashcard components from UMD to standard ES modules - Update base_svelte",
            "sha": "31d2f6c"
          },
          {
            "date": "2025-03-15",
            "text": "Fix Svelte component loading in production - Remove code in base",
            "sha": "9f494b3"
          },
          {
            "date": "2025-03-15",
            "text": "Add planning doc for Svelte ES modules standardization - Document the standardization of Svelte component loading - Explain reasoning behind ES modules over UMD approach - Track completed actions and future improvements",
            "sha": "60c1729"
          },
          {
            "date": "2025-03-15",
            "text": "Remove loading placeholder message from Svelte components - Remove the \"Loading component",
            "sha": "fb36e3c"
          },
          {
            "date": "2025-03-15",
            "text": "Fix Svelte warning for unused export property Changed FlashcardApp's targetLanguageName from 'export let' to 'export const' since it's passed from the template but not used within the component",
            "sha": "3b5f23a"
          },
          {
            "date": "2025-03-14",
            "text": "More mobile CSS changes",
            "sha": "f3d55d0"
          },
          {
            "date": "2025-03-14",
            "text": "updated docs for Svelte front-end debugging",
            "sha": "e28662e"
          },
          {
            "date": "2025-03-14",
            "text": "Add MiniLemma Svelte component for displaying lemma entries",
            "sha": "57cb8f0"
          },
          {
            "date": "2025-03-14",
            "text": "Replace MiniWordform with MiniLemma component in wordforms list",
            "sha": "059dc86"
          },
          {
            "date": "2025-03-14",
            "text": "Revert \"Replace MiniWordform with MiniLemma component in wordforms list\" This reverts commit 059dc867c25cd5cca1ca1a886c5b5920f5e6a288",
            "sha": "334caf2"
          },
          {
            "date": "2025-03-14",
            "text": "Use MiniLemma Svelte component in lemmas",
            "sha": "a285f5e"
          },
          {
            "date": "2025-03-14",
            "text": "Fix Svelte component naming and loading issues - Renamed miniwordform-entry",
            "sha": "e8cfde0"
          },
          {
            "date": "2025-03-03",
            "text": "Added MiniSentence component to lemma view",
            "sha": "5527f7c"
          },
          {
            "date": "2025-03-03",
            "text": "MiniWordform sort of has working tooltips",
            "sha": "9eba7f3"
          },
          {
            "date": "2025-03-02",
            "text": "New Tailwind base styles, lemma",
            "sha": "f92e27e"
          },
          {
            "date": "2025-03-02",
            "text": "More lemma CSS changes - not so sure about Tailwind",
            "sha": "234e8fc"
          },
          {
            "date": "2025-03-02",
            "text": "Sentence works with Svelte and ok styling But lemma is broken",
            "sha": "fdf6b06"
          }
        ]
      }
    ]
  },
  {
    "id": "february-2025",
    "title": "February 2025",
    "themes": [
      {
        "id": "auth-security",
        "title": "Auth & Security",
        "entries": [
          {
            "date": "2025-02-17",
            "text": "Imported prod dump into Supabase",
            "sha": "9ea6387"
          },
          {
            "date": "2025-02-17",
            "text": "About to try first deploy with Supabase",
            "sha": "20cea49"
          },
          {
            "date": "2025-02-16",
            "text": "Begin Supabase migration: Update env files and docs - Switch to DATABASE_URL connection string  - Add local-to-prod debugging mode  - Update DATABASE",
            "sha": "07a806e"
          },
          {
            "date": "2025-02-16",
            "text": "refactor: Update database connection to use DATABASE_URL for Supabase - Update env_config",
            "sha": "4829ebe"
          }
        ]
      },
      {
        "id": "backend-database",
        "title": "Backend & Database",
        "entries": [
          {
            "date": "2025-02-25",
            "text": "Fixed migrations 017 and 019",
            "sha": "a71fe09"
          },
          {
            "date": "2025-02-25",
            "text": "Fixed 019 migration (and added migrate_local_to_prod",
            "sha": "e443121"
          },
          {
            "date": "2025-02-24",
            "text": "Checking migrations",
            "sha": "a375843"
          },
          {
            "date": "2025-02-17",
            "text": "Fixed localhost database (which doesn't expect SSL)",
            "sha": "8370bfa"
          },
          {
            "date": "2025-02-17",
            "text": "Updated remaining Fly-database-related issues",
            "sha": "10af656"
          },
          {
            "date": "2025-02-09",
            "text": "Using pytest-postgresql (UNTESTED) also renamed test_db fixture -> fixture_for_testing_db",
            "sha": "8904b48"
          },
          {
            "date": "2025-02-09",
            "text": "Using pytest-postgresql (UNTESTED) also renamed test_db fixture -> fixture_for_testing_db",
            "sha": "4aba5c3"
          },
          {
            "date": "2025-02-09",
            "text": "Added API keys to",
            "sha": "38d0680"
          },
          {
            "date": "2025-02-09",
            "text": "Added API keys to",
            "sha": "6069c65"
          },
          {
            "date": "2025-02-09",
            "text": "Don't send API keys in",
            "sha": "ef9b52b"
          },
          {
            "date": "2025-02-09",
            "text": "Don't send API keys in",
            "sha": "5ba3fa9"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed tests/backend/conftest import issue",
            "sha": "1d22b61"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed tests/backend/conftest import issue",
            "sha": "cd8265a"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed migration to use correct utils/migrate",
            "sha": "032dafe"
          }
        ]
      },
      {
        "id": "deployment-ops",
        "title": "Deployment & Ops",
        "entries": [
          {
            "date": "2025-02-17",
            "text": "Reorganised scripts still need to update docs",
            "sha": "b677403"
          },
          {
            "date": "2025-02-17",
            "text": "Updated docs from scripts reorg",
            "sha": "9811f4f"
          },
          {
            "date": "2025-02-17",
            "text": "Make deployment scripts executable",
            "sha": "2439f15"
          },
          {
            "date": "2025-02-17",
            "text": "Removed duplicate scripts that somehow got returned when we did the Git fixing",
            "sha": "207f737"
          },
          {
            "date": "2025-02-09",
            "text": "Tests and local seem to be working, bash scripts updated but I haven't tried deploying",
            "sha": "373d674"
          },
          {
            "date": "2025-02-09",
            "text": "Tests and local seem to be working, bash scripts updated but I haven't tried deploying",
            "sha": "304d173"
          },
          {
            "date": "2025-02-09",
            "text": "Moved out _secrets, nearly finished with env still need to test deploy etc",
            "sha": "82f3cfc"
          },
          {
            "date": "2025-02-09",
            "text": "Moved out _secrets, nearly finished with env still need to test deploy etc",
            "sha": "1fc4e14"
          },
          {
            "date": "2025-02-09",
            "text": "Dockerignore",
            "sha": "503dba9"
          }
        ]
      },
      {
        "id": "docs-testing",
        "title": "Documentation & Testing",
        "entries": [
          {
            "date": "2025-02-25",
            "text": "Fixed normalisation tests (not sure why they were broken already)",
            "sha": "05cde09"
          },
          {
            "date": "2025-02-17",
            "text": "Getting tests working",
            "sha": "8103e03"
          },
          {
            "date": "2025-02-16",
            "text": "Renamed gdutils -> gjdutils tests are passing",
            "sha": "d7f4b26"
          },
          {
            "date": "2025-02-09",
            "text": "Slowly making progress getting tests to run",
            "sha": "056ef50"
          },
          {
            "date": "2025-02-09",
            "text": "Slowly making progress getting tests to run",
            "sha": "c864576"
          },
          {
            "date": "2025-02-09",
            "text": "Moved out mocks into tests/mocks lots of tests failing, for all sorts of reasons",
            "sha": "b2f6369"
          },
          {
            "date": "2025-02-09",
            "text": "Moved out mocks into tests/mocks lots of tests failing, for all sorts of reasons",
            "sha": "c0dc924"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed test import errors",
            "sha": "9bd54a9"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed test import errors",
            "sha": "534acdc"
          },
          {
            "date": "2025-02-09",
            "text": "Moved fixtures/ -> tests/fixtures/",
            "sha": "ada3c02"
          },
          {
            "date": "2025-02-09",
            "text": "Moved fixtures/ -> tests/fixtures/",
            "sha": "0c2d4bf"
          },
          {
            "date": "2025-02-09",
            "text": "Moved tests/test_*",
            "sha": "13b6390"
          },
          {
            "date": "2025-02-09",
            "text": "Moved tests/test_*",
            "sha": "0f68c03"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed a few unit tests",
            "sha": "50bf9b2"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed a few unit tests",
            "sha": "b2c6a42"
          },
          {
            "date": "2025-02-09",
            "text": "test_word_utils passes",
            "sha": "1db786c"
          },
          {
            "date": "2025-02-09",
            "text": "test_word_utils passes",
            "sha": "04e431c"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed test_vocab_llm_utils mock",
            "sha": "a94d5e3"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed test_vocab_llm_utils mock",
            "sha": "1c6bf2c"
          },
          {
            "date": "2025-02-08",
            "text": "Updated conftest",
            "sha": "65433c3"
          },
          {
            "date": "2025-02-08",
            "text": "Updated conftest",
            "sha": "1162709"
          }
        ]
      },
      {
        "id": "flashcards-content",
        "title": "Flashcards & Content",
        "entries": [
          {
            "date": "2025-02-17",
            "text": "Fixed issue with missing lemma",
            "sha": "b6a6446"
          },
          {
            "date": "2025-02-09",
            "text": "Hopefully sped up sentence query for flashcards",
            "sha": "3d9c97b"
          }
        ]
      },
      {
        "id": "misc",
        "title": "Miscellaneous",
        "entries": [
          {
            "date": "2025-02-25",
            "text": "Removed duplicate/old db_connection",
            "sha": "dd6f305"
          },
          {
            "date": "2025-02-25",
            "text": "Fixed migrate",
            "sha": "94b7e40"
          },
          {
            "date": "2025-02-25",
            "text": "Fixed prod migrate",
            "sha": "fe8e65a"
          },
          {
            "date": "2025-02-25",
            "text": "Added Sourcefile",
            "sha": "9052d29"
          },
          {
            "date": "2025-02-25",
            "text": "Made Sourcefile buttons command-clickable and visually consistent",
            "sha": "8606937"
          },
          {
            "date": "2025-02-25",
            "text": "Add ON DELETE CASCADE constraints to sourcefile relations and simplify delete_sourcefile function",
            "sha": "7b6444c"
          },
          {
            "date": "2025-02-25",
            "text": "Update 019_standardize_unicode_normalization",
            "sha": "7c864bf"
          },
          {
            "date": "2025-02-24",
            "text": "Pick a random voice",
            "sha": "1c5f4a5"
          },
          {
            "date": "2025-02-23",
            "text": "Ignore gjdutils rules",
            "sha": "cd636c7"
          },
          {
            "date": "2025-02-17",
            "text": "Updated env_config",
            "sha": "0645309"
          },
          {
            "date": "2025-02-17",
            "text": "Added export_envs",
            "sha": "28b60ed"
          },
          {
            "date": "2025-02-17",
            "text": "Moved and renamed verify_db_connection",
            "sha": "9e51edd"
          },
          {
            "date": "2025-02-17",
            "text": "Got verify_db_connection",
            "sha": "35f3615"
          },
          {
            "date": "2025-02-17",
            "text": "Use standard pip gjdutils",
            "sha": "2f0f21a"
          },
          {
            "date": "2025-02-17",
            "text": "Fixed check_health",
            "sha": "3a7f51d"
          },
          {
            "date": "2025-02-17",
            "text": "Merge preserved-work-main into main, keeping all recent changes",
            "sha": "8af1cf2"
          },
          {
            "date": "2025-02-16",
            "text": "Lower-case type",
            "sha": "a832b06"
          },
          {
            "date": "2025-02-16",
            "text": "Improved PROJECT_MANAGEMENT",
            "sha": "01ceaa5"
          },
          {
            "date": "2025-02-16",
            "text": "Gitignore",
            "sha": "4b1a7d8"
          },
          {
            "date": "2025-02-09",
            "text": "Big tidy-up of env in config",
            "sha": "cb71f68"
          },
          {
            "date": "2025-02-09",
            "text": "Big tidy-up of env in config",
            "sha": "fd00f62"
          },
          {
            "date": "2025-02-09",
            "text": "Trying to simplify db_connection",
            "sha": "1891ace"
          },
          {
            "date": "2025-02-09",
            "text": "Trying to simplify db_connection",
            "sha": "0c5e927"
          },
          {
            "date": "2025-02-09",
            "text": "Connect & backup by proxy worked!",
            "sha": "a72754e"
          },
          {
            "date": "2025-02-09",
            "text": "Connect & backup by proxy worked!",
            "sha": "6107758"
          },
          {
            "date": "2025-02-09",
            "text": "Don't reboot after setting each secret",
            "sha": "115f89e"
          },
          {
            "date": "2025-02-09",
            "text": "Don't reboot after setting each secret",
            "sha": "ec1710f"
          },
          {
            "date": "2025-02-09",
            "text": "Oops, updated the obsolete set_secrets",
            "sha": "75ae1d9"
          },
          {
            "date": "2025-02-09",
            "text": "Oops, updated the obsolete set_secrets",
            "sha": "d616030"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed issue with comment",
            "sha": "e74a0be"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed issue with comment",
            "sha": "6baaa7c"
          },
          {
            "date": "2025-02-09",
            "text": "Removed secrets from fly",
            "sha": "39485c6"
          },
          {
            "date": "2025-02-09",
            "text": "Removed secrets from fly",
            "sha": "fbb1b9d"
          },
          {
            "date": "2025-02-09",
            "text": "Moved *_views",
            "sha": "085596c"
          },
          {
            "date": "2025-02-09",
            "text": "Moved *_views",
            "sha": "53dda35"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed language_name breadcrumb",
            "sha": "1132e67"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed language_name breadcrumb",
            "sha": "eda0b4c"
          },
          {
            "date": "2025-02-09",
            "text": "Moved health-check etc out to system_views and utils",
            "sha": "fa3de5f"
          },
          {
            "date": "2025-02-09",
            "text": "Moved health-check etc out to system_views and utils",
            "sha": "f27ad9a"
          },
          {
            "date": "2025-02-09",
            "text": "Moved lots into utils/",
            "sha": "d5aefc5"
          },
          {
            "date": "2025-02-09",
            "text": "Moved lots into utils/",
            "sha": "fda03e4"
          },
          {
            "date": "2025-02-09",
            "text": "Moved favicon() to views",
            "sha": "213fea3"
          },
          {
            "date": "2025-02-09",
            "text": "Moved favicon() to views",
            "sha": "eb2a9f6"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed another import error",
            "sha": "a65d6ba"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed another import error",
            "sha": "25a3267"
          },
          {
            "date": "2025-02-09",
            "text": "Removed",
            "sha": "2a3634b"
          },
          {
            "date": "2025-02-09",
            "text": "Removed",
            "sha": "5ebc29c"
          },
          {
            "date": "2025-02-09",
            "text": "Added support for",
            "sha": "73888e5"
          },
          {
            "date": "2025-02-09",
            "text": "Added support for",
            "sha": "4a471a1"
          },
          {
            "date": "2025-02-09",
            "text": "Updated references to `utils/migrate",
            "sha": "89a56b5"
          },
          {
            "date": "2025-02-09",
            "text": "Updated references to `utils/migrate",
            "sha": "387f33d"
          },
          {
            "date": "2025-02-09",
            "text": "Removed unused imports",
            "sha": "22a5ca3"
          },
          {
            "date": "2025-02-09",
            "text": "Removed unused imports",
            "sha": "a13d616"
          },
          {
            "date": "2025-02-09",
            "text": "Some light refactoring",
            "sha": "16c7850"
          },
          {
            "date": "2025-02-09",
            "text": "Some light refactoring",
            "sha": "73a7fc2"
          },
          {
            "date": "2025-02-09",
            "text": "Fixing Pydantic env_config",
            "sha": "e5b7553"
          },
          {
            "date": "2025-02-09",
            "text": "Fixing Pydantic env_config",
            "sha": "ce1d3e8"
          },
          {
            "date": "2025-02-09",
            "text": "Trying to fix word_utils",
            "sha": "4ace2b9"
          },
          {
            "date": "2025-02-09",
            "text": "Trying to fix word_utils",
            "sha": "0ba4dc2"
          },
          {
            "date": "2025-02-09",
            "text": "Gitignore obsolete/",
            "sha": "513c9bb"
          },
          {
            "date": "2025-02-09",
            "text": "Gitignore obsolete/",
            "sha": "bf73130"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed flask secret key config",
            "sha": "ed90943"
          },
          {
            "date": "2025-02-09",
            "text": "Fixed flask secret key config",
            "sha": "187d60e"
          },
          {
            "date": "2025-02-09",
            "text": "Updated migrate_fly",
            "sha": "7a2310f"
          },
          {
            "date": "2025-02-09",
            "text": "Removed duplicate db_connection",
            "sha": "b800eb0"
          },
          {
            "date": "2025-02-08",
            "text": "Initial commit",
            "sha": "67afc7d"
          },
          {
            "date": "2025-02-08",
            "text": "Initial commit",
            "sha": "10dbed7"
          },
          {
            "date": "2025-02-08",
            "text": "Moved from spideryarn/241103_vocab",
            "sha": "9ee7d82"
          },
          {
            "date": "2025-02-08",
            "text": "Moved from spideryarn/241103_vocab",
            "sha": "3cb272b"
          },
          {
            "date": "2025-02-08",
            "text": "First stage of env planning and dotfile creation",
            "sha": "6679fa9"
          },
          {
            "date": "2025-02-08",
            "text": "First stage of env planning and dotfile creation",
            "sha": "eca92a7"
          },
          {
            "date": "2025-02-08",
            "text": "Reworked env_config",
            "sha": "3d1cb51"
          },
          {
            "date": "2025-02-08",
            "text": "Reworked env_config",
            "sha": "785834a"
          },
          {
            "date": "2025-02-08",
            "text": "Moved out google_cloud_run_utils to obsolete/",
            "sha": "7a988cf"
          },
          {
            "date": "2025-02-08",
            "text": "Moved out google_cloud_run_utils to obsolete/",
            "sha": "9b83384"
          },
          {
            "date": "2025-02-08",
            "text": "Store obsolete/ in Git, just in case",
            "sha": "86403c1"
          },
          {
            "date": "2025-02-08",
            "text": "Store obsolete/ in Git, just in case",
            "sha": "cc9db31"
          },
          {
            "date": "2025-02-08",
            "text": "Updated to use env_config",
            "sha": "e10ce43"
          },
          {
            "date": "2025-02-08",
            "text": "Updated to use env_config",
            "sha": "ed9b632"
          },
          {
            "date": "2025-02-08",
            "text": "Updated",
            "sha": "f0ae705"
          },
          {
            "date": "2025-02-08",
            "text": "Updated",
            "sha": "4ab9e97"
          },
          {
            "date": "2025-02-08",
            "text": "Setting Fly secrets",
            "sha": "12b93e6"
          },
          {
            "date": "2025-02-08",
            "text": "Setting Fly secrets",
            "sha": "5d5220b"
          }
        ]
      },
      {
        "id": "ui-components",
        "title": "UI & Components",
        "entries": [
          {
            "date": "2025-02-25",
            "text": "Fixed the weird unicode bug with τροφή in tooltip preview",
            "sha": "e8344f5"
          },
          {
            "date": "2025-02-17",
            "text": "Update gjdutils requirement to use Git repository",
            "sha": "c3e8d4e"
          },
          {
            "date": "2025-02-09",
            "text": "Don't require",
            "sha": "15844df"
          }
        ]
      }
    ]
  },
  {
    "id": "april-2025",
    "title": "April 2025",
    "themes": [
      {
        "id": "auth-security",
        "title": "Auth & Security",
        "entries": [
          {
            "date": "2025-04-27",
            "text": "Added default sort to lemmas and phrases Co-Authored-By: Claude <noreply@anthropic",
            "sha": "50f3a1a"
          },
          {
            "date": "2025-04-27",
            "text": "Show the default sort with an arrow in the column Co-Authored-By: Claude <noreply@anthropic",
            "sha": "9107a85"
          },
          {
            "date": "2025-04-26",
            "text": "Tried to add Supabase-js type generation (not sure if it's working) it's running as part of run_frontend",
            "sha": "7e0a4c8"
          },
          {
            "date": "2025-04-25",
            "text": "Supabase confirm-signup email template",
            "sha": "4a5e7ed"
          },
          {
            "date": "2025-04-25",
            "text": "If you're already logged in, then /auth redirects you",
            "sha": "9e80817"
          },
          {
            "date": "2025-04-24",
            "text": "Update confirm_signup",
            "sha": "bc26b5d"
          },
          {
            "date": "2025-04-23",
            "text": "Updating colours as per 250423 planning doc  Co-Authored-By: Claude <noreply@anthropic",
            "sha": "aa66cae"
          },
          {
            "date": "2025-04-23",
            "text": "About and FAQ backgrounds look ok Co-Authored-By: Claude <noreply@anthropic",
            "sha": "fe14818"
          },
          {
            "date": "2025-04-22",
            "text": "Fixed Flashcards auth issue",
            "sha": "64d3295"
          },
          {
            "date": "2025-04-22",
            "text": "Renamed Supabase_local MCP",
            "sha": "cde6728"
          },
          {
            "date": "2025-04-21",
            "text": "fix(auth): Use validated session in search server load, add plan doc",
            "sha": "8b9fe87"
          },
          {
            "date": "2025-04-21",
            "text": "Another fix re Supabase getSession warning",
            "sha": "4dfe87d"
          },
          {
            "date": "2025-04-20",
            "text": "Fixed lemma login-gating",
            "sha": "2657cb2"
          },
          {
            "date": "2025-04-20",
            "text": "Fix Supabase client serialization errors in Sourcefile tabs - Fixed 500 errors in all Sourcefile tabs (image, audio, words, phrases, translation) - Removed non-serializable Supabase client from server-to-client data flow - Updated all tab page",
            "sha": "8fa98ea"
          },
          {
            "date": "2025-04-20",
            "text": "Removed signup alert",
            "sha": "f48d175"
          },
          {
            "date": "2025-04-20",
            "text": "Fix: Validate 'next' param in /auth to prevent open redirect and loops",
            "sha": "7b7d3f3"
          },
          {
            "date": "2025-04-20",
            "text": "Fixing auth redirect to language homepage but the site logo link is not right",
            "sha": "6a280b0"
          },
          {
            "date": "2025-04-20",
            "text": "Update authentication documentation - Enhance AUTH",
            "sha": "7483167"
          },
          {
            "date": "2025-04-20",
            "text": "Fixed search 401 login-gating",
            "sha": "582fd7a"
          },
          {
            "date": "2025-04-19",
            "text": "Seemingly fixed the auth issue when processing, but now it's in a loop",
            "sha": "d4cfc46"
          },
          {
            "date": "2025-04-19",
            "text": "Switched to supabase/SSR library for auth",
            "sha": "f85f307"
          },
          {
            "date": "2025-04-18",
            "text": "Login to process text",
            "sha": "2f30190"
          },
          {
            "date": "2025-04-12",
            "text": "Renamed rule Co-Authored-By: Claude <noreply@anthropic",
            "sha": "97d9415"
          },
          {
            "date": "2025-04-12",
            "text": "Finished rename of language_code -> target_language_code Co-Authored-By: Claude <noreply@anthropic",
            "sha": "0a5e9c9"
          },
          {
            "date": "2025-04-12",
            "text": "Include more translations in lemma Co-Authored-By: Claude <noreply@anthropic",
            "sha": "f1fe186"
          },
          {
            "date": "2025-04-12",
            "text": "Docs Co-Authored-By: Claude <noreply@anthropic",
            "sha": "26cb2b5"
          },
          {
            "date": "2025-04-12",
            "text": "Rename rules Co-Authored-By: Claude <noreply@anthropic",
            "sha": "865315a"
          },
          {
            "date": "2025-04-11",
            "text": "Supabase_prod MCP",
            "sha": "2b36530"
          },
          {
            "date": "2025-04-08",
            "text": "Comment Co-Authored-By: Claude <noreply@anthropic",
            "sha": "400b5da"
          },
          {
            "date": "2025-04-08",
            "text": "Superfluous mis-installation Co-Authored-By: Claude <noreply@anthropic",
            "sha": "c80ed26"
          },
          {
            "date": "2025-04-05",
            "text": "Fixe prompt templates DIRN reference Co-Authored-By: Claude <noreply@anthropic",
            "sha": "468dfe7"
          },
          {
            "date": "2025-04-05",
            "text": "Docs re Vercel logs Co-Authored-By: Claude <noreply@anthropic",
            "sha": "8895d26"
          },
          {
            "date": "2025-04-05",
            "text": "Less verbose logging Co-Authored-By: Claude <noreply@anthropic",
            "sha": "31ca74e"
          }
        ]
      },
      {
        "id": "backend-database",
        "title": "Backend & Database",
        "entries": [
          {
            "date": "2025-04-26",
            "text": "Migrations for adding various fields, including created_by migrations seemed to run successfully, pages work",
            "sha": "04632bd"
          },
          {
            "date": "2025-04-23",
            "text": "Add timestamp fields to Sourcedir API - Added created_at and updated_at timestamp fields to the Sourcedir API responses - Fixed metadata section in SourcedirHeader showing 'undefined' for timestamps - Ensured both API endpoints (list and detail) include timestamp data - Updated sourcedir_utils to include timestamps in sourcedir dictionaries",
            "sha": "89d089f"
          },
          {
            "date": "2025-04-22",
            "text": "Added trim to apiFetch to try and fix issues with Flashcards random",
            "sha": "0357d4b"
          },
          {
            "date": "2025-04-20",
            "text": "Add API support for image and audio tabs in Sourcefile pages - Added new API endpoints for image and audio tabs - Updated the sourcefile_utils",
            "sha": "f7e6dc6"
          },
          {
            "date": "2025-04-19",
            "text": "API-gating various AI-generation functions",
            "sha": "ae93093"
          },
          {
            "date": "2025-04-12",
            "text": "Update language_code to target_language_code throughout the codebase - Update all occurrences in backend code to match the database migration - Fix models and queries to use the new field name - Update frontend type definitions to match the backend changes - This completes the migration started in migration file 030",
            "sha": "db0445f"
          },
          {
            "date": "2025-04-12",
            "text": "Make 'Process this text' operation synchronous - Modified process_sourcefile to run synchronously instead of using parallelisation - Removed run_async calls for text processing - Removed run_again_after parameter from all functions - Updated API message to indicate synchronous completion - Cleaner UX as the page will automatically reload when processing is done",
            "sha": "a85dde3"
          },
          {
            "date": "2025-04-12",
            "text": "Add database MODELS",
            "sha": "4710f81"
          },
          {
            "date": "2025-04-12",
            "text": "Replace parallel processing with serial for-loop in process_individual_words_api and add detailed response",
            "sha": "1ace5c6"
          },
          {
            "date": "2025-04-12",
            "text": "Add lemma metadata completion to frontend-orchestrated processing - Add functions to identify incomplete lemmas for a sourcefile - Create API endpoint for completing individual lemma metadata - Update processing queue to handle lemma completion steps - Document future enhancement to order lemmas by text appearance",
            "sha": "97ab26b"
          },
          {
            "date": "2025-04-08",
            "text": "Remove fallbacks, bandaids and excessive logging from lemma generation This commit simplifies the code by: - Removing excessive error handling and fallbacks that masked issues - Eliminating diagnostic logging that was left in production code - Simplifying API response validation to raise errors properly - Making the code fail loudly and clearly when there are problems - Properly propagating errors with informative messages",
            "sha": "9d68c5c"
          },
          {
            "date": "2025-04-07",
            "text": "Unified search API stage 1 promising, but you have to refresh the page for it to work",
            "sha": "fb2960f"
          },
          {
            "date": "2025-04-07",
            "text": "Tidied 250406_unified_search_api",
            "sha": "f86289b"
          },
          {
            "date": "2025-04-07",
            "text": "Remove hardcoded localhost fallbacks to fix production API URLs - Centralize API base URL management in config",
            "sha": "f5c972d"
          },
          {
            "date": "2025-04-05",
            "text": "Fix language selector in sourcedir page - Fix ReferenceError by properly using supported_languages from API - Add fallback for supported languages in case API doesn't provide them - Update variable names for consistency in templates",
            "sha": "37007fc"
          },
          {
            "date": "2025-04-05",
            "text": "Fix Process this text button by adding empty JSON body to API request The button was failing with a 400 Bad Request error because the API expected a JSON body, but the request was sent without one",
            "sha": "5292105"
          },
          {
            "date": "2025-04-05",
            "text": "Fix database migration scripts for production - Update migrate",
            "sha": "412d91c"
          },
          {
            "date": "2025-04-05",
            "text": "Moved backend/views/*_api",
            "sha": "5181ee5"
          },
          {
            "date": "2025-04-05",
            "text": "Fixed backend",
            "sha": "342656c"
          },
          {
            "date": "2025-04-05",
            "text": "Revert \"Fixed backend",
            "sha": "81214d2"
          },
          {
            "date": "2025-04-05",
            "text": "Revert \"Moved backend/views/*_api",
            "sha": "bfc7552"
          },
          {
            "date": "2025-04-03",
            "text": "Successful deploy, correct API urls",
            "sha": "364a3c5"
          },
          {
            "date": "2025-04-01",
            "text": "API works again for non-Jinja Lots of tidying, e",
            "sha": "ad8bfab"
          }
        ]
      },
      {
        "id": "deployment-ops",
        "title": "Deployment & Ops",
        "entries": [
          {
            "date": "2025-04-25",
            "text": "Easier to edit description",
            "sha": "1a61f49"
          },
          {
            "date": "2025-04-23",
            "text": "Redesign FAQ page with table of contents and anchor links - Remove accordion expanding boxes in favor of always-visible content - Add table of contents with links to each question - Create descriptive anchors and heading links for direct navigation - Add back-to-top buttons for better navigation - Improve styling with color-coded question headings - Optimize spacing between questions and answers",
            "sha": "101ca97"
          },
          {
            "date": "2025-04-22",
            "text": "Fixed migrate scripts",
            "sha": "2823699"
          },
          {
            "date": "2025-04-21",
            "text": "Added image-upload queue to get over Vercel 4",
            "sha": "ad81d00"
          },
          {
            "date": "2025-04-08",
            "text": "Improve description text formatting with line breaks - Enhance description display in sourcedir and sourcefile pages - Parse \\n as line breaks within paragraphs using <br> tags - Parse \\n\\n as paragraph breaks using separate <p> tags - Truncate descriptions in SourceItem listings to 100 chars",
            "sha": "f17f4b9"
          },
          {
            "date": "2025-04-07",
            "text": "Fix Sourcefile rename issue with reactive URLs and hard refresh This fixes an issue where Sourcefile rename updates the URL, but elements referencing the old slug (View image, Delete, etc",
            "sha": "a7a63a5"
          },
          {
            "date": "2025-04-06",
            "text": "Tweak to line spacing of enhanced text",
            "sha": "de67217"
          },
          {
            "date": "2025-04-05",
            "text": "Fix accessibility issues in sourcedir page modals - Add ARIA roles to divs with keydown handlers - Add aria-labels to close buttons - Add proper title associations for modal dialogs - Update STYLING",
            "sha": "ee3f52c"
          },
          {
            "date": "2025-04-05",
            "text": "Update deployment ID environment variable names in documentation and scripts",
            "sha": "f77f578"
          },
          {
            "date": "2025-04-05",
            "text": "Getting rid of VERCEL_PROD_*_DEPLOYMENT_ID environment variables",
            "sha": "08c580a"
          },
          {
            "date": "2025-04-04",
            "text": "Better deployment error message",
            "sha": "2f63f8c"
          },
          {
            "date": "2025-04-04",
            "text": "Hopefully fixing syntax error in deploy",
            "sha": "5f2c51d"
          },
          {
            "date": "2025-04-04",
            "text": "Fixed deploy urls (and hopefully health checks)",
            "sha": "1a8e6db"
          }
        ]
      },
      {
        "id": "docs-testing",
        "title": "Documentation & Testing",
        "entries": [
          {
            "date": "2025-04-27",
            "text": "Add changelog links throughout the application - Added changelog link to README",
            "sha": "75c2623"
          },
          {
            "date": "2025-04-21",
            "text": "Update README",
            "sha": "1317705"
          },
          {
            "date": "2025-04-20",
            "text": "docs(frontend): Refactor architecture and site organisation docs",
            "sha": "c66469c"
          },
          {
            "date": "2025-04-05",
            "text": "Updated docs references",
            "sha": "aa245f7"
          },
          {
            "date": "2025-04-04",
            "text": "Tidying up docs and tests",
            "sha": "b26588f"
          }
        ]
      },
      {
        "id": "flashcards-content",
        "title": "Flashcards & Content",
        "entries": [
          {
            "date": "2025-04-26",
            "text": "Changed wordforms columns",
            "sha": "f70e735"
          },
          {
            "date": "2025-04-26",
            "text": "Styling for Wordform column",
            "sha": "afeada3"
          },
          {
            "date": "2025-04-26",
            "text": "Slight improvement to processing see planning doc  some refactoring  It continues past transcribing and translating  but I'm still not convinced that it will extract the wordforms more than once!",
            "sha": "c49a7d1"
          },
          {
            "date": "2025-04-26",
            "text": "Added modified column to Wordforms list",
            "sha": "c9dbd72"
          },
          {
            "date": "2025-04-25",
            "text": "Tidied up Flashcards display",
            "sha": "8a09301"
          },
          {
            "date": "2025-04-25",
            "text": "More flashcard display tidying",
            "sha": "f903151"
          },
          {
            "date": "2025-04-25",
            "text": "Hiding button in flashcard if no next stage",
            "sha": "a000f44"
          },
          {
            "date": "2025-04-25",
            "text": "Tweaks to flashcard display & links",
            "sha": "56a92bd"
          },
          {
            "date": "2025-04-25",
            "text": "Tidied flashcard sentence & keyboard shortcuts display",
            "sha": "ce23fdd"
          },
          {
            "date": "2025-04-25",
            "text": "Filter Wordforms list by target language",
            "sha": "8d7a438"
          },
          {
            "date": "2025-04-25",
            "text": "Ignore existing phrases",
            "sha": "99937a4"
          },
          {
            "date": "2025-04-23",
            "text": "Enhance FAQ page with categorized questions and expand content - Reorganize FAQ into 6 logical categories for better organization - Expand from 8 to 30 questions with detailed answers based on marketing notes - Amalgamate audio flashcard questions into a comprehensive explanation - Update terminology from 'texts' to 'source materials/files' to reflect multi-media nature - Consistently hyphenate 'centaur-sourcing' throughout - Improve styling with category headers and enhanced TOC - Add visual separators between categories",
            "sha": "e256a1b"
          },
          {
            "date": "2025-04-22",
            "text": "Ignore lemmas in Flashcards",
            "sha": "bc5d2d9"
          },
          {
            "date": "2025-04-22",
            "text": "Fixed Flashcard ignore double-encoding",
            "sha": "48058d0"
          },
          {
            "date": "2025-04-22",
            "text": "Improved Flashcards page display",
            "sha": "1ad5ded"
          },
          {
            "date": "2025-04-21",
            "text": "Reload Wordform page when Lemma has completed",
            "sha": "6761da1"
          },
          {
            "date": "2025-04-21",
            "text": "Enhanced text now links to wordform",
            "sha": "789bf6a"
          },
          {
            "date": "2025-04-21",
            "text": "Tweaked slow speed for sentence audio",
            "sha": "b678c62"
          },
          {
            "date": "2025-04-21",
            "text": "Add link from Flashcard to Sentence",
            "sha": "364b2a0"
          },
          {
            "date": "2025-04-21",
            "text": "Fixed SourcefilePhrases",
            "sha": "4ca87d3"
          },
          {
            "date": "2025-04-20",
            "text": "Don't try and populate related_words_phrases_idioms any more because I don't think that's very useful",
            "sha": "f21be97"
          },
          {
            "date": "2025-04-20",
            "text": "feat: Complete standardized titles for all pages - Add standardized titles to all remaining sections: sentences, phrases, wordforms, search, flashcards - Add meta descriptions to sentence and phrase detail pages - Update planning document to reflect progress - Fix SITE_NAME import errors - Standardize title format across the entire application",
            "sha": "7c21444"
          },
          {
            "date": "2025-04-12",
            "text": "Simplified/updated how many words/phrases we get per processing",
            "sha": "56fd056"
          },
          {
            "date": "2025-04-08",
            "text": "Seemingly fixed lemma generation, but with a lot of extra fallbacks and logging",
            "sha": "1132c9d"
          },
          {
            "date": "2025-04-07",
            "text": "Add links to sourcefile/sourcedir in flashcard pages - Convert sourcefile and sourcedir references to hyperlinks in flashcard pages - Update URL registry documentation to include getPageUrl best practices - Remove fallbacks for better fail-fast behavior",
            "sha": "e0728d8"
          },
          {
            "date": "2025-04-05",
            "text": "Enhance flashcard experience to always play audio with LEFT key - Update documentation to clarify LEFT arrow always plays audio - Add dedicated playAudio function that doesn't interrupt already playing audio - Modify keyboard handler to play audio in any stage with LEFT arrow - Enable audio play in stage 1 with the Play audio button - Add KeyReturn icon to New sentence button for better UX",
            "sha": "a6a3aef"
          },
          {
            "date": "2025-04-04",
            "text": "Fixed Flashcards error",
            "sha": "641e929"
          },
          {
            "date": "2025-04-04",
            "text": "Fixed links to lemma",
            "sha": "62af782"
          },
          {
            "date": "2025-04-04",
            "text": "Fixed Flashcards",
            "sha": "5eed173"
          },
          {
            "date": "2025-04-04",
            "text": "Changed enhanced text links to wordform instead of lemma",
            "sha": "480f06b"
          },
          {
            "date": "2025-04-04",
            "text": "Added Translation tab",
            "sha": "175a764"
          }
        ]
      },
      {
        "id": "misc",
        "title": "Miscellaneous",
        "entries": [
          {
            "date": "2025-04-26",
            "text": "Removed deprecations verbosity from run_frontend",
            "sha": "a69d135"
          },
          {
            "date": "2025-04-26",
            "text": "Add text-on-light class for dark text on lavender background - Added new",
            "sha": "b30618d"
          },
          {
            "date": "2025-04-26",
            "text": "Update CLAUDE",
            "sha": "673f8d6"
          },
          {
            "date": "2025-04-25",
            "text": "Updated language list and added config contact variables",
            "sha": "5e6827b"
          },
          {
            "date": "2025-04-25",
            "text": "Moved marketing images around",
            "sha": "ee0cb5e"
          },
          {
            "date": "2025-04-25",
            "text": "Replaced contact buttons, and using global contact variables",
            "sha": "e95f359"
          },
          {
            "date": "2025-04-25",
            "text": "Improved GitHub logo",
            "sha": "bf0a2f9"
          },
          {
            "date": "2025-04-25",
            "text": "Fixed Sourcedir rename",
            "sha": "42b09ab"
          },
          {
            "date": "2025-04-25",
            "text": "0",
            "sha": "2dcd3ec"
          },
          {
            "date": "2025-04-25",
            "text": "Tweaked footer",
            "sha": "663a2fa"
          },
          {
            "date": "2025-04-25",
            "text": "Minor header layout tweak",
            "sha": "ce23214"
          },
          {
            "date": "2025-04-25",
            "text": "Improved layout for long Sourcefile titles",
            "sha": "b25f91e"
          },
          {
            "date": "2025-04-25",
            "text": "Fixed issue with audio upload",
            "sha": "582e02d"
          },
          {
            "date": "2025-04-25",
            "text": "Reduce overlap between STYLING",
            "sha": "2d1e791"
          },
          {
            "date": "2025-04-25",
            "text": "Automatically slow down if you keep replaying the audio of a flash card",
            "sha": "fb9deec"
          },
          {
            "date": "2025-04-25",
            "text": "Added Croatian",
            "sha": "006c56e"
          },
          {
            "date": "2025-04-25",
            "text": "Search paste button automatically triggers a search",
            "sha": "4173de2"
          },
          {
            "date": "2025-04-25",
            "text": "Search result prepopulated with search term",
            "sha": "a5fcbd6"
          },
          {
            "date": "2025-04-24",
            "text": "Created CLAUDE",
            "sha": "0942f81"
          },
          {
            "date": "2025-04-24",
            "text": "Removed package",
            "sha": "2a34a36"
          },
          {
            "date": "2025-04-24",
            "text": "Moved logo",
            "sha": "3c05fe8"
          },
          {
            "date": "2025-04-23",
            "text": "Changelog",
            "sha": "4d3244f"
          },
          {
            "date": "2025-04-23",
            "text": "Marketing materials",
            "sha": "473d1f7"
          },
          {
            "date": "2025-04-23",
            "text": "Updated Sourcedir v1",
            "sha": "100fe33"
          },
          {
            "date": "2025-04-23",
            "text": "New homepage",
            "sha": "be0dea1"
          },
          {
            "date": "2025-04-23",
            "text": "More homepage images",
            "sha": "24446c7"
          },
          {
            "date": "2025-04-23",
            "text": "Sourcedir using same buttons as Sourcefile",
            "sha": "82513af"
          },
          {
            "date": "2025-04-23",
            "text": "Homepage & image updates",
            "sha": "ceac5ed"
          },
          {
            "date": "2025-04-23",
            "text": "More marketing and copy prep",
            "sha": "963ccb0"
          },
          {
            "date": "2025-04-23",
            "text": "Fix Memrise link rendering in FAQ page - Update FAQ page to use {@html} directive for answers to correctly render HTML links - The Memrise link in the 'Is this a complete language course?' section now displays properly",
            "sha": "e879dcd"
          },
          {
            "date": "2025-04-23",
            "text": "Add consistent page titles across the site - Update STYLING",
            "sha": "d795fcb"
          },
          {
            "date": "2025-04-23",
            "text": "Update CLAUDE",
            "sha": "25e0ed0"
          },
          {
            "date": "2025-04-23",
            "text": "NebulaBackground works for a few pages about to make a big update so it'll appear on all pages",
            "sha": "d88ea4b"
          },
          {
            "date": "2025-04-23",
            "text": "Apply NebulaBackground to entire site via root layout - Add NebulaBackground to root layout for consistent site-wide application - Remove redundant NebulaBackground from about page - Ensure header and footer are properly layered with z-index",
            "sha": "787ae2f"
          },
          {
            "date": "2025-04-23",
            "text": "Updated FAQ",
            "sha": "e852581"
          },
          {
            "date": "2025-04-23",
            "text": "Add marked markdown package and blog route structure",
            "sha": "e9f84db"
          },
          {
            "date": "2025-04-23",
            "text": "Create GIT-COMMIT-GROUPED",
            "sha": "3c309d5"
          },
          {
            "date": "2025-04-23",
            "text": "Smaller images",
            "sha": "8285dab"
          },
          {
            "date": "2025-04-23",
            "text": "Error page",
            "sha": "3e12a31"
          },
          {
            "date": "2025-04-23",
            "text": "Tweak homepage copy",
            "sha": "f024fbb"
          },
          {
            "date": "2025-04-23",
            "text": "Improved apology - links to search",
            "sha": "b1d31f5"
          },
          {
            "date": "2025-04-23",
            "text": "Tweaked error page button ordering",
            "sha": "daa7a7a"
          },
          {
            "date": "2025-04-23",
            "text": "Added link to blog post image",
            "sha": "148f6f5"
          },
          {
            "date": "2025-04-23",
            "text": "Remove Markdown processing from blog post - Remove markdown content from page",
            "sha": "66b3ea4"
          },
          {
            "date": "2025-04-23",
            "text": "chore(frontend): improve Lightbox UX Portal modal to document",
            "sha": "72e725e"
          },
          {
            "date": "2025-04-23",
            "text": "Fixed minor SourcedirGrid import error",
            "sha": "a04c864"
          },
          {
            "date": "2025-04-23",
            "text": "Create hz-class-replacements",
            "sha": "5f7745f"
          },
          {
            "date": "2025-04-23",
            "text": "Slightly fainter background",
            "sha": "d369eb2"
          },
          {
            "date": "2025-04-23",
            "text": "Using auto-generated language name, fixed duplicate SearchBarMini",
            "sha": "de0c837"
          },
          {
            "date": "2025-04-23",
            "text": "Added node --trace-deprecation",
            "sha": "20eda8c"
          },
          {
            "date": "2025-04-22",
            "text": "Using SearchBarMini for search page after all seems to work ok",
            "sha": "509bd51"
          },
          {
            "date": "2025-04-22",
            "text": "Styling autofocus",
            "sha": "29a55f6"
          },
          {
            "date": "2025-04-22",
            "text": "Strip whitespace for all the environment variables we're getting an Eleven Labs issue with this now",
            "sha": "e15fb98"
          },
          {
            "date": "2025-04-22",
            "text": "Updating CLAUDE",
            "sha": "814306c"
          },
          {
            "date": "2025-04-22",
            "text": "Updating the env variables strip for secret variables",
            "sha": "3cecd20"
          },
          {
            "date": "2025-04-21",
            "text": "Improved title when uploading from url",
            "sha": "408cccd"
          },
          {
            "date": "2025-04-21",
            "text": "Mention LoadingSpinner",
            "sha": "12ee205"
          },
          {
            "date": "2025-04-21",
            "text": "Added SearchBarMini",
            "sha": "c942a76"
          },
          {
            "date": "2025-04-21",
            "text": "Tweaking EnhancedText size",
            "sha": "479b4ce"
          },
          {
            "date": "2025-04-21",
            "text": "Marketing explainer notes",
            "sha": "a4e55df"
          },
          {
            "date": "2025-04-21",
            "text": "Marketing ideas v1 I haven't read through them",
            "sha": "b220eea"
          },
          {
            "date": "2025-04-21",
            "text": "Removed redundant CORS lines",
            "sha": "24de19e"
          },
          {
            "date": "2025-04-21",
            "text": "Tidying frontend log warnings",
            "sha": "58d4cf7"
          },
          {
            "date": "2025-04-21",
            "text": "Removed progress bar expanding details and updated the collapsed message to be more informative",
            "sha": "293ac29"
          },
          {
            "date": "2025-04-21",
            "text": "Tidying unused export let",
            "sha": "f6300ae"
          },
          {
            "date": "2025-04-21",
            "text": "Removed verbose logging",
            "sha": "8691122"
          },
          {
            "date": "2025-04-20",
            "text": "Added Puppeteer",
            "sha": "54c58bb"
          },
          {
            "date": "2025-04-20",
            "text": "Add debugging documentation for Sourcefile tab issues Created a comprehensive debugging document (250420_Sourcefile_debugging",
            "sha": "9c91c83"
          },
          {
            "date": "2025-04-20",
            "text": "Site logo link",
            "sha": "6e61f50"
          },
          {
            "date": "2025-04-20",
            "text": "feat: Implement base title and trailing slash setting - Add base title via root layout (Stage 1)",
            "sha": "bff365f"
          },
          {
            "date": "2025-04-20",
            "text": "Adding SourcefileFooter plus maybe some misc changes from the titles/slashes work",
            "sha": "880855a"
          },
          {
            "date": "2025-04-20",
            "text": "Try to ignore soft linebreaks",
            "sha": "7d7aa87"
          },
          {
            "date": "2025-04-20",
            "text": "Coding always-rule",
            "sha": "441b094"
          },
          {
            "date": "2025-04-20",
            "text": "Removed broken and unnecessary",
            "sha": "9e8f8a9"
          },
          {
            "date": "2025-04-20",
            "text": "Plan for checking data egress issue",
            "sha": "cd97330"
          },
          {
            "date": "2025-04-20",
            "text": "fix: Standardize titles for remaining pages - Fix truncate import bug in sourcefile text page causing 500 error",
            "sha": "0fd2b5d"
          },
          {
            "date": "2025-04-20",
            "text": "Planning doc",
            "sha": "995eb4f"
          },
          {
            "date": "2025-04-20",
            "text": "Extract source from url v1 (working)",
            "sha": "e8cdbb1"
          },
          {
            "date": "2025-04-19",
            "text": "Avoid prefetching word previews",
            "sha": "50f76e2"
          },
          {
            "date": "2025-04-19",
            "text": "Processing seems to work!",
            "sha": "c2dbdc0"
          },
          {
            "date": "2025-04-19",
            "text": "Fixed more errors",
            "sha": "5aa9212"
          },
          {
            "date": "2025-04-18",
            "text": "Update",
            "sha": "23d3718"
          },
          {
            "date": "2025-04-18",
            "text": "Partway through frontend orchestrated Sourcefile processing",
            "sha": "29fe8eb"
          },
          {
            "date": "2025-04-12",
            "text": "Moved out",
            "sha": "dcbf264"
          },
          {
            "date": "2025-04-12",
            "text": "Collapsible Sourcefile header",
            "sha": "77606fd"
          },
          {
            "date": "2025-04-12",
            "text": "Planning frontend-orchestrated Sourcefile-processing",
            "sha": "e1490e3"
          },
          {
            "date": "2025-04-12",
            "text": "First stage of frontend Sourcefile orchestration seems to work",
            "sha": "8d521e1"
          },
          {
            "date": "2025-04-12",
            "text": "Next stage of Sourcefile processing (auto-clicks, and counter)",
            "sha": "ece68db"
          },
          {
            "date": "2025-04-12",
            "text": "Fix aggressive auto-processing and implement live-updating enhanced text 1",
            "sha": "39f4a7e"
          },
          {
            "date": "2025-04-12",
            "text": "Planning enhanced text transition",
            "sha": "53c42c4"
          },
          {
            "date": "2025-04-12",
            "text": "Click process counter multiple times",
            "sha": "0b620b2"
          },
          {
            "date": "2025-04-12",
            "text": "Renamed logs",
            "sha": "7dd52e7"
          },
          {
            "date": "2025-04-11",
            "text": "Moved gjdutils rules into ~/",
            "sha": "2098c13"
          },
          {
            "date": "2025-04-11",
            "text": "Planning doc for large data egress issue",
            "sha": "c94bb31"
          },
          {
            "date": "2025-04-11",
            "text": "Moved cursor-tools",
            "sha": "e194824"
          },
          {
            "date": "2025-04-08",
            "text": "Log Flask output to both file and terminal using tee",
            "sha": "efc569e"
          },
          {
            "date": "2025-04-07",
            "text": "Search is working much better",
            "sha": "4090b56"
          },
          {
            "date": "2025-04-07",
            "text": "Search page working pretty well",
            "sha": "321cf5b"
          },
          {
            "date": "2025-04-07",
            "text": "Uses unslugified filename for Sourcefile title",
            "sha": "361b08a"
          },
          {
            "date": "2025-04-07",
            "text": "Handle Cmd-click search",
            "sha": "70af24f"
          },
          {
            "date": "2025-04-07",
            "text": "Redirect Flask server output to log file - Capture both stdout and stderr in logs/flask",
            "sha": "6cfbbe6"
          },
          {
            "date": "2025-04-06",
            "text": "Tilted logo - thanks, Carolina!",
            "sha": "ddac8d9"
          },
          {
            "date": "2025-04-06",
            "text": "Adjust hero styling on homepage",
            "sha": "a987613"
          },
          {
            "date": "2025-04-06",
            "text": "Refactor EnhancedText word data fetching with async/await - Replace complex Promise chains with cleaner async/await syntax - Remove unnecessary XMLHttpRequest fallback (modern browsers support fetch) - Commit to type-safe URL generation using routes",
            "sha": "01c17a4"
          },
          {
            "date": "2025-04-06",
            "text": "Update EnhancedText debugging documentation - Document parameter naming standardization (language_code → target_language_code) - Add details about async/await implementation benefits - Update lessons learned with naming consistency best practices - Add code evolution summary showing incremental improvements - Remove outdated references to XMLHttpRequest fallback - Expand implementation details for future reference",
            "sha": "21df4fe"
          },
          {
            "date": "2025-04-06",
            "text": "Disable YouTube button",
            "sha": "0047ff4"
          },
          {
            "date": "2025-04-06",
            "text": "Tweak to \"easily confused\" generation",
            "sha": "a18fe69"
          },
          {
            "date": "2025-04-06",
            "text": "Rewrote enhanced text using structured word data instead of pre-generated HTML",
            "sha": "cbba331"
          },
          {
            "date": "2025-04-05",
            "text": "Fixing routes",
            "sha": "a017078"
          },
          {
            "date": "2025-04-05",
            "text": "Sourcedir sort by date default",
            "sha": "48ad3a6"
          },
          {
            "date": "2025-04-05",
            "text": "Speeding up & refactoring Sourcefile pages",
            "sha": "9714373"
          },
          {
            "date": "2025-04-05",
            "text": "Tidied up index",
            "sha": "0a2e988"
          },
          {
            "date": "2025-04-05",
            "text": "Update SEARCH",
            "sha": "6fbccc6"
          },
          {
            "date": "2025-04-05",
            "text": "Added EnhancedText and Tippy, but only partially, not working",
            "sha": "6906ebe"
          },
          {
            "date": "2025-04-05",
            "text": "Refactor prompt templates to use individual files",
            "sha": "c6f838c"
          },
          {
            "date": "2025-04-05",
            "text": "Removed console",
            "sha": "ceb761c"
          },
          {
            "date": "2025-04-05",
            "text": "Add logo to header with animated hover effect",
            "sha": "50e4ef6"
          },
          {
            "date": "2025-04-05",
            "text": "Add 'Up' button to sourcedir page for easier navigation",
            "sha": "ae33d11"
          },
          {
            "date": "2025-04-05",
            "text": "Using client-side sorting hack to fix /sources :(",
            "sha": "7ead745"
          },
          {
            "date": "2025-04-05",
            "text": "Update CLAUDE",
            "sha": "b024905"
          },
          {
            "date": "2025-04-05",
            "text": "Got rid of",
            "sha": "1e29553"
          },
          {
            "date": "2025-04-05",
            "text": "Improving ENHANCED_TEXT",
            "sha": "16d519b"
          },
          {
            "date": "2025-04-05",
            "text": "Fix accessibility issues in sourcedir page 1",
            "sha": "fd8b0af"
          },
          {
            "date": "2025-04-05",
            "text": "Update DEVOPS",
            "sha": "dded6d1"
          },
          {
            "date": "2025-04-05",
            "text": "Update ENHANCED_TEXT",
            "sha": "c23bf59"
          },
          {
            "date": "2025-04-04",
            "text": "Fixed routes",
            "sha": "01f43df"
          },
          {
            "date": "2025-04-04",
            "text": "Fixed routes",
            "sha": "de2e25d"
          },
          {
            "date": "2025-04-04",
            "text": "Fixed Prev and Next buttons",
            "sha": "83d9cb0"
          },
          {
            "date": "2025-04-04",
            "text": "Added first and last buttons to Sourcefile",
            "sha": "01fbcdc"
          },
          {
            "date": "2025-04-04",
            "text": "SourcefileLayout and improved nav tabs",
            "sha": "0047e94"
          },
          {
            "date": "2025-04-04",
            "text": "Create SITE_ORGANISATION",
            "sha": "0a14b02"
          },
          {
            "date": "2025-04-03",
            "text": "Tidying",
            "sha": "86ce1c1"
          },
          {
            "date": "2025-04-01",
            "text": "Delete vite_helpers",
            "sha": "5121ad6"
          },
          {
            "date": "2025-04-01",
            "text": "Update",
            "sha": "eed954d"
          }
        ]
      },
      {
        "id": "profile-user",
        "title": "Profile & User",
        "entries": [
          {
            "date": "2025-04-27",
            "text": "Fix user email lookup to use AuthUser model instead of Profile - Update Profile",
            "sha": "b2d7200"
          },
          {
            "date": "2025-04-27",
            "text": "Fix profile page URL error by using correct profile API route name Fixed the TypeError in the profile page by updating the route name from PROFILE_API_GET_PROFILE_API to PROFILE_API_GET_CURRENT_PROFILE_API, which matches the actual backend API endpoint /api/profile/current",
            "sha": "05fc099"
          },
          {
            "date": "2025-04-26",
            "text": "Add language-specific back button to profile page - Add back navigation button to the user profile page - Show \"Back to languages\" when no language is saved or selected - Show \"Back to [LANGUAGE_NAME]\" when a language is saved and selected - Hide button when selected language differs from saved language - Use lavender background with dark text for consistent styling",
            "sha": "c1484ae"
          },
          {
            "date": "2025-04-25",
            "text": "Fix the issue with the profile target language drop-down when the page is very wide",
            "sha": "026b8d8"
          },
          {
            "date": "2025-04-23",
            "text": "Update homepage with clickable marketing images - Made all marketing images link to the languages page - Added subtle hover effects to indicate clickable images - Improved user journey with clear visual call-to-actions - Maintained existing animation effects and styling",
            "sha": "e08de1e"
          },
          {
            "date": "2025-04-23",
            "text": "feat(frontend): add next query parameter to languages page - Implement next parameter for language selection page - Redirect users to specific features after language selection - Add Try Flashcards overlay on homepage flashcard image - Add documentation explaining the feature and usage",
            "sha": "4d08766"
          },
          {
            "date": "2025-04-21",
            "text": "Refactor authentication in sourcedir page using createAuthHeaders…       - Added createAuthHeaders helper function to centralize auth token handling       - Updated all API calls to use this helper for consistent auth implementation       - Fixed file upload authentication issues reported by user with 401 errors       - Added comment suggesting future integration with apiFetch for consistency",
            "sha": "3d2ca25"
          },
          {
            "date": "2025-04-20",
            "text": "Fix Unauthorized errors in Sourcefile processing and search - Fix processing queue authentication by properly passing Supabase client - Add robust error handling for authentication failures - Fix search functionality to handle authentication gracefully - Improve user feedback for authentication errors with login links - Make error messages more user-friendly with HTML formatting",
            "sha": "59aa74b"
          },
          {
            "date": "2025-04-19",
            "text": "Profile page works",
            "sha": "0c12fa2"
          },
          {
            "date": "2025-04-18",
            "text": "Some of the auth is working, now trying profile page",
            "sha": "f7b1f5d"
          },
          {
            "date": "2025-04-08",
            "text": "Make wordform generation fully synchronous This commit fixes the issue where users needed to manually refresh the page after wordform generation",
            "sha": "a6816cc"
          },
          {
            "date": "2025-04-05",
            "text": "Add dev-mode error details for better debugging - Import dev flag from $app/environment to detect development mode - Add collapsible developer error details section to both error pages - Display comprehensive debug information in dev mode only - Include error details, stack trace, route info, and page data - Keep the interface user-friendly in production",
            "sha": "a5b45eb"
          }
        ]
      },
      {
        "id": "seo-analytics",
        "title": "SEO & Analytics",
        "entries": [
          {
            "date": "2025-04-27",
            "text": "Terms and privacy policies Co-Authored-By: Claude <noreply@anthropic",
            "sha": "86f1f7e"
          },
          {
            "date": "2025-04-26",
            "text": "Google Analytics tag",
            "sha": "51c7117"
          },
          {
            "date": "2025-04-26",
            "text": "Add sitemap generator - Create sitemap_generator",
            "sha": "3852978"
          },
          {
            "date": "2025-04-26",
            "text": "Refactor sitemap generator to use Jinja templates - Add Jinja templates for XML sitemap generation - Create reusable templates for URL entries - Implement Jinja rendering for all sitemap types - Apply DRY principles to reduce code duplication - Improve maintainability by separating XML structure from logic",
            "sha": "57e1446"
          },
          {
            "date": "2025-04-26",
            "text": "Improve sitemap generation system - Refactor sitemap generator to use sitemap-generated- prefix for all dynamic sitemaps - Reorganize sitemaps into /sitemaps/ subdirectory for better organization - Consolidate scripts to avoid duplication (local and production versions) - Move print_header function to common",
            "sha": "b82a037"
          },
          {
            "date": "2025-04-26",
            "text": "Sitemap",
            "sha": "4f6474d"
          },
          {
            "date": "2025-04-21",
            "text": "Create robots",
            "sha": "5073bdc"
          },
          {
            "date": "2025-04-20",
            "text": "feat: Implement standard page titles and meta enhancements - Add consistent title structure with pipe separators - Fix trailing slash redirection with 307 status code - Add meta description utility function for SEO - Implement error page title standardization - Add language section redirect to sources page - Add truncation utility for long content in titles - Fix bug in languages page DOM binding",
            "sha": "883d393"
          }
        ]
      },
      {
        "id": "ui-components",
        "title": "UI & Components",
        "entries": [
          {
            "date": "2025-04-27",
            "text": "Add tooltip support to DataGrid component and implement etymology tooltips on Lemmas page",
            "sha": "2149d29"
          },
          {
            "date": "2025-04-27",
            "text": "Update Phrases list page to use DataGrid component - Implement DataGrid for the phrases page - Add columns for phrase, translations, part of speech, level, and modified date - Include hover tooltips that display usage notes - Display language difficulty level in a column",
            "sha": "e732ffd"
          },
          {
            "date": "2025-04-27",
            "text": "Update sentences list page to use DataGrid with descending date sort - Convert sentences list to use DataGrid component - Configure default sort to show newest sentences first (updated_at desc) - Add columns for sentence, translation, language level, and modified date - Match styling with other DataGrid implementations",
            "sha": "9ae1da3"
          },
          {
            "date": "2025-04-27",
            "text": "Add default sort options to DataGrid component This commit adds two new props to DataGrid: - defaultSortField: to specify which column to sort by initially - defaultSortDir: to specify the initial sort direction (asc/desc)  Updated documentation with examples of how to use the new feature",
            "sha": "5c31498"
          },
          {
            "date": "2025-04-27",
            "text": "Implement DataGrid for sourcedirs page - Fix column name (created_by_id instead of created_by) - Remove user email lookup to simplify implementation - Add transformation for API data to match database fields - Include null checking for sources array to prevent errors - Fix file count display by using statistics",
            "sha": "3bbe8a8"
          },
          {
            "date": "2025-04-27",
            "text": "Improve DataGrid for sourcedirs page - Add loading spinner to prevent \"No data\" flash - Set default sort to modified date descending - Rename \"Files\" column to \"# Sources\" for clarity - Add custom SQL query with JOIN to count sourcefiles - Handle both API and direct database data formats - Use row",
            "sha": "f906f88"
          },
          {
            "date": "2025-04-27",
            "text": "Improve DataGrid with loading spinner on initial load - Add loading spinner to DataGrid for initial data load state - Replace \"No data\" with spinner when server data is loading - Update sources and wordforms pages to use the new functionality - Make spinner the default behavior so all pages benefit",
            "sha": "f3e6773"
          },
          {
            "date": "2025-04-27",
            "text": "Update changelog page with GitHub issue button and improved commit display - Added GithubIssueButton component at the top of the page - Modified commit links to show only first 6 chars while keeping full SHA in tooltip - Added missing date to the Terms entry - Added changelog link to the footer",
            "sha": "8f28671"
          },
          {
            "date": "2025-04-27",
            "text": "Fix DataGrid sourcefile count display by aliasing count aggregate and handling PostgREST array response format Co-Authored-By: Claude <noreply@anthropic",
            "sha": "948480c"
          },
          {
            "date": "2025-04-26",
            "text": "Add interactive page input to DataGrid navigation - Replace static page display with an editable input field - Allow users to jump to any page by entering a number and pressing Enter - Use DOM focus detection to prevent input hijacking while editing - Add input validation with visual error feedback - Utilize Svelte's tick to ensure proper synchronization",
            "sha": "e2ab962"
          },
          {
            "date": "2025-04-26",
            "text": "Fixed DataGrid row clicks to use proper hrefs",
            "sha": "570d822"
          },
          {
            "date": "2025-04-26",
            "text": "Added queryModifier prop to DataGrid",
            "sha": "909127c"
          },
          {
            "date": "2025-04-26",
            "text": "DataGrid styling",
            "sha": "e7d8476"
          },
          {
            "date": "2025-04-26",
            "text": "Add row count display to DataGrid component - Shows total records in the grid - Updates to show filtered count when filters are applied - Styled as a badge with primary green background - Positioned properly with flex layout",
            "sha": "5768adc"
          },
          {
            "date": "2025-04-26",
            "text": "Gave up on DataGrid filtering for now we have a plan from o3 in 250426",
            "sha": "56e931b"
          },
          {
            "date": "2025-04-26",
            "text": "DataGrid header less obtrusive",
            "sha": "5fa4828"
          },
          {
            "date": "2025-04-26",
            "text": "Add reusable DropdownButton component with tooltip and click-outside behavior - Created new DropdownButton",
            "sha": "3bcb67c"
          },
          {
            "date": "2025-04-26",
            "text": "Improve user profile page layout - Add Card component for consistent styling - Enhance with Phosphor icons for better visual hierarchy - Use Bootstrap grid for responsive layout - Add help text for the language selection dropdown - Improve form styling and button placement - Add loading spinner component - Implement Alert component for messages",
            "sha": "a94d57c"
          },
          {
            "date": "2025-04-26",
            "text": "Implement DataGrid for lemmas page - Replace alphabetical list with DataGrid component - Add server-side pagination and sorting - Configure columns: lemma, translations, part_of_speech, language_level, is_complete, commonality, updated_at - Comment out letter navigation for potential future reuse - Create planning document for DataGrid implementation on other list pages",
            "sha": "2065556"
          },
          {
            "date": "2025-04-25",
            "text": "New AudioPlayer component",
            "sha": "074770b"
          },
          {
            "date": "2025-04-25",
            "text": "Add navigation buttons to top of DataGrid - Create DataGridNavButtons component to abstract pagination controls - Add navigation buttons at both top and bottom of DataGrid - Only show navigation when pagination is required (multiple pages) - Rename NavButtons to SourcefileNavButtons for clarity - Update LoadingSpinner to support different sizes via runes syntax",
            "sha": "d6f4560"
          },
          {
            "date": "2025-04-23",
            "text": "Refactor(theme): Update components for new color palette (Part 1)",
            "sha": "8a91011"
          },
          {
            "date": "2025-04-23",
            "text": "Add FAQ page and update About page with external links - Create new FAQ page with responsive accordion-style Q&A - Add links to Memrise",
            "sha": "bdf40b8"
          },
          {
            "date": "2025-04-23",
            "text": "Update UI components with consistent color styling - Update SearchResults component to use brand color variables for better theming - Update Sentence component to use more consistent button styles - Add hover effects to SentenceCard and SourceItem components - Fix SourcedirHeader border styling using theme variables - Add playback rate buttons to SourcefileAudio component - Update planning document with component styling progress",
            "sha": "0773604"
          },
          {
            "date": "2025-04-23",
            "text": "Fix search results component and styling - Fix SearchResults component to use proper Phosphor icon imports - Standardize variable naming between search pages (searchResults → result) - Add missing CSS classes for card headers in theme",
            "sha": "d58b5d6"
          },
          {
            "date": "2025-04-23",
            "text": "Add LightboxImage component with svelte-lightbox for screenshots • Created a reusable LightboxImage component that uses svelte-lightbox • Applied to screenshots on homepage • Updated documentation in STYLING",
            "sha": "ea6c53d"
          },
          {
            "date": "2025-04-23",
            "text": "Fix unused CSS selectors in homepage and improve flashcard image accessibility - Remove unused flashcard-screenshot-wrapper CSS selectors - Remove redundant href attribute from LightboxImage - Add detailed alt text to flashcard image for better accessibility",
            "sha": "748dda9"
          },
          {
            "date": "2025-04-23",
            "text": "Fix TypeScript errors in EnhancedText component - Properly type error variables as 'unknown' - Add type guards for error handling - Replace || with nullish coalescing operator for data-lemma attribute",
            "sha": "719d857"
          },
          {
            "date": "2025-04-23",
            "text": "Add playback rate control to SourcefileAudio component - Add variable binding for the audio element - Add currentPlaybackRate state - Add setPlaybackRate function for controlling playback speed",
            "sha": "68a8ef0"
          },
          {
            "date": "2025-04-23",
            "text": "Fix navigation URLs and use dynamic content - Update SourceItem component to use variable sourceUrl instead of hardcoded path - Change homepage link in site layout from '/languages' to '/' - Use dynamic TAGLINE variable in footer instead of hardcoded text",
            "sha": "fffe94c"
          },
          {
            "date": "2025-04-23",
            "text": "Updated phosphor-svelte imports",
            "sha": "b53aece"
          },
          {
            "date": "2025-04-23",
            "text": "Standardize colors in Sourcedir UI - Replace hardcoded colors with theme variables - Create consistent button styling with proper hover states - Add semantic badge classes for words, phrases, audio - Add hover effects to list items - Replace custom button class with standardized btn-action class - Document additional UI improvement ideas in planning doc",
            "sha": "de685c7"
          },
          {
            "date": "2025-04-23",
            "text": "Fix svelte-lightbox dependency issue with Svelte 5 - Add --legacy-peer-deps flag to build script - Document dependency management in DEVOPS",
            "sha": "95312e9"
          },
          {
            "date": "2025-04-23",
            "text": "Improve blog UI with enhanced styling and UX - Convert 'Back to all posts' to styled pill button - Enhance date & author display with frosted glass effect - Improve CTA box with gradient border and better spacing - Use proper Phosphor icon imports for better compatibility - Apply consistent styling across blog pages",
            "sha": "d98ddc1"
          },
          {
            "date": "2025-04-23",
            "text": "Centralize error handling and update error page styling - Consolidate error pages for consistent UI experience across the app - Add multilingual apology component to all error pages - Update language-specific error page to reuse root error component - Change button color to match official style guide (btn-primary)",
            "sha": "26dd4d9"
          },
          {
            "date": "2025-04-23",
            "text": "Add SVAR DataGrid implementation documentation - Create detailed planning document for SVAR DataGrid integration - Document implementation challenges with Svelte 5 compatibility - Include code examples for component structure and server-side integration - Update action items with current progress - Document next steps for further development",
            "sha": "2e80422"
          },
          {
            "date": "2025-04-23",
            "text": "Fix error component import path in language error component This resolves the failed import from '",
            "sha": "8134eb3"
          },
          {
            "date": "2025-04-23",
            "text": "Create reusable TableOfContents component for FAQ and blog posts This commit extracts the table of contents functionality into a reusable component that can support both category-based TOCs (for FAQ) and flat item TOCs (for blog posts)",
            "sha": "c21576b"
          },
          {
            "date": "2025-04-23",
            "text": "refactor(frontend): rename languages page query param from next to section Better distinguishes from /auth?next= which takes a URL, while section is more descriptive for a section of functionality within a language's pages",
            "sha": "a643374"
          },
          {
            "date": "2025-04-23",
            "text": "feat: auto-generate language data TypeScript file to eliminate API calls - Created language data generator to produce TypeScript with hardcoded language data - Added Flask CLI commands to generate language data TypeScript file - Created frontend utilities to use generated data instead of API calls - Updated frontend components to use the new utilities - Maintained backward compatibility with API fallbacks - Improved performance by eliminating unnecessary network requests",
            "sha": "e54a142"
          },
          {
            "date": "2025-04-23",
            "text": "Sourcedir DataGrid v1 working but ugly, with Flask API",
            "sha": "3a7e886"
          },
          {
            "date": "2025-04-23",
            "text": "feat(ui): switch secondary color from peach to lavender Update CSS variables and styling to use lavender as the secondary color throughout the application instead of peach, affecting buttons and card headers",
            "sha": "eb3a968"
          },
          {
            "date": "2025-04-23",
            "text": "fix(frontend): update button colors to use theme variables Replaced hardcoded #4CAD53 green with --hz-color-primary-green in NavButtons and SourcefileHeader components to maintain consistent brand styling",
            "sha": "c65a51c"
          },
          {
            "date": "2025-04-23",
            "text": "fix(ui): adjust dropcap letters to fit inside language cards",
            "sha": "bdfc635"
          },
          {
            "date": "2025-04-23",
            "text": "feat(DataGrid): add provider abstraction, pagination, sorting, filtering, loading spinner; update planning checklist",
            "sha": "3a30bc8"
          },
          {
            "date": "2025-04-23",
            "text": "Wordform page displays, but UI components don't work",
            "sha": "ee62353"
          },
          {
            "date": "2025-04-23",
            "text": "Wordforms DataGrid UI components mostly work but you can't unset the filter",
            "sha": "a7c04ec"
          },
          {
            "date": "2025-04-22",
            "text": "Trying to improve main search UI but I think the core navigation is still a bit broken",
            "sha": "4657b02"
          },
          {
            "date": "2025-04-21",
            "text": "feat: Add LoadingSpinner component and integrate into URL upload modal",
            "sha": "fae4bf4"
          },
          {
            "date": "2025-04-21",
            "text": "Fix auth integration in SvelteKit routes Pass Supabase client to API functions for proper authentication in language routes",
            "sha": "b9ebd88"
          },
          {
            "date": "2025-04-21",
            "text": "Add visual highlighting for active playback speed Highlight the currently selected playback speed button in the Sentence component",
            "sha": "1b91b05"
          },
          {
            "date": "2025-04-21",
            "text": "Add delete button to Sentence component",
            "sha": "7d2987f"
          },
          {
            "date": "2025-04-21",
            "text": "Enhance word tooltips to show wordform translation and inflection type - Update tooltips to show wordform translation instead of lemma translation - Add grammatical information (inflection type) to tooltips with distinctive styling - Keep lemma form in tooltip header for reference - Update WordPreview interface and backend to support new fields",
            "sha": "0083c4b"
          },
          {
            "date": "2025-04-21",
            "text": "feat(search): Improve 401 error message for unauthenticated search - Replace generic error message with a friendly 'Login Required' card - Add direct 'Log in to Search' button with next URL parameter - Change card styling from danger to info for 401 errors - Add better explanation about why authentication is required",
            "sha": "ab5dbae"
          },
          {
            "date": "2025-04-21",
            "text": "Refactor(svelte): Update on:event syntax in sourcedir page",
            "sha": "e774da4"
          },
          {
            "date": "2025-04-21",
            "text": "Fixing unused CSS selectors",
            "sha": "d9ad1d2"
          },
          {
            "date": "2025-04-21",
            "text": "Improved SearchBarMini UI",
            "sha": "80ea86c"
          },
          {
            "date": "2025-04-21",
            "text": "Improved UI for both kinds of search bar",
            "sha": "d552559"
          },
          {
            "date": "2025-04-20",
            "text": "Refine auth: Require login for costly generation (audio, word search)",
            "sha": "28eac93"
          },
          {
            "date": "2025-04-20",
            "text": "Add clickable tooltips linking to lemma pages - Made lemma name in tooltips clickable, linking to lemma detail page - Added \"View full details\" link at the bottom of tooltips - Added hover effects and styling for tooltip links - Enhanced error tooltips to also have clickable links to lemma pages",
            "sha": "9b9259e"
          },
          {
            "date": "2025-04-20",
            "text": "Make EnhancedText tooltip links open in new tab with target=\\_blank\\",
            "sha": "cab5a19"
          },
          {
            "date": "2025-04-20",
            "text": "feat(search): Add clear and paste buttons to search bar - Add X button (clear) that appears when text is present - Add clipboard button for one-click paste functionality - Both buttons include helpful tooltips - Focus input after button actions",
            "sha": "db94a7b"
          },
          {
            "date": "2025-04-20",
            "text": "feat: Add progressive lemma loading to wordform page - Create new shared LemmaContent component used by both Lemma and Wordform pages - Add new LemmaDetails component with progressive loading and auth awareness - Show lemma details below wordform details with a clear visual separator - Fix SSR compatibility issues with window references - Add detailed planning document with implementation strategy",
            "sha": "7034ae7"
          },
          {
            "date": "2025-04-18",
            "text": "First stage of new SvelteKit auth",
            "sha": "04c338c"
          },
          {
            "date": "2025-04-12",
            "text": "Improve API error handling and visibility - Add global 500 error handler for API routes with JSON responses - Add specific error handling for field mismatch errors - Use appropriate status codes to distinguish error types - Improve logging for better error visibility - Complete migration from language_code to target_language_code",
            "sha": "8ebb28c"
          },
          {
            "date": "2025-04-12",
            "text": "Add text file upload feature with tooltip guidance - Add",
            "sha": "7722a63"
          },
          {
            "date": "2025-04-12",
            "text": "Add description field to Create from Text dialog - Add optional description field to Create from Text dialog in SvelteKit frontend - Update backend API to process description parameter in create_sourcefile_from_text_api - Set consistent metadata format with text uploads for better API alignment - Improve UX by providing description capability in both upload and direct creation",
            "sha": "12f7f15"
          },
          {
            "date": "2025-04-12",
            "text": "Fix sourcedir dropdown with Svelte reactive approach - Replace manual DOM manipulation with Svelte's reactive approach - Fix reference error in moveSourcefile function - Use isDropdownOpen state variable to control dropdown visibility - Add proper click-outside handling to close dropdown when needed - Close dropdown after selection is made",
            "sha": "23d964b"
          },
          {
            "date": "2025-04-12",
            "text": "Fixed language_code variable in build Co-Authored-By: Claude <noreply@anthropic",
            "sha": "96179e4"
          },
          {
            "date": "2025-04-12",
            "text": "Update homepage with key benefits instead of SvelteKit port status",
            "sha": "8b3299c"
          },
          {
            "date": "2025-04-12",
            "text": "Improve Sourcefile UI with collapsible header and unified actions row - Add CollapsibleHeader component with expand/collapse functionality - Reorganize Sourcefile page buttons into a single row with dividers - Group actions logically: Process, Flashcards, and Navigation - Update STYLING",
            "sha": "0dbd2af"
          },
          {
            "date": "2025-04-12",
            "text": "Improve SourcefileHeader organization - Move File Operations section above Description in the expanded header - Remove duplicate divider line between CollapsibleHeader and MetadataSection - Add Learning Operations divider to distinguish expandable content from permanent buttons",
            "sha": "c50953e"
          },
          {
            "date": "2025-04-11",
            "text": "Fix SvelteKit build issues for Vercel deployment - Removed unused CSS selectors from EnhancedText component - Reverted experimental SvelteKit typed URL routing code from SourcefileHeader - Added SVELTE_WARNINGS_STRICT to run_frontend",
            "sha": "76fe35d"
          },
          {
            "date": "2025-04-08",
            "text": "Create DescriptionFormatted shared component for consistent description handling - Created a reusable component for formatting text with line breaks and paragraphs - Updated Sourcedir page to use the shared component - Updated SourcefileHeader to use the shared component - Exported the component through $lib for easy importing",
            "sha": "0325db3"
          },
          {
            "date": "2025-04-08",
            "text": "Enhance DescriptionFormatted with editing capabilities - Convert component to include both display and edit functionality - Add keyboard shortcuts (Ctrl+Enter to save, Esc to cancel) - Standardize description editing across Sourcedir and Sourcefile components - Maintain consistent styling and UX between components - Remove duplicate code for description editing logic",
            "sha": "27256ce"
          },
          {
            "date": "2025-04-08",
            "text": "Fix missing PencilSimple import in SourcefileHeader component",
            "sha": "8a26886"
          },
          {
            "date": "2025-04-08",
            "text": "Remove duplicate search bar from SourcefileLayout The search bar was appearing twice on sourcefile pages because it was included in both the main layout and the SourcefileLayout component",
            "sha": "721169b"
          },
          {
            "date": "2025-04-07",
            "text": "Renaming Sourcefile updates in the UI",
            "sha": "9777632"
          },
          {
            "date": "2025-04-07",
            "text": "Add SvelteKit typed URL routing planning document with gradual implementation strategy",
            "sha": "c3ed63a"
          },
          {
            "date": "2025-04-07",
            "text": "Update SvelteKit typed routing documentation with implementation details",
            "sha": "7c458a3"
          },
          {
            "date": "2025-04-06",
            "text": "Tooltips are working for Sourcefile, still in progress - still using hand-constructed url - lots of debug logging",
            "sha": "fed4131"
          },
          {
            "date": "2025-04-06",
            "text": "Tooltips seem to be working, with routes",
            "sha": "1eb62e2"
          },
          {
            "date": "2025-04-06",
            "text": "Standardize language parameter naming in EnhancedText component - Rename language_code prop to target_language_code for consistency with API - Update all references to language_code in EnhancedText",
            "sha": "15a9152"
          },
          {
            "date": "2025-04-06",
            "text": "Add WordPreview TypeScript interface for tooltips - Create dedicated WordPreview interface in types",
            "sha": "49cc444"
          },
          {
            "date": "2025-04-06",
            "text": "Update tooltip styling to use dark theme with loading spinner - Replace light theme with custom dark theme matching site colors - Add loading spinner for better user feedback during API requests - Style headers with primary color and errors with secondary color - Update debug info styling to match dark theme - Document styling changes in tooltip debugging notes",
            "sha": "51d1965"
          },
          {
            "date": "2025-04-06",
            "text": "Fix navigation in SourcefileHeader using SvelteKit's proper routing",
            "sha": "905168d"
          },
          {
            "date": "2025-04-06",
            "text": "Add tooltips to navigation buttons with file names and directory path",
            "sha": "34be676"
          },
          {
            "date": "2025-04-05",
            "text": "Add source directory management buttons - Add New Source Directory button at the top of the page - Add Delete buttons for empty source directories - Update SourceItem component to accept className property for styling",
            "sha": "86d4ad6"
          },
          {
            "date": "2025-04-05",
            "text": "Improve modal dialogues with better UX patterns - Add keyboard shortcuts (ESC to cancel, ENTER/CTRL+ENTER to submit) - Add loading spinners and disable buttons during API operations - Fix delete button UI using Phosphor icons - Add auto-focus to modal input fields - Add form validation with disabled buttons and tooltips - Prevent double submissions of forms - Add documentation in USER_EXPERIENCE",
            "sha": "5902b84"
          },
          {
            "date": "2025-04-05",
            "text": "Fix image upload functionality by modernizing API - Change API to return JSON responses with proper HTTP status codes - Remove legacy template rendering code causing Flask errors - Update SvelteKit component to properly handle API responses - Fix error handling and simplify success flow - Only display alerts for errors, not for successful uploads",
            "sha": "975a977"
          },
          {
            "date": "2025-04-05",
            "text": "Fix accessibility and CSS issues in languages page - Remove autofocus attribute to improve accessibility - Eliminate unused CSS selectors by using global styles - Update styling documentation with best practices for focus management - Properly scope card styling to avoid unused CSS warnings",
            "sha": "74525bd"
          },
          {
            "date": "2025-04-05",
            "text": "Update favicon implementation - Move favicon handling entirely to SvelteKit - Remove Flask favicon route from backend - Add modern favicon assets for different platforms - Configure proper favicon links in app",
            "sha": "affa396"
          },
          {
            "date": "2025-04-05",
            "text": "Use API-based sorting instead of client-side hack for /sources page Replace client-side JavaScript sorting with proper SvelteKit URL-based routing that leverages the API's sorting capabilities",
            "sha": "8aa1a47"
          },
          {
            "date": "2025-04-05",
            "text": "Require virtualenv to deploy backend",
            "sha": "8aded97"
          },
          {
            "date": "2025-04-05",
            "text": "Fix accessibility and Svelte warnings 1",
            "sha": "82c4ef2"
          },
          {
            "date": "2025-04-05",
            "text": "Fix Svelte component unused export warnings 1",
            "sha": "5868948"
          },
          {
            "date": "2025-04-05",
            "text": "Add error handling pages to SvelteKit frontend - Create root error page that catches 404s and other errors - Create language-specific error page that preserves language context - Add language detection to root error for better navigation - Create test-error route for testing language-specific errors - Use Bootstrap styling consistent with the rest of the site",
            "sha": "7c42b46"
          },
          {
            "date": "2025-04-05",
            "text": "Fix API requests in EnhancedText component and handle favicon requests - Updated EnhancedText",
            "sha": "0705b66"
          },
          {
            "date": "2025-04-04",
            "text": "Phosphor-Svelte icons for Sourcefile",
            "sha": "fd915dd"
          },
          {
            "date": "2025-04-03",
            "text": "Renamed sveltekit -> frontend, run_flask -> run_backend",
            "sha": "8e479a4"
          }
        ]
      }
    ]
  }
];
