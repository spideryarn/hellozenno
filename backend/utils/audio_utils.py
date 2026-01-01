from typing import Optional, BinaryIO, Any
from pathlib import Path
import os
import tempfile
import random
from peewee import fn
from loguru import logger
from utils.env_config import ELEVENLABS_API_KEY, OPENAI_API_KEY
from config import (
    MAX_AUDIO_SIZE_FOR_STORAGE,
    SUPPORTED_LANGUAGES,
    ELEVENLABS_VOICE_POOL,
    LEMMA_AUDIO_SAMPLES,
    SENTENCE_AUDIO_SAMPLES,
)
from gjdutils.audios import play_mp3
from gjdutils.outloud_text_to_speech import outloud_elevenlabs
from openai import OpenAI

# Exceptions for auth gating
from .exceptions import AuthenticationRequiredForGenerationError

from db_models import Lemma, Sentence, LemmaAudio, SentenceAudio
from utils.db_connection import database

# Import the exception and g for global context
from flask import g

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY.get_secret_value())


def validate_audio_file(file_path: Path) -> tuple[bool, Optional[str]]:
    """
    Validate an audio file for processing.
    Returns (is_valid, error_message).
    """
    if not file_path.exists():
        return False, "File does not exist"

    if file_path.suffix.lower() != ".mp3":
        return False, "Only MP3 files are supported"

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return False, "File is empty"

    if file_size > MAX_AUDIO_SIZE_FOR_STORAGE:
        return (
            False,
            f"File too large (max {MAX_AUDIO_SIZE_FOR_STORAGE/(1024*1024):.1f}MB)",
        )

    return True, None


def transcribe_audio(
    file_obj: BinaryIO | Path, target_language_code: str
) -> tuple[str, dict]:
    """
    Transcribe audio file using OpenAI's Whisper
    Returns (transcribed_text, metadata).

    Args:
        file_obj: Either a Path to an audio file or a file-like object containing audio data
        target_language_code: ISO 639-1 code (e.g. 'el' for Greek)
    """
    if target_language_code not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Language {target_language_code} not supported")

    try:
        # If it's a Path, open and read the file
        if isinstance(file_obj, Path):
            is_valid, error = validate_audio_file(file_obj)
            if not is_valid:
                raise ValueError(f"Invalid audio file: {error}")
            audio_file = open(file_obj, "rb")
        else:
            # For file-like objects, use directly
            audio_file = file_obj

        # Call Whisper API with improved parameters
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            # Explicitly set the language for better accuracy
            language=target_language_code,
            # Request timestamps for potential future use
            timestamp_granularities=["segment"],
            # Add parameters to improve transcription quality
            temperature=0,
            # prompt="This is a song with lyrics in Greek",  # Help guide the model
        )

        # Extract text and metadata
        text = response.text
        metadata = {
            "model": "whisper-1",
            "duration": getattr(response, "duration", None),
            "language": getattr(response, "language", None),
            "segments": getattr(response, "segments", []),
        }

        return text, metadata

    finally:
        # Only close if we opened it
        if isinstance(file_obj, Path):
            audio_file.close()


def get_audio_file_info(file_path: Path) -> dict:
    """
    Get information about an audio file.
    Returns dict with size and other metadata.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return {
        "size": os.path.getsize(file_path),
        "format": file_path.suffix.lower(),
    }


def add_delays(txt: str) -> str:
    """Add delay markers to text for speech synthesis."""
    delay_template = '<break time="%.2fs" />'

    # Process patterns in order: commas, periods, newlines
    txt_slow = txt
    # First handle commas
    if ", " in txt_slow:
        txt_slow = txt_slow.replace(", ", f", {delay_template % 0.5}")

    # Then handle periods, but not if they're part of a delay marker
    parts = txt_slow.split(". ")
    txt_slow = (f". {delay_template % 0.75}").join(parts)

    # Finally handle newlines
    parts = txt_slow.split("\n")
    txt_slow = (f"\n{delay_template % 1.0}").join(parts)

    return txt_slow


def ensure_audio_data(
    text: str,
    should_add_delays: bool = True,
    should_play: bool = False,
    verbose: int = 0,
    voice_name: Optional[str] = None,
    voice_settings: Optional[dict[str, Any]] = None,
    target_language_code: Optional[str] = None,
) -> bytes:
    """Core function to generate audio data from text.

    Args:
        text: Text to generate audio for
        should_add_delays: Whether to add delays between sentences
        should_play: Whether to play the audio after generating
        verbose: Verbosity level

    Returns:
        bytes: Generated MP3 audio data
    """
    if verbose >= 1:
        print(f"Generating audio for: {text[:100]}...")

    # Add delays if requested
    text_with_delays = add_delays(text) if should_add_delays else text

    # Select a voice: prefer explicit voice_name, else fall back to the first configured voice
    selected_voice = voice_name or (
        ELEVENLABS_VOICE_POOL[0] if ELEVENLABS_VOICE_POOL else ""
    )

    if verbose >= 1:
        print(f"Selected voice: {selected_voice}")

    # Create temporary file for ElevenLabs API
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
        outloud_elevenlabs(
            text=text_with_delays,
            api_key=ELEVENLABS_API_KEY.get_secret_value().strip(),
            mp3_filen=temp_file.name,
            bot_name=selected_voice,
            voice_settings=voice_settings,
        )

        # Read the generated audio
        temp_file.seek(0)
        audio_data = temp_file.read()

        # Check size
        if len(audio_data) > MAX_AUDIO_SIZE_FOR_STORAGE:
            raise ValueError(
                f"Generated audio too large (max {MAX_AUDIO_SIZE_FOR_STORAGE/(1024*1024):.1f}MB)"
            )

        # Play if requested
        if should_play:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as play_file:
                play_file.write(audio_data)
                play_file.flush()
                play_mp3(play_file.name)

        return audio_data


DEFAULT_AUDIO_PROVIDER = "elevenlabs"
DEFAULT_AUDIO_MODEL = "elevenlabs-tts-v1"


def select_random_voices(n: int, exclude: set[str] | None = None) -> list[str]:
    """Select up to n distinct voices from the configured pool."""

    exclude = exclude or set()
    available = [voice for voice in ELEVENLABS_VOICE_POOL if voice not in exclude]
    if not available or n <= 0:
        return []

    if n >= len(available):
        random.shuffle(available)
        return available

    return random.sample(available, n)


def _build_metadata(voice_name: str, settings: Optional[dict[str, Any]] = None) -> dict:
    metadata = {
        "provider": DEFAULT_AUDIO_PROVIDER,
        "voice_name": voice_name,
        "model": DEFAULT_AUDIO_MODEL,
        "settings": settings or {},
    }
    return metadata


def ensure_sentence_audio_variants(
    sentence: Sentence,
    n: int = SENTENCE_AUDIO_SAMPLES,
    *,
    enforce_auth: bool = True,
) -> tuple[list[SentenceAudio], int]:
    """Ensure up to n distinct voice variants exist for a sentence.

    Important: Keep DB connections scoped to the minimal sections of code that
    actually touch the database so we don't hold pool connections during slow
    external TTS calls. This helps avoid pool exhaustion under load.
    """

    text = (sentence.sentence or "").strip()
    if not text:
        raise ValueError("Sentence text is required for audio generation")

    # Load existing variants within a short-lived DB connection
    with database.connection_context():
        existing_variants = list(
            SentenceAudio.select()
            .where(SentenceAudio.sentence == sentence)
            .order_by(SentenceAudio.created_at)
        )

    existing_voice_names = {
        (variant.metadata or {}).get("voice_name")
        for variant in existing_variants
        if (variant.metadata or {}).get("voice_name")
    }

    target_total = min(n, len(ELEVENLABS_VOICE_POOL))
    missing = max(0, target_total - len(existing_voice_names))
    new_voice_names = select_random_voices(missing, existing_voice_names)

    if enforce_auth and new_voice_names and (not hasattr(g, "user") or g.user is None):
        raise AuthenticationRequiredForGenerationError(
            "Authentication required to generate sentence audio"
        )

    created_variants: list[SentenceAudio] = []
    created_by = getattr(g, "user_id", None)  # Pass user UUID (FK)

    # Generate audio outside of any DB connection
    generated_payloads: list[tuple[str, bytes, dict]] = []
    for voice_name in new_voice_names:
        audio_bytes = ensure_audio_data(
            text=text,
            should_add_delays=True,
            should_play=False,
            verbose=0,
            voice_name=voice_name,
        )
        metadata = _build_metadata(voice_name)
        generated_payloads.append((voice_name, audio_bytes, metadata))

    # Persist generated variants using short-lived DB connections
    # Re-check for each voice to handle concurrent requests gracefully
    for voice_name, audio_bytes, metadata in generated_payloads:
        with database.connection_context():
            # Check if this voice was created by a concurrent request
            already_exists = (
                SentenceAudio.select()
                .where(SentenceAudio.sentence == sentence)
                .where(
                    fn.json_extract_path_text(
                        SentenceAudio.metadata, "voice_name"
                    )
                    == voice_name
                )
                .exists()
            )
            if already_exists:
                continue

            try:
                variant = SentenceAudio.create(
                    sentence=sentence,
                    provider=metadata["provider"],
                    audio_data=audio_bytes,
                    metadata=metadata,
                    created_by=created_by,
                )
                created_variants.append(variant)
            except Exception as e:
                # Handle race condition where another request created this variant
                logger.debug(f"Skipping duplicate audio variant: {e}")

    if created_variants:
        # Refresh final list so callers can rely on ordering/ids
        with database.connection_context():
            existing_variants = list(
                SentenceAudio.select()
                .where(SentenceAudio.sentence == sentence)
                .order_by(SentenceAudio.created_at)
            )

    return existing_variants, len(created_variants)


def ensure_lemma_audio_variants(
    lemma: Lemma,
    n: int = LEMMA_AUDIO_SAMPLES,
    *,
    enforce_auth: bool = True,
) -> tuple[list[LemmaAudio], int]:
    """Ensure up to n distinct voice variants exist for a lemma.

    Keep DB connection windows short to protect the pool under concurrent play.
    """

    text = (lemma.lemma or "").strip()
    if not text:
        raise ValueError("Lemma text is required for audio generation")

    with database.connection_context():
        existing_variants = list(
            LemmaAudio.select()
            .where(LemmaAudio.lemma == lemma)
            .order_by(LemmaAudio.created_at)
        )

    existing_voice_names = {
        (variant.metadata or {}).get("voice_name")
        for variant in existing_variants
        if (variant.metadata or {}).get("voice_name")
    }

    target_total = min(n, len(ELEVENLABS_VOICE_POOL))
    missing = max(0, target_total - len(existing_voice_names))
    new_voice_names = select_random_voices(missing, existing_voice_names)

    if enforce_auth and new_voice_names and (not hasattr(g, "user") or g.user is None):
        raise AuthenticationRequiredForGenerationError(
            "Authentication required to generate lemma audio"
        )

    created_variants: list[LemmaAudio] = []
    created_by = getattr(g, "user_id", None)
    voice_settings = {"stability": 0.92}

    generated_payloads: list[tuple[str, bytes, dict]] = []
    for voice_name in new_voice_names:
        audio_bytes = ensure_audio_data(
            text=text,
            should_add_delays=False,
            should_play=False,
            verbose=0,
            voice_name=voice_name,
            voice_settings=voice_settings,
        )
        metadata = _build_metadata(voice_name, settings=voice_settings)
        generated_payloads.append((voice_name, audio_bytes, metadata))

    # Re-check for each voice to handle concurrent requests gracefully
    for voice_name, audio_bytes, metadata in generated_payloads:
        with database.connection_context():
            # Check if this voice was created by a concurrent request
            already_exists = (
                LemmaAudio.select()
                .where(LemmaAudio.lemma == lemma)
                .where(
                    fn.json_extract_path_text(LemmaAudio.metadata, "voice_name")
                    == voice_name
                )
                .exists()
            )
            if already_exists:
                continue

            try:
                variant = LemmaAudio.create(
                    lemma=lemma,
                    provider=metadata["provider"],
                    audio_data=audio_bytes,
                    metadata=metadata,
                    created_by=created_by,
                )
                created_variants.append(variant)
            except Exception as e:
                # Handle race condition where another request created this variant
                logger.debug(f"Skipping duplicate lemma audio variant: {e}")

    if created_variants:
        with database.connection_context():
            existing_variants = list(
                LemmaAudio.select()
                .where(LemmaAudio.lemma == lemma)
                .order_by(LemmaAudio.created_at)
            )

    return existing_variants, len(created_variants)


def stream_random_sentence_audio(sentence_id: int) -> Optional[SentenceAudio]:
    """Fetch a random sentence audio variant."""

    return (
        SentenceAudio.select()
        .where(SentenceAudio.sentence == sentence_id)
        .order_by(fn.Random())
        .first()
    )


def ensure_model_audio_data(
    model,
    should_add_delays: bool = True,
    should_play: bool = False,
    verbose: int = 0,
) -> None:
    """Ensure legacy models with audio_data blobs have generated audio.

    This retains compatibility for Sourcefile-style models that still store
    a single audio blob instead of variants.
    """

    if not hasattr(model, "audio_data"):
        raise AttributeError("Model does not define audio_data")

    if getattr(model, "audio_data", None):
        return

    if not hasattr(g, "user") or g.user is None:
        raise AuthenticationRequiredForGenerationError(
            "Authentication required to generate audio"
        )

    text = getattr(model, "text_target", None) or getattr(model, "sentence", None)
    if not text:
        raise ValueError("No text available for audio generation")

    if verbose >= 1:
        print(
            f"Generating audio for {model.__class__.__name__}: {getattr(model, 'id', '?')}"
        )

    model.audio_data = ensure_audio_data(
        text=text,
        should_add_delays=should_add_delays,
        should_play=should_play,
        verbose=verbose,
    )
    model.save()
