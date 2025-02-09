from typing import Optional
from pathlib import Path
import tempfile
from obsolete._secrets import ELEVENLABS_API_KEY
from gdutils.audios import play_mp3
from gdutils.outloud_text_to_speech import outloud_elevenlabs
from gdutils.strings import PathOrStr
from obsolete.google_cloud_storage_utils import upload_file, get_storage_client
from config import GOOGLE_CLOUD_STORAGE_BUCKET
from slugify import slugify
from gdutils.hashing import hash_consistent


def generate_mp3_filen(txt: str, mp3_dirn: str) -> str:
    """Generate a filename for an MP3 file based on the text content."""
    filen = slugify(txt)
    if len(filen) > 100:
        filen = filen[:100] + "___" + hash_consistent(txt)
    return f"{mp3_dirn}/{filen}.mp3"


def add_delays(txt: str) -> str:
    """Add delay markers to text for speech synthesis."""

    def add_to_pattern(orig: str, pattern: str, addition: str):
        return orig.replace(pattern, f"{pattern}{addition}")

    delays_from_patterns = {
        "\n": 1,
        ". ": 0.75,
        ", ": 0.5,
    }
    delay_template = '<break time="%.2fs" />'
    txt_slow = txt
    for pattern in delays_from_patterns:
        delay = delay_template % delays_from_patterns[pattern]
        txt_slow = add_to_pattern(txt_slow, pattern, delay)
    return txt_slow


def play_txt_audio_gcs(
    txt: str,
    mp3_dirn: Optional[str] = None,
    mp3_filen: Optional[str] = None,
) -> str:
    """Legacy GCS version of play_txt_audio."""
    if mp3_filen is None:
        assert mp3_dirn is not None, "Must provide mp3_dirn if mp3_filen is None"
        mp3_filen = generate_mp3_filen(txt, mp3_dirn)

    # Create a temporary file to store the downloaded content
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        try:
            client = get_storage_client()
            bucket = client.bucket(GOOGLE_CLOUD_STORAGE_BUCKET)
            blob = bucket.blob(mp3_filen)
            blob.download_to_filename(temp_file.name)
            play_mp3(temp_file.name)
        except Exception as e:
            print(f"Error playing audio: {e}")
    return mp3_filen


def generate_txt_audio_gcs(
    txt: str,
    mp3_dirn: str,
    mp3_filen: Optional[str] = None,
    should_add_delays: bool = False,
    should_play: bool = False,
    overwrite_already_exists: bool = False,
    verbose: int = 0,
) -> str:
    """Legacy GCS version of generate_txt_audio."""
    if should_add_delays:
        txt = add_delays(txt)
    if mp3_filen is None:
        mp3_filen = generate_mp3_filen(txt, mp3_dirn)

    # Check if file exists in GCS
    if not overwrite_already_exists:
        client = get_storage_client()
        bucket = client.bucket(GOOGLE_CLOUD_STORAGE_BUCKET)
        blob = bucket.blob(mp3_filen)
        if blob.exists():
            print(f"MP3 file already exists in GCS: {mp3_filen}")
            return mp3_filen

    if verbose >= 1:
        print(f"Generating MP3 file for {txt} -> {mp3_filen}")

    # Create a temporary file for the audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        outloud_elevenlabs(
            text=txt,
            api_key=ELEVENLABS_API_KEY,
            mp3_filen=temp_file.name,
        )
        # Upload to GCS
        if not GOOGLE_CLOUD_STORAGE_BUCKET:
            raise ValueError("GOOGLE_CLOUD_STORAGE_BUCKET is not set")

        upload_file(
            bucket_name=GOOGLE_CLOUD_STORAGE_BUCKET,
            source_file=temp_file.name,
            destination_blob=mp3_filen,
            verbose=verbose,
        )

    if should_play:
        play_txt_audio_gcs(txt, mp3_dirn, mp3_filen)

    return mp3_filen
