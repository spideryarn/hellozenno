def mock_quick_search_for_wordform(
    wordform: str, target_language_code: str, verbose: int = 1
):
    """Mock function to simulate quick_search_for_wordform."""
    if wordform in ["nonexistent", "καλή"]:  # Treat καλή as nonexistent after deletion
        return {
            "target_language_results": {
                "matches": [],
                "possible_misspellings": ["test"]
            },
            "english_results": {
                "matches": [],
                "possible_misspellings": None
            }
        }, {}
    else:
        return {
            "target_language_results": {
                "matches": [
                    {
                        "target_language_wordform": wordform,
                        "target_language_lemma": wordform,  # For simplicity, use wordform as lemma
                        "part_of_speech": "noun",
                        "english": ["test translation"],
                        "inflection_type": "nominative"
                    }
                ],
                "possible_misspellings": None
            },
            "english_results": {
                "matches": [],
                "possible_misspellings": None
            }
        }, {}
