# Summarizer Tool

A command-line summarizer tool that uses a local LLM to summarize YouTube videos, PDFs, and web content.

## Overview

This tool provides the ability to:
- **Summarize YouTube videos** - Extract transcripts and generate summaries
- **Summarize PDFs** - Extract text and summarize content from PDF documents (Phase 3)
- **Summarize web content** - Extract and summarize website/blog content (Phase 4)

**LLM Model**: Uses local GGUF format models via llama-cpp-python for privacy and offline operation.

## Installation

### Prerequisites
- Python 3.8+
- GGUF format model file (e.g., Gemma-4-E2B)

### Install Dependencies

```bash
cd summarizer-tool
pip install -r requirements.txt
```

### Download LLM Model

Download a GGUF model file and place it in your desired location:

```bash
# Example model path (update as needed)
MODEL_PATH="/path/to/Gemma-4-E2B-Uncensored-HauhauCS-Aggressive-Q2_K_P.gguf"
```

## Usage

### YouTube Video Summarization

Summarize a YouTube video:

```bash
# Basic usage - output to console
python -m summarizer_tool.main https://youtube.com/watch?v=VIDEO_ID

# Or use the main CLI
python main.py https://youtube.com/watch?v=VIDEO_ID
```

### Command Line Options

```
Usage: python main.py <url> [options]

Positional Arguments:
  url                   YouTube video URL

Options:
  -h, --help            Show this help message and exit
  -o, --output FILE     Output file path (default: auto-generated)
  -m, --model FILE      Path to GGUF model file (default: ./models/Gemma-4-E2B...)
  -l, --language CODE   Language code for transcript (e.g., en, es, fr). Default: auto-detect
  -n, --max-length NUM  Maximum transcript length in characters (default: 2000)
  -p, --prompt TEXT     Custom summarization prompt
  -d, --output-dir DIR  Output directory for auto-generated filenames (default: .)
  -v, --verbose         Show detailed progress information
  --prefer-manual       Prefer manual transcripts over auto-generated
  --no-prefer-manual    Allow auto-generated transcripts
  --version             Show version number
```

### Examples

```bash
# Summarize a video with default settings
python main.py https://youtube.com/watch?v=dQw4w9WgXcQ

# Summarize and save to file
python main.py https://youtube.com/watch?v=dQw4w9WgXcQ -o summary.txt

# Summarize in Spanish
python main.py https://youtube.com/watch?v=dQw4w9WgXcQ -l es

# Summarize with custom model
python main.py https://youtube.com/watch?v=dQw4w9WgXcQ -m /path/to/custom_model.gguf

# Summarize with longer transcript processing
python main.py https://youtube.com/watch?v=dQw4w9WgXcQ -n 5000

# Summarize with custom prompt
python main.py https://youtube.com/watch?v=dQw4w9WgXcQ -p "Summarize in 3 bullet points"
```

## Features

### YouTube Summarization

- **Transcript Extraction**: Uses yt-dlp for reliable YouTube transcript extraction
- **Metadata Extraction**: Extracts video title, duration, channel, upload date, views, likes
- **Multi-language Support**: Handles transcripts in multiple languages
- **Auto-generated vs Manual**: Detects and warns about auto-generated transcripts
- **Error Handling**: Gracefully handles private, unlisted, and region-restricted videos

### Transcript Language Handling

The tool automatically:
- Lists available transcript languages
- Defaults to the most appropriate transcript
- Warns when using auto-generated (potentially less accurate) transcripts
- Allows manual language specification with `-l` flag

### Video Metadata

Extracts the following information:
- Video title
- Channel name and ID
- Duration (formatted as HH:MM:SS)
- Upload date
- View count
- Like count
- Available transcript languages
- Whether transcript is auto-generated

## Error Handling

The tool handles various error scenarios:

| Error Type | Description | Solution |
|------------|-------------|----------|
| Private Video | Video is set to private | Use a public video |
| Unlisted Video | Video is not publicly accessible | Check video URL |
| Region-Restricted | Video not available in your region | Try a different video |
| No Transcript | Video has no available captions | Use a video with captions |
| Invalid URL | Malformed YouTube URL | Provide valid URL |

## Project Structure

```
summarizer-tool/
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── src/
│   ├── __init__.py          # Package initialization
│   ├── youtube_summarizer.py # YouTube summarization logic
│   └── llm_interface.py      # LLM inference interface
├── tests/
│   ├── test_youtube_summarizer.py
│   ├── test_youtube_integration.py
│   └── fixtures/
│       ├── test_videos.txt
│       └── mock_responses/
└── docs/
    └── phase2_completion_summary.md
```

## API Usage

You can also use the YouTubeSummarizer class programmatically:

```python
from summarizer_tool.src.youtube_summarizer import YouTubeSummarizer

# Initialize
summarizer = YouTubeSummarizer(
    llm_model_path="/path/to/model.gguf",
    default_language='en',
    prefer_manual=True
)

# Extract metadata
metadata = summarizer.extract_metadata("https://youtube.com/watch?v=VIDEO_ID")
print(f"Title: {metadata['title']}")
print(f"Duration: {metadata['duration_formatted']}")

# Summarize video
summary = summarizer.summarize_video(
    url="https://youtube.com/watch?v=VIDEO_ID",
    language='en',
    max_length=2000,
    output_file="summary.txt"
)

print(f"Summary: {summary['summary']}")
print(f"Processing time: {summary['processing_time']} seconds")
```

## Limitations

- **Transcript Availability**: Not all videos have transcripts. Videos without captions cannot be summarized.
- **Auto-generated Transcripts**: May have lower accuracy than manually created ones.
- **Video Length**: Very long videos (>1 hour) may be truncated based on max_length setting.
- **LLM Model**: Summary quality depends on the LLM model used.
- **Region Restrictions**: Some videos may be restricted in certain geographic regions.

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=summarizer_tool

# Run specific test file
pytest tests/test_youtube_summarizer.py -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- **yt-dlp**: For reliable YouTube transcript extraction
- **llama-cpp-python**: For local LLM inference
- **GGUF Models**: For efficient model execution
