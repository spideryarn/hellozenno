"""Utilities for downloading and processing YouTube videos."""

import tempfile
from pathlib import Path
from typing import Optional, Tuple
import yt_dlp
from datetime import datetime
import os

from config import MAX_AUDIO_SIZE_UPLOAD_ALLOWED


class YouTubeDownloadError(Exception):
    """Custom exception for YouTube download errors."""

    pass


def extract_video_metadata(url: str) -> dict:
    """Extract metadata from a YouTube video URL.

    Args:
        url: YouTube video URL

    Returns:
        dict containing video metadata including:
        - Basic video info (id, title, etc)
        - Available subtitle/caption tracks
        - Language info
        - Content type hints (music vs speech)

    Raises:
        YouTubeDownloadError: If video info cannot be extracted
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "allsubtitles": True,  # Get all available subtitle tracks
        "subtitlesformat": "vtt",  # VTT format is most widely supported
        "default_search": "none",  # Don't treat input as search query
        "nocheckcertificate": True,
        "cookiefile": None,  # Don't use cookies
        # "extractor_retries": 3,  # Retry 3 times on failure
        "http_headers": {  # Use more browser-like headers
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        },
    }

    try:
        print(f"\nDEBUG: Processing YouTube URL: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise YouTubeDownloadError("Could not extract video info")
            # Check for age restriction
            if info.get("age_limit", 0) > 0:
                raise YouTubeDownloadError("Age-restricted videos are not supported")

            # Check duration and estimated file size
            duration_secs = info.get("duration", 0)
            bitrate = 128  # kbps for MP3
            estimated_size = (duration_secs * bitrate * 1024) / 8  # bytes

            if estimated_size > MAX_AUDIO_SIZE_UPLOAD_ALLOWED:
                raise YouTubeDownloadError(
                    f"Video audio would exceed size limit of {MAX_AUDIO_SIZE_UPLOAD_ALLOWED/(1024*1024):.1f}MB"
                )

            # Extract subtitle information
            subtitles = info.get("subtitles", {})  # Manual subtitles
            auto_subtitles = info.get(
                "automatic_captions", {}
            )  # Auto-generated captions

            # Extract language information
            language = info.get("language")
            # Some videos have language in tags or description
            tags = info.get("tags", [])
            description = info.get("description", "")

            # Try to detect if it's music
            # YouTube often categorizes music in these ways:
            is_music = any(
                [
                    info.get("genre", "").lower() == "music",
                    info.get("categories", [])
                    and "Music" in info.get("categories", []),
                    "music video" in info.get("title", "").lower(),
                    "official video" in info.get("title", "").lower(),
                    "official music video" in info.get("title", "").lower(),
                    "lyrics" in info.get("title", "").lower(),
                    "τραγούδι" in info.get("title", "").lower(),  # Greek word for song
                    "στίχοι" in info.get("title", "").lower(),  # Greek word for lyrics
                ]
            )

            # If no explicit language is set but we have Greek subtitles, assume it's Greek
            if not language and ("el" in subtitles or "el" in auto_subtitles):
                language = "el"

            return {
                "source": "youtube",
                "video_id": info.get("id"),
                "video_title": info.get("title"),
                "channel": info.get("uploader"),
                "upload_date": info.get("upload_date"),
                "url": url,
                "download_date": datetime.now().isoformat(),
                "duration_secs": duration_secs,
                # Add new metadata
                "subtitles": {
                    "manual": {lang: info for lang, info in subtitles.items()},
                    "auto_generated": {
                        lang: info for lang, info in auto_subtitles.items()
                    },
                },
                "detected_language": language,
                "tags": tags,
                "is_likely_music": is_music,
                "categories": info.get("categories", []),
            }

    except yt_dlp.utils.DownloadError as e:
        raise YouTubeDownloadError(f"Could not extract video info: {str(e)}")


def download_audio(url: str) -> Tuple[bytes, dict]:
    """Download audio from a YouTube video URL.

    Args:
        url: YouTube video URL

    Returns:
        Tuple of (audio_data: bytes, metadata: dict)
        The metadata includes:
        - Basic video info
        - Available subtitles (both manual and auto-generated)
        - Language detection
        - Content type detection (music vs speech)
        - Actual subtitle content in target language if available

    Raises:
        YouTubeDownloadError: If download fails
    """
    try:
        # First extract metadata to validate video
        metadata = extract_video_metadata(url)

        # Try to get subtitles in the best available format
        target_language = metadata.get("detected_language")
        if target_language:
            try:
                # For music content, we're more willing to use auto-generated captions
                # since Whisper sometimes struggles with songs
                include_auto = metadata.get("is_likely_music", False)

                # Try to get subtitles in target language
                subtitles = download_subtitles(
                    url, target_languages=[target_language], include_auto=include_auto
                )
                if subtitles:
                    metadata["subtitle_content"] = subtitles[target_language]
                    metadata["subtitle_source"] = (
                        "manual"
                        if target_language in metadata["subtitles"]["manual"]
                        else "auto_generated"
                    )
            except Exception as e:
                metadata["subtitle_error"] = str(e)

        # Create temp dir for download
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "audio"

            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "128",
                    }
                ],
                "outtmpl": str(temp_path),
                "quiet": True,
                "no_warnings": True,
                "verbose": False,
                "nocheckcertificate": True,
                "cookiefile": None,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                    # Find the downloaded file
                    audio_path = temp_path.with_suffix(".mp3")
                    if not audio_path.exists():
                        raise YouTubeDownloadError(
                            "Could not find downloaded audio file"
                        )

                    # Read the downloaded file
                    audio_data = audio_path.read_bytes()

                    # Verify size
                    if len(audio_data) > MAX_AUDIO_SIZE_UPLOAD_ALLOWED:
                        raise YouTubeDownloadError(
                            f"Downloaded audio exceeds size limit of {MAX_AUDIO_SIZE_UPLOAD_ALLOWED/(1024*1024):.1f}MB"
                        )

                    return audio_data, metadata

            except yt_dlp.utils.DownloadError as e:
                raise YouTubeDownloadError(f"Failed to download audio: {str(e)}")
            except Exception as e:
                raise YouTubeDownloadError(f"Error processing audio: {str(e)}")

    except Exception as e:
        raise YouTubeDownloadError(f"Error downloading audio: {str(e)}")


def download_subtitles(
    url: str, target_languages: list[str] | None = None, include_auto: bool = True
) -> dict[str, str]:
    """Download subtitles/closed captions from a YouTube video.

    Args:
        url: YouTube video URL
        target_languages: List of language codes to download. If None, downloads all available.
        include_auto: Whether to include auto-generated captions if manual ones aren't available

    Returns:
        Dict mapping language codes to subtitle text in SRT format

    Raises:
        YouTubeDownloadError: If subtitles cannot be downloaded
    """
    # First get metadata to see what's available
    metadata = extract_video_metadata(url)
    subtitles = metadata["subtitles"]

    # If no target languages specified, get all available
    if target_languages is None:
        target_languages = list(
            set(
                list(subtitles["manual"].keys())
                + list(subtitles["auto_generated"].keys())
            )
        )

    results = {}

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "subs"

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "allsubtitles": True,
            "subtitlesformat": "vtt",  # VTT format is most widely supported
            "skip_download": True,  # Don't download the video
            "outtmpl": str(temp_path),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

                # For each target language
                for lang in target_languages:
                    # Try manual subs first
                    sub_path = temp_path.parent / f"{temp_path.name}.{lang}.vtt"
                    if sub_path.exists():
                        results[lang] = sub_path.read_text()
                    # Fall back to auto subs if allowed
                    elif include_auto and lang in subtitles["auto_generated"]:
                        auto_path = (
                            temp_path.parent / f"{temp_path.name}.{lang}.auto.vtt"
                        )
                        if auto_path.exists():
                            results[lang] = auto_path.read_text()

        except yt_dlp.utils.DownloadError as e:
            raise YouTubeDownloadError(f"Failed to download subtitles: {str(e)}")

    return results
