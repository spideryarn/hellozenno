from typing import Optional
import random

from utils.audio_utils import ensure_audio_data
from db_models import Sentence, Lemma, SentenceLemma
from utils.lang_utils import get_language_name
from utils.vocab_llm_utils import anthropic_client, generate_gpt_from_template


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
        # Filter sentences using database JOIN to find those with matching lemmas
        query = (
            query.join(SentenceLemma)
            .join(Lemma)
            .where(Lemma.lemma.in_(required_lemmas))
            .distinct()
        )  # Avoid duplicates if sentence has multiple matching lemmas

    # Get total count for random selection
    count = query.count()
    if count == 0:
        msg = "No sentences found for language: " + target_language_code
        if required_lemmas:
            msg += " with lemmas: " + str(required_lemmas)
        print(msg)
        return None

    # Get random offset and select one sentence
    offset = random.randint(0, count - 1)
    results = list(query.offset(offset).limit(1))
    if not results:
        return None
    chosen = results[0]

    # Generate audio if missing and requested
    if generate_missing_audio and not chosen.audio_data:
        chosen.audio_data = ensure_audio_data(
            text=chosen.sentence,
            should_add_delays=True,
            should_play=False,
            verbose=1,
        )
        chosen.save()

    # Return metadata in same format as before for compatibility
    return {
        "id": chosen.id,
        "sentence": chosen.sentence,
        "translation": chosen.translation,
        "lemma_words": chosen.lemma_words,
        "target_language_code": target_language_code,
        "slug": chosen.slug,
    }


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
