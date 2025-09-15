from typing import Optional, BinaryIO, Union
from pathlib import Path
import os
import tempfile
import random
from utils.env_config import ELEVENLABS_API_KEY, OPENAI_API_KEY
from config import MAX_AUDIO_SIZE_FOR_STORAGE, SUPPORTED_LANGUAGES
from gjdutils.audios import play_mp3
from gjdutils.outloud_text_to_speech import outloud_elevenlabs
from openai import OpenAI

# Import the exception and g for global context
from flask import g
from .exceptions import AuthenticationRequiredForGenerationError

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

    # Randomly select a voice for ElevenLabs from known-available names
    voices = [
        "Alice",
        "Bill",
        "Brian",
        "Callum",
        "Charlie",
        "Chris",
        "Clyde",
        "Daniel",
        "Eric",
        "George",
        "Harry",
        "Jessica",
        "Laura",
        "Liam",
        "Lily",
        "Matilda",
        "Rachel",
        "River",
        "Roger",
        "Sarah",
    ]
    selected_voice = random.choice(voices)

    if verbose >= 1:
        print(f"Selected voice: {selected_voice}")

    # Create temporary file for ElevenLabs API
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
        outloud_elevenlabs(
            text=text_with_delays,
            api_key=ELEVENLABS_API_KEY.get_secret_value().strip(),
            mp3_filen=temp_file.name,
            bot_name=selected_voice,
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


def get_or_create_sentence_audio(
    sentence_model,
    should_add_delays: bool = True,
    should_play: bool = False,
    verbose: int = 0,
) -> tuple[Optional[bytes], bool]:
    """Get or create audio for a Sentence, checking auth for creation.

    Args:
        sentence_model: Sentence instance
        should_add_delays: Whether to add delays between sentences
        should_play: Whether to play the audio
        verbose: Verbosity level

    Returns:
        tuple: (audio_data, requires_login)
               audio_data is None and requires_login is True if generation is needed but user is not logged in.
    """
    if sentence_model.audio_data:
        return sentence_model.audio_data, False  # Audio exists, no login required

    # Generation is needed
    if not hasattr(g, "user") or g.user is None:
        # No user logged in, cannot generate
        if verbose >= 1:
            print(
                f"Skipping audio generation for Sentence {sentence_model.id}: User not logged in."
            )
        return None, True  # Indicate login is required

    # User is logged in, proceed with generation
    if verbose >= 1:
        print(f"Generating audio for Sentence: {sentence_model.id}")

    if not sentence_model.sentence:
        raise ValueError("No text available for audio generation")

    # Generate audio
    audio_data = ensure_audio_data(
        text=sentence_model.sentence,
        should_add_delays=should_add_delays,
        should_play=should_play,
        verbose=verbose,
    )

    # Save audio data to the model
    sentence_model.audio_data = audio_data
    sentence_model.save()

    return audio_data, False  # Audio generated, no login required now


def ensure_model_audio_data(
    model: Union["Sentence", "Sourcefile"],  # type: ignore
    should_add_delays: bool = True,
    should_play: bool = False,
    verbose: int = 0,
) -> None:
    """Ensure a model instance has audio data, generating it if missing.

    Args:
        model: Sentence or Sourcefile instance
        should_add_delays: Whether to add delays between sentences
        should_play: Whether to play the audio
        verbose: Verbosity level

    Raises:
        AuthenticationRequiredForGenerationError: If generation needed for a Sentence and user is not logged in.
        -> THIS IS NOW HANDLED BY get_or_create_sentence_audio for Sentences
    """
    if not model.audio_data:
        # Generation is required. Check if it's a Sentence and call the new function.
        # For Sourcefile, assume auth is handled upstream (e.g., by @api_auth_required)
        if hasattr(model, "sentence"):  # Check if it's a Sentence model
            audio_data, requires_login = get_or_create_sentence_audio(
                sentence_model=model,
                should_add_delays=should_add_delays,
                should_play=should_play,
                verbose=verbose,
            )
            if requires_login:
                # This case should ideally not be hit if calling this function directly,
                # as it implies auth wasn't checked. Log a warning.
                print(
                    f"Warning: ensure_model_audio_data called for Sentence {model.id} without prior auth check."
                )
                # We can't raise AuthenticationRequiredForGenerationError here as the function signature is void
                # The calling context needs to handle the requires_login flag if using get_or_create_sentence_audio
                return  # Stop processing if login is required
            # If audio_data is None and requires_login is False, something went wrong in generation
            if audio_data is None and not requires_login:
                print(
                    f"Warning: Audio generation failed for Sentence {model.id} even with auth."
                )
                return  # Stop processing
            # Audio was successfully generated (or existed already indirectly), model is saved inside get_or_create
            return

        # If it's not a Sentence (e.g., Sourcefile), proceed with original logic
        # Assume auth is handled by the calling endpoint decorator (@api_auth_required)
        else:
            if not hasattr(g, "user") or g.user is None:
                # This shouldn't happen if the calling endpoint uses @api_auth_required
                print(
                    f"Warning: ensure_model_audio_data called for non-Sentence model without user context."
                )
                # Raise an error or just return, depending on desired strictness
                raise Exception(
                    "Auth context missing for non-Sentence audio generation"
                )

            print(f"Generating audio for {model.__class__.__name__}: {model.id}")
            # Get text based on model type
            text = model.sentence if hasattr(model, "sentence") else model.text_target
            if not text:
                raise ValueError("No text available for audio generation")

            # Generate audio
            model.audio_data = ensure_audio_data(
                text=text,
                should_add_delays=should_add_delays,
                should_play=should_play,
                verbose=verbose,
            )
            model.save()
