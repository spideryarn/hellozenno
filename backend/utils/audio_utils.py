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

    # Randomly select a voice for ElevenLabs
    voices = ["Charlotte", "Serena", "Josh", "Michael"]
    selected_voice = random.choice(voices)

    if verbose >= 1:
        print(f"Selected voice: {selected_voice}")

    # Create temporary file for ElevenLabs API
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as temp_file:
        outloud_elevenlabs(
            text=text_with_delays,
            api_key=ELEVENLABS_API_KEY.get_secret_value(),
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
    """
    if not model.audio_data:
        if not hasattr(g, "user") or g.user is None:
            raise AuthenticationRequiredForGenerationError(
                "User must be logged in to generate audio."
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
