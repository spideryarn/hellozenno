import os
import pytest
import requests


@pytest.mark.skipif(
    not os.environ.get("ELEVENLABS_RUN_LIVE_TESTS") or not os.environ.get("ELEVENLABS_API_KEY"),
    reason="Live ElevenLabs test disabled; set ELEVENLABS_RUN_LIVE_TESTS=1 and ELEVENLABS_API_KEY",
)
def test_elevenlabs_list_voices_live():
    api_key = os.environ["ELEVENLABS_API_KEY"].strip()
    resp = requests.get(
        "https://api.elevenlabs.io/v1/voices", headers={"xi-api-key": api_key}, timeout=15
    )
    assert resp.status_code == 200, f"Unexpected status: {resp.status_code}, body={resp.text[:2000]}"
    data = resp.json()
    voices = data.get("voices") if isinstance(data, dict) else data
    assert isinstance(voices, list) and len(voices) >= 1, "No voices available for this API key"

