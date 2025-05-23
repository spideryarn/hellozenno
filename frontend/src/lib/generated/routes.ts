// Auto-generated from Flask app.url_map
export enum RouteName {
  SYSTEM_VIEWS_HEALTH_CHECK_VW = "SYSTEM_VIEWS_HEALTH_CHECK_VW",
  SYSTEM_VIEWS_ROUTE_TEST_VW = "SYSTEM_VIEWS_ROUTE_TEST_VW",
  AUTH_API_GET_USER_API = "AUTH_API_GET_USER_API",
  CORE_VIEWS_HOME_VW = "CORE_VIEWS_HOME_VW",
  CORE_VIEWS_EXPERIM_VW = "CORE_VIEWS_EXPERIM_VW",
  LANGUAGES_VIEWS_LANGUAGES_LIST_VW = "LANGUAGES_VIEWS_LANGUAGES_LIST_VW",
  WORDFORM_VIEWS_WORDFORMS_LIST_VW = "WORDFORM_VIEWS_WORDFORMS_LIST_VW",
  WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW = "WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW",
  LEMMA_VIEWS_LEMMAS_LIST_VW = "LEMMA_VIEWS_LEMMAS_LIST_VW",
  LEMMA_VIEWS_GET_LEMMA_METADATA_VW = "LEMMA_VIEWS_GET_LEMMA_METADATA_VW",
  SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VW = "SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VW",
  SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW = "SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_VW = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_VW",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT_VW = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT_VW",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS_VW = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS_VW",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES_VW = "SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES_VW",
  SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW = "SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW",
  SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW = "SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW",
  SOURCEFILE_VIEWS_PROCESS_SOURCEFILE_VW = "SOURCEFILE_VIEWS_PROCESS_SOURCEFILE_VW",
  SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO_VW = "SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO_VW",
  SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES_VW = "SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES_VW",
  SOURCEFILE_VIEWS_NEXT_SOURCEFILE_VW = "SOURCEFILE_VIEWS_NEXT_SOURCEFILE_VW",
  SOURCEFILE_VIEWS_PREV_SOURCEFILE_VW = "SOURCEFILE_VIEWS_PREV_SOURCEFILE_VW",
  PHRASE_VIEWS_PHRASES_LIST_VW = "PHRASE_VIEWS_PHRASES_LIST_VW",
  PHRASE_VIEWS_GET_PHRASE_METADATA_VW = "PHRASE_VIEWS_GET_PHRASE_METADATA_VW",
  SENTENCE_VIEWS_SENTENCES_LIST_VW = "SENTENCE_VIEWS_SENTENCES_LIST_VW",
  SENTENCE_VIEWS_GET_SENTENCE_VW = "SENTENCE_VIEWS_GET_SENTENCE_VW",
  SEARCH_VIEWS_SEARCH_LANDING_VW = "SEARCH_VIEWS_SEARCH_LANDING_VW",
  SEARCH_VIEWS_SEARCH_WORD_VW = "SEARCH_VIEWS_SEARCH_WORD_VW",
  FLASHCARD_VIEWS_FLASHCARD_LANDING_VW = "FLASHCARD_VIEWS_FLASHCARD_LANDING_VW",
  FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW = "FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW",
  FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW = "FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW",
  SOURCEDIR_API_CREATE_SOURCEDIR_API = "SOURCEDIR_API_CREATE_SOURCEDIR_API",
  SOURCEDIR_API_DELETE_SOURCEDIR_API = "SOURCEDIR_API_DELETE_SOURCEDIR_API",
  SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API = "SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API",
  SOURCEDIR_API_RENAME_SOURCEDIR_API = "SOURCEDIR_API_RENAME_SOURCEDIR_API",
  SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API = "SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API",
  SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API = "SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API",
  SOURCEDIR_API_GET_SOURCEDIRS_FOR_LANGUAGE_API = "SOURCEDIR_API_GET_SOURCEDIRS_FOR_LANGUAGE_API",
  SOURCEDIR_API_SOURCEFILES_FOR_SOURCEDIR_API = "SOURCEDIR_API_SOURCEFILES_FOR_SOURCEDIR_API",
  WORDFORM_API_WORD_PREVIEW_API = "WORDFORM_API_WORD_PREVIEW_API",
  WORDFORM_API_GET_MP3_API = "WORDFORM_API_GET_MP3_API",
  WORDFORM_API_WORDFORMS_LIST_API = "WORDFORM_API_WORDFORMS_LIST_API",
  WORDFORM_API_GET_WORDFORM_METADATA_API = "WORDFORM_API_GET_WORDFORM_METADATA_API",
  WORDFORM_API_DELETE_WORDFORM_API = "WORDFORM_API_DELETE_WORDFORM_API",
  LEMMA_API_GET_LEMMA_DATA_API = "LEMMA_API_GET_LEMMA_DATA_API",
  LEMMA_API_LEMMAS_LIST_API = "LEMMA_API_LEMMAS_LIST_API",
  LEMMA_API_GET_LEMMA_METADATA_API = "LEMMA_API_GET_LEMMA_METADATA_API",
  LEMMA_API_COMPLETE_LEMMA_METADATA_API = "LEMMA_API_COMPLETE_LEMMA_METADATA_API",
  LEMMA_API_IGNORE_LEMMA_API = "LEMMA_API_IGNORE_LEMMA_API",
  LEMMA_API_UNIGNORE_LEMMA_API = "LEMMA_API_UNIGNORE_LEMMA_API",
  LEMMA_API_GET_IGNORED_LEMMAS_API = "LEMMA_API_GET_IGNORED_LEMMAS_API",
  LEMMA_API_DELETE_LEMMA_API = "LEMMA_API_DELETE_LEMMA_API",
  PHRASE_API_PHRASES_LIST_API = "PHRASE_API_PHRASES_LIST_API",
  PHRASE_API_PHRASE_PREVIEW_API = "PHRASE_API_PHRASE_PREVIEW_API",
  PHRASE_API_GET_PHRASE_METADATA_API = "PHRASE_API_GET_PHRASE_METADATA_API",
  PHRASE_API_DELETE_PHRASE_API = "PHRASE_API_DELETE_PHRASE_API",
  SOURCEFILE_API_INSPECT_SOURCEFILE_API = "SOURCEFILE_API_INSPECT_SOURCEFILE_API",
  SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API = "SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API",
  SOURCEFILE_API_INSPECT_SOURCEFILE_WORDS_API = "SOURCEFILE_API_INSPECT_SOURCEFILE_WORDS_API",
  SOURCEFILE_API_INSPECT_SOURCEFILE_PHRASES_API = "SOURCEFILE_API_INSPECT_SOURCEFILE_PHRASES_API",
  SOURCEFILE_API_INSPECT_SOURCEFILE_TRANSLATION_API = "SOURCEFILE_API_INSPECT_SOURCEFILE_TRANSLATION_API",
  SOURCEFILE_API_INSPECT_SOURCEFILE_IMAGE_API = "SOURCEFILE_API_INSPECT_SOURCEFILE_IMAGE_API",
  SOURCEFILE_API_INSPECT_SOURCEFILE_AUDIO_API = "SOURCEFILE_API_INSPECT_SOURCEFILE_AUDIO_API",
  SOURCEFILE_API_PROCESS_SOURCEFILE_API = "SOURCEFILE_API_PROCESS_SOURCEFILE_API",
  SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API = "SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API",
  SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API = "SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API",
  SOURCEFILE_API_MOVE_SOURCEFILE_API = "SOURCEFILE_API_MOVE_SOURCEFILE_API",
  SOURCEFILE_API_DELETE_SOURCEFILE_API = "SOURCEFILE_API_DELETE_SOURCEFILE_API",
  SOURCEFILE_API_RENAME_SOURCEFILE_API = "SOURCEFILE_API_RENAME_SOURCEFILE_API",
  SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API = "SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API",
  SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API = "SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API",
  SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API = "SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API",
  SOURCEFILE_API_CREATE_SOURCEFILE_FROM_URL_API = "SOURCEFILE_API_CREATE_SOURCEFILE_FROM_URL_API",
  SOURCEFILE_PROCESSING_API_EXTRACT_TEXT_API = "SOURCEFILE_PROCESSING_API_EXTRACT_TEXT_API",
  SOURCEFILE_PROCESSING_API_TRANSLATE_API = "SOURCEFILE_PROCESSING_API_TRANSLATE_API",
  SOURCEFILE_PROCESSING_API_PROCESS_WORDFORMS_API = "SOURCEFILE_PROCESSING_API_PROCESS_WORDFORMS_API",
  SOURCEFILE_PROCESSING_API_PROCESS_PHRASES_API = "SOURCEFILE_PROCESSING_API_PROCESS_PHRASES_API",
  SOURCEFILE_PROCESSING_API_SOURCEFILE_STATUS_API = "SOURCEFILE_PROCESSING_API_SOURCEFILE_STATUS_API",
  SENTENCE_API_GET_RANDOM_SENTENCE_API = "SENTENCE_API_GET_RANDOM_SENTENCE_API",
  SENTENCE_API_GET_SENTENCE_BY_SLUG_API = "SENTENCE_API_GET_SENTENCE_BY_SLUG_API",
  SENTENCE_API_GET_SENTENCE_AUDIO_API = "SENTENCE_API_GET_SENTENCE_AUDIO_API",
  SENTENCE_API_GET_SENTENCE_AUDIO_BY_LANGUAGE_API = "SENTENCE_API_GET_SENTENCE_AUDIO_BY_LANGUAGE_API",
  SENTENCE_API_DELETE_SENTENCE_API = "SENTENCE_API_DELETE_SENTENCE_API",
  SENTENCE_API_RENAME_SENTENCE_API = "SENTENCE_API_RENAME_SENTENCE_API",
  SENTENCE_API_GENERATE_SENTENCE_AUDIO_API = "SENTENCE_API_GENERATE_SENTENCE_AUDIO_API",
  SENTENCE_API_SENTENCES_LIST_API = "SENTENCE_API_SENTENCES_LIST_API",
  LANGUAGES_API_GET_LANGUAGES_API = "LANGUAGES_API_GET_LANGUAGES_API",
  LANGUAGES_API_GET_LANGUAGE_NAME_API = "LANGUAGES_API_GET_LANGUAGE_NAME_API",
  FLASHCARD_API_FLASHCARD_SENTENCE_API = "FLASHCARD_API_FLASHCARD_SENTENCE_API",
  FLASHCARD_API_RANDOM_FLASHCARD_API = "FLASHCARD_API_RANDOM_FLASHCARD_API",
  FLASHCARD_API_FLASHCARD_LANDING_API = "FLASHCARD_API_FLASHCARD_LANDING_API",
  SEARCH_API_SEARCH_LANDING_API = "SEARCH_API_SEARCH_LANDING_API",
  SEARCH_API_SEARCH_WORD_API = "SEARCH_API_SEARCH_WORD_API",
  SEARCH_API_UNIFIED_SEARCH_API = "SEARCH_API_UNIFIED_SEARCH_API",
  PROFILE_API_GET_CURRENT_PROFILE_API = "PROFILE_API_GET_CURRENT_PROFILE_API",
  PROFILE_API_UPDATE_PROFILE_API = "PROFILE_API_UPDATE_PROFILE_API",
  PROFILE_API_GET_USER_EMAIL_API = "PROFILE_API_GET_USER_EMAIL_API",
}


export const ROUTES = {
  SYSTEM_VIEWS_HEALTH_CHECK_VW: "/sys/health-check",
  SYSTEM_VIEWS_ROUTE_TEST_VW: "/sys/route-test",
  AUTH_API_GET_USER_API: "/api/auth/user",
  CORE_VIEWS_HOME_VW: "/",
  CORE_VIEWS_EXPERIM_VW: "/experim",
  LANGUAGES_VIEWS_LANGUAGES_LIST_VW: "/languages",
  WORDFORM_VIEWS_WORDFORMS_LIST_VW: "/language/{target_language_code}/wordforms/",
  WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW: "/language/{target_language_code}/wordform/{wordform}",
  LEMMA_VIEWS_LEMMAS_LIST_VW: "/language/{target_language_code}/lemmas",
  LEMMA_VIEWS_GET_LEMMA_METADATA_VW: "/language/{target_language_code}/lemma/{lemma}",
  SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VW: "/language/{target_language_code}/sources",
  SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW: "/language/{target_language_code}/source/{sourcedir_slug}",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/text",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/words",
  SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/phrases",
  SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/view",
  SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/download",
  SOURCEFILE_VIEWS_PROCESS_SOURCEFILE_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/process",
  SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/audio",
  SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/sentences",
  SOURCEFILE_VIEWS_NEXT_SOURCEFILE_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/next",
  SOURCEFILE_VIEWS_PREV_SOURCEFILE_VW: "/language/{target_language_code}/source/{sourcedir_slug}/{sourcefile_slug}/prev",
  PHRASE_VIEWS_PHRASES_LIST_VW: "/language/{target_language_code}/phrases",
  PHRASE_VIEWS_GET_PHRASE_METADATA_VW: "/language/{target_language_code}/phrase/{slug}",
  SENTENCE_VIEWS_SENTENCES_LIST_VW: "/language/{target_language_code}/sentences",
  SENTENCE_VIEWS_GET_SENTENCE_VW: "/language/{target_language_code}/sentence/{slug}",
  SEARCH_VIEWS_SEARCH_LANDING_VW: "/language/{target_language_code}/search",
  SEARCH_VIEWS_SEARCH_WORD_VW: "/language/{target_language_code}/search/{wordform}",
  FLASHCARD_VIEWS_FLASHCARD_LANDING_VW: "/languages/{target_language_code}/flashcards",
  FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW: "/languages/{target_language_code}/flashcards/sentence/{slug}",
  FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW: "/languages/{target_language_code}/flashcards/random",
  SOURCEDIR_API_CREATE_SOURCEDIR_API: "/api/lang/sourcedir/{target_language_code}",
  SOURCEDIR_API_DELETE_SOURCEDIR_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}",
  SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}/language",
  SOURCEDIR_API_RENAME_SOURCEDIR_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}/rename",
  SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}/upload",
  SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}/update_description",
  SOURCEDIR_API_GET_SOURCEDIRS_FOR_LANGUAGE_API: "/api/lang/sourcedir/{target_language_code}/sources",
  SOURCEDIR_API_SOURCEFILES_FOR_SOURCEDIR_API: "/api/lang/sourcedir/{target_language_code}/{sourcedir_slug}",
  WORDFORM_API_WORD_PREVIEW_API: "/api/lang/word/{target_language_code}/{word}/preview",
  WORDFORM_API_GET_MP3_API: "/api/lang/word/{target_language_code}/{word}/mp3",
  WORDFORM_API_WORDFORMS_LIST_API: "/api/lang/word/{target_language_code}/wordforms",
  WORDFORM_API_GET_WORDFORM_METADATA_API: "/api/lang/word/{target_language_code}/wordform/{wordform}",
  WORDFORM_API_DELETE_WORDFORM_API: "/api/lang/word/{target_language_code}/wordform/{wordform}/delete",
  LEMMA_API_GET_LEMMA_DATA_API: "/api/lang/lemma/{target_language_code}/{lemma}/data",
  LEMMA_API_LEMMAS_LIST_API: "/api/lang/lemma/{target_language_code}/lemmas",
  LEMMA_API_GET_LEMMA_METADATA_API: "/api/lang/lemma/{target_language_code}/lemma/{lemma}/metadata",
  LEMMA_API_COMPLETE_LEMMA_METADATA_API: "/api/lang/lemma/{target_language_code}/{lemma}/complete_metadata",
  LEMMA_API_IGNORE_LEMMA_API: "/api/lang/lemma/{target_language_code}/{lemma}/ignore",
  LEMMA_API_UNIGNORE_LEMMA_API: "/api/lang/lemma/{target_language_code}/{lemma}/unignore",
  LEMMA_API_GET_IGNORED_LEMMAS_API: "/api/lang/lemma/{target_language_code}/ignored",
  LEMMA_API_DELETE_LEMMA_API: "/api/lang/lemma/{target_language_code}/lemma/{lemma}/delete",
  PHRASE_API_PHRASES_LIST_API: "/api/lang/phrase/{target_language_code}/phrases",
  PHRASE_API_PHRASE_PREVIEW_API: "/api/lang/phrase/{target_language_code}/preview/{phrase}",
  PHRASE_API_GET_PHRASE_METADATA_API: "/api/lang/phrase/{target_language_code}/detail/{slug}",
  PHRASE_API_DELETE_PHRASE_API: "/api/lang/phrase/{target_language_code}/detail/{slug}/delete",
  SOURCEFILE_API_INSPECT_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}",
  SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/text",
  SOURCEFILE_API_INSPECT_SOURCEFILE_WORDS_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/words",
  SOURCEFILE_API_INSPECT_SOURCEFILE_PHRASES_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/phrases",
  SOURCEFILE_API_INSPECT_SOURCEFILE_TRANSLATION_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/translation",
  SOURCEFILE_API_INSPECT_SOURCEFILE_IMAGE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/image",
  SOURCEFILE_API_INSPECT_SOURCEFILE_AUDIO_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/audio",
  SOURCEFILE_API_PROCESS_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process",
  SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process_individual",
  SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/update_description",
  SOURCEFILE_API_MOVE_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/move",
  SOURCEFILE_API_DELETE_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}",
  SOURCEFILE_API_RENAME_SOURCEFILE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/rename",
  SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/create_from_text",
  SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/youtube",
  SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/generate_audio",
  SOURCEFILE_API_CREATE_SOURCEFILE_FROM_URL_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/create_from_url",
  SOURCEFILE_PROCESSING_API_EXTRACT_TEXT_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/extract_text",
  SOURCEFILE_PROCESSING_API_TRANSLATE_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/translate",
  SOURCEFILE_PROCESSING_API_PROCESS_WORDFORMS_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process_wordforms",
  SOURCEFILE_PROCESSING_API_PROCESS_PHRASES_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/process_phrases",
  SOURCEFILE_PROCESSING_API_SOURCEFILE_STATUS_API: "/api/lang/sourcefile/{target_language_code}/{sourcedir_slug}/{sourcefile_slug}/status",
  SENTENCE_API_GET_RANDOM_SENTENCE_API: "/api/lang/sentence/{target_language_code}/random",
  SENTENCE_API_GET_SENTENCE_BY_SLUG_API: "/api/lang/sentence/{target_language_code}/{slug}",
  SENTENCE_API_GET_SENTENCE_AUDIO_API: "/api/lang/sentence/{target_language_code}/{sentence_id}/audio",
  SENTENCE_API_GET_SENTENCE_AUDIO_BY_LANGUAGE_API: "/api/lang/sentence/language/{target_language_code}/{sentence_id}/audio",
  SENTENCE_API_DELETE_SENTENCE_API: "/api/lang/sentence/{target_language_code}/{slug}",
  SENTENCE_API_RENAME_SENTENCE_API: "/api/lang/sentence/{target_language_code}/{slug}/rename",
  SENTENCE_API_GENERATE_SENTENCE_AUDIO_API: "/api/lang/sentence/{target_language_code}/{slug}/generate_audio",
  SENTENCE_API_SENTENCES_LIST_API: "/api/lang/sentence/{target_language_code}/sentences",
  LANGUAGES_API_GET_LANGUAGES_API: "/api/lang/languages",
  LANGUAGES_API_GET_LANGUAGE_NAME_API: "/api/lang/language_name/{target_language_code}",
  FLASHCARD_API_FLASHCARD_SENTENCE_API: "/api/lang/{target_language_code}/flashcards/sentence/{slug}",
  FLASHCARD_API_RANDOM_FLASHCARD_API: "/api/lang/{target_language_code}/flashcards/random",
  FLASHCARD_API_FLASHCARD_LANDING_API: "/api/lang/{target_language_code}/flashcards/landing",
  SEARCH_API_SEARCH_LANDING_API: "/api/lang/{target_language_code}/search",
  SEARCH_API_SEARCH_WORD_API: "/api/lang/{target_language_code}/search/{wordform}",
  SEARCH_API_UNIFIED_SEARCH_API: "/api/lang/{target_language_code}/unified_search",
  PROFILE_API_GET_CURRENT_PROFILE_API: "/api/profile/current",
  PROFILE_API_UPDATE_PROFILE_API: "/api/profile/update",
  PROFILE_API_GET_USER_EMAIL_API: "/api/profile/user/{user_id}",
} as const;


export type RouteParams = {
  [RouteName.SYSTEM_VIEWS_HEALTH_CHECK_VW]: {};
  [RouteName.SYSTEM_VIEWS_ROUTE_TEST_VW]: {};
  [RouteName.AUTH_API_GET_USER_API]: {};
  [RouteName.CORE_VIEWS_HOME_VW]: {};
  [RouteName.CORE_VIEWS_EXPERIM_VW]: {};
  [RouteName.LANGUAGES_VIEWS_LANGUAGES_LIST_VW]: {};
  [RouteName.WORDFORM_VIEWS_WORDFORMS_LIST_VW]: { target_language_code: string };
  [RouteName.WORDFORM_VIEWS_GET_WORDFORM_METADATA_VW]: { target_language_code: string; wordform: string };
  [RouteName.LEMMA_VIEWS_LEMMAS_LIST_VW]: { target_language_code: string };
  [RouteName.LEMMA_VIEWS_GET_LEMMA_METADATA_VW]: { target_language_code: string; lemma: string };
  [RouteName.SOURCEDIR_VIEWS_SOURCEDIRS_FOR_LANGUAGE_VW]: { target_language_code: string };
  [RouteName.SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_TEXT_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_WORDS_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_INSPECT_SOURCEFILE_PHRASES_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_VIEW_SOURCEFILE_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_DOWNLOAD_SOURCEFILE_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_PROCESS_SOURCEFILE_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_PLAY_SOURCEFILE_AUDIO_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_SOURCEFILE_SENTENCES_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_NEXT_SOURCEFILE_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_VIEWS_PREV_SOURCEFILE_VW]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.PHRASE_VIEWS_PHRASES_LIST_VW]: { target_language_code: string };
  [RouteName.PHRASE_VIEWS_GET_PHRASE_METADATA_VW]: { target_language_code: string; slug: string };
  [RouteName.SENTENCE_VIEWS_SENTENCES_LIST_VW]: { target_language_code: string };
  [RouteName.SENTENCE_VIEWS_GET_SENTENCE_VW]: { target_language_code: string; slug: string };
  [RouteName.SEARCH_VIEWS_SEARCH_LANDING_VW]: { target_language_code: string };
  [RouteName.SEARCH_VIEWS_SEARCH_WORD_VW]: { target_language_code: string; wordform: string };
  [RouteName.FLASHCARD_VIEWS_FLASHCARD_LANDING_VW]: { target_language_code: string };
  [RouteName.FLASHCARD_VIEWS_FLASHCARD_SENTENCE_VW]: { target_language_code: string; slug: string };
  [RouteName.FLASHCARD_VIEWS_RANDOM_FLASHCARD_VW]: { target_language_code: string };
  [RouteName.SOURCEDIR_API_CREATE_SOURCEDIR_API]: { target_language_code: string };
  [RouteName.SOURCEDIR_API_DELETE_SOURCEDIR_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_API_UPDATE_SOURCEDIR_LANGUAGE_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_API_RENAME_SOURCEDIR_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_API_UPLOAD_SOURCEDIR_NEW_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_API_UPDATE_SOURCEDIR_DESCRIPTION_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEDIR_API_GET_SOURCEDIRS_FOR_LANGUAGE_API]: { target_language_code: string };
  [RouteName.SOURCEDIR_API_SOURCEFILES_FOR_SOURCEDIR_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.WORDFORM_API_WORD_PREVIEW_API]: { target_language_code: string; word: string };
  [RouteName.WORDFORM_API_GET_MP3_API]: { target_language_code: string; word: string };
  [RouteName.WORDFORM_API_WORDFORMS_LIST_API]: { target_language_code: string };
  [RouteName.WORDFORM_API_GET_WORDFORM_METADATA_API]: { target_language_code: string; wordform: string };
  [RouteName.WORDFORM_API_DELETE_WORDFORM_API]: { target_language_code: string; wordform: string };
  [RouteName.LEMMA_API_GET_LEMMA_DATA_API]: { target_language_code: string; lemma: string };
  [RouteName.LEMMA_API_LEMMAS_LIST_API]: { target_language_code: string };
  [RouteName.LEMMA_API_GET_LEMMA_METADATA_API]: { target_language_code: string; lemma: string };
  [RouteName.LEMMA_API_COMPLETE_LEMMA_METADATA_API]: { target_language_code: string; lemma: string };
  [RouteName.LEMMA_API_IGNORE_LEMMA_API]: { target_language_code: string; lemma: string };
  [RouteName.LEMMA_API_UNIGNORE_LEMMA_API]: { target_language_code: string; lemma: string };
  [RouteName.LEMMA_API_GET_IGNORED_LEMMAS_API]: { target_language_code: string };
  [RouteName.LEMMA_API_DELETE_LEMMA_API]: { target_language_code: string; lemma: string };
  [RouteName.PHRASE_API_PHRASES_LIST_API]: { target_language_code: string };
  [RouteName.PHRASE_API_PHRASE_PREVIEW_API]: { target_language_code: string; phrase: string };
  [RouteName.PHRASE_API_GET_PHRASE_METADATA_API]: { target_language_code: string; slug: string };
  [RouteName.PHRASE_API_DELETE_PHRASE_API]: { target_language_code: string; slug: string };
  [RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TEXT_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_WORDS_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_PHRASES_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_TRANSLATION_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_IMAGE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_INSPECT_SOURCEFILE_AUDIO_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_PROCESS_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_PROCESS_INDIVIDUAL_WORDS_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_UPDATE_SOURCEFILE_DESCRIPTION_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_MOVE_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_DELETE_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_RENAME_SOURCEFILE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_CREATE_SOURCEFILE_FROM_TEXT_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEFILE_API_ADD_SOURCEFILE_FROM_YOUTUBE_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEFILE_API_GENERATE_SOURCEFILE_AUDIO_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_API_CREATE_SOURCEFILE_FROM_URL_API]: { target_language_code: string; sourcedir_slug: string };
  [RouteName.SOURCEFILE_PROCESSING_API_EXTRACT_TEXT_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_PROCESSING_API_TRANSLATE_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_PROCESSING_API_PROCESS_WORDFORMS_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_PROCESSING_API_PROCESS_PHRASES_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SOURCEFILE_PROCESSING_API_SOURCEFILE_STATUS_API]: { target_language_code: string; sourcedir_slug: string; sourcefile_slug: string };
  [RouteName.SENTENCE_API_GET_RANDOM_SENTENCE_API]: { target_language_code: string };
  [RouteName.SENTENCE_API_GET_SENTENCE_BY_SLUG_API]: { target_language_code: string; slug: string };
  [RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_API]: { target_language_code: string; sentence_id: string };
  [RouteName.SENTENCE_API_GET_SENTENCE_AUDIO_BY_LANGUAGE_API]: { target_language_code: string; sentence_id: string };
  [RouteName.SENTENCE_API_DELETE_SENTENCE_API]: { target_language_code: string; slug: string };
  [RouteName.SENTENCE_API_RENAME_SENTENCE_API]: { target_language_code: string; slug: string };
  [RouteName.SENTENCE_API_GENERATE_SENTENCE_AUDIO_API]: { target_language_code: string; slug: string };
  [RouteName.SENTENCE_API_SENTENCES_LIST_API]: { target_language_code: string };
  [RouteName.LANGUAGES_API_GET_LANGUAGES_API]: {};
  [RouteName.LANGUAGES_API_GET_LANGUAGE_NAME_API]: { target_language_code: string };
  [RouteName.FLASHCARD_API_FLASHCARD_SENTENCE_API]: { target_language_code: string; slug: string };
  [RouteName.FLASHCARD_API_RANDOM_FLASHCARD_API]: { target_language_code: string };
  [RouteName.FLASHCARD_API_FLASHCARD_LANDING_API]: { target_language_code: string };
  [RouteName.SEARCH_API_SEARCH_LANDING_API]: { target_language_code: string };
  [RouteName.SEARCH_API_SEARCH_WORD_API]: { target_language_code: string; wordform: string };
  [RouteName.SEARCH_API_UNIFIED_SEARCH_API]: { target_language_code: string };
  [RouteName.PROFILE_API_GET_CURRENT_PROFILE_API]: {};
  [RouteName.PROFILE_API_UPDATE_PROFILE_API]: {};
  [RouteName.PROFILE_API_GET_USER_EMAIL_API]: { user_id: string };
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
