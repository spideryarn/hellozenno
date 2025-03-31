"""Tests for youtube_utils.py."""

import pytest
from unittest.mock import patch, MagicMock
from utils.youtube_utils import (
    extract_video_metadata,
    download_audio,
    download_subtitles,
    YouTubeDownloadError,
)
from api.config import MAX_AUDIO_SIZE_UPLOAD_ALLOWED
import shutil
import os
import yt_dlp
from pathlib import Path


@pytest.fixture
def mock_yt_dlp():
    """Mock yt-dlp for testing."""
    with patch("utils.youtube_utils.yt_dlp.YoutubeDL") as mock_ydl:
        # Create mock info dict
        mock_info = {
            "id": "test_video_id",
            "title": "Test Video",
            "uploader": "Test Channel",
            "upload_date": "20240111",
            "duration": 300,  # 5 minutes
            "age_limit": 0,
        }

        # Setup mock YoutubeDL instance
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = mock_info
        mock_ydl.return_value.__enter__.return_value = mock_instance

        yield mock_ydl


def test_extract_video_metadata(mock_yt_dlp):
    """Test extracting metadata from a YouTube video."""
    url = "https://www.youtube.com/watch?v=test_video_id"
    metadata = extract_video_metadata(url)

    assert metadata["source"] == "youtube"
    assert metadata["video_id"] == "test_video_id"
    assert metadata["video_title"] == "Test Video"
    assert metadata["channel"] == "Test Channel"
    assert metadata["upload_date"] == "20240111"
    assert metadata["url"] == url
    assert metadata["duration_secs"] == 300
    assert "download_date" in metadata


def test_extract_video_metadata_age_restricted(mock_yt_dlp):
    """Test that age-restricted videos are rejected."""
    # Update mock to return age-restricted video info
    mock_yt_dlp.return_value.__enter__.return_value.extract_info.return_value[
        "age_limit"
    ] = 18

    url = "https://www.youtube.com/watch?v=age_restricted_video"
    with pytest.raises(
        YouTubeDownloadError, match="Age-restricted videos are not supported"
    ):
        extract_video_metadata(url)


def test_extract_video_metadata_too_long(mock_yt_dlp):
    """Test that videos that would exceed size limit are rejected."""
    # Update mock to return long video info
    # At 128kbps, 1 minute = ~1MB
    # Set duration to exceed MAX_AUDIO_SIZE_UPLOAD_ALLOWED
    duration = (MAX_AUDIO_SIZE_UPLOAD_ALLOWED * 8) // (128 * 1024) + 1  # seconds
    mock_yt_dlp.return_value.__enter__.return_value.extract_info.return_value[
        "duration"
    ] = duration

    url = "https://www.youtube.com/watch?v=long_video"
    with pytest.raises(YouTubeDownloadError, match="would exceed size limit"):
        extract_video_metadata(url)


def test_download_audio(mock_yt_dlp, tmp_path):
    """Test downloading audio from a YouTube video."""
    # Create mock audio file
    mock_audio = b"test audio data" * 1000  # Some test audio data

    # Update mock to handle download
    def mock_download(urls):
        # Get the output template from ydl_opts
        output_template = mock_yt_dlp.call_args[0][0]["outtmpl"]
        # Create the output file
        output_path = output_template + ".mp3"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(mock_audio)
        return True

    mock_yt_dlp.return_value.__enter__.return_value.download = mock_download

    url = "https://www.youtube.com/watch?v=test_video_id"
    audio_data, metadata = download_audio(url)

    assert len(audio_data) > 0
    assert metadata["video_id"] == "test_video_id"


def test_download_audio_download_error(mock_yt_dlp):
    """Test handling of download errors."""
    # Make download fail with yt-dlp's error
    mock_yt_dlp.return_value.__enter__.return_value.download.side_effect = (
        yt_dlp.utils.DownloadError("Download failed")
    )

    url = "https://www.youtube.com/watch?v=nonexistent_video"
    with pytest.raises(YouTubeDownloadError, match="Failed to download audio"):
        download_audio(url)


def test_download_audio_size_limit(mock_yt_dlp, tmp_path):
    """Test that downloaded audio respecting size limit."""
    # Create mock audio file that's too large
    mock_audio = b"x" * (MAX_AUDIO_SIZE_UPLOAD_ALLOWED + 1024)  # Exceed limit

    # Update mock to handle download
    def mock_download(urls):
        # Get the output template from ydl_opts
        output_template = mock_yt_dlp.call_args[0][0]["outtmpl"]
        # Create the output file
        output_path = output_template + ".mp3"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(mock_audio)
        return True

    mock_yt_dlp.return_value.__enter__.return_value.download = mock_download

    url = "https://www.youtube.com/watch?v=large_video"
    with pytest.raises(YouTubeDownloadError, match="exceeds size limit"):
        download_audio(url)


def test_extract_video_metadata_with_subtitles(mock_yt_dlp):
    """Test extracting metadata with subtitle information."""
    # Mock subtitle information
    mock_info = (
        mock_yt_dlp.return_value.__enter__.return_value.extract_info.return_value
    )
    mock_info.update(
        {
            "subtitles": {
                "en": [{"url": "http://example.com/manual_en.srt"}],
                "es": [{"url": "http://example.com/manual_es.srt"}],
            },
            "automatic_captions": {
                "en": [{"url": "http://example.com/auto_en.srt"}],
                "fr": [{"url": "http://example.com/auto_fr.srt"}],
            },
            "language": "en",
            "tags": ["music", "official video"],
            "categories": ["Music"],
        }
    )

    url = "https://www.youtube.com/watch?v=test_video_id"
    metadata = extract_video_metadata(url)

    assert "manual" in metadata["subtitles"]
    assert "auto_generated" in metadata["subtitles"]
    assert "en" in metadata["subtitles"]["manual"]
    assert "fr" in metadata["subtitles"]["auto_generated"]
    assert metadata["detected_language"] == "en"
    assert metadata["is_likely_music"] is True


def test_download_subtitles(mock_yt_dlp, tmp_path):
    """Test downloading subtitles."""

    # Mock subtitle files
    def mock_download(urls):
        # Get the output template
        output_template = mock_yt_dlp.call_args[0][0]["outtmpl"]
        base_path = Path(output_template)

        # Create mock subtitle files
        (base_path.parent / f"{base_path.name}.en.vtt").write_text("English subtitles")
        (base_path.parent / f"{base_path.name}.es.auto.vtt").write_text(
            "Spanish auto-generated"
        )
        return True

    mock_yt_dlp.return_value.__enter__.return_value.download = mock_download

    # Mock metadata with subtitle info
    mock_info = (
        mock_yt_dlp.return_value.__enter__.return_value.extract_info.return_value
    )
    mock_info.update(
        {
            "subtitles": {"en": [{}]},
            "automatic_captions": {"es": [{}]},
        }
    )

    url = "https://www.youtube.com/watch?v=test_video_id"
    subtitles = download_subtitles(url, target_languages=["en", "es"])

    assert "en" in subtitles
    assert subtitles["en"] == "English subtitles"
    assert "es" in subtitles
    assert subtitles["es"] == "Spanish auto-generated"


def test_download_audio_with_subtitles(mock_yt_dlp, tmp_path):
    """Test downloading audio with available subtitles."""
    # Create mock audio file
    mock_audio = b"test audio data" * 1000

    # Mock subtitle information
    mock_info = (
        mock_yt_dlp.return_value.__enter__.return_value.extract_info.return_value
    )
    mock_info.update(
        {
            "language": "el",  # Greek
            "subtitles": {"el": [{}]},  # Manual Greek subtitles available
            "categories": ["Music"],  # Mark as music
        }
    )

    # Mock audio download
    def mock_download(urls):
        # Get the output template from ydl_opts
        output_template = mock_yt_dlp.call_args[0][0]["outtmpl"]
        # Create the output file
        if "subs" in output_template:  # Subtitle download
            base_path = Path(output_template)
            (base_path.parent / f"{base_path.name}.el.vtt").write_text(
                "WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nGreek subtitles"
            )
        else:  # Audio download
            output_path = output_template + ".mp3"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(mock_audio)
        return True

    mock_yt_dlp.return_value.__enter__.return_value.download = mock_download

    url = "https://www.youtube.com/watch?v=test_video_id"
    audio_data, metadata = download_audio(url)

    assert len(audio_data) > 0
    assert metadata["detected_language"] == "el"
    assert metadata["is_likely_music"] is True
    assert "subtitle_content" in metadata
    assert "Greek subtitles" in metadata["subtitle_content"]
    assert metadata["subtitle_source"] == "manual"


def test_download_audio_with_auto_subs_for_music(mock_yt_dlp, tmp_path):
    """Test that auto-generated subtitles are used for music content."""
    # Create mock audio file
    mock_audio = b"test audio data" * 1000

    # Mock subtitle information - only auto subs available
    mock_info = (
        mock_yt_dlp.return_value.__enter__.return_value.extract_info.return_value
    )
    mock_info.update(
        {
            "language": "el",
            "automatic_captions": {"el": [{}]},  # Only auto subs available
            "categories": ["Music"],
            "tags": ["music video"],
        }
    )

    # Mock audio download
    def mock_download(urls):
        # Get the output template from ydl_opts
        output_template = mock_yt_dlp.call_args[0][0]["outtmpl"]
        # Create the output file
        if "subs" in output_template:  # Subtitle download
            base_path = Path(output_template)
            (base_path.parent / f"{base_path.name}.el.auto.vtt").write_text(
                "WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nAuto-generated Greek subtitles"
            )
        else:  # Audio download
            output_path = output_template + ".mp3"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(mock_audio)
        return True

    mock_yt_dlp.return_value.__enter__.return_value.download = mock_download

    url = "https://www.youtube.com/watch?v=test_video_id"
    audio_data, metadata = download_audio(url)

    assert len(audio_data) > 0
    assert metadata["detected_language"] == "el"
    assert metadata["is_likely_music"] is True
    assert "subtitle_content" in metadata
    assert "Auto-generated Greek subtitles" in metadata["subtitle_content"]
    assert metadata["subtitle_source"] == "auto_generated"
