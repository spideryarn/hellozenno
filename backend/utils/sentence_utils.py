from typing import Optional, Any
import random

from db_models import (
    Sentence,
    Lemma,
    SentenceLemma,
    Wordform,
    Profile,
    UserLemma,
    SentenceAudio,
)
from utils.lang_utils import get_language_name
from utils.vocab_llm_utils import (
    anthropic_client,
    generate_gpt_from_template,
    extract_tokens,
    create_interactive_word_links,
)
from utils.prompt_utils import get_prompt_template_path
from utils.word_utils import normalize_text
from peewee import DoesNotExist


def generate_sentence(
    target_language_code: str,
    sentence: str,
    translation: str,
    lemma_words: Optional[list] = None,
    language_level: Optional[str] = None,
    *,
    provenance: Optional[str] = None,
    generation_metadata: Optional[dict[str, Any]] = None,
) -> tuple[Sentence, dict]:
    """Create or update a sentence record without generating audio."""

    sentence_text = sentence[:-1] if sentence.endswith(".") else sentence

    db_sentence, created = Sentence.get_or_create(
        target_language_code=target_language_code,
        sentence=sentence_text,
        defaults={
            "translation": translation,
            "language_level": language_level,
            "provenance": provenance or "manual",
            "generation_metadata": generation_metadata,
        },
    )

    if not created:
        updated = False
        if db_sentence.translation != translation:
            db_sentence.translation = translation
            updated = True
        if db_sentence.language_level != language_level:
            db_sentence.language_level = language_level
            updated = True
        if provenance and db_sentence.provenance != provenance:
            db_sentence.provenance = provenance
            updated = True
        if generation_metadata is not None:
            db_sentence.generation_metadata = generation_metadata
            updated = True
        if updated:
            db_sentence.save()

    # Add lemma relationships if provided
    if lemma_words:
        for lemma_word in lemma_words:
            # Get or create the lemma
            lemma, _ = Lemma.get_or_create(
                lemma=lemma_word,
                target_language_code=target_language_code,
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
        "sentence": sentence_text,
        "translation": translation,
        "lemma_words": db_sentence.lemma_words,
        "target_language_code": target_language_code,
        "slug": db_sentence.slug,
    }

    return db_sentence, metadata


def get_all_sentences(target_language_code: str) -> list[dict]:
    """Get all available sentences with their metadata.

    Args:
        target_language_code: ISO language code

    Returns:
        List[Dict]: List of sentence metadata dictionaries
    """
    # Use the optimized class method to get all sentences with eager-loaded lemmas
    sentences = Sentence.get_all_sentences_for(target_language_code, sort_by="date")

    print(f"Successfully loaded {len(sentences)} sentences")
    return sentences


def get_random_sentence(
    target_language_code: str,
    required_lemmas: Optional[list[str]] = None,
    profile: Optional[Profile] = None,
) -> Optional[dict]:
    """Get a random sentence with its metadata.

    Args:
        target_language_code: ISO language code
        required_lemmas: Optional list of lemmas that must be used in the sentence.
                        Will match sentences containing at least one of these lemmas.
        profile: Optional Profile model to filter out ignored lemmas.

    Returns:
        Optional[Dict]: Random sentence metadata or None if no matching sentences found
    """
    query = Sentence.select().where(
        Sentence.target_language_code == target_language_code
    )

    if required_lemmas:
        # Filter sentences using database JOIN to find those with matching lemmas
        base_query = (
            query.join(SentenceLemma)
            .join(Lemma)
            .where(Lemma.lemma.in_(required_lemmas))
        )

        # If profile is provided, exclude ignored lemmas
        if profile:
            # Modified query that excludes ignored lemmas
            query = base_query.where(
                ~(
                    (
                        SentenceLemma.lemma
                        << UserLemma.select(UserLemma.lemma).where(
                            (UserLemma.user_id == profile.user_id)
                            & (UserLemma.ignored_dt.is_null(False))
                        )
                    )
                )
            ).distinct()
        else:
            # Use the base query without ignoring lemmas
            query = base_query.distinct()

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

    # Return metadata in same format as before for compatibility
    return {
        "id": chosen.id,
        "sentence": chosen.sentence,
        "translation": chosen.translation,
        "lemma_words": chosen.lemma_words,
        "target_language_code": target_language_code,
        "slug": chosen.slug,
        "language_level": chosen.language_level,
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
            prompt_template=get_prompt_template_path("generate_sentence_flashcards"),
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
                language_level=sentence_data.get(
                    "language_level"
                ),  # Store language_level from LLM response
            )


def get_detailed_sentence_data(target_language_code: str, slug: str) -> dict:
    """Get detailed data for a specific sentence including enhanced text and metadata.

    Args:
        target_language_code: The language code
        slug: The sentence slug

    Returns:
        A dictionary containing the sentence data, metadata, and enhanced text

    Raises:
        DoesNotExist: If the sentence is not found
    """
    sentence = Sentence.get(
        (Sentence.target_language_code == target_language_code)
        & (Sentence.slug == slug)
    )

    # Extract tokens from the sentence text
    tokens_in_text = extract_tokens(str(sentence.sentence))

    # Query database for all wordforms in this language
    wordforms = list(
        Wordform.select().where((Wordform.target_language_code == target_language_code))
    )

    # Filter wordforms in Python using normalize_text
    normalized_tokens = {normalize_text(t) for t in tokens_in_text}
    wordforms = [
        wf for wf in wordforms if normalize_text(wf.wordform) in normalized_tokens
    ]

    # Convert to dictionary format
    wordforms_d = []
    for wordform in wordforms:
        wordform_d = wordform.to_dict()
        wordform_d["centrality"] = 0.3  # Default centrality
        wordform_d["ordering"] = len(wordforms_d) + 1
        wordforms_d.append(wordform_d)

    # Create enhanced text with interactive word links
    enhanced_sentence_text, found_wordforms = create_interactive_word_links(
        text=str(sentence.sentence),
        wordforms=wordforms_d,
        target_language_code=target_language_code,
    )

    # Create serializable versions of the data
    metadata = {
        "created_at": (
            sentence.created_at.isoformat() if sentence.created_at else None
        ),
        "updated_at": (
            sentence.updated_at.isoformat() if sentence.updated_at else None
        ),
    }

    # Get lemmas both from the database relationships and from the matched wordforms
    db_lemma_words = sentence.lemma_words if hasattr(sentence, "lemma_words") else []

    # Extract lemmas from the matched wordforms
    matched_lemmas = []
    for wf in wordforms_d:
        if (
            wf.get("lemma")
            and wf["lemma"] not in matched_lemmas
            and wf["lemma"] not in db_lemma_words
        ):
            matched_lemmas.append(wf["lemma"])

    # Combine both sources of lemmas, removing duplicates
    all_lemmas = list(set(db_lemma_words + matched_lemmas))

    sentence_data = {
        "id": sentence.id,
        "sentence": str(sentence.sentence),
        "translation": str(sentence.translation) if sentence.translation else None,
        "slug": sentence.slug,
        "target_language_code": sentence.target_language_code,
        "has_audio": (
            SentenceAudio.select()
            .where(SentenceAudio.sentence == sentence)
            .exists()
        ),
        "language_level": sentence.language_level,
        "lemma_words": all_lemmas if all_lemmas else None,
    }

    return {
        "sentence": sentence_data,
        "metadata": metadata,
        "enhanced_sentence_text": enhanced_sentence_text,
    }
