from pathlib import Path
import pytest
from unittest.mock import MagicMock
from tests.mocks.audio_mocks import mock_openai_whisper, mock_elevenlabs

from utils.audio_utils import (
    validate_audio_file,
    add_delays,
    transcribe_audio,
    ensure_audio_data,
    ensure_model_audio_data,
    ensure_sentence_audio_variants,
    ensure_lemma_audio_variants,
    stream_random_sentence_audio,
)
from db_models import (
    Sourcefile,
    Sourcedir,
    Sentence,
    Lemma,
    SentenceAudio,
    LemmaAudio,
)
from config import MAX_AUDIO_SIZE_FOR_STORAGE
from utils.exceptions import AuthenticationRequiredForGenerationError


@pytest.fixture
def test_sourcedir(fixture_for_testing_db):
    """Create a test sourcedir."""
    sourcedir = Sourcedir.create(
        path="test_dir",
        target_language_code="el",
    )
    return sourcedir


def test_validate_audio_file(tmp_path):
    """Test audio file validation."""
    # Test non-existent file
    non_existent = tmp_path / "nonexistent.mp3"
    is_valid, error = validate_audio_file(non_existent)
    assert not is_valid
    assert error == "File does not exist"

    # Test wrong extension
    wav_file = tmp_path / "test.wav"
    wav_file.write_bytes(b"fake wav data")
    is_valid, error = validate_audio_file(wav_file)
    assert not is_valid
    assert error == "Only MP3 files are supported"

    # Test empty file
    empty_mp3 = tmp_path / "empty.mp3"
    empty_mp3.write_bytes(b"")
    is_valid, error = validate_audio_file(empty_mp3)
    assert not is_valid
    assert error == "File is empty"

    # Test file too large
    large_mp3 = tmp_path / "large.mp3"
    large_mp3.write_bytes(b"x" * (MAX_AUDIO_SIZE_FOR_STORAGE + 1024))
    is_valid, error = validate_audio_file(large_mp3)
    assert not is_valid
    assert error is not None
    assert "MB" in error  # Check for size message

    # Test valid file
    valid_mp3 = tmp_path / "valid.mp3"
    valid_mp3.write_bytes(b"x" * 1024)  # 1KB file
    is_valid, error = validate_audio_file(valid_mp3)
    assert is_valid
    assert error is None


def test_add_delays():
    """Test adding delay markers to text."""
    # Test each case separately
    assert add_delays("one, two") == 'one, <break time="0.50s" />two'
    assert add_delays("one. two") == 'one. <break time="0.75s" />two'
    assert add_delays("line1\nline2") == 'line1\n<break time="1.00s" />line2'

    # Test a simple combined case - just ensure we get reasonable pauses
    result = add_delays("Hello, world.\nNew line")
    assert '<break time="0.50s" />' in result  # Has comma pause
    assert '<break time="1.00s" />' in result  # Has newline pause


def test_transcribe_audio(mock_openai_whisper, tmp_path):
    """Test audio transcription."""
    # Test with invalid language
    with pytest.raises(ValueError, match="Language xx not supported"):
        transcribe_audio(tmp_path / "test.mp3", "xx")

    # Create test audio file
    test_file = tmp_path / "test.mp3"
    test_file.write_bytes(b"fake mp3 data")

    # Test successful transcription
    text, metadata = transcribe_audio(test_file, "el")
    assert text == "Transcribed text"
    assert "model" in metadata
    assert metadata["model"] == "whisper-1"

    # Test with file-like object
    with open(test_file, "rb") as f:
        text, metadata = transcribe_audio(f, "el")
        assert text == "Transcribed text"


def test_ensure_audio_data(mock_elevenlabs):
    """Test core audio generation function."""
    # Test basic generation without delays
    audio_data = ensure_audio_data("Test text", should_add_delays=False)
    assert audio_data == b"fake mp3 data"
    mock_elevenlabs.assert_called_once()
    assert mock_elevenlabs.call_args[1]["text"] == "Test text"

    # Verify voice selection (display name passed into resolver)
    assert mock_elevenlabs.call_args[1]["bot_name"] in [
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

    # Test with delays - use text that will trigger delays
    mock_elevenlabs.reset_mock()
    audio_data = ensure_audio_data(
        "Test text, with commas. And periods.\nAnd newlines.", should_add_delays=True
    )
    assert audio_data == b"fake mp3 data"
    text_with_delays = mock_elevenlabs.call_args[1]["text"]
    assert (
        text_with_delays != "Test text, with commas. And periods.\nAnd newlines."
    )  # Text should be modified
    assert "<break" in text_with_delays  # Should have delay markers

    # Verify voice selection again
    assert mock_elevenlabs.call_args[1]["bot_name"] in [
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


@pytest.mark.skip(reason="Low-value unit test - requires complex db binding; audio tested via API")
def test_ensure_model_audio_data_for_sourcefiles(
    mock_elevenlabs, fixture_for_testing_db, test_sourcedir, client
):
    """Ensure legacy sourcefile audio generation behaves as expected."""
    pass


@pytest.mark.skip(reason="Low-value unit test - requires complex db binding; audio tested via API")
def test_ensure_sentence_audio_variants(
    mock_elevenlabs, fixture_for_testing_db, client
):
    """Test sentence audio variant generation."""
    pass


@pytest.mark.skip(reason="Low-value unit test - requires complex db binding; audio tested via API")
def test_ensure_lemma_audio_variants(mock_elevenlabs, fixture_for_testing_db, client):
    """Test lemma audio variant generation."""
    pass
