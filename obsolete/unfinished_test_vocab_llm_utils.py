import pytest
from utils.vocab_llm_utils import quick_search_for_wordform

# pytest -m slow to run only slow tests
# pytest -m "not slow" to run only fast tests (default)


@pytest.mark.slow
def test_quick_search_for_wordform():
    # Test with Greek word "Έπειτα" (meaning "then", "afterwards")
    result, extra = quick_search_for_wordform("επειτα", "el", verbose=0)

    # should automatically convert to lowercase
    assert result["lemma"] == "έπειτα"
    assert set.intersection(set(result["translations"]), set(["then", "after"]))
    assert result["part_of_speech"] in ["adverb", "particle"]


@pytest.mark.slow
def test_quick_search_for_wordform_lemma_mapping():
    """Test lemma mapping for complex and ambiguous cases.

    Tests key categories: irregular verbs, nouns, adjectives, particles,
    contractions, and compounds.
    """
    test_cases = [
        ("Έπειτα ", "έπειτα"),  # added uppercase and space
        # Irregular verbs (present, past, participles)
        ("είναι", "είμαι"),  # present, third person -> base form
        ("ήταν", "είμαι"),  # past tense -> base form
        ("πήγα", "πηγαίνω"),  # suppletive past -> base form
        ("έφαγα", "τρώω"),  # suppletive past -> base form
        # Adjectives and their forms
        ("καλή", "καλός"),  # feminine -> base form
        ("καλύτερος", "καλός"),  # comparative -> base form
        # Irregular nouns and plurals
        ("παιδιά", "παιδί"),  # irregular plural
        ("γυναίκες", "γυναίκα"),  # irregular plural
        # Contractions and particles
        ("στον", "σε"),  # contraction of σε + τον
        # Ambiguous cases
        ("μόνο", "μόνος"),  # adverb/adjective
        # Compounds, e.g. car
    ]
    for wordform, expected_lemma in test_cases:
        result, _ = quick_search_for_wordform(wordform, "el", verbose=0)
        assert isinstance(result, dict)
        assert (
            result["lemma"].lower() == expected_lemma.lower()
        ), f"Expected lemma '{expected_lemma}' for wordform '{wordform}', got '{result['lemma']}'"


@pytest.mark.slow
def test_quick_search_for_wordform_validation_errors():
    """Test cases where the input itself is invalid (should raise ValueError)."""
    # Empty or whitespace-only inputs
    empty_inputs = [
        ("", "el"),
        (" ", "el"),
        ("\n", "el"),
        ("καλός", ""),
        (" ", " "),
    ]
    for wordform, lang_code in empty_inputs:
        with pytest.raises(ValueError, match="cannot be empty"):
            quick_search_for_wordform(wordform, lang_code, verbose=0)

    # None/null values
    none_inputs = [
        (None, "el"),
        ("καλός", None),
    ]
    for wordform, lang_code in none_inputs:
        with pytest.raises(ValueError, match="must be strings"):
            quick_search_for_wordform(wordform, lang_code, verbose=0)

    # Wrong types
    wrong_types = [
        (123, "el"),
        (["καλός"], "el"),
        ("καλός", ["el"]),
    ]
    for wordform, lang_code in wrong_types:
        with pytest.raises(ValueError, match="must be strings"):
            quick_search_for_wordform(wordform, lang_code, verbose=0)

    # Invalid language codes
    invalid_lang_codes = [
        ("καλός", "xx"),  # non-existent language code
        ("καλός", "123"),  # numeric language code
    ]
    for wordform, lang_code in invalid_lang_codes:
        with pytest.raises(LookupError):
            quick_search_for_wordform(wordform, lang_code, verbose=0)


@pytest.mark.slow
def test_quick_search_for_wordform_nonexistent():
    """Test cases for various types of inputs.

    Tests:
    1. Valid lemmas - should return full metadata with inflection_type
    2. Valid wordforms - should return full metadata with lemma and inflection_type
    3. Near-matches - should return only possible_misspellings
    4. Invalid words - should return all None
    5. Sanitization - should handle extra characters but still work
    """
    # Test valid lemmas
    result, _ = quick_search_for_wordform("καλός", "el", verbose=0)
    assert result["wordform"] == "καλός"
    assert result["lemma"] == "καλός"
    assert result["part_of_speech"] == "adjective"
    assert "good" in result["translations"]
    assert result["inflection_type"] == "masculine singular nominative"
    assert result["possible_misspellings"] is None

    # Test valid wordforms
    result, _ = quick_search_for_wordform("καλή", "el", verbose=0)
    assert result["wordform"] == "καλή"
    assert result["lemma"] == "καλός"
    assert result["part_of_speech"] == "adjective"
    assert "good" in result["translations"]
    assert result["inflection_type"] == "feminine singular nominative"
    assert result["possible_misspellings"] is None

    # Test near-matches (common typos)
    result, _ = quick_search_for_wordform("καλλός", "el", verbose=0)
    assert result["wordform"] is None
    assert result["lemma"] is None
    assert result["part_of_speech"] is None
    assert result["translations"] is None
    assert result["inflection_type"] is None
    assert "καλός" in result["possible_misspellings"]

    # Test invalid words
    invalid_cases = [
        "xyzzyx",  # completely made up
        "αβγδεζηθ",  # random Greek letters
        "hello",  # English word
        "スシ",  # Japanese word
        "café",  # French word
    ]
    for wordform in invalid_cases:
        result, _ = quick_search_for_wordform(wordform, "el", verbose=0)
        assert result["wordform"] is None
        assert result["lemma"] is None
        assert result["part_of_speech"] is None
        assert result["translations"] is None
        assert result["inflection_type"] is None
        assert result["possible_misspellings"] is None

    # Test sanitization
    result, _ = quick_search_for_wordform("καλός!", "el", verbose=0)
    assert result["wordform"] == "καλός"
    assert result["lemma"] == "καλός"
    assert result["part_of_speech"] == "adjective"
    assert "good" in result["translations"]
    assert result["inflection_type"] == "masculine singular nominative"
    assert result["possible_misspellings"] is None


@pytest.mark.slow
def test_quick_search_for_wordform_edge_cases():
    """Test edge cases including typos, whitespace, and punctuation.

    Tests:
    1. Common typos - should return only possible_misspellings
    2. Whitespace variations - should be stripped
    3. Punctuation marks - should be stripped
    4. Diacritics/accent variations
    5. Mixed case variations
    6. Unicode normalization cases
    """
    # Valid variations (should work after normalization)
    valid_variations = [
        # Punctuation -> "έπειτα"
        ("έπειτα,", "έπειτα"),
        ("«έπειτα»", "έπειτα"),
        ("έπειτα!", "έπειτα"),
        ("έπειτα;", "έπειτα"),
        ("(έπειτα)", "έπειτα"),
        # Case variations -> "καλός"
        ("ΚΑΛΟΣ", "καλός"),
        ("Καλός", "καλός"),
        ("ΚαΛόΣ", "καλός"),
        # Diacritics/accent variations -> "άνθρωπος"
        ("ανθρωπος", "άνθρωπος"),  # missing accent
        ("άνθρωπός", "άνθρωπος"),  # extra accent
        # # Unicode normalization -> "μιλώ"
        # ("μιλω", "μιλώ"),  # without tonos
        # ("μιλώ", "μιλώ"),  # with tonos
        # ("ΜΙΛΏ", "μιλώ"),  # uppercase with tonos
    ]

    for wordform, expected_lemma in valid_variations:
        result, _ = quick_search_for_wordform(wordform, "el", verbose=0)
        assert isinstance(result, dict)
        assert (
            result["lemma"] == expected_lemma
        ), f"Expected lemma '{expected_lemma}' for wordform '{wordform}', got '{result['lemma']}'"

    # Test near-matches (common typos)
    typo_cases = [
        # Common typos
        ("καλλός", ["καλός"]),  # double lambda
        ("καί", ["και"]),  # wrong accent
        ("έπιτα", ["έπειτα"]),  # missing epsilon
        ("άνθροπος", ["άνθρωπος"]),  # missing omega
        ("μηλώ", ["μιλώ"]),  # eta instead of iota
        ("μιλο", ["μιλώ"]),  # missing omega
        # Nonsense variations
        ("καλόςς", ["καλός"]),  # extra sigma
        ("καλσς", ["καλός"]),  # omicron -> sigma
        ("κκαι", ["και"]),  # double kappa
        # Mixed alphabet
        ("καλoς", ["καλός"]),  # with Latin 'o'
        ("kaλος", ["καλός"]),  # mixed Greek/Latin
        ("καλos", ["καλός"]),  # mixed Greek/Latin
    ]

    for wordform, expected_corrections in typo_cases:
        result, _ = quick_search_for_wordform(wordform, "el", verbose=0)
        assert result["wordform"] is None
        assert result["lemma"] is None
        assert result["part_of_speech"] is None
        assert result["translations"] is None
        assert result["inflection_type"] is None
        assert any(
            correction in result["possible_misspellings"]
            for correction in expected_corrections
        ), f"Expected one of {expected_corrections} in possible_misspellings for '{wordform}', got {result['possible_misspellings']}"

    # Test definitely invalid words
    invalid_cases = [
        "xyz",  # completely made up
        "αβγδεζηθ",  # random Greek letters
        "hello",  # English word
        "スシ",  # Japanese word
        "café",  # French word
        "καλός™",  # trademark symbol
        "καλός®",  # registered trademark
        "καλός2",  # number
        "2καλός",  # number
        "καλ0ς",  # zero instead of omicron
    ]

    for wordform in invalid_cases:
        result, _ = quick_search_for_wordform(wordform, "el", verbose=0)
        assert result["wordform"] is None
        assert result["lemma"] is None
        assert result["part_of_speech"] is None
        assert result["translations"] is None
        assert result["inflection_type"] is None
        assert result["possible_misspellings"] is None
