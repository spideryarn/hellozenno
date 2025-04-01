import pytest
import unicodedata
from utils.word_utils import ensure_nfc

# This test file provides a simplified way to test the Unicode normalization functionality
# without requiring the full test environment setup. The comprehensive tests are in
# tests/backend/test_word_utils.py and tests/backend/test_vocab_llm_utils.py


def test_ensure_nfc_with_various_inputs():
    """Test ensure_nfc with various input types and edge cases."""
    # Test with already NFC text
    nfc_text = "τροφή"
    assert ensure_nfc(nfc_text) == nfc_text
    assert len(ensure_nfc(nfc_text)) == 5

    # Test with NFD text
    nfd_text = unicodedata.normalize("NFD", "τροφή")
    assert ensure_nfc(nfd_text) == "τροφή"
    assert len(nfd_text) == 6  # NFD form has 6 characters
    assert len(ensure_nfc(nfd_text)) == 5  # NFC form has 5 characters

    # Test with mixed text containing both forms
    mixed_text = f"This is {nfc_text} and {nfd_text}"
    assert ensure_nfc(mixed_text) == f"This is {nfc_text} and {nfc_text}"

    # Test with non-Greek text
    non_greek = "food"
    assert ensure_nfc(non_greek) == non_greek

    # Test with empty string
    assert ensure_nfc("") == ""

    # Test with string containing only whitespace
    assert ensure_nfc("   ") == "   "


def test_unicode_normalization_simulation():
    """Simulate database lookups with different Unicode normalization forms."""
    # Create NFC and NFD versions of the same word
    nfc_word = "τροφή"
    nfd_word = unicodedata.normalize("NFD", "τροφή")

    # Verify they are different in their raw form
    assert nfc_word != nfd_word
    assert len(nfc_word) == 5
    assert len(nfd_word) == 6

    # Verify they are the same after normalization
    assert ensure_nfc(nfc_word) == ensure_nfc(nfd_word)

    # Simulate a database lookup with normalization
    def mock_db_lookup(word):
        # This simulates what our database lookup would do with normalization
        normalized_word = ensure_nfc(word)
        # Pretend we have a database with the word "τροφή" in NFC form
        if normalized_word == "τροφή":
            return {"wordform": "τροφή", "lemma": "τροφή"}
        return None

    # Both forms should find the same word in our mock database
    assert mock_db_lookup(nfc_word) is not None
    assert mock_db_lookup(nfd_word) is not None
    assert mock_db_lookup(nfc_word) == mock_db_lookup(nfd_word)


def test_multiple_diacritics():
    """Test normalization with words that have multiple diacritics."""
    # Greek word with multiple diacritics (e.g., ἄνθρωπος with breathing and accent)
    complex_word = "ἄνθρωπος"
    nfd_complex = unicodedata.normalize("NFD", complex_word)

    # Verify normalization works correctly
    assert ensure_nfc(nfd_complex) == complex_word
    assert len(nfd_complex) > len(complex_word)  # NFD form has more characters

    # Test with a mix of modern and ancient Greek
    mixed_greek = f"Ο {complex_word} και η τροφή"
    nfd_mixed = unicodedata.normalize("NFD", mixed_greek)
    assert ensure_nfc(nfd_mixed) == mixed_greek


if __name__ == "__main__":
    # This allows running the tests directly with python test_normalization.py
    # For proper pytest integration, run with: pytest test_normalization.py -v
    pytest.main(["-v", __file__])
