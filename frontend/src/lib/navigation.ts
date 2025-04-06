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
      url = `/language/${params.language_code}/wordforms`;
      break;
    case 'lemmas':
      url = `/language/${params.language_code}/lemmas`;
      break;
    case 'phrases':
      url = `/language/${params.language_code}/phrases`;
      break;
    case 'sentences':
      url = `/language/${params.language_code}/sentences`;
      break;
    case 'search':
      url = `/language/${params.language_code}/search`;
      break;
    
    // Source directory/file pages
    case 'sourcedir':
      url = `/language/${params.language_code}/source/${params.sourcedir_slug}`;
      break;
    case 'sourcefile':
      url = `/language/${params.language_code}/source/${params.sourcedir_slug}/${params.sourcefile_slug}`;
      break;
    case 'sourcefile_text':
      url = `/language/${params.language_code}/source/${params.sourcedir_slug}/${params.sourcefile_slug}/text`;
      break;
    case 'sourcefile_words':
      url = `/language/${params.language_code}/source/${params.sourcedir_slug}/${params.sourcefile_slug}/words`;
      break;
    case 'sourcefile_phrases':
      url = `/language/${params.language_code}/source/${params.sourcedir_slug}/${params.sourcefile_slug}/phrases`;
      break;
    
    // Flashcards
    case 'flashcards':
      url = `/language/${params.language_code}/flashcards`;
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