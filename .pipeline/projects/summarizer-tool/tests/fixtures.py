"""
YouTube Summarizer Test Fixtures

This module provides test fixtures and mock data for testing the YouTube summarizer.
"""

# Test video URLs for integration testing
TEST_VIDEOS = {
    "public_with_transcript": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "public_auto_transcript": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "short_video": "https://www.youtube.com/watch?v=L_jWHffIx5E",
}

# Mock video metadata for testing
MOCK_VIDEO_METADATA = {
    "video_id": "dQw4w9WgXcQ",
    "title": "Test Video Title",
    "channel": "Test Channel",
    "channel_id": "UC123456789",
    "duration": 212,
    "duration_formatted": "00:03:32",
    "upload_date": "20230101",
    "upload_date_formatted": "2023-01-01",
    "view_count": 1000000,
    "like_count": 50000,
    "description": "This is a test video description.",
    "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "tags": ["test", "video", "example"],
    "categories": ["Entertainment"],
    "is_live": False,
    "was_live": False,
    "availability": "public",
    "age_limit": 0,
    "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

# Mock transcript data
MOCK_TRANSCRIPT = """
[00:00:00] Welcome to this test video. In this video, we'll be discussing
[00:00:05] the importance of testing and verification in software development.
[00:00:10] Testing is crucial for ensuring quality and reliability.
[00:00:15] Without proper testing, bugs and issues can slip through.
[00:00:20] In this video, we'll cover different types of testing,
[00:00:25] including unit tests, integration tests, and end-to-end tests.
[00:00:30] We'll also discuss test automation and best practices.
[00:00:35] Thank you for watching, and don't forget to subscribe!
"""

# Mock transcript info
MOCK_TRANSCRIPT_INFO = {
    "video_id": "dQw4w9WgXcQ",
    "title": "Test Video Title",
    "channel": "Test Channel",
    "duration": 212,
    "upload_date": "20230101",
    "selected_language": "en",
    "is_auto_generated": False,
    "available_languages": ["en", "es", "fr"]
}

# Mock LLM response
MOCK_LLM_RESPONSE = {
    "summary": "This video discusses the importance of testing in software development, covering unit tests, integration tests, end-to-end tests, test automation, and best practices. The video emphasizes that proper testing is crucial for ensuring quality and reliability.",
    "prompt_used": "Summarize the following text...",
    "processing_time": 2.5,
    "tokens_used": 45
}

# Mock error responses
ERROR_RESPONSES = {
    "private_video": {
        "error": "Private video"
    },
    "unlisted_video": {
        "error": "Video unavailable"
    },
    "region_restricted": {
        "error": "Video is region-restricted"
    },
    "no_transcript": {
        "subtitles": {},
        "automatic_captions": {}
    }
}

# Mock transcript URLs - Fixed format to match yt-dlp's actual structure
# yt-dlp returns subtitles as: {'lang': {'url': '...', 'ext': '...'}}
MOCK_TRANSCRIPT_URLS = {
    "en": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=en&fmt=ttml", "ext": "ttml"},
    "es": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=es&fmt=ttml", "ext": "ttml"},
    "fr": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=fr&fmt=ttml", "ext": "ttml"},
    "auto_en": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=en&fmt=ttml&kind=asr", "ext": "ttml"},
    "en-US": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=en-US&fmt=ttml", "ext": "ttml"},
    "en-GB": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=en-GB&fmt=ttml", "ext": "ttml"},
}

# Mock subtitles format (manual transcripts)
MOCK_SUBTITLES = {
    "en": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=en&fmt=ttml", "ext": "ttml"},
    "es": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=es&fmt=ttml", "ext": "ttml"},
    "fr": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=fr&fmt=ttml", "ext": "ttml"},
}

# Mock automatic captions (auto-generated)
MOCK_AUTOMATIC_CAPTIONS = {
    "en": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=en&fmt=ttml&kind=asr", "ext": "ttml"},
    "es": {"url": "https://www.youtube.com/api/timedtext?v=dQw4w9WgXcQ&lang=es&fmt=ttml&kind=asr", "ext": "ttml"},
}

# Combined mock data for full info
MOCK_FULL_INFO = {
    "id": "dQw4w9WgXcQ",
    "title": "Test Video Title",
    "channel": "Test Channel",
    "channel_id": "UC123456789",
    "duration": 212,
    "upload_date": "20230101",
    "view_count": 1000000,
    "like_count": 50000,
    "description": "Test description",
    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "tags": ["test", "video"],
    "categories": ["Entertainment"],
    "is_live": False,
    "was_live": False,
    "availability": "public",
    "subtitles": MOCK_SUBTITLES,
    "automatic_captions": MOCK_AUTOMATIC_CAPTIONS,
    "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

# URL patterns for testing
VALID_YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "https://www.youtube.com/v/dQw4w9WgXcQ",
]

INVALID_URLS = [
    "https://example.com/video",
    "not a url",
    "",
    None,
    "https://www.youtube.com/watch",
    "https://www.youtube.com/",
]

# Test cases for language selection
LANGUAGE_SELECTION_TESTS = [
    {
        "name": "Exact language match",
        "language": "en",
        "transcripts": {"en": {"url": "url1"}, "es": {"url": "url2"}},
        "prefer_manual": True,
        "expected_lang": "en",
        "expected_url": "url1"
    },
    {
        "name": "Language prefix match",
        "language": "en",
        "transcripts": {"en-US": {"url": "url1"}, "en-GB": {"url": "url2"}},
        "prefer_manual": True,
        "expected_lang": "en-US",
        "expected_url": "url1"
    },
    {
        "name": "Manual preferred over auto",
        "language": "en",
        "transcripts": {"en": {"url": "manual", "kind": "manual"}, "en_auto": {"url": "auto", "kind": "asr"}},
        "prefer_manual": True,
        "expected_lang": "en",
        "expected_url": "manual"
    },
    {
        "name": "Auto when no manual",
        "language": "en",
        "transcripts": {"en": {"url": "auto", "kind": "asr"}},
        "prefer_manual": True,
        "expected_lang": "en",
        "expected_url": "auto"
    },
    {
        "name": "No language specified, prefer manual",
        "language": None,
        "transcripts": {"en": {"url": "manual"}, "es": {"url": "auto", "kind": "asr"}},
        "prefer_manual": True,
        "expected_lang": "en",
        "expected_url": "manual"
    },
    {
        "name": "No transcripts available",
        "language": "en",
        "transcripts": {},
        "prefer_manual": True,
        "expected_lang": None,
        "expected_url": None
    }
]

# Test cases for video ID extraction
VIDEO_ID_TESTS = [
    {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "expected": "dQw4w9WgXcQ"},
    {"url": "https://youtu.be/dQw4w9WgXcQ", "expected": "dQw4w9WgXcQ"},
    {"url": "https://www.youtube.com/embed/dQw4w9WgXcQ", "expected": "dQw4w9WgXcQ"},
    {"url": "https://www.youtube.com/v/dQw4w9WgXcQ", "expected": "dQw4w9WgXcQ"},
]

# Test cases for duration formatting
DURATION_TESTS = [
    {"seconds": 0, "expected": "00:00:00"},
    {"seconds": 5, "expected": "00:00:05"},
    {"seconds": 65, "expected": "00:01:05"},
    {"seconds": 3665, "expected": "01:01:05"},
    {"seconds": 86400, "expected": "24:00:00"},
]

# Test cases for upload date formatting
UPLOAD_DATE_TESTS = [
    {"date": "20230101", "expected": "2023-01-01"},
    {"date": "20241231", "expected": "2024-12-31"},
    {"date": "", "expected": "Unknown"},
    {"date": "12345", "expected": "Unknown"},
]

# Test cases for number formatting
NUMBER_TESTS = [
    {"num": 0, "expected": "0"},
    {"num": 1000, "expected": "1,000"},
    {"num": 1000000, "expected": "1,000,000"},
    {"num": 1234567, "expected": "1,234,567"},
]
