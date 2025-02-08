from typing import Optional
import random

from audio_utils import ensure_audio_data
from db_models import Sentence, Lemma, SentenceLemma
from lang_utils import get_language_name
from vocab_llm_utils import anthropic_client, generate_gpt_from_template


def generate_sentence(
    target_language_code: str,
    sentence: str,
    translation: str,
    lemma_words: Optional[list] = None,
    should_play: bool = False,
) -> tuple[None, dict]:
    """Generate audio and metadata for a sentence.

    Args:
        target_language_code: ISO language code
        sentence: The sentence in target language
        translation: English translation
        lemma_words: List of lemmas/vocabulary words used in the sentence
        should_play: Whether to play the audio after generating

    Returns:
        Tuple of (None, metadata_dict)
    """
    # Remove trailing period if present
    if sentence.endswith("."):
        sentence = sentence[:-1]

    # Generate audio data
    audio_data = ensure_audio_data(
        text=sentence,
        should_add_delays=True,
        should_play=should_play,
        verbose=1,
    )

    # Create or update sentence in database
    db_sentence, created = Sentence.get_or_create(
        language_code=target_language_code,
        sentence=sentence,
        defaults={
            "translation": translation,
            "audio_data": audio_data,
        },
    )

    # Update if it already existed and fields are different
    if not created:
        if (
            db_sentence.translation != translation
            or db_sentence.audio_data != audio_data
        ):
            db_sentence.translation = translation
            db_sentence.audio_data = audio_data
            db_sentence.save()

    # Add lemma relationships if provided
    if lemma_words:
        for lemma_word in lemma_words:
            # Get or create the lemma
            lemma, _ = Lemma.get_or_create(
                lemma=lemma_word,
                language_code=target_language_code,
                defaults={
                    "part_of_speech": "unknown",
                    "translations": [],
                },
            )
            # Create the junction table entry
            SentenceLemma.get_or_create(
                sentence=db_sentence,
                lemma=lemma,
            )

    # Return metadata in same format as before for compatibility
    metadata = {
        "id": db_sentence.id,
        "sentence": sentence,
        "translation": translation,
        "lemma_words": db_sentence.lemma_words,
        "target_language_code": target_language_code,
        "slug": db_sentence.slug,
    }

    return None, metadata


def get_all_sentences(target_language_code: str) -> list[dict]:
    """Get all available sentences with their metadata.

    Args:
        target_language_code: ISO language code

    Returns:
        List[Dict]: List of sentence metadata dictionaries
    """
    sentences = []
    query = Sentence.select().where(Sentence.language_code == target_language_code)

    for db_sentence in query:
        sentences.append(
            {
                "id": db_sentence.id,
                "sentence": db_sentence.sentence,
                "translation": db_sentence.translation,
                "lemma_words": db_sentence.lemma_words,
                "target_language_code": db_sentence.language_code,
                "slug": db_sentence.slug,
            }
        )

    print(f"Successfully loaded {len(sentences)} sentences")
    return sentences


def get_random_sentence(
    target_language_code: str,
    required_lemmas: Optional[list[str]] = None,
    generate_missing_audio: bool = True,
) -> Optional[dict]:
    """Get a random sentence with its metadata.

    Args:
        target_language_code: ISO language code
        required_lemmas: Optional list of lemmas that must be used in the sentence.
                        Will match sentences containing at least one of these lemmas.
        generate_missing_audio: Whether to generate audio if missing. Defaults to True.

    Returns:
        Optional[Dict]: Random sentence metadata or None if no matching sentences found
    """
    query = Sentence.select().where(Sentence.language_code == target_language_code)

    if required_lemmas:
        # Filter sentences to those containing at least one of the required lemmas
        matching_sentences = []
        for sentence in query:
            if any(lemma in sentence.lemma_words for lemma in required_lemmas):
                matching_sentences.append(sentence)

        print(
            f"Found {len(matching_sentences)} sentences matching at least one of lemmas: {required_lemmas}"
        )
        if not matching_sentences:
            return None
        chosen = random.choice(matching_sentences)
    else:
        # Convert to list for random.choice
        sentences = list(query)
        if not sentences:
            print(f"No sentences found for language: {target_language_code}")
            return None
        chosen = random.choice(sentences)

    # Generate audio if missing and requested
    if generate_missing_audio and not chosen.audio_data:
        chosen.audio_data = ensure_audio_data(
            text=chosen.sentence,
            should_add_delays=True,
            should_play=False,
            verbose=1,
        )
        chosen.save()

    # Format response the same way as before
    metadata = {
        "id": chosen.id,
        "sentence": chosen.sentence,
        "translation": chosen.translation,
        "lemma_words": chosen.lemma_words,
        "target_language_code": target_language_code,
        "slug": chosen.slug,
    }

    print(f"Chosen sentence: {metadata['sentence']}")
    return metadata


def generate_practice_sentences(
    target_language_code: str, lemmas: list[str], num_sentences: int = 5
) -> None:
    """Generate practice sentences that use the given lemmas.

    Args:
        target_language_code: The target language code.
        lemmas: List of lemmas to include in generated sentences.
        num_sentences: Number of sentences to generate. Defaults to 5.
    """
    for lemma in lemmas:
        # Generate sentence and translation
        response = generate_gpt_from_template(
            client=anthropic_client,
            prompt_template_var="generate_sentence_flashcards",
            context_d={
                "target_language_name": get_language_name(target_language_code),
                "already_words": [lemma],
            },
            response_json=True,
        )

        if not response or not isinstance(response, dict):
            continue

        # Process each sentence in the response
        for sentence_data in response.get("sentences", []):
            if not sentence_data.get("sentence") or not sentence_data.get(
                "translation"
            ):
                continue

            # Save the sentence
            generate_sentence(
                target_language_code=target_language_code,
                sentence=sentence_data["sentence"],
                translation=sentence_data["translation"],
                lemma_words=[lemma],
            )
