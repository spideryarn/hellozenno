import pytest
from utils.lang_utils import get_language_name, get_all_languages
from pycountry import languages


def test_get_language_name():
    # Test with language code
    assert get_language_name("en") == "English"
    assert get_language_name("el") == "Greek (modern)"

    # Test with language object
    lang_obj = languages.get(alpha_2="es")
    assert get_language_name(lang_obj) == "Spanish"

    # Test with invalid code
    with pytest.raises(LookupError):
        get_language_name("xx")


def test_get_all_languages():
    languages_list = get_all_languages()

    # Check that we get a non-empty list
    assert isinstance(languages_list, list)
    assert len(languages_list) > 0

    # Check structure of returned items
    first_lang = languages_list[0]
    assert isinstance(first_lang, dict)
    assert "code" in first_lang
    assert "name" in first_lang
    assert len(first_lang["code"]) == 2  # Should be 2-letter code

    # Check that list is sorted by name
    names = [lang["name"] for lang in languages_list]
    assert names == sorted(names)

    # check that Greek is in the list
    assert any(lang["name"] == "Greek (modern)" for lang in languages_list)
