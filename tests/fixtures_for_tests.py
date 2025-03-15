"""Test fixtures and constants."""

from typing import Dict, Any
from pathlib import Path
from db_models import (
    Lemma,
    Wordform,
    Sentence,
    Phrase,
    LemmaExampleSentence,
    PhraseExampleSentence,
    RelatedPhrase,
    Sourcedir,
    Sourcefile,
    SourcefileWordform,
    SourcefilePhrase,
    SentenceLemma,
)

# Basic test constants
TEST_LANGUAGE_CODE = "el"
TEST_LANGUAGE_NAME = "Greek"
TEST_SOURCE_DIR = "test_source"
TEST_SOURCE_FILE = "test.txt"
TEST_SOURCE_FILE_AUDIO = "test.mp3"
TEST_IMAGE_PATH_JPG = Path("tests/fixtures/small_test_fixture_image.jpg")
TEST_IMAGE_PATH_PNG = Path("tests/fixtures/small png image fixture.png")

# Sample data for lemma tests
SAMPLE_LEMMA_DATA = {
    "lemma": "καλός",
    "translations": ["good", "beautiful"],
    "part_of_speech": "adjective",
    "etymology": "From Ancient Greek καλός (kalós)",
    "commonality": 0.8,
    "guessability": 0.7,
    "register": "neutral",
    "example_usage": [
        {
            "phrase": "Είναι καλός άνθρωπος.",
            "translation": "He is a good person.",
        }
    ],
    "mnemonics": ["Think of 'call us' - when someone is good, you want to call them."],
    "related_words_phrases_idioms": [
        {
            "lemma": "καλή όρεξη",
            "translation": "bon appetit",
        }
    ],
    "synonyms": [
        {
            "lemma": "ωραίος",
            "translation": "beautiful",
        }
    ],
    "antonyms": [
        {
            "lemma": "κακός",
            "translation": "bad",
        }
    ],
    "example_wordforms": ["καλός", "καλή", "καλό", "καλοί", "καλές", "καλά"],
    "cultural_context": "Fundamental to Greek politeness",
    "easily_confused_with": [
        {
            "lemma": "κακός",
            "explanation": "Means 'bad', opposite meaning",
            "example_usage_this_target": "Είναι καλός άνθρωπος.",
            "example_usage_this_source": "He is a good person.",
            "example_usage_other_target": "Είναι κακός άνθρωπος.",
            "example_usage_other_source": "He is a bad person.",
            "mnemonic": "καλός sounds like 'call us' (good), κακός sounds like 'cactus' (bad)",
            "notes": "Very common confusion for beginners",
        }
    ],
    "is_complete": True,
}

# Sample data for phrase tests
SAMPLE_PHRASE_DATA = {
    "canonical_form": "κάθομαι και σκέφτομαι",
    "raw_forms": ["κάθομαι και σκέφτομαι"],
    "translations": ["I sit and think", "I'm sitting and thinking"],
    "literal_translation": "I sit and I think",
    "part_of_speech": "verbal phrase",
    "register": "neutral",
    "commonality": 0.8,
    "guessability": 0.7,
    "etymology": "Combination of κάθομαι (to sit) and σκέφτομαι (to think)",
    "cultural_context": "Common expression for deep contemplation",
    "mnemonics": ["Imagine someone sitting in a thinking pose"],
    "component_words": [
        {"lemma": "κάθομαι", "translation": "to sit", "notes": "verb"},
        {"lemma": "και", "translation": "and", "notes": "conjunction"},
        {"lemma": "σκέφτομαι", "translation": "to think", "notes": "verb"},
    ],
    "usage_notes": "Used to describe thoughtful contemplation",
    "difficulty_level": "intermediate",
}


# Test data fixtures
def create_test_lemma(db) -> Lemma:
    """Create a test lemma."""
    return Lemma.create(
        lemma="test",
        language_code=TEST_LANGUAGE_CODE,
        part_of_speech="noun",
        translations=["test"],
        register="neutral",
        commonality=0.5,
        guessability=0.5,
    )


def create_test_wordform(db, lemma: Lemma) -> Wordform:
    """Create a test wordform."""
    return Wordform.create(
        wordform="test",
        lemma_entry=lemma,
        language_code=TEST_LANGUAGE_CODE,
        part_of_speech="noun",
        translations=["test translation"],
        inflection_type="nominative",
        is_lemma=True,
    )


def create_test_phrase(db) -> Phrase:
    """Create a test phrase."""
    return Phrase.create(language_code=TEST_LANGUAGE_CODE, **SAMPLE_PHRASE_DATA)


def create_test_sourcedir(db) -> Dict[str, Sourcedir]:
    """Create test sourcedirs."""
    return {
        "empty": Sourcedir.create(
            path="empty_dir",
            language_code=TEST_LANGUAGE_CODE,
        ),
        "with_files": Sourcedir.create(
            path=TEST_SOURCE_DIR,
            language_code=TEST_LANGUAGE_CODE,
        ),
        "other_lang": Sourcedir.create(
            path="test_dir_fr",
            language_code="fr",
        ),
    }


def create_test_sourcefile(db, sourcedir: Sourcedir) -> Sourcefile:
    """Create a test sourcefile."""
    return Sourcefile.create(
        sourcedir=sourcedir,
        filename=TEST_SOURCE_FILE,
        text_target="test text",
        text_english="test translation",
        description="Test file description",
        metadata={
            "words": [
                {
                    "wordform": "test",
                    "lemma": "test",
                    "part_of_speech": "noun",
                    "translations": ["test translation"],
                }
            ],
            "phrases": [
                {
                    "canonical_form": "test phrase",
                    "raw_forms": ["test phrase"],
                    "translations": ["test translation"],
                    "literal_translation": "test literal translation",
                    "part_of_speech": "verbal phrase",
                    "centrality": 0.8,
                    "ordering": 1,
                }
            ],
        },
        image_data=b"test content",
        audio_data=b"test audio content",
        sourcefile_type="image",
    )


def create_test_sourcefile_links(
    db, sourcefile: Sourcefile, wordform: Wordform, phrase: Phrase
) -> Dict[str, Any]:
    """Create test sourcefile links."""
    return {
        "wordform": SourcefileWordform.create(
            sourcefile=sourcefile,
            wordform=wordform,
            centrality=0.8,
            ordering=1,
        ),
        "phrase": SourcefilePhrase.create(
            sourcefile=sourcefile,
            phrase=phrase,
            centrality=0.8,
            ordering=1,
        ),
    }


def create_test_sentence(db) -> Sentence:
    """Create a test sentence with audio data."""
    sentence = Sentence.create(
        language_code=TEST_LANGUAGE_CODE,
        sentence="Το σπίτι είναι μεγάλο",
        translation="The house is big",
        audio_data=b"test audio data",  # Dummy audio data for testing
    )

    # Create lemmas and relationships
    for lemma_word in ["σπίτι", "μεγάλος"]:
        lemma = Lemma.create(
            lemma=lemma_word,
            language_code=TEST_LANGUAGE_CODE,
            part_of_speech="unknown",
            translations=[],
        )
        SentenceLemma.create(
            sentence=sentence,
            lemma=lemma,
        )

    return sentence


def create_complete_test_data(db) -> Dict[str, Any]:
    """Create a complete set of test data."""
    lemma = create_test_lemma(db)
    wordform = create_test_wordform(db, lemma)
    phrase = create_test_phrase(db)
    sourcedirs = create_test_sourcedir(db)
    sourcefile = create_test_sourcefile(db, sourcedirs["with_files"])
    links = create_test_sourcefile_links(db, sourcefile, wordform, phrase)
    sentence = create_test_sentence(db)  # Add sentence creation

    return {
        "lemma": lemma,
        "wordform": wordform,
        "phrase": phrase,
        "sourcedirs": sourcedirs,
        "sourcefile": sourcefile,
        "sentence": sentence,  # Add sentence to returned data
        **links,
    }
