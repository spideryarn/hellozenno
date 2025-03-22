// Auto-generated from Flask app.url_map
export enum RouteName {
  SYSTEM_VIEWS_ROUTE_TEST = "SYSTEM_VIEWS_ROUTE_TEST",
  SYSTEM_VIEWS_ROUTE_REGISTRY_EXAMPLE = "SYSTEM_VIEWS_ROUTE_REGISTRY_EXAMPLE",
  SYSTEM_VIEWS_MANAGE_SESSION = "SYSTEM_VIEWS_MANAGE_SESSION",
  SYSTEM_VIEWS_GET_USER = "SYSTEM_VIEWS_GET_USER",
  SYS_VIEWS_HEALTH_CHECK = "SYS_VIEWS_HEALTH_CHECK",
  AUTH_VIEWS_AUTH_PAGE = "AUTH_VIEWS_AUTH_PAGE",
  AUTH_VIEWS_PROTECTED_PAGE = "AUTH_VIEWS_PROTECTED_PAGE",
  AUTH_VIEWS_PROFILE_PAGE = "AUTH_VIEWS_PROFILE_PAGE",
  CORE_VIEWS_HOME_VW = "CORE_VIEWS_HOME_VW",
  CORE_VIEWS_LANGUAGES_VW = "CORE_VIEWS_LANGUAGES_VW",
  CORE_VIEWS_EXPERIM_VW = "CORE_VIEWS_EXPERIM_VW",
  CORE_VIEWS_FAVICON_VW = "CORE_VIEWS_FAVICON_VW",
  WORDFORM_VIEWS_WORDFORMS_LIST_VW = "WORDFORM_VIEWS_WORDFORMS_LIST_VW",
  WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW = "WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW",
  WORDFORM_VIEWS_DELETE_WORDFORM = "WORDFORM_VIEWS_DELETE_WORDFORM",
  LEMMA_VIEWS_LEMMAS_LIST_VW = "LEMMA_VIEWS_LEMMAS_LIST_VW",
  LEMMA_VIEWS_GET_LEMMA_METADATA_VW = "LEMMA_VIEWS_GET_LEMMA_METADATA_VW",
  LEMMA_VIEWS_DELETE_LEMMA_VW = "LEMMA_VIEWS_DELETE_LEMMA_VW",
  SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VIEW = "SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VIEW",
  SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VIEW = "SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VIEW",
  SOURCEDIR_VIEWS_CREATE_SOURCEDIR = "SOURCEDIR_VIEWS_CREATE_SOURCEDIR",
  SOURCEDIR_VIEWS_DELETE_SOURCEDIR = "SOURCEDIR_VIEWS_DELETE_SOURCEDIR",
  SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_LANGUAGE = "SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_LANGUAGE",
  SOURCEDIR_VIEWS_RENAME_SOURCEDIR = "SOURCEDIR_VIEWS_RENAME_SOURCEDIR",
  SOURCEDIR_VIEWS_UPLOAD_SOURCEDIR_NEW_SOURCEFILE = "SOURCEDIR_VIEWS_UPLOAD_SOURCEDIR_NEW_SOURCEFILE",
  SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_DESCRIPTION = "SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_DESCRIPTION",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES",
  SOURCEFILE_VIEWS_VIEW_SOURCEFILE = "SOURCEFILE_VIEWS_VIEW_SOURCEFILE",
  SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE = "SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE",
  SOURCEFILE_VIEWS_PROCESS_SOURCEFILE = "SOURCEFILE_VIEWS_PROCESS_SOURCEFILE",
  SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO = "SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO",
  SOURCEFILE_VIEWS_UPDATE_SOURCEFILE = "SOURCEFILE_VIEWS_UPDATE_SOURCEFILE",
  SOURCEFILE_VIEWS_PROCESS_INDIVIDUAL_WORDS = "SOURCEFILE_VIEWS_PROCESS_INDIVIDUAL_WORDS",
  SOURCEFILE_VIEWS_UPDATE_SOURCEFILE_DESCRIPTION = "SOURCEFILE_VIEWS_UPDATE_SOURCEFILE_DESCRIPTION",
  SOURCEFILE_VIEWS_MOVE_SOURCEFILE = "SOURCEFILE_VIEWS_MOVE_SOURCEFILE",
  SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES = "SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES",
  SOURCEFILE_VIEWS_DELETE_SOURCEFILE = "SOURCEFILE_VIEWS_DELETE_SOURCEFILE",
  SOURCEFILE_VIEWS_RENAME_SOURCEFILE = "SOURCEFILE_VIEWS_RENAME_SOURCEFILE",
  SOURCEFILE_VIEWS_NEXT_SOURCEFILE = "SOURCEFILE_VIEWS_NEXT_SOURCEFILE",
  SOURCEFILE_VIEWS_PREV_SOURCEFILE = "SOURCEFILE_VIEWS_PREV_SOURCEFILE",
  SOURCEFILE_VIEWS_CREATE_SOURCEFILE_FROM_TEXT = "SOURCEFILE_VIEWS_CREATE_SOURCEFILE_FROM_TEXT",
  SOURCEFILE_VIEWS_ADD_SOURCEFILE_FROM_YOUTUBE = "SOURCEFILE_VIEWS_ADD_SOURCEFILE_FROM_YOUTUBE",
  SOURCEFILE_VIEWS_GENERATE_SOURCEFILE_AUDIO = "SOURCEFILE_VIEWS_GENERATE_SOURCEFILE_AUDIO",
  PHRASE_VIEWS_PHRASES_LIST_VW = "PHRASE_VIEWS_PHRASES_LIST_VW",
  PHRASE_VIEWS_GET_PHRASE_METADATA_VW = "PHRASE_VIEWS_GET_PHRASE_METADATA_VW",
  SENTENCE_VIEWS_SENTENCES_LIST_VW = "SENTENCE_VIEWS_SENTENCES_LIST_VW",
  SENTENCE_VIEWS_GET_SENTENCE_VW = "SENTENCE_VIEWS_GET_SENTENCE_VW",
  SEARCH_SEARCH_LANDING_VW = "SEARCH_SEARCH_LANDING_VW",
  SEARCH_SEARCH_WORD_VW = "SEARCH_SEARCH_WORD_VW",
  FLASHCARD_VIEWS_STATIC = "FLASHCARD_VIEWS_STATIC",
  FLASHCARD_VIEWS_FLASHCARD_LANDING_VW = "FLASHCARD_VIEWS_FLASHCARD_LANDING_VW",
  FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW = "FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW",
  FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW = "FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW",
  CORE_API_HOME_API = "CORE_API_HOME_API",
  WORDFORM_API_WORD_PREVIEW = "WORDFORM_API_WORD_PREVIEW",
  WORDFORM_API_GET_MP3 = "WORDFORM_API_GET_MP3",
  LEMMA_API_GET_LEMMA_DATA_API = "LEMMA_API_GET_LEMMA_DATA_API",
  PHRASE_API_PHRASE_PREVIEW_API = "PHRASE_API_PHRASE_PREVIEW_API",
  SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API = "SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API",
  SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API = "SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API",
  SOURCEFILE_API_MOVE_SOURCEFILE_API = "SOURCEFILE_API_MOVE_SOURCEFILE_API",
  SOURCEFILE_API_DELETE_SOURCEFILE_API = "SOURCEFILE_API_DELETE_SOURCEFILE_API",
  SOURCEFILE_API_RENAME_SOURCEFILE_API = "SOURCEFILE_API_RENAME_SOURCEFILE_API",
  SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API = "SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API",
  SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API = "SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API",
  SENTENCE_API_GET_RANDOM_SENTENCE_API = "SENTENCE_API_GET_RANDOM_SENTENCE_API",
  SENTENCE_API_GET_SENTENCE_AUDIO_API = "SENTENCE_API_GET_SENTENCE_AUDIO_API",
  SENTENCE_API_DELETE_SENTENCE_API = "SENTENCE_API_DELETE_SENTENCE_API",
  SENTENCE_API_RENAME_SENTENCE_API = "SENTENCE_API_RENAME_SENTENCE_API",
  SENTENCE_API_GENERATE_SENTENCE_AUDIO_API = "SENTENCE_API_GENERATE_SENTENCE_AUDIO_API",
}


export const ROUTES = {
  SYSTEM_VIEWS_ROUTE_TEST: "/route-test",
  SYSTEM_VIEWS_ROUTE_REGISTRY_EXAMPLE: "/route-registry-example",
  SYSTEM_VIEWS_MANAGE_SESSION: "/api/auth/session",
  SYSTEM_VIEWS_GET_USER: "/api/auth/user",
  SYS_VIEWS_HEALTH_CHECK: "/sys/health-check",
  AUTH_VIEWS_AUTH_PAGE: "/auth/",
  AUTH_VIEWS_PROTECTED_PAGE: "/auth/protected",
  AUTH_VIEWS_PROFILE_PAGE: "/auth/profile",
  CORE_VIEWS_HOME_VW: "/",
  CORE_VIEWS_LANGUAGES_VW: "/lang",
  CORE_VIEWS_EXPERIM_VW: "/experim",
  CORE_VIEWS_FAVICON_VW: "/favicon.ico",
  WORDFORM_VIEWS_WORDFORMS_LIST_VW: "/lang/{target_language_code}/wordforms",
  WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW: "/lang/{target_language_code}/wordform/{wordform}",
  WORDFORM_VIEWS_DELETE_WORDFORM: "/lang/{target_language_code}/wordform/{wordform}/delete",
  LEMMA_VIEWS_LEMMAS_LIST_VW: "/lang/{target_language_code}/lemmas",
  LEMMA_VIEWS_GET_LEMMA_METADATA_VW: "/lang/{target_language_code}/lemma/{lemma}",
  LEMMA_VIEWS_DELETE_LEMMA_VW: "/lang/{target_language_code}/lemma/{lemma}/delete",
  SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VIEW: "/lang/{target_language_code}/",
  SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VIEW: "/lang/{target_language_code}/{sourcedir_slug}",
  SOURCEDIR_VIEWS_CREATE_SOURCEDIR: "/lang/api/sourcedir/{target_language_code}",
  SOURCEDIR_VIEWS_DELETE_SOURCEDIR: "/lang/api/sourcedir/{target_language_code}/{sourcedir_slug}",
  SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_LANGUAGE: "/lang/api/sourcedir/{target_language_code}/{sourcedir_slug}/language",
  SOURCEDIR_VIEWS_RENAME_SOURCEDIR: "/lang/api/sourcedir/{target_language_code}/{sourcedir_slug}/rename",
  SOURCEDIR_VIEWS_UPLOAD_SOURCEDIR_NEW_SOURCEFILE: "/lang/api/sourcedir/{target_language_code}/{sourcedir_slug}/upload",
  SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_DESCRIPTION: "/lang/api/sourcedir/{target_language_code}/{sourcedir_slug}/update_description",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/text",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/words",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/phrases",
  SOURCEFILE_VIEWS_VIEW_SOURCEFILE: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/view",
  SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/download",
  SOURCEFILE_VIEWS_PROCESS_SOURCEFILE: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process",
  SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/audio",
  SOURCEFILE_VIEWS_UPDATE_SOURCEFILE: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/update",
  SOURCEFILE_VIEWS_PROCESS_INDIVIDUAL_WORDS: "/lang/api/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process_individual",
  SOURCEFILE_VIEWS_UPDATE_SOURCEFILE_DESCRIPTION: "/lang/api/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/update_description",
  SOURCEFILE_VIEWS_MOVE_SOURCEFILE: "/lang/api/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/move",
  SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/sentences",
  SOURCEFILE_VIEWS_DELETE_SOURCEFILE: "/lang/api/sourcedir/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}",
  SOURCEFILE_VIEWS_RENAME_SOURCEFILE: "/lang/api/sourcedir/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/rename",
  SOURCEFILE_VIEWS_NEXT_SOURCEFILE: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/next",
  SOURCEFILE_VIEWS_PREV_SOURCEFILE: "/lang/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/prev",
  SOURCEFILE_VIEWS_CREATE_SOURCEFILE_FROM_TEXT: "/lang/api/sourcedir/{target_language_code}/{sourcedir_slug}/create_from_text",
  SOURCEFILE_VIEWS_ADD_SOURCEFILE_FROM_YOUTUBE: "/lang/{language_code}/{sourcedir_slug}/add_from_youtube",
  SOURCEFILE_VIEWS_GENERATE_SOURCEFILE_AUDIO: "/lang/api/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/generate_audio",
  PHRASE_VIEWS_PHRASES_LIST_VW: "/lang/{target_language_code}/phrases",
  PHRASE_VIEWS_GET_PHRASE_METADATA_VW: "/lang/{target_language_code}/phrases/{slug}",
  SENTENCE_VIEWS_SENTENCES_LIST_VW: "/lang/{language_code}/sentences",
  SENTENCE_VIEWS_GET_SENTENCE_VW: "/lang/{language_code}/sentence/{slug}",
  SEARCH_SEARCH_LANDING_VW: "/lang/{target_language_code}/search",
  SEARCH_SEARCH_WORD_VW: "/lang/{target_language_code}/search/{wordform}",
  FLASHCARD_VIEWS_STATIC: "/lang/build/{filename}",
  FLASHCARD_VIEWS_FLASHCARD_LANDING_VW: "/lang/{language_code}/flashcards",
  FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW: "/lang/{language_code}/flashcards/sentence/{slug}",
  FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW: "/lang/{language_code}/flashcards/random",
  CORE_API_HOME_API: "/api/",
  WORDFORM_API_WORD_PREVIEW: "/api/lang/word/{target_language_code}/{word}/preview",
  WORDFORM_API_GET_MP3: "/api/lang/word/{target_language_code}/{word}/mp3",
  LEMMA_API_GET_LEMMA_DATA_API: "/api/lang/lemma/{target_language_code}/{lemma}/data",
  PHRASE_API_PHRASE_PREVIEW_API: "/api/lang/phrase/{target_language_code}/preview/{phrase}",
  SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process_individual",
  SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/update_description",
  SOURCEFILE_API_MOVE_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/move",
  SOURCEFILE_API_DELETE_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}",
  SOURCEFILE_API_RENAME_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/rename",
  SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/create_from_text",
  SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/generate_audio",
  SENTENCE_API_GET_RANDOM_SENTENCE_API: "/api/lang/sentence/{target_language_code}/random",
  SENTENCE_API_GET_SENTENCE_AUDIO_API: "/api/lang/sentence/{target_language_code}/{sentence_id}/audio",
  SENTENCE_API_DELETE_SENTENCE_API: "/api/lang/sentence/{target_language_code}/{slug}",
  SENTENCE_API_RENAME_SENTENCE_API: "/api/lang/sentence/{target_language_code}/{slug}/rename",
  SENTENCE_API_GENERATE_SENTENCE_AUDIO_API: "/api/lang/sentence/{target_language_code}/{slug}/generate_audio",
} as const;


export type RouteParams = {
  [RouteName.SYSTEM_VIEWS_ROUTE_TEST]: {};
  [RouteName.SYSTEM_VIEWS_ROUTE_REGISTRY_EXAMPLE]: {};
  [RouteName.SYSTEM_VIEWS_MANAGE_SESSION]: {};
  [RouteName.SYSTEM_VIEWS_GET_USER]: {};
  [RouteName.SYS_VIEWS_HEALTH_CHECK]: {};
  [RouteName.AUTH_VIEWS_AUTH_PAGE]: {};
  [RouteName.AUTH_VIEWS_PROTECTED_PAGE]: {};
  [RouteName.AUTH_VIEWS_PROFILE_PAGE]: {};
  [RouteName.CORE_VIEWS_HOME_VW]: {};
  [RouteName.CORE_VIEWS_LANGUAGES_VW]: {};
  [RouteName.CORE_VIEWS_EXPERIM_VW]: {};
  [RouteName.CORE_VIEWS_FAVICON_VW]: {};
  [RouteName.WORDFORM_VIEWS_WORDFORMS_LIST_VW]: { target_language_code: string };
  [RouteName.WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW]: { target_language_code: string; wordform: string };
  [RouteName.WORDFORM_VIEWS_DELETE_WORDFORM]: { target_language_code: string; wordform: string };
  [RouteName.LEMMA_VIEWS_LEMMAS_LIST_VW]: { target_language_code: string };
  [RouteName.LEMMA_VIEWS_GET_LEMMA_METADATA_VW]: { target_language_code: string; lemma: string };
  [RouteName.LEMMA_VIEWS_DELETE_LEMMA_VW]: { target_language_code: string; lemma: string };
  [RouteName.SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VIEW]: { target_language_code: string };
  [RouteName.SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VIEW]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_VIEWS_CREATE_SOURCEDIR]: { target_language_code: string };
  [RouteName.SOURCEDIR_VIEWS_DELETE_SOURCEDIR]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_LANGUAGE]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_VIEWS_RENAME_SOURCEDIR]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_VIEWS_UPLOAD_SOURCEDIR_NEW_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_VIEWS_UPDATE_SOURCEDIR_DESCRIPTION]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_VIEW_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_PROCESS_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_UPDATE_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_PROCESS_INDIVIDUAL_WORDS]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_UPDATE_SOURCEFILE_DESCRIPTION]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_MOVE_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_DELETE_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_RENAME_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_NEXT_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_PREV_SOURCEFILE]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_CREATE_SOURCEFILE_FROM_TEXT]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEFILE_VIEWS_ADD_SOURCEFILE_FROM_YOUTUBE]: { language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEFILE_VIEWS_GENERATE_SOURCEFILE_AUDIO]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.PHRASE_VIEWS_PHRASES_LIST_VW]: { target_language_code: string };
  [RouteName.PHRASE_VIEWS_GET_PHRASE_METADATA_VW]: { target_language_code: string; slug: string };
  [RouteName.SENTENCE_VIEWS_SENTENCES_LIST_VW]: { language_code: string };
  [RouteName.SENTENCE_VIEWS_GET_SENTENCE_VW]: { language_code: string; slug: string };
  [RouteName.SEARCH_SEARCH_LANDING_VW]: { target_language_code: string };
  [RouteName.SEARCH_SEARCH_WORD_VW]: { target_language_code: string; wordform: string };
  [RouteName.FLASHCARD_VIEWS_STATIC]: { filename: string };
  [RouteName.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW]: { language_code: string };
  [RouteName.FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW]: { language_code: string; slug: string };
  [RouteName.FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW]: { language_code: string };
  [RouteName.CORE_API_HOME_API]: {};
  [RouteName.WORDFORM_API_WORD_PREVIEW]: { target_language_code: string; word: string };
  [RouteName.WORDFORM_API_GET_MP3]: { target_language_code: string; word: string };
  [RouteName.LEMMA_API_GET_LEMMA_DATA_API]: { target_language_code: string; lemma: string };
  [RouteName.PHRASE_API_PHRASE_PREVIEW_API]: { target_language_code: string; phrase: string };
  [RouteName.SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_MOVE_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_DELETE_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_RENAME_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SENTENCE_API_GET_RANDOM_SENTENCE_API]: { target_language_code: string };
  [RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_API]: { target_language_code: string; sentence_id: string };
  [RouteName.SENTENCE_API_DELETE_SENTENCE_API]: { target_language_code: string; slug: string };
  [RouteName.SENTENCE_API_RENAME_SENTENCE_API]: { target_language_code: string; slug: string };
  [RouteName.SENTENCE_API_GENERATE_SENTENCE_AUDIO_API]: { target_language_code: string; slug: string };
};


/**
 * Resolve a route template with parameters.
 * 
 * @param routeName Name of the route from ROUTES
 * @param params Parameters to substitute in the route template
 * @returns Resolved URL with parameters
 */
export function resolveRoute<T extends RouteName>(
  routeName: T, 
  params: RouteParams[T]
): string {
  let url = ROUTES[routeName];
  
  // Replace template parameters with actual values
  Object.entries(params).forEach(([key, value]) => {
    url = url.replace(`{${key}}`, encodeURIComponent(String(value)));
  });
  
  return url;
}
