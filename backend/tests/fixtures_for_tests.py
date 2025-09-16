"""Test fixtures and constants."""

from typing import Dict, Any, Union
from pathlib import Path
from db_models import (
    Lemma,
    Wordform,
    Sentence,
    SentenceAudio,
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
TEST_TARGET_LANGUAGE_CODE = "el"
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
def create_test_lemma(db, **kwargs) -> Lemma:
    """Create a test lemma with customizable properties."""
    lemma_data = {
        "lemma": "test",
        "target_language_code": TEST_TARGET_LANGUAGE_CODE,
        "part_of_speech": "noun",
        "translations": ["test"],
        "register": "neutral",
        "commonality": 0.5,
        "guessability": 0.5,
    }
    lemma_data.update(kwargs)
    return Lemma.create(**lemma_data)


def create_test_wordform(db, lemma: Lemma = None, **kwargs) -> Wordform:
    """Create a test wordform with customizable properties."""
    # Create a lemma if one wasn't provided
    if not lemma:
        lemma = create_test_lemma(db)

    wordform_data = {
        "wordform": "test",
        "lemma_entry": lemma,
        "target_language_code": TEST_TARGET_LANGUAGE_CODE,
        "part_of_speech": "noun",
        "translations": ["test translation"],
        "inflection_type": "nominative",
        "is_lemma": True,
    }
    wordform_data.update(kwargs)
    return Wordform.create(**wordform_data)


def create_test_phrase(db, **kwargs) -> Phrase:
    """Create a test phrase with customizable properties."""
    phrase_data = {
        "target_language_code": TEST_TARGET_LANGUAGE_CODE,
        **SAMPLE_PHRASE_DATA,
    }
    phrase_data.update(kwargs)
    return Phrase.create(**phrase_data)


def create_test_sourcedir(
    db, return_dict=True, path=None, target_language_code=None, **kwargs
) -> Union[Dict[str, Sourcedir], Sourcedir]:
    """Create test sourcedirs.

    Args:
        db: Database connection
        return_dict: If True, returns dictionary with multiple sourcedirs, otherwise returns a single sourcedir
        path: Optional path to use for a single sourcedir
        target_language_code: Optional language code for a single sourcedir
        **kwargs: Additional arguments to pass to Sourcedir.create

    Returns:
        Dict[str, Sourcedir] or Sourcedir: Dictionary of sourcedirs or a single sourcedir
    """
    if return_dict:
        return {
            "empty": Sourcedir.create(
                path="empty_dir",
                target_language_code=TEST_TARGET_LANGUAGE_CODE,
                **kwargs
            ),
            "with_files": Sourcedir.create(
                path=TEST_SOURCE_DIR,
                target_language_code=TEST_TARGET_LANGUAGE_CODE,
                **kwargs
            ),
            "other_lang": Sourcedir.create(
                path="test_dir_fr", target_language_code="fr", **kwargs
            ),
        }
    else:
        sourcedir_data = {
            "path": path or TEST_SOURCE_DIR,
            "target_language_code": target_language_code or TEST_TARGET_LANGUAGE_CODE,
        }
        sourcedir_data.update(kwargs)
        return Sourcedir.create(**sourcedir_data)


def create_test_sourcefile(db, sourcedir: Sourcedir = None, **kwargs) -> Sourcefile:
    """Create a test sourcefile with customizable properties."""
    # Create a sourcedir if one wasn't provided
    if not sourcedir:
        sourcedir = create_test_sourcedir(db, return_dict=False)

    sourcefile_data = {
        "sourcedir": sourcedir,
        "filename": TEST_SOURCE_FILE,
        "text_target": "test text",
        "text_english": "test translation",
        "description": "Test file description",
        "metadata": {
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
        "image_data": b"test content",
        "audio_data": b"test audio content",
        "sourcefile_type": "image",
    }
    sourcefile_data.update(kwargs)
    return Sourcefile.create(**sourcefile_data)


def create_test_sourcefile_links(
    db,
    sourcefile: Sourcefile = None,
    wordform: Wordform = None,
    phrase: Phrase = None,
    **kwargs
) -> Dict[str, Any]:
    """Create test sourcefile links with customizable properties."""
    # Create entities if they weren't provided
    if not sourcefile:
        sourcefile = create_test_sourcefile(db)
    if not wordform:
        wordform = create_test_wordform(db)
    if not phrase:
        phrase = create_test_phrase(db)

    wordform_link_data = {
        "sourcefile": sourcefile,
        "wordform": wordform,
        "centrality": 0.8,
        "ordering": 1,
    }
    phrase_link_data = {
        "sourcefile": sourcefile,
        "phrase": phrase,
        "centrality": 0.8,
        "ordering": 1,
    }

    # Apply any overrides from kwargs
    if "wordform_kwargs" in kwargs:
        wordform_link_data.update(kwargs.pop("wordform_kwargs"))
    if "phrase_kwargs" in kwargs:
        phrase_link_data.update(kwargs.pop("phrase_kwargs"))

    # Create the links
    return {
        "wordform": SourcefileWordform.create(**wordform_link_data),
        "phrase": SourcefilePhrase.create(**phrase_link_data),
    }


def create_test_sentence(db, lemma_words=None, **kwargs) -> Sentence:
    """Create a test sentence with audio data and customizable properties."""
    sentence_data = {
        "target_language_code": TEST_TARGET_LANGUAGE_CODE,
        "sentence": "Το σπίτι είναι μεγάλο",
        "translation": "The house is big",
    }
    sentence_data.update(kwargs)
    sentence = Sentence.create(**sentence_data)

    # Create lemmas and relationships
    lemma_words = lemma_words or ["σπίτι", "μεγάλος"]
    for lemma_word in lemma_words:
        lemma = Lemma.create(
            lemma=lemma_word,
            target_language_code=TEST_TARGET_LANGUAGE_CODE,
            part_of_speech="unknown",
            translations=[],
        )
        SentenceLemma.create(
            sentence=sentence,
            lemma=lemma,
        )

    SentenceAudio.create(
        sentence=sentence,
        provider="elevenlabs",
        audio_data=b"test audio data",
        metadata={
            "provider": "elevenlabs",
            "voice_name": "TestVoice",
            "model": "test-model",
            "settings": {},
        },
        created_by=None,
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
