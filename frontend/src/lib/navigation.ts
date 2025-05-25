/**
 * Navigation utilities for client-side routing
 */

/**
 * Page types available for navigation
 */
export type PageType = 
  // Source directory/file navigation
  | 'sourcedir'
  | 'sourcefile'
  | 'sourcefile_text'
  | 'sourcefile_words'
  | 'sourcefile_phrases'
  | 'flashcards'
  // Language related pages
  | 'languages'
  | 'wordforms'
  | 'lemmas'
  | 'phrases'
  | 'sentences'
  | 'sources'
  | 'search';

/**
 * Helper function for generating client-side navigation URLs
 * This is separate from API URLs which are used for data fetching
 * 
 * @param page The page type to navigate to
 * @param params Parameters needed for the URL (language code, slugs, etc.)
 * @param query Optional query parameters
 * @returns The full URL string for client-side navigation
 */

import type { SupabaseClient } from '@supabase/supabase-js';
import { goto } from '$app/navigation';
import { apiFetch } from './api';
import { RouteName } from './generated/routes';

/**
 * Handles post-authentication redirection based on user profile
 * If the user has a target language set, redirects to that language's sources page
 * Otherwise, falls back to the provided URL
 * 
 * @param supabaseClient The Supabase client instance
 * @param fallbackUrl URL to redirect to if no target language is set
 * @returns Promise resolving when redirection is complete
 */
export async function redirectBasedOnProfile(
  supabaseClient: SupabaseClient | null,
  fallbackUrl: string
): Promise<void> {
  if (!supabaseClient) {
    await goto(fallbackUrl);
    return;
  }

  try {
    const profile = await apiFetch({
      supabaseClient,
      routeName: RouteName.PROFILE_API_GET_CURRENT_PROFILE_API,
      params: {},
      options: { method: 'GET' }
    });
    
    // If user has a target language set, redirect to sources page
    if (profile && profile.target_language_code) {
      await goto(getPageUrl('sources', { target_language_code: profile.target_language_code }));
    } else {
      await goto(fallbackUrl);
    }
  } catch (err) {
    // Fall back to the original redirect if profile fetch fails
    console.error('Error fetching profile for redirection:', err);
    await goto(fallbackUrl);
  }
}
export function getPageUrl(
  page: PageType,
  params: Record<string, string | undefined>,
  query?: Record<string, string>
): string {
  let url: string;
  
  // Build the appropriate URL based on the page type
  switch (page) {
    // Language pages
    case 'languages':
      url = '/languages';
      break;
    case 'wordforms':
      url = `/language/${params.target_language_code}/wordforms`;
      break;
    case 'lemmas':
      url = `/language/${params.target_language_code}/lemmas`;
      break;
    case 'phrases':
      url = `/language/${params.target_language_code}/phrases`;
      break;
    case 'sentences':
      url = `/language/${params.target_language_code}/sentences`;
      break;
    case 'search':
      url = `/language/${params.target_language_code}/search`;
      break;
    case 'sources':
      url = `/language/${params.target_language_code}/sources`;
      break;
    
    // Source directory/file pages
    case 'sourcedir':
      url = `/language/${params.target_language_code}/source/${params.sourcedir_slug}`;
      break;
    case 'sourcefile':
      url = `/language/${params.target_language_code}/source/${params.sourcedir_slug}/${params.sourcefile_slug}`;
      break;
    case 'sourcefile_text':
      url = `/language/${params.target_language_code}/source/${params.sourcedir_slug}/${params.sourcefile_slug}/text`;
      break;
    case 'sourcefile_words':
      url = `/language/${params.target_language_code}/source/${params.sourcedir_slug}/${params.sourcefile_slug}/words`;
      break;
    case 'sourcefile_phrases':
      url = `/language/${params.target_language_code}/source/${params.sourcedir_slug}/${params.sourcefile_slug}/phrases`;
      break;
    
    // Flashcards
    case 'flashcards':
      url = `/language/${params.target_language_code}/flashcards`;
      break;
    
    default:
      url = '/';
  }
  
  // Add query string if provided
  if (query && Object.keys(query).length > 0) {
    const queryString = Object.entries(query)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&');
    url = `${url}?${queryString}`;
  }
  
  return url;
} 