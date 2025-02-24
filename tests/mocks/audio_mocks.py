import pytest


from unittest.mock import Mock, patch


@pytest.fixture
def mock_elevenlabs():
    """Mock ElevenLabs API calls."""
    with patch("utils.audio_utils.outloud_elevenlabs") as mock:

        def fake_generate_audio(text, api_key, mp3_filen, bot_name=None):
            # Write some fake audio data to the file
            with open(mp3_filen, "wb") as f:
                f.write(b"fake mp3 data")

        mock.side_effect = fake_generate_audio
        yield mock


@pytest.fixture
def mock_play_mp3():
    """Mock MP3 playback."""
    with patch("utils.audio_utils.play_mp3") as mock:
        yield mock


@pytest.fixture
def mock_openai_whisper():
    """Mock OpenAI Whisper API calls."""
    with patch("utils.audio_utils.client") as mock:
        mock_response = Mock()
        mock_response.text = "Transcribed text"
        mock.audio.transcriptions.create.return_value = mock_response
        yield mock
