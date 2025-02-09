def mock_download_audio(url):
    return (
        b"test audio data",
        {
            "source": "youtube",
            "video_id": "test_id",
            "video_title": "Test Video",
            "channel": "Test Channel",
            "upload_date": "20240111",
            "url": url,
            "download_date": "2024-01-11T12:00:00",
            "duration_secs": 300,
        },
    )
