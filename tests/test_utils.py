"""Test utilities and mock functions."""


def mock_quick_search_for_wordform(
    wordform: str, target_language_code: str, verbose: int = 1
):
    """Mock function to simulate quick_search_for_wordform."""
    if wordform in ["nonexistent", "καλή"]:  # Treat καλή as nonexistent after deletion
        return {
            "wordform": None,
            "lemma": None,
            "part_of_speech": None,
            "translations": None,
            "inflection_type": None,
            "possible_misspellings": ["test"],
        }, {}
    else:
        return {
            "wordform": wordform,
            "lemma": wordform,  # For simplicity, use wordform as lemma
            "part_of_speech": "noun",
            "translations": ["test translation"],
            "inflection_type": "nominative",
            "possible_misspellings": None,
        }, {}
