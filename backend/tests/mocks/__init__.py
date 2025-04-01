"""Common test mocks for the application."""

from .search_mocks import mock_quick_search_for_wordform
from .audio_mocks import mock_elevenlabs, mock_play_mp3, mock_openai_whisper
from .gpt_mocks import mock_gpt_from_template
from .youtube_mocks import mock_download_audio

__all__ = [
    "mock_quick_search_for_wordform",
    "mock_elevenlabs",
    "mock_play_mp3",
    "mock_openai_whisper",
    "mock_gpt_from_template",
    "mock_download_audio",
]
