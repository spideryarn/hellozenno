from pathlib import Path
import pytest
from unittest.mock import Mock, patch, MagicMock

from audio_utils import (
    validate_audio_file,
    add_delays,
    transcribe_audio,
    ensure_audio_data,
    ensure_model_audio_data,
)
from db_models import Sourcefile, Sourcedir, Sentence
from config import MAX_AUDIO_SIZE_FOR_STORAGE


@pytest.fixture
def test_sourcedir(test_db):
    """Create a test sourcedir."""
    sourcedir = Sourcedir.create(
        path="test_dir",
        language_code="el",
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


@pytest.fixture
def mock_elevenlabs():
    """Mock ElevenLabs API calls."""
    with patch("audio_utils.outloud_elevenlabs") as mock:

        def fake_generate_audio(text, api_key, mp3_filen):
            # Write some fake audio data to the file
            with open(mp3_filen, "wb") as f:
                f.write(b"fake mp3 data")

        mock.side_effect = fake_generate_audio
        yield mock


@pytest.fixture
def mock_play_mp3():
    """Mock MP3 playback."""
    with patch("audio_utils.play_mp3") as mock:
        yield mock


@pytest.fixture
def mock_openai():
    """Mock OpenAI Whisper API calls."""
    with patch("audio_utils.client") as mock:
        mock_response = Mock()
        mock_response.text = "Transcribed text"
        mock.audio.transcriptions.create.return_value = mock_response
        yield mock


def test_transcribe_audio(mock_openai, tmp_path):
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


def test_ensure_model_audio_data(mock_elevenlabs, test_db, test_sourcedir):
    """Test generating audio for model instances."""
    # Test with Sentence model
    sentence = Sentence.create(
        language_code="el",
        sentence="Test sentence",
        translation="Test translation",
    )
    ensure_model_audio_data(sentence)
    assert sentence.audio_data == b"fake mp3 data"

    # Test with Sourcefile model
    sourcefile = Sourcefile.create(
        sourcedir=test_sourcedir,
        filename="test.txt",
        text_target="Test text",
        text_english="Test translation",
        metadata={},
        sourcefile_type="text",
    )
    ensure_model_audio_data(sourcefile)
    assert sourcefile.audio_data == b"fake mp3 data"

    # Test with empty text
    empty_sentence = Sentence.create(
        language_code="el",
        sentence="",
        translation="",
    )
    with pytest.raises(ValueError, match="No text available for audio generation"):
        ensure_model_audio_data(empty_sentence)

    # Test with existing audio
    mock_elevenlabs.reset_mock()
    ensure_model_audio_data(sentence)  # Should not regenerate
    assert not mock_elevenlabs.called
